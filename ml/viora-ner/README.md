# Viora NER

نظام التعرف على الكيانات المسمّاة (Named Entity Recognition) لتحليل السير الذاتية واستخراج المعلومات المهيكلة منها.

يقوم النظام بضبط نموذج `roberta-base` على بيانات سير ذاتية إنجليزية مشروحة، لاكتشاف 8 أنواع من الكيانات باستخدام مخطط BIO (Begin-Inside-Outside).

---

## أنواع الكيانات (8 أنواع)

| النوع | الوصف | مثال |
|---|---|---|
| `SKILL` | المهارات التقنية والشخصية | Python, Machine Learning, Leadership |
| `CREDENTIAL` | الشهادات والدرجات العلمية | B.Sc. Computer Science, PMP |
| `ORG` | المنشآت: شركات، جامعات، منظمات | Google, MIT, WHO |
| `PERSON` | أسماء الأشخاص | John Smith |
| `LOCATION` | المواقع الجغرافية: مدن، دول | New York, Germany |
| `CONTACT` | معلومات الاتصال: بريد، هاتف، روابط | john@email.com, +1-555-0123 |
| `JOB_TITLE` | المسميات الوظيفية | Software Engineer, Data Analyst |
| `EXPERIENCE` | التواريخ ومدد الخبرة | 2019-2023, 5 years |

كل نوع ينتج تسميتَيْ BIO (`B-SKILL`, `I-SKILL`...) بالإضافة إلى التسمية `O` (خارج أي كيان) = **17 تسمية إجمالاً**.

يتم تعريف هذه التسميات في `src/labels.py`، حيث يُولَّد قاموسا التحويل `LABEL2ID` و `ID2LABEL` تلقائياً. يُستخدم الفهرس `-100` (`IGNORE_INDEX`) لتجاهل الـ subword tokens والرموز الخاصة أثناء حساب الخسارة.

---

## هيكل المشروع

```
viora-ner/
├── configs/
│   └── train.yaml                  # إعدادات التدريب الكاملة
├── src/                            # الوحدات الأساسية (9 ملفات)
│   ├── labels.py                   # تعريف 8 أنواع كيانات → 17 تسمية BIO
│   ├── config.py                   # تحميل الإعدادات من YAML مع دعم تجاوز CLI
│   ├── data_module.py              # تحميل JSONL + تقطيع + توكنة + نافذة منزلقة
│   ├── gazetteer.py                # قاموس المهارات والمسميات الوظيفية (Trie)
│   ├── metrics.py                  # حساب F1/Precision/Recall عبر seqeval
│   ├── callbacks.py                # NaNStopCallback لإيقاف التدريب عند NaN
│   ├── trainer_module.py           # WeightedNERTrainer + بناء المدرّب
│   ├── export_onnx.py              # تصدير إلى ONNX مع تكميم INT8
│   └── inference.py                # خط أنابيب الاستدلال الإنتاجي
├── scripts/                        # أدوات مساعدة (10 ملفات)
│   ├── train.py                    # نقطة بدء التدريب
│   ├── evaluate.py                 # تقييم النموذج وطباعة تقرير التصنيف
│   ├── annotate.py                 # توسيم البيانات عبر Groq API (LLM)
│   ├── augment_data.py             # تعزيز البيانات (استبدال كيانات + قوالب)
│   ├── build_gazetteer.py          # بناء قواميس المهارات من O*NET + ESCO
│   ├── fix_annotations.py          # إصلاح أخطاء التوسيم تلقائياً (6 خطوات)
│   ├── audit_annotations.py        # تدقيق جودة التوسيم (5 أنماط أخطاء)
│   ├── split.py                    # تقسيم طبقي حسب الكيانات
│   ├── extract_texts.py            # استخراج نصوص من PDF/DOCX
│   └── pack_colab.py               # تجهيز أرشيف ZIP للتدريب على Colab
├── tests/                          # اختبارات (4 ملفات)
│   ├── test_labels.py              # التحقق من تعريفات التسميات
│   ├── test_data_quality.py        # فحص جودة البيانات المعالجة
│   ├── test_pipeline.py            # اختبار إعدادات خط أنابيب التدريب
│   └── test_cv.py                  # اختبار الاستدلال على سير ذاتية حقيقية
├── notebooks/
│   └── train.ipynb                 # دفتر Google Colab (8 خلايا)
├── data/
│   ├── processed/                  # البيانات الجاهزة للتدريب (JSONL)
│   ├── raw/                        # البيانات الخام (Kaggle + HuggingFace)
│   ├── gazetteers/                 # قواميس JSON (مهارات + مسميات وظيفية)
│   └── taxonomy/                   # تصنيفات O*NET و ESCO
├── models/
│   ├── checkpoints/best_model/     # أفضل نموذج مدرّب (safetensors)
│   └── exported/                   # نماذج ONNX (عادي + مكمّم)
└── requirements.txt                # 14 مكتبة مطلوبة
```

---

## الوحدات الأساسية (`src/`)

