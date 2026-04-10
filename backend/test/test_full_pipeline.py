"""
Viora Full Pipeline Test — يحاكي بالضبط ما يفعله المستخدم في تطبيق الجوال.

الاستخدام:
    python test_full_pipeline.py path/to/your_cv.pdf

المراحل:
    1. تسجيل مستخدم جديد
    2. تسجيل دخول
    3. رفع السيرة الذاتية (PDF/DOCX)
    4. تحليل السيرة الذاتية (NER + O*NET)
    5. إنشاء خارطة طريق التعلم (Roadmap)
    6. عرض لوحة المستخدم (Dashboard)

كل مرحلة تطبع بالضبط ما يراه المستخدم في الموبايل.
"""
import sys
import os
import json
import time
import requests
import random
import string

# ── Configuration ──────────────────────────────────────────────
BASE_URL = "http://127.0.0.1:8000"
DIVIDER = "=" * 70


def random_email():
    """Generate a random test email."""
    suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"test_{suffix}@viora-test.com"


def print_section(title: str):
    """Print a visible section header."""
    print(f"\n{DIVIDER}")
    print(f"  {title}")
    print(DIVIDER)


def check_server():
    """Check if the backend server is running."""
    try:
        r = requests.get(f"{BASE_URL}/health", timeout=5)
        if r.status_code == 200:
            print("  [OK] Server is running!")
            return True
    except requests.ConnectionError:
        pass
    print("  [ERROR] Server is not running! Start it first:")
    print(f"     cd backend && python -m uvicorn main:app --reload")
    return False


# ======================================================================
#  Stage 1: Registration
# ======================================================================

def step_register(email: str, password: str = "Test@12345") -> dict:
    """Register a new user."""
    print_section("Stage 1: Register New User")

    data = {
        "full_name": "Ahmed Mohammed (Test User)",
        "email": email,
        "password": password,
        "confirm_password": password,
    }
    print(f"  Email: {email}")
    print(f"  Name: {data['full_name']}")

    r = requests.post(f"{BASE_URL}/api/auth/register", json=data)

    if r.status_code == 201:
        result = r.json()
        print("  [OK] Registration successful!")
        print(f"  Access Token: {result['access_token'][:50]}...")
        user = result.get("user", {})
        for key, val in user.items():
            print(f"    {key}: {val}")
        return result
    else:
        print(f"  [ERROR] Registration failed: {r.status_code}")
        print(f"     {r.text}")
        sys.exit(1)


# ======================================================================
#  Stage 2: Login
# ======================================================================

def step_login(email: str, password: str = "Test@12345") -> dict:
    """Login."""
    print_section("Stage 2: Login")

    r = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": email,
        "password": password,
    })

    if r.status_code == 200:
        result = r.json()
        print("  [OK] Login successful!")
        print(f"  Access Token: {result['access_token'][:50]}...")
        print(f"  Refresh Token: {result['refresh_token'][:50]}...")
        return result
    else:
        print(f"  [ERROR] Login failed: {r.status_code}")
        print(f"     {r.text}")
        sys.exit(1)


# ======================================================================
#  Stage 3: Upload CV
# ======================================================================

def step_upload(token: str, cv_path: str) -> dict:
    """Upload CV file."""
    print_section("Stage 3: Upload CV")

    if not os.path.exists(cv_path):
        print(f"  [ERROR] File not found: {cv_path}")
        sys.exit(1)

    file_size = os.path.getsize(cv_path)
    file_ext = os.path.splitext(cv_path)[1]
    print(f"  File: {os.path.basename(cv_path)}")
    print(f"  Size: {file_size / 1024:.1f} KB")
    print(f"  Type: {file_ext}")

    headers = {"Authorization": f"Bearer {token}"}

    with open(cv_path, "rb") as f:
        files = {"file": (os.path.basename(cv_path), f)}
        r = requests.post(f"{BASE_URL}/api/resume/upload", headers=headers, files=files)

    if r.status_code == 200:
        result = r.json()
        print("  [OK] File uploaded successfully!")
        print(f"  File ID: {result['file_id']}")
        print(f"  Filename: {result['filename']}")
        print(f"  Uploaded: {result.get('uploaded_at', 'N/A')}")
        return result
    else:
        print(f"  [ERROR] Upload failed: {r.status_code}")
        print(f"     {r.text}")
        sys.exit(1)


# ======================================================================
#  Stage 4: Analyze CV
# ======================================================================

