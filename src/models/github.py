from datetime import datetime
from typing import List, Optional

from pydantic import (
    Field,
    HttpUrl,
)

from models.common import BaseSchema


class GitHubMetrics(BaseSchema):
    stars: int = 0
    forks: int = 0
    watchers: int = 0
    open_issues: int = 0
    commits_count: Optional[int] = None


class GitHubProject(BaseSchema):
    """
    Represents a GitHub repository analyzed
    against the target Job Description.

    Goal:
    Decide whether this repo should
    appear in the tailored resume.
    """

    # ---------------------------------
    # Raw Repo Metadata
    # ---------------------------------

    repo_name: str
    repo_url: HttpUrl
    description: Optional[str] = None
    readme_summary: Optional[str] = None
    primary_language: Optional[str] = None
    technologies_detected: List[str] = (Field(default_factory=list))
    topics: List[str] = (Field(default_factory=list))
    metrics: Optional[GitHubMetrics] = None
    last_commit_date: Optional[datetime] = None
    actively_maintained: bool = False

    # ---------------------------------
    # Resume Relevance
    # ---------------------------------

    jd_relevance_score: float = Field(
        ge=0,
        le=100,
        description=(
            "How relevant this repo "
            "is to the target job"))
    ats_keyword_match_score: float = (Field(ge=0, le=100))
    semantic_similarity_score: float = (Field(ge=0, le=100))
    technical_complexity_score: float = (Field(ge=0, le=100))
    production_readiness_score: float = (Field(ge=0, le=100))

    # ---------------------------------
    # Resume Decisioning
    # ---------------------------------

    should_include_in_resume: bool = (False)
    inclusion_priority: int = Field(
        ge=1,
        le=10,
        description=(
            "Higher means show earlier "
            "in resume"))
    why_selected: List[str] = (Field(default_factory=list))
    matched_jd_skills: List[str] = (Field(default_factory=list))
    missing_jd_skills: List[str] = (Field(default_factory=list))

    # ---------------------------------
    # Resume Writing Assistance
    # ---------------------------------

    extracted_achievements: List[str] = (Field(default_factory=list))
    suggested_resume_bullets: List[str] = Field(default_factory=list)
    quantified_impacts: List[str] = (Field(default_factory=list))
    recruiter_value: Optional[str] = (None)

    # ---------------------------------
    # Risk Flags
    # ---------------------------------

    concerns: List[str] = (Field(default_factory=list))
    is_resume_worthy: bool = False