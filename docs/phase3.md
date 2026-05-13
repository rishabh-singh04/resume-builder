---

# Sequential Implementation Plan

The project should be built in phases.

Each phase must produce a runnable artifact.

Avoid building everything simultaneously.

Rule:

```text
Build → Test → Stabilize → Move Forward
```

---

# Phase 1 — Foundation Layer (MVP)

Estimated Time:

```text
2–3 Days
```

Goal:

```text
JD + Resume → Structured JSON
```

Deliverable:

A functioning parser pipeline.

---

## Step 1 — Setup Project

Create repository:

```bash
mkdir ai-resume-builder

cd ai-resume-builder
```

Initialize:

```bash
git init
```

Install dependencies.

Setup:

```text
.env
```

Create modular structure.

---

## Step 2 — Configure Gemini Client

Create:

```text
utils/gemini_client.py
```

Responsibilities:

- API calls
- Retry logic
- JSON response handling
- Rate limiting

Example:

```python
import google.generativeai as genai
from app.config import settings


genai.configure(api_key=settings.GEMINI_API_KEY)


model = genai.GenerativeModel(
    settings.MODEL_NAME
)


def generate_response(prompt: str):
    response = model.generate_content(prompt)
    return response.text
```

---

## Step 3 — Create Pydantic Schemas

Create:

```text
models/
```

This is the backbone of the system.

Never pass raw dictionaries between services.

Always use typed models.

Example:

```python
from pydantic import BaseModel
from typing import List


class JobDescription(BaseModel):
    role: str
    seniority: str
    required_skills: List[str]
    preferred_skills: List[str]
    responsibilities: List[str]
    keywords: List[str]
```

---

## Step 4 — Build JD Parser

File:

```text
services/jd_parser.py
```

Responsibilities:

- Parse JD
- Extract keywords
- Detect seniority
- Identify hidden requirements

Input:

```text
Raw JD
```

Output:

```python
JobDescription
```

Execution:

```text
raw JD
   ↓
Gemini
   ↓
structured JSON
   ↓
Pydantic validation
```

Checkpoint:

You should now have:

```text
JD → JSON
```

working reliably.

---

## Step 5 — Build Resume Parser

File:

```text
services/resume_parser.py
```

Responsibilities:

Extract:

- experience
- projects
- education
- certifications
- skills

Pipeline:

```text
PDF
 ↓
pdfplumber
 ↓
raw text
 ↓
Gemini normalization
 ↓
structured schema
```

Example Schema:

```python
class WorkExperience(BaseModel):
    company: str
    role: str
    duration: str
    bullet_points: list[str]


class Resume(BaseModel):
    summary: str
    skills: list[str]
    work_experience: list[WorkExperience]
    education: list[str]
    projects: list[str]
```

Checkpoint:

Working:

```text
Resume PDF → JSON
```

---

# Phase 2 — Intelligence Layer

Estimated Time:

```text
2–4 Days
```

Goal:

```text
Research + Analysis
```

Deliverable:

Rich research packet.

---

## Step 6 — Build Embedding Pipeline

File:

```text
utils/embeddings.py
```

Load model once.

Example:

```python
from sentence_transformers import SentenceTransformer


model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


def generate_embedding(text):
    return model.encode(text)
```

Why?

Avoid repeated loading.

Loading model repeatedly slows inference.

---

## Step 7 — GitHub Analyzer

File:

```text
services/github_analyzer.py
```

Responsibilities:

- fetch repos
- analyze README
- extract technologies
- rank relevance

Pipeline:

```text
GitHub Username
      ↓
PyGithub
      ↓
Fetch Repositories
      ↓
README extraction
      ↓
Embedding Similarity
      ↓
Gemini enrichment
      ↓
Scored Projects
```

Example Output:

```json
[
  {
    "project": "AI Resume Builder",
    "score": 91,
    "tech_stack": [
      "Python",
      "Gemini",
      "FastAPI"
    ]
  }
]
```

---

## Step 8 — Company Research

File:

```text
services/company_research.py
```

Responsibilities:

Research:

- engineering blog
- hiring patterns
- technologies
- architecture hints

Example Query:

```text
"{company_name} engineering blog"
```

Use:

```text
duckduckgo-search
```

Output:

```python
CompanyResearch(
    company_name="",
    technologies=[],
    culture_keywords=[],
    engineering_focus=[]
)
```

---

## Step 9 — ATS Scorer