### `labels.py` — تعريف التسميات

يعرّف قائمة `ENTITY_TYPES` بأنواع الكيانات الثمانية، ثم يولّد `BIO_LABELS` ديناميكياً: `["O", "B-SKILL", "I-SKILL", "B-CREDENTIAL", ...]` ليصبح المجموع 17 تسمية. يصدّر أيضاً `LABEL2ID`، `ID2LABEL`، `NUM_LABELS=17`، و `IGNORE_INDEX=-100`.

### `config.py` — تحميل الإعدادات

يعرّف `TrainConfig` كـ dataclass يحتوي على جميع معلمات التدريب. الدالة `parse_args_and_load()` تقرأ ملف YAML (مثل `configs/train.yaml`) ثم تتيح تجاوز أي قيمة من سطر الأوامر. مثلاً:
```bash
python scripts/train.py --config configs/train.yaml --epochs 20 --learning_rate 2e-5
```
يدعم أيضاً بيئة Jupyter/Colab عبر تمرير `args=[]` لتجنب أخطاء argparse.

### `data_module.py` — معالجة البيانات

يقرأ ملفات JSONL بتنسيقين:
- **تنسيق character-span**: `{"text": "...", "entities": [[start, end, "LABEL"], ...]}`
- **تنسيق BIO جاهز**: `{"tokens": [...], "bio_tags": [...]}`

خط المعالجة:
1. **تقطيع الكلمات** (`split_into_words`): فصل بالمسافات مع حفظ `(start_char, end_char)` لكل كلمة
2. **تعيين تسميات BIO** (`assign_bio_labels`): مطابقة character spans مع الكلمات؛ أول كلمة تلمس span تأخذ `B-`، الباقي `I-`
3. **التوكنة** (`tokenize_and_align`): استخدام `is_split_into_words=True` مع نافذة منزلقة (stride). يُحاذي التسميات عبر `word_ids()` — الـ subword الأول فقط يأخذ تسمية الكلمة، والبقية تأخذ `IGNORE_INDEX`
4. الدالة `prepare_dataset()` تجمع كل ما سبق وتُرجع كائن `Dataset` من HuggingFace

### `gazetteer.py` — قواميس البحث

يوفّر صنفين:
- **`SkillGazetteer`**: يحمّل `skills_gazetteer.json` ويبني فهرساً Trie لمطابقة المهارات (منفردة ومتعددة الكلمات). يدعم `match(text)` لإرجاع قائمة `(start, end, skill_text)` و `is_known(text)` للتحقق الثنائي
- **`JobTitleGazetteer`**: مماثل لكن يحمّل `job_titles_gazetteer.json`

القواميس تُستخدم اختيارياً في الاستدلال للتحقق من صحة الكيانات المستخرجة.

### `metrics.py` — مقاييس التقييم

يبني تسميات BIO الحقيقية والمتوقّعة من مصفوفات `predictions` و `labels` (مع تجاهل الفهارس `IGNORE_INDEX`). يستخدم مكتبة `seqeval` لحساب:
- `f1` (micro-average)
- `precision`
- `recall`

الدالة `get_classification_report()` تعطي تقريراً مفصلاً لكل نوع كيان.

### `callbacks.py` — حماية التدريب

`NaNStopCallback` يرث من `TrainerCallback` ويفحص في `on_log` قيمة الخسارة. إذا كانت `NaN` أو `inf`، يطبع تحذيراً ويضع `control.should_training_stop = True`.

### `trainer_module.py` — المدرّب

#### `WeightedNERTrainer`
يرث من `Trainer` ويعيد تعريف `compute_loss()` لتطبيق أوزان الفئات على `CrossEntropyLoss`. وزن الفئة `O` يُقلَّص (الافتراضي `0.3`) لتوجيه التدريب نحو الكيانات الفعلية. يدعم `label_smoothing_factor`.

#### `build_trainer()`
تبني المدرّب الكامل:
1. تحمّل `tokenizer` و `model` من `AutoModelForTokenClassification` مع `id2label`/`label2id`
2. تُعدّ مجموعات البيانات (train/val/test) عبر `prepare_dataset()`
3. تنشئ `TrainingArguments` من الإعدادات
4. تضيف callbacks: `EarlyStoppingCallback(patience)` + `NaNStopCallback`
5. إذا `use_weighted_loss=True`، تحسب أوزان الفئات وتُمرّرها لـ `WeightedNERTrainer`

### `export_onnx.py` — تصدير ONNX

يصدّر النموذج إلى تنسيق ONNX عبر مكتبة `optimum` باستخدام `ORTModelForTokenClassification`. يدعم:
- **تصدير عادي** (float32)
- **تكميم INT8** (`ORTQuantizer` مع `QuantizationConfig` ديناميكي) لتقليل حجم النموذج ~4×

الدالة `validate_onnx()` تقارن مخرجات النموذج الأصلي (PyTorch) مع ONNX وتتحقق من التطابق عبر `numpy.allclose`.

### `inference.py` — الاستدلال الإنتاجي

