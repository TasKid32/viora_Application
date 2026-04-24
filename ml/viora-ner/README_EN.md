# 🧠 Viora NER Engine
### Named Entity Recognition for Smart CV Analysis

## 📋 Overview
The **Viora NER Engine** is a specialized AI system designed to automate resume parsing. It transforms unstructured text from CVs into structured data, enabling smart job matching and career guidance.

## 🚀 Technical Highlights
* **Core Model:** Powered by a fine-tuned `RoBERTa` architecture for superior context understanding.
* **Optimized Performance:** Uses `ONNX` runtime for ultra-fast inference (under **100ms**).
* **Privacy-First:** Fully local processing, ensuring user data never leaves the server during analysis.

## 🔍 Extracted Entities (8 Types)
The system identifies and extracts:
* **SKILL:** Technical and soft skills.
* **JOB_TITLE:** Professional roles and positions.
* **ORG:** Companies and educational institutions.
* **CREDENTIAL:** Degrees and certifications.
* **EXPERIENCE:** Work durations and dates.
* **PERSON, CONTACT, & LOCATION.**

## 🛠️ Pipeline
1. **Extraction:** Converting documents to clean text.
2. **Analysis:** Deep learning model classifies text segments using the **BIO Tagging** scheme.
3. **Integration:** Results are mapped to the **O*NET Taxonomy** for gap analysis and roadmap generation.