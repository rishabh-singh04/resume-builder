---

# Streamlit UI Architecture

The UI should remain thin.

Business logic must never live inside:

```text
streamlit_app.py
```

The UI only:

```text
collects inputs
shows progress
renders outputs
downloads files
```

All intelligence belongs in:

```text
services/
```

---

# UI Flow

```text
User Uploads Inputs
        ↓
Validation Layer
        ↓
Generate Button Clicked
        ↓
Pipeline Triggered
        ↓
Live Status Updates
        ↓
Preview Resume
        ↓
Download PDF / TEX / ATS Report
```

---

# Streamlit Layout

### Sidebar

Inputs:

- Gemini API Key (optional local override)
- GitHub Username
- ATS Threshold
- Optimization Attempts

---

### Main Page

Sections:

### 1. Job Description

```text
Paste JD here
```

---

### 2. Resume Upload

```text
Upload PDF
```

---

### 3. Generate Button

```text
Generate Resume
```

---

### 4. Progress Tracking

Show:

```text
✓ Parsing JD
✓ Parsing Resume
✓ Analyzing GitHub
✓ Company Research
✓ ATS Analysis
✓ Optimizing Resume
✓ Generating PDF
```

Use:

```python
st.status()
```

---

### 5. Preview Section

Show:

```text
Optimized Resume
```

Editable:

```python
st.text_area()
```

Human-in-the-loop approval.

---

### 6. Downloads

Buttons:

```text
Download PDF
Download TEX
Download ATS Report
```

---

# Example Streamlit Execution

Run:

```bash
streamlit run app/streamlit_app.py
```

Application:

```text
http://localhost:8501
```

---

# Example Pipeline Execution

Input:

### Job Description

```text
AI Backend Engineer
Python, FastAPI, Docker
RAG, LLM Systems
```

### Resume

```text
resume.pdf
```

### GitHub

```text
github.com/username
```

---

## Output

### ATS Score

```text
89/100
```

### Resume Improvements

```text
✓ Improved backend bullets
✓ Added missing Docker signals
✓ Prioritized AI projects
✓ Strengthened action verbs
✓ Better ATS keyword coverage
```

### Files Generated

```text
resume.pdf
resume.tex
ats_report.md
changelog.md
```

---

# Dockerization

Why Docker?

Benefits:

- reproducible environment
- dependency isolation
- easy deployment
- easier onboarding

---

# Dockerfile

Create:

```text
Dockerfile
```

Add:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD [
  "streamlit",
  "run",
  "app/streamlit_app.py",
  "--server.port=8501",
  "--server.address=0.0.0.0"
]
```

---

# docker-compose.yml

```yaml
version: "3.9"

services:
  ai-resume-builder:
    build: .
    ports:
      - "8501:8501"
    env_file:
      - .env
```

---

# Run with Docker

Build:

```bash
docker compose build
```

Run:

```bash
docker compose up
```

Access:

```text
localhost:8501
```

---

# .gitignore

Create:

```text
.gitignore
```

Add:

```gitignore
venv/
__pycache__/
*.pyc
.env

output/
cache/

.streamlit/

*.aux
*.log
*.out
*.toc
*.fdb_latexmk
*.fls

.idea/
.vscode/

.DS_Store
```

---

# Recommended Development Workflow

Do not build everything together.

Recommended sequence:

### Week 1

Build:

```text
JD Parser
Resume Parser
Pydantic Models
Gemini Client
```

---

### Week 2

Build:

```text
GitHub Analysis
Embeddings
Company Research
ATS Scorer
```

---

### Week 3

Build:

```text
Resume Optimizer
Feedback Loop
Prompt Refinement
```

---

### Week 4

Build:

```text
LaTeX Generator
PDF Compiler
Streamlit UI
```

---

### Week 5

Production hardening:

```text
logging
retries
caching
Docker
tests
```

---

# Testing Strategy

Never test manually only.

Add tests for:

### JD Parser

Check:

```text
keyword extraction accuracy
```

---

### Resume Parser

Check:

```text
PDF parsing consistency
```

---

### ATS Scorer

Check:

```text
score correctness
```

---

### Optimizer

Check:

```text
no hallucination
```

---

### End-to-End Pipeline

Check:

```text
JD → PDF generation
```

Run:

```bash
pytest
```

---

# Security Best Practices

Never expose:

```text
API Keys
```

Always:

```text
.env
```

Never commit:

```text
.env
```

Add:

```text
.env
```

inside:

```text
.gitignore
```

---

# Performance Optimizations

### Use AsyncIO

Parallelize:

```text
GitHub
Company Research
ATS Analysis
```

---

### Cache Everything Possible

Cache:

```text
GitHub Results
Embeddings
Company Search
```

---

### Minimize LLM Calls

Bad:

```text
Many small prompts
```

Good:

```text
Few high-quality prompts
```

---

### Reuse Embedding Model

Load once.

Never:

```python
SentenceTransformer()
```

inside loops.

---

### Avoid Over-Agentification

Do NOT create:

```text
10 talking agents
```

Use:

```text
specialized services
```

instead.

---

# Common Pitfalls

### 1. UI First Development

Wrong:

```text
UI → Backend
```

Correct:

```text
Backend → UI
```

---

### 2. Overusing Gemini

Use Gemini only for:

```text
reasoning
rewriting
structured extraction
```

Avoid:

```text
deterministic logic
```

---

### 3. Hallucinated Resume Content

Never allow:

```text
fake metrics
```

Always enforce:

```text
truthfulness
```

---

### 4. Weak Prompting

Weak prompt:

```text
Improve resume
```

Strong prompt:

```text
Improve ATS score while
preserving factual accuracy
and rewriting weak bullets only.
```

---

# Future Enhancements

### Cover Letter Generator

Auto-generate tailored cover letters.

---

### Multi-Resume Profiles

Different resume personas:

```text
AI Engineer
Backend Engineer
Data Engineer
MLE
```

---

### Resume Version History

Track:

```text
changes over time
```

---

### LinkedIn Optimization

Auto-tailored LinkedIn summary.

---

### Interview Readiness

Generate:

```text
likely interview questions
```

based on JD.

---

### Multi-Language Support

Support:

```text
English
German
French
```

---

### Analytics Dashboard

Track:

```text
applications
ATS scores
response rates
```

---

# Final Engineering Philosophy

This project intentionally avoids unnecessary complexity.

Core principle:

```text
Simple > Clever
Reliable > Fancy
Deterministic > Autonomous
Fast > Over-engineered
```

The system is designed as a:

```text
Production AI Workflow
```

not an:

```text
Autonomous Multi-Agent Experiment
```

This architecture gives:

- Faster execution
- Lower cost
- Better ATS optimization
- Easier debugging
- Lower hallucination risk
- Cleaner production scaling

---

# Final End-to-End Flow

```text
User Input
(JD + Resume + GitHub)
            │
            ▼
        JD Parser
            │
            ▼
      Resume Parser
            │
            ▼
      Async Research Layer
 ┌──────────┬──────────┬──────────┐
 ▼          ▼          ▼
GitHub   Company     ATS
Analysis Research   Analysis
 └──────────┴──────────┘
            │
            ▼
      ATS Gap Report
            │
            ▼
     Resume Optimizer
            │
            ▼
      ATS Re-scoring
     (max 3 iterations)
            │
            ▼
      Resume Generator
            │
            ▼
        PDF Builder
            │
            ▼
         Outputs
```

---

# Author

Built with:

```text
Python + Gemini + AsyncIO + Pydantic
```

for intelligent ATS-optimized resume generation.