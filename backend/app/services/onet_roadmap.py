"""
O*NET Roadmap Generator — Learning roadmap and job opportunity generation.

Extracted from onet_service.py for Single Responsibility:
This module handles ONLY roadmap phase generation and job matching.
"""
from typing import Dict, List, Optional, Tuple

from app.core.logging import get_logger

logger = get_logger(__name__)


def generate_roadmap(
    missing_skills: List[str],
    job_title: str,
    experience_level: str,
    tech_skills: Optional[List[Dict]],
    esco,
    match_occupation_fn,
    skills_data: Dict[str, List[Dict]],
) -> List[Dict]:
    """
    Generate a learning roadmap from missing skills.

    Uses TWO sources of skills (works for ALL professions):
    - tech_skills: Specific tools from technology_skills.txt (Docker, EHR, Adobe, ERP)
      → These are the PRIMARY source, especially Hot Technology items
    - missing_skills: Generic competencies from skills.txt (Programming, Mathematics)
      → These are SECONDARY, and soft skills are filtered out

    Args:
        missing_skills: List of missing skill names
        job_title: Target job title
        experience_level: Junior/Mid-Level/Senior
        tech_skills: List of missing tech skill dicts
        esco: ESCOSkillResolver instance (for soft skill filtering)
        match_occupation_fn: Callable to match job title → occupation
        skills_data: Dict of SOC → skill list

    Returns: [{phase, duration, topics, priority}, ...]
    """
    tech_skills = tech_skills or []

    # ── Soft skills to EXCLUDE from roadmap (not learnable as courses) ──
    # Uses ESCO transversal skills for unified classification
    # (replaces separate hardcoded soft_skill_names list)

    # ── Phase 1: Build topics from TECH SKILLS (primary) ──
    # Three-tier classification:
    #   1. Hot Technology → Foundations (BLS confirmed industry standard)
    #   2. In Demand → Intermediate (growing job postings)
    #   3. Other relevant tools → Advanced (domain-specific, not trivial)
    # Use the ACTUAL TOOL NAME as topic (e.g. "Docker", "PostgreSQL")
    # instead of O*NET Commodity Title (e.g. "Database management system software")
    # because tool names are searchable on YouTube/Coursera/edX.
    hot_topics = []        # Hot Technology → Foundations
    in_demand_topics = []  # In Demand → Intermediate
    other_topics = []      # Other relevant → Advanced
    seen_categories = set()  # Deduplicate by category

    for tech in tech_skills:
        skill_name = tech.get("skill", "")
        category = tech.get("category", "")
        is_hot = tech.get("hot_technology", False)
        is_in_demand = tech.get("in_demand", False)

        if not skill_name:
            continue

        # Deduplicate by category — max 1 tool per category
        # (prevents 5 different "Development environment" tools)
        dedup_key = (category if category else skill_name).lower()
        if dedup_key in seen_categories:
            continue
        seen_categories.add(dedup_key)

        # Use the ACTUAL tool name as topic — searchable on all platforms
        # "Docker" → finds real tutorials. "Platform and container software" → does not.
        topic = skill_name

        if is_hot:
            hot_topics.append(topic)
        elif is_in_demand:
            in_demand_topics.append(topic)
        else:
            # Tier 3: Other tools — include if priority is not "Low"
            # or if the category is domain-specific (not trivial)
            if tech.get("priority", "Low") != "Low":
                other_topics.append(topic)

    # ── Phase 2: Build topics from GENERIC SKILLS (secondary) ──
    # Only include non-soft, important generic skills.
    # Sort by O*NET importance score: higher importance = more foundational
    # → learned FIRST. This works for ALL professions:
    #   Nurse:      "Active Listening" (4.38) before "Monitoring" (3.75)
    #   Developer:  "Programming" (4.75) before "Systems Analysis" (3.50)
    #   Accountant: "Mathematics" (4.25) before "Negotiation" (3.00)
    generic_topics = []
    soft_skill_topics = []  # Learnable soft skills → separate phase
    importance_scores: Dict[str, float] = {}  # Track score for sorting later

    # Soft skills that CAN be learned via courses/workshops
    # (vs. personality traits that are not "learnable")
    _LEARNABLE_SOFT = {
        "complex problem solving", "judgment and decision making",
        "persuasion", "negotiation", "time management",
        "coordination", "instructing", "social perceptiveness",
        "service orientation", "monitoring", "management of personnel resources",
        "management of financial resources", "management of material resources",
    }

    if missing_skills:
        occupation = match_occupation_fn(job_title) if job_title else None
        soc = occupation["soc_code"] if occupation else ""
        required = skills_data.get(soc, [])

        # Build importance map from O*NET data
        importance_map: Dict[str, float] = {}
        for s in required:
            importance_map[s["name"].lower()] = s["importance"]

        for skill in missing_skills:
            skill_lower = skill.lower().strip()

            # Classify: soft skill vs hard skill
            if esco.is_soft_skill(skill):
                # Only include LEARNABLE soft skills (not personality traits)
                if skill_lower in _LEARNABLE_SOFT:
                    soft_skill_topics.append(skill)
                continue

            # Include generic hard skills with importance >= 3.0
            # (lowered from 3.5 to catch more real learning gaps)
            imp = importance_map.get(skill_lower, 2.5)
            if imp >= 3.0:
                generic_topics.append(skill)
                importance_scores[skill.lower()] = imp

    # ── Sort generic skills by O*NET importance (data-driven ordering) ──
    # Higher importance = more foundational → learn FIRST.
    # This replaces any hardcoded prerequisite maps and works
    # universally across ALL 1,000+ O*NET occupations.
    generic_topics.sort(key=lambda t: importance_scores.get(t.lower(), 2.5),
                        reverse=True)

    # Tech skills keep their existing order from _tech_relevance_score()
    # which already uses: user-category match > occupation-frequency > market demand
    # (set in onet_service.py Step 1) — no re-sorting needed.

    # ── Build phases (topic count based on experience level) ──
    phases = []

    # Experience-based topic limits: Junior needs more, Senior needs less
    if experience_level == "Junior":
        phase_limit = 5
    elif experience_level == "Senior":
        phase_limit = 3
    else:  # Mid-Level
        phase_limit = 4

    # Foundations: Hot Technology (top priority for any profession)
    foundation_topics = hot_topics[:phase_limit]
    if not foundation_topics and in_demand_topics:
        # If no hot tech, use first few in-demand tech
        foundation_topics = in_demand_topics[:phase_limit]
        in_demand_topics = in_demand_topics[phase_limit:]

    if foundation_topics:
        phases.append({
            "phase": "Foundations",
            "duration": f"{max(2, len(foundation_topics))} weeks",
            "topics": foundation_topics,
            "priority": "High",
        })

    # Intermediate: In Demand tech skills + other relevant tools
    intermediate_topics = in_demand_topics[:phase_limit]
    # Fill remaining slots with other relevant tools
    remaining_slots = phase_limit - len(intermediate_topics)
    if remaining_slots > 0 and other_topics:
        intermediate_topics.extend(other_topics[:remaining_slots])
        other_topics = other_topics[remaining_slots:]

    if intermediate_topics:
        phases.append({
            "phase": "Intermediate",
            "duration": f"{max(2, len(intermediate_topics))} weeks",
            "topics": intermediate_topics,
            "priority": "Medium",
        })

    # Advanced: Important generic skills (non-soft only) — real learning gaps
    # These are skills like Programming, Systems Analysis, Quality Control
    # that the auto-assume fix now properly identifies as missing.
    advanced_topics = generic_topics[:phase_limit]
    if advanced_topics:
        phases.append({
            "phase": "Advanced",
            "duration": f"{max(2, len(advanced_topics))} weeks",
            "topics": advanced_topics,
            "priority": "Medium",
        })

    # Professional Development: Learnable soft skills
    # Skills like "Persuasion", "Complex Problem Solving", "Time Management"
    # are genuinely trainable via courses and workshops.
    if soft_skill_topics:
        dev_topics = soft_skill_topics[:phase_limit]
        phases.append({
            "phase": "Professional Development",
            "duration": f"{max(2, len(dev_topics))} weeks",
            "topics": dev_topics,
            "priority": "Medium",
        })

    # Specialization: Remaining other tools (if any left)
    specialization_topics = other_topics[:phase_limit]
    if specialization_topics:
        phases.append({
            "phase": "Specialization",
            "duration": f"{max(2, len(specialization_topics))} weeks",
            "topics": specialization_topics,
            "priority": "Low",
        })

    # Fallback: if no tech skills at all, use filtered generic skills
    if not phases and missing_skills:
        filtered = [s for s in missing_skills if not esco.is_soft_skill(s)]
        if filtered:
            phases.append({
                "phase": "Foundations",
                "duration": f"{max(2, len(filtered[:phase_limit]))} weeks",
                "topics": filtered[:phase_limit],
                "priority": "High",
            })

    return phases


