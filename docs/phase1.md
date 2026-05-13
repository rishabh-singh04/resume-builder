# AI-Powered Tailored Resume Builder Agent

An intelligent AI-powered system that automatically tailors resumes for specific job descriptions (JD), optimizes ATS compatibility, prioritizes relevant GitHub projects, incorporates company-specific insights, and generates a professional LaTeX-based PDF resume.

The system is designed to reduce manual resume customization effort while increasing interview shortlist probability through intelligent optimization and structured reasoning.

---

# Problem Statement

Job seekers spend significant time manually modifying resumes for every application.

Generic resumes often fail to:

- Pass Applicant Tracking Systems (ATS)
- Match exact job keywords
- Highlight relevant technical projects
- Align with company culture or technology stack
- Showcase the strongest experience for a role

This leads to:

- Low interview conversion rates
- Poor ATS scores
- Irrelevant resume content
- Time-consuming manual edits

The goal of this project is to build an intelligent resume optimization system that:

1. Understands a Job Description deeply
2. Extracts relevant resume content
3. Researches the company and technical stack
4. Matches GitHub projects against the role
5. Optimizes bullet points naturally
6. Improves ATS compatibility
7. Generates a polished professional resume automatically

---

# Goals

The system should:

- Generate tailored resumes in under **2–3 minutes**
- Achieve **80–95% ATS compatibility**
- Highlight highly relevant projects automatically
- Improve keyword coverage naturally
- Maintain truthfulness (no fabricated experience)
- Produce ATS-friendly professional PDFs
- Require minimal manual editing

---

# Key Features

### JD Understanding
- Extract required skills
- Extract role responsibilities
- Identify seniority level
- Detect hidden expectations
- Build keyword map

### Resume Parsing
- Parse uploaded resume PDF
- Extract skills, projects, experience
- Normalize resume structure

### GitHub Intelligence
- Analyze repositories
- Rank relevance against JD
- Extract technical stack
- Surface strongest projects

### Company Research
- Research company stack
- Research engineering culture
- Detect role-specific terminology

### ATS Optimization
- Keyword matching
- Semantic similarity scoring
- Missing keyword detection
- Weak section analysis

### Resume Tailoring
- Rewrite bullets to be achievement-oriented
- Improve keyword coverage naturally
- Prioritize relevant projects
- Maintain factual accuracy

### PDF Generation
- Generate professional LaTeX resume
- Downloadable PDF
- Downloadable `.tex`
- ATS report generation

---

# Why This Architecture?

Instead of using heavy autonomous agent frameworks, this system follows a **deterministic AI workflow architecture**.

### Why not CrewAI?

CrewAI introduces:

- More latency
- More token usage
- Harder debugging
- Unnecessary agent communication

This project is primarily:

```text
Input → Analysis → Optimization → Output
```

rather than:

```text
Agent ↔ Agent ↔ Agent
```

For resume optimization, deterministic workflows are significantly more reliable.

---

# Why not LangChain / LangGraph?

While powerful, they add:

- Framework overhead
- Complex debugging
- Extra abstraction
- Higher maintenance cost

This project benefits more from:

```text
Plain Python + AsyncIO + Pydantic
```

because:

### Advantages

#### Faster
Minimal abstraction overhead.

#### Easier Debugging
Simple function-level debugging.

#### More Predictable
Deterministic execution.

#### Lower Token Usage
No unnecessary multi-agent reasoning loops.

#### Better Production Stability
Fewer moving parts.

#### Easier Interview Explanation
Architecture decisions are easier to justify.

---

# Final Production Architecture

The system uses a **hybrid AI architecture**.

## Architecture Principles

### LLMs for reasoning only
Gemini is used only where intelligence is required.

### Deterministic code for logic
Scoring, orchestration, ranking, retries are deterministic.

### Local embeddings for speed
No embedding API cost.

### Parallel execution
Independent tasks run simultaneously.

---

# Final Tech Stack

