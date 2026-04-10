# Viora NER

A Named Entity Recognition (NER) system for analyzing resumes/CVs and extracting structured information.

The system fine-tunes a `roberta-base` model on annotated English resume data to detect 8 entity types using the BIO (Begin-Inside-Outside) tagging scheme.

---

## Entity Types (8 Types)

| Type | Description | Example |
|---|---|---|
| `SKILL` | Technical and soft skills | Python, Machine Learning, Leadership |
| `CREDENTIAL` | Degrees and certifications | B.Sc. Computer Science, PMP |
| `ORG` | Organizations: companies, universities | Google, MIT, WHO |
| `PERSON` | Person names | John Smith |
| `LOCATION` | Geographic locations: cities, countries | New York, Germany |
| `CONTACT` | Contact info: email, phone, links | john@email.com, +1-555-0123 |
| `JOB_TITLE` | Job titles and roles | Software Engineer, Data Analyst |
| `EXPERIENCE` | Dates and experience durations | 2019-2023, 5 years |

Each type produces two BIO tags (`B-SKILL`, `I-SKILL`...) plus the `O` tag (outside any entity) = **17 labels total**.

These labels are defined in `src/labels.py`, where the mappings `LABEL2ID` and `ID2LABEL` are generated dynamically. The index `-100` (`IGNORE_INDEX`) is used to ignore subword tokens and special tokens during loss computation.

---

## Project Structure

```
viora-ner/
├── configs/
│   └── train.yaml                  # Full training configuration
├── src/                            # Core modules (9 files)
│   ├── labels.py                   # 8 entity types → 17 BIO labels
│   ├── config.py                   # YAML config loading with CLI override support
│   ├── data_module.py              # JSONL loading + tokenization + sliding window
│   ├── gazetteer.py                # Skills and job titles dictionary (Trie)
│   ├── metrics.py                  # F1/Precision/Recall via seqeval
│   ├── callbacks.py                # NaNStopCallback to halt training on NaN
│   ├── trainer_module.py           # WeightedNERTrainer + trainer builder
│   ├── export_onnx.py              # ONNX export with INT8 quantization
│   └── inference.py                # Production inference pipeline
├── scripts/                        # Utilities (10 files)
│   ├── train.py                    # Training entry point
│   ├── evaluate.py                 # Model evaluation and classification report
│   ├── annotate.py                 # Data annotation via Groq API (LLM)
│   ├── augment_data.py             # Data augmentation (entity substitution + templates)
│   ├── build_gazetteer.py          # Build skill dictionaries from O*NET + ESCO
│   ├── fix_annotations.py          # Auto-fix annotation errors (6 steps)
│   ├── audit_annotations.py        # Annotation quality audit (5 error patterns)
│   ├── split.py                    # Stratified split by entity types
│   ├── extract_texts.py            # Text extraction from PDF/DOCX
│   └── pack_colab.py               # Pack ZIP archive for Colab training
├── tests/                          # Tests (4 files)
│   ├── test_labels.py              # Verify label definitions
│   ├── test_data_quality.py        # Check processed data quality
│   ├── test_pipeline.py            # Test training pipeline setup
│   └── test_cv.py                  # Test inference on real resumes
├── notebooks/
│   └── train.ipynb                 # Google Colab notebook (8 cells)
├── data/
│   ├── processed/                  # Training-ready data (JSONL)
│   ├── raw/                        # Raw data (Kaggle + HuggingFace)
│   ├── gazetteers/                 # JSON dictionaries (skills + job titles)
│   └── taxonomy/                   # O*NET and ESCO taxonomies
├── models/
│   ├── checkpoints/best_model/     # Best trained model (safetensors)
│   └── exported/                   # ONNX models (standard + quantized)
└── requirements.txt                # 14 required libraries
```

---

## Core Modules (`src/`)

### `labels.py` — Label Definitions

