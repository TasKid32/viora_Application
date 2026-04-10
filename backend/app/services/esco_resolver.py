"""
ESCO Skill Resolver — Data-driven skill matching using ESCO v1.2.1 taxonomy.

Extracted from onet_service.py for Single Responsibility:
This module handles ONLY ESCO taxonomy operations.

Uses three data sources:
- skills_en.csv: 13,939 skills with 85,916 altLabels (synonym dictionary)
- broaderRelationsSkillPillar_en.csv: 14,575 hierarchy relations
- transversalSkillsCollection_en.csv: 96 transversal (soft) skills

Provides:
- resolve(skill) → hierarchy path (e.g. "python" → [..., "ICTs", "knowledge"])
- shares_ancestor(a, b) → bool (do two skills share a common category?)
- is_soft_skill(skill) → bool (is this a transversal/soft skill?)
"""
import csv
import io
from pathlib import Path
from typing import Dict, List, Optional

from app.core.logging import get_logger

logger = get_logger(__name__)


# Bridge mapping: O*NET generic skill → ESCO preferredLabel
# This is NOT hardcoding tools — it's a stable bridge between
# two classification systems (~20 mappings, rarely changes).
_ONET_TO_ESCO_BRIDGE: Dict[str, str] = {
    "programming": "computer programming",
    "mathematics": "mathematics",
    "active listening": "listen actively",
    "critical thinking": "think critically",
    "systems analysis": "perform system analysis",
    "quality control analysis": "conduct quality control analysis",
    "operations analysis": "operational research",
    "complex problem solving": "solve problems",
    "coordination": "coordinate activities",
    "monitoring": "monitor developments in field of expertise",
    "science": "apply scientific methods",
    "technology design": "design technology",
    "instructing": "instruct others",
    "writing": "write work-related reports",
    "speaking": "present reports",
    "reading comprehension": "interpret texts",
    "social perceptiveness": "show intercultural awareness",
    "persuasion": "use sales argumentation",
    "negotiation": "negotiate compromises",
    "service orientation": "identify customer's needs",
    "judgment and decision making": "make decisions",
    "time management": "manage time",
    "management of personnel resources": "manage staff",
    "learning strategies": "identify learning needs",
}


