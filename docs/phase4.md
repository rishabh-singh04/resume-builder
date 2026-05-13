---

# Prompt Engineering Strategy

The quality of this system depends heavily on prompt design.

A weak prompt produces:

- generic resumes
- poor ATS optimization
- repetitive bullet points
- hallucinated achievements

A strong prompt produces:

- targeted resumes
- better ATS scores
- stronger bullet impact
- role alignment

---

# Prompt Design Principles

All prompts follow these rules:

### 1. Structured Output First

Always force JSON output.

Never allow free-form responses.

Bad:

```text
Explain the JD.
```

Good:

```text
Return structured JSON.
```

---

### 2. No Hallucination Rule

The model must never invent:

- experience
- numbers
- companies
- projects
- metrics
- technologies

Only strengthen wording.

---

### 3. Role-Specific Optimization

Resume must adapt to:

```text
Backend Role
ML Role
AI Engineer Role
Data Engineer Role
Full Stack Role
```

without changing core truth.

---

### 4. ATS Naturalness

Keyword stuffing is forbidden.

Bad:

```text
Python Docker Kubernetes
Python REST APIs Docker
```

Good:

```text
Built scalable Python APIs
deployed using Docker-based workflows.
```

---

# JD Parser Prompt

File:

```text
prompts/jd_parser_prompt.py
```

Purpose:

Convert raw JD into structured data.

Prompt:

```python
JD_PARSER_PROMPT = """
You are an expert job description analyst.

Analyze the provided job description.

Extract:

1. Role title
2. Seniority level
3. Required skills
4. Preferred skills
5. Responsibilities
6. Technologies
7. ATS keywords
8. Hidden expectations

Rules:
- Deduplicate keywords
- Infer implicit requirements
- Keep output factual
- Return JSON only

Schema:

{
    "role": "",
    "seniority": "",
    "required_skills": [],
    "preferred_skills": [],
    "responsibilities": [],
    "technologies": [],
    "keywords": [],
    "hidden_expectations": []
}

Job Description:

{jd}
"""
```

Expected Output:

```json
{
  "role": "AI Backend Engineer",
  "seniority": "Mid-Level",
  "required_skills": [
    "Python",
    "FastAPI",
    "Docker"
  ]
}
```

---

# Resume Parser Prompt

File:

```text
prompts/resume_parser_prompt.py
```

Purpose:

Normalize extracted resume text.

Prompt:

```python
RESUME_PARSER_PROMPT = """
You are a resume parsing expert.

Convert raw resume text into structured JSON.

Extract:

- summary
- skills
- work experience
- projects
- certifications
- education

Rules:
- Preserve wording
- Do not invent content
- Preserve chronology
- Return JSON only

Schema:

{
    "summary": "",
    "skills": [],
    "work_experience": [],
    "projects": [],
    "education": [],
    "certifications": []
}

Resume Text:

{resume_text}
"""
```

---

# GitHub Analyzer Prompt

File:

```text
prompts/github_prompt.py
```

Purpose:

Score repository relevance.

Prompt:

```python
GITHUB_ANALYZER_PROMPT = """
You are an expert technical recruiter.

Evaluate the GitHub repositories
against the target job description.

For each repository:

Evaluate:

1. Technical relevance
2. Complexity
3. Production readiness
4. Resume value
5. ATS relevance

Give:

- score (0–100)
- strengths
- weaknesses
- technologies
- resume suitability

Rules:
- Be strict
- Prioritize JD relevance
- No assumptions

Return JSON only.

Job Description:

{jd}

Repositories:

{repositories}
"""
```

Expected Output:

```json
[
  {
    "repo_name": "resume-builder",
    "score": 92,
    "strengths": [
      "Strong backend architecture"
    ],
    "technologies": [
      "Python",
      "FastAPI"
    ]
  }
]
```

---

# Company Research Prompt

File:

```text
prompts/company_prompt.py
```

Purpose:

Extract meaningful signals.

Prompt:

```python
COMPANY_PROMPT = """
You are an expert company researcher.

Analyze the information.

Identify:

1. Engineering culture
2. Technologies used
3. Product direction
4. Keywords for resume alignment
5. Hiring signals

Return concise structured JSON.

Company Information:

{research_data}
"""
```

---

# ATS Scorer Prompt

File:

```text
prompts/ats_prompt.py
```

Purpose:

Identify weaknesses.

Prompt:

