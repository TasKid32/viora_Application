# 🎯 Viora — AI-Powered Career Development Platform
### Intelligent System for Local CV Analysis and Career Roadmap Generation

---

## 📋 Table of Contents
- [✨ Features](#-features)
- [🛠️ Tech Stack](#-tech-stack)
- [🏗️ Project Architecture](#-project-architecture)
- [🔄 AI Analysis Pipeline](#-ai-analysis-pipeline)
- [🚀 Setup Guide](#-setup-guide)
- [🌐 Connection & Environment](#-connection--environment)
- [🔒 Security & Privacy](#-security--privacy)

---

## ✨ Features
| Feature | Description |
| :--- | :--- |
| 📄 **CV Analysis** | Fully local analysis of PDF/DOCX files with high entity extraction accuracy. |
| 🎯 **Skill Gap Analysis** | Matches your skills with O*NET global standards to identify career gaps. |
| 🗺️ **Learning Roadmaps** | Personalized paths linking you to top courses on YouTube, Coursera, and Udemy. |
| 💬 **Smart Career Assistant** | Gemini-powered AI chat providing career advice based on your profile context. |
| 📊 **Progress Tracking** | Dashboard with weekly activity tracking and course completion visuals. |
| 🌐 **Bilingual Support** | Full Arabic and English interface with RTL support. |

---

## 🛠️ Tech Stack
* **Mobile App:** Flutter & Dart (Provider, Dio, GoRouter).
* **Backend:** Python (FastAPI, SQLAlchemy, Pydantic V2).
* **AI Engine:** RoBERTa NER (ONNX Quantized for speed).
* **Taxonomy:** O*NET Occupational Data & ESCO v1.2.1.
* **LLM:** Google Gemini 2.5 Flash (For Chat Assistant only).
* **Database:** SQLite (Dev) & PostgreSQL (Prod).

---

## 🏗️ Project Architecture
The project is organized into three main components:
* **`backend/`**: Restful API, database management, and business logic.
* **`mobile/`**: Flutter mobile application source code.
* **`ml/`**: Machine Learning models and occupational taxonomy data.

---

## 🔄 AI Analysis Pipeline
Viora utilizes a high-speed pipeline ensuring analysis results in under **200ms**:

![NER Inference Pipeline for Resume Analysis](ml/viora-ner/docs/pipeline_diagram.png)

1. **Extraction:** Converts uploaded CVs into clean, processable text.
2. **NER Engine:** Classifies text into 8 categories (Skills, Titles, Orgs, etc.).
3. **Matching:** Maps extracted skills to 1016 O*NET-certified occupations.
4. **Analysis:** Generates a skill gap report and a tailored learning roadmap.

---

## 🚀 Setup Guide

### 1. Clone the Repository
```bash
git clone https://github.com/TasKid32/viora_Application.git

```
### 2. Backend Setup
```bash
cd backend
python -m venv venv
# Activate environment (Windows)
.\venv\Scripts\Activate.ps1
# Install dependencies
pip install -r requirements.txt

```
### 3. Download AI Models (ML Data)
> ⚠️ **Mandatory Step:** Run this script to download required NER models and data (~1.6 GB).
> 
```bash
cd ..
python setup_ml_data.py

```
### 4. Run Mobile App
```bash
cd mobile
flutter pub get
flutter gen-l10n
# Run the app (Replace YOUR_IP with your computer's IP)
flutter run --dart-define=API_URL=http://YOUR_IP:8000

```

## 🔒 Security & Privacy
 * **Data Privacy:** CVs are analyzed locally; no personal data is sent to 3rd party analysis APIs.
 * **Encryption:** Bcrypt for password hashing and secure JWT session management.
 * **Session Safety:** Dual-token system (Access & Refresh) for robust user protection.
**Version:** 1.0.0 | **Status:** GP Phase 2 | **Last Updated:** April 2026
```

```
