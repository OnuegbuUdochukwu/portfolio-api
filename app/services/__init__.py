from asyncio import run
from io import BytesIO
from os import path

from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

from app.schemas import ResumeData

HERE = path.dirname(path.abspath(__file__))
TEMPLATES = path.join(HERE, "..", "templates")
env = Environment(loader=FileSystemLoader(TEMPLATES))


def render_resume_html(data: ResumeData) -> str:
    template = env.get_template("resume.html")
    return template.render(data=data.model_dump())


def generate_pdf(data: ResumeData) -> BytesIO:
    html_str = render_resume_html(data)
    buf = BytesIO()
    HTML(string=html_str).write_pdf(buf)
    buf.seek(0)
    return buf