def step_analyze(token: str, file_id: str) -> dict:
    """Analyze CV — what the user sees after pressing 'Analyze'."""
    print_section("Stage 4: Analyze CV (NER + O*NET)")

    headers = {"Authorization": f"Bearer {token}"}
    data = {"file_id": file_id}

    print("  Analyzing...")
    start = time.time()
    r = requests.post(f"{BASE_URL}/api/resume/analyze", headers=headers, json=data)
    elapsed = time.time() - start

    if r.status_code == 200:
        result = r.json()
        print(f"  [OK] Analysis completed in {elapsed:.1f} seconds!")
        print(f"  Analysis ID: {result.get('analysis_id', 'N/A')}")

        # ── USER PROFILE (what mobile user sees) ──
        profile = result.get("user_profile", {})
        print("\n  +------ Professional Profile ------+")
        print(f"  | Predicted Job Title: {profile.get('predicted_job_title', 'N/A')}")
        print(f"  | Experience Level: {profile.get('experience_level', 'N/A')}")
        cd = profile.get('career_direction', 'N/A')
        if cd and len(cd) > 80:
            cd = cd[:80] + "..."
        print(f"  | Career Direction: {cd}")
        print(f"  | Extracted Skills Count: {len(profile.get('extracted_skills', []))}")
        print("  +----------------------------------+")

        # ── STRONG SKILLS ──
        strong = profile.get("strong_skills", [])
        if strong:
            print(f"\n  Strong Skills ({len(strong)}):")
            for s in strong[:15]:
                name = s.get("name", "?") if isinstance(s, dict) else s
                prof = s.get("proficiency", "?") if isinstance(s, dict) else "?"
                bar = ""
                if isinstance(prof, (int, float)):
                    blocks = int(prof) // 10
                    bar = "#" * blocks + "." * (10 - blocks)
                print(f"    - {name:<35} {prof}% [{bar}]")
            if len(strong) > 15:
                print(f"    ... and {len(strong) - 15} more")

        # ── EXTRACTED SKILLS ──
        extracted = profile.get("extracted_skills", [])
        if extracted:
            print(f"\n  All Extracted Skills ({len(extracted)}):")
            for s in extracted[:20]:
                print(f"    - {s}")
            if len(extracted) > 20:
                print(f"    ... and {len(extracted) - 20} more")

        # ── JOB OPPORTUNITIES ──
        jobs = result.get("job_opportunities", [])
        if jobs:
            print(f"\n  Job Opportunities ({len(jobs)}):")
            for j in jobs[:5]:
                print(f"    - {j}")

        # ── STRENGTHS ──
        strengths = result.get("strengths", [])
        if strengths:
            print(f"\n  Strengths ({len(strengths)}):")
            for s in strengths:
                if isinstance(s, dict):
                    print(f"    - {s.get('skill', '?')}: {s.get('description', '')[:80]}")
                else:
                    print(f"    - {s}")

        # ── GAP ANALYSIS ──
        gap = result.get("gap_analysis", {})
        print(f"\n  Gap Analysis:")
        print(f"    Target Job: {gap.get('predicted_job', 'N/A')}")
        print(f"    Experience Level: {gap.get('experience_level', 'N/A')}")

        missing_hard = gap.get("missing_hard_skills", [])
        missing_soft = gap.get("missing_soft_skills", [])
        missing_tech = gap.get("missing_tech_skills", [])

        if missing_hard:
            print(f"\n    Missing Hard Skills ({len(missing_hard)}):")
            for s in missing_hard[:10]:
                if isinstance(s, dict):
                    print(f"      - {s.get('skill', s)} (priority: {s.get('priority', '?')})")
                else:
                    print(f"      - {s}")
            if len(missing_hard) > 10:
                print(f"      ... and {len(missing_hard) - 10} more")

        if missing_soft:
            print(f"\n    Missing Soft Skills ({len(missing_soft)}):")
            for s in missing_soft[:5]:
                if isinstance(s, dict):
                    print(f"      - {s.get('skill', s)} (priority: {s.get('priority', '?')})")
                else:
                    print(f"      - {s}")

        if missing_tech:
            print(f"\n    Missing Tech/Tools ({len(missing_tech)}):")
            for t in missing_tech[:10]:
                if isinstance(t, dict):
                    hot = " [HOT]" if t.get("hot_technology") else ""
                    print(f"      - {t.get('skill', '?')} [{t.get('category', '')}]{hot}")
                else:
                    print(f"      - {t}")
            if len(missing_tech) > 10:
                print(f"      ... and {len(missing_tech) - 10} more")

        # ── RECOMMENDATIONS ──
        recs = result.get("recommendations", [])
        if recs:
            print(f"\n  Recommendations ({len(recs)}):")
            for rec in recs:
                if isinstance(rec, dict):
                    print(f"    - Learn {rec.get('skill', '?')} (priority: {rec.get('priority', '?')})")
                else:
                    print(f"    - {rec}")

        # ── CV QUALITY ──
        quality = result.get("cv_quality", {})
        if quality:
            score = quality.get("quality_score", 0)
            print(f"\n  CV Quality Score: {score}/100")
            print(f"    Word Count: {quality.get('word_count', 0)}")
            sections = quality.get("sections_found", [])
            missing_sec = quality.get("sections_missing", [])
            if sections:
                print(f"    Sections Found: {', '.join(sections)}")
            if missing_sec:
                print(f"    Missing Sections: {', '.join(missing_sec)}")
            warnings = quality.get("warnings", [])
            for w in warnings:
                print(f"    WARNING: {w}")

        # ── LANGUAGES ──
        langs = result.get("languages", [])
        if langs:
            print(f"\n  Languages detected: {', '.join(langs)}")

        return result
    else:
        print(f"  [ERROR] Analysis failed: {r.status_code}")
        print(f"     {r.text}")
        sys.exit(1)