def get_job_opportunities(
    user_skills: List[str],
    occupations: Dict[str, Dict],
    skills_data: Dict[str, List[Dict]],
    tech_skills_data: Dict[str, List[Dict]],
    skill_matches_fn,
    limit: int = 5,
    matched_soc: str = "",
    experience_level: str = "",
) -> List[str]:
    """
    Find job titles that match user's skills.

    Returns list of O*NET job titles sorted by match quality.
    Improvements:
    - SOC prefix bonus: same SOC family gets +5 boost
    - Management filter: Junior → exclude SOC 11-xxxx
    - Tech cap raised: 5 → 15

    Args:
        user_skills: List of user skill strings
        occupations: SOC → {title, description}
        skills_data: SOC → [{name, importance}]
        tech_skills_data: SOC → [{name, category, hot_technology}]
        skill_matches_fn: Callable(skill_name, user_lower) → bool
        limit: Max results
        matched_soc: SOC code of matched occupation (for family bonus)
        experience_level: Junior/Mid-Level/Senior
    """
    if not user_skills:
        return []

    user_lower = {s.lower().strip() for s in user_skills if s}
    scores: List[Tuple[str, int]] = []

    # Extract SOC prefix for family bonus
    # 4-digit prefix for sub-family matching:
    #   "29-10" (pharmacists) ≠ "29-20" (therapists)
    # 2-digit prefix for broad family (fallback bonus)
    soc_prefix_4 = matched_soc[:5] if matched_soc else ""
    soc_prefix_2 = matched_soc[:2] if matched_soc else ""

    for soc, skills_list in skills_data.items():
        if soc not in occupations:
            continue

        # Skip user's own occupation
        if matched_soc and soc == matched_soc:
            continue

        # Management filter: exclude SOC 11-xxxx for Junior
        if experience_level == "Junior" and soc.startswith("11-"):
            continue

        match_count = 0
        for skill in skills_list:
            if skill_matches_fn(skill["name"], user_lower):
                match_count += 1

        # Also check tech skills for this occupation
        tech_list = tech_skills_data.get(soc, [])
        tech_match_count = sum(
            1 for tech in tech_list
            if tech["name"].lower() in user_lower
        )

        total_match = match_count + min(tech_match_count, 15)  # Cap raised 5→15

        # SOC prefix bonus: 4-digit sub-family gets high boost,
        # 2-digit broad family gets smaller boost
        if soc_prefix_4 and soc.startswith(soc_prefix_4):
            total_match += 8  # Same sub-family (strong relevance)
        elif soc_prefix_2 and soc.startswith(soc_prefix_2 + "-"):
            total_match += 2  # Same broad family (weak relevance)

        if total_match >= 4:  # Minimum match threshold
            title = occupations[soc]["title"]
            scores.append((title, total_match))

    # Sort by match count (highest first), deduplicate
    scores.sort(key=lambda x: x[1], reverse=True)
    seen = set()
    result = []
    for title, _ in scores:
        if title not in seen:
            seen.add(title)
            result.append(title)
        if len(result) >= limit:
            break
    return result
