"""
edX Service — Smart search link generator.

edX's catalog API has limited access. This service generates
optimized search URLs targeting edX's academic course offerings
from MIT, Harvard, and other top institutions.
"""
from typing import List, Dict
from urllib.parse import quote_plus, urlencode


# ── Skill → edX subject mapping ────────────────────────────
_SKILL_SUBJECTS: Dict[str, str] = {
    "python": "computer-science",
    "javascript": "computer-science",
    "java": "computer-science",
    "machine learning": "data-science",
    "deep learning": "data-science",
    "data science": "data-science",
    "statistics": "data-science",
    "aws": "computer-science",
    "cybersecurity": "computer-science",
    "leadership": "business-management",
    "management": "business-management",
    "communication": "communication",
    "engineering": "engineering",
    "mathematics": "math",
}


class EdXService:
    BASE = "https://www.edx.org"

    def search_courses(
        self, query: str, max_results: int = 5, experience_level: str = ""
    ) -> List[Dict]:
        """Generate smart edX search links with subject + difficulty filtering."""
        if not query or not query.strip():
            return []

        query_clean = query.strip()
        query_lower = query_clean.lower()

        # Map experience level to edX level
        level_map = {
            "junior": "introductory",
            "mid-level": "intermediate",
            "senior": "advanced",
        }
        edx_level = level_map.get(experience_level.lower(), "")
        level_label = edx_level.title() if edx_level else "All Levels"

        # Build search URL
        params = {"q": query_clean}

        subject = _SKILL_SUBJECTS.get(query_lower)
        if subject:
            params["subject"] = subject
        if edx_level:
            params["level"] = edx_level

        search_url = f"{self.BASE}/search?{urlencode(params)}"

        results = [
            {
                "type": "course",
                "platform": "edX",
                "title": f"{query_clean} — edX ({level_label})",
                "url": search_url,
                "thumbnail": None,
                "instructor": "MIT, Harvard, Top Universities",
                "duration": "Self-paced",
                "level": level_label,
                "rating": None,
                "price": "Free (Verified Certificate Available)",
                "description": (
                    f"Browse {query_clean} courses, MicroMasters, "
                    f"and Professional Certificates — filtered for {level_label} level."
                ),
            },
        ]

        return results[:max_results]


# Singleton
edx_service = EdXService()
