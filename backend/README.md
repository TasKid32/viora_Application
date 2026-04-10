<div dir="rtl">

# 🖥️ Viora Backend — واجهة برمجة التطبيقات

> 🌐 [English Version (README_EN.md)](README_EN.md)

**نظام التطوير المهني الذكي — الخادم الخلفي**

واجهة برمجة تطبيقات RESTful مبنية بـ FastAPI، تُدير تحليل السير الذاتية باستخدام نموذج Viora NER محلي (ONNX) مدمج مع تصنيف O\*NET المهني، بدون أي اعتماد على APIs خارجية لتحليل السيرة الذاتية. يُستخدم Gemini فقط كمساعد محادثة ذكي.

---

## 📋 جدول المحتويات

- [الإعداد والتشغيل](#الإعداد-والتشغيل)
- [هيكل المشروع](#هيكل-المشروع)
- [بنية التطبيق](#بنية-التطبيق)
  - [نقطة الدخول](#نقطة-الدخول-mainpy)
  - [طبقة Core](#طبقة-core)
  - [طبقة قاعدة البيانات](#طبقة-قاعدة-البيانات)
  - [طبقة API](#طبقة-api)
  - [طبقة Schemas](#طبقة-schemas)
  - [طبقة Services](#طبقة-services)
- [خط أنابيب تحليل السيرة الذاتية](#خط-أنابيب-تحليل-السيرة-الذاتية)
- [نقاط النهاية API Endpoints](#نقاط-النهاية-api-endpoints)
- [نماذج قاعدة البيانات](#نماذج-قاعدة-البيانات)
- [الخدمات الخارجية](#الخدمات-الخارجية)
- [متغيرات البيئة](#متغيرات-البيئة)
- [الاختبارات](#الاختبارات)
- [ملاحظات تقنية](#ملاحظات-تقنية)

---

## الإعداد والتشغيل

> 📖 لتعليمات التثبيت والتشغيل الكاملة خطوة بخطوة، راجع [**README الرئيسي**](../README.md#-إعداد-المشروع-خطوة-بخطوة)

**المتطلبات**: Python 3.11.9 · نموذج Viora NER ONNX · بيانات O\*NET + ESCO

**الخادم**: `http://localhost:8000` · **Swagger**: `http://localhost:8000/docs`

---

## هيكل المشروع

```
backend/
├── main.py                    # نقطة الدخول الرئيسية — FastAPI app
├── requirements.txt           # المتطلبات (Python 3.11.9)
├── .env                       # متغيرات البيئة (غير متتبع بـ Git)
├── .env.example               # قالب متغيرات البيئة
├── viora.db                   # قاعدة بيانات SQLite (تُنشأ تلقائياً)
├── uploads/                   # مجلد الملفات المرفوعة (صور + CVs مؤقتة)
│   └── avatars/               # صور الملفات الشخصية
├── test/                      # اختبارات pytest
│   ├── test_full_pipeline.py  # اختبار خط الأنابيب الكامل
│   ├── test_onet_service.py   # اختبار خدمة O*NET
│   ├── test_chat.py           # اختبار المحادثة الذكية
│   └── test_quota.py          # اختبار إدارة الحصص
│
└── app/                       # كود التطبيق الرئيسي
    ├── __init__.py
    ├── core/                  # الإعدادات والأمان والأدوات المشتركة
    │   ├── config.py          # إعدادات Pydantic Settings
    │   ├── dependencies.py    # دوال Dependency Injection
    │   ├── logging.py         # نظام التسجيل المُهيكل
    │   ├── quota_handler.py   # معالجة استنفاد حصص APIs
    │   └── security.py        # تشفير كلمات المرور + JWT + إعادة التعيين
    │
    ├── db/                    # طبقة قاعدة البيانات
    │   ├── database.py        # إعداد SQLAlchemy Engine + Session
    │   ├── models.py          # نماذج ORM (7 جداول)
    │   └── init_db.py         # تهيئة وفحص قاعدة البيانات
    │
    ├── api/v1/                # نقاط النهاية (API Endpoints)
    │   ├── auth.py            # تسجيل + دخول + تحديث Token + نسيان كلمة المرور
    │   ├── resume.py          # رفع + تحليل السيرة الذاتية (SSE streaming)
    │   ├── roadmap.py         # خارطة التعلم (توليد + تتبع الإكمال)
    │   ├── chat.py            # المساعد الذكي (Gemini)
    │   ├── dashboard.py       # لوحة المعلومات
    │   ├── courses.py         # إدارة الدورات (CRUD كامل)
    │   ├── notifications.py   # الإشعارات
    │   ├── profile.py         # الملف الشخصي + رفع الصور
    │   └── progress.py        # تتبع التقدم الأسبوعي
    │
    ├── schemas/               # نماذج Pydantic للتحقق من البيانات
    │   ├── auth_schemas.py
    │   ├── resume_schemas.py
    │   ├── chat_schemas.py
    │   ├── course_schemas.py
    │   ├── dashboard_schemas.py
    │   ├── notification_schemas.py
    │   └── progress_schemas.py
    │
    └── services/              # طبقة الأعمال (Business Logic)
        ├── auth_service.py            # منطق التسجيل والتوثيق
        ├── hybrid_analysis_service.py # دمج NER + O*NET (الخط الهجين)
        ├── viora_ner_service.py       # استخراج الكيانات بـ ONNX
        ├── onet_service.py            # مطابقة المهن + تحليل الفجوات
        ├── onet_data_loader.py        # تحميل ملفات O*NET TSV
        ├── onet_roadmap.py            # توليد خارطة التعلم
        ├── esco_resolver.py           # تصنيف ESCO (85K مهارة)
        ├── cv_parsers.py              # استخراج المهارات الناعمة + الخبرة
        ├── cv_quality.py              # تقييم جودة السيرة الذاتية
        ├── text_extractor.py          # استخراج النص (PDF/DOCX)
        ├── file_upload.py             # حفظ الملفات المرفوعة
        ├── llm_service.py             # Gemini API (للمحادثة فقط)
        ├── email_service.py           # إرسال بريد SMTP
        ├── youtube_service.py         # بحث فيديوهات YouTube
        ├── udemy_service.py           # روابط بحث Udemy
        ├── coursera_service.py        # روابط بحث Coursera
        ├── edx_service.py             # روابط بحث edX
        ├── course_search_service.py   # بحث Google Custom Search عن دورات
        └── web_search_service.py      # بحث ويب (DuckDuckGo)
```

---

## بنية التطبيق

### نقطة الدخول (`main.py`)

ملف `main.py` هو نقطة الدخول الرئيسية للتطبيق، ويقوم بالتالي:

1. **Lifespan Event**: يُحمّل نموذج Viora NER ONNX (~120MB) وبيانات O\*NET (~1016 وظيفة) مسبقاً عند بدء التشغيل لتجنب تأخر الطلب الأول (Cold Start)
2. **CORS Middleware**: يدعم أصول متعددة قابلة للتكوين عبر متغير بيئة `CORS_ORIGINS` أو القيم الافتراضية (`localhost:8080`, `3000`, `5173`)
3. **9 Routers**: يُسجّل 9 موجّهات API تحت المسار `/api/`
4. **Static Files**: يخدم مجلد `uploads/` للصور والملفات المرفوعة
5. **Health Check**: نقطة `/health` لفحص حالة الخادم

### طبقة Core

#### `config.py` — الإعدادات المركزية
- يستخدم `pydantic-settings` (V2) لتحميل الإعدادات من `.env`
- **حماية SECRET_KEY**: يرفض التشغيل في الإنتاج إذا كان المفتاح الافتراضي لم يُغيَّر (`model_validator` يمنع تزوير JWT)
- يدعم SQLite (للتطوير) و PostgreSQL (للإنتاج) عبر `DATABASE_URL`
- إعدادات قابلة للتكوين: حجم الملف الأقصى (10MB)، مسار نموذج NER، عتبة ثقة NER (0.50)، إعدادات SMTP، أصول CORS

#### `security.py` — الأمان والتوثيق
- **تشفير كلمات المرور**: يستخدم `bcrypt` مباشرة (يقطع على 72 بايت حسب مواصفات bcrypt)
- **JWT Tokens**: نظام Token مزدوج:
  - `access_token`: صالح 24 ساعة، نوع `"access"`
  - `refresh_token`: صالح 7 أيام، نوع `"refresh"`
  - فحص `token_type` يمنع استخدام refresh كـ access والعكس
- **Password Reset**: يستخدم `itsdangerous.URLSafeTimedSerializer` لتوليد رموز إعادة تعيين محدودة الوقت (30 دقيقة)، منفصلة عن JWT

#### `dependencies.py` — Dependency Injection
- `get_current_user()`: يستخرج المستخدم الحالي من JWT Bearer token، يُستخدم في جميع نقاط النهاية المحمية

#### `logging.py` — التسجيل المُهيكل
- يستخدم `logging` القياسي بدلاً من `print()`
- تنسيق: `YYYY-MM-DD HH:MM:SS | LEVEL | module | message`
- مستوى التسجيل قابل للتكوين عبر `LOG_LEVEL` في `.env`

#### `quota_handler.py` — إدارة حصص APIs
- لا يحد من المستخدمين بل يتعامل مع استنفاد حصص YouTube و Gemini
- يُصدر `HTTP 429` مع رسالة واضحة عند استنفاد الحصة

### طبقة قاعدة البيانات

#### `database.py` — اتصال قاعدة البيانات
- يدعم **SQLite** (للتطوير: `check_same_thread=False`) و **PostgreSQL** (للإنتاج: pool_size=10, max_overflow=20)
- يستخدم `DeclarativeBase` من SQLAlchemy 2.0
- `get_db()`: يُنتج جلسة مع `rollback` تلقائي عند الأخطاء

#### `models.py` — نماذج ORM (7 جداول)
- جميع المعرفات UUID4 (سلاسل نصية)
- جميع التواريخ timezone-aware (UTC)
- `cascade="all, delete-orphan"` على جميع العلاقات

| الجدول | الوصف | الحقول الرئيسية |
|---|---|---|
| `users` | المستخدمون | full_name, email, password_hash, avatar_url, bio, phone_number, language |
| `resumes` | السير الذاتية المرفوعة | file_path, original_filename, language |
| `skill_analyses` | نتائج التحليل | predicted_job_title, experience_level, strong_skills (JSON), missing_skills (JSON), extracted_entities (JSON), is_archived |
| `learning_roadmaps` | خرائط التعلم | roadmap_data (JSON), is_archived |
| `notifications` | الإشعارات | type, title, message, is_read |
| `chat_history` | سجل المحادثات | message, reply |
| `courses` | الدورات | title, category, platform, completion (0-100) |

#### `init_db.py` — تهيئة قاعدة البيانات
- يُنشئ الجداول تلقائياً عبر `Base.metadata.create_all()`
- `verify_tables()`: يتحقق من وجود جميع الجداول السبعة المتوقعة
- `test_connection()`: يختبر الاتصال ويعرض إصدار قاعدة البيانات

### طبقة API

#### `auth.py` — المصادقة (6 نقاط نهاية)
| الطريقة | المسار | الوصف |
|---|---|---|
| POST | `/api/auth/register` | تسجيل مستخدم جديد (إرجاع access + refresh tokens) |
| POST | `/api/auth/login` | تسجيل الدخول |
| POST | `/api/auth/refresh` | تجديد access token من refresh token |
| POST | `/api/auth/forgot-password` | طلب إعادة تعيين كلمة المرور (يرسل بريد SMTP) |
| POST | `/api/auth/reset-password` | إعادة تعيين كلمة المرور بالرمز المُرسل |

> **ملاحظة أمنية**: `forgot-password` يُرجع نجاح دائماً (لمنع هجمات تعداد البريد الإلكتروني)

#### `resume.py` — تحليل السيرة الذاتية (3 نقاط نهاية)
| الطريقة | المسار | الوصف |
|---|---|---|
| POST | `/api/resume/upload` | رفع CV (PDF/DOCX) — حد 10MB، إنجليزي فقط |
| POST | `/api/resume/analyze` | تحليل CV (يرفض السير العربية + PDF المحمي + الملفات الفارغة) |
| POST | `/api/resume/analyze/stream` | تحليل بث SSE (أحداث مرحلية في الوقت الفعلي) |

**ميزات متقدمة**:
- **تخزين مؤقت**: إذا نفس الـ CV تم تحليله سابقاً، يُرجع النتيجة المخزنة بدون إعادة تحليل
- **حماية متعددة الطبقات**: يرفض السير العربية + PDF المحمي بكلمة مرور + الملفات الفارغة + الملفات > 10MB
- **أرشفة ذكية**: عند إعادة التحليل، يؤرشف التحليلات وخرائط التعلم القديمة (soft delete بدلاً من hard delete) مع الحفاظ على سجل المحادثات
- **تنظيف الملفات**: يحذف ملف CV المرفوع بعد التحليل الناجح (النص مُستخرج والكيانات مُخزنة)
- **بث SSE**: أحداث مرحلية (`extracting_text` → `running_ner` → `matching_onet` → `result`)

#### `roadmap.py` — خارطة التعلم
| الطريقة | المسار | الوصف |
|---|---|---|
| GET | `/api/roadmap` | جلب خارطة التعلم (أحدث أو بمعرف محدد) |
| POST | `/api/roadmap/generate` | توليد خارطة تعلم من نتائج التحليل |
| PUT | `/api/roadmap/steps/{step_id}/complete` | تعليم مرحلة كمكتملة |
| PUT | `/api/roadmap/steps/{step_id}/incomplete` | إلغاء اكتمال مرحلة |
| PUT | `/api/roadmap/steps/{step_id}/resources/{resource_id}/toggle` | تبديل إكمال مورد تعليمي |

#### `chat.py` — المساعد الذكي
| الطريقة | المسار | الوصف |
|---|---|---|
| POST | `/api/chat/send` | إرسال رسالة (يحصل على سياق آخر تحليل + تقدم خارطة التعلم) |
| GET | `/api/chat/history` | سجل آخر 50 محادثة |
| DELETE | `/api/chat/history` | حذف سجل المحادثات |

**ميزة**: يُنشئ اقتراحات ذكية بالعربية بناءً على حالة المستخدم (هل لديه تحليل؟ ما أول مهارة ناقصة؟)

#### `courses.py` — إدارة الدورات (CRUD كامل)
| الطريقة | المسار | الوصف |
|---|---|---|
| GET | `/api/courses` | جميع دورات المستخدم |
| GET | `/api/courses/completed` | الدورات المكتملة فقط |
| GET | `/api/courses/{id}` | دورة محددة |
| POST | `/api/courses` | إضافة دورة |
| PUT | `/api/courses/{id}` | تحديث (يُعيّن completed_date تلقائياً عند completion=100) |
| DELETE | `/api/courses/{id}` | حذف دورة |

#### `dashboard.py` — لوحة المعلومات
- يحسب نسبة التقدم الكلية بنظام **أوزان مرجحة**:
  - 20 نقطة: تحليل CV مكتمل
  - 20 نقطة: خارطة تعلم مُنشأة
  - 60 نقطة: نسبة إكمال الدورات
- **تتبع موارد**: يعد الموارد التعليمية المكتملة (فيديوهات + دورات) داخل خارطة التعلم

#### `notifications.py` — الإشعارات
- جلب + تعليم كمقروء (فردي أو جماعي) + حذف
- أيقونات ذكية حسب النوع: ✅ تحليل، 🏆 إنجاز، 📚 توصية، 📊 تقرير

#### `profile.py` — الملف الشخصي
- تعديل البيانات مع فحص تفرد البريد الإلكتروني
- رفع صورة شخصية (JPEG/PNG/WebP، حد 5MB، يحذف الصورة القديمة تلقائياً)
- تغيير لغة الواجهة

#### `progress.py` — تتبع التقدم
- نشاط أسبوعي حقيقي: يعدّ رسائل المحادثة وتحديثات الدورات لكل يوم من آخر 7 أيام
- قائمة الدورات المكتملة

### طبقة Schemas

نماذج Pydantic V2 تُستخدم للتحقق من بيانات الطلبات والاستجابات:

| الملف | النماذج | الاستخدام |
|---|---|---|
| `auth_schemas.py` | `UserRegister`, `UserLogin`, `Token`, `UserResponse` | المصادقة |
| `resume_schemas.py` | `ResumeUploadResponse`, `SkillsInput`, `AnalysisRequest`, `AnalysisResponse` | تحليل CV |
| `chat_schemas.py` | `ChatMessage`, `ChatResponse` | المحادثة |
| `course_schemas.py` | `CourseResponse`, `CourseCreate`, `CourseUpdate` | الدورات |
| `dashboard_schemas.py` | `DashboardResponse` | لوحة المعلومات |
| `notification_schemas.py` | `NotificationResponse` | الإشعارات |
| `progress_schemas.py` | `WeeklyActivity`, `CompletedCourse` | التقدم |

### طبقة Services

#### خدمات تحليل السيرة الذاتية (محلية 100%)

| الخدمة | الملف | الوصف | الحجم |
|---|---|---|---|
| **Hybrid Analysis** | `hybrid_analysis_service.py` | يدمج NER + O\*NET في خط أنابيب واحد | 275 سطر |
| **Viora NER** | `viora_ner_service.py` | استخراج كيانات CV بنموذج ONNX INT8 (119MB) | 332 سطر |
| **O\*NET Service** | `onet_service.py` | مطابقة مهن + تحليل فجوات + semantic matching | 710 سطر |
| **O\*NET Data Loader** | `onet_data_loader.py` | تحميل 5 ملفات TSV + قاموس أسماء وظيفية | 338 سطر |
| **O\*NET Roadmap** | `onet_roadmap.py` | توليد خارطة تعلم + مطابقة فرص عمل | 232 سطر |
| **ESCO Resolver** | `esco_resolver.py` | تصنيف ESCO v1.2.1 (85K مهارة بديلة + 96 مهارة ناعمة) | 370 سطر |
| **CV Parsers** | `cv_parsers.py` | مهارات ناعمة + سنوات خبرة + سنة تخرج + تنظيف نص | 336 سطر |
| **CV Quality** | `cv_quality.py` | تقييم جودة CV (0-100 نقطة، عربي + إنجليزي) | 131 سطر |

#### خدمات الملفات

| الخدمة | الملف | الوصف |
|---|---|---|
| **Text Extractor** | `text_extractor.py` | استخراج نص من PDF (PyMuPDF) و DOCX (python-docx) |
| **File Upload** | `file_upload.py` | حفظ الملفات مع فحص الحجم (10MB) والتحقق من الفراغ |

#### خدمات خارجية

| الخدمة | الملف | الوصف |
|---|---|---|
| **LLM Service** | `llm_service.py` | Gemini 2.5 Flash — المحادثة **فقط** (ليس التحليل) |
| **Email Service** | `email_service.py` | SMTP — إعادة تعيين كلمة المرور + إشعار التغيير |
| **YouTube** | `youtube_service.py` | YouTube Data API v3 — بحث فيديوهات تعليمية مع مدة |
| **Udemy** | `udemy_service.py` | مولّد روابط بحث ذكية (API مُلغى منذ 2025) |
| **Coursera** | `coursera_service.py` | مولّد روابط بحث ذكية |
| **edX** | `edx_service.py` | مولّد روابط بحث ذكية |
| **Web Search** | `web_search_service.py` | Google → Bing → DuckDuckGo (مجاني) |
| **Auth Service** | `auth_service.py` | منطق التسجيل والدخول (مفصول عن الـ Controllers) |

---

## خط أنابيب تحليل السيرة الذاتية

```
┌─────────────────────────────────────────────────────────────┐
│                    تحليل السيرة الذاتية                      │
│              (محلي بالكامل — بدون APIs خارجية)                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. رفع CV (PDF/DOCX)                                       │
│     └─→ file_upload.py → text_extractor.py                  │
│                                                             │
│  2. تقييم جودة CV (نقاط 0-100)                              │
│     └─→ cv_quality.py                                       │
│         • طول النص ≥ 100 حرف                                │
│         • أقسام: خبرة، تعليم، مهارات، اتصال                  │
│         • وجود بريد إلكتروني                                 │
│         • يرفض الأقل من 30 نقطة                              │
│                                                             │
│  3. Viora NER (ONNX INT8) — <100ms                          │
│     └─→ viora_ner_service.py                                │
│         • 8 أنواع كيانات: PERSON, SKILL, JOB_TITLE,         │
│           ORG, LOCATION, CONTACT, CREDENTIAL, EXPERIENCE    │
│         • فلترة ثقة ≥ 50% (قابل للتكوين)                    │
│         • إعادة تصنيف اللغات (Arabic → ليست SKILL)           │
│         • cv_parsers.py: مهارات ناعمة + سنوات خبرة           │
│                                                             │
│  4. O*NET Taxonomy — <50ms                                  │
│     └─→ onet_service.py                                     │
│         • مطابقة المهنة: exact → alias → semantic → fuzzy    │
│         • تحليل فجوات: skills.txt + technology_skills.txt   │
│         • مستوى الخبرة: NER years → skill ratio fallback     │
│         • ESCO: مهارات أساسية vs اختيارية                    │
│                                                             │
│  5. دمج النتائج                                              │
│     └─→ hybrid_analysis_service.py                          │
│         • مهارات قوية + مهارات ناقصة (صلبة + ناعمة + تقنية)  │
│         • فرص عمل + نقاط قوة + توصيات                       │
│                                                             │
│  إجمالي الوقت: <200ms (مقارنة بـ 5-10 ثوانٍ مع Gemini)      │
└─────────────────────────────────────────────────────────────┘
```

### استراتيجية مطابقة المهن (4 مراحل)

```
المسمى الوظيفي المُستخرج
    │
    ├─ 1. Exact Match → تطابق دقيق (100%)
    │
    ├─ 2. Alias Lookup → 60+ اسم بديل، مرتب بالطول تنازلياً
    │      (مثال: "attorney" → "Lawyers")
    │
    ├─ 3. Semantic Match → all-MiniLM-L6-v2 (cosine similarity ≥0.45)
    │      (مثال: "Chemical Process Engineer" → "Chemical Engineers")
    │
    └─ 4. Fuzzy Match → RapidFuzz WRatio (score ≥70)
           مع قائمة False-Positive: Java≠JavaScript, C≠C++
```

---

## نماذج قاعدة البيانات

```mermaid
erDiagram
    users ||--o{ resumes : "has"
    users ||--o{ skill_analyses : "has"
    users ||--o{ learning_roadmaps : "has"
    users ||--o{ notifications : "has"
    users ||--o{ chat_history : "has"
    users ||--o{ courses : "has"
    resumes ||--o| skill_analyses : "analyzed as"
    skill_analyses ||--o| learning_roadmaps : "generates"
```

---

## الخدمات الخارجية

| الخدمة | الاستخدام | مفتاح API مطلوب |
|---|---|---|
| **Gemini 2.5 Flash** | المساعد الذكي (محادثة فقط) | `GEMINI_API_KEY` (مطلوب) |
| **YouTube Data v3** | بحث فيديوهات تعليمية مع مدة | `YOUTUBE_API_KEY` (اختياري) |
| **SMTP** | إعادة تعيين كلمة المرور | `SMTP_HOST/USERNAME/PASSWORD` (اختياري) |
| **DuckDuckGo** | بحث ويب مجاني (بديل) | غير مطلوب |
| **Udemy** | روابط بحث ذكية (بدون API) | غير مطلوب |
| **Coursera** | روابط بحث ذكية (بدون API) | غير مطلوب |
| **edX** | روابط بحث ذكية (بدون API) | غير مطلوب |

> **مهم**: تحليل السيرة الذاتية يعمل بالكامل محلياً بدون أي API خارجي. Gemini يُستخدم فقط للمحادثة.

---

## متغيرات البيئة

```env
# --- قاعدة البيانات ---
DATABASE_URL=sqlite:///./viora.db
# PostgreSQL: postgresql://user:pass@localhost:5432/viora_db

# --- الأمان ---
SECRET_KEY=change-this-to-a-random-32-char-string

# --- الذكاء الاصطناعي ---
GEMINI_API_KEY=                 # مطلوب للمحادثة
YOUTUBE_API_KEY=                # اختياري — لفيديوهات خارطة التعلم

# --- SMTP (اختياري — لإعادة تعيين كلمة المرور) ---
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your@gmail.com
SMTP_PASSWORD=app-password
SMTP_FROM_EMAIL=noreply@viora.app

# --- إعدادات تقنية ---
LOG_LEVEL=INFO                  # DEBUG, INFO, WARNING, ERROR
CORS_ORIGINS=                   # قائمة أصول مفصولة بفاصلة
NER_CONFIDENCE_THRESHOLD=0.50   # عتبة ثقة NER (0.0-1.0)
```

---

## الاختبارات

```bash
# تشغيل جميع الاختبارات
pytest test/ -v

# اختبار محدد
pytest test/test_full_pipeline.py -v
pytest test/test_onet_service.py -v
pytest test/test_chat.py -v
pytest test/test_quota.py -v
```

| ملف الاختبار | الوصف |
|---|---|
| `test_full_pipeline.py` | اختبار شامل لخط الأنابيب الكامل (رفع → تحليل → فجوات → خارطة) |
| `test_onet_service.py` | اختبار مطابقة المهن + تحليل الفجوات |
| `test_chat.py` | اختبار المساعد الذكي |
| `test_quota.py` | اختبار إدارة استنفاد حصص APIs |

---

## ملاحظات تقنية

### أنماط التصميم المُستخدمة
- **Singleton Pattern**: جميع الخدمات الثقيلة (NER, O\*NET, ESCO, LLM) تُحمَّل مرة واحدة
- **Lazy Initialization**: النماذج تُحمَّل عند أول استخدام (مع `warmup()` اختياري)
- **Dependency Injection**: عبر `Depends()` في FastAPI
- **Service Layer**: منطق الأعمال مفصول عن الـ Controllers (thin controllers)
- **Single Responsibility**: كل ملف مسؤول عن وظيفة واحدة

### أداء التحليل
- **Viora NER ONNX INT8**: 119MB بدلاً من 1.76GB (GLiNER)، أقل من 100ms استنتاج
- **O\*NET Taxonomy**: أقل من 50ms، حتمي 100%، بدون إنترنت
- **إجمالي التحليل**: أقل من 200ms (مقارنة بـ 5-10 ثوانٍ مع Gemini)
- **Semantic Matching**: all-MiniLM-L6-v2 (22M معامل، 80MB)، embeddings مخزنة على القرص

### الأمان
- **bcrypt**: تشفير كلمات المرور (يقطع على 72 بايت)
- **JWT مزدوج**: access + refresh tokens مع فحص النوع
- **itsdangerous**: رموز إعادة تعيين كلمة المرور محدودة الوقت
- **SECRET_KEY Guard**: يمنع التشغيل في الإنتاج بالمفتاح الافتراضي
- **Anti-Enumeration**: نقطة forgot-password تُرجع نجاح دائماً
- **IDOR Prevention**: جميع نقاط النهاية تُصفّي بـ `user_id`

### دورة حياة البيانات
- **Soft Delete**: التحليلات وخرائط التعلم تُؤرشف (لا تُحذف) عند إعادة التحليل
- **File Cleanup**: ملفات CV تُحذف بعد التحليل الناجح
- **Chat Preservation**: سجل المحادثات يُحفظ عبر إعادة التحليلات

### المكتبات الرئيسية

| المكتبة | الإصدار | الاستخدام |
|---|---|---|
| FastAPI | 0.135.1 | إطار عمل الويب |
| SQLAlchemy | 2.0.48 | ORM + قاعدة البيانات |
| Pydantic | 2.12.5 | تحقق البيانات + الإعدادات |
| bcrypt | 5.0.0 | تشفير كلمات المرور |
| python-jose | 3.5.0 | JWT tokens |
| PyMuPDF | 1.27.2 | استخراج نص PDF |
| python-docx | 1.2.0 | استخراج نص DOCX |
| transformers | 4.57.6 | tokenizer لنموذج NER |
| onnxruntime | 1.24.3 | استنتاج ONNX |
| sentence-transformers | 5.3.0 | semantic matching |
| RapidFuzz | 3.14.3 | fuzzy string matching |
| google-genai | 1.66.0 | Gemini API (محادثة) |
| requests | 2.32.5 | HTTP client |
| itsdangerous | 2.2.0 | رموز آمنة |
| duckduckgo-search | 8.1.1 | بحث ويب مجاني |
| uvicorn | 0.41.0 | ASGI server |

</div>
