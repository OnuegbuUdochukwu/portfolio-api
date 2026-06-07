from cachetools import TTLCache
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import TrendingPost
from app.schemas import TrendingPostSchema

CACHE_TTL = 300

router = APIRouter(prefix="/api/trending", tags=["trending"])
cache = TTLCache(maxsize=1, ttl=CACHE_TTL)


@router.get("")
async def get_trending(
    limit: int = Query(default=10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    cache_key = f"trending_{limit}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    try:
        result = await db.execute(
            select(TrendingPost)
            .where(TrendingPost.is_visible == True)  # noqa: E712
            .order_by(desc(TrendingPost.points))
            .limit(limit)
        )
        posts = result.scalars().all()
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=503, detail=f"Database unavailable: {e}")

    data = [
        TrendingPostSchema(
            id=p.id,
            hn_id=p.hn_id,
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
