"""
Viora NER — Build Gazetteer from O*NET and ESCO taxonomy data.

Reads ALL O*NET data files + ESCO skills (with altLabels),
extracts unique names, and saves them as JSON gazetteer files
for use in annotation validation AND runtime skill extraction.

Sources included:
  - O*NET skills.txt (Element Name)          → 35 core skills
  - O*NET technology_skills.txt (Example)    → ~8000 tools
  - O*NET knowledge.txt (Element Name)       → 33 knowledge areas
  - O*NET abilities.txt (Element Name)       → 52 abilities
  - ESCO skills_en.csv (preferredLabel)      → ~14,000 skills
  - ESCO skills_en.csv (altLabels)           → ~86,000 synonyms

Usage:
    python scripts/build_gazetteer.py
"""

import csv
import json
import os
import sys
from pathlib import Path
from collections import OrderedDict

# ── Paths ──────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
TAXONOMY_DIR = PROJECT_ROOT / "data" / "taxonomy"
ONET_DIR = TAXONOMY_DIR / "onet"
ESCO_DIR = TAXONOMY_DIR / "esco" / "ESCO dataset - v1.2.1 - classification - en - csv"
OUTPUT_DIR = PROJECT_ROOT / "data" / "gazetteers"


def read_onet_tsv(filepath: Path, name_col: int, skip_header: bool = True) -> set[str]:
    """Read a TSV file and extract unique values from a specific column."""
    names = set()
    if not filepath.exists():
        print(f"    ⚠️  File not found: {filepath}")
        return names

    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        if skip_header:
            next(reader, None)
        for row in reader:
            if len(row) > name_col:
                name = row[name_col].strip()
                if name and len(name) > 1:  # skip single-char entries
                    names.add(name)
    return names


def read_esco_csv(filepath: Path, include_alt_labels: bool = False) -> set[str]:
    """Read ESCO skills CSV and extract preferredLabel + altLabels.
    
    Args:
        filepath: Path to skills_en.csv
        include_alt_labels: If True, also extract altLabels (synonyms)
    
    Returns:
        Set of unique skill names
    """
    names = set()
    if not filepath.exists():
        print(f"    ⚠️  File not found: {filepath}")
        return names

    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # preferredLabel — always included
            label = row.get("preferredLabel", "").strip()
            if label and len(label) > 1:
                names.add(label)
            
            # altLabels — synonyms/alternative names
            if include_alt_labels:
                alt_labels = row.get("altLabels", "").strip()
                if alt_labels:
                    for alt in alt_labels.split("\n"):
                        alt = alt.strip()
                        if alt and len(alt) > 1:
                            names.add(alt)
    return names


def normalize_skill(name: str) -> str:
    """Normalize a skill name for consistent matching."""
    return name.strip().lower()


