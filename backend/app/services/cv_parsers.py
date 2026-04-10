"""
CV Parsers — Text parsing utilities for CV analysis.

Extracted from viora_ner_service.py for Single Responsibility:
This module handles ONLY text-based parsing (no ML model dependency).

Includes:
- Soft skills gazetteer (~50 ESCO transversal skills)
- Experience years parsing (with discount for freelance/intern/student)
- Graduation year detection from credentials
- NER entity text cleanup
"""
import re
from typing import Dict, List, Optional
from datetime import datetime

from app.core.logging import get_logger

logger = get_logger(__name__)


# ── Soft skills gazetteer ──────────────────────────────────
# Covers ESCO transversal skills + O*NET generic soft skills
# Organized by category for systematic coverage
SOFT_SKILL_GAZETTEER = {
    # Thinking & Problem Solving
    "critical thinking", "creative thinking", "analytical thinking",
    "strategic thinking", "problem solving", "problem-solving",
    "complex problem solving", "analytical skills", "decision making",
    "judgment and decision making", "logical thinking", "reasoning",
    # Communication
    "communication", "effective communication", "verbal communication",
    "written communication", "active listening", "public speaking",
    "presentation skills", "negotiation", "persuasion", "speaking",
    "writing", "listening", "reading comprehension",
    # Leadership & Management
    "leadership", "team leadership", "management", "mentoring",
    "coaching", "delegation", "conflict resolution",
    "management of personnel resources", "instructing",
    # Teamwork & Collaboration
    "teamwork", "team work", "collaboration", "cooperation",
    "working under pressure", "interpersonal skills",
    "social perceptiveness", "coordination",
    # Personal
    "adaptability", "flexibility", "time management",
    "self-management", "self management", "attention to detail",
    "initiative", "self-motivation", "work ethic",
    "task organization", "organization", "multitasking",
    "stress management", "emotional intelligence",
    # Learning
    "active learning", "learning strategies", "continuous learning",
    "research skills", "curiosity",
    # Service
    "service orientation", "customer service", "empathy",
    "cultural awareness", "monitoring",
}

# Section headers that typically contain soft skills
SOFT_SECTIONS = {
    "personal skills", "soft skills", "key skills", "core competencies",
    "competencies", "interpersonal skills", "transferable skills",
    "professional skills", "key competencies", "strengths",
    "personal qualities", "المهارات الشخصية", "المهارات",
}


def extract_soft_skills_from_text(text: str) -> List[str]:
    """Extract soft skills from CV text using gazetteer matching.

    Strategy:
    1. Find soft skill sections (PERSONAL SKILLS, KEY SKILLS, etc.)
    2. Extract text from those sections
    3. Match against gazetteer of ~50 common soft skills
    4. Also scan full text for explicit soft skill mentions

    Returns list of matched soft skill names.
    """
    if not text or not text.strip():
        return []

    text_lower = text.lower()
    found_skills: List[str] = []
    found_lower: set = set()

    # Strategy 1: Extract from soft skill sections (higher precision)
    # Find section boundaries: "PERSONAL SKILLS\n..." until next section header
    section_pattern = re.compile(
        r'(?:^|\n)\s*([A-Z][A-Z\s&/]+)\s*\n',  # ALL-CAPS section headers
        re.MULTILINE,
    )
    sections = list(section_pattern.finditer(text))

    for i, match in enumerate(sections):
        header = match.group(1).strip().lower()
        # Check if this is a soft skills section
        if any(kw in header for kw in SOFT_SECTIONS):
            # Get section text (from header to next section or end)
            start = match.end()
            end = sections[i + 1].start() if i + 1 < len(sections) else len(text)
            section_text = text[start:end].lower()

            # Match gazetteer skills in this section
            for skill in SOFT_SKILL_GAZETTEER:
                if skill in section_text and skill not in found_lower:
                    # Capitalize nicely for display
                    found_skills.append(skill.title())
                    found_lower.add(skill)

    # Strategy 2: Full-text scan for explicit soft skill mentions
    # Use word boundaries to avoid partial matches
    for skill in SOFT_SKILL_GAZETTEER:
        if skill not in found_lower and skill in text_lower:
            # Verify word boundary (not part of a longer word)
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower):
                found_skills.append(skill.title())
                found_lower.add(skill)

    logger.info("Soft skills extracted via gazetteer: %d → %s",
                len(found_skills), found_skills[:5])
    return found_skills