```python
ATS_PROMPT = """
You are an ATS scoring expert.

Compare the resume against
the job description.

Evaluate:

1. Keyword match
2. Semantic relevance
3. Skill alignment
4. Experience relevance
5. Project quality

Return:

{
    "ats_score": 0,
    "missing_keywords": [],
    "weak_sections": [],
    "recommendations": []
}

Rules:
- Be strict
- Be realistic
- Avoid inflated scores

Job Description:

{jd}

Resume:

{resume}
"""
```

---

# Resume Optimizer Prompt

File:

```text
prompts/optimizer_prompt.py
```

This is the most important prompt.

Purpose:

Rewrite intelligently.

Prompt:

```python
OPTIMIZER_PROMPT = """
You are an elite technical resume writer.

Your task is to optimize
the resume for the target role.

Objectives:

1. Improve ATS score
2. Rewrite weak bullet points
3. Increase clarity
4. Prioritize relevant projects
5. Add missing keywords naturally
6. Improve achievement language

STRICT RULES:

- NEVER invent metrics
- NEVER invent experience
- NEVER invent technologies
- NEVER add fake numbers
- NEVER fabricate responsibilities

You may:

- improve phrasing
- reorder sections
- strengthen wording
- improve readability

Rewrite weak content only.

Job Description:

{jd}

Current Resume:

{resume}

ATS Gaps:

{gaps}

Company Signals:

{company_signals}

GitHub Analysis:

{github_analysis}
"""
```

---

# Optimization Strategy

The system optimizes iteratively.

Flow:

```text
Initial ATS Score
        ↓
Find Weak Areas
        ↓
Rewrite Selectively
        ↓
Re-score
        ↓
Repeat Until Threshold
```

Why selective rewriting?

Avoids:

```text
over-optimization
```

which makes resumes sound robotic.

---

# ATS Scoring Strategy

Score Formula:

```text
ATS Score =
40% Keyword Match
+ 35% Semantic Match
+ 15% Project Relevance
+ 10% Resume Quality
```

---

## 1. Keyword Match

Checks:

```text
Exact keywords
```

Example:

JD:

```text
Docker
FastAPI
CI/CD
```

Resume:

```text
Python
FastAPI
Docker
```

Score:

```text
2/3
```

---

## 2. Semantic Match

Embedding similarity.

Example:

Resume:

```text
Built backend APIs
```

JD:

```text
Develop scalable REST services
```

Semantically similar.

---

## 3. Project Relevance

Strong projects improve score.

Example:

AI Engineer role:

Good:

```text
RAG System
LLM Evaluation Framework
```

Weak:

```text
Calculator App
```

---

## 4. Resume Quality

Checks:

- quantified bullets
- strong action verbs
- impact language
- readability

---

# Retry Strategy

Use:

```text
tenacity
```

for retries.

Why?

External APIs fail.

Example:

```python
from tenacity import retry
from tenacity import stop_after_attempt


@retry(stop=stop_after_attempt(3))
def call_gemini(prompt):
    return model.generate_content(prompt)
```

Retry on:

- timeout
- rate limit
- API failure

---

# Logging Strategy

File:

```text
utils/logger.py
```

Use:

```text
Loguru
```

Benefits:

- readable logs
- structured logs
- rotating files

Example:

```python
from loguru import logger


logger.info("JD parsed")
logger.error("PDF failed")
```

Log:

```text
pipeline logs
optimization attempts
API failures
PDF compilation errors
```

---

# Caching Strategy

Use:

```text
diskcache
```

Cache:

### Company Research

Avoid repeated searches.

TTL:

```text
24 hours
```

---

### GitHub Analysis

Avoid rate limits.

TTL:

```text
12 hours
```

---

### Embeddings

Store vectors.

Avoid recomputation.

Benefit:

```text
2–3x faster execution
```

---

# Error Handling Strategy

Every service should fail gracefully.

Bad:

```text
Pipeline crashes
```

Good:

```text
Fallback handling
```

Example:

```text
GitHub fails
```

Continue with:

```text
Resume + JD optimization
```

Example:

```text
Company research unavailable
```

Continue:

```text
without company signals
```

---

# Failure Recovery Matrix

| Failure | Action |
|----------|--------|
| Gemini API Error | Retry |
| GitHub Rate Limit | Cached result |
| PDF Parsing Failure | Retry extraction |
| Company Search Fail | Skip |
| ATS Failure | Fallback scoring |
| LaTeX Error | Recompile |

Goal:

```text
Never fail entire pipeline
```