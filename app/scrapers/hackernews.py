import asyncio
import re
from datetime import datetime

from httpx import AsyncClient
from sqlalchemy import select

from app.database import async_session
from app.models import TrendingPost

SOURCE = "hackernews"
HN_API = "https://hn.algolia.com/api/v1/search?tags=front_page&hitsPerPage=30"

BACKEND_KEYWORDS = [
    "backend", "api", "rest", "graphql", "grpc",
    "database", "postgresql", "postgres", "sql", "nosql", "redis", "mongodb", "sqlite",
    "docker", "kubernetes", "container", "k8s",
    "microservice", "distributed", "message queue", "kafka", "rabbitmq",
    "server", "lambda", "cloud", "aws", "gcp", "azure", "deploy",
    "python", "rust", "go", "golang", "java", "c++", "typescript", "node",
    "framework", "spring", "django", "fastapi", "flask", "express", "nextjs",
    "testing", "unit test", "integration test", "ci/cd", "pipeline",
    "authentication", "authorization", "oauth", "jwt", "security",
    "performance", "optimization", "caching", "load balancing", "scalab",
    "monitoring", "observability", "logging", "tracing", "telemetry",
    "orm", "migration", "schema", "indexing", "query",
    "websocket", "realtime", "streaming", "event-driven", "event sourcing",
    "architecture", "system design", "design pattern", "solid", "clean architecture",
    "devops", "infrastructure", "terraform", "ansible", "nginx", "proxy",
    "functional programming", "concurrency", "parallelism", "async",
]


def _match_keywords(title: str) -> list[str]:
    lower = title.lower()
    matched = []
    for kw in BACKEND_KEYWORDS:
        pattern = re.escape(kw)
        if re.search(rf"\b{pattern}\b", lower):
            matched.append(kw)
    return matched


async def scrape_and_persist(max_pages: int = 1) -> int:
    all_hits: list[dict] = []
    async with AsyncClient(timeout=15) as client:
        for page in range(max_pages):
            url = f"{HN_API}&page={page}"
            try:
                resp = await client.get(url)
                resp.raise_for_status()
                body = resp.json()
                all_hits.extend(body.get("hits", []))
            except Exception as e:
                print(f"[hn-scraper] page {page} failed: {e}")
                break

    matched_hits: list[dict] = []
    for hit in all_hits:
        title = hit.get("title", "")
        tags = _match_keywords(title)
        if tags:
            hit["_topic_tags"] = tags
            matched_hits.append(hit)

    if not matched_hits:
        print("[hn-scraper] no matching posts found")
        return 0

    async with async_session() as session:
        saved = 0
        for hit in matched_hits:
            source_id = str(hit["objectID"])
            existing = await session.execute(
                select(TrendingPost).where(
                    TrendingPost.source == SOURCE,
                    TrendingPost.source_id == source_id,
                )
            )
            row = existing.scalar_one_or_none()

            created_at = None
            if hit.get("created_at"):
                try:
                    created_at = datetime.fromisoformat(
                        hit["created_at"].replace("Z", "+00:00")
                    )
                except (ValueError, TypeError):
                    pass

            if row:
                row.title = hit["title"]
                row.url = hit.get("url")
                row.points = hit.get("points", 0)
                row.comment_count = hit.get("num_comments", 0)
                row.author = hit.get("author")
                row.created_at = created_at
                row.topic_tags = hit["_topic_tags"]
            else:
                session.add(
                    TrendingPost(
                        source=SOURCE,
                        source_id=source_id,
                        title=hit["title"],
                        url=hit.get("url"),
                        points=hit.get("points", 0),
                        comment_count=hit.get("num_comments", 0),
                        author=hit.get("author"),
                        created_at=created_at,
                        topic_tags=hit["_topic_tags"],
                    )
                )
            saved += 1

        await session.commit()
        print(f"[hn-scraper] saved/updated {saved} posts")
        return saved


def main():
    asyncio.run(scrape_and_persist())


if __name__ == "__main__":
    main()