Defines the `ENTITY_TYPES` list with 8 entity types, then dynamically generates `BIO_LABELS`: `["O", "B-SKILL", "I-SKILL", "B-CREDENTIAL", ...]` totaling 17 labels. Also exports `LABEL2ID`, `ID2LABEL`, `NUM_LABELS=17`, and `IGNORE_INDEX=-100`.

### `config.py` — Configuration Loading

Defines `TrainConfig` as a dataclass containing all training parameters. The function `parse_args_and_load()` reads a YAML file (e.g., `configs/train.yaml`) then allows overriding any value from the command line. Example:
```bash
python scripts/train.py --config configs/train.yaml --epochs 20 --learning_rate 2e-5
```
Also supports Jupyter/Colab environments by passing `args=[]` to avoid argparse errors.

### `data_module.py` — Data Processing

Reads JSONL files in two formats:
- **Character-span format**: `{"text": "...", "entities": [[start, end, "LABEL"], ...]}`
- **Ready BIO format**: `{"tokens": [...], "bio_tags": [...]}`

Processing pipeline:
1. **Word splitting** (`split_into_words`): Splits by whitespace while preserving `(start_char, end_char)` for each word
2. **BIO label assignment** (`assign_bio_labels`): Matches character spans to words; the first word touching a span gets `B-`, the rest get `I-`
3. **Tokenization** (`tokenize_and_align`): Uses `is_split_into_words=True` with a sliding window (stride). Aligns labels via `word_ids()` — only the first subword of each word gets the word's label, the rest get `IGNORE_INDEX`
4. The `prepare_dataset()` function combines all the above and returns a HuggingFace `Dataset` object

### `gazetteer.py` — Lookup Dictionaries

Provides two classes:
- **`SkillGazetteer`**: Loads `skills_gazetteer.json` and builds a Trie index for matching skills (single and multi-word). Supports `match(text)` returning a list of `(start, end, skill_text)` and `is_known(text)` for boolean checking
- **`JobTitleGazetteer`**: Similar but loads `job_titles_gazetteer.json`

Gazetteers are optionally used during inference to validate extracted entities.

### `metrics.py` — Evaluation Metrics

Builds ground-truth and predicted BIO labels from `predictions` and `labels` arrays (ignoring `IGNORE_INDEX` indices). Uses the `seqeval` library to compute:
- `f1` (micro-average)
- `precision`
- `recall`

The `get_classification_report()` function provides a detailed report per entity type.

### `callbacks.py` — Training Protection

`NaNStopCallback` inherits from `TrainerCallback` and checks the loss value in `on_log`. If it's `NaN` or `inf`, it prints a warning and sets `control.should_training_stop = True`.

### `trainer_module.py` — Trainer

#### `WeightedNERTrainer`
Inherits from `Trainer` and overrides `compute_loss()` to apply class weights to `CrossEntropyLoss`. The weight for class `O` is reduced (default `0.3`) to direct training toward actual entities. Supports `label_smoothing_factor`.

#### `build_trainer()`
Builds the complete trainer:
1. Loads `tokenizer` and `model` from `AutoModelForTokenClassification` with `id2label`/`label2id`
2. Prepares datasets (train/val/test) via `prepare_dataset()`
3. Creates `TrainingArguments` from configuration
4. Adds callbacks: `EarlyStoppingCallback(patience)` + `NaNStopCallback`
5. If `use_weighted_loss=True`, computes class weights and passes them to `WeightedNERTrainer`

### `export_onnx.py` — ONNX Export

Exports the model to ONNX format via the `optimum` library using `ORTModelForTokenClassification`. Supports:
- **Standard export** (float32)
- **INT8 quantization** (`ORTQuantizer` with dynamic `QuantizationConfig`) to reduce model size ~4×

The `validate_onnx()` function compares outputs from the original (PyTorch) model with ONNX and verifies match via `numpy.allclose`.

### `inference.py` — Production Inference

#### `Entity` Object
Stores: `text`, `label`, `start`, `end`, `confidence`.

#### `NERPipeline` Class
Accepts a PyTorch or ONNX model path. Inference steps:

