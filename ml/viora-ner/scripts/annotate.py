#!/usr/bin/env python3
"""
Step 2: Re-annotate resume texts using Groq API (Llama 3.3 70B).
Free tier, no credit card needed, ~30 RPM, ~14,400 RPD.

Usage:
    python scripts/annotate.py --api-key YOUR_GROQ_KEY --limit 5   # test
    python scripts/annotate.py --api-key YOUR_GROQ_KEY              # full
    python scripts/annotate.py --api-key YOUR_GROQ_KEY --resume     # resume
"""

import json
import os
import re
import sys
import time
import argparse
from pathlib import Path
from typing import Optional

from groq import Groq

# ─── Entity Schema ───────────────────────────────────────────────────────────

ENTITY_LABELS = [
    "PERSON", "ORG", "LOCATION", "SKILL",
    "JOB_TITLE", "CREDENTIAL", "CONTACT", "EXPERIENCE",
]

# ─── Prompt ───────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are an expert NER annotator for resumes/CVs.
Your task: Given a resume text, extract ALL named entities with their EXACT character offsets.

ENTITY TYPES:
- PERSON: Full name of the resume owner (usually at the top)
- ORG: Companies, universities, schools, organizations
- LOCATION: Cities, states, countries, full addresses
- SKILL: Technical skills, programming languages, tools, frameworks, libraries, methodologies, soft skills
- JOB_TITLE: Job titles and professional roles (e.g., "Senior Software Engineer", "Data Analyst")
- CREDENTIAL: Academic degrees, certifications, licenses (e.g., "B.Tech", "MBA", "AWS Certified Solutions Architect")
- CONTACT: Email addresses, phone numbers, LinkedIn/GitHub URLs, websites
- EXPERIENCE: Date ranges for employment or education periods (e.g., "Jan 2019 - Dec 2021", "2015-2019")

CRITICAL RULES:
1. Every entity's start and end offsets must correspond EXACTLY to the substring in the original text.
2. text[start:end] must equal the entity text exactly - no extra/missing characters.
3. Do NOT overlap entities - each character belongs to at most one entity.
4. Prefer specific labels: "Python" -> SKILL, "Google" -> ORG, "B.Tech" -> CREDENTIAL.
5. For compound items like "B.Tech in Computer Science", label "B.Tech" as CREDENTIAL and "Computer Science" as SKILL.
6. Date ranges like "Jan 2019 to Dec 2021" -> EXPERIENCE (not SKILL or ORG).
7. Job titles like "Senior Data Engineer" -> JOB_TITLE (not SKILL).
8. University names like "MIT", "Stanford University" -> ORG (not PERSON or SKILL).
9. Only annotate meaningful entities, skip noise, articles, prepositions.
10. Be thorough - capture ALL skills, ALL companies, ALL dates, ALL credentials.

Output ONLY a valid JSON array. Each element must have exactly these keys:
  {"text": "exact substring", "start": integer, "end": integer, "label": "ENTITY_TYPE"}

Example:
[
  {"text": "John Smith", "start": 0, "end": 10, "label": "PERSON"},
  {"text": "Software Engineer", "start": 11, "end": 28, "label": "JOB_TITLE"},
  {"text": "Google LLC", "start": 32, "end": 42, "label": "ORG"},
  {"text": "Python", "start": 43, "end": 49, "label": "SKILL"},
  {"text": "B.Tech", "start": 56, "end": 62, "label": "CREDENTIAL"},
  {"text": "2015-2019", "start": 72, "end": 81, "label": "EXPERIENCE"}
]"""

USER_PROMPT_TEMPLATE = """Annotate the following resume text. Return ONLY the JSON array of entities.

RESUME TEXT:
---
{text}
---

