import asyncio
from datetime import datetime, timezone

from httpx import AsyncClient
from sqlalchemy import select

from app.database import async_session
from app.models import TrendingPost

SOURCE = "devto"
API_URL = "https://dev.to/api/articles?tag=backend&per_page=30"


async def scrape_and_persist() -> int:
    async with AsyncClient(timeout=15) as client:
        try:
            resp = await client.get(API_URL)
            resp.raise_for_status()
            articles = resp.json()
        except Exception as e:
            print(f"[devto-scraper] fetch failed: {e}")
            return 0

    if not articles:
        print("[devto-scraper] no articles found")
        return 0

    async with async_session() as session:
        saved = 0
        for article in articles:
            source_id = str(article.get("id", ""))
            if not source_id:
                continue

            existing = await session.execute(
                select(TrendingPost).where(
                    TrendingPost.source == SOURCE,
                    TrendingPost.source_id == source_id,
                )
            )
            row = existing.scalar_one_or_none()

            created_at = None
            if article.get("published_at"):
                try:
                    created_at = datetime.fromisoformat(
                        article["published_at"].replace("Z", "+00:00")
                    )
                except (ValueError, TypeError):
                    pass

            tags = article.get("tag_list", [])

            if row:
                row.title = article.get("title", "")
                row.url = article.get("url")
                row.points = article.get("positive_reactions_count", 0)
                row.comment_count = article.get("comments_count", 0)
                row.author = article.get("user", {}).get("name") if article.get("user") else None
                row.created_at = created_at
                row.topic_tags = tags
            else:
                if not created_at:
                    created_at = datetime.now(timezone.utc)
                session.add(
                    TrendingPost(
                        source=SOURCE,
                        source_id=source_id,
                        title=article.get("title", ""),
                        url=article.get("url"),
                        points=article.get("positive_reactions_count", 0),
                        comment_count=article.get("comments_count", 0),
                        author=article.get("user", {}).get("name") if article.get("user") else None,
                        created_at=created_at,
                        topic_tags=tags,
                    )
                )
            saved += 1

        await session.commit()
        print(f"[devto-scraper] saved/updated {saved} articles")
        return saved


def main():
    asyncio.run(scrape_and_persist())


if __name__ == "__main__":
    main()
