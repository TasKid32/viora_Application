<div dir="rtl">

> 🌐 [English Version (README_EN.md)](README_EN.md)

# 🎯 Viora — نظام تطوير المسار المهني بالذكاء الاصطناعي

> منصة ذكية لتحليل السيرة الذاتية محلياً باستخدام نموذج Viora NER (ONNX) (RoBERTa)، تحليل فجوات المهارات عبر تصنيف O\*NET المهني، بناء خارطة طريق تعليمية مخصصة، ومساعد ذكي للإرشاد المهني مدعوم بـ Gemini.

---

## 📋 فهرس المحتويات

- [المميزات](#-المميزات)
- [التقنيات المستخدمة](#-التقنيات-المستخدمة)
- [بنية المشروع](#-بنية-المشروع)
- [المتطلبات الأساسية](#-المتطلبات-الأساسية)
- [إعداد المشروع خطوة بخطوة](#-إعداد-المشروع-خطوة-بخطوة)
- [ربط التطبيق بالباك اند](#-ربط-التطبيق-بالباك-اند-نفس-الشبكة)
- [المتغيرات البيئية](#-المتغيرات-البيئية)
- [نقاط الـ API](#-نقاط-الـ-api)
- [هيكل المشروع التفصيلي](#-هيكل-المشروع-التفصيلي)
- [خط أنابيب التحليل](#-خط-أنابيب-التحليل)
- [الرخصة](#-الرخصة)

---

## ✨ المميزات

| الميزة | الوصف |
|--------|-------|
| 📄 **تحليل السيرة الذاتية** | ارفع سيرتك (PDF/DOCX) — تحليل محلي بالكامل بدون APIs خارجية (إنجليزي فقط) |
| 🎯 **تحليل فجوة المهارات** | يحدد مهاراتك القوية والناقصة (صلبة + ناعمة + تقنية) والوظيفة المتوقعة ومستوى الخبرة عبر تصنيف O\*NET |
| 🗺️ **خارطة طريق تعليمية** | مسار تعلم مخصص متعدد المراحل مع دورات من YouTube و Udemy و Coursera و edX |
| 💬 **مساعد مهني ذكي** | محادثة ذكية مدعومة بـ Gemini 2.5 Flash تفهم سياق مهاراتك وأهدافك |
| 📊 **تتبع التقدم** | لوحة معلومات مع النشاط الأسبوعي والدورات المكتملة ونسبة التقدم |
| 📚 **إدارة الدورات** | تسجيل وتتبع الدورات (CRUD كامل) |
| 🔔 **الإشعارات** | تنبيهات النشاط مع إمكانية القراءة والحذف |
| 🌐 **دعم اللغتين** | ترجمة كاملة (عربي/إنجليزي) مع دعم RTL |
| 🔒 **أمان متقدم** | JWT مزدوج (access + refresh) + bcrypt + إعادة تعيين كلمة المرور بالبريد |

---

## 🛠️ التقنيات المستخدمة

| الطبقة | التقنية |
|--------|---------|
| **الباك اند** | Python 3.11.9 · FastAPI 0.135 · SQLAlchemy 2.0 · Pydantic V2 · Uvicorn |
| **الذكاء الاصطناعي (CV)** | Viora NER (RoBERTa ONNX INT8 — 119MB) · O\*NET Taxonomy · ESCO v1.2.1 |
| **الذكاء الاصطناعي (Chat)** | Google Gemini 2.5 Flash (للمحادثة فقط) |
| **مطابقة المهن** | Semantic Matching (all-MiniLM-L6-v2) · RapidFuzz · Alias Database |
| **تطبيق الموبايل** | Flutter 3.x (Dart SDK ^3.6.0) · Provider · Dio · GoRouter |
| **قاعدة البيانات** | SQLite (تطوير) · PostgreSQL (إنتاج) |
| **الترجمة** | Flutter l10n (ARB — عربي + إنجليزي) |

---

## 🏗️ بنية المشروع

يتكون المشروع من **3 مكونات رئيسية**:

```
viora_app/
├── backend/        ← الخادم الخلفي (FastAPI + Python)
├── mobile/         ← تطبيق الموبايل (Flutter + Dart)
├── ml/             ← نماذج تعلم الآلة وبيانات التصنيف
│   └── viora-ner/  ← نموذج NER المخصص للسير الذاتية
├── README.md       ← هذا الملف
└── .gitignore
```

| المكون | الوصف | التوثيق التفصيلي |
|--------|-------|------------------|
| **Backend** | واجهة برمجة RESTful — 9 مجموعات API، 19 خدمة، 7 جداول | [`backend/README.md`](backend/README.md) |
| **ML / Viora NER** | نموذج NER مدرّب على بيانات السير الذاتية | [`ml/viora-ner/README.md`](ml/viora-ner/README.md) |
| **Taxonomy** | بيانات O\*NET (1016 وظيفة) + ESCO (85K مهارة) | [`ml/viora-ner/data/taxonomy/README.md`](ml/viora-ner/data/taxonomy/README.md) |
| **Mobile** | تطبيق Flutter بـ 8 وحدات feature-based | — |

---

## 📦 المتطلبات الأساسية

| الأداة | الإصدار | التحميل |
|--------|---------|---------|
| **Python** | 3.11.9 | [python.org](https://www.python.org/downloads/) |
| **Flutter** | 3.x (stable) · Dart SDK ^3.6.0 | [flutter.dev](https://docs.flutter.dev/get-started/install) |
| **Git** | أي إصدار حديث | [git-scm.com](https://git-scm.com/downloads) |
| **Android Studio** أو **VS Code** | أحدث إصدار | لتطوير Flutter ومحاكي Android |

**مفاتيح API المطلوبة:**
- **مفتاح Google Gemini API** *(مطلوب)* — احصل عليه مجاناً من [Google AI Studio](https://aistudio.google.com/apikey)
- **مفتاح YouTube Data API** *(اختياري)* — لفيديوهات خارطة التعلم من [Google Cloud Console](https://console.cloud.google.com/)

> ⚠️ **ملاحظة**: تحليل السيرة الذاتية يعمل **بالكامل محلياً** بدون أي مفتاح API — نموذج Viora NER ONNX + بيانات O\*NET مُضمّنة في المشروع.

---

## 🚀 إعداد المشروع خطوة بخطوة

### 1. استنساخ المشروع

</div>

```bash
git clone https://github.com/salman11169/Viora_app.git
cd Viora_app
```

---

<div dir="rtl">

### 2. إعداد الباك اند (تريمنال 1)

افتح تريمنال ونفّذ الأوامر التالية:

</div>

```bash
# انتقل إلى مجلد الباك اند
cd backend

# أنشئ بيئة افتراضية Python
python -m venv venv

# فعّل البيئة الافتراضية
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Windows (CMD):
venv\Scripts\activate.bat
# macOS / Linux:
source venv/bin/activate

# ثبّت المكتبات المطلوبة
pip install -r requirements.txt
```

<div dir="rtl">

### 3. تحميل بيانات ML (النماذج والداتاست)

> ⚠️ **هذه الخطوة مطلوبة!** بيانات النماذج والداتاست كبيرة الحجم (~1.6 GB) ولا تُرفع على GitHub. يجب تحميلها بشكل منفصل.

#### الطريقة 1: عبر السكريبت (موصى بها)

ارجع إلى مجلد المشروع الرئيسي وشغّل السكريبت:

</div>

```bash
cd ..
python setup_ml_data.py
```

<div dir="rtl">

السكريبت سيقوم تلقائياً بتحميل الملف المضغوط من Google Drive، فك الضغط، ووضع جميع الملفات في أماكنها الصحيحة.

#### الطريقة 2: تحميل يدوي من Google Drive

1. حمّل ملف `viora_ml_data.zip` من الرابط التالي:
   **[📥 تحميل بيانات ML من Google Drive](https://drive.google.com/file/d/1TA8BA82QIFu5vTQqhH1iUAUKe_ROpgap/view?usp=sharing)**
2. ضع الملف المضغوط في **المجلد الرئيسي للمشروع** (`viora_app/`)
3. فك الضغط:

</div>

```bash
# Windows (PowerShell):
Expand-Archive -Path viora_ml_data.zip -DestinationPath . -Force

# macOS / Linux:
unzip viora_ml_data.zip -d .
```

<div dir="rtl">

4. تأكد من وجود هذه المجلدات بعد فك الضغط:
   - `ml/viora-ner/models/checkpoints/best_model/`
   - `ml/viora-ner/models/exported/onnx/`
   - `ml/viora-ner/models/exported/onnx_quantized/`
   - `ml/viora-ner/data/processed/`
   - `ml/viora-ner/data/raw/`

> 📦 **محتويات الأرشيف:**
> | المجلد | الحجم | الوصف |
> |--------|-------|-------|
> | `ml/viora-ner/models/` | ~1.1 GB | نماذج NER المدرّبة (safetensors + ONNX + quantized) |
> | `ml/viora-ner/data/processed/` | ~467 MB | بيانات التدريب المُعالجة |
> | `ml/viora-ner/data/raw/` | ~101 MB | الداتاست الخام (Kaggle NER + HF Resumes) |
> | `ml/viora-ner/data/cache/` | ~1 MB | ملفات embeddings مُخزنة |

ارجع إلى مجلد الباك اند لإكمال الإعداد:

</div>

```bash
cd backend
```

<div dir="rtl">

---

### 4. إعداد المتغيرات البيئية والتشغيل

**إعداد المتغيرات البيئية:**

</div>

```bash
# انسخ ملف البيئة النموذجي
# Windows:
copy .env.example .env
# macOS / Linux:
cp .env.example .env
```

<div dir="rtl">

**عدّل ملف `.env`** وأضف مفاتيح الـ API:

</div>

```env
# مطلوب — احصل عليه من https://aistudio.google.com/apikey
GEMINI_API_KEY=ضع-مفتاح-gemini-هنا

#  لفيديوهات خارطة التعلم
YOUTUBE_API_KEY=ضع-مفتاح-youtube-هنا

# أمان — غيّر هذا في الإنتاج! (النظام يرفض التشغيل بالقيمة الافتراضية)
SECRET_KEY=غيّر-هذا-إلى-نص-عشوائي-طويل
```

<div dir="rtl">

**شغّل سيرفر الباك اند:**

</div>

```bash
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

<div dir="rtl">

> ⚠️ **مهم:** استخدم `--host 0.0.0.0` (وليس `localhost`) حتى يكون السيرفر متاحاً من الأجهزة الأخرى على شبكتك.

> ℹ️ **عند أول تشغيل:** النظام يُحمّل نموذج Viora NER ONNX (~119MB) وبيانات O\*NET (~1016 وظيفة) تلقائياً. قد يستغرق الأمر ~10 ثوانٍ.

✅ الباك اند يعمل الآن! تحقق من:
- **جذر الـ API:** http://localhost:8000
- **توثيق Swagger:** http://localhost:8000/docs
- **فحص الصحة:** http://localhost:8000/health

---

### 5. إعداد وتشغيل تطبيق الموبايل (تريمنال 2)

افتح **تريمنال جديد/منفصل** ونفّذ:

</div>

```bash
# انتقل إلى مجلد التطبيق
cd mobile

# ثبّت مكتبات Flutter
flutter pub get

# ولّد ملفات الترجمة
flutter gen-l10n
```

<div dir="rtl">

**⚡ قبل التشغيل، اضبط عنوان الـ API** (انظر القسم التالي):

</div>

```bash
# شغّل مع عنوان IP جهازك (استبدل بعنوان IP الخاص بك)
flutter run --dart-define=API_URL=http://192.168.1.100:8000
```

<div dir="rtl">

أو شغّل مباشرة (العنوان الافتراضي `10.0.2.2:8000` لمحاكي Android):

</div>

```bash
flutter run
```

---

<div dir="rtl">

## 🌐 ربط التطبيق بالباك اند (نفس الشبكة)

لكي يتواصل التطبيق مع الباك اند، **يجب أن يكون الجهازان على نفس شبكة الـ Wi-Fi**.

### الخطوة 1: اعرف عنوان IP جهاز الكمبيوتر

</div>

```bash
# Windows:
ipconfig
# ابحث عن "IPv4 Address" تحت محول Wi-Fi (مثال: 192.168.1.100)

# macOS / Linux:
ifconfig | grep "inet "
```

<div dir="rtl">

### الخطوة 2: اضبط عنوان الـ API في Flutter

هناك **3 طرق** لضبط عنوان الـ API:

#### الطريقة 1: عند البناء (مُوصى بها للتطوير)

</div>

```bash
flutter run --dart-define=API_URL=http://عنوان_IP:8000
# مثال:
flutter run --dart-define=API_URL=http://192.168.1.100:8000
```

<div dir="rtl">

#### الطريقة 2: تعديل الكود المصدري

افتح ملف `mobile/lib/core/config/environment.dart` وغيّر القيمة الافتراضية:

</div>

```dart
static const String _buildTimeApiUrl = String.fromEnvironment(
  'API_URL',
  defaultValue: 'http://عنوان_IP:8000',  // ← غيّر هذا
);
```

<div dir="rtl">

#### الطريقة 3: محاكي Android

إذا تستخدم محاكي Android Studio، استخدم العنوان الخاص `10.0.2.2` (يُحوّل إلى `localhost` الخاص بالكمبيوتر):

</div>

```bash
flutter run --dart-define=API_URL=http://10.0.2.2:8000
```

<div dir="rtl">

### ⚠️ مشاكل الاتصال الشائعة

| المشكلة | الحل |
|---------|------|
| التطبيق لا يتصل بالباك اند | تأكد أن الجهازين على **نفس شبكة Wi-Fi** |
| رفض الاتصال (Connection refused) | تأكد أن الباك اند يعمل بـ `--host 0.0.0.0` (وليس `127.0.0.1`) |
| انتهاء المهلة (Timeout) | تحقق من جدار الحماية — اسمح بالمنفذ `8000` |
| تستخدم محاكي Android | استخدم `http://10.0.2.2:8000` بدلاً من `localhost` |
| تغيّر عنوان IP | شغّل `ipconfig` مجدداً وحدّث عنوان الـ API |

---

## 🔧 المتغيرات البيئية

### الباك اند (`backend/.env`)

| المتغير | مطلوب | الوصف |
|---------|-------|-------|
| `DATABASE_URL` | ✅ | رابط قاعدة البيانات. الافتراضي: `sqlite:///./viora.db` |
| `SECRET_KEY` | ✅ | مفتاح توقيع JWT. **النظام يرفض التشغيل بالقيمة الافتراضية** |
| `GEMINI_API_KEY` | ✅ | مفتاح Gemini — للمحادثة الذكية فقط (ليس لتحليل CV) |
| `YOUTUBE_API_KEY` | ❌ | مفتاح YouTube Data v3 — لفيديوهات خارطة التعلم |
| `SMTP_HOST` / `SMTP_USERNAME` / `SMTP_PASSWORD` | ❌ | SMTP لإرسال بريد إعادة تعيين كلمة المرور |
| `NER_CONFIDENCE_THRESHOLD` | ❌ | عتبة ثقة NER. الافتراضي: `0.50` |
| `CORS_ORIGINS` | ❌ | النطاقات المسموحة مفصولة بفواصل |
| `LOG_LEVEL` | ❌ | مستوى التسجيل. الافتراضي: `INFO` |

### تطبيق الموبايل (`mobile/lib/core/config/environment.dart`)

| الإعداد | القيمة الافتراضية | التغيير |
|---------|-----------------|---------|
| عنوان API | `http://10.0.2.2:8000` | `--dart-define=API_URL=...` |
| مهلة الاتصال | 15 ثانية | `Environment.connectTimeout` |
| مهلة الاستقبال | 30 ثانية | `Environment.receiveTimeout` |
| مهلة الرفع | 60 ثانية | `Environment.uploadTimeout` |
| حد حجم الملف | 10 MB | `Environment.maxFileSizeMB` |

---

## 📝 نقاط الـ API

### المصادقة
| المسار | الطريقة | الوصف |
|--------|---------|-------|
| `/api/auth/register` | POST | تسجيل مستخدم جديد (يرجع access + refresh tokens) |
| `/api/auth/login` | POST | تسجيل الدخول |
| `/api/auth/refresh` | POST | تجديد access token من refresh token |
| `/api/auth/forgot-password` | POST | طلب إعادة تعيين كلمة المرور بالبريد |
| `/api/auth/reset-password` | POST | إعادة تعيين كلمة المرور بالرمز |

### تحليل السيرة الذاتية
| المسار | الطريقة | الوصف |
|--------|---------|-------|
| `/api/resume/upload` | POST | رفع CV (PDF/DOCX — حد 10MB، إنجليزي فقط) |
| `/api/resume/analyze` | POST | تحليل هجين (Viora NER + O\*NET) |
| `/api/resume/analyze/stream` | POST | تحليل بث SSE (أحداث مرحلية) |

### خارطة التعلم
| المسار | الطريقة | الوصف |
|--------|---------|-------|
| `/api/roadmap` | GET | جلب خارطة التعلم |
| `/api/roadmap/generate` | POST | توليد خارطة تعلم من نتائج التحليل |
| `/api/roadmap/steps/{id}/complete` | PUT | تعليم مرحلة كمكتملة |
| `/api/roadmap/steps/{id}/incomplete` | PUT | إلغاء اكتمال مرحلة |
| `/api/roadmap/steps/{id}/resources/{res_id}/toggle` | PUT | تبديل إكمال مورد تعليمي |

### المساعد الذكي والدورات ولوحة المعلومات
| المسار | الطريقة | الوصف |
|--------|---------|-------|
| `/api/chat/send` | POST | إرسال رسالة للمساعد الذكي (Gemini) |
| `/api/chat/history` | GET | سجل آخر 50 محادثة |
| `/api/chat/history` | DELETE | حذف سجل المحادثات |
| `/api/dashboard` | GET | بيانات لوحة المعلومات (نسبة تقدم مرجّحة + تتبع موارد) |
| `/api/courses` | GET/POST | عرض أو إنشاء دورات |
| `/api/courses/{id}` | GET/PUT/DELETE | عمليات CRUD على الدورات |
| `/api/progress/weekly` | GET | إحصائيات النشاط الأسبوعي الحقيقي |

### الملف الشخصي والإشعارات
| المسار | الطريقة | الوصف |
|--------|---------|-------|
| `/api/profile` | GET/PUT | عرض/تعديل الملف الشخصي |
| `/api/profile/avatar` | POST | رفع صورة شخصية (JPEG/PNG/WebP) |
| `/api/profile/settings/language` | PUT | تغيير لغة الواجهة |
| `/api/notifications` | GET | جميع الإشعارات |
| `/api/notifications/{id}/read` | PUT | تعليم إشعار كمقروء |
| `/api/notifications/read-all` | PUT | تعليم الجميع كمقروءة |
| `/api/notifications/{id}` | DELETE | حذف إشعار |

> 📖 توثيق تفاعلي كامل للـ API متاح على `http://localhost:8000/docs` عند تشغيل الباك اند.

---

## 📁 هيكل المشروع التفصيلي

</div>

```
viora_app/
├── backend/                           # ═══ الخادم الخلفي (FastAPI) ═══
│   ├── main.py                        # نقطة الدخول — FastAPI + Lifespan + CORS
│   ├── requirements.txt               # متطلبات Python 3.11.9
│   ├── .env.example                   # قالب المتغيرات البيئية
│   ├── app/
│   │   ├── core/                      # ── الإعدادات والأمان ──
│   │   │   ├── config.py              #   Pydantic Settings + حماية SECRET_KEY
│   │   │   ├── security.py            #   bcrypt + JWT مزدوج + Password Reset
│   │   │   ├── dependencies.py        #   Dependency Injection (get_current_user)
│   │   │   ├── logging.py             #   تسجيل مُهيكل
│   │   │   └── quota_handler.py       #   معالجة استنفاد حصص APIs
│   │   │
│   │   ├── db/                        # ── قاعدة البيانات ──
│   │   │   ├── database.py            #   SQLAlchemy Engine (SQLite/PostgreSQL)
│   │   │   ├── models.py             #   7 جداول ORM (UUID4 + UTC timestamps)
│   │   │   └── init_db.py            #   تهيئة + فحص الجداول
│   │   │
│   │   ├── api/v1/                    # ── نقاط النهاية (9 ملفات) ──
│   │   │   ├── auth.py               #   تسجيل/دخول/refresh/forgot-password
│   │   │   ├── resume.py             #   رفع + تحليل CV (SSE streaming)
│   │   │   ├── roadmap.py            #   خارطة تعلم + تتبع الإكمال
│   │   │   ├── chat.py               #   مساعد ذكي (Gemini)
│   │   │   ├── dashboard.py          #   لوحة معلومات (تقدم مرجّح)
│   │   │   ├── courses.py            #   CRUD كامل للدورات
│   │   │   ├── notifications.py      #   إشعارات
│   │   │   ├── profile.py            #   ملف شخصي + رفع صور
│   │   │   └── progress.py           #   نشاط أسبوعي حقيقي
│   │   │
│   │   ├── schemas/                   # ── نماذج Pydantic (7 ملفات) ──
│   │   │
│   │   └── services/                  # ── طبقة الأعمال (19 خدمة) ──
│   │       ├── hybrid_analysis_service.py  # دمج NER + O*NET (الخط الهجين)
│   │       ├── viora_ner_service.py        # استخراج كيانات ONNX
│   │       ├── onet_service.py             # مطابقة مهن + فجوات (710 سطر)
│   │       ├── onet_data_loader.py         # تحميل 5 ملفات TSV + 60+ alias
│   │       ├── onet_roadmap.py             # توليد خارطة تعلم
│   │       ├── esco_resolver.py            # ESCO v1.2.1 (85K مهارة)
│   │       ├── cv_parsers.py              # مهارات ناعمة + خبرة + تخرج
│   │       ├── cv_quality.py              # تقييم جودة CV (0-100)
│   │       ├── text_extractor.py          # استخراج نص PDF/DOCX
│   │       ├── file_upload.py             # حفظ ملفات
│   │       ├── llm_service.py             # Gemini 2.5 Flash (محادثة فقط)
│   │       ├── email_service.py           # SMTP لإعادة التعيين
│   │       ├── auth_service.py            # منطق التسجيل/الدخول
│   │       ├── youtube_service.py         # YouTube Data API v3
│   │       ├── udemy_service.py           # روابط Udemy ذكية
│   │       ├── coursera_service.py        # روابط Coursera ذكية
│   │       ├── edx_service.py             # روابط edX ذكية
│   │       ├── course_search_service.py   # بحث Google Custom Search عن دورات
│   │       └── web_search_service.py      # Google/Bing/DuckDuckGo
│   │
│   └── test/                          # ── اختبارات ──
│       ├── test_full_pipeline.py      #   اختبار خط الأنابيب الكامل
│       ├── test_onet_service.py       #   اختبار O*NET
│       ├── test_chat.py               #   اختبار المحادثة
│       └── test_quota.py              #   اختبار الحصص
│
├── mobile/                            # ═══ تطبيق Flutter ═══
│   ├── pubspec.yaml                   # المتطلبات (Dart SDK ^3.6.0)
│   ├── l10n.yaml                      # إعدادات الترجمة
│   ├── assets/                        # أيقونة + شعار التطبيق
│   └── lib/
│       ├── main.dart                  # نقطة الدخول + AppLoader + MultiProvider
│       │
│       ├── core/                      # ── البنية التحتية (14 ملف) ──
│       │   ├── config/
│       │   │   └── environment.dart   #   إعدادات API URL + timeouts
│       │   ├── api/
│       │   │   ├── api_client.dart    #   Dio + auto token refresh (Completer)
│       │   │   ├── api_endpoints.dart #   ثوابت مسارات API
│       │   │   ├── retry_interceptor.dart   # exponential backoff (1→2→4s)
│       │   │   └── quota_interceptor.dart   # 403/429 handling
│       │   ├── auth/
│       │   │   └── token_manager.dart #   JWT + SecureStorage + RAM cache
│       │   ├── cache/
│       │   │   └── local_cache.dart   #   SharedPreferences + TTL (30 دقيقة)
│       │   ├── routing/
│       │   │   └── app_router.dart    #   GoRouter + ShellRoute + auth redirect
│       │   ├── theme/
│       │   │   ├── app_colors.dart    #   نظام ألوان Viora (بنفسجي/وردي)
│       │   │   ├── app_theme.dart     #   ThemeData
│       │   │   └── app_styles.dart    #   أنماط نصية
│       │   ├── l10n/
│       │   │   └── locale_provider.dart  # تبديل EN↔AR مع حفظ
│       │   └── utils/
│       │       ├── logger.dart        #   نظام تسجيل
│       │       └── error_helper.dart  #   معالجة أخطاء Dio
│       │
│       ├── features/                  # ── الوحدات (8 وحدات، 30 ملف) ──
│       │   ├── auth/                  #   تسجيل + دخول + نسيان كلمة المرور
│       │   │   ├── data/             #     auth_api.dart, auth_models.dart
│       │   │   ├── provider/         #     auth_provider.dart
│       │   │   ├── screens/          #     login, register, forgot_password
│       │   │   └── widgets/          #     auth_text_field.dart
│       │   ├── analysis/              #   رفع CV + عرض نتائج التحليل
│       │   │   ├── data/             #     analysis_api.dart, analysis_models.dart
│       │   │   ├── provider/         #     analysis_provider.dart
│       │   │   ├── screens/          #     analysis_screen.dart
│       │   │   └── widgets/          #     upload_section, results_section, loading
│       │   ├── dashboard/             #   لوحة المعلومات
│       │   ├── roadmap/               #   خارطة التعلم
│       │   ├── chat/                  #   المساعد الذكي
│       │   ├── profile/               #   الملف الشخصي
│       │   ├── notifications/         #   الإشعارات
│       │   └── progress/              #   تتبع التقدم
│       │
│       ├── l10n/                      # ── ملفات الترجمة ──
│       │   ├── app_en.arb            #   نصوص إنجليزية
│       │   └── app_ar.arb            #   نصوص عربية
│       │
│       └── shared/                    # ── مكونات مشتركة ──
│           ├── widgets/              #   مكونات واجهة قابلة لإعادة الاستخدام
│           └── utils/                #   أدوات مساعدة مشتركة
│
└── ml/                                # ═══ تعلم الآلة ═══
    └── viora-ner/                     # نموذج NER المدرّب على السير الذاتية
        ├── README.md                  # توثيق تفصيلي بالعربي
        ├── requirements.txt           # متطلبات التدريب
        ├── src/                       # ── كود المصدر (10 ملفات) ──
        │   ├── inference.py          #   استنتاج ONNX (يستورده Backend)
        │   ├── trainer_module.py     #   حلقة التدريب
        │   ├── data_module.py        #   معالجة البيانات + sliding window
        │   ├── export_onnx.py        #   تصدير + تكميم INT8
        │   ├── config.py             #   إعدادات YAML
        │   ├── gazetteer.py          #   قوائم مهارات
        │   ├── labels.py             #   8 تصنيفات NER
        │   ├── metrics.py            #   تقييم seqeval
        │   └── callbacks.py          #   callbacks تدريب
        │
        ├── models/                    # ── النماذج ──
        │   └── exported/
        │       └── onnx_quantized/   #   ONNX INT8 (119MB) ← يستخدمه Backend
        │
        ├── data/
        │   ├── taxonomy/              # ── بيانات التصنيف ──
        │   │   ├── onet/             #   O*NET (1016 وظيفة × 5 ملفات TSV)
        │   │   └── esco/             #   ESCO v1.2.1 (13,939 مهارة)
        │   ├── gazetteers/           #   قوائم مهارات للتدريب
        │   ├── processed/            #   بيانات مُعالجة
        │   ├── raw/                  #   بيانات خام
        │   └── cache/                #   embeddings مُخزنة
        │
        ├── configs/                   # إعدادات التدريب YAML
        ├── scripts/                   # سكربتات مساعدة
        ├── notebooks/                 # Jupyter notebooks
        └── tests/                     # اختبارات ML
```

---

<div dir="rtl">

## 🔄 خط أنابيب التحليل

```
┌─────────────────────────────────────────────────────────────┐
│              خط أنابيب تحليل السيرة الذاتية                   │
│          (محلي بالكامل — بدون APIs خارجية — <200ms)           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  📤 رفع CV (PDF/DOCX)                                       │
│    └─→ text_extractor.py (PyMuPDF / python-docx)            │
│                                                             │
│  📋 تقييم جودة CV (0-100 نقطة)                              │
│    └─→ cv_quality.py                                        │
│        يرفض الأقل من 30 نقطة                                │
│                                                             │
│  🧠 Viora NER (ONNX INT8 — 119MB) — <100ms                 │
│    └─→ viora_ner_service.py                                 │
│        8 كيانات: PERSON, SKILL, JOB_TITLE, ORG,            │
│        LOCATION, CONTACT, CREDENTIAL, EXPERIENCE            │
│    └─→ cv_parsers.py                                        │
│        مهارات ناعمة (~50 ESCO) + سنوات خبرة + تخرج          │
│                                                             │
│  🎯 O*NET + ESCO — <50ms                                    │
│    └─→ onet_service.py                                      │
│        مطابقة المهنة: exact → alias → semantic → fuzzy       │
│        تحليل فجوات: skills + tech_skills + knowledge        │
│    └─→ esco_resolver.py                                     │
│        تصنيف مهارات ناعمة (96 transversal skill)             │
│                                                             │
│  🔗 دمج النتائج                                              │
│    └─→ hybrid_analysis_service.py                           │
│        مهارات قوية + ناقصة + فرص عمل + توصيات               │
│                                                             │
│  📊 إجمالي: <200ms (مقارنة بـ 5-10 ثوانٍ مع Gemini)         │
└─────────────────────────────────────────────────────────────┘
```

---

## 📄 الرخصة

MIT License

---

**الإصدار:** 1.0.0 · **الحالة:** 🚧 تطوير نشط · **آخر تحديث:** أبريل 2026

</div>
