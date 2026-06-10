# Resume Agent

AI-powered tailored resume builder with ATS optimization, GitHub analysis, and company research.

## Tech Stack Overview

| Technology | Version | Badge |
|------------|---------|-------|
| [Gemini 2.5 Flash](https://cloud.google.com/vertex-ai/docs/generative-ai/learn/models#gemini-2-5-flash) | 2.5 Flash | ![Gemini](https://img.shields.io/badge/Gemini-2.5%20Flash-FFB100?logo=google) |
| [Pydantic v2](https://docs.pydantic.dev/latest/) | v2 | ![Pydantic](https://img.shields.io/badge/Pydantic-v2-ff69b4?logo=pydantic) |
| [sentence-transformers (all-MiniLM-L6-v2)](https://www.sbert.net/) | all-MiniLM-L6-v2 | ![Sentence Transformers](https://img.shields.io/badge/sentence--transformers-all--MiniLM--L6--v2-2b5c85?logo=python) |
| [pdfplumber](https://github.com/jsvine/pdfplumber) | latest | ![pdfplumber](https://img.shields.io/badge/pdfplumber-latest-2b5c85?logo=github) |
| [PyGithub](https://pygithub.readthedocs.io/) | latest | ![PyGithub](https://img.shields.io/badge/PyGithub-latest-2b5c85?logo=github) |
| [Serper.dev](https://serper.dev/) | latest | ![Serper.dev](https://img.shields.io/badge/Serper.dev-latest-2b5c85?logo=google) |
| [Jinja2](https://palletsprojects.com/p/jinja/) + [LaTeX](https://www.latex-project.org/) | latest | ![Jinja2](https://img.shields.io/badge/Jinja2-latest-2b5c85?logo=jinja) |
| [FastAPI](https://fastapi.tiangolo.com/) + [Uvicorn](https://www.uvicorn.org/) | latest | ![FastAPI](https://img.shields.io/badge/FastAPI-latest-2b5c85?logo=fastapi) |
| [Streamlit](https://streamlit.io/) | latest | ![Streamlit](https://img.shields.io/badge/Streamlit-latest-FF4B4B?logo=streamlit) |
| [Loguru](https://github.com/Delgan/loguru) | latest | ![Loguru](https://img.shields.io/badge/Loguru-latest-2b5c85?logo=github) |

## What It Does

1. **Parses** your job description and resume into structured data
2. **Researches** the target company (tech stack, culture, hiring signals)
3. **Analyzes** your GitHub projects for JD relevance
4. **Scores** your resume against ATS criteria (keyword match + semantic similarity)
5. **Optimizes** weak sections with LLM-powered rewriting
6. **Generates** a professional LaTeX PDF resume

## Tech Stack

![NumPy](https://img.shields.io/badge/NumPy-1.24%2B-013243?logo=numpy)
![TorchVision](https://img.shields.io/badge/TorchVision-0.17%2B-EE4C2C?logo=pytorch)
![Gmail API](https://img.shields.io/badge/Gmail_API-v1-EA4335?logo=gmail)
![Google OAuth 2.0](https://img.shields.io/badge/OAuth_2.0-Google-4285F4?logo=google)
![Jinja2](https://img.shields.io/badge/Jinja2-3.1%2B-B41717)
![HTML5](https://img.shields.io/badge/HTML5-E34F26?logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?logo=css3&logoColor=white)
![Gunicorn](https://img.shields.io/badge/Gunicorn-WSGI-499848)
![Roboflow](https://img.shields.io/badge/Roboflow-PPE_Dataset-6706CE)
![Google Cloud](https://img.shields.io/badge/Google_Cloud-Gmail_API-4285F4?logo=googlecloud)


## Project Structure

```
resume-agent/
├── src/
│   ├── main.py                          # FastAPI entry point (uvicorn)
│   ├── core/
│   │   ├── config.py                    # Central settings (env vars)
│   │   └── gemini_client.py             # Gemini API wrapper
│   ├── models/
│   │   ├── common.py                    # Base schema, enums
│   │   ├── jd.py                        # JobDescription model
│   │   ├── resume.py                    # ParsedResume model
│   │   ├── github.py                    # GitHubProject model
│   │   ├── ats.py                       # ATSReport model
│   │   └── tailored_resume.py           # TailoredResume model
│   ├── services/
│   │   ├── orchestrator.py              # Pipeline manager
│   │   ├── embeddings.py                # Local embedding service
│   │   ├── latex_resume.py              # LaTeX/Jinja2 renderer
│   │   ├── agents/
│   │   │   ├── jd_parser.py             # JD parsing agent
│   │   │   ├── resume_parser.py         # Resume parsing agent
│   │   │   ├── github_analyzer.py       # GitHub analysis agent
│   │   │   ├── ats_scorer.py            # ATS scoring agent
│   │   │   ├── resume_optimizer.py      # Resume optimization agent
│   │   │   └── company_research.py      # Company research agent
│   │   ├── prompts/                     # LLM prompt templates
│   │   └── templates/
│   │       └── resume.tex.j2            # LaTeX resume template
│   ├── api/
│   │   └── routes.py                    # REST API endpoints
│   └── utils/
│       └── decorators.py                # Reusable retry/logging decorators
├── ui/
│   └── app.py                           # Streamlit frontend
├── docs/                                # Phase documentation
├── pyproject.toml                       # Dependencies & tooling config
└── .env                                 # API keys (not committed)
```

## Setup

```bash
# 1. Clone and enter project
cd resume-agent

# 2. Create virtual environment
python -m venv .venv
.venv\Scripts\activate   # Windows

# 3. Install dependencies
pip install -e .

# 4. Configure environment
# Edit .env with your API keys:
#   GEMINI_API_KEY=your_key
#   GITHUB_TOKEN=your_token      (optional)
#   SERPER_API_KEY=your_key      (optional)
```

## Running

### API Server
```bash
cd src
uvicorn main:app --reload --port 8000
```

### Streamlit UI
```bash
streamlit run ui/app.py
```

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| POST | `/api/parse-jd` | Parse a job description |
| POST | `/api/parse-resume/text` | Parse resume from text |
| POST | `/api/parse-resume/pdf` | Parse resume from PDF upload |
| POST | `/api/generate` | Full pipeline (text inputs) |
| POST | `/api/generate/upload` | Full pipeline with PDF upload |

## Architecture

```mermaid
graph LR
    UI["User Input (JD + Resume + GitHub)"] --> JD["JD Parser"]
    JD --> RP["Resume Parser"]
    RP --> PR["Parallel Research"]
    PR --> CR["Company Research"]
    PR --> GA["GitHub Analysis"]
    PR --> ASA["ATS Semantic Analysis"]
    CR --> AG["ATS Gap Analysis"]
    GA --> AG
    ASA --> AG
    AG --> RO["Resume Optimizer"]
    RO --> AR["ATS Re-Score"]
    AR --> LG["LaTeX Generation"]
    LG --> PDF["PDF"]
```