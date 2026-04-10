from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified
from typing import List, Dict, Optional
from urllib.parse import quote_plus
from pydantic import BaseModel

from app.db.database import get_db
from app.db import models
from app.services.onet_service import get_onet_service
from app.services.youtube_service import youtube_service
from app.services.web_search_service import web_search_service
from app.core.dependencies import get_current_user

router = APIRouter()

# ── Official Learning Portals ─────────────────────────────────
# Maps skill/tool names → vendor training portals.
# These are REAL, curated links to official documentation and
# training — not auto-generated search URLs.
_OFFICIAL_PORTALS: Dict[str, Dict[str, str]] = {
    # Cloud & DevOps
    "microsoft azure software": {
        "title": "Microsoft Learn — Azure Training",
        "url": "https://learn.microsoft.com/en-us/training/azure/",
        "platform": "Microsoft Learn",
    },
    "amazon web services aws software": {
        "title": "AWS Skill Builder — Free Training",
        "url": "https://skillbuilder.aws/",
        "platform": "AWS Training",
    },
    "docker": {
        "title": "Docker Docs — Get Started",
        "url": "https://docs.docker.com/get-started/",
        "platform": "Docker Docs",
    },
    "kubernetes": {
        "title": "Kubernetes — Official Tutorials",
        "url": "https://kubernetes.io/docs/tutorials/",
        "platform": "Kubernetes",
    },
    "terraform": {
        "title": "Terraform — Hands-on Tutorials",
        "url": "https://developer.hashicorp.com/terraform/tutorials",
        "platform": "HashiCorp",
    },
    "splunk enterprise": {
        "title": "Splunk Docs — Getting Started",
        "url": "https://docs.splunk.com/Documentation/Splunk/latest/SearchTutorial/WelcometotheSearchTutorial",
        "platform": "Splunk",
    },
    # Databases
    "postgresql": {
        "title": "PostgreSQL — Official Tutorial",
        "url": "https://www.postgresql.org/docs/current/tutorial.html",
        "platform": "PostgreSQL",
    },
    "oracle": {
        "title": "Oracle MyLearn — Training Portal",
        "url": "https://mylearn.oracle.com/",
        "platform": "Oracle University",
    },
    "mongodb": {
        "title": "MongoDB University — Free Courses",
        "url": "https://learn.mongodb.com/",
        "platform": "MongoDB University",
    },
    "mysql": {
        "title": "MySQL — Official Reference Manual",
        "url": "https://dev.mysql.com/doc/refman/en/",
        "platform": "MySQL",
    },
    "sql server": {
        "title": "Microsoft Learn — SQL Server",
        "url": "https://learn.microsoft.com/en-us/sql/",
        "platform": "Microsoft Learn",
    },
    "teradata database": {
        "title": "Teradata — Developer Portal",
        "url": "https://www.teradata.com/getting-started",
        "platform": "Teradata",
    },
    "nosql": {
        "title": "MongoDB University — NoSQL Basics",
        "url": "https://learn.mongodb.com/",
        "platform": "MongoDB University",
    },
    "apache hadoop": {
        "title": "Apache Hadoop — Getting Started",
        "url": "https://hadoop.apache.org/docs/stable/hadoop-project-dist/hadoop-common/SingleCluster.html",
        "platform": "Apache",
    },
    # Programming Languages
    "python": {
        "title": "Python — Official Tutorial",
        "url": "https://docs.python.org/3/tutorial/",
        "platform": "Python.org",
    },
    "c#": {
        "title": "Microsoft Learn — C# Guide",
        "url": "https://learn.microsoft.com/en-us/dotnet/csharp/",
        "platform": "Microsoft Learn",
    },
    "perl": {
        "title": "Learn Perl — Official",
        "url": "https://learn.perl.org/",
        "platform": "Perl.org",
    },
    "shell script": {
        "title": "GNU Bash — Reference Manual",
        "url": "https://www.gnu.org/software/bash/manual/",
        "platform": "GNU",
    },
    "git": {
        "title": "Pro Git Book — Official",
        "url": "https://git-scm.com/book/en/v2",
        "platform": "Git SCM",
    },
    # Frameworks
    "react": {
        "title": "React — Official Documentation",
        "url": "https://react.dev/learn",
        "platform": "React",
    },
    "angular": {
        "title": "Angular — Getting Started",
        "url": "https://angular.dev/tutorials",
        "platform": "Angular",
    },
    "vue": {
        "title": "Vue.js — Official Guide",
        "url": "https://vuejs.org/guide/introduction",
        "platform": "Vue.js",
    },
    "node.js": {
        "title": "Node.js — Learn",
        "url": "https://nodejs.org/en/learn",
        "platform": "Node.js",
    },
    "django": {
        "title": "Django — Official Tutorial",
        "url": "https://docs.djangoproject.com/en/5.0/intro/tutorial01/",
        "platform": "Django",
    },
    "laravel": {
        "title": "Laravel — Official Documentation",
        "url": "https://laravel.com/docs",
        "platform": "Laravel",
    },
    "flutter": {
        "title": "Flutter — Official Documentation",
        "url": "https://docs.flutter.dev/",
        "platform": "Flutter",
    },
    # AI/ML
    "tensorflow": {
        "title": "TensorFlow — Official Tutorials",
        "url": "https://www.tensorflow.org/tutorials",
        "platform": "TensorFlow",
    },
    "pytorch": {
        "title": "PyTorch — Official Tutorials",
        "url": "https://pytorch.org/tutorials/",
        "platform": "PyTorch",
    },
    # Networking
    "cisco": {
        "title": "Cisco Networking Academy",
        "url": "https://www.netacad.com/",
        "platform": "Cisco NetAcad",
    },
    # Google
    "google analytics": {
        "title": "Google Skillshop — Analytics",
        "url": "https://skillshop.withgoogle.com/",
        "platform": "Google Skillshop",
    },
    # Microsoft Tools
    "microsoft project": {
        "title": "Microsoft Learn — Project",
        "url": "https://learn.microsoft.com/en-us/project/",
        "platform": "Microsoft Learn",
    },
    # Medical
    "meditech software": {
        "title": "MEDITECH — EHR Learning Resources",
        "url": "https://ehr.meditech.com/",
        "platform": "MEDITECH",
    },
    # Project Management
    "atlassian jira": {
        "title": "Atlassian University — Jira Training",
        "url": "https://university.atlassian.com/",
        "platform": "Atlassian University",
    },
}


