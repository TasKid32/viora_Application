"""
O*NET Data Loader — Loads occupations, skills, tech skills, knowledge, abilities.

Extracted from onet_service.py for Single Responsibility:
This module handles ONLY file I/O and parsing of O*NET TSV data files.

Data files loaded:
- occupations.txt: SOC Code → Title → Description (900+ occupations)
- skills.txt: SOC Code → Skill → Importance scale
- technology_skills.txt: SOC Code → Tool → Category → Hot Technology flag
- knowledge.txt: SOC Code → Knowledge Area → Importance
- abilities.txt: SOC Code → Ability → Importance
"""
import csv
import io
from pathlib import Path
from typing import Dict, List

from app.core.logging import get_logger

logger = get_logger(__name__)


def load_occupations(filepath: Path) -> tuple:
    """Load occupations.txt (SOC Code → Title → Description).

    Returns:
        (occupations dict, title_to_soc dict)
    """
    occupations: Dict[str, Dict] = {}
    title_to_soc: Dict[str, str] = {}

    text = filepath.read_text(encoding="utf-8")
    reader = csv.DictReader(io.StringIO(text), delimiter="\t")

    for row in reader:
        soc = row.get("O*NET-SOC Code", "").strip()
        title = row.get("Title", "").strip()
        desc = row.get("Description", "").strip()

        if soc and title:
            occupations[soc] = {
                "title": title,
                "description": desc,
            }
            title_to_soc[title.lower()] = soc

    return occupations, title_to_soc


def load_skills(filepath: Path) -> Dict[str, List[Dict]]:
    """Load skills.txt (SOC Code → Skill → Importance/Level).

    Only loads Importance (IM) scale, skips Level (LV).
    Now also loads Element ID and Not Relevant flag for taxonomy-aware
    skill classification (transferable vs domain-specific).

    Returns: {soc_code: [{name, importance, element_id, not_relevant, is_transferable}, ...]}
    """
    skills: Dict[str, List[Dict]] = {}

    text = filepath.read_text(encoding="utf-8")
    reader = csv.DictReader(io.StringIO(text), delimiter="\t")

    for row in reader:
        soc = row.get("O*NET-SOC Code", "").strip()
        name = row.get("Element Name", "").strip()
        element_id = row.get("Element ID", "").strip()
        scale = row.get("Scale ID", "").strip()
        value = row.get("Data Value", "0").strip()
        not_relevant = row.get("Not Relevant", "").strip()

        if not soc or not name or scale != "IM":
            # Only load Importance (IM) scale, skip Level (LV)
            continue

        try:
            importance = float(value)
        except ValueError:
            continue

        if soc not in skills:
            skills[soc] = []

        # Element ID taxonomy:
        #   2.A.* = Basic Skills (Reading, Writing, Math, Science, etc.)
        #   2.B.* = Cross-Functional Skills (Problem Solving, Systems, etc.)
        # Both are transferable — any educated/experienced person has them.
        is_transferable = (
            element_id.startswith("2.A.") or element_id.startswith("2.B.")
        )

        skills[soc].append({
            "name": name,
            "importance": importance,
            "element_id": element_id,
            "not_relevant": not_relevant == "Y",
            "is_transferable": is_transferable,
        })

    # Sort each occupation's skills by importance (highest first)
    for soc in skills:
        skills[soc].sort(key=lambda x: x["importance"], reverse=True)

    return skills


def load_tech_skills(filepath: Path) -> Dict[str, List[Dict]]:
    """Load technology_skills.txt (SOC → Tool → Category → Hot → In Demand).

    Now also loads In Demand flag for market-driven prioritization.
    Returns: {soc_code: [{name, category, hot_technology, in_demand}, ...]}
    """
    tech_skills: Dict[str, List[Dict]] = {}

    text = filepath.read_text(encoding="utf-8")
    reader = csv.DictReader(io.StringIO(text), delimiter="\t")

    for row in reader:
        soc = row.get("O*NET-SOC Code", "").strip()
        example = row.get("Example", "").strip()
        category = row.get("Commodity Title", "").strip()
        hot = row.get("Hot Technology", "").strip()
        in_demand = row.get("In Demand", "").strip()

        if not soc or not example:
            continue

        if soc not in tech_skills:
            tech_skills[soc] = []

        tech_skills[soc].append({
            "name": example,
            "category": category,
            "hot_technology": hot == "Y",
            "in_demand": in_demand == "Y",
        })

    return tech_skills


