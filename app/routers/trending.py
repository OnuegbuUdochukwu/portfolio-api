from cachetools import TTLCache
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import TrendingPost
from app.schemas import TrendingPostSchema

CACHE_TTL = 300

router = APIRouter(prefix="/api/trending", tags=["trending"])
cache = TTLCache(maxsize=8, ttl=CACHE_TTL)


@router.get("")
async def get_trending(
    limit: int = Query(default=10, ge=1, le=50),
    source: str = Query(default="all", description="Filter by source: hackernews, lobsters, devto, reddit, or all"),
    db: AsyncSession = Depends(get_db),
):
    cache_key = f"trending_{limit}_{source}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    try:
        query = (
            select(TrendingPost)
            .where(TrendingPost.is_visible == True)  # noqa: E712
            .order_by(desc(TrendingPost.points))
            .limit(limit)
        )
        if source != "all":
            query = query.where(TrendingPost.source == source)

        result = await db.execute(query)
        posts = result.scalars().all()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database unavailable: {e}")

    data = [
        TrendingPostSchema(
            id=p.id,
            source_id=p.source_id,
            source=p.source,
            title=p.title,
            url=p.url,
            points=p.points or 0,
            comment_count=p.comment_count or 0,
            author=p.author,
            created_at=p.created_at.isoformat() if p.created_at else None,
            scraped_at=p.scraped_at.isoformat() if p.scraped_at else None,
            topic_tags=p.topic_tags or [],
        )
        for p in posts
    ]

    cache[cache_key] = data
    return data