def _generate_search_link(topic: str, experience_level: str) -> Dict:
    """Generate a single Coursera search link as a fallback.

    This is NOT a fake course — it's clearly typed as 'course_search'
    so the frontend can display it as a "Browse courses" button.
    """
    level = {"Junior": "beginner", "Senior": "advanced"}.get(experience_level, "")
    params = f"query={quote_plus(topic)}"
    if level:
        params += f"&productDifficultyLevel={level}"

    return {
        "type": "course_search",
        "platform": "Coursera",
        "title": f"Browse courses: {topic}",
        "url": f"https://www.coursera.org/search?{params}",
        "thumbnail": None,
    }


def _find_official_portal(topic: str) -> Optional[Dict]:
    """Find official learning portal for a topic."""
    key = topic.lower().strip()
    portal = _OFFICIAL_PORTALS.get(key)
    if portal:
        return {
            "type": "official_doc",
            "platform": portal["platform"],
            "title": portal["title"],
            "url": portal["url"],
            "thumbnail": None,
        }
    # Fuzzy: try partial match (e.g. "Amazon Web Services AWS" matches)
    for portal_key, portal_val in _OFFICIAL_PORTALS.items():
        if portal_key in key or key in portal_key:
            return {
                "type": "official_doc",
                "platform": portal_val["platform"],
                "title": portal_val["title"],
                "url": portal_val["url"],
                "thumbnail": None,
            }
    return None


def _update_step_completion(
    step_id: str,
    completed: bool,
    current_user: models.User,
    db: Session,
) -> dict:
    """Shared logic for marking a roadmap step as complete/incomplete."""
    roadmap = db.query(models.LearningRoadmap).filter(
        models.LearningRoadmap.user_id == current_user.id,
        models.LearningRoadmap.is_archived.is_(False),
    ).order_by(models.LearningRoadmap.created_at.desc()).first()

    if not roadmap:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No roadmap found"
        )

    roadmap_data = roadmap.roadmap_data or []
    try:
        step_index = int(step_id)
        if 0 <= step_index < len(roadmap_data):
            roadmap_data[step_index]["completed"] = completed
            roadmap.roadmap_data = roadmap_data
            flag_modified(roadmap, "roadmap_data")
            db.commit()
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Step index {step_id} out of range"
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="step_id must be a valid integer index"
        )

    return {"success": True, "step_id": step_id, "completed": completed}


