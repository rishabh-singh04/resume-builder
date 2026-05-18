"""Resume parsing models."""

from datetime import datetime, timezone
from typing import List, Optional
from pydantic import EmailStr, Field, HttpUrl, field_validator

from models.common import BaseSchema


def _sanitize_url(value: Optional[str]) -> Optional[str]:
    """Convert placeholder URLs and invalid formats to None."""
    if not value or not isinstance(value, str):
        return None
    # Detect placeholder patterns
    placeholder_indicators = ['[', ']', 'placeholder', 'link', 'url', 'http']
    if any(ind in value.lower() for ind in placeholder_indicators[:2]):  # '[' or ']'
        return None
    return value

class ContactInfo(BaseSchema):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    location: Optional[str] = None

    @field_validator('linkedin_url', 'github_url', 'portfolio_url', mode='before')
    @classmethod
    def validate_contact_urls(cls, v: Optional[str]) -> Optional[str]:
        """Convert placeholder URLs to None."""
        if not v or not isinstance(v, str):
            return None
        if v.strip().startswith('[') or v.strip().endswith(']') or 'placeholder' in v.lower():
            return None
        if v.startswith(('http://', 'https://', 'ftp://')):
            return v
        return None


class SkillCategory(BaseSchema):
    category: str
    skills: Optional[List[str]] = Field(default_factory=list)


class Education(BaseSchema):
    institution: str
    degree: str
    field_of_study: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    grade: Optional[str] = None
    achievements: Optional[List[str]] = Field(default_factory=list)


class Certification(BaseSchema):
    name: str
    issuer: Optional[str] = None
    issue_date: Optional[str] = None
    credential_url: Optional[str] = None

    @field_validator('credential_url', mode='before')
    @classmethod
    def validate_cert_url(cls, v: Optional[str]) -> Optional[str]:
        """Convert placeholder URLs to None."""
        if not v or not isinstance(v, str):
            return None
        if v.strip().startswith('[') or v.strip().endswith(']') or 'placeholder' in v.lower():
            return None
        if v.startswith(('http://', 'https://', 'ftp://')):
            return v
        return None


class WorkExperience(BaseSchema):
    company: str
    role: str
    employment_type: Optional[str] = None
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    currently_working: bool = False
    technologies_used: Optional[List[str]] = Field(default_factory=list)
    bullet_points: Optional[List[str]] = Field(default_factory=list)
    achievements: Optional[List[str]] = Field(default_factory=list)


class ResumeProject(BaseSchema):
    project_name: str
    project_type: Optional[str] = None
    description: Optional[str] = None
    technologies_used: Optional[List[str]] = Field(default_factory=list)
    bullet_points: Optional[List[str]] = Field(default_factory=list)
    github_url: Optional[str] = None
    live_url: Optional[str] = None

    @field_validator('github_url', 'live_url', mode='before')
    @classmethod
    def validate_urls(cls, v: Optional[str]) -> Optional[str]:
        """Convert placeholder URLs to None, allow actual URLs through."""
        if not v or not isinstance(v, str):
            return None
        # Block placeholder patterns
        if v.strip().startswith('[') or v.strip().endswith(']') or 'placeholder' in v.lower():
            return None
        # Let pydantic validate real URLs; if they fail, we'll catch it
        try:
            # Try to parse as URL; if it looks valid enough, keep it
            if v.startswith(('http://', 'https://', 'ftp://')):
                return v
        except Exception:
            pass
        return None


class ParsedResume(BaseSchema):
    contact_info: ContactInfo
    summary: Optional[str] = None
    skill_categories: Optional[List[SkillCategory]] = Field(default_factory=list)
    work_experience: Optional[List[WorkExperience]] = Field(default_factory=list)
    projects: Optional[List[ResumeProject]] = Field(default_factory=list)
    education: Optional[List[Education]] = Field(default_factory=list)
    certifications: Optional[List[Certification]] = Field(default_factory=list)
    achievements: Optional[List[str]] = Field(default_factory=list)
    total_years_experience: Optional[float] = None
    raw_text: str
    parsed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))