JSON entities:"""


# ─── Model rotation list (ordered by preference) ─────────────────────────────

ALL_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "qwen/qwen3-32b",
    "meta-llama/llama-4-scout-17b-16e-instruct",
    # "openai/gpt-oss-20b",  # BROKEN: can't produce JSON
    # "meta-llama/llama-4-maverick-17b-128e-instruct",  # BROKEN: garbage NER
]

# ─── Annotator ────────────────────────────────────────────────────────────────

class GroqAnnotator:
    def __init__(self, api_key: str, model: str = "llama-3.3-70b-versatile"):
        self.client = Groq(api_key=api_key, timeout=60.0)
        self.model = model
        self.rpm_limit = 28
        self.request_times = []
        self.json_mode = True
        # Build rotation list starting from the specified model
        self.exhausted_models = set()
        self.model_list = [model] + [m for m in ALL_MODELS if m != model]

    def _rate_limit(self):
        """Enforce rate limiting"""
        now = time.time()
        self.request_times = [t for t in self.request_times if now - t < 60]
        if len(self.request_times) >= self.rpm_limit:
            wait_time = 60 - (now - self.request_times[0]) + 2
            if wait_time > 0:
                print(f"    [Rate limit] Waiting {wait_time:.0f}s...", flush=True)
                time.sleep(wait_time)
        self.request_times.append(time.time())

    def annotate(self, text: str, max_retries: int = 5) -> Optional[list[dict]]:
        """Send text to Groq for NER annotation"""
        # Truncate very long texts to fit context window
        max_len = 30000
        if len(text) > max_len:
            text = text[:max_len]

        prompt = USER_PROMPT_TEMPLATE.format(text=text)

        for attempt in range(max_retries):
            try:
                self._rate_limit()

                kwargs = dict(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.0,
                    max_tokens=8192,
                )
                if self.json_mode:
                    kwargs["response_format"] = {"type": "json_object"}

                response = self.client.chat.completions.create(**kwargs)

                raw = response.choices[0].message.content
                if not raw:
                    print(f"    [WARN] Empty response (attempt {attempt+1})", flush=True)
                    # After 2 empty responses, this model is broken for NER — switch
                    if attempt >= 2:
                        self.exhausted_models.add(self.model)
                        print(f"    [BROKEN] {self.model} returns empty — skipping!", flush=True)
                        switched = False
                        for m in self.model_list:
                            if m not in self.exhausted_models:
                                self.model = m
                                self.json_mode = True
                                print(f"    [SWITCH] Now using: {self.model}", flush=True)
                                switched = True
                                break
                        if not switched:
                            return None
                    time.sleep(2)
                    continue
                raw = raw.strip()

                # Parse JSON - strip markdown fences if any
                if raw.startswith("```"):
                    raw = re.sub(r"^```(?:json)?\s*", "", raw)
                    raw = re.sub(r"\s*```$", "", raw)

                # Try to find JSON array in the response
                if not raw.startswith("[") and not raw.startswith("{"):
                    match = re.search(r'(\[.*\])', raw, re.DOTALL)
                    if match:
                        raw = match.group(1)

                parsed = json.loads(raw)

                # Handle both {"entities": [...]} and [...] formats
                if isinstance(parsed, dict):
                    # Try common keys
                    for key in ["entities", "results", "annotations", "data"]:
                        if key in parsed and isinstance(parsed[key], list):
                            entities = parsed[key]
                            break
                    else:
                        # If dict has entity-like values, wrap in list
                        entities = [parsed] if "text" in parsed else []
                elif isinstance(parsed, list):
                    entities = parsed
                else:
                    print(f"    [WARN] Unexpected format (attempt {attempt+1})", flush=True)
                    continue

                if not isinstance(entities, list):
                    continue

                return entities

            except json.JSONDecodeError as e:
                print(f"    [WARN] JSON parse error (attempt {attempt+1})", flush=True)
                time.sleep(2)

            except KeyboardInterrupt:
                print("\n[INTERRUPTED] Saving progress...", flush=True)
                raise

            except Exception as e:
                err = str(e).lower()
                err_short = str(e)[:200]
                print(f"    [ERROR] {err_short}", flush=True)

                # Check JSON validation errors FIRST
                if "json_validate_failed" in err or "failed to generate json" in err:
                    print(f"    [WARN] JSON validation failed (attempt {attempt+1})", flush=True)
                    time.sleep(2)
                    continue
                elif "413" in str(e) or "request too large" in err:
                    # Text too large for model, truncate more aggressively
                    max_len = max_len // 2
                    text = text[:max_len]
                    prompt = USER_PROMPT_TEMPLATE.format(text=text)
                    print(f"    [TOO LARGE] Truncating to {max_len} chars, retrying...", flush=True)
                    continue
                elif "tokens per day" in err or "tpd" in err:
                    self.exhausted_models.add(self.model)
                    print(f"    [TPD LIMIT] {self.model} exhausted!", flush=True)
                    switched = False
                    for m in self.model_list:
                        if m not in self.exhausted_models:
                            self.model = m
                            self.json_mode = True
                            print(f"    [SWITCH] Now using: {self.model}", flush=True)
                            switched = True
                            break
                    if not switched:
                        print(f"    [ALL EXHAUSTED] All models hit TPD. Stop.", flush=True)
                        return None
                    continue
                elif "429" in str(e) or "rate_limit" in err:
                    wait = min(60 * (attempt + 1), 120)
                    print(f"    [Rate limited] Waiting {wait}s...", flush=True)
                    time.sleep(wait)
                elif "timeout" in err or "timed out" in err or "connection" in err:
                    wait = 10 * (attempt + 1)
                    print(f"    [NETWORK] Retrying in {wait}s...", flush=True)
                    time.sleep(wait)
                elif "api_key" in err or "auth" in err or "401" in str(e):
                    print(f"    [AUTH] Check your API key!", flush=True)
                    return None
                else:
                    time.sleep(5 * (attempt + 1))

        return None


# ─── Validation ───────────────────────────────────────────────────────────────

def validate_entities(text: str, entities: list[dict]) -> tuple[list[dict], dict]:
    """Validate and fix entity offsets."""
    valid = []
    stats = {"total": len(entities), "valid": 0, "fixed": 0, "dropped": 0, "overlap_removed": 0}

    for ent in entities:
        if not isinstance(ent, dict):
            stats["dropped"] += 1
            continue
        if not all(k in ent for k in ("text", "start", "end", "label")):
            stats["dropped"] += 1
            continue

        label = ent["label"]
        if label not in ENTITY_LABELS:
            stats["dropped"] += 1
            continue

        ent_text = str(ent["text"])
        start = ent["start"]
        end = ent["end"]

        if not isinstance(start, int) or not isinstance(end, int):
            try:
                start, end = int(start), int(end)
            except (ValueError, TypeError):
                stats["dropped"] += 1
                continue

        if start < 0 or end > len(text) or start >= end:
            idx = text.find(ent_text)
            if idx >= 0:
                start, end = idx, idx + len(ent_text)
                stats["fixed"] += 1
            else:
                stats["dropped"] += 1
                continue

        actual = text[start:end]
        if actual != ent_text:
            idx = text.find(ent_text)
            if idx >= 0:
                start, end = idx, idx + len(ent_text)
                stats["fixed"] += 1
            else:
                idx = text.lower().find(ent_text.lower())
                if idx >= 0:
                    ent_text = text[idx:idx+len(ent_text)]
                    start, end = idx, idx + len(ent_text)
                    stats["fixed"] += 1
                else:
                    stats["dropped"] += 1
                    continue

        valid.append({"text": ent_text, "start": start, "end": end, "label": label})

    # Remove overlaps (keep longer entities)
    valid.sort(key=lambda e: (e["start"], -(e["end"] - e["start"])))
    non_overlapping = []
    last_end = -1
    for ent in valid:
        if ent["start"] >= last_end:
            non_overlapping.append(ent)
            last_end = ent["end"]
        else:
            stats["overlap_removed"] += 1

    stats["valid"] = len(non_overlapping)
    return non_overlapping, stats


def entities_to_bio(text: str, entities: list[dict]) -> list[list[str]]:
    """Convert character-level entities to word-level BIO tags.
    Returns list of [word, tag] pairs."""
    entities = sorted(entities, key=lambda e: e["start"])
    char_labels = ["O"] * len(text)
    for ent in entities:
        for i in range(ent["start"], min(ent["end"], len(text))):
            char_labels[i] = f"B-{ent['label']}" if i == ent["start"] else f"I-{ent['label']}"

    result = []
    i = 0
    while i < len(text):
        while i < len(text) and text[i].isspace():
            i += 1
        if i >= len(text):
            break
        word_start = i
        while i < len(text) and not text[i].isspace():
            i += 1
        result.append([text[word_start:i], char_labels[word_start]])
    return result


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Groq NER Re-annotation")
    parser.add_argument("--api-key", required=True, help="Groq API key")
    parser.add_argument("--input", default="data/processed/raw_texts.jsonl")
    parser.add_argument("--output", default="data/processed/annotated.jsonl")
    parser.add_argument("--resume", action="store_true", help="Resume from checkpoint")
    parser.add_argument("--limit", type=int, default=0, help="Process only N texts (0=all)")
    parser.add_argument("--rpm", type=int, default=28, help="Requests per minute (default 28)")
    parser.add_argument("--model", default="llama-3.3-70b-versatile",
                        help="Groq model (default: llama-3.3-70b-versatile)")
    args = parser.parse_args()

    # Load input
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"ERROR: {input_path} not found. Run extract_texts.py first!")
        sys.exit(1)

    texts = []
    with open(input_path, "r", encoding="utf-8") as f:
        for line in f:
            texts.append(json.loads(line))
    print(f"[LOAD] {len(texts)} texts from {input_path}", flush=True)

    # Output setup
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Checkpoint
    done_ids = set()
    if args.resume and output_path.exists():
        with open(output_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    done_ids.add(json.loads(line)["id"])
                except:
                    pass
        print(f"[RESUME] {len(done_ids)} already processed", flush=True)

    remaining = [t for t in texts if t["id"] not in done_ids]
    if args.limit > 0:
        remaining = remaining[:args.limit]
    print(f"[START] Processing {len(remaining)} texts (model={args.model}, RPM={args.rpm})\n", flush=True)

    # Init annotator
    annotator = GroqAnnotator(api_key=args.api_key, model=args.model)
    annotator.rpm_limit = args.rpm

    stats = {"ok": 0, "fail": 0, "total_ents": 0, "valid_ents": 0}
    start_time = time.time()

    with open(output_path, "a", encoding="utf-8") as fout:
        for i, sample in enumerate(remaining):
            tid = sample["id"]
            text = sample["text"]
            src = sample["source"]

            elapsed = time.time() - start_time
            rate = (i / elapsed * 3600) if elapsed > 0 and i > 0 else 0
            eta = ((len(remaining) - i) / (i / elapsed)) if elapsed > 0 and i > 0 else 0
            eta_str = f"{eta/60:.0f}m" if eta < 3600 else f"{eta/3600:.1f}h"

            print(f"[{i+1}/{len(remaining)}] {tid} ({len(text)} chars) "
                  f"| {rate:.0f}/hr | ETA: {eta_str}", flush=True)

            raw = annotator.annotate(text)

            if raw is None:
                print(f"  X FAILED", flush=True)
                stats["fail"] += 1
                stats["consecutive_fails"] = stats.get("consecutive_fails", 0) + 1
                record = {"id": tid, "source": src, "text": text,
                          "entities": [], "bio_tags": [], "status": "failed"}
                fout.write(json.dumps(record, ensure_ascii=False) + "\n")
                fout.flush()
                # If 3+ consecutive failures, all models exhausted — STOP
                if stats["consecutive_fails"] >= 3:
                    print(f"\n[STOP] All models exhausted. Stopping to avoid flooding failures.", flush=True)
                    break
                continue
            stats["consecutive_fails"] = 0  # Reset on success

            valid_ents, vstats = validate_entities(text, raw)

            # ── Quality gate: reject garbage annotations ──
            if len(valid_ents) > 10:
                label_counts = {}
                for e in valid_ents:
                    label_counts[e["label"]] = label_counts.get(e["label"], 0) + 1
                n = len(valid_ents)
                # SKILL dominance is normal in resumes (up to 85%)
                # But PERSON/ORG dominance = hallucination garbage
                person_pct = label_counts.get("PERSON", 0) / n
                org_pct = label_counts.get("ORG", 0) / n
                if person_pct > 0.40 or org_pct > 0.50:
                    dominant = "PERSON" if person_pct > org_pct else "ORG"
                    dom_n = label_counts.get(dominant, 0)
                    print(f"  X REJECTED (quality: {dominant}={dom_n}/{n}={dom_n/n*100:.0f}%)", flush=True)
                    stats["fail"] += 1
                    record = {"id": tid, "source": src, "text": text,
                              "entities": [], "bio_tags": [], "status": "failed"}
                    fout.write(json.dumps(record, ensure_ascii=False) + "\n")
                    fout.flush()
                    continue

            bio = entities_to_bio(text, valid_ents)

            record = {"id": tid, "source": src, "text": text,
                      "entities": valid_ents, "bio_tags": bio,
                      "status": "ok", "stats": vstats}
            fout.write(json.dumps(record, ensure_ascii=False) + "\n")
            fout.flush()

            stats["ok"] += 1
            stats["total_ents"] += vstats["total"]
            stats["valid_ents"] += vstats["valid"]

            labels = {}
            for e in valid_ents:
                labels[e["label"]] = labels.get(e["label"], 0) + 1
            dist = " ".join(f"{k}:{v}" for k, v in sorted(labels.items()))
            print(f"  OK {vstats['valid']} entities (fixed={vstats['fixed']}, "
                  f"dropped={vstats['dropped']}) | {dist}", flush=True)

    total_time = time.time() - start_time
    print(f"\n{'='*60}")
    print(f"  DONE in {total_time/60:.1f} minutes")
    print(f"  OK: {stats['ok']} | Failed: {stats['fail']}")
    print(f"  Entities: {stats['valid_ents']}/{stats['total_ents']} valid")
    print(f"  Output: {output_path}")
    if output_path.exists():
        print(f"  Size: {output_path.stat().st_size / 1024 / 1024:.1f} MB")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
