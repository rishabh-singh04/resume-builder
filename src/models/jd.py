"""Job Description models."""

from datetime import datetime, timezone
from typing import List, Optional

from pydantic import Field

from models.common import BaseSchema


class CompensationRange(BaseSchema):
    currency: Optional[str] = None
    min_salary: Optional[float] = None
    max_salary: Optional[float] = None


class JobDescription(BaseSchema):
    role_title: str
    company_name: Optional[str] = None
    seniority: Optional[str] = None
    employment_type: Optional[str] = None
    location: Optional[str] = None
    remote_allowed: bool = False
    required_skills: Optional[List[str]] = Field(default_factory=list)
    preferred_skills: Optional[List[str]] = Field(default_factory=list)
    tech_stack: Optional[List[str]] = Field(default_factory=list)
    responsibilities: Optional[List[str]] = Field(default_factory=list)
    qualifications: Optional[List[str]] = Field(default_factory=list)
    ats_keywords: Optional[List[str]] = Field(default_factory=list)
    soft_skills: Optional[List[str]] = Field(default_factory=list)
    hidden_expectations: Optional[List[str]] = Field(default_factory=list)
    compensation: Optional[CompensationRange] = None
    raw_text: str
    parsed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))