def build_skills_gazetteer() -> dict:
    """Build unified skills gazetteer from ALL O*NET + ESCO sources."""
    print("📦 Building skills gazetteer...")

    # 1. O*NET Skills (Element Name, col 2) — 35 core skills
    onet_skills = read_onet_tsv(ONET_DIR / "skills.txt", name_col=2)
    print(f"   ✅ O*NET skills.txt: {len(onet_skills)} unique skills")

    # 2. O*NET Technology Skills (Example, col 1) — ~8000 tools
    onet_tech = read_onet_tsv(ONET_DIR / "technology_skills.txt", name_col=1)
    print(f"   ✅ O*NET technology_skills.txt: {len(onet_tech)} unique technologies")

    # 3. O*NET Knowledge (Element Name, col 2) — 33 knowledge areas
    #    e.g. Chemistry, Biology, Medicine and Dentistry, Engineering
    onet_knowledge = read_onet_tsv(ONET_DIR / "knowledge.txt", name_col=2)
    print(f"   ✅ O*NET knowledge.txt: {len(onet_knowledge)} unique knowledge areas")

    # 4. O*NET Abilities (Element Name, col 2) — 52 abilities
    #    e.g. Deductive Reasoning, Finger Dexterity, Far Vision
    onet_abilities = read_onet_tsv(ONET_DIR / "abilities.txt", name_col=2)
    print(f"   ✅ O*NET abilities.txt: {len(onet_abilities)} unique abilities")

    # 5. ESCO Skills (preferredLabel + altLabels)
    esco_skills = read_esco_csv(ESCO_DIR / "skills_en.csv", include_alt_labels=True)
    print(f"   ✅ ESCO skills_en.csv (with altLabels): {len(esco_skills)} unique entries")

    # ── Step 6: Extract standalone short forms from existing entries ──
    # Many terms exist only as parts of longer entries:
    #   "Amazon Web Services AWS software" → need standalone "AWS"
    #   "Apache Kafka" → need standalone "Kafka"
    #   "hematology analysers" → need standalone "hematology"
    # This step extracts them automatically from the raw data.
    import re as _re

    all_raw_so_far = onet_skills | onet_tech | onet_knowledge | onet_abilities | esco_skills
    extracted_short_forms = set()

    for entry in all_raw_so_far:
        # Pattern 1: Extract uppercase abbreviations (2-6 chars) from entries
        # e.g. "Amazon Web Services AWS software" → "AWS"
        # e.g. "Laboratory Automated Quality Control Systems LAQC" → "LAQC"
        for abbr in _re.findall(r'\b([A-Z]{2,6})\b', entry):
            # Skip if it's just a common word in caps
            if abbr not in {'THE', 'AND', 'FOR', 'ALL', 'NOT', 'ARE', 'HAS',
                            'INC', 'LLC', 'LTD', 'USA', 'IBM'}:
                extracted_short_forms.add(abbr)

        # Pattern 2: Extract product names after vendor prefix
        # "Apache Kafka" → "Kafka", "Atlassian JIRA" → "JIRA"
        # "Microsoft Azure Data Factory" → "Azure"
        vendor_match = _re.match(
            r'^(?:Apache|Atlassian|Microsoft|Google|Amazon|Oracle|IBM|SAP|Adobe|Cisco)\s+(\w+)',
            entry
        )
        if vendor_match:
            product = vendor_match.group(1)
            if len(product) >= 2:
                extracted_short_forms.add(product)

        # Pattern 3: Extract standalone domain terms from compound entries
        # "clinical biochemistry" → "biochemistry"
        # "hematology analysers" → "hematology"
        # "assembly line teamwork" → "teamwork"
        modifiers = {'clinical', 'medical', 'applied', 'advanced', 'basic',
                     'general', 'digital', 'modern', 'industrial', 'routine'}
        suffixes = {'software', 'systems', 'tools', 'services', 'technologies',
                    'solutions', 'applications', 'management', 'analysers',
                    'analyzers', 'instruments', 'equipment', 'devices',
                    'procedures', 'techniques', 'processes', 'operations'}
        parts = entry.lower().split()

        if len(parts) >= 2:
            # "clinical biochemistry" → "biochemistry" (modifier + term)
            if parts[0] in modifiers and len(parts[1]) >= 4:
                extracted_short_forms.add(parts[1])
            # "hematology analysers" → "hematology" (term + suffix)
            if parts[-1] in suffixes and len(parts[0]) >= 4:
                extracted_short_forms.add(parts[0])
            # "quality control software" → "quality control" (2-word + suffix)
            if len(parts) >= 3 and parts[-1] in suffixes:
                core = ' '.join(parts[:-1])
                if len(core) >= 6:
                    extracted_short_forms.add(core)

        # Pattern 4: Extract meaningful last word from action phrases
        # "apply problem solving" → "problem solving"
        # "facilitate teamwork between students" → "teamwork"
        action_verbs = {'apply', 'use', 'perform', 'carry', 'conduct', 'manage',
                        'develop', 'facilitate', 'adapt', 'administer', 'assess',
                        'demonstrate', 'ensure', 'maintain', 'implement', 'assist'}
        if len(parts) >= 3 and parts[0] in action_verbs:
            # Extract 2-word core from position 1-2 only (NOT single words)
            # "apply problem solving" → "problem solving" ✅
            # "manage inventory control" → "inventory control" ✅
            # But NOT: "manage stock" → "stock" ❌ (too generic)
            if len(parts[1]) >= 3 and len(parts[2]) >= 3:
                candidate = f"{parts[1]} {parts[2]}"
                if len(candidate) >= 8:
                    extracted_short_forms.add(candidate)

    print(f"   ✅ Auto-extracted short forms: {len(extracted_short_forms)} terms")

    # ── Step 7: Verified-missing terms ──
    # Category A: Confirmed completely absent from ALL O*NET + ESCO files
    # Category B: Exist only in DESCRIPTIONS, never as preferredLabel/altLabel
    # (both verified by deep search on 2026-04-03)
    verified_missing = {
        # Category A: Completely absent
        "blood banking", "specimen collection", "urinalysis",
        "GCP", "FastAPI", "Express.js", "CI/CD",
        "Svelte", "gRPC", "serverless",
        # Category B: In descriptions only — common standalone CV terms
        # Verified present in ESCO/O*NET descriptions but NOT as labels
        "leadership", "teamwork", "problem solving",
        "anatomy", "physiology",
        "hematology", "serology",
        "quality control", "laboratory safety",
        "flow cytometry", "molecular diagnostics",
        "Rust",  # only false matches like "DataTrust" in gazetteer
    }
    print(f"   ✅ Verified-missing terms: {len(verified_missing)} terms")

    # Merge all skills
    all_skills_raw = all_raw_so_far | extracted_short_forms | verified_missing

    # Deduplicate by lowercase
    seen_lower = {}
    for skill in sorted(all_skills_raw):
        key = normalize_skill(skill)
        if key not in seen_lower:
            seen_lower[key] = skill

    # Sort final list
    skills_list = sorted(seen_lower.values(), key=str.lower)

    print(f"   📊 Total unique skills (after dedup): {len(skills_list)}")

    return {
        "skills": skills_list,
        "count": len(skills_list),
        "sources": [
            "onet_skills", "onet_technology_skills",
            "onet_knowledge", "onet_abilities",
            "esco_skills_with_altLabels",
        ],
    }