#### كائن `Entity`
يخزّن: `text`، `label`، `start`، `end`، `confidence`.

#### صنف `NERPipeline`
يقبل مسار نموذج PyTorch أو ONNX. خطوات الاستدلال:

1. **استخراج النص**: يستقبل نصاً خاماً (أو يُستخرج من PDF عبر `PyMuPDF` / من DOCX عبر `python-docx` في `test_cv.py`)
2. **تقطيع بالمسافات**: `split_into_words()` — مطابق تماماً لما يحصل في التدريب
3. **التوكنة الفرعية**: `is_split_into_words=True` مع `stride` و `return_overflowing_tokens=True` لإنشاء نوافذ متداخلة تغطي النص بالكامل
4. **التنبؤ**: لكل نافذة، يُشغَّل النموذج ويُؤخذ `argmax` على البعد الأخير. فقط الـ subword الأول لكل كلمة (عبر `word_ids()`) يُعتمد
5. **دمج الكيانات** (`_merge_entities`): يجمع تسميات B/I المتتالية من نفس النوع في كيان واحد، ويستخدم `char_spans` للحصول على النص الأصلي ومواقعه

يدعم كلا النموذجين:
- **PyTorch**: عبر `AutoModelForTokenClassification`
- **ONNX**: عبر `onnxruntime.InferenceSession`

---

## السكربتات (`scripts/`)

### `train.py` — التدريب

نقطة البدء الرئيسية. يستدعي `parse_args_and_load()` ثم `build_trainer()` ثم:
1. `trainer.train()` — يبدأ التدريب
2. `trainer.evaluate(val_dataset)` — يقيّم على مجموعة التحقق
3. `trainer.evaluate(test_dataset)` — يقيّم على مجموعة الاختبار
4. يحفظ أفضل نموذج في `models/checkpoints/best_model/`
5. يطبع تقرير التصنيف المفصل ووقت التدريب

يُرجع قاموساً يحتوي:
- `test_metrics`: مقاييس الاختبار
- `training_time_min`: الوقت بالدقائق
- `best_model_path`: مسار أفضل نموذج

```bash
python scripts/train.py --config configs/train.yaml
```

### `annotate.py` — توسيم البيانات عبر LLM

يستخدم **Groq API** لتوسيم نصوص السير الذاتية تلقائياً باستخدام نماذج LLM.

#### أمر التشغيل
```bash
# اختبار على 5 نصوص فقط
python scripts/annotate.py --api-key YOUR_GROQ_KEY --limit 5

# توسيم كامل
python scripts/annotate.py --api-key YOUR_GROQ_KEY

# استئناف من نقطة توقف
python scripts/annotate.py --api-key YOUR_GROQ_KEY --resume

# تحديد نموذج معين وسرعة
python scripts/annotate.py --api-key YOUR_GROQ_KEY --model llama-3.3-70b-versatile --rpm 28
```

#### معاملات سطر الأوامر (CLI)
| المعامل | الافتراضي | الوصف |
|---|---|---|
| `--api-key` | *مطلوب* | مفتاح Groq API |
| `--input` | `data/processed/raw_texts.jsonl` | ملف النصوص الخام |
| `--output` | `data/processed/annotated.jsonl` | ملف الإخراج |
| `--resume` | `false` | استئناف من checkpoint |
| `--limit` | `0` (الكل) | عدد النصوص المراد معالجتها |
| `--rpm` | `28` | الحد الأقصى للطلبات في الدقيقة |
| `--model` | `llama-3.3-70b-versatile` | نموذج Groq المستخدم |

#### النماذج المدعومة (بالترتيب حسب الأفضلية)
1. `llama-3.3-70b-versatile` — النموذج الأساسي
2. `llama-3.1-8b-instant` — بديل سريع
3. `qwen/qwen3-32b` — بديل ثالث
4. `meta-llama/llama-4-scout-17b-16e-instruct` — بديل رابع

عند استنفاد حصة نموذج (TPD limit)، ينتقل تلقائياً للنموذج التالي.

#### الـ Prompt المُستخدم للتوسيم

**System Prompt:**
```
You are an expert NER annotator for resumes/CVs.
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
```

**User Prompt Template:**
```
Annotate the following resume text. Return ONLY the JSON array of entities.

RESUME TEXT:
---
{text}
---

JSON entities:
```

#### آلية العمل الداخلية
1. يقرأ نصوصاً خام من ملف JSONL (`raw_texts.jsonl`)
2. يُرسل كل نص إلى نموذج LLM مع `temperature=0.0` و `max_tokens=8192` ووضع `json_object`
3. يُحلّل استجابة JSON (يدعم تنسيقات `[...]` و `{"entities": [...]}` و markdown fences)
4. **التحقق** (`validate_entities`): يفحص كل كيان — هل `text[start:end]` يطابق النص فعلاً؟ إن لم يطابق، يبحث عن النص في المستند ويُصلح الإحداثيات. يحذف الكيانات غير القابلة للإصلاح ويزيل التداخلات (يُفضّل الأطول)
5. **بوابة الجودة**: يرفض التوسيمات التي تحتوي على أكثر من 40% `PERSON` أو 50% `ORG` (علامة على هلوسة النموذج)
6. **التحويل إلى BIO** (`entities_to_bio`): يحوّل الكيانات من character-spans إلى word-level BIO tags
7. يحفظ النتائج في `annotated.jsonl` مع إحصائيات لكل سجل
8. يدعم **إيقاف واستئناف** عبر checkpoint (`--resume`)
9. يتوقف تلقائياً بعد 3 إخفاقات متتالية (جميع النماذج مستنفدة)