# Request model for roadmap generation
class RoadmapGenerateRequest(BaseModel):
    analysis_id: str


@router.get("", response_model=dict)
async def get_roadmap(
    analysis_id: Optional[str] = None,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get learning roadmap for user (latest or by analysis_id)"""

    if analysis_id:
        roadmap = db.query(models.LearningRoadmap).filter(
            models.LearningRoadmap.analysis_id == analysis_id,
            models.LearningRoadmap.user_id == current_user.id
        ).first()
    else:
        roadmap = db.query(models.LearningRoadmap).filter(
            models.LearningRoadmap.user_id == current_user.id,
            models.LearningRoadmap.is_archived.is_(False),
        ).order_by(models.LearningRoadmap.created_at.desc()).first()

    if not roadmap:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No roadmap found"
        )

    return {
        "roadmap_id": roadmap.id,
        "learning_roadmap": roadmap.roadmap_data
    }


@router.post("/generate", response_model=dict)
async def generate_roadmap(
    request: RoadmapGenerateRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate personalized learning roadmap from analysis.

    Resource strategy per topic (3 layers):
    1. YouTube (real API) — 2 videos per topic
    2. Official Portal (curated map) — 1 doc link if available
    3. Smart Web Search (DuckDuckGo) — 1-2 real courses/articles
    4. Coursera search link — 1 browse link (clearly typed as course_search)
    """

    user_id = current_user.id
    analysis_id = request.analysis_id

    # Get analysis
    analysis = db.query(models.SkillAnalysis).filter(
        models.SkillAnalysis.id == analysis_id,
        models.SkillAnalysis.user_id == user_id
    ).first()

    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )

    # Generate roadmap phases using O*NET taxonomy (local, no API)
    missing_skills = analysis.missing_skills or []
    entities = analysis.extracted_entities or {}
    missing_tech = entities.get("missing_tech_skills", [])

    if not missing_skills and not missing_tech:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No missing skills to create roadmap"
        )

    onet = get_onet_service()
    roadmap_phases = onet.generate_roadmap(
        missing_skills=missing_skills,
        job_title=analysis.predicted_job_title or "",
        experience_level=analysis.experience_level or "Mid-Level",
        tech_skills=missing_tech,
    )

    # ── Fetch resources for each phase — PER TOPIC ──
    exp_level = analysis.experience_level or "Mid-Level"
    job_context = analysis.predicted_job_title or ""

    import asyncio
    from concurrent.futures import ThreadPoolExecutor

    executor = ThreadPoolExecutor(max_workers=8)
    loop = asyncio.get_event_loop()

    async def fetch_topic_resources(topic: str) -> dict:
        """Fetch all resources for a single topic using 3-layer strategy."""

        # Layer 1: YouTube (real API) — 2 videos
        def _youtube():
            return youtube_service.search_videos(
                topic, max_results=2,
                experience_level=exp_level, job_context=job_context,
            )

        # Layer 2: Web Search — real courses + articles
        def _web():
            try:
                return web_search_service.search_courses(
                    topic, max_results=2, experience_level=exp_level,
                )
            except Exception:
                return []

        # Run layers in parallel
        yt_task = loop.run_in_executor(executor, _youtube)
        web_task = loop.run_in_executor(executor, _web)
        yt_results, web_results = await asyncio.gather(yt_task, web_task)

        resources = list(yt_results)

        # Layer 2.5: Official portal (instant, no API)
        portal = _find_official_portal(topic)
        if portal:
            resources.append(portal)

        resources.extend(list(web_results))

        # Layer 3: Coursera search link (always, as fallback browse)
        resources.append(_generate_search_link(topic, exp_level))

        # Add completed=false to each resource
        for res in resources:
            res["completed"] = False

        return {"name": topic, "resources": resources}

    # Build full roadmap with per-topic resources
    full_roadmap = []

    for phase in roadmap_phases:
        topic_names = phase.get("topics", [])

        # Fetch ALL topics in this phase in parallel (no [:3] cutoff!)
        topic_results = await asyncio.gather(
            *[fetch_topic_resources(t) for t in topic_names]
        )

        full_roadmap.append({
            "phase": phase.get("phase"),
            "duration": phase.get("duration"),
            "topics": list(topic_results),  # List[{name, resources}]
            "priority": phase.get("priority", "Medium"),
            "completed": False,
        })

    # Save roadmap
    roadmap = models.LearningRoadmap(
        user_id=user_id,
        analysis_id=analysis_id,
        roadmap_data=full_roadmap
    )

    db.add(roadmap)
    db.commit()
    db.refresh(roadmap)

    return {
        "roadmap_id": roadmap.id,
        "learning_roadmap": full_roadmap
    }