1. **Text extraction**: Receives raw text (or extracts from PDF via `PyMuPDF` / from DOCX via `python-docx` in `test_cv.py`)
2. **Whitespace splitting**: `split_into_words()` — identical to training
3. **Subword tokenization**: `is_split_into_words=True` with `stride` and `return_overflowing_tokens=True` to create overlapping windows covering the entire text
4. **Prediction**: For each window, runs the model and takes `argmax` on the last dimension. Only the first subword of each word (via `word_ids()`) is considered
5. **Entity merging** (`_merge_entities`): Combines consecutive B/I tags of the same type into a single entity, using `char_spans` to get the original text and positions

Supports both model types:
- **PyTorch**: via `AutoModelForTokenClassification`
- **ONNX**: via `onnxruntime.InferenceSession`

---

## Scripts (`scripts/`)

### `train.py` — Training

Main entry point. Calls `parse_args_and_load()` then `build_trainer()` then:
1. `trainer.train()` — starts training
2. `trainer.evaluate(val_dataset)` — evaluates on validation set
3. `trainer.evaluate(test_dataset)` — evaluates on test set
4. Saves the best model to `models/checkpoints/best_model/`
5. Prints detailed classification report and training time

Returns a dictionary containing:
- `test_metrics`: test metrics
- `training_time_min`: time in minutes
- `best_model_path`: path to best model

```bash
python scripts/train.py --config configs/train.yaml
```

### `annotate.py` — Data Annotation via LLM

Uses **Groq API** to automatically annotate resume texts using LLM models.

#### Run Command
```bash
# Test on 5 texts only
python scripts/annotate.py --api-key YOUR_GROQ_KEY --limit 5

# Full annotation
python scripts/annotate.py --api-key YOUR_GROQ_KEY

# Resume from checkpoint
python scripts/annotate.py --api-key YOUR_GROQ_KEY --resume

# Specify model and rate
python scripts/annotate.py --api-key YOUR_GROQ_KEY --model llama-3.3-70b-versatile --rpm 28
```

#### CLI Arguments
| Argument | Default | Description |
|---|---|---|
| `--api-key` | *required* | Groq API key |
| `--input` | `data/processed/raw_texts.jsonl` | Input raw texts file |
| `--output` | `data/processed/annotated.jsonl` | Output file |
| `--resume` | `false` | Resume from checkpoint |
| `--limit` | `0` (all) | Number of texts to process |
| `--rpm` | `28` | Max requests per minute |
| `--model` | `llama-3.3-70b-versatile` | Groq model to use |

#### Supported Models (in preference order)
1. `llama-3.3-70b-versatile` — Primary model
2. `llama-3.1-8b-instant` — Fast fallback
3. `qwen/qwen3-32b` — Third fallback
4. `meta-llama/llama-4-scout-17b-16e-instruct` — Fourth fallback

When a model's quota is exhausted (TPD limit), it automatically switches to the next one.

#### Annotation Prompt

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

#### Internal Workflow
1. Reads raw texts from a JSONL file (`raw_texts.jsonl`)
2. Sends each text to the LLM with `temperature=0.0`, `max_tokens=8192`, and `json_object` mode
3. Parses JSON response (supports `[...]`, `{"entities": [...]}`, and markdown fence formats)
4. **Validation** (`validate_entities`): Checks each entity — does `text[start:end]` match the text? If not, searches for the text in the document and fixes offsets. Drops unfixable entities and removes overlaps (prefers longer ones)
5. **Quality gate**: Rejects annotations with >40% `PERSON` or >50% `ORG` (sign of model hallucination)
6. **BIO conversion** (`entities_to_bio`): Converts entities from character-spans to word-level BIO tags
7. Saves results to `annotated.jsonl` with per-record statistics
8. Supports **stop and resume** via checkpoint (`--resume`)
9. Automatically stops after 3 consecutive failures (all models exhausted)

### `augment_data.py` — Data Augmentation

The largest script (964 lines). Generates synthetic training data via three strategies:

1. **Entity substitution** (`entity_substitution`): Replaces existing entities with random ones from **multi-domain entity banks** (IT, healthcare, finance, education, engineering, marketing, law, ...) — each domain contains realistic skills, job titles, credentials, organizations, names, and locations
2. **Template generation** (`template_generation`): Uses resume templates (summary, experience, education, skills sections) and fills them with random entities
3. **Section shuffling** (`section_shuffle`): Reorders resume sections

Saves the result to `train_augmented.jsonl`.

### `build_gazetteer.py` — Dictionary Building

Reads taxonomy data from two sources:
- **O*NET**: Files `skills.txt` and `technology_skills.txt` (skills) + `occupations.txt` (job titles)
- **ESCO**: Files `skills_en.csv` and `occupations_en.csv`

Extracts names, cleans them (lowercase, remove parentheses, deduplicate), and saves to:
- `data/gazetteers/skills_gazetteer.json`
- `data/gazetteers/job_titles_gazetteer.json`

### `fix_annotations.py` — Annotation Fixing

Applies 6 correction steps on annotated data:
1. **BIO fix**: Corrects `I-` sequences without a preceding `B-`
2. **Zero-length removal**: Entities with `start == end`
3. **Single-char SKILL removal**: Since they're usually errors
4. **Section header fix**: Removes SKILL labels from words like "Skills", "Education"
5. **Overlap resolution**: Resolves overlapping entities (prefers longer ones)
6. **Whitespace cleanup**

Reads `annotated.jsonl` and writes the corrected version + a stats file `fix_stats.json`. Latest stats: 4,291 input records → 2,709 records after fixing and cleaning.

### `audit_annotations.py` — Quality Audit

Inspects annotated data and detects 5 error patterns:
1. **`entity_bio_mismatch`**: `I-` tag without a preceding `B-` of the same type
2. **`overlapping_entities`**: Entities with overlapping boundaries
3. **`repetition_inconsistency`**: Same text labeled with different types across different records
4. **`suspicious_length`**: Entities too long or single character
5. **`boundary_errors`**: Entities starting/ending with whitespace or punctuation

Produces `audit_report.json` with detailed statistics. The latest report showed a 61.9% error rate in raw data (before cleaning by `fix_annotations.py`).

### `split.py` — Data Splitting

Splits data into train/val/test with configurable ratios (default: 80/10/10). Uses **entity-stratified splitting**: computes entity types present in each record and creates an "entity fingerprint" to ensure balanced distribution across all three splits.

### `evaluate.py` — Model Evaluation

Loads a trained model and test dataset, runs evaluation, and prints:
- F1, Precision, Recall (overall)
- Detailed classification report per entity type

```bash
python scripts/evaluate.py --model models/checkpoints/best_model --data data/processed/test.jsonl
```

### `extract_texts.py` — Text Extraction

Extracts raw texts from multiple sources:
- **PDF** via `PyMuPDF` (`fitz`)
- **DOCX** via `python-docx`
- **Annotated JSON** from Kaggle NER and HuggingFace Annotated Resumes

Collects texts into a single JSONL file for passing to `annotate.py`.

### `pack_colab.py` — Colab Preparation

Creates a ZIP archive containing:
- `configs/`
- `src/`
- `scripts/`
- `data/processed/` (JSONL files)
- `train.ipynb` notebook
- `requirements.txt`

Excludes: large models, raw data, gazetteers, and taxonomies. Saves as `viora_ner_colab.zip`.

---

## Tests (`tests/`)

### `test_labels.py`
- Verifies `NUM_LABELS == 17`
- Verifies each entity type produces `B-` and `I-` tags
- Verifies `LABEL2ID` and `ID2LABEL` are inverse mappings

### `test_data_quality.py`
- Reads train/val/test files and verifies:
  - Each record contains `tokens` and `bio_tags` keys
  - `tokens` length equals `bio_tags` length
  - All labels exist in `BIO_LABELS`
  - No broken BIO sequences

### `test_pipeline.py`
- Creates dummy data and tests the complete pipeline:
  - Tokenization and label alignment
  - Trainer construction without errors
  - One training step without crashing

