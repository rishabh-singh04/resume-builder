# Resume Builder Source Pipeline Architecture

This document explains the current `src` pipeline logic and how the application flows from API input through parsing, scoring, optimization, and LaTeX generation.

## High-Level Flow

```mermaid
flowchart TD
    A[API Request] --> B[ResumeOrchestrator]
    B --> C1[JD Parser (Gemini)]
    B --> C2[Resume Parser (Gemini)]
    B --> D[Parallel Research]
    D --> D1[GitHub Analyzer (Gemini + repo data)]
    D --> D2[Company Research (Serper/Gemini)]
    B --> E[ATSScorerService]
    E --> F[ResumeOptimizerService]
    F -->|loop until threshold| E
    F --> G[LatexGeneratorService]
    G --> H[Resume TEX Output]
    H --> I[API Response]
    E --> I
    F --> I
    D1 --> F
    D1 --> E
    C1 --> E
    C2 --> E
```

## Core Components

### 1. API Layer (`src/api/routes.py`)
- Thin HTTP layer exposing endpoints such as `/api/generate`, `/api/parse-resume/text`, `/api/parse-resume/pdf`, and `/api/parse-jd`.
- Delegates all business logic to `ResumeOrchestrator` and its agents.

### 2. Orchestrator (`src/services/orchestrator.py`)
- Central coordinator for the full pipeline.
- Responsible for:
  - JD parsing
  - Resume parsing (PDF or raw text)
  - Research tasks in parallel
  - ATS scoring
  - Iterative resume optimization
  - LaTeX generation
- Builds a `PipelineResult` containing `TailoredResume`, ATS report, parsed resume, GitHub projects, and optional TEX path.

### 3. Job Description Parser (`src/services/agents/jd_parser.py`)
- Uses `GeminiClient.structured_generate()` to map raw JD text into `JobDescription`.
- Validates structured output with the Pydantic model.

### 4. Resume Parser (`src/services/agents/resume_parser.py`)
- Extracts text from PDF using `pdfplumber`.
- Uses `GeminiClient.structured_generate()` to parse resume text into `ParsedResume`.

### 5. Parallel Research
- `GitHubAnalyzerService` evaluates a GitHub username and returns resume-relevant projects.
- `CompanyResearchService` gathers company and role insights.
- Both run concurrently via `asyncio` inside the orchestrator.

### 6. ATS Scorer (`src/services/agents/ats_scorer.py`)
- Computes a hybrid score using:
   - exact keyword match
   - semantic similarity (embeddings)
   - keyword placement
   - parsing quality
   - recruiter readability via LLM
   - project relevance
- First attempts structured Gemini ATS scoring with `ATS_SCORING_PROMPT` and then falls back to the deterministic hybrid formula if the LLM path fails.
- Produces an `ATSReport` with category breakdowns and reasoning:
   - `keyword_score`
   - `experience_score`
   - `section_score`
   - `format_score`
   - `impact_score`
   - `score_reasoning`
   - `scoring_method` (`llm` or `fallback`)
   - matched and missing keywords
   - weak sections
   - recommendations
   - optimization priority

### 7. Resume Optimizer (`src/services/agents/resume_optimizer.py`)
- Iteratively calls Gemini to rewrite and improve the resume.
- Each iteration:
   1. Builds a prompt with JD context, ATS gaps, weak sections, recommendations, and selected GitHub projects.
   2. Generates a `TailoredResume` through Gemini.
   3. Re-scores the optimized resume with `ATSScorerService`.
   4. Stops when the score meets `settings.ATS_THRESHOLD`, the improvement delta is too small, or maximum loops are reached.
- Tracks bullet-level changes via `OptimizedBullet`.

### 8. LaTeX Generator (`src/services/latex_resume.py`)
- Renders `TailoredResume` into `resume.tex` using Jinja2 templating.
- Includes escaping for LaTeX special characters.
- Safely continues if LaTeX generation fails.

### 9. Gemini Client Wrapper (`src/core/gemini_client.py`)
- Centralized wrapper for Gemini API usage.
- Provides:
  - `generate()` for raw text
  - `generate_json()` for JSON responses
  - `structured_generate()` for Pydantic-validated structured output
- Handles markdown fence cleanup and retry logic.

## Data Model Boundaries

- `JobDescription` — parsed from JD text.
- `ParsedResume` — structured resume data parsed from PDF/text.
- `GitHubProject` — enriched GitHub repo analysis.
- `ATSReport` — scoring result used for optimization, now including:
   - `keyword_score`, `experience_score`, `section_score`, `format_score`, `impact_score`
   - `score_reasoning`
   - `scoring_method`
- `TailoredResume` — final rewritten resume and output model.

## Pipeline Stages

1. **Input**
   - User sends JD text and either raw resume text or PDF upload.
2. **Parse Phase**
   - JD is parsed into `JobDescription`.
   - Resume is parsed into `ParsedResume`.
3. **Research Phase**
   - GitHub and company research run in parallel.
   - Their outputs inform scoring and optimization.
4. **ATS Scoring Phase**
   - Compute initial ATS report with hybrid scoring.
5. **Optimization Phase**
   - Rewrite the resume via Gemini.
   - Re-score until the performance target is reached.
6. **Render Phase**
   - Convert the final `TailoredResume` into LaTeX.
7. **Response**
   - Return structured `tailored_resume`, `ats_report`, GitHub projects, and generated TEX path.

## Notes on Resilience

- Many Gemini calls are wrapped with `@llm_retry`.
- `ATSScorerService` has fallback default evaluation if LLM resume quality analysis fails.
- LaTeX generation failure is caught and logged without crashing the whole pipeline.

## File Locations

- `src/api/routes.py` — HTTP entrypoint
- `src/services/orchestrator.py` — pipeline coordinator
- `src/services/agents/jd_parser.py` — JD parsing
- `src/services/agents/resume_parser.py` — resume parsing
- `src/services/agents/ats_scorer.py` — scoring logic
- `src/services/agents/resume_optimizer.py` — iterative optimization
- `src/services/latex_resume.py` — TEX generation
- `src/core/gemini_client.py` — LLM wrapper
- `src/models/*.py` — schema definitions

## Diagram Legend

- Boxes represent service components.
- Arrows represent data flow.
- The optimizer loop is the only iterative stage.
- Research is parallelized before scoring.
