"""
Coursera Service — Smart search link generator.

Coursera's API requires partner-level access. This service generates
optimized search URLs with advanced filters (difficulty, subject)
so users land on pre-filtered, relevant results.
"""
from typing import List, Dict
from urllib.parse import urlencode


# ── Skill category → Coursera topic mapping ────────────────
_SKILL_TOPICS: Dict[str, str] = {
    "python": "data-science,computer-science",
    "javascript": "computer-science",
    "java": "computer-science",
    "react": "computer-science",
    "machine learning": "data-science",
    "deep learning": "data-science",
    "data science": "data-science",
    "sql": "data-science,computer-science",
    "aws": "cloud-computing,information-technology",
    "docker": "cloud-computing",
    "kubernetes": "cloud-computing",
    "devops": "cloud-computing",
    "cybersecurity": "information-technology",
    "project management": "business",
    "leadership": "business",
    "communication": "personal-development",
}


class CourseraService:
    BASE = "https://www.coursera.org"

    def search_courses(
        self, query: str, max_results: int = 5, experience_level: str = ""
    ) -> List[Dict]:
        """Generate smart Coursera search links with topic + difficulty filtering."""
        if not query or not query.strip():
            return []

        query_clean = query.strip()
        query_lower = query_clean.lower()

        # Map experience level to Coursera difficulty
        level_map = {
            "junior": "beginner",
            "mid-level": "intermediate",
            "senior": "advanced",
        }
        coursera_level = level_map.get(experience_level.lower(), "")
        level_label = coursera_level.title() if coursera_level else "All Levels"

        # Build search URL with smart topic + difficulty filters
        params = {"query": query_clean}

        topic = _SKILL_TOPICS.get(query_lower)
        if topic:
            params["topic"] = topic
        if coursera_level:
            params["productDifficultyLevel"] = coursera_level

        search_url = f"{self.BASE}/search?{urlencode(params)}"

        results = [
            {
                "type": "course",
                "platform": "Coursera",
                "title": f"{query_clean} — Coursera ({level_label})",
                "url": search_url,
                "thumbnail": None,
                "instructor": "Google, IBM, Meta, Top Universities",
                "duration": "Self-paced",
                "level": level_label,
                "rating": None,
                "price": "Free to Audit",
                "description": (
                    f"Browse {query_clean} courses, Professional Certificates, "
                    f"and Specializations — filtered for {level_label} level."
                ),
            },
        ]

        return results[:max_results]


# Singleton
coursera_service = CourseraService()
