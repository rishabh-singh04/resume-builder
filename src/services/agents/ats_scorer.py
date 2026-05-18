"""ATS Scorer agent — hybrid scoring using exact match, embeddings, and LLM critique."""

from typing import List

from loguru import logger

from core.gemini_client import get_gemini_client
from models.ats import ATSGap, ATSReport, WeakSection
from models.github import GitHubProject
from models.jd import JobDescription
from models.resume import ParsedResume
from services.prompts.ats_scorer import ATS_QUALITY_PROMPT, ATS_SCORING_PROMPT
from services.embeddings import get_embedding_service
from utils.decorators import llm_retry, log_operation
from utils.safe import safe_list, safe_str


class ATSScorerService:
    """
    Hybrid ATS scorer.

    Weighted formula:
        30% Exact Keyword Match
        25% Semantic Similarity
        15% Keyword Placement
        10% Parsing Quality
        10% Recruiter Readability (LLM)
        10% Project Relevance
    """

    def __init__(self):
        self.client = get_gemini_client()
        self.embeddings = get_embedding_service()

    @log_operation("ATS scoring")
    def score_resume(
        self,
        job_description: JobDescription,
        resume: ParsedResume,
        github_projects: List[GitHubProject] | None = None,
    ) -> ATSReport:
        """Score a resume against a JD using the hybrid formula and optional Gemini structured scoring."""
        github_projects = github_projects or []

        keyword_score = self._keyword_match_score(job_description, resume)
        semantic_score = self._semantic_score(job_description, resume)
        placement_score = self._keyword_placement_score(job_description, resume)
        parsing_score = self._parsing_quality_score(resume)
        recruiter_quality = self._safe_resume_quality_analysis(resume)
        project_score = self._project_relevance_score(github_projects)

        try:
            llm_report = self._safe_structured_ats_report(
                job_description=job_description,
                resume=resume,
                github_projects=github_projects,
            )
            return self._build_ats_report_from_llm(
                job_description=job_description,
                resume=resume,
                github_projects=github_projects,
                recruiter_quality=recruiter_quality,
                llm_report=llm_report,
                keyword_score=keyword_score,
                semantic_score=semantic_score,
                placement_score=placement_score,
                project_score=project_score,
            )
        except Exception:
            logger.warning(
                "Structured ATS scoring failed; falling back to hybrid formula."
            )

        final_score = round(
            keyword_score * 0.30
            + semantic_score * 0.25
            + placement_score * 0.15
            + parsing_score * 0.10
            + recruiter_quality["resume_quality_score"] * 0.10
            + project_score * 0.10,
            2,
        )

        matched = self._matched_keywords(job_description, resume)
        missing = self._missing_keywords(job_description, matched)

        return ATSReport(
            ats_score=final_score,
            keyword_score=keyword_score,
            keyword_match_score=keyword_score,
            semantic_similarity_score=semantic_score,
            project_relevance_score=project_score,
            resume_quality_score=recruiter_quality["resume_quality_score"],
            scoring_method="fallback",
            matched_keywords=matched,
            missing_keywords=missing,
            weak_sections=[
                WeakSection(**section)
                for section in recruiter_quality.get("weak_sections", [])
            ],
            recommendations=recruiter_quality.get("recommendations", []),
            optimization_priority=recruiter_quality.get("optimization_priority", []),
        )

    # ─────────────────────────────────────────────
    # Keyword Match (exact string matching)
    # ─────────────────────────────────────────────

    def _keyword_match_score(self, jd: JobDescription, resume: ParsedResume) -> float:
        resume_text = safe_str(resume.raw_text).lower()
        required = safe_list(jd.required_skills)
        preferred = safe_list(jd.preferred_skills)

        required_matches = sum(1 for s in required if s.lower() in resume_text)
        preferred_matches = sum(1 for s in preferred if s.lower() in resume_text)

        required_score = (required_matches / max(len(required), 1)) * 70
        preferred_score = (preferred_matches / max(len(preferred), 1)) * 30

        return round(required_score + preferred_score, 2)

    # ─────────────────────────────────────────────
    # Semantic Similarity (embeddings)
    # ─────────────────────────────────────────────

    def _semantic_score(self, jd: JobDescription, resume: ParsedResume) -> float:
        jd_text = " ".join(
            safe_list(jd.responsibilities)
            + safe_list(jd.required_skills)
            + safe_list(jd.tech_stack)
        )
        return self.embeddings.similarity_score(jd_text, safe_str(resume.raw_text))

    # ─────────────────────────────────────────────
    # Keyword Placement (where keywords appear matters)
    # ─────────────────────────────────────────────

    def _keyword_placement_score(self, jd: JobDescription, resume: ParsedResume) -> float:
        score = 0
        keywords = safe_list(jd.required_skills)
        summary = safe_str(resume.summary).lower()
        project_text = " ".join(
            safe_str(p.description) for p in (resume.projects or [])
        ).lower()
        experience_text = " ".join(
            safe_str(bullet)
            for exp in (resume.work_experience or [])
            for bullet in (exp.bullet_points or [])
        ).lower()

        for keyword in keywords:
            kw = keyword.lower()
            if kw in summary:
                score += 3
            if kw in experience_text:
                score += 2
            if kw in project_text:
                score += 1

        max_score = len(keywords) * 6
        return round((score / max(max_score, 1)) * 100, 2)

    # ─────────────────────────────────────────────
    # Parsing Quality (structural completeness)
    # ─────────────────────────────────────────────

    @staticmethod
    def _parsing_quality_score(resume: ParsedResume) -> float:
        score = 100
        if not resume.contact_info.full_name:
            score -= 20
        if not resume.work_experience:
            score -= 20
        if not resume.skill_categories:
            score -= 10
        return max(score, 0)

    # ─────────────────────────────────────────────
    # Project Relevance (from GitHub analysis)
    # ─────────────────────────────────────────────

    @staticmethod
    def _project_relevance_score(github_projects: List[GitHubProject]) -> float:
        if not github_projects:
            return 0
        top = sorted(github_projects, key=lambda p: p.jd_relevance_score, reverse=True)[:3]
        return round(sum(p.jd_relevance_score for p in top) / len(top), 2)

    # ─────────────────────────────────────────────
    # Keyword Matching Helpers
    # ─────────────────────────────────────────────

    @staticmethod
    def _matched_keywords(jd: JobDescription, resume: ParsedResume) -> List[str]:
        resume_text = safe_str(resume.raw_text).lower()
        return [
            skill
            for skill in safe_list(jd.required_skills) + safe_list(jd.preferred_skills)
            if skill.lower() in resume_text
        ]

    @staticmethod
    def _missing_keywords(jd: JobDescription, matched: List[str]) -> List[ATSGap]:
        return [
            ATSGap(keyword=skill, importance_score=9, reason="Required skill missing")
            for skill in safe_list(jd.required_skills)
            if skill not in matched
        ]

    # ─────────────────────────────────────────────
    # LLM Quality Check (single Gemini call)
    # ─────────────────────────────────────────────

    @llm_retry
    def _resume_quality_analysis(self, resume: ParsedResume) -> dict:
        prompt = ATS_QUALITY_PROMPT.format(resume=resume.raw_text)
        return self.client.generate_json(prompt)

    def _safe_resume_quality_analysis(self, resume: ParsedResume) -> dict:
        """Attempt resume quality analysis, with fallback on LLM/JSON failures."""
        try:
            return self._resume_quality_analysis(resume)
        except Exception as exc:
            logger.warning(
                "Resume quality analysis failed; applying fallback default scores.",
                exc_info=exc,
            )
            return {
                "resume_quality_score": 50.0,
                "weak_sections": [],
                "recommendations": [
                    "Resume quality analysis unavailable due to model/response error."
                ],
                "optimization_priority": [],
            }

    @llm_retry
    def _safe_structured_ats_report(
        self,
        job_description: JobDescription,
        resume: ParsedResume,
        github_projects: List[GitHubProject],
    ) -> dict:
        prompt = ATS_SCORING_PROMPT.format(
            job_description=job_description.raw_text,
            resume=resume.raw_text,
            github_projects="\n".join(
                f"{proj.repo_name}: {proj.description or ''}"
                for proj in github_projects[:3]
            ),
        )
        return self.client.generate_json(prompt)

    def _build_ats_report_from_llm(
        self,
        job_description: JobDescription,
        resume: ParsedResume,
        github_projects: List[GitHubProject],
        recruiter_quality: dict,
        llm_report: dict,
        keyword_score: float,
        semantic_score: float,
        placement_score: float,
        project_score: float,
    ) -> ATSReport:
        """Convert trusted LLM scoring output into an ATSReport."""
        matched_keywords = safe_list(llm_report.get("matched_keywords"))
        if not matched_keywords:
            matched_keywords = self._matched_keywords(job_description, resume)

        missing_keywords = [
            ATSGap(keyword=keyword, importance_score=9, reason="Required skill missing")
            for keyword in safe_list(llm_report.get("missing_keywords"))
        ]

        weak_sections = []
        for section in safe_list(llm_report.get("weak_sections")):
            if isinstance(section, dict):
                weak_sections.append(
                    WeakSection(
                        section_name=section.get("section_name", "Unknown section"),
                        issue=section.get("issue", ""),
                        recommendation=section.get("recommendation", ""),
                    )
                )

        overall_score = llm_report.get("overall_score")
        if overall_score is None:
            overall_score = round(
                keyword_score * 0.30
                + semantic_score * 0.25
                + placement_score * 0.15
                + recruiter_quality["resume_quality_score"] * 0.10
                + project_score * 0.10,
                2,
            )

        llm_keyword_score = llm_report.get("keyword_score", keyword_score)

        return ATSReport(
            ats_score=overall_score,
            keyword_score=llm_keyword_score,
            keyword_match_score=llm_keyword_score,
            experience_score=llm_report.get("experience_score"),
            section_score=llm_report.get("section_score"),
            format_score=llm_report.get("format_score"),
            impact_score=llm_report.get("impact_score"),
            semantic_similarity_score=semantic_score,
            project_relevance_score=project_score,
            resume_quality_score=recruiter_quality.get("resume_quality_score", 50.0),
            scoring_method="llm",
            matched_keywords=matched_keywords,
            missing_keywords=missing_keywords,
            weak_sections=weak_sections,
            recommendations=safe_list(llm_report.get("recommendations")),
            optimization_priority=safe_list(llm_report.get("optimization_priority")),
            score_reasoning=llm_report.get("score_reasoning"),
        )