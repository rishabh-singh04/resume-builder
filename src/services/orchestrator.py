"""
Pipeline Orchestrator — manages the full resume tailoring workflow.

Flow:
    1. Parse JD
    2. Parse Resume
    3. Parallel: Company Research + GitHub Analysis
    4. ATS Scoring
    5. Resume Optimization Loop
    6. LaTeX Generation
"""

import asyncio
from dataclasses import dataclass, field
from typing import List, Optional

from loguru import logger

from models.ats import ATSReport
from models.github import GitHubProject
from models.jd import JobDescription
from models.resume import ParsedResume
from models.tailored_resume import TailoredResume
from services.agents.ats_scorer import ATSScorerService
from services.agents.company_research import CompanyInsight, CompanyResearchService
from services.agents.github_analyzer import GitHubAnalyzerService
from services.agents.jd_parser import JDParserService
from services.agents.resume_optimizer import ResumeOptimizerService
from services.agents.resume_parser import ResumeParserService
from services.latex_resume import LatexGeneratorService
from utils.decorators import timed_block


@dataclass
class PipelineResult:
    """Complete output of the resume tailoring pipeline."""

    tailored_resume: TailoredResume
    ats_report: ATSReport
    job_description: JobDescription
    parsed_resume: ParsedResume
    github_projects: List[GitHubProject] = field(default_factory=list)
    company_insight: Optional[CompanyInsight] = None
    tex_path: Optional[str] = None


class ResumeOrchestrator:
    """
    Central pipeline orchestrator.

    Coordinates all agents in a deterministic sequential flow
    with parallel research where possible.
    """

    def __init__(self):
        self.jd_parser = JDParserService()
        self.resume_parser = ResumeParserService()
        self.github_analyzer = GitHubAnalyzerService()
        self.company_researcher = CompanyResearchService()
        self.ats_scorer = ATSScorerService()
        self.resume_optimizer = ResumeOptimizerService(ats_scorer=self.ats_scorer)
        self.latex_generator = LatexGeneratorService()

    async def run_pipeline(
        self,
        jd_text: str,
        resume_pdf_path: Optional[str] = None,
        resume_text: Optional[str] = None,
        github_username: Optional[str] = None,
    ) -> PipelineResult:
        """
        Full resume tailoring pipeline.

        Args:
            jd_text: Raw job description text.
            resume_pdf_path: Path to resume PDF file.
            resume_text: Raw resume text (alternative to PDF).
            github_username: GitHub username for project analysis.
        """
        # ── Stage 1: Parse Inputs ────────────────────────
        with timed_block("Stage 1: Input Parsing"):
            jd = self.jd_parser.parse(jd_text)
            resume = self._parse_resume(resume_pdf_path, resume_text)

        # ── Stage 2: Parallel Research ───────────────────
        with timed_block("Stage 2: Research (parallel)"):
            github_projects, company_insight = await self._run_research(
                jd=jd, github_username=github_username
            )

        # ── Stage 3: ATS Scoring ─────────────────────────
        with timed_block("Stage 3: ATS Scoring"):
            ats_report = self.ats_scorer.score_resume(
                job_description=jd,
                resume=resume,
                github_projects=github_projects,
            )
            logger.info(f"Initial ATS Score: {ats_report.ats_score}")

        # ── Stage 4: Resume Optimization ─────────────────
        with timed_block("Stage 4: Resume Optimization"):
            tailored = self.resume_optimizer.optimize_resume(
                job_description=jd,
                parsed_resume=resume,
                ats_report=ats_report,
                github_projects=github_projects,
            )

        # ── Stage 5: LaTeX Generation ────────────────────
        tex_path = None
        with timed_block("Stage 5: LaTeX Generation"):
            try:
                tex_path = self.latex_generator.generate_tex(tailored)
            except Exception:
                logger.exception("LaTeX generation failed — continuing without TEX output")

        return PipelineResult(
            tailored_resume=tailored,
            ats_report=ats_report,
            job_description=jd,
            parsed_resume=resume,
            github_projects=github_projects,
            company_insight=company_insight,
            tex_path=tex_path,
        )

    # ─────────────────────────────────────────────
    # Internal Helpers
    # ─────────────────────────────────────────────

    def _parse_resume(
        self,
        pdf_path: Optional[str],
        text: Optional[str],
    ) -> ParsedResume:
        """Parse resume from PDF or raw text."""
        if pdf_path:
            return self.resume_parser.parse_pdf(pdf_path)
        if text:
            return self.resume_parser.parse_text(text)
        raise ValueError("Either resume_pdf_path or resume_text must be provided.")

    async def _run_research(
        self,
        jd: JobDescription,
        github_username: Optional[str],
    ) -> tuple:
        """Run GitHub analysis and company research in parallel using asyncio."""
        loop = asyncio.get_event_loop()

        github_task = loop.run_in_executor(
            None,
            lambda: (
                self.github_analyzer.analyze_user(github_username, jd.raw_text)
                if github_username
                else []
            ),
        )

        company_task = loop.run_in_executor(
            None,
            lambda: self.company_researcher.research(
                company_name=jd.company_name or "",
                role_title=jd.role_title,
            ),
        )

        github_projects, company_insight = await asyncio.gather(
            github_task, company_task
        )

        logger.info(
            f"Research complete: {len(github_projects)} repos, "
            f"company={'found' if company_insight else 'skipped'}"
        )

        return github_projects, company_insight
