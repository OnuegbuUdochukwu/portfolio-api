from asyncio import run

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.config import DATABASE_URL
from app.models import Base, Experience, Education, Certification, Project


async def seed():
    engine = create_async_engine(DATABASE_URL, echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with session_factory() as session:
        session.add_all([
            Experience(
                company="Quidax",
                role="Backend Developer Intern",
                period="Mar 2025 - Sep 2025",
                type="Internship \u00b7 Hybrid",
                description="Built and integrated REST APIs for cryptocurrency platforms using Java and Spring Boot. Collaborated on designing secure data flow pipelines and gained hands-on experience with production backend systems.",
                highlights=[
                    "Built 7+ Spring Boot microservices including crypto converter, market depth visualizer, and trade feed APIs",
                    "Integrated Quidax REST API for real-time price data, wallet balances, and order management",
                    "Wrote authenticated API integrations handling secure key storage and request signing",
                ],
                tags=["Java", "Spring Boot", "REST APIs", "Cryptocurrency"],
                sort_order=0,
            ),
            Experience(
                company="Chequebase",
                role="Backend Intern",
                period="2024",
                type="Internship",
                description="Worked with the backend team to integrate and optimize APIs ensuring seamless system communication. Conducted usability testing and contributed to improving user interfaces.",
                highlights=[
                    "Collaborated on API integration and optimization for cross-system communication",
                    "Conducted usability testing to improve UI/UX for end users",
                    "Debugged real-world backend issues in a sprint-based environment",
                ],
                tags=["API Development", "Backend", "Testing"],
                sort_order=1,
            ),
            Experience(
                company="Cowrywise",
                role="CowryWise Ambassador",
                period="Nov 2025 - Dec 2025",
                type="Ambassador",
                description="Represented Cowrywise on campus, promoting financial literacy and the platform's savings/investment products to students.",
                highlights=[
                    "Promoted financial literacy and investment awareness among university students",
                ],
                tags=["Fintech", "Community"],
                sort_order=2,
            ),
        ])

        session.add(
            Education(
                school="Covenant University",
                degree="Bachelor of Computer Science",
                location="Ota, Ogun State",
                period="Sep 2022 - Present",
                gpa="4.89 / 5.00",
                details=[
                    "Member, Nigerian Association of Computing Students (NACOS)",
                    "Coursework: Structured Programming, Database Management, Operating Systems",
                ],
            )
        )

        session.add_all([
            Certification(name="Responsive Web Design", issuer="freeCodeCamp", date="Dec 2023"),
            Certification(name="CS50 Introduction to Programming with Python", issuer="Harvard / CS50", date="2024"),
            Certification(name="Discover the Art of Prompting", issuer="Google", date="Sep 2025"),
            Certification(name="Start Writing Prompts like a Pro", issuer="Google", date="Sep 2025"),
        ])

        session.add_all([
            Project(name="Telegram Complaint System", description="A communication platform for managing complaints directly through Telegram, enabling faster response rates.", language="Python", tags=["Python", "PostgreSQL", "Docker", "Telegram API"], github_url="https://github.com/OnuegbuUdochukwu/telegram-complaint-system", category="Full Stack", sort_order=0),
            Project(name="Cryptocurrency Price Ticker", description="Real-time cryptocurrency price tracking platform powered entirely by Java, integrating with Quidax APIs.", language="Java", tags=["Java", "Spring Boot", "Quidax API", "Real-time"], github_url="https://github.com/OnuegbuUdochukwu/Cryptocurrency-Price-Ticker", category="Backend", sort_order=1),
            Project(name="Dynamic Portfolio", description="Multi-language portfolio showcasing projects with a Java backend, TypeScript interactivity, and Python scripting.", language="Java", tags=["Java", "TypeScript", "Python", "Full Stack"], github_url="https://github.com/OnuegbuUdochukwu/Dynamic_Portfolio", category="Full Stack", sort_order=2),
            Project(name="Water Cooler Network", description="Digital networking platform for remote and hybrid workers.", language="Java", tags=["Java", "Spring Boot", "Social", "Real-time"], github_url="https://github.com/OnuegbuUdochukwu/water-cooler-network", category="Backend", sort_order=3),
            Project(name="Facial Emotion Detection", description="Real-time facial emotion detection using a Convolutional Neural Network classifying 7 emotion categories.", language="Python", tags=["Python", "CNN", "Deep Learning", "Computer Vision"], github_url="https://github.com/OnuegbuUdochukwu/ONUEGBU--22CG031937", category="AI/ML", sort_order=4),
            Project(name="Intelligent Career Optimizer", description="Analyzes resumes against job market data and computes the shortest path to a target role.", language="Python", tags=["Python", "Graph Algorithms", "ML", "Career Tech"], github_url="https://github.com/OnuegbuUdochukwu/intelligent-career-optimizer", category="AI/ML", sort_order=5),
            Project(name="Pathfinder", description="Visualizing search algorithms - BFS, DFS, Dijkstra, A*.", language="Python", tags=["Python", "Algorithms", "Visualization"], github_url="https://github.com/OnuegbuUdochukwu/pathfinder", category="Tooling", sort_order=6),
        ])

        await session.commit()

    await engine.dispose()
    print("Database seeded successfully.")


if __name__ == "__main__":
    run(seed())