### `augment_data.py` — تعزيز البيانات

أكبر سكربت (964 سطراً). يولّد بيانات تدريب صناعية عبر ثلاث استراتيجيات:

1. **استبدال الكيانات** (`entity_substitution`): يستبدل كيانات موجودة بأخرى عشوائية من **بنوك كيانات متعددة المجالات** (تقنية معلومات، صحة، تمويل، تعليم، هندسة، تسويق، قانون، ...) — كل مجال يحتوي على مهارات ومسميات وظيفية وشهادات ومنشآت وأسماء ومواقع واقعية
2. **توليد بالقوالب** (`template_generation`): يستخدم قوالب سير ذاتية (summary, experience, education, skills sections) ويملأها بكيانات عشوائية
3. **خلط الأقسام** (`section_shuffle`): يعيد ترتيب أقسام السيرة الذاتية

يحفظ النتيجة في `train_augmented.jsonl`.

### `build_gazetteer.py` — بناء القواميس

يقرأ بيانات التصنيفات من مصدرين:
- **O*NET**: ملفات `skills.txt` و `technology_skills.txt` (مهارات) + `occupations.txt` (مسميات وظيفية)
- **ESCO**: ملفات `skills_en.csv` و `occupations_en.csv`

يستخرج الأسماء، يُنظّفها (lowercase, إزالة أقواس، حذف تكرارات)، ويحفظها في:
- `data/gazetteers/skills_gazetteer.json`
- `data/gazetteers/job_titles_gazetteer.json`

### `fix_annotations.py` — إصلاح التوسيم

يُطبّق 6 خطوات تصحيح على البيانات المشروحة:
1. **إصلاح BIO**: تصحيح تسلسلات `I-` بدون `B-` سابق
2. **حذف تسميات طول صفر**: كيانات بحدود `start == end`
3. **حذف كيانات حرف واحد SKILL**: لأنها غالباً أخطاء
4. **إصلاح عناوين الأقسام**: إزالة تسميات SKILL من كلمات مثل "Skills", "Education"
5. **تصحيح التداخلات**: حل الكيانات المتداخلة (يُفضّل الأطول)
6. **تنظيف المسافات الزائدة**

يقرأ `annotated.jsonl` ويكتب النسخة المصححة + ملف إحصائيات `fix_stats.json`. الإحصائيات الأخيرة: 4,291 سجل دخول → 2,709 سجل بعد الإصلاح والتنقية.

### `audit_annotations.py` — تدقيق الجودة

يفحص البيانات المشروحة ويكشف 5 أنماط أخطاء:
1. **`entity_bio_mismatch`**: تسمية I- بدون B- سابق لنفس النوع
2. **`overlapping_entities`**: كيانات متداخلة الحدود
3. **`repetition_inconsistency`**: نفس النص يُوسَم بأنواع مختلفة في سجلات مختلفة
4. **`suspicious_length`**: كيانات طويلة جداً أو حرف واحد
5. **`boundary_errors`**: كيانات تبدأ/تنتهي بمسافة أو علامات ترقيم

يُنتج `audit_report.json` بإحصائيات مفصلة. التقرير الأخير أظهر معدل أخطاء 61.9% في البيانات الخام (قبل التنقية بـ `fix_annotations.py`).

### `split.py` — تقسيم البيانات

يقسم البيانات إلى train/val/test بنسب قابلة للتعديل (الافتراضي: 80/10/10). يستخدم **تقسيماً طبقياً حسب الكيانات**: يحسب أنواع الكيانات الموجودة في كل سجل ويُنشئ "بصمة كيانات" لضمان توزيع متوازن عبر التقسيمات الثلاث.

### `evaluate.py` — تقييم النموذج

يحمّل نموذجاً مدرّباً ومجموعة بيانات اختبار، يُشغّل التقييم، ويطبع:
- F1, Precision, Recall (إجمالي)
- تقرير تصنيف مفصل لكل نوع كيان

```bash
python scripts/evaluate.py --model models/checkpoints/best_model --data data/processed/test.jsonl
```

### `extract_texts.py` — استخراج النصوص

يستخرج نصوصاً خامة من مصادر متعددة:
- **PDF** عبر `PyMuPDF` (`fitz`)
- **DOCX** عبر `python-docx`
- **JSON المشروح** من Kaggle NER و HuggingFace Annotated Resumes

يجمع النصوص في ملف JSONL واحد للتمرير إلى `annotate.py`.

