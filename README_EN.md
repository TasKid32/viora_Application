> 🌐 [النسخة العربية (README.md)](README.md)

# 🎯 Viora — AI-Powered Career Development Platform

> An intelligent platform for locally analyzing CVs using Viora NER (ONNX), skill gap analysis via O\*NET occupational taxonomy, personalized learning roadmaps, and a smart career assistant powered by Gemini.

---

## 📋 Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Architecture](#-project-architecture)
- [Prerequisites](#-prerequisites)
- [Setup Guide](#-step-by-step-setup)
- [Connecting the App to Backend](#-connecting-the-app-to-backend)
- [Environment Variables](#-environment-variables)
- [API Endpoints](#-api-endpoints)
- [Detailed Project Structure](#-detailed-project-structure)
- [Analysis Pipeline](#-analysis-pipeline)
- [License](#-license)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📄 **CV Analysis** | Upload your CV (PDF/DOCX) — fully local analysis without external APIs (English only) |
| 🎯 **Skill Gap Analysis** | Identifies strong and missing skills (hard + soft + technical) with predicted job title and experience level via O\*NET |
| 🗺️ **Learning Roadmap** | Personalized multi-phase learning path with courses from YouTube, Udemy, Coursera, and edX |
| 💬 **Smart Career Assistant** | AI chat powered by Gemini 2.5 Flash that understands your skills context and career goals |
| 📊 **Progress Tracking** | Dashboard with weekly activity, completed courses, and progress percentage |
| 📚 **Course Management** | Full CRUD course registration and tracking |
| 🔔 **Notifications** | Activity alerts with read/delete functionality |
| 🌐 **Bilingual Support** | Full Arabic/English translation with RTL support |
| 🔒 **Advanced Security** | Dual JWT (access + refresh) + bcrypt + email password reset |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.11.9 · FastAPI 0.135 · SQLAlchemy 2.0 · Pydantic V2 · Uvicorn |
| **AI (CV)** | Viora NER (RoBERTa ONNX INT8 — 119MB) · O\*NET Taxonomy · ESCO v1.2.1 |
| **AI (Chat)** | Google Gemini 2.5 Flash (chat only) |
| **Job Matching** | Semantic Matching (all-MiniLM-L6-v2) · RapidFuzz · Alias Database |
| **Mobile App** | Flutter 3.x (Dart SDK ^3.6.0) · Provider · Dio · GoRouter |
| **Database** | SQLite (dev) · PostgreSQL (production) |
| **Localization** | Flutter l10n (ARB — Arabic + English) |

---

## 🏗️ Project Architecture

The project consists of **3 main components**:

```
viora_app/
├── backend/        ← Backend server (FastAPI + Python)
├── mobile/         ← Mobile app (Flutter + Dart)
├── ml/             ← ML models and taxonomy data
│   └── viora-ner/  ← Custom NER model for CVs
├── README.md       ← Arabic documentation
├── README_EN.md    ← This file
└── .gitignore
```

| Component | Description | Detailed Docs |
|-----------|-------------|---------------|
| **Backend** | RESTful API — 9 route groups, 19 services, 7 tables | [`backend/README.md`](backend/README.md) |
| **ML / Viora NER** | NER model trained on CV data | [`ml/viora-ner/README_EN.md`](ml/viora-ner/README_EN.md) |
| **Taxonomy** | O\*NET data (1016 occupations) + ESCO (85K skills) | [`ml/viora-ner/data/taxonomy/README.md`](ml/viora-ner/data/taxonomy/README.md) |
| **Mobile** | Flutter app with 8 feature-based modules | — |

---

## 📦 Prerequisites

| Tool | Version | Download |
|------|---------|----------|
| **Python** | 3.11.9 | [python.org](https://www.python.org/downloads/) |
| **Flutter** | 3.x (stable) · Dart SDK ^3.6.0 | [flutter.dev](https://docs.flutter.dev/get-started/install) |
| **Git** | Any recent version | [git-scm.com](https://git-scm.com/downloads) |
| **Android Studio** or **VS Code** | Latest | For Flutter development and Android emulator |

**Required API Keys:**
- **Google Gemini API Key** *(required)* — Get it free from [Google AI Studio](https://aistudio.google.com/apikey)
- **YouTube Data API Key** *(optional)* — For learning roadmap videos from [Google Cloud Console](https://console.cloud.google.com/)

> ⚠️ **Note**: CV analysis works **entirely locally** without any API key — Viora NER ONNX model + O\*NET data are bundled with the project.

---

## 🚀 Step-by-Step Setup

### 1. Clone the Repository

```bash
git clone https://github.com/TasKid32/viora_Application.git
cd Viora_app
```

---

### 2. Setup the Backend (Terminal 1)

Open a terminal and run the following commands:

```bash
# Navigate to the backend directory
cd backend

# Create a Python virtual environment
python -m venv venv

# Activate the virtual environment
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1

# Install required packages
pip install -r requirements.txt
```

---

### 3. Download ML Data (Models & Datasets)

> ⚠️ **This step is required!** Model and dataset files are large (~1.6 GB) and are not hosted on GitHub. They must be downloaded separately.

#### Method 1: Via Script (Recommended)

Navigate back to the project root and run the setup script:

```bash
cd ..
python setup_ml_data.py
```

The script will automatically download the archive from Google Drive, extract it, and place all files in their correct locations.


4. Verify these directories exist after extraction:
   - `ml/viora-ner/models/checkpoints/best_model/`
   - `ml/viora-ner/models/exported/onnx/`
   - `ml/viora-ner/models/exported/onnx_quantized/`
   - `ml/viora-ner/data/processed/`
   - `ml/viora-ner/data/raw/`

> 📦 **Archive Contents:**
> | Directory | Size | Description |
> |-----------|------|-------------|
> | `ml/viora-ner/models/` | ~1.1 GB | Trained NER models (safetensors + ONNX + quantized) |
> | `ml/viora-ner/data/processed/` | ~467 MB | Processed training data |
> | `ml/viora-ner/data/raw/` | ~101 MB | Raw datasets (Kaggle NER + HF Resumes) |
> | `ml/viora-ner/data/cache/` | ~1 MB | Pre-computed embedding cache |

Navigate back to the backend directory to continue setup:

```bash
cd backend
```

---

### 4. Environment Variables & Running the Server

**Setup environment variables:**

```bash
# Copy the example environment file
# Windows:
copy .env.example .env


**Edit `.env`** and add your API keys:

```env
# Required — get from https://aistudio.google.com/apikey
GEMINI_API_KEY=your-gemini-key-here

# For learning roadmap videos
YOUTUBE_API_KEY=your-youtube-key-here

# Security — change this in production! (system refuses to start with default)
SECRET_KEY=change-this-to-a-long-random-string
```

**Start the backend server:**

```bash
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

> ⚠️ **Important:** Use `--host 0.0.0.0` (not `localhost`) so the server is accessible from other devices on your network.

> ℹ️ **First run:** The system loads the Viora NER ONNX model (~119MB) and O\*NET data (~1016 occupations) automatically. This may take ~10 seconds.

✅ Backend is now running! Check:
- **API root:** http://localhost:8000
- **Swagger docs:** http://localhost:8000/docs
- **Health check:** http://localhost:8000/health

---

### 5. Setup and Run the Mobile App (Terminal 2)

Open a **new/separate terminal** and run:

```bash
# Navigate to the mobile directory
cd mobile

# Install Flutter packages
flutter pub get

# Generate localization files
flutter gen-l10n
```

**⚡ Before running, set the API URL** (see next section):

```bash
# Run with your computer's IP address (replace with your IP)
flutter run --dart-define=API_URL=http://192.168.1.100:8000
```

Or run directly (default address `10.0.2.2:8000` for Android emulator):

```bash
flutter run
```

---

## 🌐 Connecting the App to Backend

For the app to communicate with the backend, **both devices must be on the same Wi-Fi network**.

### Step 1: Find Your Computer's IP Address

```bash
# Windows:
ipconfig
# Look for "IPv4 Address" under Wi-Fi adapter (e.g., 192.168.1.100)

```

### Step 2: Set the API URL in Flutter

There are **3 methods** to set the API URL:

#### Method 1: At build time (Recommended for development)

```bash
flutter run --dart-define=API_URL=http://YOUR_IP:8000
# Example:
flutter run --dart-define=API_URL=http://192.168.1.100:8000
```

#### Method 2: Modify the source code

Open `mobile/lib/core/config/environment.dart` and change the default value:

```dart
static const String _buildTimeApiUrl = String.fromEnvironment(
  'API_URL',
  defaultValue: 'http://YOUR_IP:8000',  // ← change this
);
```

#### Method 3: Android Emulator

If using Android Studio emulator, use the special address `10.0.2.2` (maps to your computer's `localhost`):

```bash
flutter run --dart-define=API_URL=http://10.0.2.2:8000
```

### ⚠️ Common Connection Issues

| Problem | Solution |
|---------|----------|
| App can't connect to backend | Ensure both devices are on the **same Wi-Fi network** |
| Connection refused | Ensure backend is running with `--host 0.0.0.0` (not `127.0.0.1`) |
| Timeout | Check firewall — allow port `8000` |
| Using Android emulator | Use `http://10.0.2.2:8000` instead of `localhost` |
| IP changed | Run `ipconfig` again and update the API URL |

---

## 🔧 Environment Variables

### Backend (`backend/.env`)

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | ✅ | Database URL. Default: `sqlite:///./viora.db` |
| `SECRET_KEY` | ✅ | JWT signing key. **System refuses to start with default value** |
| `GEMINI_API_KEY` | ✅ | Gemini key — for smart chat only (not CV analysis) |
| `YOUTUBE_API_KEY` | ❌ | YouTube Data v3 key — for learning roadmap videos |
| `SMTP_HOST` / `SMTP_USERNAME` / `SMTP_PASSWORD` | ❌ | SMTP for password reset emails |
| `NER_CONFIDENCE_THRESHOLD` | ❌ | NER confidence threshold. Default: `0.50` |
| `CORS_ORIGINS` | ❌ | Allowed origins, comma-separated |
| `LOG_LEVEL` | ❌ | Logging level. Default: `INFO` |

### Mobile App (`mobile/lib/core/config/environment.dart`)

| Setting | Default | Override |
|---------|---------|----------|
| API URL | `http://10.0.2.2:8000` | `--dart-define=API_URL=...` |
| Connect timeout | 15 seconds | `Environment.connectTimeout` |
| Receive timeout | 30 seconds | `Environment.receiveTimeout` |
| Upload timeout | 60 seconds | `Environment.uploadTimeout` |
| Max file size | 10 MB | `Environment.maxFileSizeMB` |

---

## 📝 API Endpoints

### Authentication
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/register` | POST | Register new user (returns access + refresh tokens) |
| `/api/auth/login` | POST | Login |
| `/api/auth/refresh` | POST | Refresh access token from refresh token |
| `/api/auth/forgot-password` | POST | Request password reset email |
| `/api/auth/reset-password` | POST | Reset password with code |

### CV Analysis
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/resume/upload` | POST | Upload CV (PDF/DOCX — 10MB limit, English only) |
| `/api/resume/analyze` | POST | Hybrid analysis (Viora NER + O\*NET) |
| `/api/resume/analyze/stream` | POST | SSE streaming analysis (stage events) |

### Learning Roadmap
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/roadmap` | GET | Get learning roadmap |
| `/api/roadmap/generate` | POST | Generate roadmap from analysis results |
| `/api/roadmap/steps/{id}/complete` | PUT | Mark phase as completed |
| `/api/roadmap/steps/{id}/incomplete` | PUT | Mark phase as incomplete |
| `/api/roadmap/steps/{id}/resources/{res_id}/toggle` | PUT | Toggle resource completion |

### Smart Assistant, Courses & Dashboard
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/chat/send` | POST | Send message to smart assistant (Gemini) |
| `/api/chat/history` | GET | Last 50 chat messages |
| `/api/chat/history` | DELETE | Clear chat history |
| `/api/dashboard` | GET | Dashboard data (weighted progress + resource tracking) |
| `/api/courses` | GET/POST | List or create courses |
| `/api/courses/{id}` | GET/PUT/DELETE | CRUD operations on courses |
| `/api/progress/weekly` | GET | Real weekly activity stats |

### Profile & Notifications
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/profile` | GET/PUT | View/edit profile |
| `/api/profile/avatar` | POST | Upload avatar (JPEG/PNG/WebP) |
| `/api/profile/settings/language` | PUT | Change UI language |
| `/api/notifications` | GET | All notifications |
| `/api/notifications/{id}/read` | PUT | Mark notification as read |
| `/api/notifications/read-all` | PUT | Mark all as read |
| `/api/notifications/{id}` | DELETE | Delete notification |

> 📖 Full interactive API docs available at `http://localhost:8000/docs` when the backend is running.

---

## 🔄 Analysis Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│                  CV Analysis Pipeline                        │
│          (Fully Local — No External APIs — <200ms)           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  📤 Upload CV (PDF/DOCX)                                    │
│    └─→ text_extractor.py (PyMuPDF / python-docx)            │
│                                                             │
│  📋 CV Quality Score (0-100)                                │
│    └─→ cv_quality.py                                        │
│        Rejects scores below 30                              │
│                                                             │
│  🧠 Viora NER (ONNX INT8 — 119MB) — <100ms                 │
│    └─→ viora_ner_service.py                                 │
│        8 entities: PERSON, SKILL, JOB_TITLE, ORG,          │
│        LOCATION, CONTACT, CREDENTIAL, EXPERIENCE            │
│    └─→ cv_parsers.py                                        │
│        Soft skills (~50 ESCO) + years of experience         │
│                                                             │
│  🎯 O*NET + ESCO — <50ms                                    │
│    └─→ onet_service.py                                      │
│        Job matching: exact → alias → semantic → fuzzy       │
│        Gap analysis: skills + tech_skills + knowledge       │
│    └─→ esco_resolver.py                                     │
│        Soft skill classification (96 transversal skills)    │
│                                                             │
│  🔗 Result Merging                                           │
│    └─→ hybrid_analysis_service.py                           │
│        Strong skills + missing skills + job opportunities   │
│                                                             │
│  📊 Total: <200ms (compared to 5-10s with Gemini)           │
└─────────────────────────────────────────────────────────────┘
```

---

## 📄 License

MIT License

---

**Version:** 1.0.0 · **Status:** 🚧 Active Development · **Last Updated:** April 2026
