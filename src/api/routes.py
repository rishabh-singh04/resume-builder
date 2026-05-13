"""
REST API routes — thin endpoint layer.

No business logic here. All processing is delegated to the orchestrator and services.
"""

import tempfile
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from loguru import logger
from pydantic import BaseModel

from services.orchestrator import ResumeOrchestrator

router = APIRouter(prefix="/api", tags=["Resume Agent"])

# Lazy-initialized orchestrator
_orchestrator: ResumeOrchestrator | None = None


def _get_orchestrator() -> ResumeOrchestrator:
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = ResumeOrchestrator()
    return _orchestrator


# ─────────────────────────────────────────────
# Request / Response Schemas
# ─────────────────────────────────────────────


class ParseJDRequest(BaseModel):
    jd_text: str


class ParseResumeTextRequest(BaseModel):
    resume_text: str


class GenerateRequest(BaseModel):
    jd_text: str
    resume_text: Optional[str] = None
    github_username: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    version: str


# ─────────────────────────────────────────────
# Endpoints
# ─────────────────────────────────────────────


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(status="healthy", version="1.0.0")


@router.post("/parse-jd")
async def parse_jd(request: ParseJDRequest):
    """Parse a job description into structured data."""
    try:
        orchestrator = _get_orchestrator()
        result = orchestrator.jd_parser.parse(request.jd_text)
        return result.model_dump()
    except Exception as e:
        logger.exception("JD parsing failed")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/parse-resume/text")
async def parse_resume_text(request: ParseResumeTextRequest):
    """Parse resume from raw text."""
    try:
        orchestrator = _get_orchestrator()
        result = orchestrator.resume_parser.parse_text(request.resume_text)
        return result.model_dump()
    except Exception as e:
        logger.exception("Resume text parsing failed")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/parse-resume/pdf")
async def parse_resume_pdf(file: UploadFile = File(...)):
    """Parse resume from uploaded PDF."""
    try:
        orchestrator = _get_orchestrator()
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        result = orchestrator.resume_parser.parse_pdf(tmp_path)
        Path(tmp_path).unlink(missing_ok=True)
        return result.model_dump()
    except Exception as e:
        logger.exception("Resume PDF parsing failed")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate")
async def generate_resume(request: GenerateRequest):
    """Full pipeline — parse JD + resume, research, optimize, generate."""
    try:
        orchestrator = _get_orchestrator()
        result = await orchestrator.run_pipeline(
            jd_text=request.jd_text,
            resume_text=request.resume_text,
            github_username=request.github_username,
        )

        return {
            "tailored_resume": result.tailored_resume.model_dump(),
            "ats_report": result.ats_report.model_dump(),
            "github_projects": [p.model_dump() for p in result.github_projects],
            "tex_path": result.tex_path,
        }
    except Exception as e:
        logger.exception("Pipeline failed")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate/upload")
async def generate_resume_with_pdf(
    jd_text: str = Form(...),
    github_username: Optional[str] = Form(None),
    resume_file: UploadFile = File(...),
):
    """Full pipeline with PDF upload instead of text."""
    try:
        orchestrator = _get_orchestrator()

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            content = await resume_file.read()
            tmp.write(content)
            tmp_path = tmp.name

        result = await orchestrator.run_pipeline(
            jd_text=jd_text,
            resume_pdf_path=tmp_path,
            github_username=github_username,
        )

        Path(tmp_path).unlink(missing_ok=True)

        return {
            "tailored_resume": result.tailored_resume.model_dump(),
            "ats_report": result.ats_report.model_dump(),
            "github_projects": [p.model_dump() for p in result.github_projects],
            "tex_path": result.tex_path,
        }
    except Exception as e:
        logger.exception("Pipeline with PDF failed")
        raise HTTPException(status_code=500, detail=str(e))