File:

```text
services/ats_scorer.py
```

Responsibilities:

Calculate:

### 1. Keyword Score

Direct match.

Example:

```text
Python ✓
Docker ✓
Kubernetes ✗
```

### 2. Semantic Match

Embedding similarity.

Example:

```text
"Built REST APIs"

≈

"Developed scalable backend APIs"
```

### 3. Section Strength

Check:

- weak bullets
- missing metrics
- passive language

Formula:

```text
ATS Score =
40% keyword score
+ 40% semantic score
+ 20% resume quality
```

Example:

```json
{
  "ats_score": 84,
  "missing_keywords": [
    "Docker",
    "CI/CD"
  ],
  "weak_sections": [
    "Projects"
  ]
}
```

Checkpoint:

You should now have:

```text
JD + Resume
      ↓
Research
      ↓
ATS Analysis
```

---

# Phase 3 — Optimization Layer

Estimated Time:

```text
2–3 Days
```

Goal:

```text
Rewrite intelligently
```

Deliverable:

Tailored resume.

---

## Step 10 — Resume Optimizer

File:

```text
services/resume_optimizer.py
```

Responsibilities:

- rewrite bullets
- prioritize skills
- insert keywords naturally
- improve impact

Rules:

### Never hallucinate

Never invent:

- companies
- numbers
- metrics
- technologies

### Rewrite for impact

Weak:

```text
Worked on backend APIs.
```

Strong:

```text
Developed scalable REST APIs
using Python, reducing latency
through optimized request handling.
```

### Prioritize relevance

Most relevant projects first.

---

## Step 11 — Optimization Feedback Loop

Pipeline:

```text
Optimize Resume
       ↓
ATS Score
       ↓
Below threshold?
       ↓
Yes → Optimize Again
No → Continue
```

Threshold:

```text
85
```

Maximum retries:

```text
3
```

Pseudo Flow:

```python
score = 0
attempt = 0


while score < 85 and attempt < 3:
    resume = optimize_resume()
    score = score_resume()
    attempt += 1
```

Checkpoint:

You now have:

```text
ATS Optimized Resume
```

---

# Phase 4 — Resume Generation

Estimated Time:

```text
1–2 Days
```

Goal:

```text
Professional PDF
```

Deliverable:

```text
.tex + PDF
```

---

## Step 12 — Build Jinja2 Resume Template

Location:

```text
templates/resume.tex.j2
```

Why Jinja2?

Separation:

```text
Logic ≠ Presentation
```

Cleaner.

Maintainable.

---

## Step 13 — Generate TEX

File:

```text
services/latex_generator.py
```

Pipeline:

```text
optimized JSON
      ↓
Jinja2
      ↓
.tex file
```

Output:

```text
resume.tex
```

---

## Step 14 — Compile PDF

File:

```text
services/pdf_generator.py
```

Use:

```python
subprocess.run()
```

Example:

```bash
latexmk -pdf resume.tex
```

Why latexmk?

Handles:

- retries
- references
- compile consistency

Checkpoint:

You now have:

```text
Resume PDF Generated
```

---

# Async Orchestration Strategy

We intentionally use:

```text
AsyncIO
```

instead of orchestration frameworks.

Why?

Faster.

Cleaner.

Less abstraction.

---

## Parallel Layer

Run together:

```text
Company Research
GitHub Analysis
ATS Analysis
```

Example:

```python
results = await asyncio.gather(
    company_research(),
    github_analysis(),
    ats_score()
)
```

Benefit:

Instead of:

```text
45–60 seconds
```

runtime becomes:

```text
15–20 seconds
```

---

# Orchestrator Flow

File:

```text
orchestrator/pipeline.py
```

Pipeline:

```text
parse_jd()
      ↓
parse_resume()
      ↓
parallel_research()
      ↓
score_resume()
      ↓
optimize_resume()
      ↓
score_again()
      ↓
generate_pdf()
```

Single entry point.

Cleaner debugging.

---

# Recommended Build Order

Do NOT build UI first.

Correct order:

```text
Schemas
   ↓
Gemini Client
   ↓
JD Parser
   ↓
Resume Parser
   ↓
Embeddings
   ↓
GitHub Analysis
   ↓
Company Research
   ↓
ATS Scorer
   ↓
Optimizer
   ↓
PDF Generation
   ↓
UI
```

Reason:

```text
Backend first
UI last
```

Prevents rewrites.