| Layer | Technology | Purpose |
|--------|-------------|----------|
| LLM | Gemini 2.5 Flash | Reasoning + rewriting |
| Orchestration | Python AsyncIO | Workflow execution |
| Validation | Pydantic | Structured outputs |
| Embeddings | sentence-transformers | Semantic similarity |
| Embedding Model | all-MiniLM-L6-v2 | Lightweight matching |
| Similarity | cosine similarity | ATS scoring |
| PDF Parsing | pdfplumber | Resume extraction |
| GitHub Integration | PyGithub | Repo analysis |
| Search | DuckDuckGo Search | Company research |
| Template Engine | Jinja2 | Resume templating |
| PDF Generation | LaTeX + latexmk | Professional output |
| UI | Streamlit | Frontend |
| Caching | diskcache | Local cache |
| Logging | Loguru | Observability |
| Containerization | Docker | Deployment |

---

# System Workflow

```text
User Inputs
(JD + Resume + GitHub Username)
            │
            ▼
     Job Description Parser
            │
            ▼
        Resume Parser
            │
            ▼
      Parallel Research Layer
 ┌────────────┬──────────────┬────────────┐
 │            │              │
 ▼            ▼              ▼
Company     GitHub       ATS Semantic
Research    Analysis      Analysis
 │            │              │
 └────────────┴──────────────┘
            │
            ▼
       ATS Gap Analysis
            │
            ▼
      Resume Optimizer
            │
            ▼
      ATS Re-Scoring Loop
      (until score ≥ 85)
            │
            ▼
      LaTeX Resume Builder
            │
            ▼
        PDF Generation
            │
            ▼
Outputs:
- Tailored Resume PDF
- LaTeX File
- ATS Score Report
- Change Log
```

---

# High-Level Execution Flow

## Step 1 — User Uploads Inputs

Inputs:

### Required
- Job Description

### Optional
- Base Resume PDF
- GitHub Username

---

## Step 2 — Parse JD

Gemini extracts:

```json
{
  "role": "",
  "skills_required": [],
  "preferred_skills": [],
  "responsibilities": [],
  "seniority": "",
  "keywords": []
}
```

---

## Step 3 — Parse Resume

Extract:

- Work experience
- Projects
- Education
- Skills
- Certifications

Resume becomes structured JSON.

---

## Step 4 — Parallel Intelligence Layer

Three async jobs run simultaneously.

### Company Research

Research:

- Tech stack
- Engineering culture
- Recent technologies
- Hiring signals

### GitHub Analyzer

Analyze:

- Repository relevance
- Tech stack alignment
- Quantifiable impact

### ATS Semantic Matching

Compute:

- Keyword coverage
- Missing skills
- Semantic relevance

---

## Step 5 — Resume Optimization

Gemini rewrites:

- Bullet points
- Skills ordering
- Project prioritization
- Role alignment

---

## Step 6 — ATS Feedback Loop

Re-score.

If:

```text
ATS Score < 85
```

Retry optimization.

Maximum:

```text
3 iterations
```

---

## Step 7 — Resume Generation

Generate:

```text
.tex
```

Compile:

```text
PDF
```

---

# Performance Optimizations

This system is intentionally lightweight.

### Local embeddings
No embedding API latency.

### Async execution
Research tasks run simultaneously.

### Caching
GitHub + company research cached.

### Focused prompting
No chain-of-thought waste.

### Deterministic orchestration
No agent chaos.

---

# Expected Results

| Metric | Target |
|--------|--------|
| Resume Generation Time | < 3 min |
| ATS Score | 80–95 |
| Optimization Cycles | 1–3 |
| Manual Editing Needed | Minimal |
| Hallucination Risk | Low |

---

# Architecture Decision Summary

**We intentionally avoid heavy AI frameworks.**

Instead:

```text
Gemini
+ Async Python
+ Pydantic
+ Sentence Transformers
+ Jinja2
```

This gives:

- Better speed
- Lower cost
- Easier debugging
- Strong production stability
- Cleaner architecture
- Better maintainability