### `test_cv.py`
- Accepts a file path (PDF/DOCX/TXT) via command line
- Extracts text then runs `NERPipeline`
- Prints detected entities with their positions and confidence scores

```bash
python tests/test_cv.py path/to/resume.pdf
```

---

## Data

### Processed Data (`data/processed/`)

| File | Description | Size |
|---|---|---|
| `annotated.jsonl` | Annotated data after cleaning | 57 MB |
| `train_augmented.jsonl` | Training data after augmentation | 326 MB |
| `train.jsonl` | Training split | — |
| `val.jsonl` | Validation split | — |
| `test.jsonl` | Test split | — |
| `label_info.json` | Entity types, BIO labels, and mappings | — |
| `fix_stats.json` | Annotation fixing stats (4291→2709) | — |
| `audit_report.json` | Quality audit report (61.9% raw errors) | — |

Format for each line in JSONL files:
```json
{"tokens": ["John", "Smith", "is", "a", "Software", "Engineer"],
 "bio_tags": ["B-PERSON", "I-PERSON", "O", "O", "B-JOB_TITLE", "I-JOB_TITLE"]}
```
Or:
```json
{"text": "John Smith is a Software Engineer",
 "entities": [[0, 10, "PERSON"], [16, 33, "JOB_TITLE"]]}
```

### Raw Data (`data/raw/`)

#### Kaggle NER (`kaggle_ner/`)
- **`train.json`** (63 MB): NER dataset containing 5,960 resume samples from 4 original sources with 14 entity categories (including broader categories that were mapped to our 8)
- **`sample.json`**: 5 preview examples — each containing a full resume text with an `annotations` list in `[start, end, label]` format

#### HuggingFace Annotated Resumes (`hf_annotated_resumes/ResumesJsonAnnotated/`)
- Approximately **3,500+ individual JSON files** in `cv (N)_annotated.json` format
- Each file contains a resume text with its annotations
- Some files are empty (31 bytes only) or very small
- Some are large (>100 KB) containing detailed resumes

### Gazetteers (`data/gazetteers/`)

| File | Contents | Size |
|---|---|---|
| `skills_gazetteer.json` | Thousands of skills from O*NET + ESCO | 808 KB |
| `job_titles_gazetteer.json` | Hundreds of job titles from O*NET + ESCO | 141 KB |

### Taxonomy (`data/taxonomy/`)

#### O*NET (`onet/`) — Occupational Information Network

5 tab-delimited files, all from the O*NET database:

##### 1. `occupations.txt` — Occupations (0.25 MB)
- **Columns (3):** `O*NET-SOC Code` | `Title` | `Description`
- **1,016 unique occupations** with SOC codes (e.g., `11-1011.00` = Chief Executives)
- Covers all sectors: management, technology, healthcare, engineering, education, military, transportation...
- Each record contains a detailed description of the occupation's tasks

##### 2. `skills.txt` — Skills (5.38 MB, 62,581 lines)
- **Columns (13):** `O*NET-SOC Code` | `Element ID` | `Element Name` | `Scale ID` | `Data Value` | `N` | `Standard Error` | `Lower CI Bound` | `Upper CI Bound` | `Recommend Suppress` | `Not Relevant` | `Date` | `Domain Source`
- **894 occupations × 35 skills × 2 scales** = quantitative data for importance and level of each skill per occupation
- **Two scales:**
  - `IM` (Importance): How important the skill is for the occupation (1-5)
  - `LV` (Level): Required skill level (0-7)
- **The 35 skills:**
  - **Content:** Reading Comprehension, Active Listening, Writing, Speaking, Mathematics, Science
  - **Process:** Critical Thinking, Active Learning, Learning Strategies, Monitoring
  - **Social:** Social Perceptiveness, Coordination, Persuasion, Negotiation, Instructing, Service Orientation
  - **Problem Solving:** Complex Problem Solving
  - **Technical:** Operations Analysis, Technology Design, Equipment Selection, Installation, Programming, Operations Monitoring, Operation and Control, Equipment Maintenance, Troubleshooting, Repairing, Quality Control Analysis
  - **Systems:** Judgment and Decision Making, Systems Analysis, Systems Evaluation
  - **Resource Management:** Time Management, Management of Financial Resources, Management of Material Resources, Management of Personnel Resources

