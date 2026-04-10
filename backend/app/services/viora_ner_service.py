"""
Viora NER Service — Local ONNX-based Named Entity Recognition for CVs.

Replaces GLiNER service with our fine-tuned RoBERTa model (ONNX INT8).
Imports inference logic directly from ml/viora-ner/src/inference.py
to preserve the entity fragmentation fix and ONNX support.

Key advantages:
- Fine-tuned on CV data: higher accuracy than zero-shot GLiNER
- ONNX INT8: 119 MB (vs GLiNER 1.76 GB), <100ms inference
- Fully offline: no API calls, no internet required
- Anti-fragmentation fix built-in (word-level tokenization)
- Gazetteer validation (128K skills) confirms NER output quality

Architecture (after refactoring):
- cv_parsers.py: Text parsing (soft skills, experience, graduation, text cleanup)
- viora_ner_service.py: ONNX model + gazetteer validation + structured CV
"""
import re
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

from app.core.config import settings
from app.core.logging import get_logger
from app.services.cv_parsers import (
    extract_soft_skills_from_text,
    detect_graduation_year,
    parse_experience_years,
    clean_entity_text,
    extract_contact_from_text,
)

logger = get_logger(__name__)

# ── Add viora-ner to Python path ────────────────────────────
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent  # viora_app/
_VIORA_NER_ROOT = _PROJECT_ROOT / "ml" / "viora-ner"

if str(_VIORA_NER_ROOT) not in sys.path:
    sys.path.insert(0, str(_VIORA_NER_ROOT))


_inference_module = None
try:
    from src import inference as _inference_module
except ImportError:
    pass  # Will be handled in _ensure_initialized


# ── spaCy NLP — Lazy singleton for linguistic analysis ──────
# Used for: lemmatization, dependency parsing, POS tagging
# Model: en_core_web_sm (12MB) — loaded on first proficiency call
_spacy_nlp = None


def _get_spacy():
    """Lazy-load spaCy with only the components we need."""
    global _spacy_nlp
    if _spacy_nlp is None:
        try:
            import spacy
            _spacy_nlp = spacy.load(
                "en_core_web_sm",
                disable=["ner"],  # We have our own NER — skip spaCy's
            )
            logger.info("spaCy NLP loaded (lemmatizer + dependency parser)")
        except (ImportError, OSError) as e:
            logger.warning("spaCy not available — proficiency scoring degraded: %s", e)
    return _spacy_nlp


# ── Bloom's Taxonomy — Universal verb proficiency levels ─────
# Academic framework (Anderson & Krathwohl, 2001) used by MIT,
# Oregon State, and production ATS systems worldwide.
# Domain-agnostic: "diagnose" = Level 4 in medicine AND software.
#
# Mapping: verb_lemma → Bloom level (6=highest, 0=passive)
_BLOOM_LEVELS: Dict[str, int] = {
    # Level 6: Create (إنشاء/ابتكار)
    "design": 6, "develop": 6, "create": 6, "architect": 6,
    "engineer": 6, "build": 6, "formulate": 6, "construct": 6,
    "invent": 6, "pioneer": 6, "author": 6, "compose": 6,
    "establish": 6, "launch": 6, "spearhead": 6, "initiate": 6,
    # Level 5: Evaluate (تقييم/حكم)
    "evaluate": 5, "assess": 5, "audit": 5, "appraise": 5,
    "critique": 5, "justify": 5, "judge": 5, "recommend": 5,
    "select": 5, "prioritize": 5, "validate": 5,
    # Level 4: Analyze (تحليل/تشخيص)
    "analyze": 4, "diagnose": 4, "investigate": 4, "compare": 4,
    "differentiate": 4, "examine": 4, "debug": 4, "troubleshoot": 4,
    "optimize": 4, "research": 4, "test": 4, "inspect": 4,
    "survey": 4, "calculate": 4, "measure": 4, "streamline": 4,
    # Level 3: Apply (تطبيق/تنفيذ)
    "implement": 3, "perform": 3, "conduct": 3, "operate": 3,
    "execute": 3, "deploy": 3, "integrate": 3, "configure": 3,
    "administer": 3, "manage": 3, "process": 3, "collect": 3,
    "maintain": 3, "install": 3, "calibrate": 3, "prepare": 3,
    "monitor": 3, "coordinate": 3, "deliver": 3, "resolve": 3,
    "produce": 3, "organize": 3, "schedule": 3, "lead": 3,
    "negotiate": 3, "facilitate": 3, "train": 3, "supervise": 3,
    "draft": 3, "prosecute": 3, "counsel": 3, "fabricate": 3,
    "automate": 3, "reduce": 3, "increase": 3, "improve": 3,
    "screen": 3, "compile": 3, "generate": 3, "migrate": 3,
    "ensure": 3,
    # Level 2: Understand (فهم/تفسير)
    "describe": 2, "explain": 2, "interpret": 2, "classify": 2,
    "summarize": 2, "report": 2, "discuss": 2, "translate": 2,
    "review": 2, "document": 2, "present": 2,
    # Level 1: Remember (تذكر)
    "identify": 1, "list": 1, "recall": 1, "recognize": 1,
    "state": 1, "define": 1, "name": 1, "record": 1,
    # Level 0: Passive/Support (دعم سلبي)
    "assist": 0, "support": 0, "help": 0, "participate": 0,
    "attend": 0, "observe": 0, "shadow": 0, "follow": 0,
    "use": 0, "utilize": 0, "work": 0, "collaborate": 0,
    "contribute": 0,
}

