# ⚙️ Viora Backend Engine
### Smart Career Development System — Backend Server

## 📋 Overview
The **Viora Backend** is a high-performance server built with **FastAPI**. It serves as the brain of the system, managing communication between the mobile app, the database, and the AI analysis engine.

## 🚀 Technical Highlights
* **High Performance:** CV analysis and processing completed in under **200ms**.
* **100% Local Analysis:** CVs are analyzed locally using **ONNX** for maximum privacy and efficiency.
* **Professional Matching:** Integrated with the **O*NET Taxonomy** for precise job matching and gap analysis.
* **Smart Resource Retrieval:** Automated search for courses on YouTube, Coursera, and Udemy.

## 📂 System Architecture
* **API Layer:** Handles authentication, file uploads, and the smart chat assistant.
* **Service Layer:** Contains the business logic for entity extraction, skill matching, and roadmap generation.
* **Database Layer:** Manages user data and analysis history using SQLAlchemy ORM.

## 🔒 Security & Privacy
* Secure password hashing using **Bcrypt**.
* Robust authentication with **Dual JWT Tokens** (Access & Refresh).
* Privacy-first approach with automated file cleanup after analysis.