##### 3. `abilities.txt` — Abilities (8.16 MB, 92,977 lines)
- **Same column structure (13)** as the skills file
- **894 occupations × 52 abilities × 2 scales**
- **The 52 abilities:**
  - **Cognitive:** Oral Comprehension, Written Comprehension, Oral Expression, Written Expression, Fluency of Ideas, Originality, Problem Sensitivity, Deductive Reasoning, Inductive Reasoning, Information Ordering, Category Flexibility, Mathematical Reasoning, Number Facility, Memorization, Perceptual Speed, Flexibility of Closure, Speed of Closure, Spatial Orientation, Visualization, Selective Attention, Time Sharing
  - **Psychomotor:** Arm-Hand Steadiness, Manual Dexterity, Finger Dexterity, Control Precision, Multilimb Coordination, Response Orientation, Rate Control, Reaction Time, Wrist-Finger Speed, Speed of Limb Movement
  - **Physical:** Static Strength, Explosive Strength, Dynamic Strength, Trunk Strength, Stamina, Extent Flexibility, Dynamic Flexibility, Gross Body Coordination, Gross Body Equilibrium
  - **Sensory:** Near Vision, Far Vision, Visual Color Discrimination, Night Vision, Peripheral Vision, Depth Perception, Glare Sensitivity, Hearing Sensitivity, Auditory Attention, Sound Localization, Speech Recognition, Speech Clarity

##### 4. `knowledge.txt` — Knowledge Areas (5.35 MB, 59,005 lines)
- **Same column structure (13)**
- **894 occupations × 33 knowledge areas × 2 scales**
- **The 33 knowledge areas:** Administration and Management, Administrative, Biology, Building and Construction, Chemistry, Communications and Media, Computers and Electronics, Customer and Personal Service, Design, Economics and Accounting, Education and Training, Engineering and Technology, English Language, Fine Arts, Food Production, Foreign Language, Geography, History and Archeology, Law and Government, Mathematics, Mechanical, Medicine and Dentistry, Personnel and Human Resources, Philosophy and Theology, Physics, Production and Processing, Psychology, Public Safety and Security, Sales and Marketing, Sociology and Anthropology, Telecommunications, Therapy and Counseling, Transportation

##### 5. `technology_skills.txt` — Technology Skills & Tools (2.48 MB, 32,774 lines)
- **Columns (6):** `O*NET-SOC Code` | `Example` | `Commodity Code` | `Commodity Title` | `Hot Technology` | `In Demand`
- **923 occupations** linked to **8,785 unique tools/software** classified in **137 technology categories**
- **11,526 entries flagged as Hot Technology** (trending technologies)
- **2,493 entries flagged as In Demand** (market demand)
- **Sample categories:** Accounting software, Analytical or scientific software, Business intelligence and data analysis software, Cloud-based management software, Computer aided design CAD software, Configuration management software, Database management system software...
- **Sample tools:** Python, JavaScript, SAP, Salesforce, Microsoft Excel, AutoCAD, Docker, Kubernetes, AWS, Adobe Creative Suite...

#### ESCO (`esco/ESCO dataset - v1.2.1 - classification - en - csv/`) — European Classification

19 CSV files from the ESCO (European Skills, Competences, Qualifications and Occupations) project, version 1.2.1:

