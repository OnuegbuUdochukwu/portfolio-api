import asyncio
import re
from datetime import datetime, timezone

from httpx import AsyncClient
from sqlalchemy import select

from app.database import async_session
from app.models import TrendingPost

SOURCE = "reddit"
SUBREDDITS = ["programming", "backend"]
API_URL = "https://www.reddit.com/r/{}/hot/.json?limit=25"
HEADERS = {"User-Agent": "portfolio-api/0.1 (backend engineer portfolio scraper)"}

BACKEND_KEYWORDS = [
    "backend", "api", "rest", "graphql", "grpc",
    "database", "postgresql", "postgres", "sql", "nosql", "redis", "mongodb", "sqlite",
    "docker", "kubernetes", "container", "k8s",
    "microservice", "distributed", "message queue", "kafka", "rabbitmq",
    "server", "lambda", "cloud", "aws", "gcp", "azure", "deploy",
    "python", "rust", "go", "golang", "java", "c++", "typescript", "node",
    "framework", "spring", "django", "fastapi", "flask", "express", "nextjs",
    "testing", "ci/cd", "pipeline",
    "authentication", "authorization", "oauth", "jwt", "security",
    "performance", "optimization", "caching", "scalab",
    "monitoring", "observability", "logging", "tracing",
    "orm", "migration", "schema", "indexing", "query",
    "websocket", "realtime", "streaming", "event-driven",
    "architecture", "system design", "design pattern",
    "devops", "infrastructure", "terraform", "ansible", "nginx", "proxy",
    "concurrency", "parallelism", "async",
]


def _match_keywords(title: str) -> list[str]:
    lower = title.lower()
    matched = []
    for kw in BACKEND_KEYWORDS:
        pattern = re.escape(kw)
        if re.search(rf"\b{pattern}\b", lower):
            matched.append(kw)
    return matched


async def scrape_and_persist() -> int:
    total_saved = 0
    seen_ids: set[str] = set()

    async with AsyncClient(timeout=15, headers=HEADERS) as client:
        for subreddit in SUBREDDITS:
            try:
                resp = await client.get(API_URL.format(subreddit))
                resp.raise_for_status()
                body = resp.json()
            except Exception as e:
                print(f"[reddit-scraper] r/{subreddit} failed: {e}")
                continue

            children = body.get("data", {}).get("children", [])
            for child in children:
                data = child.get("data", {})
                source_id = data.get("id", "")
                if not source_id or source_id in seen_ids:
                    continue
                seen_ids.add(source_id)

                title = data.get("title", "")
                tags = _match_keywords(title)
                if not tags:
                    continue

                created_utc = data.get("created_utc")
                created_at = (
                    datetime.fromtimestamp(created_utc, tz=timezone.utc)
                    if created_utc else None
                )

                async with async_session() as session:
                    row = await session.execute(
                        select(TrendingPost).where(
                            TrendingPost.source == SOURCE,
                            TrendingPost.source_id == source_id,
                        )
                    )
                    existing = row.scalar_one_or_none()

                    permalink = data.get("permalink", "")
                    url = data.get("url") or f"https://www.reddit.com{permalink}"

                    if existing:
                        existing.title = title
                        existing.url = url
                        existing.points = data.get("score", 0)
                        existing.comment_count = data.get("num_comments", 0)
                        existing.author = data.get("author")
                        existing.created_at = created_at
                        existing.topic_tags = tags
                    else:
                        if not created_at:
                            created_at = datetime.now(timezone.utc)
                        session.add(
                            TrendingPost(
                                source=SOURCE,
                                source_id=source_id,
                                title=title,
                                url=url,
                                points=data.get("score", 0),
                                comment_count=data.get("num_comments", 0),
                                author=data.get("author"),
                                created_at=created_at,
                                topic_tags=tags,
                            )
                        )
                    total_saved += 1
                    await session.commit()

    print(f"[reddit-scraper] saved/updated {total_saved} posts")
    return total_saved


def main():
    asyncio.run(scrape_and_persist())


if __name__ == "__main__":
    main()