### `pack_colab.py` — تجهيز Colab

يُنشئ أرشيف ZIP يحتوي:
- `configs/`
- `src/`
- `scripts/`
- `data/processed/` (ملفات JSONL)
- دفتر `train.ipynb`
- `requirements.txt`

يُستبعد: النماذج الكبيرة، البيانات الخام، القواميس، والتصنيفات. يُحفظ كـ `viora_ner_colab.zip`.

---

## الاختبارات (`tests/`)

### `test_labels.py`
- يتحقق أن `NUM_LABELS == 17`
- يتحقق أن كل نوع كيان ينتج `B-` و `I-`
- يتحقق أن `LABEL2ID` و `ID2LABEL` عكسيان

### `test_data_quality.py`
- يقرأ ملفات التدريب/التحقق/الاختبار ويتحقق:
  - كل سجل يحتوي على مفاتيح `tokens` و `bio_tags`
  - طول `tokens` يساوي طول `bio_tags`
  - جميع التسميات موجودة في `BIO_LABELS`
  - لا توجد تسلسلات BIO مكسورة

### `test_pipeline.py`
- يُنشئ بيانات وهمية ويختبر خط المعالجة الكامل:
  - التوكنة وتحاذي التسميات
  - بناء المدرّب بدون أخطاء
  - خطوة تدريب واحدة بدون انهيار

### `test_cv.py`
- يقبل مسار ملف (PDF/DOCX/TXT) عبر سطر الأوامر
- يستخرج النص ثم يُشغّل `NERPipeline`
- يطبع الكيانات المكتشفة مع مواقعها ودرجات الثقة

```bash
python tests/test_cv.py path/to/resume.pdf
```

---

## البيانات

### البيانات المعالجة (`data/processed/`)

| الملف | الوصف | الحجم |
|---|---|---|
| `annotated.jsonl` | البيانات المشروحة بعد التنقية | 57 MB |
| `train_augmented.jsonl` | بيانات التدريب بعد التعزيز | 326 MB |
| `train.jsonl` | تقسيمة التدريب | — |
| `val.jsonl` | تقسيمة التحقق | — |
| `test.jsonl` | تقسيمة الاختبار | — |
| `label_info.json` | أنواع الكيانات وتسميات BIO وتحويلاتها | — |
| `fix_stats.json` | إحصائيات إصلاح التوسيم (4291→2709) | — |
| `audit_report.json` | تقرير تدقيق الجودة (61.9% أخطاء خام) | — |

تنسيق كل سطر في ملفات JSONL:
```json
{"tokens": ["John", "Smith", "is", "a", "Software", "Engineer"],
 "bio_tags": ["B-PERSON", "I-PERSON", "O", "O", "B-JOB_TITLE", "I-JOB_TITLE"]}
```
أو:
```json
{"text": "John Smith is a Software Engineer",
 "entities": [[0, 10, "PERSON"], [16, 33, "JOB_TITLE"]]}
```

### البيانات الخام (`data/raw/`)

#### Kaggle NER (`kaggle_ner/`)
- **`train.json`** (63 MB): مجموعة بيانات NER تحتوي 5,960 عينة سيرة ذاتية من 4 مصادر أصلية مع 14 فئة كيان (تشمل فئات أوسع تم تحويلها إلى فئاتنا الـ 8)
- **`sample.json`**: 5 أمثلة للمعاينة — كل مثال يحتوي نص سيرة ذاتية كاملة مع قائمة `annotations` بتنسيق `[start, end, label]`

#### HuggingFace Annotated Resumes (`hf_annotated_resumes/ResumesJsonAnnotated/`)
- حوالي **3,500+ ملف JSON فردي** بالتنسيق `cv (N)_annotated.json`
- كل ملف يحتوي نص سيرة ذاتية مع شروحها
- بعض الملفات فارغة (31 بايت فقط) أو صغيرة جداً
- بعضها كبير (>100 KB) يحتوي سير ذاتية مفصلة

### القواميس (`data/gazetteers/`)

| الملف | المحتوى | الحجم |
|---|---|---|
| `skills_gazetteer.json` | آلاف المهارات من O*NET + ESCO | 808 KB |
| `job_titles_gazetteer.json` | مئات المسميات الوظيفية من O*NET + ESCO | 141 KB |

### التصنيفات (`data/taxonomy/`)

#### O*NET (`onet/`) — شبكة المعلومات المهنية الأمريكية

5 ملفات مفصولة بعلامات Tab، جميعها من قاعدة بيانات O*NET:

##### 1. `occupations.txt` — المهن (0.25 MB)
- **الأعمدة (3):** `O*NET-SOC Code` | `Title` | `Description`
- **1,016 مهنة فريدة** برموز SOC (مثل `11-1011.00` = Chief Executives)
- يغطي جميع القطاعات: إدارة، تقنية، صحة، هندسة، تعليم، عسكرية، نقل...
- كل سجل يحتوي وصفاً تفصيلياً لمهام المهنة

