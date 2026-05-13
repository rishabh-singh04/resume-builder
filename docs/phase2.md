---

# Production Folder Structure

The project follows a modular service-oriented architecture.

```text
ai-resume-builder/
│
├── app/
│   ├── main.py
│   ├── streamlit_app.py
│   └── config.py
│
├── orchestrator/
│   ├── pipeline.py
│   ├── workflow.py
│   └── async_executor.py
│
├── services/
│   ├── jd_parser.py
│   ├── resume_parser.py
│   ├── github_analyzer.py
│   ├── company_research.py
│   ├── ats_scorer.py
│   ├── resume_optimizer.py
│   ├── latex_generator.py
│   └── pdf_generator.py
│
├── prompts/
│   ├── jd_parser_prompt.py
│   ├── github_prompt.py
│   ├── ats_prompt.py
│   ├── optimizer_prompt.py
│   └── company_prompt.py
│
├── models/
│   ├── jd_models.py
│   ├── resume_models.py
│   ├── github_models.py
│   ├── ats_models.py
│   └── output_models.py
│
├── utils/
│   ├── gemini_client.py
│   ├── embeddings.py
│   ├── similarity.py
│   ├── cache.py
│   ├── logger.py
│   ├── retry.py
│   └── helpers.py
│
├── templates/
│   ├── resume.tex.j2
│   └── sections/
│       ├── education.tex
│       ├── experience.tex
│       ├── projects.tex
│       └── skills.tex
│
├── output/
│   ├── generated_pdfs/
│   ├── generated_tex/
│   └── ats_reports/
│
├── cache/
│
├── tests/
│   ├── test_jd_parser.py
│   ├── test_resume_parser.py
│   ├── test_optimizer.py
│   └── test_pipeline.py
│
├── .env
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── README.md
└── .gitignore
```

---

# Why This Structure?

This architecture is intentionally modular.

Each component is:

- Independent
- Testable
- Replaceable
- Production-friendly

For example:

You can swap:

```text
Gemini → OpenAI
```

without changing business logic.

Or:

```text
Streamlit → FastAPI
```

without rewriting orchestration.

---

# Service Responsibilities

## 1. JD Parser

### Purpose
Convert unstructured Job Description into structured JSON.

### Input

```text
Raw JD text
```

### Output

```json
{
  "role": "",
  "skills_required": [],
  "preferred_skills": [],
  "responsibilities": [],
  "keywords": [],
  "seniority": ""
}
```

### Responsibilities

- Extract skills
- Identify hidden requirements
- Detect experience level
- Extract ATS keywords

---

## 2. Resume Parser

### Purpose

Convert uploaded PDF into structured resume data.

### Responsibilities

Extract:

- Work Experience
- Projects
- Skills
- Education
- Certifications

### Pipeline

```text
PDF
  ↓
pdfplumber
  ↓
raw text
  ↓
Gemini normalization
  ↓
structured JSON
```

---

## 3. GitHub Analyzer

### Purpose

Analyze repositories against JD relevance.

### Responsibilities

- Fetch repositories
- Parse README
- Analyze tech stack
- Rank relevance

### Scoring Criteria

| Factor | Weight |
|--------|--------|
| Tech Match | 40% |
| Similarity | 25% |
| Activity | 15% |
| Complexity | 10% |
| Popularity | 10% |

---

## 4. Company Research Service

### Purpose

Understand company context.

### Research Areas

- Engineering culture
- Company tech stack
- Product direction
- Recent engineering news

### Goal

Generate company-specific signals.

Example:

```text
Company values:
"scalable backend systems"

Resume bullet rewrite:
"Built scalable microservices..."
```

---

## 5. ATS Scorer

### Purpose

Estimate ATS compatibility.

### Responsibilities

- Keyword matching
- Semantic scoring
- Missing keyword detection
- Weak section analysis

### Output

```json
{
  "ats_score": 82,
  "missing_keywords": [],
  "weak_sections": [],
  "recommendations": []
}
```

---

## 6. Resume Optimizer

### Purpose

Rewrite resume intelligently.

### Responsibilities

- Improve bullets
- Increase ATS coverage
- Prioritize relevant projects
- Remove weak content
- Maintain factual correctness

---

## 7. LaTeX Generator

### Purpose

Generate professional ATS-safe PDF.

### Responsibilities

- Populate template
- Escape LaTeX characters
- Validate layout
- Generate `.tex`

---

## 8. PDF Compiler

### Purpose

Compile LaTeX safely.

### Engine

```text
latexmk
```

### Why latexmk?

Better than:

```text
pdflatex
```

because:

- retries automatically
- resolves references
- fewer failures

---

# Technology Decisions

## Why Gemini 2.5 Flash?

Used for:

- reasoning
- rewriting
- structured extraction

Benefits:

- long context
- cheaper than larger models
- excellent JSON output
- fast response time

---

## Why Sentence Transformers?

Used for:

- semantic similarity
- repo relevance
- ATS scoring

Recommended model:

```python
all-MiniLM-L6-v2
```

Benefits:

- lightweight
- CPU friendly
- fast inference
- no API cost

---

# Environment Variables

Create:

```text
.env
```

Add:

```env
GEMINI_API_KEY=your_key_here
GITHUB_TOKEN=your_token_here

MODEL_NAME=gemini-2.5-flash

EMBEDDING_MODEL=all-MiniLM-L6-v2

CACHE_DIR=cache/

MAX_OPTIMIZATION_LOOPS=3
ATS_THRESHOLD=85

LOG_LEVEL=INFO
```

---

# Requirements.txt

```txt
google-generativeai
sentence-transformers
scikit-learn
pdfplumber
PyGithub
duckduckgo-search
jinja2
streamlit
pydantic
python-dotenv
diskcache
loguru
numpy
pandas
tenacity
latex
pylatex
```

---

# Installation Guide

## Step 1 — Clone Repository

```bash
git clone https://github.com/your-username/ai-resume-builder.git

cd ai-resume-builder
```

---

## Step 2 — Create Virtual Environment

### Windows

```bash
python -m venv venv

venv\Scripts\activate
```

### Linux / Mac

```bash
python3 -m venv venv

source venv/bin/activate
```

---

## Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Step 4 — Install LaTeX

### Ubuntu

```bash
sudo apt install texlive-full
```

### MacOS

Install:

```text
MacTeX
```

### Windows

Install:

```text
MiKTeX
```

Enable:

```text
latexmk
```

---

## Step 5 — Configure Environment

Create:

```text
.env
```

Add API keys.

---

## Step 6 — Run Application

```bash
streamlit run app/streamlit_app.py
```

---

# First Execution Flow

User uploads:

- Resume PDF
- Job Description
- GitHub username

System:

```text
Parse JD
    ↓
Parse Resume
    ↓
Parallel Research
    ↓
ATS Analysis
    ↓
Optimization
    ↓
PDF Generation
```

Output appears inside:

```text
output/
```

---

# Local Development Commands

### Run Tests

```bash
pytest
```

### Format Code

```bash
black .
```

### Sort Imports

```bash
isort .
```

### Lint

```bash
flake8
```

### Type Check

```bash
mypy .
```

---

# Development Philosophy

This project follows:

```text
Simple > Fancy
Deterministic > Autonomous
Reliable > Complex
Fast > Over-engineered
```