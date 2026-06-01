from sqlalchemy import Column, Integer, String, Text, ARRAY, Float, DateTime, func
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Experience(Base):
    __tablename__ = "experiences"

    id = Column(Integer, primary_key=True, autoincrement=True)
    company = Column(String(255), nullable=False)
    role = Column(String(255), nullable=False)
    period = Column(String(100), nullable=False)
    type = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    highlights = Column(ARRAY(Text), nullable=True)
    tags = Column(ARRAY(String(100)), nullable=True)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Education(Base):
    __tablename__ = "education"

    id = Column(Integer, primary_key=True, autoincrement=True)
    school = Column(String(255), nullable=False)
    degree = Column(String(255), nullable=False)
    location = Column(String(255), nullable=True)
    period = Column(String(100), nullable=True)
    gpa = Column(String(50), nullable=True)
    details = Column(ARRAY(Text), nullable=True)


class Certification(Base):
    __tablename__ = "certifications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    issuer = Column(String(255), nullable=True)
    date = Column(String(100), nullable=True)


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    language = Column(String(100), nullable=True)
    tags = Column(ARRAY(String(100)), nullable=True)
    github_url = Column(String(500), nullable=True)
    category = Column(String(100), nullable=True)
    sort_order = Column(Integer, default=0)