##### 2. `skills.txt` — المهارات (5.38 MB، 62,581 سطر)
- **الأعمدة (13):** `O*NET-SOC Code` | `Element ID` | `Element Name` | `Scale ID` | `Data Value` | `N` | `Standard Error` | `Lower CI Bound` | `Upper CI Bound` | `Recommend Suppress` | `Not Relevant` | `Date` | `Domain Source`
- **894 مهنة × 35 مهارة × مقياسين** = بيانات كمية لأهمية ومستوى كل مهارة لكل مهنة
- **المقياسان:**
  - `IM` (Importance): أهمية المهارة للمهنة (1-5)
  - `LV` (Level): مستوى المهارة المطلوب (0-7)
- **المهارات الـ 35:**
  - **أساسية (Content):** Reading Comprehension, Active Listening, Writing, Speaking, Mathematics, Science
  - **تفكير (Process):** Critical Thinking, Active Learning, Learning Strategies, Monitoring
  - **اجتماعية (Social):** Social Perceptiveness, Coordination, Persuasion, Negotiation, Instructing, Service Orientation
  - **حل مشاكل:** Complex Problem Solving
  - **تقنية (Technical):** Operations Analysis, Technology Design, Equipment Selection, Installation, Programming, Operations Monitoring, Operation and Control, Equipment Maintenance, Troubleshooting, Repairing, Quality Control Analysis
  - **تحليل أنظمة:** Judgment and Decision Making, Systems Analysis, Systems Evaluation
  - **إدارة موارد:** Time Management, Management of Financial Resources, Management of Material Resources, Management of Personnel Resources

##### 3. `abilities.txt` — القدرات (8.16 MB، 92,977 سطر)
- **نفس هيكل الأعمدة (13)** كملف المهارات
- **894 مهنة × 52 قدرة × مقياسين**
- **القدرات الـ 52:**
  - **إدراكية:** Oral Comprehension, Written Comprehension, Oral Expression, Written Expression, Fluency of Ideas, Originality, Problem Sensitivity, Deductive Reasoning, Inductive Reasoning, Information Ordering, Category Flexibility, Mathematical Reasoning, Number Facility, Memorization, Perceptual Speed, Flexibility of Closure, Speed of Closure, Spatial Orientation, Visualization, Selective Attention, Time Sharing
  - **حركية:** Arm-Hand Steadiness, Manual Dexterity, Finger Dexterity, Control Precision, Multilimb Coordination, Response Orientation, Rate Control, Reaction Time, Wrist-Finger Speed, Speed of Limb Movement
  - **بدنية:** Static Strength, Explosive Strength, Dynamic Strength, Trunk Strength, Stamina, Extent Flexibility, Dynamic Flexibility, Gross Body Coordination, Gross Body Equilibrium
  - **حسية:** Near Vision, Far Vision, Visual Color Discrimination, Night Vision, Peripheral Vision, Depth Perception, Glare Sensitivity, Hearing Sensitivity, Auditory Attention, Sound Localization, Speech Recognition, Speech Clarity

##### 4. `knowledge.txt` — مجالات المعرفة (5.35 MB، 59,005 سطر)
- **نفس هيكل الأعمدة (13)**
- **894 مهنة × 33 مجال معرفة × مقياسين**
- **المجالات الـ 33:** Administration and Management, Administrative, Biology, Building and Construction, Chemistry, Communications and Media, Computers and Electronics, Customer and Personal Service, Design, Economics and Accounting, Education and Training, Engineering and Technology, English Language, Fine Arts, Food Production, Foreign Language, Geography, History and Archeology, Law and Government, Mathematics, Mechanical, Medicine and Dentistry, Personnel and Human Resources, Philosophy and Theology, Physics, Production and Processing, Psychology, Public Safety and Security, Sales and Marketing, Sociology and Anthropology, Telecommunications, Therapy and Counseling, Transportation

##### 5. `technology_skills.txt` — المهارات التقنية والأدوات (2.48 MB، 32,774 سطر)
- **الأعمدة (6):** `O*NET-SOC Code` | `Example` | `Commodity Code` | `Commodity Title` | `Hot Technology` | `In Demand`
- **923 مهنة** مرتبطة بـ **8,785 أداة/برنامج فريد** مصنفة في **137 فئة تقنية**
- **11,526 إدخال مصنف كـ Hot Technology** (تقنيات رائجة)
- **2,493 إدخال مصنف كـ In Demand** (مطلوبة في السوق)
- **أمثلة على الفئات:** Accounting software, Analytical or scientific software, Business intelligence and data analysis software, Cloud-based management software, Computer aided design CAD software, Configuration management software, Database management system software...
- **أمثلة على الأدوات:** Python, JavaScript, SAP, Salesforce, Microsoft Excel, AutoCAD, Docker, Kubernetes, AWS, Adobe Creative Suite...

#### ESCO (`esco/ESCO dataset - v1.2.1 - classification - en - csv/`) — التصنيف الأوروبي

19 ملف CSV من مشروع ESCO (European Skills, Competences, Qualifications and Occupations) الإصدار 1.2.1:

