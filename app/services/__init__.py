from io import BytesIO
from os import path

from fpdf import FPDF

from app.schemas import ResumeData

FONT_DIR = path.join(path.dirname(path.abspath(__file__)), "..", "assets")
FONT_SANS = path.join(FONT_DIR, "DejaVuSans.ttf")
FONT_BOLD = path.join(FONT_DIR, "DejaVuSans-Bold.ttf")
FONT_ITALIC = path.join(FONT_DIR, "DejaVuSans-Oblique.ttf")


def generate_pdf(data: ResumeData) -> BytesIO:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=20)

    pdf.add_font("Sans", "", FONT_SANS)
    pdf.add_font("Sans", "B", FONT_BOLD)
    pdf.add_font("Sans", "I", FONT_ITALIC)

    pdf.add_page()
    family = "Sans"
    pdf.set_font(family, "B", 22)

    # --- Header ---
    cell_w = pdf.w - 2 * pdf.l_margin

    pdf.set_font(family, "B", 20)
    pdf.cell(cell_w, 8, data.name, new_x="LMARGIN", new_y="NEXT")
    pdf.set_font(family, "", 11)
    pdf.set_text_color(40, 140, 60)
    pdf.cell(cell_w, 5, data.tagline, new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(80, 80, 80)
    pdf.set_font(family, "", 8)
    contact = f"{data.email}  |  {data.phone}  |  {data.location}"
    pdf.cell(cell_w, 4, contact, new_x="LMARGIN", new_y="NEXT")
    links = f"{data.github}  |  {data.linkedin}"
    pdf.cell(cell_w, 4, links, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    # --- Blurb ---
    pdf.set_font(family, "I", 9)
    pdf.set_text_color(60, 60, 60)
    pdf.multi_cell(cell_w, 4.5, data.blurb)
    pdf.ln(3)

    GREEN = (30, 130, 60)
    DARK = (30, 30, 30)
    GRAY = (100, 100, 100)
    MID = (60, 60, 60)

    def section(title):
        pdf.ln(2)
        pdf.set_text_color(*GREEN)
        pdf.set_font(family, "B", 10)
        pdf.cell(cell_w, 5, title.upper(), new_x="LMARGIN", new_y="NEXT")
        pdf.set_draw_color(200, 200, 200)
        pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
        pdf.ln(2)

    def body_text(text, size=9):
        pdf.set_text_color(*MID)
        pdf.set_font(family, "", size)
        pdf.multi_cell(cell_w, 4.5, text)

    def bold_text(text, size=9):
        pdf.set_text_color(*DARK)
        pdf.set_font(family, "B", size)
        pdf.cell(cell_w, 5, text, new_x="LMARGIN", new_y="NEXT")

    # --- Experience ---
    if data.experiences:
        section("Experience")
        for exp in data.experiences:
            pdf.set_text_color(*DARK)
            pdf.set_font(family, "B", 10)
            company_w = pdf.get_string_width(exp.company + "  ")
            pdf.cell(company_w, 5, exp.company)
            pdf.set_text_color(*GRAY)
            pdf.set_font(family, "", 8)
            pdf.cell(cell_w - company_w, 5, exp.period, new_x="LMARGIN", new_y="NEXT")
            pdf.set_text_color(*MID)
            pdf.set_font(family, "", 9)
            role = exp.role
            if exp.type:
                role += f"  |  {exp.type}"
            pdf.cell(cell_w, 5, role, new_x="LMARGIN", new_y="NEXT")
            if exp.description:
                body_text(exp.description)
            if exp.highlights:
                for h in exp.highlights:
                    pdf.set_font(family, "", 9)
                    pdf.set_text_color(*MID)
                    x = pdf.l_margin + 4
                    pdf.set_x(x)
                    pdf.cell(4, 4.5, "\u2022")
                    pdf.multi_cell(cell_w - 8, 4.5, h)
            pdf.ln(2)

    # --- Education ---
    if data.education:
        section("Education")
        pdf.set_text_color(*DARK)
        pdf.set_font(family, "B", 10)
        edu = data.education
        pdf.cell(cell_w, 5, edu.school, new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(*GRAY)
        pdf.set_font(family, "", 8)
        pdf.cell(cell_w, 5, edu.period, new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(*MID)
        pdf.set_font(family, "", 9)
        degree = edu.degree
        if edu.gpa:
            degree += f"  |  GPA: {edu.gpa}"
        pdf.cell(cell_w, 5, degree, new_x="LMARGIN", new_y="NEXT")
        if edu.details:
            for d in edu.details:
                pdf.set_font(family, "", 9)
                pdf.set_text_color(*MID)
                x = pdf.l_margin + 4
                pdf.set_x(x)
                pdf.cell(4, 4.5, "\u2022")
                pdf.multi_cell(cell_w - 8, 4.5, d)
        pdf.ln(2)

    # --- Certifications ---
    if data.certifications:
        section("Certifications")
        for i, cert in enumerate(data.certifications):
            if i % 2 == 0:
                pdf.set_x(pdf.l_margin)
            else:
                pdf.set_x(pdf.l_margin + cell_w / 2)
            pdf.set_font(family, "B", 9)
            pdf.set_text_color(*DARK)
            name_w = pdf.get_string_width(cert.name + "  ")
            pdf.cell(name_w, 5, cert.name)
            pdf.set_font(family, "", 8)
            pdf.set_text_color(*GRAY)
            issuer = cert.issuer or ""
            if cert.date:
                issuer += f"  |  {cert.date}"
            pdf.cell(cell_w / 2 - name_w, 5, issuer)
            if i % 2 == 1:
                pdf.ln(5)

    # --- Skills ---
    section("Skills")
    pdf.set_font(family, "", 9)
    pdf.set_text_color(*MID)
    pdf.cell(cell_w, 5, "Languages: Java, Python, TypeScript, JavaScript, C, C++, SQL", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(cell_w, 5, "Frameworks: Spring Boot, Flask, Express, React, Next.js", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(cell_w, 5, "Databases: PostgreSQL, SQLite", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(cell_w, 5, "DevOps: Docker, Git, HCL", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    # --- Projects ---
    if data.projects:
        section("Projects")
        for proj in data.projects:
            pdf.set_font(family, "B", 9)
            pdf.set_text_color(*DARK)
            proj_name = proj.name
            if proj.language:
                proj_name += f"  ({proj.language})"
            pdf.cell(cell_w, 5, proj_name, new_x="LMARGIN", new_y="NEXT")
            if proj.description:
                pdf.set_font(family, "", 8)
                pdf.set_text_color(*GRAY)
                pdf.cell(cell_w, 4, proj.description, new_x="LMARGIN", new_y="NEXT")
            pdf.ln(1)

    # --- Footer ---
    pdf.set_y(-15)
    pdf.set_font(family, "", 7)
    pdf.set_text_color(180, 180, 180)
    pdf.cell(cell_w, 10, f"Generated from portfolio-api  |  Last updated {data.last_updated}", align="C", new_x="LMARGIN", new_y="NEXT")

    return BytesIO(pdf.output())
