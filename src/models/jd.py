"""Job Description models."""

from datetime import datetime, timezone
from typing import List, Optional

from pydantic import Field

from models.common import BaseSchema, EmploymentType, SeniorityLevel


class CompensationRange(BaseSchema):
    currency: Optional[str] = None
    min_salary: Optional[float] = None
    max_salary: Optional[float] = None


class JobDescription(BaseSchema):
    role_title: str
    company_name: Optional[str] = None
    seniority: Optional[SeniorityLevel] = None
    employment_type: Optional[EmploymentType] = None
    location: Optional[str] = None
    remote_allowed: bool = False
    required_skills: List[str] = Field(default_factory=list)
    preferred_skills: List[str] = Field(default_factory=list)
    tech_stack: List[str] = Field(default_factory=list)
    responsibilities: List[str] = Field(default_factory=list)
    qualifications: List[str] = Field(default_factory=list)
    ats_keywords: List[str] = Field(default_factory=list)
    soft_skills: List[str] = Field(default_factory=list)
    hidden_expectations: List[str] = Field(default_factory=list)
    compensation: Optional[CompensationRange] = None
    raw_text: str
    parsed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))