| الملف | السطور | الحجم | الأعمدة | الوصف |
|---|---|---|---|---|
| `skills_en.csv` | 104,065 | 9.1 MB | 13 | المهارات والكفاءات (conceptType, skillType, preferredLabel, altLabels, definition...) |
| `occupations_en.csv` | 35,204 | 3.0 MB | 15 | المهن (conceptType, iscoGroup, preferredLabel, altLabels, definition, code, naceCode...) |
| `occupationSkillRelations_en.csv` | 126,052 | 27.3 MB | 6 | علاقات المهن بالمهارات (occupationLabel, relationType: essential/optional, skillLabel) |
| `broaderRelationsSkillPillar_en.csv` | 20,820 | 4.8 MB | 6 | العلاقات الهرمية بين المهارات |
| `conceptSchemes_en.csv` | 13,106 | 919 KB | 7 | مخططات المفاهيم |
| `ISCOGroups_en.csv` | 9,025 | 944 KB | 8 | مجموعات التصنيف الدولي ISCO |
| `skillSkillRelations_en.csv` | 5,819 | 1.0 MB | 5 | علاقات المهارات ببعضها |
| `skillGroups_en.csv` | 3,529 | 333 KB | 11 | تجميعات المهارات |
| `broaderRelationsOccPillar_en.csv` | 3,649 | 713 KB | 6 | العلاقات الهرمية بين المهن |
| `greenShareOcc_en.csv` | 3,591 | 442 KB | 5 | المهن الخضراء (بيئية) |
| `skillsHierarchy_en.csv` | 2,505 | 373 KB | 14 | الهرمية الكاملة للمهارات |
| `digitalSkillsCollection_en.csv` | 1,285 | 792 KB | 10 | مجموعة المهارات الرقمية |
| `greenSkillsCollection_en.csv` | 630 | 445 KB | 10 | مجموعة المهارات الخضراء |
| `languageSkillsCollection_en.csv` | 360 | 141 KB | 10 | مجموعة المهارات اللغوية |
| `dictionary_en.csv` | 185 | 19 KB | 4 | قاموس المصطلحات |
| `researchOccupationsCollection_en.csv` | 123 | 124 KB | 8 | مهن البحث العلمي |
| `transversalSkillsCollection_en.csv` | 96 | 56 KB | 10 | المهارات العرضية (Transversal) |
| `researchSkillsCollection_en.csv` | 41 | 26 KB | 10 | مهارات البحث العلمي |
| `digCompSkillsCollection_en.csv` | 26 | 18 KB | 10 | إطار الكفاءة الرقمية DigComp |

**الملفات الثلاثة الرئيسية التي يستخدمها `build_gazetteer.py`:**
- `skills_en.csv`: يستخرج عمود `preferredLabel` و `altLabels` لبناء قاموس المهارات
- `occupations_en.csv`: يستخرج `preferredLabel` و `altLabels` لبناء قاموس المسميات الوظيفية
- `occupationSkillRelations_en.csv`: يربط كل مهنة بمهاراتها (essential أو optional) عبر `skillLabel`

---

## إعدادات التدريب (`configs/train.yaml`)

| المعلمة | القيمة | الشرح |
|---|---|---|
| `model_name` | `roberta-base` | النموذج الأساسي (125M بارامتر) |
| `max_length` | `512` | أقصى طول للتوكنات |
| `stride` | `128` | خطوة النافذة المنزلقة |
| `epochs` | `15` | عدد جولات التدريب |
| `per_device_train_batch_size` | `8` | حجم الدفعة للتدريب |
| `per_device_eval_batch_size` | `16` | حجم الدفعة للتقييم |
| `gradient_accumulation_steps` | `4` | تجميع التدرجات (حجم فعّال = 32) |
| `learning_rate` | `3e-5` | معدل التعلّم |
| `warmup_ratio` | `0.1` | نسبة الإحماء |
| `weight_decay` | `0.01` | اضمحلال الأوزان |
| `max_grad_norm` | `1.0` | قص التدرجات |
| `lr_scheduler_type` | `linear` | جدولة معدل التعلّم |
| `use_weighted_loss` | `false` | الخسارة الموزونة (معطّلة افتراضياً) |
| `o_class_weight` | `0.3` | وزن الفئة O (عند التفعيل) |
| `label_smoothing_factor` | `0.1` | عامل تنعيم التسميات |
| `early_stopping_patience` | `5` | صبر الإيقاف المبكر (عدد الجولات) |
| `metric_for_best_model` | `eval_f1` | مقياس اختيار أفضل نموذج |
| `save_total_limit` | `3` | أقصى عدد نقاط حفظ محتفظ بها |
| `use_crf` | `false` | طبقة CRF (معطّلة) |
| `seed` | `42` | بذرة العشوائية |

---

## النموذج المدرّب

### ملفات النموذج (`models/checkpoints/best_model/`)