def load_knowledge(filepath: Path) -> Dict[str, List[Dict]]:
    """Load knowledge.txt (SOC → Knowledge Area → Importance).

    Knowledge areas: 'Administration and Management', 'Economics and Accounting',
    'Computers and Electronics', 'Engineering and Technology', etc.
    Same format as skills.txt — we only load Scale ID = 'IM' (Importance).

    Returns: {soc_code: [{name, importance}, ...]}
    """
    knowledge: Dict[str, List[Dict]] = {}

    if not filepath.exists():
        logger.warning("knowledge.txt not found at: %s", filepath)
        return knowledge

    text = filepath.read_text(encoding="utf-8")
    reader = csv.DictReader(io.StringIO(text), delimiter="\t")

    for row in reader:
        soc = row.get("O*NET-SOC Code", "").strip()
        name = row.get("Element Name", "").strip()
        scale = row.get("Scale ID", "").strip()
        value = row.get("Data Value", "0").strip()

        if not soc or not name or scale != "IM":
            continue

        try:
            importance = float(value)
        except ValueError:
            continue

        if soc not in knowledge:
            knowledge[soc] = []

        knowledge[soc].append({
            "name": name,
            "importance": importance,
        })

    # Sort by importance
    for soc in knowledge:
        knowledge[soc].sort(key=lambda x: x["importance"], reverse=True)

    return knowledge


def load_abilities(filepath: Path) -> Dict[str, List[Dict]]:
    """Load abilities.txt (SOC → Ability → Importance).

    Abilities: 'Oral Comprehension', 'Problem Sensitivity',
    'Deductive Reasoning', 'Mathematical Reasoning', etc.
    Same format — only load Scale ID = 'IM'.

    Returns: {soc_code: [{name, importance}, ...]}
    """
    abilities: Dict[str, List[Dict]] = {}

    if not filepath.exists():
        logger.warning("abilities.txt not found at: %s", filepath)
        return abilities

    text = filepath.read_text(encoding="utf-8")
    reader = csv.DictReader(io.StringIO(text), delimiter="\t")

    for row in reader:
        soc = row.get("O*NET-SOC Code", "").strip()
        name = row.get("Element Name", "").strip()
        scale = row.get("Scale ID", "").strip()
        value = row.get("Data Value", "0").strip()

        if not soc or not name or scale != "IM":
            continue

        try:
            importance = float(value)
        except ValueError:
            continue

        if soc not in abilities:
            abilities[soc] = []

        abilities[soc].append({
            "name": name,
            "importance": importance,
        })

    # Sort by importance
    for soc in abilities:
        abilities[soc].sort(key=lambda x: x["importance"], reverse=True)

    return abilities


