from pydantic import BaseModel


class ExperienceSchema(BaseModel):
    company: str
    role: str
    period: str
    type: str | None = None
    description: str | None = None
    highlights: list[str] = []
    tags: list[str] = []

    model_config = {"from_attributes": True}


class EducationSchema(BaseModel):
    school: str
    degree: str
    location: str | None = None
    period: str | None = None
    gpa: str | None = None
    details: list[str] = []

    model_config = {"from_attributes": True}


class CertificationSchema(BaseModel):
    name: str
    issuer: str | None = None
    date: str | None = None

    model_config = {"from_attributes": True}


class ProjectSchema(BaseModel):
    name: str
    description: str | None = None
    language: str | None = None
    tags: list[str] = []
    github_url: str | None = None
    category: str | None = None

    model_config = {"from_attributes": True}


class TrendingPostSchema(BaseModel):
    id: int
    hn_id: str
    title: str
    url: str | None = None
    points: int = 0
    comment_count: int = 0
    author: str | None = None
    created_at: str | None = None
    scraped_at: str | None = None
    topic_tags: list[str] = []

    model_config = {"from_attributes": True}


class ResumeData(BaseModel):
    name: str
    email: str
    phone: str
    location: str
    linkedin: str
    github: str
    tagline: str
    subtitle: str
    blurb: str
    experiences: list[ExperienceSchema]
    education: EducationSchema | None = None
    certifications: list[CertificationSchema] = []
    projects: list[ProjectSchema] = []
    last_updated: str
