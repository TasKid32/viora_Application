# 🖥️ Viora Backend — API Reference

**Smart Career Development System — Backend Server**

A RESTful API built with FastAPI, managing CV analysis using a local Viora NER model (ONNX) integrated with O\*NET occupational taxonomy. No external APIs are used for CV analysis. Gemini is used only as a smart chat assistant.

---

## Setup & Running

> 📖 For complete step-by-step installation and setup instructions, see the [**Main README**](../README_EN.md#-step-by-step-setup)

**Requirements**: Python 3.11.9 · Viora NER ONNX model · O\*NET + ESCO data

**Server**: `http://localhost:8000` · **Swagger**: `http://localhost:8000/docs`

---

## Project Structure

```
backend/
├── main.py                    # Entry point — FastAPI app
├── requirements.txt           # Dependencies (Python 3.11.9)
├── .env                       # Environment variables (not tracked by Git)
├── .env.example               # Environment variables template
├── viora.db                   # SQLite database (auto-created)
├── uploads/                   # Uploaded files (avatars + temp CVs)
│   └── avatars/               # Profile pictures
├── test/                      # pytest tests
│   ├── test_full_pipeline.py  # Full pipeline test
│   ├── test_onet_service.py   # O*NET service test
│   ├── test_chat.py           # Chat test
│   └── test_quota.py          # Quota management test
│
└── app/                       # Main application code
    ├── __init__.py
    ├── core/                  # Settings, security, shared utilities
    │   ├── config.py          # Pydantic Settings configuration
    │   ├── dependencies.py    # Dependency Injection functions
    │   ├── logging.py         # Structured logging
    │   ├── quota_handler.py   # API quota exhaustion handling
    │   └── security.py        # Password hashing + JWT + Reset
    │
    ├── db/                    # Database layer
    │   ├── database.py        # SQLAlchemy Engine + Session setup
    │   ├── models.py          # ORM models (7 tables)
    │   └── init_db.py         # Database initialization & verification
    │
    ├── api/v1/                # API Endpoints
    │   ├── auth.py            # Register + login + token refresh + forgot password
    │   ├── resume.py          # Upload + analyze CV (SSE streaming)
    │   ├── roadmap.py         # Learning roadmap (generation + completion tracking)
    │   ├── chat.py            # Smart assistant (Gemini)
    │   ├── dashboard.py       # Dashboard
    │   ├── courses.py         # Course management (full CRUD)
    │   ├── notifications.py   # Notifications
    │   ├── profile.py         # Profile + avatar upload
    │   └── progress.py        # Weekly progress tracking
    │
    ├── schemas/               # Pydantic validation models
    │   ├── auth_schemas.py
    │   ├── resume_schemas.py
    │   ├── chat_schemas.py
    │   ├── course_schemas.py
    │   ├── dashboard_schemas.py
    │   ├── notification_schemas.py
    │   └── progress_schemas.py
    │
    └── services/              # Business Logic layer
        ├── auth_service.py            # Registration & authentication logic
        ├── hybrid_analysis_service.py # NER + O*NET merge (hybrid pipeline)
        ├── viora_ner_service.py       # ONNX entity extraction
        ├── onet_service.py            # Job matching + gap analysis
        ├── onet_data_loader.py        # Load O*NET TSV files
        ├── onet_roadmap.py            # Learning roadmap generation
        ├── esco_resolver.py           # ESCO v1.2.1 classification (85K skills)
        ├── cv_parsers.py              # Soft skills + experience extraction
        ├── cv_quality.py              # CV quality scoring (0-100)
        ├── text_extractor.py          # Text extraction (PDF/DOCX)
        ├── file_upload.py             # File saving with validation
        ├── llm_service.py             # Gemini API (chat only)
        ├── email_service.py           # SMTP email sending
        ├── youtube_service.py         # YouTube Data API v3 search
        ├── udemy_service.py           # Smart Udemy search links
        ├── coursera_service.py        # Smart Coursera search links
        ├── edx_service.py             # Smart edX search links
        ├── course_search_service.py   # Google Custom Search for courses
        └── web_search_service.py      # Web search (DuckDuckGo)
```

---

## Application Architecture

### Entry Point (`main.py`)

1. **Lifespan Event**: Pre-loads Viora NER ONNX model (~120MB) and O\*NET data (~1016 occupations) at startup to avoid cold start delay
2. **CORS Middleware**: Configurable origins via `CORS_ORIGINS` env variable
3. **9 Routers**: Registers 9 API routers under `/api/`
4. **Static Files**: Serves `uploads/` directory for uploaded images and files
5. **Health Check**: `/health` endpoint for server status

### Core Layer

#### `config.py` — Centralized Settings
- Uses `pydantic-settings` (V2) to load settings from `.env`
- **SECRET_KEY guard**: Refuses to start in production with default key (`model_validator`)
- Supports SQLite (dev) and PostgreSQL (production) via `DATABASE_URL`
- Configurable: max file size (10MB), NER model path, NER confidence threshold (0.50), SMTP settings, CORS origins

#### `security.py` — Security & Authentication
- **Password hashing**: Uses `bcrypt` directly (truncates at 72 bytes per bcrypt spec)
- **Dual JWT Tokens**:
  - `access_token`: Valid 24 hours, type `"access"`
  - `refresh_token`: Valid 7 days, type `"refresh"`
  - Token type checking prevents using refresh as access and vice versa
- **Password Reset**: Uses `itsdangerous.URLSafeTimedSerializer` for time-limited reset tokens (30 minutes), separate from JWT

#### `dependencies.py` — Dependency Injection
- `get_current_user()`: Extracts current user from JWT Bearer token, used in all protected endpoints

#### `logging.py` — Structured Logging
- Standard `logging` module instead of `print()`
- Format: `YYYY-MM-DD HH:MM:SS | LEVEL | module | message`
- Log level configurable via `LOG_LEVEL` in `.env`

#### `quota_handler.py` — API Quota Management
- Handles YouTube and Gemini quota exhaustion
- Returns `HTTP 429` with clear message when quota is exhausted

### Database Layer

#### `models.py` — ORM Models (7 Tables)
- All IDs are UUID4 (string)
- All timestamps are timezone-aware (UTC)
- `cascade="all, delete-orphan"` on all relationships

| Table | Description | Key Fields |
|---|---|---|
| `users` | Users | full_name, email, password_hash, avatar_url, bio, phone_number, language |
| `resumes` | Uploaded CVs | file_path, original_filename, language |
| `skill_analyses` | Analysis results | predicted_job_title, experience_level, strong_skills (JSON), missing_skills (JSON), extracted_entities (JSON), is_archived |
| `learning_roadmaps` | Learning roadmaps | roadmap_data (JSON), is_archived |
| `notifications` | Notifications | type, title, message, is_read |
| `chat_history` | Chat history | message, reply |
| `courses` | Courses | title, category, platform, completion (0-100) |

### Services Layer

#### CV Analysis Services (100% Local)

| Service | File | Description |
|---|---|---|
| **Hybrid Analysis** | `hybrid_analysis_service.py` | Merges NER + O\*NET in single pipeline |
| **Viora NER** | `viora_ner_service.py` | ONNX INT8 entity extraction (119MB) |
| **O\*NET Service** | `onet_service.py` | Job matching + gap analysis + semantic matching (710 lines) |
| **O\*NET Data Loader** | `onet_data_loader.py` | Loads 5 TSV files + job title alias dictionary |
| **O\*NET Roadmap** | `onet_roadmap.py` | Learning roadmap generation |
| **ESCO Resolver** | `esco_resolver.py` | ESCO v1.2.1 (85K alternative skills + 96 soft skills) |
| **CV Parsers** | `cv_parsers.py` | Soft skills + years of experience + graduation year |
| **CV Quality** | `cv_quality.py` | CV quality scoring (0-100, Arabic + English) |

#### External Services

| Service | File | Description |
|---|---|---|
| **LLM Service** | `llm_service.py` | Gemini 2.5 Flash — chat **only** (not analysis) |
| **Email Service** | `email_service.py` | SMTP — password reset + change notification |
| **YouTube** | `youtube_service.py` | YouTube Data API v3 — educational video search |
| **Udemy** | `udemy_service.py` | Smart search link generator (API deprecated since 2025) |
| **Coursera** | `coursera_service.py` | Smart search link generator |
| **edX** | `edx_service.py` | Smart search link generator |
| **Web Search** | `web_search_service.py` | Google → Bing → DuckDuckGo (free) |

---

## CV Analysis Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│                  CV Analysis Pipeline                        │
│            (Fully Local — No External APIs)                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. Upload CV (PDF/DOCX)                                    │
│     └─→ file_upload.py → text_extractor.py                  │
│                                                             │
│  2. CV Quality Score (0-100)                                │
│     └─→ cv_quality.py                                       │
│         Rejects scores below 30                             │
│                                                             │
│  3. Viora NER (ONNX INT8) — <100ms                          │
│     └─→ viora_ner_service.py                                │
│         8 entity types: PERSON, SKILL, JOB_TITLE,          │
│         ORG, LOCATION, CONTACT, CREDENTIAL, EXPERIENCE      │
│     └─→ cv_parsers.py: soft skills + years of experience    │
│                                                             │
│  4. O*NET Taxonomy — <50ms                                  │
│     └─→ onet_service.py                                     │
│         Job matching: exact → alias → semantic → fuzzy      │
│         Gap analysis: skills + tech_skills + knowledge      │
│     └─→ esco_resolver.py: essential vs optional skills      │
│                                                             │
│  5. Result Merging                                          │
│     └─→ hybrid_analysis_service.py                          │
│         Strong skills + missing skills + job opportunities  │
│                                                             │
│  Total: <200ms (compared to 5-10s with Gemini)              │
└─────────────────────────────────────────────────────────────┘
```

### Job Matching Strategy (4 stages)

```
Extracted Job Title
    │
    ├─ 1. Exact Match → exact match (100%)
    │
    ├─ 2. Alias Lookup → 60+ aliases, sorted by length descending
    │      (e.g., "attorney" → "Lawyers")
    │
    ├─ 3. Semantic Match → all-MiniLM-L6-v2 (cosine similarity ≥0.45)
    │      (e.g., "Chemical Process Engineer" → "Chemical Engineers")
    │
    └─ 4. Fuzzy Match → RapidFuzz WRatio (score ≥70)
           with False-Positive list: Java≠JavaScript, C≠C++
```

---

## Environment Variables

```env
# --- Database ---
DATABASE_URL=sqlite:///./viora.db
# PostgreSQL: postgresql://user:pass@localhost:5432/viora_db

# --- Security ---
SECRET_KEY=change-this-to-a-random-32-char-string

# --- AI ---
GEMINI_API_KEY=                 # Required for chat
YOUTUBE_API_KEY=                # Optional — for learning roadmap videos

# --- SMTP (Optional — for password reset) ---
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your@gmail.com
SMTP_PASSWORD=app-password
SMTP_FROM_EMAIL=noreply@viora.app

# --- Technical Settings ---
LOG_LEVEL=INFO                  # DEBUG, INFO, WARNING, ERROR
CORS_ORIGINS=                   # Comma-separated list of origins
NER_CONFIDENCE_THRESHOLD=0.50   # NER confidence threshold (0.0-1.0)
```

---

## Tests

```bash
# Run all tests
pytest test/ -v

# Specific test
pytest test/test_full_pipeline.py -v
pytest test/test_onet_service.py -v
pytest test/test_chat.py -v
pytest test/test_quota.py -v
```

| Test File | Description |
|---|---|
| `test_full_pipeline.py` | Full pipeline test (upload → analyze → gaps → roadmap) |
| `test_onet_service.py` | O\*NET job matching + gap analysis test |
| `test_chat.py` | Smart assistant chat test |
| `test_quota.py` | API quota management test |

---

## Technical Notes

### Design Patterns
- **Singleton Pattern**: All heavy services (NER, O\*NET, ESCO, LLM) loaded once
- **Lazy Initialization**: Models loaded on first use (with optional `warmup()`)
- **Dependency Injection**: Via FastAPI `Depends()`
- **Service Layer**: Business logic separated from controllers (thin controllers)
- **Single Responsibility**: Each file responsible for one function

### Performance
- **Viora NER ONNX INT8**: 119MB instead of 1.76GB (GLiNER), under 100ms inference
- **O\*NET Taxonomy**: Under 50ms, 100% deterministic, no internet required
- **Total Analysis**: Under 200ms (compared to 5-10 seconds with Gemini)
- **Semantic Matching**: all-MiniLM-L6-v2 (22M params, 80MB), embeddings cached on disk

### Security
- **bcrypt**: Password hashing (truncates at 72 bytes)
- **Dual JWT**: access + refresh tokens with type checking
- **itsdangerous**: Time-limited password reset tokens
- **SECRET_KEY Guard**: Prevents production startup with default key
- **Anti-Enumeration**: forgot-password always returns success
- **IDOR Prevention**: All endpoints filter by `user_id`

### Data Lifecycle
- **Soft Delete**: Analyses and roadmaps are archived (not deleted) on re-analysis
- **File Cleanup**: CV files deleted after successful analysis
- **Chat Preservation**: Chat history preserved across re-analyses

### Key Libraries

| Library | Version | Usage |
|---|---|---|
| FastAPI | 0.135.1 | Web framework |
| SQLAlchemy | 2.0.48 | ORM + database |
| Pydantic | 2.12.5 | Data validation + settings |
| bcrypt | 5.0.0 | Password hashing |
| python-jose | 3.5.0 | JWT tokens |
| PyMuPDF | 1.27.2 | PDF text extraction |
| python-docx | 1.2.0 | DOCX text extraction |
| transformers | 4.57.6 | NER model tokenizer |
| onnxruntime | 1.24.3 | ONNX inference |
| sentence-transformers | 5.3.0 | Semantic matching |
| RapidFuzz | 3.14.3 | Fuzzy string matching |
| google-genai | 1.66.0 | Gemini API (chat) |
| requests | 2.32.5 | HTTP client |
| itsdangerous | 2.2.0 | Secure tokens |
| duckduckgo-search | 8.1.1 | Free web search |
| uvicorn | 0.41.0 | ASGI server |