# ── Job title aliases ────────────────────────────────────
# Maps common job titles / degree names → O*NET occupation titles.
# match_occupation() uses SUBSTRING matching: if any alias key
# appears IN the NER-extracted job title, we match to that O*NET title.
# Example: "Senior Litigation Attorney" contains "attorney" → "Lawyers"
JOB_ALIASES: Dict[str, str] = {
    # ── IT / Software ──
    "information technology": "Software Developers",
    "information technology engineering": "Software Developers",
    "computer science": "Software Developers",
    "computer engineering": "Software Developers",
    "software engineering": "Software Developers",
    "software developer": "Software Developers",
    "software engineer": "Software Developers",
    "it engineering": "Software Developers",
    "web developer": "Web Developers",
    "web development": "Web Developers",
    "data science": "Data Scientists",
    "data scientist": "Data Scientists",
    "data analyst": "Data Scientists",
    "artificial intelligence": "Data Scientists",
    "machine learning": "Data Scientists",
    "cybersecurity": "Information Security Analysts",
    "information security": "Information Security Analysts",
    "network engineering": "Network and Computer Systems Administrators",
    "database administration": "Database Administrators",
    "systems administration": "Network and Computer Systems Administrators",
    "devops": "Software Developers",
    # ── Legal ──
    "attorney": "Lawyers",
    "lawyer": "Lawyers",
    "counsel": "Lawyers",
    "solicitor": "Lawyers",
    "litigation": "Lawyers",
    "law": "Lawyers",
    "paralegal": "Paralegals and Legal Assistants",
    "legal assistant": "Paralegals and Legal Assistants",
    "judge": "Judges, Magistrate Judges, and Magistrates",
    "magistrate": "Judges, Magistrate Judges, and Magistrates",
    # ── Medical / Healthcare ──
    "nursing": "Registered Nurses",
    "nurse": "Registered Nurses",
    "physician": "Physicians, All Other",
    "doctor": "Physicians, All Other",
    "medicine": "Physicians, All Other",
    "surgeon": "Surgeons",
    "pharmacy": "Pharmacists",
    "pharmacist": "Pharmacists",
    "dentistry": "Dentists, General",
    "dentist": "Dentists, General",
    "physical therapy": "Physical Therapists",
    "physical therapist": "Physical Therapists",
    "therapist": "Physical Therapists",
    "psychologist": "Psychologists, All Other",
    "psychology": "Psychologists, All Other",
    # ── Engineering ──
    "electrical engineering": "Electrical Engineers",
    "electrical engineer": "Electrical Engineers",
    "mechanical engineering": "Mechanical Engineers",
    "mechanical engineer": "Mechanical Engineers",
    "civil engineering": "Civil Engineers",
    "civil engineer": "Civil Engineers",
    "chemical engineering": "Chemical Engineers",
    "chemical engineer": "Chemical Engineers",
    "industrial engineering": "Industrial Engineers",
    "industrial engineer": "Industrial Engineers",
    "environmental engineering": "Environmental Engineers",
    "biomedical engineering": "Biomedical Engineers",
    "petroleum engineering": "Petroleum Engineers",
    # ── Business / Finance ──
    "business administration": "Management Analysts",
    "consultant": "Management Analysts",
    "management consultant": "Management Analysts",
    "marketing": "Market Research Analysts and Marketing Specialists",
    "marketing manager": "Market Research Analysts and Marketing Specialists",
    "accounting": "Accountants and Auditors",
    "accountant": "Accountants and Auditors",
    "auditor": "Accountants and Auditors",
    "finance": "Financial and Investment Analysts",
    "financial analyst": "Financial and Investment Analysts",
    "economist": "Economists",
    "economics": "Economists",
    # ── Education ──
    "professor": "Political Science Teachers, Postsecondary",
    "teacher": "Secondary School Teachers, Except Special and Career/Technical Education",
    "instructor": "Secondary School Teachers, Except Special and Career/Technical Education",
    "tutor": "Tutors",
    # ── Creative / Design ──
    "graphic design": "Graphic Designers",
    "graphic designer": "Graphic Designers",
    "interior design": "Interior Designers",
    "interior designer": "Interior Designers",
    "architect": "Architects, Except Landscape and Naval",
    "architecture": "Architects, Except Landscape and Naval",
    "ui designer": "Graphic Designers",
    "ux designer": "Graphic Designers",
    # ── Media / Communication ──
    # NOTE: O*NET data lacks "Reporters and Correspondents" (SOC 27-3022),
    # so we map to the closest available occupation.
    "journalism": "Public Relations Managers",
    "journalist": "Public Relations Managers",
    "investigative journalist": "Public Relations Managers",
    "reporter": "Public Relations Managers",
    "public relations": "Public Relations Specialists",
    # ── HR / Social ──
    "human resources manager": "Human Resources Managers",
    "human resources director": "Human Resources Managers",
    "human resources": "Human Resources Specialists",
    "hr manager": "Human Resources Managers",
    "hr director": "Human Resources Managers",
    "recruiter": "Human Resources Specialists",
    "social work": "Social Workers, All Other",
    "social worker": "Social Workers, All Other",
    # ── Other ──
    "geology": "Geoscientists, Except Hydrologists and Geographers",
    "project manager": "Project Management Specialists",
    "chef": "Chefs and Head Cooks",
    "real estate": "Real Estate Sales Agents",
    "dental hygienist": "Dental Hygienists",
    "supply chain": "Logisticians",
}
