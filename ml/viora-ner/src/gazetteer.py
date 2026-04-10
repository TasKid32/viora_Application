"""
Viora NER -- Gazetteer module for skill/job-title matching.

Loads gazetteer JSON files built by scripts/build_gazetteer.py
and provides fast lookup for entity validation.
"""

import json
import re
from pathlib import Path
from typing import Optional


class SkillGazetteer:
    """Fast lookup for known skills from O*NET + ESCO gazetteers."""

    def __init__(self, gazetteer_path: str | Path):
        """Load skills gazetteer from JSON file.

        Args:
            gazetteer_path: Path to skills_gazetteer.json
        """
        self.path = Path(gazetteer_path)
        with open(self.path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.skills_list: list[str] = data.get("skills", [])
        self.count: int = data.get("count", len(self.skills_list))

        # Build lookup set (lowercase for case-insensitive matching)
        self._skills_lower: set[str] = {s.lower() for s in self.skills_list}

        # Build multi-word index for text scanning
        # Sort by length descending so longer matches are found first
        self._sorted_skills = sorted(self.skills_list, key=len, reverse=True)
        self._sorted_lower = [s.lower() for s in self._sorted_skills]

    def is_known_skill(self, text: str) -> bool:
        """Check if text is a known skill (case-insensitive).

        Args:
            text: The text to check

        Returns:
            True if text matches a known skill
        """
        return text.strip().lower() in self._skills_lower

    def find_skills_in_text(self, text: str) -> list[tuple[int, int, str]]:
        """Find all known skills mentioned in text.

        Args:
            text: The text to search

        Returns:
            List of (start_idx, end_idx, skill_name) tuples
        """
        text_lower = text.lower()
        found = []
        used_ranges = []

        for skill, skill_lower in zip(self._sorted_skills, self._sorted_lower):
            start = 0
            while True:
                idx = text_lower.find(skill_lower, start)
                if idx == -1:
                    break
                end_idx = idx + len(skill_lower)

                # Check word boundaries
                if idx > 0 and text_lower[idx - 1].isalnum():
                    start = idx + 1
                    continue
                if end_idx < len(text_lower) and text_lower[end_idx].isalnum():
                    start = idx + 1
                    continue

                # Check for overlap with already-found matches
                overlap = False
                for ur_start, ur_end in used_ranges:
                    if not (end_idx <= ur_start or idx >= ur_end):
                        overlap = True
                        break

                if not overlap:
                    found.append((idx, end_idx, skill))
                    used_ranges.append((idx, end_idx))

                start = idx + 1

        # Sort by position
        found.sort(key=lambda x: x[0])
        return found

    def validate_entities(self, entities: list[dict]) -> dict:
        """Validate SKILL entities against gazetteer.

        Args:
            entities: List of entity dicts with 'text' and 'label' keys

        Returns:
            Dict with validation results:
                - total_skills: count of SKILL entities
                - known_skills: count matching gazetteer
                - unknown_skills: list of non-matching skill texts
                - coverage: percentage of known skills
        """
        skill_entities = [
            e for e in entities
            if e.get("label", "").upper() in ("SKILL", "B-SKILL", "I-SKILL")
        ]

        total = len(skill_entities)
        known = []
        unknown = []

        for ent in skill_entities:
            text = ent.get("text", "").strip()
            if self.is_known_skill(text):
                known.append(text)
            else:
                unknown.append(text)

        return {
            "total_skills": total,
            "known_skills": len(known),
            "unknown_skills": unknown,
            "coverage": len(known) / total if total > 0 else 0.0,
        }


class JobTitleGazetteer:
    """Fast lookup for known job titles from O*NET + ESCO."""

    def __init__(self, gazetteer_path: str | Path):
        """Load job titles gazetteer from JSON file."""
        self.path = Path(gazetteer_path)
        with open(self.path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.titles_list: list[str] = data.get("job_titles", [])
        self.count: int = data.get("count", len(self.titles_list))
        self._titles_lower: set[str] = {t.lower() for t in self.titles_list}

    def is_known_title(self, text: str) -> bool:
        """Check if text is a known job title (case-insensitive)."""
        return text.strip().lower() in self._titles_lower
