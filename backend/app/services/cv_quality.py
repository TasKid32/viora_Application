"""
CV Quality Assessment — Intelligent CV quality validation.

Scoring system (production-grade):
1. Word count scoring (graduated, not binary)
2. Section detection + section depth
3. Quantifiable achievements (numbers, percentages, metrics)
4. Date range detection (work experience periods)
5. Professional language scoring (action verbs, domain terminology)

Extracted from file_handler.py for Single Responsibility:
This module handles ONLY CV quality analysis and scoring.
"""
import re
from typing import Dict, List

from app.core.logging import get_logger

logger = get_logger(__name__)

# ── CV quality assessment constants ──────────────────────────────

# Minimum text length to consider a CV valid (characters)
MIN_CV_TEXT_LENGTH = 100

# Key section patterns (English + Arabic)
CV_SECTION_PATTERNS = {
    "experience": re.compile(
        r"(experience|work\s*history|employment|الخبر[اة]|خبرات?\s*العمل|التجربة)",
        re.IGNORECASE,
    ),
    "education": re.compile(
        r"(education|academic|degree|university|التعليم|الشهاد[اة]|الجامع[ةه]|المؤهل)",
        re.IGNORECASE,
    ),
    "skills": re.compile(
        r"(skills|technologies|tools|competenc|المهار[اة]ت?|التقن[يى]ات|الأدوات)",
        re.IGNORECASE,
    ),
    "contact": re.compile(
        r"(email|phone|tel|mobile|address|linkedin|البريد|الهاتف|الجوال|العنوان)",
        re.IGNORECASE,
    ),
}

# ── Quantifiable achievement patterns ────────────────────────────
# Matches: "3+ years", "95% accuracy", "managed 10+", "$50K", "20% increase"
_ACHIEVEMENT_PATTERNS = [
    re.compile(r"\d+\+?\s*(years?|months?|yrs?)", re.IGNORECASE),
    re.compile(r"\d+%", re.IGNORECASE),
    re.compile(r"\$\d+", re.IGNORECASE),
    re.compile(r"(led|managed|supervised|mentored|trained)\s+\d+", re.IGNORECASE),
    re.compile(r"(increased|decreased|reduced|improved|grew|saved)\s*(by\s*)?\d+", re.IGNORECASE),
    re.compile(r"\d+\s*(projects?|clients?|teams?|members?|people|employees)", re.IGNORECASE),
]

# ── Date range patterns ──────────────────────────────────────────
# Matches: "2020-2023", "Jan 2021 - Present", "2019 – 2022", "March 2020 to December 2021"
_DATE_RANGE_PATTERNS = [
    re.compile(r"\d{4}\s*[-–—]\s*(\d{4}|[Pp]resent|[Cc]urrent)", re.IGNORECASE),
    re.compile(
        r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+\d{4}\s*[-–—to]+\s*"
        r"((Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+\d{4}|[Pp]resent|[Cc]urrent)",
        re.IGNORECASE,
    ),
]

# ── Action verbs (professional language — all domains) ───────────
# Uses Bloom's Taxonomy verb lemmas for universal coverage.
# spaCy lemmatization handles verb forms (performing→perform).
_ACTION_VERB_LEMMAS = {
    # Create (Level 6)
    "design", "develop", "create", "architect", "engineer", "build",
    "formulate", "construct", "invent", "pioneer", "establish", "launch",
    "spearhead", "initiate", "compose", "author",
    # Evaluate (Level 5)
    "evaluate", "assess", "audit", "appraise", "critique", "validate",
    "recommend", "prioritize",
    # Analyze (Level 4)
    "analyze", "diagnose", "investigate", "examine", "debug",
    "troubleshoot", "optimize", "research", "test", "inspect",
    "calculate", "measure", "streamline", "compare",
    # Apply (Level 3)
    "implement", "perform", "conduct", "operate", "execute", "deploy",
    "integrate", "configure", "administer", "manage", "process",
    "collect", "maintain", "install", "calibrate", "prepare", "monitor",
    "coordinate", "deliver", "resolve", "produce", "organize", "lead",
    "negotiate", "facilitate", "train", "supervise", "draft", "counsel",
    "automate", "reduce", "improve", "screen", "migrate", "generate",
    # Understand (Level 2)
    "interpret", "classify", "report", "review", "document", "present",
    # Support (Level 0)
    "assist", "support", "collaborate", "contribute",
}

# Fallback: past-tense forms for when spaCy is unavailable
_ACTION_VERBS_FALLBACK = {
    "developed", "implemented", "managed", "designed", "led", "created",
    "analyzed", "improved", "built", "established", "coordinated", "executed",
    "delivered", "optimized", "streamlined", "spearheaded", "orchestrated",
    "engineered", "maintained", "monitored", "supervised", "conducted",
    "performed", "collaborated", "contributed", "resolved", "achieved",
    "administered", "facilitated", "supported", "trained", "initiated",
    "diagnosed", "calibrated", "collected", "tested", "screened",
    "drafted", "inspected", "surveyed", "fabricated", "measured",
    "assessed", "evaluated", "audited", "validated", "investigated",
}


