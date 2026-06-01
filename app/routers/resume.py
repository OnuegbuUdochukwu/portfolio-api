from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Experience, Education, Certification, Project
from app.schemas import ResumeData, ExperienceSchema, EducationSchema, CertificationSchema, ProjectSchema
from app.services import generate_pdf

router = APIRouter(prefix="/api/resume", tags=["resume"])


async def _get_resume_data(db: AsyncSession) -> ResumeData:
    try:
        exp_result = await db.execute(select(Experience).order_by(Experience.sort_order))
        edu_result = await db.execute(select(Education))
        cert_result = await db.execute(select(Certification).order_by(Certification.id))
        proj_result = await db.execute(select(Project).order_by(Project.sort_order))

        experiences = [ExperienceSchema.model_validate(e) for e in exp_result.scalars().all()]
        education_list = [EducationSchema.model_validate(e) for e in edu_result.scalars().all()]
        certifications = [CertificationSchema.model_validate(c) for c in cert_result.scalars().all()]
        projects = [ProjectSchema.model_validate(p) for p in proj_result.scalars().all()]
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database unavailable: {e}")

    return ResumeData(
        name="Udochukwu Onuegbu",
        email="onuegbuudochukwu6@gmail.com",
        phone="09035854102",
        location="Ikeja, Lagos, Nigeria",
        linkedin="https://linkedin.com/in/udochukwu-onuegbu-672096277",
        github="https://github.com/OnuegbuUdochukwu",
        tagline="Backend Engineer",
        subtitle="Final year @ Covenant University \u00b7 4.89 GPA \u00b7 1,400+ contributions.",
        blurb="I write clean, maintainable code. I focus on what happens behind the scenes \u2014 server logic, data structures, and the systems that carry weight without making noise. I prefer logic over design.",
        experiences=experiences,
        education=education_list[0] if education_list else None,
        certifications=certifications,
        projects=projects,
        last_updated="June 2026",
    )


@router.get("")
async def get_resume_data(db: AsyncSession = Depends(get_db)):
    return await _get_resume_data(db)


@router.get("/pdf")
async def download_resume_pdf(db: AsyncSession = Depends(get_db)):
    data = await _get_resume_data(db)
    pdf_buf = generate_pdf(data)

    return StreamingResponse(
        pdf_buf,
        media_type="application/pdf",
        headers={
            "Content-Disposition": 'attachment; filename="Udochukwu_Onuegbu_Resume.pdf"',
            "Content-Type": "application/pdf",
        },
    )