# Bloom level → proficiency points (verb_score component)
_BLOOM_SCORES: Dict[int, int] = {
    6: 20, 5: 17, 4: 15, 3: 12, 2: 8, 1: 5, 0: 3,
}


class VioraNERService:
    """Viora NER service with ONNX model loading.

    Cold start optimization:
    - `src.inference` is imported eagerly at module level (~17s saved on first request)
    - `warmup()` can be called from FastAPI startup to preload the model
    - Singleton pattern ensures model is loaded only once
    """

    def __init__(self):
        self._model = None
        self._tokenizer = None
        self._initialized = False
        self._available = False
        self._skill_gazetteer = None  # Supplementary extraction layer

    def warmup(self):
        """Eagerly load the model — call from FastAPI startup event."""
        self._ensure_initialized()

    def _ensure_initialized(self):
        """Load ONNX model on first use (or via warmup)."""
        if self._initialized:
            return

        self._initialized = True
        model_dir = _PROJECT_ROOT / settings.VIORA_NER_MODEL_DIR

        try:
            global _inference_module
            if _inference_module is None:
                from src import inference as _inference_module

            start = time.time()

            if not model_dir.exists():
                logger.error("Viora NER model not found at: %s", model_dir)
                self._available = False
                return

            logger.info("Loading Viora NER ONNX model from: %s", model_dir)
            self._model, self._tokenizer = _inference_module.load_model(
                str(model_dir), use_onnx=True,
            )

            # Load skills gazetteer for supplementary extraction
            gaz_path = _VIORA_NER_ROOT / "data" / "gazetteers" / "skills_gazetteer.json"
            if gaz_path.exists():
                try:
                    from src.gazetteer import SkillGazetteer
                    self._skill_gazetteer = SkillGazetteer(gaz_path)
                    logger.info(
                        "Skills gazetteer loaded: %d entries",
                        self._skill_gazetteer.count,
                    )
                except Exception as gaz_err:
                    logger.warning("Gazetteer load failed: %s", gaz_err)
            else:
                logger.warning("Skills gazetteer not found at: %s", gaz_path)

            elapsed = time.time() - start
            self._available = True
            logger.info("Viora NER model loaded in %.1fs", elapsed)

        except ImportError as e:
            logger.error("Failed to import viora-ner modules: %s", e)
            self._available = False
        except Exception as e:
            logger.error("Failed to load Viora NER model: %s", e)
            self._available = False

    @property
    def is_available(self) -> bool:
        """Check if model is loaded and ready."""
        self._ensure_initialized()
        return self._available

    def extract_entities(self, text: str) -> List[Dict]:
        """
        Extract raw entities from text using Viora NER.

        Returns list of dicts: [{text, label, start, end, confidence}, ...]
        Labels: PERSON, SKILL, JOB_TITLE, ORG, LOCATION, CONTACT, CREDENTIAL, EXPERIENCE
        """
        self._ensure_initialized()

        if not self._available:
            logger.warning("Viora NER not available — returning empty results")
            return []

        if not text or not text.strip():
            return []

        try:
            start = time.time()
            entities = _inference_module.predict_entities(
                text,
                self._model,
                self._tokenizer,
                max_length=512,
                stride=128,
                use_onnx=True,
            )
            elapsed = time.time() - start

            results = [
                {
                    "text": clean_entity_text(ent.text),
                    "label": ent.label,
                    "start": ent.start,
                    "end": ent.end,
                    "confidence": ent.confidence,
                }
                for ent in entities
            ]

            logger.info(
                "Viora NER extracted %d entities in %.0fms",
                len(results),
                elapsed * 1000,
            )
            return results

        except Exception as e:
            logger.error("Viora NER extraction failed: %s", e)
            return []

    def extract_cv_structured(self, text: str) -> Dict:
        """
        Extract structured CV data using Viora NER.

        Returns a structured dict with categorized skills, contact info,
        education, experience, etc. — ready for merging with O*NET output.
        """
        raw = self.extract_entities(text)

        if not raw:
            return self._empty_cv_result()

        # ── Confidence filtering ─────────────────────────────
        # Remove entities with confidence below threshold
        # Configurable via NER_CONFIDENCE_THRESHOLD env var (default 0.50)
        threshold = settings.NER_CONFIDENCE_THRESHOLD
        filtered = [ent for ent in raw if ent["confidence"] >= threshold]
        logger.info(
            "NER filter: %d/%d entities passed (threshold=%.2f)",
            len(filtered), len(raw), threshold,
        )

        # ── Language reclassification ────────────────────────
        # "Arabic", "English", etc. are often tagged as SKILL by NER
        LANGUAGE_NAMES = {"arabic", "english", "french", "german", "spanish",
                          "chinese", "japanese", "korean", "hindi", "turkish",
                          "urdu", "persian", "russian", "portuguese", "italian"}

        languages_detected = []
        cleaned = []
        for ent in filtered:
            text_lower = ent["text"].strip().lower()
            if ent["label"] == "SKILL" and text_lower in LANGUAGE_NAMES:
                languages_detected.append(ent["text"].strip())
            else:
                cleaned.append(ent)

        # Group entities by label, deduplicating by lowercased text
        grouped: Dict[str, List[Dict]] = {}
        for ent in cleaned:
            label = ent["label"]
            if label not in grouped:
                grouped[label] = []

            # Avoid duplicates
            existing = [e["text"].lower() for e in grouped[label]]
            if ent["text"].strip().lower() not in existing:
                grouped[label].append(ent)

        # Sort each group by confidence (highest first)
        for label in grouped:
            grouped[label].sort(key=lambda x: x["confidence"], reverse=True)

        # ── Build structured result ──────────────────────────

        # Skills (already filtered and cleaned)
        hard_skills = [e["text"] for e in grouped.get("SKILL", [])]

        # Build strong_skills with CONTEXT-BASED proficiency scoring
        # (NOT NER confidence — see _compute_proficiency() for rationale)
        strong_skills = [
            {
                "name": e["text"],
                "proficiency": self._compute_proficiency(e["text"], text, raw),
                "category": "technical",
                "source": "ner",
            }
            for e in grouped.get("SKILL", [])
        ]

        # Contact info
        persons = [e["text"] for e in grouped.get("PERSON", [])]
        contacts = [e["text"] for e in grouped.get("CONTACT", [])]

        # Parse contact info (emails, phones, etc.)
        emails = [c for c in contacts if "@" in c]
        phones = [c for c in contacts if any(ch.isdigit() for ch in c) and "@" not in c]

        # Fallback: extract contact info from raw text if NER missed them
        text_contacts = extract_contact_from_text(text)
        if not emails and text_contacts.get("email"):
            emails = [text_contacts["email"]]
        if not phones and text_contacts.get("phone"):
            phones = [text_contacts["phone"]]

        # Career info
        job_titles = [e["text"] for e in grouped.get("JOB_TITLE", [])]
        companies = [e["text"] for e in grouped.get("ORG", [])]

        # Education
        credentials = [e["text"] for e in grouped.get("CREDENTIAL", [])]

        # Location
        locations = [e["text"] for e in grouped.get("LOCATION", [])]

        # Experience
        experience = [e["text"] for e in grouped.get("EXPERIENCE", [])]

        # ── Gazetteer validation of NER output (NOT full-text extraction) ──
        # The gazetteer (128K skills) is used ONLY to validate NER results,
        # NOT to independently scan text. Scanning text with 128K entries
        # produces massive false positives (common words like "practice",
        # "managing", "COM" etc. match gazetteer entries from ESCO altLabels).
        #
        # Best practice (per NLP research):
        #   - NER model extracts skills (understands CONTEXT)
        #   - Gazetteer validates/boosts confidence (is this a KNOWN skill?)
        #   - Soft skills handled separately by cv_parsers.py (~50 curated terms)
        hard_lower = {s.lower() for s in hard_skills}
        if self._skill_gazetteer:
            validated = 0
            for ss in strong_skills:
                if self._skill_gazetteer.is_known_skill(ss["name"]):
                    ss["validated"] = True
                    validated += 1
                else:
                    ss["validated"] = False
            logger.info(
                "Gazetteer validation: %d/%d NER skills are known in taxonomy",
                validated, len(strong_skills),
            )

        # ── Soft skills extraction via gazetteer (from cv_parsers) ──
        # NER is trained on technical entities — soft skills need text matching
        # cv_parsers.py uses a CURATED set of ~50 ESCO transversal skills
        # (no false positives because the list is manually vetted)
        soft_skills = extract_soft_skills_from_text(text)
        # Remove any soft skills that NER already captured as hard skills
        soft_skills = [s for s in soft_skills if s.lower() not in hard_lower]

        # ── Graduation year detection (from cv_parsers) ──
        graduation_year = detect_graduation_year(credentials, text)

        return {
            "hard_skills": hard_skills,
            "soft_skills": soft_skills,
            "strong_skills": strong_skills,
            "contact": {
                "name": persons[0] if persons else "",
                "email": emails[0] if emails else "",
                "phone": phones[0] if phones else "",
                "location": locations[0] if locations else "",
            },
            "job_titles": job_titles,
            "companies": companies,
            "education": {
                "degrees": credentials,
                "universities": [
                    c for c in companies
                    if any(kw in c.lower() for kw in
                           ["university", "college", "institute", "school",
                            "جامع", "كلية", "معهد"])
                ],
                "certifications": [],
            },
            "projects": [],
            "languages": languages_detected,
            "experience_years": experience,
            "parsed_experience_years": parse_experience_years(
                experience, text, graduation_year=graduation_year,
            ),
            "graduation_year": graduation_year,
            "raw_entities": grouped,
        }

    def _compute_proficiency(
        self, skill_name: str, full_text: str, raw_entities: List[Dict],
    ) -> int:
        """Compute proficiency score using spaCy + Bloom's Taxonomy.

        Production-grade approach (replaces hardcoded verb lists):
        - spaCy lemmatizer: handles ALL verb forms (performing→perform)
        - spaCy dependency parser: links verbs to skills syntactically
        - Bloom's Taxonomy: 6-level academic framework for proficiency
        - Domain-agnostic: works for medicine, law, engineering, IT, etc.

        Scoring signals:
        1. Frequency: How many times is the skill mentioned?
        2. Context depth: Which CV section is it in?
        3. Bloom verb level: spaCy extracts verbs → Bloom maps to proficiency
        4. Recency: Is it near "Present" / "Current"?
        5. Gazetteer validation: Known skill gets a small boost

        Returns: 30-95 (clamped)
        """
        text_lower = full_text.lower()
        skill_lower = skill_name.lower().strip()
        skill_words = set(skill_lower.split())

        # ── Signal 1: Frequency of mentions (max +25) ────────────
        pattern = re.compile(re.escape(skill_lower), re.IGNORECASE)
        mention_count = len(pattern.findall(full_text))

        if mention_count >= 5:
            freq_score = 25
        elif mention_count >= 3:
            freq_score = 20
        elif mention_count >= 2:
            freq_score = 12
        else:
            freq_score = 5  # Mentioned once

        # ── Signal 2: Context sections (max +30) ─────────────────
        context_score = 0

        _section_patterns = {
            "experience": re.compile(
                r'(?:^|\n)\s*(?:(?:PROFESSIONAL\s+)?EXPERIENCE|'
                r'WORK\s*(?:EXPERIENCE|HISTORY)|EMPLOYMENT|'
                r'CLINICAL\s+EXPERIENCE)\s*\n',
                re.IGNORECASE | re.MULTILINE,
            ),
            "projects": re.compile(
                r'(?:^|\n)\s*(?:PROJECTS|KEY\s*PROJECTS|'
                r'PORTFOLIO|PERSONAL\s*PROJECTS)\s*\n',
                re.IGNORECASE | re.MULTILINE,
            ),
            "summary": re.compile(
                r'(?:^|\n)\s*(?:(?:PROFESSIONAL\s+)?SUMMARY|'
                r'PROFILE|OBJECTIVE|ABOUT\s*ME|'
                r'CAREER\s+(?:OVERVIEW|SUMMARY))\s*\n',
                re.IGNORECASE | re.MULTILINE,
            ),
            "skills": re.compile(
                r'(?:^|\n)\s*(?:(?:TECHNICAL\s+|CORE\s+|KEY\s+|'
                r'LABORATORY\s+|CLINICAL\s+)?SKILLS|'
                r'TECHNOLOGIES|TOOLS|(?:CORE\s+)?COMPETENC|'
                r'QUALIFICATIONS)\s*\n',
                re.IGNORECASE | re.MULTILINE,
            ),
            "education": re.compile(
                r'(?:^|\n)\s*(?:EDUCATION|CERTIFICATIONS?|ACADEMIC)\s*\n',
                re.IGNORECASE | re.MULTILINE,
            ),
        }

        _section_scores = {
            "projects": 30,
            "experience": 25,
            "summary": 20,
            "education": 15,
            "skills": 10,
        }

        for section_name, section_re in _section_patterns.items():
            match = section_re.search(full_text)
            if match:
                sec_start = match.end()
                remaining = full_text[sec_start:]
                next_header = re.search(
                    r'(?:^|\n)\s*[A-Z][A-Z\s&/]{3,}\s*\n', remaining,
                )
                sec_end = (
                    sec_start + next_header.start() if next_header
                    else len(full_text)
                )
                section_text = full_text[sec_start:sec_end].lower()
                sec_points = _section_scores.get(section_name, 8)

                # Exact match
                if skill_lower in section_text:
                    context_score = max(context_score, sec_points)
                # Partial word match (multi-word skills):
                # "Quality Control" in text matches "Quality Assurance" skill
                elif len(skill_words) >= 2:
                    matched_words = sum(
                        1 for w in skill_words if w in section_text
                    )
                    if matched_words >= max(1, len(skill_words) // 2):
                        # Partial match → slightly lower score
                        context_score = max(
                            context_score, int(sec_points * 0.7)
                        )

        if context_score == 0:
            context_score = 8

        # ── Signal 3: Bloom verb proficiency via spaCy (max +20) ─
        # Production-grade: spaCy parses sentences, extracts verb-object
        # relationships, lemmatizes verbs, and maps to Bloom's Taxonomy.
        # Replaces the old 120-char window + hardcoded verb list approach.
        verb_score = 0
        nlp = _get_spacy()

        if nlp is not None:
            # Split text into lines → process bullet points individually
            # (more accurate than parsing the entire CV as one document)
            _BULLET_RE = re.compile(r'^[\u2022\u2023\u25e6\u2043\u2219\u25aa\u25ab\u25b8\u25b9\u2013\u2014\-\*\u00b7]+\s*')
            lines = [ln.strip() for ln in full_text.split("\n") if ln.strip()]

            for line in lines:
                line_lower = line.lower()
                # Quick check: skip lines that don't mention this skill
                if skill_lower not in line_lower:
                    # Also check partial word match for multi-word skills
                    if not (len(skill_words) >= 2 and
                            any(w in line_lower for w in skill_words)):
                        continue

                # Strip bullet markers before spaCy parsing.
                # Without this, "•" causes spaCy to misparse the
                # dependency tree: "Performing" becomes amod instead
                # of ROOT, breaking verb-skill subtree detection.
                clean_line = _BULLET_RE.sub("", line)
                doc = nlp(clean_line)

                for token in doc:
                    if token.pos_ != "VERB":
                        continue

                    lemma = token.lemma_.lower()
                    bloom_level = _BLOOM_LEVELS.get(lemma)

                    if bloom_level is None:
                        continue

                    # Check if this verb is syntactically linked to our skill
                    # via dependency tree (dobj, pobj, prep→pobj, etc.)
                    verb_objects = set()
                    for child in token.subtree:
                        if child != token:
                            verb_objects.add(child.text.lower())

                    # Check if skill (or any of its words) appears in
                    # the verb's dependency subtree
                    skill_in_subtree = (
                        skill_lower in " ".join(verb_objects)
                        or bool(skill_words & verb_objects)
                    )

                    if skill_in_subtree:
                        score = _BLOOM_SCORES.get(bloom_level, 0)
                        verb_score = max(verb_score, score)

        else:
            # Fallback if spaCy unavailable: simple text-based matching
            for m in pattern.finditer(full_text):
                ctx = full_text[max(0, m.start() - 120):m.start()].lower()
                words_before = set(ctx.split())
                for word in words_before:
                    bl = _BLOOM_LEVELS.get(word)
                    if bl is not None:
                        verb_score = max(
                            verb_score, _BLOOM_SCORES.get(bl, 0)
                        )

        # ── Signal 4: Recency (max +10) ──────────────────────────
        recency_score = 0
        for m in pattern.finditer(full_text):
            context_around = full_text[
                max(0, m.start() - 300):min(len(full_text), m.end() + 100)
            ].lower()
            if any(kw in context_around
                   for kw in ["present", "current", "2026", "2025"]):
                recency_score = 10
                break

        # ── Signal 5: Gazetteer validation boost (+5) ────────────
        gaz_score = 0
        if self._skill_gazetteer and self._skill_gazetteer.is_known_skill(
            skill_name
        ):
            gaz_score = 5

        # ── Combine all signals ──────────────────────────────────
        total = (
            freq_score + context_score + verb_score
            + recency_score + gaz_score
        )

        # Clamp to 30-95 range
        proficiency = max(30, min(95, total))

        return proficiency

    def _empty_cv_result(self) -> Dict:
        """Return empty structured result when extraction fails."""
        return {
            "hard_skills": [],
            "soft_skills": [],
            "strong_skills": [],
            "contact": {"name": "", "email": "", "phone": "", "location": ""},
            "job_titles": [],
            "companies": [],
            "education": {
                "degrees": [],
                "universities": [],
                "certifications": [],
            },
            "projects": [],
            "languages": [],
            "experience_years": [],
            "parsed_experience_years": None,
            "graduation_year": None,
            "raw_entities": {},
        }


# ── Singleton & DI ──────────────────────────────────────────

_ner_instance: Optional[VioraNERService] = None


def get_ner_service() -> VioraNERService:
    """Dependency injection factory (singleton to avoid reloading model)."""
    global _ner_instance
    if _ner_instance is None:
        _ner_instance = VioraNERService()
    return _ner_instance
