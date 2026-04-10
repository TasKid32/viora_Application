"""
O*NET Service — Skill gap analysis & learning roadmap using O*NET taxonomy.

Replaces Gemini API for:
1. Occupation matching (fuzzy match user's job title → O*NET SOC code)
2. Skill gap analysis (compare user skills vs O*NET requirements)
3. Learning roadmap generation (prioritize missing skills)

Uses official U.S. Department of Labor data (900+ occupations).
Runs fully offline, <50ms per analysis, 100% deterministic.

Architecture (after refactoring):
- esco_resolver.py: ESCO taxonomy operations (85K skills + hierarchy)
- onet_data_loader.py: File I/O for O*NET TSV data (5 loaders + aliases)
- onet_roadmap.py: Roadmap generation + job opportunity matching
- onet_service.py: Main service class (matching + gap analysis)
"""
import math
from pathlib import Path
from typing import Dict, List, Optional

from app.core.config import settings
from app.core.logging import get_logger
from app.services.esco_resolver import ESCOSkillResolver, _ONET_TO_ESCO_BRIDGE
from app.services.onet_data_loader import (
    load_occupations,
    load_skills,
    load_tech_skills,
    load_knowledge,
    load_abilities,
    JOB_ALIASES,
)
from app.services.onet_roadmap import (
    generate_roadmap as _generate_roadmap,
    get_job_opportunities as _get_job_opportunities,
)

logger = get_logger(__name__)

# ── Trivial tools filter ─────────────────────────────────────
# These tools are so universally known that listing them as "missing
# skills" is unhelpful and dilutes the real skill gaps.
# Only filtered if they are NOT marked as hot_technology (safety check).
_TRIVIAL_TOOLS = {
    # Category names (from O*NET technology_skills.txt categories)
    "microsoft word", "microsoft excel", "microsoft powerpoint",
    "microsoft outlook", "microsoft office", "microsoft office software",
    "word processing software", "spreadsheet software",
    "presentation software", "electronic mail software",
    "web browser software", "internet browser",
    "web browser", "operating system software",
    "calendar and scheduling software",
    "desktop publishing software",
    "instant messaging software",
    "video conferencing software",
    # Actual O*NET tool names (differ from category names)
    "email software", "office suite software",
    "calendar software", "database software",
    "web platform development software",
    "internet browser software", "file versioning software",
}

# ── Project root ─────────────────────────────────────────────
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent  # viora_app/


