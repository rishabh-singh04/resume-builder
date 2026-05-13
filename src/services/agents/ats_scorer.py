"""ATS Scorer agent — hybrid scoring using exact match, embeddings, and LLM critique."""

from typing import List

from loguru import logger

from core.gemini_client import get_gemini_client
from models.ats import ATSGap, ATSReport, WeakSection
from models.github import GitHubProject
from models.jd import JobDescription
from models.resume import ParsedResume
from services.prompts.ats_scorer import ATS_QUALITY_PROMPT
from services.embeddings import get_embedding_service
from utils.decorators import llm_retry, log_operation


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
        """Score a resume against a JD using the hybrid formula."""
        github_projects = github_projects or []

        keyword_score = self._keyword_match_score(job_description, resume)
        semantic_score = self._semantic_score(job_description, resume)
        placement_score = self._keyword_placement_score(job_description, resume)
        parsing_score = self._parsing_quality_score(resume)
        recruiter_quality = self._resume_quality_analysis(resume)
        project_score = self._project_relevance_score(github_projects)

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
            keyword_match_score=keyword_score,
            semantic_similarity_score=semantic_score,
            project_relevance_score=project_score,
            resume_quality_score=recruiter_quality["resume_quality_score"],
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

    @staticmethod
    def _keyword_match_score(jd: JobDescription, resume: ParsedResume) -> float:
        resume_text = resume.raw_text.lower()
        required = jd.required_skills
        preferred = jd.preferred_skills

        required_matches = sum(1 for s in required if s.lower() in resume_text)
        preferred_matches = sum(1 for s in preferred if s.lower() in resume_text)

        required_score = (required_matches / max(len(required), 1)) * 70
        preferred_score = (preferred_matches / max(len(preferred), 1)) * 30

        return round(required_score + preferred_score, 2)

    # ─────────────────────────────────────────────
    # Semantic Similarity (embeddings)
    # ─────────────────────────────────────────────

    def _semantic_score(self, jd: JobDescription, resume: ParsedResume) -> float:
        jd_text = " ".join(jd.responsibilities + jd.required_skills + jd.tech_stack)
        return self.embeddings.similarity_score(jd_text, resume.raw_text)

    # ─────────────────────────────────────────────
    # Keyword Placement (where keywords appear matters)
    # ─────────────────────────────────────────────

    @staticmethod
    def _keyword_placement_score(jd: JobDescription, resume: ParsedResume) -> float:
        score = 0
        keywords = jd.required_skills
        summary = (resume.summary or "").lower()
        project_text = " ".join(p.description for p in resume.projects).lower()
        experience_text = " ".join(
            bullet for exp in resume.work_experience for bullet in exp.bullet_points
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
        resume_text = resume.raw_text.lower()
        return [
            skill
            for skill in (jd.required_skills + jd.preferred_skills)
            if skill.lower() in resume_text
        ]

    @staticmethod
    def _missing_keywords(jd: JobDescription, matched: List[str]) -> List[ATSGap]:
        return [
            ATSGap(keyword=skill, importance_score=9, reason="Required skill missing")
            for skill in jd.required_skills
            if skill not in matched
        ]

    # ─────────────────────────────────────────────
    # LLM Quality Check (single Gemini call)
    # ─────────────────────────────────────────────

    @llm_retry
    def _resume_quality_analysis(self, resume: ParsedResume) -> dict:
        prompt = ATS_QUALITY_PROMPT.format(resume=resume.raw_text)
        return self.client.generate_json(prompt)