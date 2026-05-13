"""Resume parsing models."""

from datetime import datetime, timezone
from typing import List, Optional

from pydantic import EmailStr, Field, HttpUrl

from models.common import BaseSchema, EmploymentType, ProjectType


class ContactInfo(BaseSchema):
    full_name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    linkedin_url: Optional[HttpUrl] = None
    github_url: Optional[HttpUrl] = None
    portfolio_url: Optional[HttpUrl] = None
    location: Optional[str] = None


class SkillCategory(BaseSchema):
    category: str
    skills: List[str]


class Education(BaseSchema):
    institution: str
    degree: str
    field_of_study: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    grade: Optional[str] = None
    achievements: List[str] = Field(default_factory=list)


class Certification(BaseSchema):
    name: str
    issuer: Optional[str] = None
    issue_date: Optional[str] = None
    credential_url: Optional[HttpUrl] = None


class WorkExperience(BaseSchema):
    company: str
    role: str
    employment_type: Optional[EmploymentType] = None
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    currently_working: bool = False
    technologies_used: List[str] = Field(default_factory=list)
    bullet_points: List[str] = Field(default_factory=list)
    achievements: List[str] = Field(default_factory=list)


class ResumeProject(BaseSchema):
    project_name: str
    project_type: Optional[ProjectType] = None
    description: str
    technologies_used: List[str] = Field(default_factory=list)
    bullet_points: List[str] = Field(default_factory=list)
    github_url: Optional[HttpUrl] = None
    live_url: Optional[HttpUrl] = None


class ParsedResume(BaseSchema):
    contact_info: ContactInfo
    summary: Optional[str] = None
    skill_categories: List[SkillCategory] = Field(default_factory=list)
    work_experience: List[WorkExperience] = Field(default_factory=list)
    projects: List[ResumeProject] = Field(default_factory=list)
    education: List[Education] = Field(default_factory=list)
    certifications: List[Certification] = Field(default_factory=list)
    achievements: List[str] = Field(default_factory=list)
    total_years_experience: Optional[float] = None
    raw_text: str
    parsed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))