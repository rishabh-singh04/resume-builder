"""ATS scoring models."""

from datetime import datetime, timezone
from typing import List, Literal, Optional

from pydantic import Field

from models.common import BaseSchema


class ATSGap(BaseSchema):
    keyword: str
    importance_score: float = Field(ge=0, le=10)
    reason: Optional[str] = None


class WeakSection(BaseSchema):
    section_name: str
    issue: str
    recommendation: str


class ATSReport(BaseSchema):
    ats_score: float = Field(ge=0, le=100)
    keyword_score: float = Field(ge=0, le=100)
    keyword_match_score: float = Field(ge=0, le=100)
    semantic_similarity_score: float = Field(ge=0, le=100)
    project_relevance_score: float = Field(ge=0, le=100)
    resume_quality_score: float = Field(ge=0, le=100)
    experience_score: Optional[float] = Field(default=None, ge=0, le=100)
    section_score: Optional[float] = Field(default=None, ge=0, le=100)
    format_score: Optional[float] = Field(default=None, ge=0, le=100)
    impact_score: Optional[float] = Field(default=None, ge=0, le=100)
    score_reasoning: Optional[str] = None
    scoring_method: Literal["llm", "fallback"]
    matched_keywords: List[str] = Field(default_factory=list)
    missing_keywords: List[ATSGap] = Field(default_factory=list)
    weak_sections: List[WeakSection] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    optimization_priority: List[str] = Field(default_factory=list)
    analyzed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))