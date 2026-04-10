"""
Hybrid Analysis Service — Merges Viora NER + O*NET results.

Architecture:
1. Viora NER (ONNX) extracts entities locally (~100ms)
2. O*NET taxonomy provides skill gap analysis + roadmap (~50ms)
3. No external API calls needed for CV analysis

Total analysis time: <200ms (vs 5-10s with Gemini)
"""
import asyncio
from typing import Dict, List, Optional

from app.core.logging import get_logger
from app.services.viora_ner_service import get_ner_service, VioraNERService
from app.services.onet_service import get_onet_service, ONetService

logger = get_logger(__name__)


class HybridAnalysisService:
    """
    Hybrid NER + O*NET analysis pipeline.

    Combines:
    - Viora NER (ONNX): precise entity extraction from CV text
    - O*NET taxonomy: skill gap analysis using official occupational data
    """

    def __init__(self):
        self._ner: VioraNERService = get_ner_service()
        self._onet: ONetService = get_onet_service()

    async def analyze_cv(self, text: str) -> Dict:
        """
        Full hybrid CV analysis pipeline.

        1. Viora NER extracts entities (in thread — CPU-bound)
        2. O*NET matches occupation and analyzes gaps
        3. Results are merged into unified format

        Returns unified analysis result.
        """
        if not text or not text.strip():
            return self._empty_result()

        # Step 1: Extract entities with Viora NER (CPU-bound → run in thread)
        ner_result = await asyncio.to_thread(
            self._ner.extract_cv_structured, text
        )

        logger.info(
            "NER extracted: %d skills, job_titles=%s",
            len(ner_result.get("hard_skills", [])),
            ner_result.get("job_titles", []),
        )

        # Step 2: Determine job title from NER output
        job_titles = ner_result.get("job_titles", [])
        primary_job = job_titles[0] if job_titles else ""

        # Step 3: Analyze skill gaps with O*NET
        # IMPORTANT: Include BOTH hard skills (from NER) AND soft skills (from gazetteer)
        # Without soft_skills, "Critical Thinking" written in CV → classified as missing!
        user_skills = (
            ner_result.get("hard_skills", []) +
            ner_result.get("soft_skills", [])
        )
        parsed_years = ner_result.get("parsed_experience_years")

        # Detect if user has real work experience (not just graduation dates)
        # Fresh graduates: have CREDENTIAL but no real EXPERIENCE entities
        raw_entities = ner_result.get("raw_entities", {})
        has_credential = bool(raw_entities.get("CREDENTIAL"))
        has_real_experience = parsed_years is not None and parsed_years > 0

        gap_result = self._onet.analyze_skill_gaps(
            user_skills=user_skills,
            job_title=primary_job,
            experience_years=parsed_years,
            has_work_experience=has_real_experience,
        )

        logger.info(
            "O*NET analysis: job=%s, %d missing_hard, %d missing_soft, level=%s",
            gap_result.get("predicted_job", "?"),
            len(gap_result.get("missing_hard_skills", [])),
            len(gap_result.get("missing_soft_skills", [])),
            gap_result.get("experience_level", "?"),
        )

        # Step 4: Get job opportunities (with SOC context + experience filtering)
        matched_soc = gap_result.get("occupation", {}).get("soc_code", "") if gap_result.get("occupation") else ""
        exp_level = gap_result.get("experience_level", "")
        job_opportunities = self._onet.get_job_opportunities(
            user_skills,
            matched_soc=matched_soc,
            experience_level=exp_level,
        )

        # Step 5: Merge everything
        merged = self._merge_results(ner_result, gap_result, job_opportunities)

        logger.info(
            "Hybrid result: %d skills, %d missing, job=%s",
            len(merged.get("strong_skills", [])),
            len(merged.get("missing_skills", [])),
            merged.get("predicted_job", "?"),
        )

        return merged

    def _merge_results(
        self, ner: Dict, gaps: Dict, job_opportunities: List[str]
    ) -> Dict:
        """
        Merge NER entities + O*NET gap analysis into final result.

        - Skills, contact, education: from NER (precise extraction)
        - Job match, gaps, experience level: from O*NET (official data)
        - Job opportunities: from O*NET matching
        """

        strong_skills = ner.get("strong_skills", [])

        # Build hard/soft skill lists
        hard_skills = ner.get("hard_skills", [])
        soft_skills = ner.get("soft_skills", [])

        # Build recommendations — prioritize TECH SKILLS (specific tools)
        missing_hard = gaps.get("missing_hard_skills", [])
        missing_soft = gaps.get("missing_soft_skills", [])
        missing_tech = gaps.get("missing_tech_skills", [])

        recommendations = []
        target_job = gaps.get("predicted_job", "Professional")

        # Priority 1: Tech skills (Docker, AWS, EHR, Adobe, etc.)
        for tech in missing_tech[:3]:
            recommendations.append({
                "type": "learn",
                "skill": tech["skill"],
                "priority": tech["priority"],
                "target_job": target_job,
            })

        # Priority 2: Hard skills (only if we have fewer than 3 recommendations)
        remaining = 5 - len(recommendations)
        if remaining > 0:
            for skill in missing_hard[:remaining]:
                recommendations.append({
                    "type": "learn",
                    "skill": skill["skill"],
                    "priority": skill["priority"],
                    "target_job": target_job,
                })

        return {
            # Career info — from O*NET (official occupational data)
            "predicted_job": gaps.get("predicted_job", "Professional"),
            "career_direction": gaps.get("career_direction", ""),
            "experience_level": gaps.get("experience_level", "Mid-Level"),
            # Skills — from NER (precise extraction)
            "strong_skills": strong_skills,
            "hard_skills": hard_skills,
            "soft_skills": soft_skills,
            # Career opportunities — from O*NET matching
            "job_opportunities": job_opportunities,
            # Missing skills — from O*NET gap analysis
            "missing_skills": gaps.get("missing_skills", []),
            "missing_hard_skills": missing_hard,
            "missing_soft_skills": missing_soft,
            "missing_tech_skills": gaps.get("missing_tech_skills", []),
            "recommendations": recommendations,
            # gap_analysis wrapper — Mobile reads from this key
            "gap_analysis": {
                "predicted_job": gaps.get("predicted_job", "Professional"),
                "experience_level": gaps.get("experience_level", "Mid-Level"),
                "missing_skills": gaps.get("missing_skills", []),
                "missing_hard_skills": missing_hard,
                "missing_soft_skills": missing_soft,
                "missing_tech_skills": gaps.get("missing_tech_skills", []),
            },
            # Contact — from NER (precise extraction)
            "contact": ner.get("contact", {}),
            # Education — from NER
            "education": self._format_education(ner),
            "experience": ner.get("experience_years", []),
            # Additional NER data
            "companies": ner.get("companies", []),
            "projects": ner.get("projects", []),
            "languages": ner.get("languages", []),
            "experience_years": ner.get("experience_years", []),
            # Metadata
            "analysis_metadata": {
                "ner_skills_count": len(hard_skills),
                "onet_gaps_count": len(missing_hard) + len(missing_soft),
                "merged_skills_count": len(strong_skills),
                "ner_available": bool(hard_skills),
                "onet_available": bool(gaps.get("occupation")),
                "pipeline": "viora_ner_onnx + onet_taxonomy",
            },
        }

    def _format_education(self, ner: Dict) -> List[str]:
        """Format education data from NER extraction."""
        edu = ner.get("education", {})
        if isinstance(edu, dict):
            result = []
            result.extend(edu.get("degrees", []))
            result.extend(edu.get("universities", []))
            return result
        elif isinstance(edu, list):
            return edu
        return []

    def _empty_result(self) -> Dict:
        """Return empty result when no text provided."""
        return {
            "predicted_job": "Professional",
            "career_direction": "",
            "experience_level": "Mid-Level",
            "strong_skills": [],
            "hard_skills": [],
            "soft_skills": [],
            "job_opportunities": [],
            "strengths": [],
            "missing_skills": [],
            "missing_hard_skills": [],
            "missing_soft_skills": [],
            "missing_tech_skills": [],
            "recommendations": [],
            "contact": {},
            "education": [],
            "experience": [],
            "companies": [],
            "projects": [],
            "languages": [],
            "experience_years": [],
            "analysis_metadata": {
                "ner_skills_count": 0,
                "onet_gaps_count": 0,
                "merged_skills_count": 0,
                "ner_available": False,
                "onet_available": False,
                "pipeline": "viora_ner_onnx + onet_taxonomy",
            },
        }


# ── Singleton & DI ──────────────────────────────────────────────

_hybrid_instance: Optional[HybridAnalysisService] = None


def get_hybrid_service() -> HybridAnalysisService:
    """Dependency injection factory (singleton)."""
    global _hybrid_instance
    if _hybrid_instance is None:
        _hybrid_instance = HybridAnalysisService()
    return _hybrid_instance