| الملف | الحجم | الوصف |
|---|---|---|
| `model.safetensors` | 496 MB | أوزان النموذج (safetensors) |
| `config.json` | 1.4 KB | إعدادات الهندسة المعمارية |
| `tokenizer.json` | — | ملف التوكنة السريع |
| `tokenizer_config.json` | — | إعدادات التوكنة |
| `training_args.bin` | — | معلمات التدريب المحفوظة |

### الهندسة المعمارية (من `config.json`)

- **النوع**: `RobertaForTokenClassification`
- **الطبقات**: 12 طبقة transformer
- **رؤوس الانتباه**: 12
- **البعد المخفي**: 768
- **البعد الوسيط**: 3,072
- **حجم المفردات**: 50,265
- **أقصى مواقع**: 514
- **عدد التسميات**: 17 (محددة في `id2label`/`label2id`)
- **التنشيط**: GELU
- **Dropout**: 0.1 (attention + hidden)

### النماذج المصدّرة (`models/exported/`)

- `onnx/` — نموذج ONNX بصيغة float32
- `onnx_quantized/` — نموذج ONNX بتكميم INT8 ديناميكي (حجم أصغر ~4×)

---

## خط أنابيب البيانات الكامل

```
[البيانات الخام]
    ├── Kaggle NER (train.json: 5,960 عينة, 14 فئة)
    └── HuggingFace Resumes (~3,500+ ملف JSON)
         │
         ▼
[extract_texts.py] → نصوص خام JSONL
         │
         ▼
[annotate.py] → توسيم عبر Groq LLM → annotated.jsonl (57 MB)
         │
         ▼
[audit_annotations.py] → تقرير الجودة (61.9% أخطاء)
         │
         ▼
[fix_annotations.py] → إصلاح تلقائي (4,291 → 2,709 سجل)
         │
         ▼
[split.py] → تقسيم طبقي → train.jsonl + val.jsonl + test.jsonl
         │
         ▼
[augment_data.py] → تعزيز البيانات → train_augmented.jsonl (326 MB)
         │
         ▼
[build_gazetteer.py] → قواميس من O*NET + ESCO
         │
         ▼
[train.py] → تدريب roberta-base → best_model/
         │
         ▼
[evaluate.py] → تقييم F1/Precision/Recall
         │
         ▼
[export_onnx.py] → ONNX + تكميم INT8
         │
         ▼
[inference.py / test_cv.py] → استدلال على سير ذاتية حقيقية
```

---

## الاستخدام

> ⚠️ **ملاحظة**: الأوامر التالية مخصصة **لإعادة تدريب النموذج أو تعديله** 
> إذا كنت تريد فقط تشغيل تطبيق Viora، راجع [README الرئيسي](../../README.md#-إعداد-المشروع-خطوة-بخطوة).

### تثبيت المتطلبات
```bash
pip install -r requirements.txt
```

### التدريب محلياً
```bash
python scripts/train.py --config configs/train.yaml
```

### التدريب على Google Colab
```bash
# 1. تجهيز أرشيف المشروع
python scripts/pack_colab.py

# 2. رفع viora_ner_colab.zip إلى Google Drive

# 3. فتح notebooks/train.ipynb في Colab وتشغيل الخلايا
```

دفتر Colab يتضمن 8 خلايا:
1. ربط Google Drive
2. تثبيت المكتبات
3. فك ضغط ملفات المشروع
4. ضبط مسار العمل
5. تشغيل الاختبارات
6. بدء التدريب
7. عرض النتائج (F1, Precision, Recall, وقت التدريب)
8. حفظ النموذج إلى Drive

### اختبار على سيرة ذاتية
```bash
python tests/test_cv.py path/to/resume.pdf
python tests/test_cv.py path/to/resume.docx
```

### التقييم
```bash
python scripts/evaluate.py --model models/checkpoints/best_model --data data/processed/test.jsonl
```

### تشغيل جميع الاختبارات
```bash
python -m pytest tests/ -v
```

### تصدير ONNX
```python
from src.export_onnx import export_to_onnx

export_to_onnx(
    model_path="models/checkpoints/best_model",
    output_dir="models/exported/onnx",
    quantize=True  # لتكميم INT8
)
```

---

## المكتبات المطلوبة

| المكتبة | الغرض |
|---|---|
| `torch` | إطار التعلّم العميق |
| `transformers` | نماذج HuggingFace (RoBERTa) |
| `datasets` | مجموعات بيانات HuggingFace |
| `seqeval` | مقاييس تقييم NER على مستوى الكيانات |
| `pyyaml` | قراءة ملفات الإعدادات |
| `accelerate` | تسريع التدريب |
| `sentencepiece` | توكنة subword |
| `PyMuPDF` (`fitz`) | استخراج نص من PDF |
| `python-docx` | استخراج نص من DOCX |
| `pytest` | تشغيل الاختبارات |
| `optimum[onnxruntime]` | تصدير وتكميم ONNX |
| `groq` | واجهة Groq API للتوسيم |
| `numpy` | عمليات حسابية |
| `scikit-learn` | تقسيم طبقي |