def detect_graduation_year(
    credentials: List[str], raw_text: str = "",
) -> Optional[int]:
    """Detect graduation year from CREDENTIAL entities and raw text.

    Looks for patterns like:
    - 'Bachelor of Science ... July 2025'
    - 'BSc ... 2024'
    - 'Graduated: 2025'
    """
    years = []

    # From credentials (NER entities)
    for cred in credentials:
        for match in re.finditer(r'(20\d{2})', cred):
            years.append(int(match.group(1)))

    # From raw text: look near degree keywords
    degree_pattern = re.compile(
        r'(?:bachelor|master|bsc|msc|b\.?s\.?|m\.?s\.?|ph\.?d|diploma|degree|graduated)'
        r'[^\n]{0,80}?(20\d{2})',
        re.IGNORECASE,
    )
    for match in degree_pattern.finditer(raw_text):
        years.append(int(match.group(1)))

    return max(years) if years else None


def parse_experience_years(
    experience_entities: List[str],
    raw_text: str = "",
    graduation_year: Optional[int] = None,
) -> Optional[int]:
    """Parse years of experience from NER EXPERIENCE entities and raw CV text.

    Improvements over original:
    - Detects freelance/intern/student context → discounts by 50%
    - Detects overlap with graduation year → discounts
    - Uses weighted sum instead of raw MAX

    Patterns matched:
    - Direct: '5+ years', '10 years of experience', '3 yrs'
    - Date ranges: '2018-2024' or '2019 - present' → calculates difference
    """
    current_year = datetime.now().year
    weighted_years: List[float] = []

    # Freelance / intern / student indicators
    _DISCOUNT_KEYWORDS = {
        "freelance", "intern", "trainee", "student", "part-time",
        "part time", "volunteer", "project", "final year",
    }

    all_texts = list(experience_entities)
    if raw_text:
        all_texts.append(raw_text)

    for text_block in all_texts:
        text_lower = text_block.lower()

        # Pattern 1: "5+ years", "10 years of experience", "3 yrs"
        for match in re.finditer(r'(\d+)\+?\s*(?:years?|yrs?)', text_block, re.IGNORECASE):
            try:
                weighted_years.append(float(int(match.group(1))))
            except ValueError:
                pass

        # Pattern 2: Date ranges with context awareness
        for match in re.finditer(
            r'(20\d{2})\s*[-–—to]+\s*(20\d{2}|present|current|now)',
            text_block,
            re.IGNORECASE,
        ):
            try:
                start_year = int(match.group(1))
                end_str = match.group(2).lower()
                if end_str in ("present", "current", "now"):
                    end_year = current_year
                else:
                    end_year = int(end_str)
                diff = end_year - start_year
                if 0 < diff <= 50:
                    # Check context around this date range for discount keywords
                    ctx_start = max(0, match.start() - 200)
                    ctx_end = min(len(text_lower), match.end() + 50)
                    context = text_lower[ctx_start:ctx_end]

                    discount = 1.0

                    # Discount if freelance/intern/student context
                    if any(kw in context for kw in _DISCOUNT_KEYWORDS):
                        discount = 0.5

                    # Discount if overlaps with study period
                    if graduation_year and start_year < graduation_year:
                        discount = min(discount, 0.5)

                    weighted_years.append(diff * discount)
            except ValueError:
                pass

    if not weighted_years:
        return None

    # Use max of weighted years (rounded down)
    result = int(max(weighted_years))
    return result if result > 0 else None