@router.put("/steps/{step_id}/complete")
async def mark_step_complete(
    step_id: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark a roadmap step/phase as completed."""
    return _update_step_completion(step_id, True, current_user, db)


@router.put("/steps/{step_id}/incomplete")
async def mark_step_incomplete(
    step_id: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark a roadmap step/phase as incomplete."""
    return _update_step_completion(step_id, False, current_user, db)


@router.put("/steps/{step_id}/resources/{resource_id}/toggle")
async def toggle_resource_completion(
    step_id: str,
    resource_id: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Toggle completion of a specific resource within a topic.

    resource_id format: "{topic_index}_{resource_index}" (e.g. "0_2")
    Phase auto-completes when all its resources are completed.
    """
    roadmap = db.query(models.LearningRoadmap).filter(
        models.LearningRoadmap.user_id == current_user.id,
        models.LearningRoadmap.is_archived.is_(False),
    ).order_by(models.LearningRoadmap.created_at.desc()).first()

    if not roadmap:
        raise HTTPException(status_code=404, detail="No roadmap found")

    roadmap_data = roadmap.roadmap_data or []
    try:
        phase_idx = int(step_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Phase index must be integer")

    if phase_idx < 0 or phase_idx >= len(roadmap_data):
        raise HTTPException(status_code=404, detail="Phase index out of range")

    phase = roadmap_data[phase_idx]
    topics = phase.get("topics", [])

    # Support both old format (resource_id = flat index) and new (topic_resource)
    if "_" in resource_id:
        # New format: "topicIdx_resourceIdx"
        parts = resource_id.split("_")
        topic_idx = int(parts[0])
        res_idx = int(parts[1])

        if topic_idx < 0 or topic_idx >= len(topics):
            raise HTTPException(status_code=404, detail="Topic index out of range")

        topic = topics[topic_idx]
        resources = topic.get("resources", [])

        if res_idx < 0 or res_idx >= len(resources):
            raise HTTPException(status_code=404, detail="Resource index out of range")

        # Toggle
        current = resources[res_idx].get("completed", False)
        resources[res_idx]["completed"] = not current
    else:
        # Legacy flat format — backward compatibility
        res_idx = int(resource_id)
        # Flatten all resources to find by flat index
        flat_idx = 0
        toggled = False
        for topic in topics:
            topic_resources = topic.get("resources", []) if isinstance(topic, dict) else []
            for r in topic_resources:
                if flat_idx == res_idx:
                    current = r.get("completed", False)
                    r["completed"] = not current
                    toggled = True
                    break
                flat_idx += 1
            if toggled:
                break

        if not toggled:
            # Try old flat resources format
            resources = phase.get("resources", [])
            if res_idx < len(resources):
                current = resources[res_idx].get("completed", False)
                resources[res_idx]["completed"] = not current
            else:
                raise HTTPException(status_code=404, detail="Resource index out of range")

    # Auto-compute phase completion
    all_done = True
    total_res = 0
    completed_res = 0
    for topic in topics:
        if isinstance(topic, dict):
            for r in topic.get("resources", []):
                total_res += 1
                if r.get("completed", False):
                    completed_res += 1
                else:
                    all_done = False
        # Legacy: string topics with flat resources
    # Also check flat resources (backward compat)
    for r in phase.get("resources", []):
        total_res += 1
        if r.get("completed", False):
            completed_res += 1
        else:
            all_done = False

    phase["completed"] = all_done

    roadmap.roadmap_data = roadmap_data
    flag_modified(roadmap, "roadmap_data")
    db.commit()

    return {
        "success": True,
        "phase_index": phase_idx,
        "resource_id": resource_id,
        "resource_completed": not current if '_' in resource_id or not isinstance(topics[0], dict) else True,
        "phase_completed": all_done,
        "completed_resources": completed_res,
        "total_resources": total_res,
    }