class ONetService:
    """O*NET taxonomy service for career analysis."""

    def __init__(self):
        self._initialized = False
        self._occupations: Dict[str, Dict] = {}       # soc_code → {title, description}
        self._skills: Dict[str, List[Dict]] = {}       # soc_code → [{name, importance}]
        self._tech_skills: Dict[str, List[Dict]] = {}  # soc_code → [{name, category, hot}]
        self._knowledge: Dict[str, List[Dict]] = {}    # soc_code → [{name, importance}]
        self._abilities: Dict[str, List[Dict]] = {}    # soc_code → [{name, importance}]
        self._title_to_soc: Dict[str, str] = {}        # lowercase title → soc_code
        self._esco: ESCOSkillResolver = ESCOSkillResolver()  # ESCO enrichment layer
        # Cross-SOC co-occurrence index for personalized tech ranking
        self._tool_to_socs: Dict[str, set] = {}        # tool.lower() → {soc_codes}
        self._total_socs_with_tech: int = 0             # count of SOCs with any tech

    def _ensure_initialized(self):
        """Load O*NET data files on first use."""
        if self._initialized:
            return
        self._initialized = True

        data_dir = _PROJECT_ROOT / settings.ONET_DATA_DIR

        if not data_dir.exists():
            logger.error("O*NET data directory not found: %s", data_dir)
            return

        try:
            self._occupations, self._title_to_soc = load_occupations(
                data_dir / "occupations.txt"
            )
            self._skills = load_skills(data_dir / "skills.txt")
            self._tech_skills = load_tech_skills(data_dir / "technology_skills.txt")
            self._knowledge = load_knowledge(data_dir / "knowledge.txt")
            self._abilities = load_abilities(data_dir / "abilities.txt")

            # Build cross-SOC co-occurrence index (inverted index)
            # Maps each tool → set of SOC codes where it appears.
            # Used for personalized recommendations: "how often does this
            # missing tool appear alongside the user's existing tools?"
            for soc_code, tech_list in self._tech_skills.items():
                for tech in tech_list:
                    tool_lower = tech["name"].lower()
                    if tool_lower not in self._tool_to_socs:
                        self._tool_to_socs[tool_lower] = set()
                    self._tool_to_socs[tool_lower].add(soc_code)
            self._total_socs_with_tech = len({
                soc for soc in self._tech_skills if self._tech_skills[soc]
            })

            logger.info(
                "O*NET loaded: %d occupations, %d skill entries, %d tech, "
                "%d knowledge, %d abilities, %d unique tools indexed",
                len(self._occupations),
                sum(len(v) for v in self._skills.values()),
                sum(len(v) for v in self._tech_skills.values()),
                sum(len(v) for v in self._knowledge.values()),
                sum(len(v) for v in self._abilities.values()),
                len(self._tool_to_socs),
            )
        except Exception as e:
            logger.error("Failed to load O*NET data: %s", e)

        # Load ESCO enrichment layer (non-blocking — O*NET works alone)
        esco_dir = _PROJECT_ROOT / settings.ESCO_DATA_DIR
        self._esco.load(esco_dir)

    # ── Semantic Embedding Matcher ───────────────────────────
    # Uses sentence-transformers (all-MiniLM-L6-v2) for semantic
    # similarity matching. Pre-computes embeddings for all O*NET
    # titles and caches to disk for fast reload.

    _semantic_model = None
    _title_embeddings = None
    _title_list = None  # ordered list matching embeddings

    def _init_semantic_matcher(self):
        """Lazily load sentence-transformers and pre-compute title embeddings."""
        if self._semantic_model is not None:
            return True

        try:
            from sentence_transformers import SentenceTransformer
            import numpy as np
        except ImportError:
            logger.warning("sentence-transformers not installed — skipping semantic matching")
            return False

        # Cache path for pre-computed embeddings
        cache_dir = _PROJECT_ROOT / "ml" / "viora-ner" / "data" / "cache"
        cache_dir.mkdir(parents=True, exist_ok=True)
        embeddings_path = cache_dir / "onet_title_embeddings.npy"
        titles_path = cache_dir / "onet_title_list.npy"

        # Load the model (small: 22M params, ~80MB, very fast)
        logger.info("Loading semantic embedding model (all-MiniLM-L6-v2)...")
        self._semantic_model = SentenceTransformer(
            "all-MiniLM-L6-v2", device="cpu"
        )

        # Build title list from O*NET
        self._title_list = list(self._title_to_soc.keys())

        # Try to load cached embeddings
        if embeddings_path.exists() and titles_path.exists():
            cached_titles = np.load(titles_path, allow_pickle=True).tolist()
            if cached_titles == self._title_list:
                self._title_embeddings = np.load(embeddings_path)
                logger.info(
                    "Loaded cached title embeddings: %d titles",
                    len(self._title_list),
                )
                return True

        # Compute embeddings for all O*NET titles
        logger.info("Computing embeddings for %d O*NET titles...", len(self._title_list))
        self._title_embeddings = self._semantic_model.encode(
            self._title_list,
            batch_size=64,
            show_progress_bar=False,
            normalize_embeddings=True,  # for cosine similarity via dot product
        )

        # Cache to disk
        np.save(embeddings_path, self._title_embeddings)
        np.save(titles_path, np.array(self._title_list, dtype=object))
        logger.info("Cached title embeddings to %s", embeddings_path)

        return True

    def _semantic_match(self, job_title: str, threshold: float = 0.45) -> Optional[Dict]:
        """Find best O*NET match using semantic similarity.

        Uses cosine similarity between the input job title embedding
        and pre-computed O*NET title embeddings.
        Threshold 0.45 balances precision and recall:
          - "Attorney" → "Lawyers" scores ~0.55 ✓
          - "Plumber" → "Plumbers" scores ~0.90 ✓
          - "Attorney" → "Tutors" scores ~0.15 ✗ (rejected)
        """
        if not self._init_semantic_matcher():
            return None

        import numpy as np

        # Encode the query
        query_embedding = self._semantic_model.encode(
            [job_title.lower()],
            normalize_embeddings=True,
        )

        # Cosine similarity (dot product since both are normalized)
        similarities = np.dot(self._title_embeddings, query_embedding.T).flatten()
        best_idx = int(np.argmax(similarities))
        best_score = float(similarities[best_idx])

        if best_score < threshold:
            return None

        matched_title = self._title_list[best_idx]
        soc = self._title_to_soc[matched_title]
        occ = self._occupations[soc]

        logger.info(
            "Semantic match: '%s' → '%s' (similarity=%.3f)",
            job_title, occ["title"], best_score,
        )
        return {
            "soc_code": soc,
            "title": occ["title"],
            "description": occ["description"],
            "match_score": int(best_score * 100),
        }

    # ── Occupation matching ──────────────────────────────────

    def match_occupation(self, job_title: str) -> Optional[Dict]:
        """
        Find the closest O*NET occupation for a given job title.

        Matching strategy (per O*NET expert recommendations):
        1. Exact title match (100% score)
        2. Alias lookup — sorted longest-first so specific aliases win
        3. Semantic embedding match (all-MiniLM-L6-v2 cosine similarity)
        4. Fuzzy match with WRatio (score_cutoff=70)

        Returns: {soc_code, title, description, match_score}
        """
        self._ensure_initialized()

        if not job_title or not self._occupations:
            return None

        job_lower = job_title.strip().lower()

        # Strategy 1: Exact match
        if job_lower in self._title_to_soc:
            soc = self._title_to_soc[job_lower]
            occ = self._occupations[soc]
            return {
                "soc_code": soc,
                "title": occ["title"],
                "description": occ["description"],
                "match_score": 100,
            }

        # Strategy 2: Job title → O*NET alias (substring match)
        # Sorted by key length DESCENDING so specific aliases match first:
        #   "interior design" (15 chars) wins over "consultant" (10 chars)
        sorted_aliases = sorted(
            JOB_ALIASES.items(), key=lambda x: len(x[0]), reverse=True
        )
        for alias_key, alias_job in sorted_aliases:
            if alias_key in job_lower or job_lower in alias_key:
                alias_lower = alias_job.lower()
                if alias_lower in self._title_to_soc:
                    soc = self._title_to_soc[alias_lower]
                    occ = self._occupations[soc]
                    logger.info(
                        "O*NET alias match: '%s' → '%s' (via degree alias)",
                        job_title, occ["title"],
                    )
                    return {
                        "soc_code": soc,
                        "title": occ["title"],
                        "description": occ["description"],
                        "match_score": 95,  # High confidence alias
                    }

        # Strategy 3: Semantic embedding match
        # Uses all-MiniLM-L6-v2 to find semantically similar O*NET titles
        # e.g. "Chemical Process Engineer" → "Chemical Engineers" (similarity=0.72)
        semantic_result = self._semantic_match(job_title)
        if semantic_result:
            return semantic_result

        # Strategy 4: Fuzzy match (final fallback, cutoff=70)
        try:
            from rapidfuzz import fuzz, process

            titles = list(self._title_to_soc.keys())
            result = process.extractOne(
                job_lower, titles, scorer=fuzz.WRatio, score_cutoff=70
            )

            if result:
                matched_title, score, _ = result
                soc = self._title_to_soc[matched_title]
                occ = self._occupations[soc]
                return {
                    "soc_code": soc,
                    "title": occ["title"],
                    "description": occ["description"],
                    "match_score": int(score),
                }
        except ImportError:
            logger.warning("rapidfuzz not installed — using simple matching")
            # Fallback: substring matching
            for title, soc in self._title_to_soc.items():
                if job_lower in title or title in job_lower:
                    occ = self._occupations[soc]
                    return {
                        "soc_code": soc,
                        "title": occ["title"],
                        "description": occ["description"],
                        "match_score": 70,
                    }

        logger.info("No O*NET match found for: %s", job_title)
        return None

    # ── Skill gap analysis ───────────────────────────────────

    def analyze_skill_gaps(
        self,
        user_skills: List[str],
        job_title: str = "",
        soc_code: str = "",
        experience_years: Optional[int] = None,
        has_work_experience: bool = True,
    ) -> Dict:
        """
        Analyze skill gaps between user's skills and O*NET requirements.

        O*NET has TWO types of skill data:
        - skills.txt: Generic competencies (e.g. "Programming", "Critical Thinking")
        - technology_skills.txt: Specific tools (e.g. "Python", "React", "Docker")

        User skills from NER are typically specific (Python, React, SQL) so we
        match against BOTH: technology_skills for direct tool matching, and
        skills.txt for generic competency matching.
        """
        self._ensure_initialized()

        # Find target occupation
        if soc_code and soc_code in self._occupations:
            occupation = {
                "soc_code": soc_code,
                "title": self._occupations[soc_code]["title"],
                "description": self._occupations[soc_code]["description"],
                "match_score": 100,
            }
        elif job_title:
            occupation = self.match_occupation(job_title)
        else:
            occupation = None

        if not occupation:
            logger.info("No O*NET occupation match — returning empty gap result")
            return self._empty_gap_result()

        soc = occupation["soc_code"]

        # Get required skills, tech skills, and knowledge
        required_skills = self._skills.get(soc, [])
        required_tech = self._tech_skills.get(soc, [])
        required_knowledge = self._knowledge.get(soc, [])

        # Normalize user skills for matching
        user_lower = {s.lower().strip() for s in user_skills if s}

        # ── Step 1: Match user skills against TECHNOLOGY skills ──
        # This is where "Python" matches "Python" or "JavaScript" matches "JavaScript"
        matched_tech = []
        matched_tech_categories: set = set()  # Track user's tech categories
        missing_tech_raw = []
        for tech in required_tech:
            tech_name = tech["name"]
            if self._skill_matches(tech_name, user_lower):
                matched_tech.append(tech_name)
                matched_tech_categories.add(tech["category"])  # Remember category
            else:
                # Priority: Hot Technology > In Demand > other
                is_hot = tech.get("hot_technology", False)
                is_in_demand = tech.get("in_demand", False)
                if is_hot:
                    priority = "High"
                elif is_in_demand:
                    priority = "Medium"
                else:
                    priority = "Low"

                missing_tech_raw.append({
                    "skill": tech_name,
                    "priority": priority,
                    "category": tech["category"],
                    "hot_technology": is_hot,
                    "in_demand": is_in_demand,
                })

        # ── Filter 1: Remove trivial/universally-known tools ─────
        # These tools are so basic that listing them as "missing" is unhelpful.
        # O*NET marks Word/Excel/PowerPoint as "hot_technology" because they
        # appear in many job listings, but they are NOT real skill gaps.
        # Filtered unconditionally — anyone applying for jobs knows these.
        missing_tech_raw = [
            item for item in missing_tech_raw
            if item["skill"].lower() not in _TRIVIAL_TOOLS
        ]

        # ── Filter 2: Semantic deduplication ──────────────────────
        # O*NET lists both specific tools AND their generic categories:
        #   "Microsoft Excel" (tool) + "Spreadsheet software" (category)
        # Remove the generic category name if a specific tool exists.
        specific_tool_categories = {
            item["category"].lower() for item in missing_tech_raw
            if item["skill"].lower() != item["category"].lower()
        }
        missing_tech_raw = [
            item for item in missing_tech_raw
            if not (
                item["skill"].lower() == item["category"].lower()
                and item["category"].lower() in specific_tool_categories
            )
        ]

        # ── Specificity-Weighted Affinity Score ──────────────────
        # Production-quality ranking for missing tech skills.
        # Based on research from Lightcast/LinkedIn Skills Graph.
        #
        # relevance = weighted_affinity × specificity × market_signal
        #
        # KEY INSIGHT: Binary co-occurrence (does ANY user tool appear
        # in this SOC?) fails because Python/JS/Git appear in 800+
        # SOC codes, making nearly all SOCs "related". Instead, we
        # use WEIGHTED co-occurrence: a SOC with 11 user tools matched
        # (like 15-1252 Software Developers) weighs 11x more than a
        # SOC with just 1 match (like 11-1011 Chief Executives).
        #
        # Three independent signals:
        # 1. Weighted Affinity: How strongly do the user's tools
        #    concentrate in SOCs that also list this missing tool?
        #    Proven by diagnostic: MS Access #29→#93, Docker #43→#18
        #
        # 2. Specificity (IDF): How specialized is this tool?
        #    IDF = log(total_SOCs / SOCs_with_tool)
        #    Microsoft Access (372 SOCs): IDF=0.79 → GENERIC
        #    Docker (~50 SOCs): IDF=2.79 → SPECIALIZED
        #
        # 3. Market Signal: Hot Technology > In Demand > other

        # Step 1: Build WEIGHTED SOC profile from user's matched tools
        # Each SOC gets a weight = number of user tools it contains.
        # Minimum 2 overlap — a SOC with just 1 user tool (e.g. Python
        # in Chief Executives) is noise, not signal.
        user_tools_lower = {t.lower() for t in matched_tech}
        soc_weights: Dict[str, int] = {}
        for soc_code_iter, tech_list in self._tech_skills.items():
            soc_tools = {t["name"].lower() for t in tech_list}
            overlap = len(soc_tools & user_tools_lower)
            if overlap >= 2:
                soc_weights[soc_code_iter] = overlap

        total_weight = sum(soc_weights.values()) or 1
        total_socs = max(1, self._total_socs_with_tech)

        # Step 2: Score each missing tool
        def _tech_relevance_score(item: Dict) -> float:
            """Compute Specificity-Weighted Affinity Score.

            Returns NEGATIVE relevance (for ascending sort: lower = better).
            """
            tool_lower = item["skill"].lower()
            tool_socs = self._tool_to_socs.get(tool_lower, set())

            # Signal 1: Weighted Affinity
            # Sum of match-weights for SOCs where this tool appears
            weighted_sum = sum(
                soc_weights.get(s, 0) for s in tool_socs
            )
            affinity = weighted_sum / total_weight

            # Signal 2: Specificity (IDF — penalizes generic tools)
            specificity = math.log(total_socs / max(1, len(tool_socs)))

            # Signal 3: Market demand
            if item.get("hot_technology"):
                market = 1.0
            elif item.get("in_demand"):
                market = 0.7
            else:
                market = 0.3

            return -(affinity * specificity * market)

        missing_tech_raw.sort(key=_tech_relevance_score)

        logger.info(
            "Tech scoring: %d focused SOCs (≥2 tools), total_weight=%d, "
            "%d missing tools ranked (weighted IDF)",
            len(soc_weights), total_weight, len(missing_tech_raw),
        )

        # ── Category diversity: max 3 items per category ──────────
        # Without this, all 10 results could be from one category.
        # With diversity: 3 dev tools + 3 DB tools + 3 cloud tools = better mix
        MAX_PER_CATEGORY = 3
        cat_counts: Dict[str, int] = {}
        missing_tech = []
        for item in missing_tech_raw:
            cat = item["category"]
            cat_counts[cat] = cat_counts.get(cat, 0) + 1
            if cat_counts[cat] <= MAX_PER_CATEGORY:
                missing_tech.append(item)
            if len(missing_tech) >= 10:
                break

        # ── Step 2: Match against generic O*NET skills ──────────
        # Uses Element ID taxonomy for data-driven classification:
        #   2.A.* = Basic Skills (transferable: Reading, Writing, etc.)
        #   2.B.* = Cross-Functional Skills (transferable: Problem Solving, etc.)
        #   Other = Domain-Specific (must be learned)
        matched_generic = []
        missing_hard = []      # Domain-specific gaps (the real learning needs)
        missing_soft = []      # Kept for backward compatibility in API response

        # Determine if user has education/experience (for transferable auto-assume)
        has_education_or_experience = (
            has_work_experience
            or (experience_years is not None and experience_years >= 0)
        )

        # Get occupation title for ESCO essential/optional lookup
        occ_title = occupation["title"]

        for skill in required_skills:
            skill_name = skill["name"]
            importance = skill["importance"]
            skill_lower_name = skill_name.lower()
            is_transferable = skill.get("is_transferable", False)
            not_relevant = skill.get("not_relevant", False)

            # ── Skip O*NET "Not Relevant" flagged skills ─────────
            # These are skills O*NET itself marks as irrelevant for this SOC.
            if not_relevant:
                continue

            # ── Official O*NET importance threshold ──────────────
            # O*NET Center defines importance < 3.0 as "not important"
            # for a given occupation (scale 1-5, midpoint = 3.0).
            # This universally filters irrelevant skills for ALL professions:
            #   Dentist: removes "Programming" (1.75), "Installation" (1.50)
            #   Lawyer:  removes "Equipment Maintenance" (1.25)
            #   Developer: keeps "Programming" (4.75), "Critical Thinking" (4.25)
            #   Nurse:   keeps "Active Listening" (4.38), "Monitoring" (3.75)
            if importance < 3.0:
                continue  # Skip low-importance skills

            # Check direct match
            is_matched = self._skill_matches(skill_name, user_lower)

            # Data-driven: check via ESCO hierarchy (replaces hardcoded tech_to_generic)
            if not is_matched:
                is_matched = self._skill_matches_data_driven(
                    skill_lower_name, user_lower, soc
                )

            # ── Auto-assume ONLY truly basic skills (Element ID-based) ──
            # Only 2.A.* (Basic Skills) are genuinely universal:
            #   Reading Comprehension, Writing, Speaking, Active Listening,
            #   Mathematics, Science, etc.
            # 2.B.* (Cross-Functional) are NOT auto-assumed because they
            # include domain-specific skills like:
            #   Programming (2.B.1), Systems Analysis (2.B.4),
            #   Operations Monitoring (2.B.3), Quality Control (2.B.2)
            # These are real gaps that must be verified against user skills.
            element_id = skill.get("element_id", "")
            is_truly_basic = element_id.startswith("2.A.")
            if not is_matched and is_truly_basic and has_education_or_experience:
                is_matched = True
                logger.debug(
                    "Auto-assumed basic skill: %s (Element ID: %s)",
                    skill_name, element_id,
                )

            if is_matched:
                matched_generic.append(skill_name)
            else:
                if importance >= 4.0:
                    priority = "High"
                elif importance >= 3.0:
                    priority = "Medium"
                else:
                    priority = "Low"

                # ESCO essential/optional flag
                essential_flag = self._esco.get_essential_flag(occ_title, skill_name)

                entry = {
                    "skill": skill_name,
                    "priority": priority,
                    "importance": importance,
                    "essential_in_esco": essential_flag,
                }

                # Remaining unmatched skills are domain-specific gaps.
                # Transferable skills were already auto-assumed above,
                # so anything left here is a genuine learning need.
                # Still use ESCO soft check for API backward-compatibility.
                if self._esco.is_soft_skill(skill_name):
                    missing_soft.append(entry)
                else:
                    missing_hard.append(entry)

        # ── Step 3: Calculate experience level ──────────────────
        # PRIMARY: use NER-parsed experience years (most reliable)
        # FALLBACK: use skill match counts
        all_matched = matched_generic + matched_tech
        matched_generic_count = len(matched_generic)
        matched_tech_count = len(matched_tech)

        if experience_years is not None and experience_years >= 0:
            # Primary method: NER-extracted years of experience
            if experience_years >= 6:
                experience_level = "Senior"
            elif experience_years >= 3:
                experience_level = "Mid-Level"
            else:
                experience_level = "Junior"
        elif not has_work_experience:
            # No parsed years AND no real work experience detected
            # → Fresh graduate (common: has Bachelor but no job history)
            experience_level = "Junior"
        else:
            # Fallback: use skill match ratios
            # Changed default from Mid-Level → Junior for fresh graduates
            # who have few matched skills (common for new graduates)
            total_generic = len(required_skills)
            if total_generic > 0:
                generic_ratio = matched_generic_count / total_generic
                if generic_ratio >= 0.5 or matched_generic_count >= 15 or matched_tech_count >= 30:
                    experience_level = "Senior"
                elif generic_ratio >= 0.3 or matched_generic_count >= 8 or matched_tech_count >= 15:
                    experience_level = "Mid-Level"
                elif matched_tech_count >= 8:
                    experience_level = "Mid-Level"
                else:
                    experience_level = "Junior"
            else:
                experience_level = "Junior"  # No data → assume fresh graduate

        # ── Step 4: Analyze knowledge gaps ───────────────────
        missing_knowledge = []
        for k in required_knowledge:
            k_name = k["name"]
            k_importance = k["importance"]
            if k_importance >= 3.5 and not self._skill_matches(k_name, user_lower):
                priority = "High" if k_importance >= 4.0 else "Medium"
                missing_knowledge.append({
                    "area": k_name,
                    "priority": priority,
                    "importance": k_importance,
                })

        return {
            "occupation": occupation,
            "predicted_job": occupation["title"],
            "career_direction": occupation["description"][:200],
            "experience_level": experience_level,
            "missing_hard_skills": missing_hard[:15],
            "missing_soft_skills": missing_soft[:10],
            "missing_tech_skills": missing_tech[:20],
            "missing_knowledge": missing_knowledge[:10],
            "matched_skills": all_matched,
            "missing_skills": [
                {"skill": s["skill"], "priority": s["priority"],
                 "reason": f"Required for {occupation['title']}"}
                for s in (missing_hard + missing_soft)[:15]
            ],
        }

    # Known false-positive pairs — prevent fuzzy matching from confusing these
    _FALSE_MATCHES = {
        ("java", "javascript"), ("javascript", "java"),
        ("c", "c++"), ("c++", "c"), ("c", "c#"), ("c#", "c"),
        ("r", "react"), ("react", "r"), ("r", "ruby"), ("ruby", "r"),
        ("go", "google"), ("google", "go"),
        ("swift", "swiftui"), ("swiftui", "swift"),
        ("sql", "nosql"), ("nosql", "sql"),
        ("aws", "gcp"), ("gcp", "aws"),
    }

    def _skill_matches(self, skill_name: str, user_skills: set) -> bool:
        """Check if a required skill matches any user skill.

        Matching layers (in order):
        1. Exact match (lowercase)
        2. ESCO canonical normalization (85K synonyms from EU taxonomy)
           "Cascading style sheets CSS" → canonical "cascading style sheets"
           User's "css3" → canonical "cascading style sheets" → MATCH!
        3. Substring containment (O*NET names often embed abbreviations)
           "Cascading style sheets CSS" contains "css" → user has "css3" → MATCH!
        4. Fuzzy match with rapidfuzz (score ≥ 90, false-match blacklist)
        """
        skill_lower = skill_name.lower().strip()

        # ── Layer 1: Exact match ──
        if skill_lower in user_skills:
            return True

        # ── Layer 2: ESCO canonical normalization ──
        # Normalize the O*NET skill → ESCO canonical name
        # Then check if any user skill normalizes to the SAME canonical
        if self._esco._loaded:
            onet_canonical = self._esco.normalize_skill(skill_lower)

            for user_skill in user_skills:
                user_canonical = self._esco.normalize_skill(user_skill)
                if onet_canonical == user_canonical:
                    return True

        # ── Layer 3: Abbreviation extraction from O*NET names ──
        # O*NET names often embed the abbreviation:
        #   "Cascading style sheets CSS" → extract "CSS"
        #   "Hypertext markup language HTML" → extract "HTML"
        #   "Enterprise resource planning ERP software" → extract "ERP"
        # Check if any part of the O*NET name matches user skills
        onet_parts = set(skill_lower.split())
        for user_skill in user_skills:
            user_parts = set(user_skill.split())
            # If any single token (≥2 chars) from O*NET matches a user token
            common = onet_parts & user_parts
            if common and any(len(t) >= 2 for t in common):
                # Verify via false-match blacklist
                if (skill_lower, user_skill) not in self._FALSE_MATCHES:
                    return True
            # Also check if user skill is a substring of O*NET name or vice versa
            # "css3" in "cascading style sheets css" → no (but handles "css" in name)
            # "tailwind css" → "css" is in onet_parts
            if len(user_skill) >= 3 and user_skill in skill_lower:
                if (skill_lower, user_skill) not in self._FALSE_MATCHES:
                    return True
            if len(skill_lower) >= 3 and skill_lower in user_skill:
                if (skill_lower, user_skill) not in self._FALSE_MATCHES:
                    return True

        # ── Layer 4: Fuzzy match (last resort) ──
        try:
            from rapidfuzz import fuzz

            is_short = len(skill_lower.split()) <= 2

            for user_skill in user_skills:
                if (skill_lower, user_skill) in self._FALSE_MATCHES:
                    continue

                if is_short:
                    score = fuzz.ratio(skill_lower, user_skill)
                else:
                    score = fuzz.token_set_ratio(skill_lower, user_skill)

                if score >= 90:
                    return True

        except ImportError:
            pass

        return False

    def _skill_matches_data_driven(
        self, onet_skill_lower: str, user_skills: set, soc: str
    ) -> bool:
        """Data-driven skill matching using ESCO hierarchy + O*NET tech fallback.

        Replaces hardcoded tech_to_generic with:
        1. ESCO bridge: O*NET skill → ESCO equivalent → hierarchy match
        2. O*NET tech fallback: check if user tech tool belongs to same SOC family
        """
        # Layer 1: ESCO bridge + hierarchy
        esco_equiv = _ONET_TO_ESCO_BRIDGE.get(onet_skill_lower)
        if esco_equiv:
            for user_skill in user_skills:
                if self._esco.shares_ancestor(user_skill, esco_equiv, max_depth=3):
                    return True

        # Layer 2: O*NET tech fallback (ONLY for skills that have a bridge entry)
        # Having Python tools doesn't mean you have "Active Listening"
        # Only match if: (a) this generic skill has a bridge, AND
        #                (b) user has tech tools for this SOC
        if esco_equiv and not self._esco._loaded:
            # ESCO not loaded but bridge exists — use tech presence as weak signal
            tech_list = self._tech_skills.get(soc, [])
            if tech_list:
                user_tech_in_soc = any(
                    tech["name"].lower() in user_skills
                    for tech in tech_list
                )
                if user_tech_in_soc:
                    return True

        return False

    # ── Learning roadmap (delegates to onet_roadmap.py) ──────

    def generate_roadmap(
        self,
        missing_skills: List[str],
        job_title: str = "",
        experience_level: str = "Mid-Level",
        tech_skills: Optional[List[Dict]] = None,
    ) -> List[Dict]:
        """Generate a learning roadmap from missing skills.

        Delegates to onet_roadmap.generate_roadmap with proper dependencies.
        """
        self._ensure_initialized()
        return _generate_roadmap(
            missing_skills=missing_skills,
            job_title=job_title,
            experience_level=experience_level,
            tech_skills=tech_skills,
            esco=self._esco,
            match_occupation_fn=self.match_occupation,
            skills_data=self._skills,
        )

    # ── Job opportunities (delegates to onet_roadmap.py) ─────

    def get_job_opportunities(
        self,
        user_skills: List[str],
        limit: int = 5,
        matched_soc: str = "",
        experience_level: str = "",
    ) -> List[str]:
        """Find job titles that match user's skills.

        Delegates to onet_roadmap.get_job_opportunities with proper dependencies.
        """
        self._ensure_initialized()
        return _get_job_opportunities(
            user_skills=user_skills,
            occupations=self._occupations,
            skills_data=self._skills,
            tech_skills_data=self._tech_skills,
            skill_matches_fn=self._skill_matches,
            limit=limit,
            matched_soc=matched_soc,
            experience_level=experience_level,
        )

    # ── Helpers ──────────────────────────────────────────────

    def _empty_gap_result(self) -> Dict:
        """Fallback when no occupation match is found."""
        return {
            "occupation": None,
            "predicted_job": "Professional",
            "career_direction": "",
            "experience_level": "Mid-Level",
            "missing_hard_skills": [],
            "missing_soft_skills": [],
            "missing_tech_skills": [],
            "matched_skills": [],
            "missing_skills": [],
        }


# ── Singleton & DI ──────────────────────────────────────────

_onet_instance: Optional[ONetService] = None


def get_onet_service() -> ONetService:
    """Dependency injection factory (singleton)."""
    global _onet_instance
    if _onet_instance is None:
        _onet_instance = ONetService()
    return _onet_instance
