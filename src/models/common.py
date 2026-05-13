from enum import Enum
from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        str_strip_whitespace=True,
        use_enum_values=True,
    )


class SeniorityLevel(str, Enum):
    INTERN = "Intern"
    JUNIOR = "Junior"
    MID_LEVEL = "Mid-Level"
    SENIOR = "Senior"
    STAFF = "Staff"
    LEAD = "Lead"
    PRINCIPAL = "Principal"


class EmploymentType(str, Enum):
    FULL_TIME = "Full-Time"
    PART_TIME = "Part-Time"
    CONTRACT = "Contract"
    INTERNSHIP = "Internship"
    FREELANCE = "Freelance"


class ProjectType(str, Enum):
    PERSONAL = "Personal"
    PROFESSIONAL = "Professional"
    OPEN_SOURCE = "Open-Source"
    RESEARCH = "Research"