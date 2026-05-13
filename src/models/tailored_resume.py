"""Tailored resume models — final output of the optimization pipeline."""

from datetime import datetime, timezone
from typing import List, Optional

from pydantic import Field

from models.common import BaseSchema
from models.resume import (
    Certification,
    ContactInfo,
    Education,
    ResumeProject,
    SkillCategory,
    WorkExperience,
)


class OptimizedBullet(BaseSchema):
    """Tracks bullet rewrites for changelog and auditability."""

    original: str
    optimized: str


class ResumeOptimizationMetadata(BaseSchema):
    """Tracks the optimization process across iterations."""

    optimization_iteration: int = 1
    ats_score_before: Optional[float] = None
    ats_score_after: Optional[float] = None
    keywords_added: List[str] = Field(default_factory=list)
    projects_prioritized: List[str] = Field(default_factory=list)
    sections_modified: List[str] = Field(default_factory=list)
    recruiter_notes: List[str] = Field(default_factory=list)


class TailoredResume(BaseSchema):
    """
    Final optimized resume — source of truth for PDF/TEX generation and preview UI.
    """

    contact_info: ContactInfo
    professional_summary: Optional[str] = None
    skill_categories: List[SkillCategory] = Field(default_factory=list)
    optimized_work_experience: List[WorkExperience] = Field(default_factory=list)
    optimized_projects: List[ResumeProject] = Field(default_factory=list)
    education: List[Education] = Field(default_factory=list)
    certifications: List[Certification] = Field(default_factory=list)
    optimized_bullets: List[OptimizedBullet] = Field(default_factory=list)
    target_role: Optional[str] = None
    target_company: Optional[str] = None
    final_ats_score: Optional[float] = None
    optimization_metadata: Optional[ResumeOptimizationMetadata] = None
    generated_tex_path: Optional[str] = None
    generated_pdf_path: Optional[str] = None
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))