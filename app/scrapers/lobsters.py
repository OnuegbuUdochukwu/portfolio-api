import asyncio
from datetime import datetime, timezone

from httpx import AsyncClient
from sqlalchemy import select

from app.database import async_session
from app.models import TrendingPost

SOURCE = "lobsters"
API_URL = "https://lobste.rs/hottest.json"


async def scrape_and_persist() -> int:
    async with AsyncClient(timeout=15) as client:
        try:
            resp = await client.get(API_URL)
            resp.raise_for_status()
            posts = resp.json()
        except Exception as e:
            print(f"[lobsters-scraper] fetch failed: {e}")
            return 0

    if not posts:
        print("[lobsters-scraper] no posts found")
        return 0

    async with async_session() as session:
        saved = 0
        for post in posts:
            source_id = str(post.get("short_id", ""))
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
            if post.get("created_at"):
                try:
                    created_at = datetime.fromisoformat(
                        post["created_at"].replace("Z", "+00:00")
                    )
                except (ValueError, TypeError):
                    pass

            tags = [t for t in post.get("tags", []) if t]

            if row:
                row.title = post.get("title", "")
                row.url = post.get("url")
                row.points = post.get("score", 0)
                row.comment_count = post.get("comment_count", 0)
                row.author = post.get("submitter_user", {}).get("display_username")
                row.created_at = created_at
                row.topic_tags = tags
            else:
                if not created_at:
                    created_at = datetime.now(timezone.utc)
                session.add(
                    TrendingPost(
                        source=SOURCE,
                        source_id=source_id,
                        title=post.get("title", ""),
                        url=post.get("url"),
                        points=post.get("score", 0),
                        comment_count=post.get("comment_count", 0),
                        author=post.get("submitter_user", {}).get("display_username"),
                        created_at=created_at,
                        topic_tags=tags,
                    )
                )
            saved += 1

        await session.commit()
        print(f"[lobsters-scraper] saved/updated {saved} posts")
        return saved


def main():
    asyncio.run(scrape_and_persist())


if __name__ == "__main__":
    main()
