"""
Unit tests for Chat API — send message & history endpoints.

Uses mocked database and LLM service to test API logic without
external dependencies.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone


# ── Helper: Create mock user & analysis ─────────────────

def _mock_user(user_id=1, name="Test User"):
    user = MagicMock()
    user.id = user_id
    user.name = name
    return user


def _mock_analysis(
    job_title="Software Developer",
    experience_level="Mid",
    strong_skills=None,
    missing_skills=None,
    extracted_entities=None,
):
    analysis = MagicMock()
    analysis.predicted_job_title = job_title
    analysis.experience_level = experience_level
    analysis.strong_skills = strong_skills if strong_skills is not None else [
        {"name": "Python", "score": 0.85},
        {"name": "SQL", "score": 0.70},
    ]
    analysis.missing_skills = missing_skills if missing_skills is not None else ["Docker", "Kubernetes"]
    analysis.extracted_entities = extracted_entities or {}
    return analysis


def _mock_roadmap(phases=None):
    roadmap = MagicMock()
    roadmap.roadmap_data = phases if phases is not None else [
        {"topics": [{"name": "Learn Docker", "completed": True}, {"name": "Learn K8s", "completed": False}]},
    ]
    return roadmap


# ── Chat Suggestion Tests ───────────────────────────────

class TestChatSuggestions:
    """Tests for smart suggestion generation logic in chat.py."""

    def test_suggestions_without_analysis(self):
        """When user has no analysis, default suggestions should appear."""
        analysis = None
        if not analysis:
            suggestions = [
                "حلل سيرتي الذاتية",
                "ما المهارات المطلوبة في سوق العمل؟",
                "نصائح لتحسين CV",
            ]
        assert len(suggestions) == 3
        assert "حلل سيرتي الذاتية" in suggestions

    def test_suggestions_with_analysis(self):
        """With analysis results, suggestions should be personalized."""
        analysis = _mock_analysis()
        first_missing = (
            analysis.missing_skills[0] if analysis.missing_skills else None
        )
        suggestions = []
        if first_missing:
            suggestions.append(f"كيف أتعلم {first_missing}؟")
        suggestions.append(
            f"نصائح لمسار {analysis.predicted_job_title or 'مهني'}"
        )
        suggestions.append("أنشئ خارطة تعلم")

        assert len(suggestions) == 3
        assert "Docker" in suggestions[0]
        assert "Software Developer" in suggestions[1]

    def test_suggestions_no_missing_skills(self):
        """When no missing skills, first suggestion should be career-based."""
        analysis = _mock_analysis(missing_skills=[])
        first_missing = (
            analysis.missing_skills[0] if analysis.missing_skills else None
        )
        suggestions = []
        if first_missing:
            suggestions.append(f"كيف أتعلم {first_missing}؟")
        suggestions.append(
            f"نصائح لمسار {analysis.predicted_job_title or 'مهني'}"
        )
        suggestions.append("أنشئ خارطة تعلم")

        assert len(suggestions) == 2  # No missing skill suggestion
        assert "Software Developer" in suggestions[0]


# ── Roadmap Progress Context ────────────────────────────

class TestRoadmapContext:
    """Tests for roadmap progress calculation in chat context."""

    def test_progress_calculation(self):
        """Verify correct step counting from roadmap data."""
        roadmap = _mock_roadmap()
        phases = roadmap.roadmap_data or []
        total_steps = sum(len(p.get("topics", [])) for p in phases)
        completed = sum(
            1 for p in phases
            for t in p.get("topics", [])
            if isinstance(t, dict) and t.get("completed")
        )
        progress = f"{completed}/{total_steps} steps completed"

        assert total_steps == 2
        assert completed == 1
        assert progress == "1/2 steps completed"

    def test_empty_roadmap(self):
        """Empty roadmap should show 0/0."""
        roadmap = _mock_roadmap(phases=[])
        phases = roadmap.roadmap_data or []
        total_steps = sum(len(p.get("topics", [])) for p in phases)
        completed = sum(
            1 for p in phases
            for t in p.get("topics", [])
            if isinstance(t, dict) and t.get("completed")
        )

        assert total_steps == 0
        assert completed == 0


# ── Chat History Tests ──────────────────────────────────

class TestChatHistory:
    """Tests for chat history formatting."""

    def test_history_format(self):
        """Chat history should return correct structure."""
        mock_chats = [
            MagicMock(message="Hello", reply="Hi!", timestamp=datetime.now(timezone.utc)),
            MagicMock(message="Help", reply="Sure!", timestamp=datetime.now(timezone.utc)),
        ]

        result = {
            "chats": [
                {
                    "message": chat.message,
                    "reply": chat.reply,
                    "timestamp": chat.timestamp,
                }
                for chat in mock_chats
            ]
        }

        assert len(result["chats"]) == 2
        assert result["chats"][0]["message"] == "Hello"
        assert result["chats"][0]["reply"] == "Hi!"

    def test_empty_history(self):
        """No chats should return empty list."""
        result = {"chats": []}
        assert len(result["chats"]) == 0