# ======================================================================
#  Stage 5: Generate Learning Roadmap
# ======================================================================

def step_roadmap(token: str, analysis_id: str) -> dict:
    """Generate roadmap — what the user sees after pressing 'Create Roadmap'."""
    print_section("Stage 5: Generate Learning Roadmap")

    headers = {"Authorization": f"Bearer {token}"}
    data = {"analysis_id": analysis_id}

    print("  Generating roadmap (fetching YouTube, Official Docs, Web resources)...")
    start = time.time()
    r = requests.post(f"{BASE_URL}/api/roadmap/generate", headers=headers, json=data)
    elapsed = time.time() - start

    if r.status_code == 200:
        result = r.json()
        roadmap = result.get("learning_roadmap", [])
        print(f"  [OK] Roadmap generated in {elapsed:.1f} seconds!")
        print(f"  Roadmap ID: {result.get('roadmap_id', 'N/A')}")
        print(f"  Total Phases: {len(roadmap)}")

        for i, phase in enumerate(roadmap):
            phase_name = phase.get("phase", f"Phase {i+1}")
            duration = phase.get("duration", "?")
            priority = phase.get("priority", "?")
            topics = phase.get("topics", [])

            priority_tag = {"High": "[HIGH]", "Medium": "[MEDIUM]", "Low": "[LOW]"}.get(priority, "[?]")

            # Handle both old (string) and new (dict) topic formats
            topic_names = []
            for t in topics:
                if isinstance(t, dict):
                    topic_names.append(t.get("name", "?"))
                else:
                    topic_names.append(str(t))

            print(f"\n  +--- Phase {i+1}: {phase_name} ---")
            print(f"  | Duration: {duration}")
            print(f"  | Priority: {priority_tag}")
            print(f"  | Topics ({len(topics)}): {', '.join(topic_names[:5])}")

            # Per-topic resource display
            for t in topics:
                if isinstance(t, dict):
                    tname = t.get("name", "?")
                    resources = t.get("resources", [])
                    print(f"  |")
                    print(f"  | 📦 {tname} ({len(resources)} resources)")

                    for r in resources:
                        rtype = r.get("type", "?")
                        platform = r.get("platform", "?")
                        title = r.get("title", "?")[:65]
                        url = r.get("url", "")[:80]

                        icon = {"video": "🎬", "official_doc": "📄", "article": "📝", "course_search": "🔍"}.get(rtype, "🔗")
                        print(f"  |   {icon} [{platform}] {title}")

                        if rtype == "video":
                            ch = r.get("channel", "?")
                            dur = r.get("duration", "?")
                            print(f"  |     Channel: {ch} | Duration: {dur}")

                        print(f"  |     URL: {url}")

            print(f"  +----------------------------------------------")

        return result
    else:
        print(f"  [ERROR] Roadmap failed: {r.status_code}")
        print(f"     {r.text}")
        return {}


# ======================================================================
#  Stage 6: Dashboard
# ======================================================================