| File | Lines | Size | Columns | Description |
|---|---|---|---|---|
| `skills_en.csv` | 104,065 | 9.1 MB | 13 | Skills and competences (conceptType, skillType, preferredLabel, altLabels, definition...) |
| `occupations_en.csv` | 35,204 | 3.0 MB | 15 | Occupations (conceptType, iscoGroup, preferredLabel, altLabels, definition, code, naceCode...) |
| `occupationSkillRelations_en.csv` | 126,052 | 27.3 MB | 6 | Occupation-skill relations (occupationLabel, relationType: essential/optional, skillLabel) |
| `broaderRelationsSkillPillar_en.csv` | 20,820 | 4.8 MB | 6 | Hierarchical skill relations |
| `conceptSchemes_en.csv` | 13,106 | 919 KB | 7 | Concept schemes |
| `ISCOGroups_en.csv` | 9,025 | 944 KB | 8 | ISCO international classification groups |
| `skillSkillRelations_en.csv` | 5,819 | 1.0 MB | 5 | Skill-to-skill relations |
| `skillGroups_en.csv` | 3,529 | 333 KB | 11 | Skill groups |
| `broaderRelationsOccPillar_en.csv` | 3,649 | 713 KB | 6 | Hierarchical occupation relations |
| `greenShareOcc_en.csv` | 3,591 | 442 KB | 5 | Green (environmental) occupations |
| `skillsHierarchy_en.csv` | 2,505 | 373 KB | 14 | Complete skills hierarchy |
| `digitalSkillsCollection_en.csv` | 1,285 | 792 KB | 10 | Digital skills collection |
| `greenSkillsCollection_en.csv` | 630 | 445 KB | 10 | Green skills collection |
| `languageSkillsCollection_en.csv` | 360 | 141 KB | 10 | Language skills collection |
| `dictionary_en.csv` | 185 | 19 KB | 4 | Terminology dictionary |
| `researchOccupationsCollection_en.csv` | 123 | 124 KB | 8 | Research occupations |
| `transversalSkillsCollection_en.csv` | 96 | 56 KB | 10 | Transversal skills |
| `researchSkillsCollection_en.csv` | 41 | 26 KB | 10 | Research skills |
| `digCompSkillsCollection_en.csv` | 26 | 18 KB | 10 | DigComp digital competence framework |

**Three key files used by `build_gazetteer.py`:**
- `skills_en.csv`: Extracts `preferredLabel` and `altLabels` columns to build the skills dictionary
- `occupations_en.csv`: Extracts `preferredLabel` and `altLabels` to build the job titles dictionary
- `occupationSkillRelations_en.csv`: Links each occupation to its skills (essential or optional) via `skillLabel`

---

## Training Configuration (`configs/train.yaml`)

| Parameter | Value | Description |
|---|---|---|
| `model_name` | `roberta-base` | Base model (125M parameters) |
| `max_length` | `512` | Maximum token length |
| `stride` | `128` | Sliding window step |
| `epochs` | `15` | Number of training epochs |
| `per_device_train_batch_size` | `8` | Training batch size |
| `per_device_eval_batch_size` | `16` | Evaluation batch size |
| `gradient_accumulation_steps` | `4` | Gradient accumulation (effective batch = 32) |
| `learning_rate` | `3e-5` | Learning rate |
| `warmup_ratio` | `0.1` | Warmup ratio |
| `weight_decay` | `0.01` | Weight decay |
| `max_grad_norm` | `1.0` | Gradient clipping |
| `lr_scheduler_type` | `linear` | Learning rate scheduler |
| `use_weighted_loss` | `false` | Weighted loss (disabled by default) |
| `o_class_weight` | `0.3` | Weight for O class (when enabled) |
| `label_smoothing_factor` | `0.1` | Label smoothing factor |
| `early_stopping_patience` | `5` | Early stopping patience (epochs) |
| `metric_for_best_model` | `eval_f1` | Metric for best model selection |
| `save_total_limit` | `3` | Maximum checkpoints retained |
| `use_crf` | `false` | CRF layer (disabled) |
| `seed` | `42` | Random seed |

---

## Trained Model

### Model Files (`models/checkpoints/best_model/`)

| File | Size | Description |
|---|---|---|
| `model.safetensors` | 496 MB | Model weights (safetensors) |
| `config.json` | 1.4 KB | Architecture configuration |
| `tokenizer.json` | — | Fast tokenizer file |
| `tokenizer_config.json` | — | Tokenizer settings |
| `training_args.bin` | — | Saved training arguments |