def build_job_titles_gazetteer() -> dict:
    """Build job titles gazetteer from O*NET occupations + ESCO."""
    print("\n📦 Building job titles gazetteer...")

    # O*NET Occupations (Title, col 1)
    titles = read_onet_tsv(ONET_DIR / "occupations.txt", name_col=1)
    print(f"   ✅ O*NET occupations.txt: {len(titles)} unique titles")

    # Also read ESCO occupations if available
    esco_occ_path = ESCO_DIR / "occupations_en.csv"
    if esco_occ_path.exists():
        esco_titles = read_esco_csv(esco_occ_path, include_alt_labels=True)
        print(f"   ✅ ESCO occupations_en.csv (with altLabels): {len(esco_titles)} unique titles")
        titles = titles | esco_titles

    # Deduplicate by lowercase
    seen_lower = {}
    for title in sorted(titles):
        key = normalize_skill(title)
        if key not in seen_lower:
            seen_lower[key] = title

    titles_list = sorted(seen_lower.values(), key=str.lower)

    print(f"   📊 Total unique job titles (after dedup): {len(titles_list)}")

    return {
        "job_titles": titles_list,
        "count": len(titles_list),
        "sources": ["onet_occupations", "esco_occupations_with_altLabels"],
    }


def main():
    print("=" * 60)
    print("🔧 Viora NER — Gazetteer Builder (v2 — Full Coverage)")
    print("=" * 60)

    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Build skills gazetteer
    skills_data = build_skills_gazetteer()
    skills_path = OUTPUT_DIR / "skills_gazetteer.json"
    with open(skills_path, "w", encoding="utf-8") as f:
        json.dump(skills_data, f, indent=2, ensure_ascii=False)
    print(f"   💾 Saved: {skills_path}")

    # Build job titles gazetteer
    titles_data = build_job_titles_gazetteer()
    titles_path = OUTPUT_DIR / "job_titles_gazetteer.json"
    with open(titles_path, "w", encoding="utf-8") as f:
        json.dump(titles_data, f, indent=2, ensure_ascii=False)
    print(f"   💾 Saved: {titles_path}")

    print("\n" + "=" * 60)
    print(f"🎉 Done! Skills: {skills_data['count']}, Job Titles: {titles_data['count']}")
    print("=" * 60)


if __name__ == "__main__":
    main()
