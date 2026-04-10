"""
Udemy Service — Smart search link generator.

Udemy's Affiliate API was discontinued on January 1, 2025.
This service generates optimized search URLs with advanced filters
(ratings, sort order, language) so users land on pre-filtered results.

Future: Can be upgraded to Rakuten Advertising Product Search API
when affiliate partnership is approved.
"""
from typing import List, Dict
from urllib.parse import quote_plus, urlencode

from app.core.logging import get_logger

logger = get_logger(__name__)

# ── Skill category → Udemy subcategory mapping ─────────────
# Maps common tech skills to Udemy's URL-friendly subcategory slugs
# This ensures users see the most relevant course category
_SKILL_CATEGORIES: Dict[str, str] = {
    # Programming Languages
    "python": "development/programming-languages/python/",
    "javascript": "development/programming-languages/javascript/",
    "java": "development/programming-languages/java/",
    "c++": "development/programming-languages/c-plus-plus/",
    "c#": "development/programming-languages/c-sharp/",
    "typescript": "development/programming-languages/typescript/",
    "go": "development/programming-languages/go/",
    "rust": "development/programming-languages/rust/",
    "ruby": "development/programming-languages/ruby/",
    "php": "development/programming-languages/php/",
    "swift": "development/programming-languages/swift/",
    "kotlin": "development/programming-languages/kotlin/",
    "r": "development/programming-languages/r/",
    # Web Development
    "react": "development/web-development/react/",
    "angular": "development/web-development/angular/",
    "vue": "development/web-development/vue-js/",
    "node.js": "development/web-development/node-js/",
    "django": "development/web-development/django/",
    "html": "development/web-development/html/",
    "css": "development/web-development/css/",
    # Data Science & AI
    "machine learning": "development/data-science/machine-learning/",
    "deep learning": "development/data-science/deep-learning/",
    "data science": "development/data-science/",
    "nlp": "development/data-science/natural-language-processing/",
    "tensorflow": "development/data-science/tensorflow/",
    "pytorch": "development/data-science/pytorch/",
    # DevOps & Cloud
    "docker": "development/devops/docker/",
    "kubernetes": "development/devops/kubernetes/",
    "aws": "it-and-software/it-certifications/aws-certified-solutions-architect-associate/",
    "azure": "it-and-software/it-certifications/microsoft-azure/",
    "devops": "development/devops/",
    "ci/cd": "development/devops/",
    "terraform": "development/devops/terraform/",
    # Databases
    "sql": "development/database/sql/",
    "postgresql": "development/database/postgresql/",
    "mongodb": "development/database/mongodb/",
    "mysql": "development/database/mysql/",
    # General
    "git": "development/software-engineering/git/",
    "api": "development/web-development/api-development/",
}


class UdemyService:
    """Udemy smart search link generator with pre-filtered URLs."""

    BASE = "https://www.udemy.com"

    def search_courses(
        self, query: str, max_results: int = 5, experience_level: str = ""
    ) -> List[Dict]:
        """
        Generate Udemy search results with smart, pre-filtered URLs.

        - If the skill matches a known category, generates a direct category link
        - Otherwise generates an optimized search URL with rating + sort filters
        - experience_level: 'Junior' | 'Mid-Level' | 'Senior' → maps to Udemy levels
        """
        if not query or not query.strip():
            return []

        query_clean = query.strip()
        query_lower = query_clean.lower()
        encoded = quote_plus(query_clean)

        # Map experience level to Udemy's instructional_level filter
        level_map = {
            "junior": "beginner",
            "mid-level": "intermediate",
            "senior": "expert",
        }
        udemy_level = level_map.get(experience_level.lower(), "")
        level_label = udemy_level.title() if udemy_level else "All Levels"

        # Check if skill maps to a specific Udemy category
        category_path = _SKILL_CATEGORIES.get(query_lower)

        # Build smart search URL with filters (ratings ≥ 4.0, sorted by relevance)
        search_params = {
            "q": query_clean,
            "sort": "relevance",
            "ratings": "4.0",
        }
        if udemy_level:
            search_params["instructional_level"] = udemy_level

        search_url = f"{self.BASE}/courses/search/?{urlencode(search_params)}"

        # Category URL (more specific, better results)
        if category_path:
            category_url = f"{self.BASE}/courses/{category_path}"
            if udemy_level:
                category_url += f"?instructional_level={udemy_level}"
        else:
            category_url = search_url

        results = [
            {
                "type": "course",
                "platform": "Udemy",
                "title": f"{query_clean} — Top Rated ({level_label})",
                "url": category_url,
                "thumbnail": None,
                "instructor": "Top Instructors",
                "rating": 4.5,
                "num_reviews": None,
                "price": "Paid (Discounts available)",
                "duration": "Self-paced",
                "level": level_label,
                "description": (
                    f"Browse top-rated {query_clean} courses on Udemy — "
                    f"filtered for {level_label} level."
                ),
            },
        ]

        # Add a search link if we used a category link above
        if category_path:
            results.append({
                "type": "course",
                "platform": "Udemy",
                "title": f"Search All: {query_clean}",
                "url": search_url,
                "thumbnail": None,
                "instructor": "Various",
                "rating": None,
                "num_reviews": None,
                "price": "Free & Paid",
                "duration": "Varies",
                "level": level_label,
                "description": (
                    f"Search all Udemy courses for '{query_clean}' "
                    f"including free courses."
                ),
            })

        return results[:max_results]



# Singleton
udemy_service = UdemyService()