def assess_cv_quality(text: str) -> Dict:
    """Assess the quality and completeness of extracted CV text.

    Returns a dict with:
        - quality_score: 0-100 overall quality score
        - is_valid: True if CV meets minimum quality threshold
        - sections_found: list of detected CV sections
        - sections_missing: list of missing critical sections
        - warnings: list of human-readable warnings
        - word_count: number of words
    """
    warnings: List[str] = []
    sections_found: List[str] = []
    sections_missing: List[str] = []
    score = 0  # Start at 0, build up to 100

    # ── Check 1: Text length ────────────────────────────────
    text_stripped = text.strip()
    word_count = len(text_stripped.split())

    if len(text_stripped) < MIN_CV_TEXT_LENGTH:
        warnings.append(
            "The extracted text is very short. "
            "The CV may be incomplete or image-based."
        )

    # ── Score Component 1: Word count (max 25 points) ───────
    # Professional CVs: 350-800 words
    if word_count < 30:
        wc_score = 0
        warnings.append(
            f"Only {word_count} words detected. "
            "A typical CV has 200-800 words."
        )
    elif word_count < 100:
        wc_score = 5
        warnings.append(
            f"Only {word_count} words detected. "
            "The CV may be missing important details."
        )
    elif word_count < 200:
        wc_score = 10
        warnings.append(
            f"{word_count} words detected — below average. "
            "Consider adding more details about experience and skills."
        )
    elif word_count < 350:
        wc_score = 18
    elif word_count <= 800:
        wc_score = 25  # Ideal range
    else:
        wc_score = 22  # Slightly penalize very long CVs
    score += wc_score

    # ── Score Component 2: Section presence (max 30 points) ─
    for section_name, pattern in CV_SECTION_PATTERNS.items():
        if pattern.search(text):
            sections_found.append(section_name)
        else:
            sections_missing.append(section_name)

    # Critical sections: experience, education, skills = 8 pts each
    # Contact = 6 pts
    section_scores = {
        "experience": 8, "education": 8, "skills": 8, "contact": 6,
    }
    section_score = sum(
        section_scores.get(s, 0) for s in sections_found
    )
    score += section_score

    critical = {"experience", "education", "skills"}
    missing_critical = critical - set(sections_found)
    if missing_critical:
        section_names = ", ".join(sorted(missing_critical))
        warnings.append(
            f"Missing key sections: {section_names}. "
            "These are typically expected in a CV."
        )

    if "contact" not in sections_found:
        warnings.append(
            "No contact information detected. "
            "Consider adding email and phone number."
        )

    # ── Score Component 3: Email presence (max 5 points) ────
    email_pattern = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
    if email_pattern.search(text):
        score += 5
    else:
        warnings.append("No email address found in the CV.")

    # ── Score Component 4: Quantifiable achievements (max 15 points) ─
    achievement_count = 0
    for pattern in _ACHIEVEMENT_PATTERNS:
        achievement_count += len(pattern.findall(text))
    achievement_count = min(achievement_count, 6)  # Cap at 6

    if achievement_count == 0:
        ach_score = 0
        warnings.append(
            "No quantifiable achievements found. "
            "Adding numbers and metrics improves CV quality "
            "(e.g. 'managed 5 projects', 'improved efficiency by 20%')."
        )
    elif achievement_count <= 2:
        ach_score = 7
    elif achievement_count <= 4:
        ach_score = 12
    else:
        ach_score = 15
    score += ach_score

    # ── Score Component 5: Date ranges for work experience (max 10 points) ─
    date_range_count = 0
    for pattern in _DATE_RANGE_PATTERNS:
        date_range_count += len(pattern.findall(text))

    if date_range_count == 0:
        dr_score = 0
        if "experience" in sections_found:
            warnings.append(
                "No date ranges found in experience section. "
                "Adding specific employment periods improves credibility."
            )
    elif date_range_count == 1:
        dr_score = 5
    else:
        dr_score = 10
    score += dr_score

    # ── Score Component 6: Professional language (max 15 points) ─
    # Use spaCy lemmatizer for universal verb form matching:
    # "Performing" → "perform" → matched!
    # Fallback: exact matching against past-tense verb forms
    text_lower = text.lower()
    action_verb_count = 0

    try:
        from app.services.viora_ner_service import _get_spacy
        nlp = _get_spacy()
        if nlp is not None:
            # Sample first ~2000 chars (enough for verb detection, fast)
            sample = text[:2000]
            doc = nlp(sample)
            found_lemmas = set()
            for token in doc:
                if token.pos_ == "VERB":
                    lemma = token.lemma_.lower()
                    if lemma in _ACTION_VERB_LEMMAS:
                        found_lemmas.add(lemma)
            action_verb_count = len(found_lemmas)
        else:
            raise ImportError("spaCy not loaded")
    except (ImportError, Exception):
        # Fallback: exact matching (legacy behavior)
        words_set = set(text_lower.split())
        action_verb_count = len(words_set & _ACTION_VERBS_FALLBACK)

    if action_verb_count == 0:
        pl_score = 2  # Minimum — text exists
    elif action_verb_count <= 3:
        pl_score = 7
    elif action_verb_count <= 6:
        pl_score = 12
    else:
        pl_score = 15
    score += pl_score

    # Clamp score
    score = max(0, min(100, score))
    is_valid = score >= 25  # Below 25 = likely not a real CV

    result = {
        "quality_score": score,
        "is_valid": is_valid,
        "sections_found": sections_found,
        "sections_missing": sections_missing,
        "warnings": warnings,
        "word_count": word_count,
    }

    logger.info(
        "CV quality assessment: score=%d, valid=%s, words=%d, found=%s, missing=%s",
        score, is_valid, word_count, sections_found, sections_missing,
    )

    return result