def step_dashboard(token: str):
    """Get dashboard — what the user sees on the home screen."""
    print_section("Stage 6: Dashboard")

    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(f"{BASE_URL}/api/dashboard", headers=headers)

    if r.status_code == 200:
        result = r.json()
        user = result.get("user", {})
        progress = result.get("progress", {})

        print(f"  User: {user.get('name', user.get('full_name', 'N/A'))}")
        print(f"  Email: {user.get('email', 'N/A')}")

        pct = progress.get("learning_progress", progress.get("overall_percentage", 0))
        bar = "#" * (pct // 5) + "." * (20 - pct // 5)
        print(f"\n  Learning Progress: [{bar}] {pct}%")
        print(f"    Journey Step: {progress.get('journey_step', 'N/A')}")
        print(f"    CV Analysis: {'Yes' if progress.get('has_analysis') else 'No'}")
        print(f"    Learning Roadmap: {'Yes' if progress.get('has_roadmap') else 'No'}")
        print(f"    Skills Found: {progress.get('skills_found', progress.get('skill_growth', 0))}")
        print(f"    Topics: {progress.get('topics_completed', 0)}/{progress.get('topics_total', 0)}")
        print(f"    Resources: {progress.get('roadmap_resources_completed', 0)}/{progress.get('roadmap_resources_total', 0)}")
        print(f"    Notifications: {result.get('notifications_count', 0)}")

        return result
    else:
        print(f"  [ERROR] Dashboard failed: {r.status_code}")
        return {}


# ======================================================================
#  Main Entry Point
# ======================================================================

def main():
    print("\n" + "=" * 70)
    print("  Viora Full Pipeline Test — Simulating Complete User Experience")
    print("=" * 70)

    # ── Check arguments ──
    if len(sys.argv) < 2:
        print("\n  [ERROR] You must provide the path to a CV file!")
        print("\n  Usage:")
        print("    python test_full_pipeline.py path/to/cv.pdf")
        print("    python test_full_pipeline.py path/to/cv.docx")
        print("\n  Example:")
        print("    python test_full_pipeline.py C:\\Users\\Ahmed\\Documents\\my_cv.pdf")
        sys.exit(1)

    cv_path = sys.argv[1]
    if not os.path.exists(cv_path):
        print(f"\n  [ERROR] File not found: {cv_path}")
        sys.exit(1)

    # ── Check server ──
    print_section("Checking Server")
    if not check_server():
        sys.exit(1)

    # ── Run full pipeline ──
    email = random_email()
    password = "Test@12345"
    total_start = time.time()

    # 1. Register
    reg_result = step_register(email, password)
    token = reg_result["access_token"]

    # 2. Login (to verify it works)
    login_result = step_login(email, password)
    token = login_result["access_token"]  # Use fresh token

    # 3. Upload CV
    upload_result = step_upload(token, cv_path)
    file_id = upload_result["file_id"]

    # 4. Analyze CV
    analysis_result = step_analyze(token, file_id)
    analysis_id = analysis_result.get("analysis_id", "")

    # 5. Generate Roadmap
    roadmap_result = {}
    if analysis_id:
        roadmap_result = step_roadmap(token, analysis_id)

    # 6. Dashboard
    step_dashboard(token)

    # ── Summary ──
    total_elapsed = time.time() - total_start
    print_section("EXECUTION SUMMARY")
    print(f"  Total Time: {total_elapsed:.1f} seconds")
    print(f"  User: {email}")
    print(f"  CV File: {os.path.basename(cv_path)}")
    profile = analysis_result.get('user_profile', {})
    print(f"  Predicted Job: {profile.get('predicted_job_title', 'N/A')}")
    print(f"  Experience Level: {profile.get('experience_level', 'N/A')}")
    skills = profile.get('extracted_skills', [])
    print(f"  Extracted Skills: {len(skills)}")
    gap = analysis_result.get('gap_analysis', {})
    missing_h = gap.get('missing_hard_skills', [])
    missing_t = gap.get('missing_tech_skills', [])
    print(f"  Missing Hard Skills: {len(missing_h)}")
    print(f"  Missing Tech/Tools: {len(missing_t)}")
    phases = roadmap_result.get('learning_roadmap', [])
    print(f"  Roadmap Phases: {len(phases)}")

    # ── Save full JSON output ──
    output_file = "test_pipeline_output.json"
    full_output = {
        "analysis": analysis_result,
        "roadmap": roadmap_result,
    }
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(full_output, f, ensure_ascii=False, indent=2, default=str)
    print(f"\n  Full JSON output saved to: {output_file}")

    print(f"\n  [OK] All stages completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()