class ESCOSkillResolver:
    """Data-driven skill resolver using ESCO v1.2.1 taxonomy.

    Uses three data sources:
    - skills_en.csv: 13,939 skills with 85,916 altLabels (synonym dictionary)
    - broaderRelationsSkillPillar_en.csv: 14,575 hierarchy relations
    - transversalSkillsCollection_en.csv: 96 transversal (soft) skills

    Provides:
    - resolve(skill) → hierarchy path (e.g. "python" → [..., "ICTs", "knowledge"])
    - shares_ancestor(a, b) → bool (do two skills share a common category?)
    - is_soft_skill(skill) → bool (is this a transversal/soft skill?)
    """

    def __init__(self):
        self._alt_index: Dict[str, str] = {}       # 85K: altLabel.lower() → preferredLabel
        self._skill_to_uri: Dict[str, str] = {}    # preferredLabel.lower() → conceptUri
        self._broader: Dict[str, str] = {}          # uri → broader_uri
        self._uri_to_label: Dict[str, str] = {}     # uri → label
        self._soft_skills: Dict[str, set] = {}      # preferredLabel → {altLabels}
        self._soft_labels: set = set()              # all soft skill labels (pref + alt)
        self._resolve_cache: Dict[str, List[str]] = {}  # skill.lower() → cached path
        self._loaded = False

        # ESCO essential/optional per occupation
        self._occ_skill_relations: Dict[str, List[Dict]] = {}  # esco_occ_uri → [{skill, type}]
        self._esco_title_to_uri: Dict[str, str] = {}           # occ title.lower() → uri

    def load(self, esco_dir: Path) -> bool:
        """Load ESCO data files. Returns True if successful."""
        if self._loaded:
            return True

        if not esco_dir.exists():
            logger.warning("ESCO data directory not found: %s", esco_dir)
            return False

        try:
            self._load_skills(esco_dir / "skills_en.csv")
            self._load_broader(esco_dir / "broaderRelationsSkillPillar_en.csv")
            self._load_transversal(esco_dir / "transversalSkillsCollection_en.csv")
            self._load_occupation_skills(
                esco_dir / "occupationSkillRelations_en.csv",
                esco_dir / "occupations_en.csv",
            )
            self._loaded = True

            logger.info(
                "ESCO loaded: %d skills, %d altLabels, %d broader, %d soft, %d occ-skill rels",
                len(self._skill_to_uri),
                len(self._alt_index),
                len(self._broader),
                len(self._soft_labels),
                sum(len(v) for v in self._occ_skill_relations.values()),
            )
            return True
        except Exception as e:
            logger.error("Failed to load ESCO data: %s", e)
            return False

    # ── Data loading ─────────────────────────────────────────

    def _load_skills(self, filepath: Path):
        """Load skills_en.csv → build alt_index + skill_to_uri."""
        if not filepath.exists():
            logger.warning("ESCO skills file not found: %s", filepath)
            return

        text = filepath.read_text(encoding="utf-8")
        reader = csv.DictReader(io.StringIO(text))

        for row in reader:
            pref = row.get("preferredLabel", "").strip()
            uri = row.get("conceptUri", "").strip()
            alt = row.get("altLabels", "").strip()

            if not pref or not uri:
                continue

            pref_lower = pref.lower()
            self._skill_to_uri[pref_lower] = uri
            self._uri_to_label[uri] = pref

            # Also index preferredLabel as a lookup key
            self._alt_index[pref_lower] = pref

            if alt:
                for a in alt.split("\n"):
                    a_clean = a.strip()
                    if a_clean:
                        self._alt_index[a_clean.lower()] = pref

    def _load_broader(self, filepath: Path):
        """Load broaderRelationsSkillPillar_en.csv → hierarchy tree."""
        if not filepath.exists():
            logger.warning("ESCO broader relations file not found: %s", filepath)
            return

        text = filepath.read_text(encoding="utf-8")
        reader = csv.DictReader(io.StringIO(text))

        for row in reader:
            c_uri = row.get("conceptUri", "").strip()
            b_uri = row.get("broaderUri", "").strip()
            c_label = row.get("conceptLabel", "").strip()
            b_label = row.get("broaderLabel", "").strip()

            if c_uri and b_uri:
                self._broader[c_uri] = b_uri
                if c_label:
                    self._uri_to_label[c_uri] = c_label
                if b_label:
                    self._uri_to_label[b_uri] = b_label

    def _load_transversal(self, filepath: Path):
        """Load transversalSkillsCollection_en.csv → soft skills set."""
        if not filepath.exists():
            logger.warning("ESCO transversal file not found: %s", filepath)
            return

        text = filepath.read_text(encoding="utf-8")
        reader = csv.DictReader(io.StringIO(text))

        for row in reader:
            pref = row.get("preferredLabel", "").strip()
            if not pref:
                continue

            pref_lower = pref.lower()
            self._soft_labels.add(pref_lower)

            # Also add altLabels of transversal skills
            alt = row.get("altLabels", "").strip()
            alt_set = set()
            if alt:
                for a in alt.split("\n"):
                    a_clean = a.strip().lower()
                    if a_clean:
                        self._soft_labels.add(a_clean)
                        alt_set.add(a_clean)

            self._soft_skills[pref_lower] = alt_set

    def _load_occupation_skills(self, relations_path: Path, occupations_path: Path):
        """Load ESCO occupation-skill relations (essential/optional)."""
        if not relations_path.exists() or not occupations_path.exists():
            logger.warning("ESCO occupation-skill files not found")
            return

        # Load occupation titles → URIs
        text = occupations_path.read_text(encoding="utf-8")
        reader = csv.DictReader(io.StringIO(text))
        for row in reader:
            uri = row.get("conceptUri", "").strip()
            pref = row.get("preferredLabel", "").strip()
            if uri and pref:
                self._esco_title_to_uri[pref.lower()] = uri

        # Load relations
        text = relations_path.read_text(encoding="utf-8")
        reader = csv.DictReader(io.StringIO(text))
        for row in reader:
            occ_uri = row.get("occupationUri", "").strip()
            skill_uri = row.get("skillUri", "").strip()
            rel_type = row.get("relationType", "").strip()  # essential / optional
            skill_type = row.get("skillType", "").strip()

            if not occ_uri or not skill_uri:
                continue

            skill_label = self._uri_to_label.get(skill_uri, "")
            if not skill_label:
                continue

            if occ_uri not in self._occ_skill_relations:
                self._occ_skill_relations[occ_uri] = []

            self._occ_skill_relations[occ_uri].append({
                "skill_label": skill_label,
                "relation_type": rel_type,
                "skill_type": skill_type,
            })

    # ── Public API ───────────────────────────────────────────

    def resolve(self, user_skill: str) -> List[str]:
        """Resolve a user skill to its ESCO hierarchy path.

        Returns list of labels from specific → broad:
        e.g. "python" → ["Python (computer programming)",
              "computer programming", "software dev", "ICTs", "knowledge"]
        """
        if not self._loaded:
            return []

        skill_lower = user_skill.lower().strip()

        # Check cache first
        if skill_lower in self._resolve_cache:
            return self._resolve_cache[skill_lower]

        # Find matching ESCO preferredLabel
        pref = None
        if skill_lower in self._skill_to_uri:
            pref = skill_lower
        elif skill_lower in self._alt_index:
            pref = self._alt_index[skill_lower].lower()

        if not pref or pref not in self._skill_to_uri:
            return []

        # Walk up the hierarchy
        uri = self._skill_to_uri[pref]
        path = []
        seen = set()

        current = uri
        while current and current not in seen:
            seen.add(current)
            label = self._uri_to_label.get(current, "")
            if label:
                path.append(label.lower())
            current = self._broader.get(current)

        # Cache the result
        self._resolve_cache[skill_lower] = path
        return path

    def shares_ancestor(self, skill_a: str, skill_b: str, max_depth: int = 3) -> bool:
        """Check if two skills share a common ancestor in ESCO hierarchy.

        max_depth limits how far up the tree to check (avoids matching
        everything via top-level "knowledge" or "skills" nodes).
        """
        path_a = self.resolve(skill_a)
        path_b = self.resolve(skill_b)

        if not path_a or not path_b:
            return False

        # Trim paths to max_depth (skip first element = self)
        ancestors_a = set(path_a[1:max_depth + 1])
        ancestors_b = set(path_b[1:max_depth + 1])

        return bool(ancestors_a & ancestors_b)

    def normalize_skill(self, skill_name: str) -> str:
        """Resolve any variant/abbreviation to its ESCO canonical (preferredLabel).

        Uses the 85K altLabel index to normalize skill names:
          "CSS"      → "cascading style sheets"
          "CSS3"     → "cascading style sheets"  (altLabel match)
          "JS"       → "JavaScript"              (altLabel match)
          "Python"   → "Python (computer programming)"

        Returns the canonical name (lowercase), or the original input if not found.
        This is the KEY function for synonym resolution.
        """
        if not self._loaded:
            return skill_name.lower().strip()

        skill_lower = skill_name.lower().strip()

        # Direct preferredLabel match
        if skill_lower in self._skill_to_uri:
            return skill_lower

        # AltLabel → preferredLabel
        pref = self._alt_index.get(skill_lower)
        if pref:
            return pref.lower()

        return skill_lower

    def get_all_variants(self, skill_name: str) -> set:
        """Get ALL known variants/synonyms for a skill from ESCO.

        Given "cascading style sheets", returns {"css", "css3", ...}
        Given "CSS", first resolves to canonical, then returns all synonyms.

        Returns: set of lowercase variants (including the canonical name).
        """
        if not self._loaded:
            return {skill_name.lower().strip()}

        canonical = self.normalize_skill(skill_name)
        variants = {canonical}

        # Find the URI for this canonical name
        uri = self._skill_to_uri.get(canonical)
        if not uri:
            return variants

        # Collect all altLabels that resolve to this canonical name
        pref_label = self._uri_to_label.get(uri, "")
        if pref_label:
            variants.add(pref_label.lower())

        # Scan alt_index for all labels pointing to this preferredLabel
        for alt_lower, pref in self._alt_index.items():
            if pref.lower() == canonical:
                variants.add(alt_lower)

        return variants

    def is_soft_skill(self, skill_name: str) -> bool:
        """Check if a skill is a transversal/soft skill per ESCO.

        Uses three strategies:
        1. O*NET bridge: map O*NET name → ESCO name (e.g. 'Active Listening' → 'listen actively')
        2. Direct ESCO transversal label match
        3. Fallback keywords for common O*NET soft skills
        """
        skill_lower = skill_name.lower().strip()

        # Strategy 1: Check if O*NET skill name has a bridge to ESCO
        # Bridge maps O*NET names like "Active Listening" to ESCO "listen actively"
        esco_equiv = _ONET_TO_ESCO_BRIDGE.get(skill_lower)
        if esco_equiv:
            esco_equiv_lower = esco_equiv.lower()
            # Check if the ESCO equivalent is a transversal skill
            if esco_equiv_lower in self._soft_labels:
                return True

        # Strategy 2: Direct match against ESCO transversal labels
        if self._loaded and skill_lower in self._soft_labels:
            return True

        # Strategy 3: Fallback — O*NET generic soft skill names
        # (covers cases where neither ESCO nor bridge resolves)
        _ONET_SOFT_KEYWORDS = {
            "speaking", "writing", "listening", "reading comprehension",
            "social perceptiveness", "coordination", "persuasion",
            "negotiation", "instructing", "service orientation",
            "active listening", "critical thinking", "monitoring",
            "judgment and decision making", "time management",
            "management of personnel resources", "learning strategies",
            "active learning",
        }
        return skill_lower in _ONET_SOFT_KEYWORDS

    def get_essential_flag(self, onet_title: str, skill_name: str) -> Optional[bool]:
        """Check if a skill is essential for an occupation per ESCO.

        Returns True=essential, False=optional, None=unknown.
        """
        if not self._loaded:
            return None

        # Find ESCO occupation URI by fuzzy title match
        title_lower = onet_title.lower().strip()
        occ_uri = self._esco_title_to_uri.get(title_lower)

        if not occ_uri:
            # Try partial match
            for esco_title, uri in self._esco_title_to_uri.items():
                if title_lower in esco_title or esco_title in title_lower:
                    occ_uri = uri
                    break

        if not occ_uri or occ_uri not in self._occ_skill_relations:
            return None

        # Check if skill appears in this occupation's relations
        skill_lower = skill_name.lower().strip()
        for rel in self._occ_skill_relations[occ_uri]:
            rel_label = rel["skill_label"].lower()
            if skill_lower == rel_label or skill_lower in rel_label or rel_label in skill_lower:
                return rel["relation_type"] == "essential"

        return None