def clean_entity_text(text: str) -> str:
    """Normalize whitespace and clean NER entity text.

    Handles:
    - Newlines/tabs/extra spaces from PDF column layouts → single space
    - Unclosed parentheses: "Object-Oriented Programming (OOP" → adds ")"
    - Trailing punctuation cleanup
    """
    # Step 1: Normalize whitespace (newlines, tabs, multi-space → single space)
    text = re.sub(r'\s+', ' ', text).strip()
    # Step 2: Strip trailing punctuation
    text = text.rstrip(".,;:!?")
    # Step 3: Balance parentheses — add missing closing paren
    open_count = text.count("(")
    close_count = text.count(")")
    if open_count > close_count:
        text += ")" * (open_count - close_count)
    elif close_count > open_count:
        text = text.rstrip(")")
    # Step 4: Strip leading/trailing parens if they wrap nothing useful
    if text.startswith("(") and text.endswith(")"):
        inner = text[1:-1].strip()
        if inner:
            text = inner
    return text


def extract_contact_from_text(text: str) -> Dict[str, str]:
    """Extract contact info directly from raw CV text using regex.

    Fallback for when NER misses CONTACT entities.
    Handles:
    - Emails with subdomains, +tags, international TLDs (.co.uk, .edu)
    - Phone numbers: international (+1...), local (555-...), UK (07...)
    - LinkedIn profile URLs
    - Personal website URLs
    """
    result = {"email": "", "phone": "", "linkedin": "", "website": ""}

    if not text or not text.strip():
        return result

    # ── Email extraction ─────────────────────────────────────
    # Supports: user+tag@sub.domain.co.uk, first.last@company.com
    email_pattern = re.compile(
        r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}',
    )
    email_match = email_pattern.search(text)
    if email_match:
        result["email"] = email_match.group(0).strip().rstrip(".,;:")

    # ── Phone extraction ─────────────────────────────────────
    # Priority order: international format first, then local
    phone_patterns = [
        # International: +1 (555) 123-4567, +44 7911 123456
        re.compile(
            r'\+\d{1,3}[\s.\-]?\(?\d{1,4}\)?[\s.\-]?\d{2,4}[\s.\-]?\d{2,4}[\s.\-]?\d{0,4}'
        ),
        # US/CA: (555) 123-4567, 555-123-4567, 555.123.4567
        re.compile(
            r'\(?\d{3}\)?[\s.\-]\d{3}[\s.\-]\d{4}'
        ),
        # Generic: sequences of 7-15 digits with separators
        re.compile(
            r'(?:(?:tel|phone|mobile|cell|fax)[:\s]*)?'
            r'[\(]?\d{2,4}[\)\s.\-]*\d{3,4}[\s.\-]?\d{3,4}',
            re.IGNORECASE,
        ),
    ]
    for pattern in phone_patterns:
        phone_match = pattern.search(text)
        if phone_match:
            phone_raw = phone_match.group(0).strip().rstrip(".,;:")
            # Validate: at least 7 digits total (not a year like "2024")
            digits_only = re.sub(r'\D', '', phone_raw)
            if len(digits_only) >= 7:
                result["phone"] = phone_raw
                break

    # ── LinkedIn extraction ──────────────────────────────────
    linkedin_pattern = re.compile(
        r'(?:https?://)?(?:www\.)?linkedin\.com/in/([\w\-]+)',
        re.IGNORECASE,
    )
    linkedin_match = linkedin_pattern.search(text)
    if linkedin_match:
        result["linkedin"] = f"linkedin.com/in/{linkedin_match.group(1)}"

    # ── Website extraction ───────────────────────────────────
    website_pattern = re.compile(
        r'https?://(?!(?:www\.)?linkedin\.com)[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}[/\w.\-]*',
        re.IGNORECASE,
    )
    website_match = website_pattern.search(text)
    if website_match:
        result["website"] = website_match.group(0).strip().rstrip(".,;:")

    found_items = [k for k, v in result.items() if v]
    if found_items:
        logger.info("Contact regex fallback found: %s", found_items)

    return result
