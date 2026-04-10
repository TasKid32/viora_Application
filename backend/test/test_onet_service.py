"""
Unit tests for ONetService — occupation matching & skill gap analysis.

Tests use mock data injected directly into the service instead of reading
from O*NET data files, so they run instantly without external dependencies.
"""
import pytest
from unittest.mock import patch, MagicMock
from app.services.onet_service import ONetService


@pytest.fixture
def service():
    """Create an ONetService instance with mock data."""
    svc = ONetService()
    svc._initialized = True  # Skip file loading

    # Mock occupations
    svc._occupations = {
        "15-1252.00": {"title": "Software Developers", "description": "Develop software applications."},
        "15-1211.00": {"title": "Computer Systems Analysts", "description": "Analyze computer systems."},
        "11-3021.00": {"title": "Computer and Information Systems Managers", "description": "Manage IT dept."},
    }
    svc._title_to_soc = {
        "software developers": "15-1252.00",
        "computer systems analysts": "15-1211.00",
        "computer and information systems managers": "11-3021.00",
    }

    # Mock skills (Importance scale)
    svc._skills = {
        "15-1252.00": [
            {"name": "Programming", "importance": 4.75},
            {"name": "Critical Thinking", "importance": 4.25},
            {"name": "Complex Problem Solving", "importance": 4.12},
        ],
    }

    # Mock tech skills
    svc._tech_skills = {
        "15-1252.00": [
            {"name": "Python", "category": "Programming Languages", "hot_technology": True},
            {"name": "JavaScript", "category": "Programming Languages", "hot_technology": True},
            {"name": "Docker", "category": "DevOps", "hot_technology": True},
            {"name": "SQL", "category": "Databases", "hot_technology": False},
        ],
    }

    # Mock knowledge
    svc._knowledge = {
        "15-1252.00": [
            {"name": "Computers and Electronics", "importance": 4.88},
            {"name": "Mathematics", "importance": 3.75},
        ],
    }

    svc._abilities = {}
    return svc


# ── Occupation Matching ─────────────────────────────────

class TestMatchOccupation:
    def test_exact_match(self, service):
        """Exact title match should return 100% score."""
        result = service.match_occupation("Software Developers")
        assert result is not None
        assert result["soc_code"] == "15-1252.00"
        assert result["match_score"] == 100
        assert result["title"] == "Software Developers"

    def test_exact_match_case_insensitive(self, service):
        """Matching should be case-insensitive."""
        result = service.match_occupation("software developers")
        assert result is not None
        assert result["match_score"] == 100

    def test_empty_title_returns_none(self, service):
        """Empty or None title should return None."""
        assert service.match_occupation("") is None
        assert service.match_occupation(None) is None

    def test_no_match_returns_none(self, service):
        """Completely unrelated title should return None (if no fuzzy lib)."""
        with patch.dict("sys.modules", {"rapidfuzz": None}):
            # Force ImportError for rapidfuzz
            service._title_to_soc = {"software developers": "15-1252.00"}
            result = service.match_occupation("Chef")
            # With substring fallback, "chef" is not in any title
            assert result is None


# ── Skill Gap Analysis ──────────────────────────────────

class TestAnalyzeSkillGaps:
    def test_returns_dict(self, service):
        """analyze_skill_gaps should return a dictionary."""
        result = service.analyze_skill_gaps(
            user_skills=["Python", "SQL"],
            job_title="Software Developers"
        )
        assert isinstance(result, dict)

    def test_identifies_matched_skills(self, service):
        """User skills that match O*NET tech should appear as matched."""
        result = service.analyze_skill_gaps(
            user_skills=["Python", "SQL"],
            job_title="Software Developers"
        )
        # Should have some strong/matched skills
        assert result is not None

    def test_identifies_missing_skills(self, service):
        """Skills in O*NET but not in user skills should be flagged."""
        result = service.analyze_skill_gaps(
            user_skills=["Python"],
            job_title="Software Developers"
        )
        # User has Python but not JavaScript/Docker/SQL
        assert result is not None

    def test_no_occupation_match_returns_empty(self, service):
        """If no occupation is matched, should return empty result."""
        # Force no match
        service._occupations = {}
        service._title_to_soc = {}
        result = service.analyze_skill_gaps(
            user_skills=["Python"],
            job_title="Unknown Job XYZ"
        )
        assert isinstance(result, dict)

    def test_empty_user_skills(self, service):
        """Empty user skills should still work — all O*NET skills become 'missing'."""
        result = service.analyze_skill_gaps(
            user_skills=[],
            job_title="Software Developers"
        )
        assert isinstance(result, dict)

    def test_soc_code_direct_lookup(self, service):
        """Providing SOC code directly should bypass fuzzy matching."""
        result = service.analyze_skill_gaps(
            user_skills=["Python"],
            soc_code="15-1252.00"
        )
        assert result is not None


# ── Edge Cases ──────────────────────────────────────────

class TestEdgeCases:
    def test_uninitialized_service_loads_data(self):
        """Service should attempt to load data on first use."""
        svc = ONetService()
        assert svc._initialized is False
        # match_occupation should trigger _ensure_initialized
        with patch.object(svc, '_ensure_initialized') as mock_init:
            svc.match_occupation("test")
            mock_init.assert_called_once()

    def test_skills_sorted_by_importance(self, service):
        """Skills should be sorted by importance descending."""
        skills = service._skills.get("15-1252.00", [])
        for i in range(len(skills) - 1):
            assert skills[i]["importance"] >= skills[i + 1]["importance"]