### Architecture (from `config.json`)

- **Type**: `RobertaForTokenClassification`
- **Layers**: 12 transformer layers
- **Attention heads**: 12
- **Hidden size**: 768
- **Intermediate size**: 3,072
- **Vocabulary size**: 50,265
- **Max positions**: 514
- **Number of labels**: 17 (defined in `id2label`/`label2id`)
- **Activation**: GELU
- **Dropout**: 0.1 (attention + hidden)

### Exported Models (`models/exported/`)

- `onnx/` — ONNX model in float32 format
- `onnx_quantized/` — ONNX model with dynamic INT8 quantization (size ~4× smaller)

---

## Complete Data Pipeline

```
[Raw Data]
    ├── Kaggle NER (train.json: 5,960 samples, 14 categories)
    └── HuggingFace Resumes (~3,500+ JSON files)
         │
         ▼
[extract_texts.py] → Raw texts JSONL
         │
         ▼
[annotate.py] → Annotation via Groq LLM → annotated.jsonl (57 MB)
         │
         ▼
[audit_annotations.py] → Quality report (61.9% errors)
         │
         ▼
[fix_annotations.py] → Auto-fix (4,291 → 2,709 records)
         │
         ▼
[split.py] → Stratified split → train.jsonl + val.jsonl + test.jsonl
         │
         ▼
[augment_data.py] → Data augmentation → train_augmented.jsonl (326 MB)
         │
         ▼
[build_gazetteer.py] → Gazetteers from O*NET + ESCO
         │
         ▼
[train.py] → Fine-tune roberta-base → best_model/
         │
         ▼
[evaluate.py] → Evaluate F1/Precision/Recall
         │
         ▼
[export_onnx.py] → ONNX + INT8 quantization
         │
         ▼
[inference.py / test_cv.py] → Inference on real resumes
```

---

## Usage

> ⚠️ **Note**: The following commands are for **retraining or modifying the model**.
> If you just want to run the Viora app, see the [Main README](../../README_EN.md#-step-by-step-setup).

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Train Locally
```bash
python scripts/train.py --config configs/train.yaml
```

### Train on Google Colab
```bash
# 1. Pack the project archive
python scripts/pack_colab.py

# 2. Upload viora_ner_colab.zip to Google Drive

# 3. Open notebooks/train.ipynb in Colab and run all cells
```

The Colab notebook contains 8 cells:
1. Mount Google Drive
2. Install libraries
3. Unzip project files
4. Set working directory
5. Run tests
6. Start training
7. Display results (F1, Precision, Recall, training time)
8. Save model to Drive

### Test on a Resume
```bash
python tests/test_cv.py path/to/resume.pdf
python tests/test_cv.py path/to/resume.docx
```

### Evaluate
```bash
python scripts/evaluate.py --model models/checkpoints/best_model --data data/processed/test.jsonl
```

### Run All Tests
```bash
python -m pytest tests/ -v
```

### Export to ONNX
```python
from src.export_onnx import export_to_onnx

export_to_onnx(
    model_path="models/checkpoints/best_model",
    output_dir="models/exported/onnx",
    quantize=True  # For INT8 quantization
)
```

---

## Required Libraries

| Library | Purpose |
|---|---|
| `torch` | Deep learning framework |
| `transformers` | HuggingFace models (RoBERTa) |
| `datasets` | HuggingFace datasets |
| `seqeval` | Entity-level NER evaluation metrics |
| `pyyaml` | YAML configuration file reading |
| `accelerate` | Training acceleration |
| `sentencepiece` | Subword tokenization |
| `PyMuPDF` (`fitz`) | PDF text extraction |
| `python-docx` | DOCX text extraction |
| `pytest` | Running tests |
| `optimum[onnxruntime]` | ONNX export and quantization |
| `groq` | Groq API interface for annotation |
| `numpy` | Numerical operations |
| `scikit-learn` | Stratified splitting |
