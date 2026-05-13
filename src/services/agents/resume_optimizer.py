"""
Resume
   ↓
ATS Report
   ↓
Weak sections
   ↓
Gemini rewrite
   ↓
TailoredResume
   ↓
ATS re-score
   ↓
score >= threshold?
        yes → done
        no → optimize again
"""
import json
from typing import List, Optional

from loguru import logger

from core.config import settings
from core.gemini_client import get_gemini_client
from models.ats import ATSReport
from models.github import GitHubProject
from models.jd import JobDescription
from models.resume import ParsedResume
from models.tailored_resume import (
    OptimizedBullet,
    ResumeOptimizationMetadata,
    TailoredResume,
)
from services.prompts.resume_optimizer import RESUME_OPTIMIZER_PROMPT
from services.agents.ats_scorer import ATSScorerService
from utils.decorators import llm_retry, log_operation


class ResumeOptimizerService:
    """
    Iterative resume optimizer.

    Pipeline:
        Resume → ATS Report → Weak sections → Gemini rewrite → Re-score → Repeat until threshold
    """

    def __init__(self, ats_scorer: ATSScorerService):
        self.client = get_gemini_client()
        self.ats_scorer = ats_scorer

    @log_operation("Resume optimization loop")
    def optimize_resume(
        self,
        job_description: JobDescription,
        parsed_resume: ParsedResume,
        ats_report: ATSReport,
        github_projects: Optional[List[GitHubProject]] = None,
    ) -> TailoredResume:
        """Run iterative optimization until ATS threshold is met or max loops reached."""
        github_projects = github_projects or []
        current_report = ats_report
        current_resume = parsed_resume
        optimized_resume = None

        for iteration in range(1, settings.MAX_OPTIMIZATION_LOOPS + 1):
            if current_report.ats_score >= settings.ATS_THRESHOLD:
                logger.success(f"ATS threshold reached at iteration {iteration}")
                break

            logger.info(f"Optimization iteration {iteration}")

            optimized_resume = self._optimize_once(
                job_description=job_description,
                parsed_resume=current_resume,
                ats_report=current_report,
                github_projects=github_projects,
                iteration=iteration,
            )

            # Re-score the optimized resume
            rescored = self.ats_scorer.score_resume(
                job_description=job_description,
                resume=self._tailored_to_parsed(optimized_resume),
                github_projects=github_projects,
            )

            optimized_resume.final_ats_score = rescored.ats_score
            optimized_resume.optimization_metadata.ats_score_after = rescored.ats_score

            if rescored.ats_score >= settings.ATS_THRESHOLD:
                logger.success(f"ATS threshold reached: {rescored.ats_score}")
                return optimized_resume

            current_report = rescored
            current_resume = self._tailored_to_parsed(optimized_resume)

        return optimized_resume

    # ─────────────────────────────────────────────
    # Single Optimization Pass
    # ─────────────────────────────────────────────

    @llm_retry
    def _optimize_once(
        self,
        job_description: JobDescription,
        parsed_resume: ParsedResume,
        ats_report: ATSReport,
        github_projects: List[GitHubProject],
        iteration: int,
    ) -> TailoredResume:
        """Run a single optimization pass through Gemini."""
        top_projects = self._select_top_projects(github_projects)

        prompt = RESUME_OPTIMIZER_PROMPT.format(
            role=job_description.role_title,
            company=job_description.company_name or "Unknown",
            job_description=job_description.raw_text,
            ats_score=ats_report.ats_score,
            missing_keywords=[k.keyword for k in ats_report.missing_keywords],
            weak_sections=[w.section_name for w in ats_report.weak_sections],
            recommendations=ats_report.recommendations,
            optimization_priority=ats_report.optimization_priority,
            github_projects=[p.model_dump() for p in top_projects],
            resume=parsed_resume.model_dump_json(indent=2),
        )

        optimized = self.client.structured_generate(prompt=prompt, schema=TailoredResume)

        # Preserve original contact info and set target metadata
        optimized.contact_info = parsed_resume.contact_info
        optimized.target_role = job_description.role_title
        optimized.target_company = job_description.company_name

        optimized.optimization_metadata = ResumeOptimizationMetadata(
            optimization_iteration=iteration,
            ats_score_before=ats_report.ats_score,
            keywords_added=[gap.keyword for gap in ats_report.missing_keywords],
            projects_prioritized=[p.repo_name for p in top_projects],
            sections_modified=[s.section_name for s in ats_report.weak_sections],
        )

        optimized.optimized_bullets = self._track_changes(parsed_resume, optimized)
        return optimized

    # ─────────────────────────────────────────────
    # Helpers
    # ─────────────────────────────────────────────

    @staticmethod
    def _select_top_projects(
        github_projects: List[GitHubProject], top_k: int = 3
    ) -> List[GitHubProject]:
        """Select top-k resume-worthy projects by JD relevance."""
        filtered = [p for p in github_projects if p.should_include_in_resume]
        filtered.sort(key=lambda p: p.jd_relevance_score, reverse=True)
        return filtered[:top_k]

    @staticmethod
    def _track_changes(
        original: ParsedResume, optimized: TailoredResume
    ) -> List[OptimizedBullet]:
        """Track bullet point changes between original and optimized resume."""
        original_bullets = [b for exp in original.work_experience for b in exp.bullet_points]
        optimized_bullets = [
            b for exp in optimized.optimized_work_experience for b in exp.bullet_points
        ]

        return [
            OptimizedBullet(original=orig, optimized=opt)
            for orig, opt in zip(original_bullets, optimized_bullets)
            if orig != opt
        ]

    @staticmethod
    def _tailored_to_parsed(tailored: TailoredResume) -> ParsedResume:
        """Convert TailoredResume back to ParsedResume for ATS re-scoring."""
        return ParsedResume(
            contact_info=tailored.contact_info,
            summary=tailored.professional_summary,
            skill_categories=tailored.skill_categories,
            work_experience=tailored.optimized_work_experience,
            projects=tailored.optimized_projects,
            education=tailored.education,
            certifications=tailored.certifications,
            raw_text=tailored.model_dump_json(),
        )