from datetime import datetime, timezone

from cachetools import TTLCache
from fastapi import APIRouter, HTTPException
from httpx import AsyncClient

from app.config import LEETCODE_USERNAME

LEETCODE_GRAPHQL = "https://leetcode.com/graphql"
CACHE_TTL = 1800

cache = TTLCache(maxsize=1, ttl=CACHE_TTL)

QUERY = """
query userPublicProfile($username: String!) {
  matchedUser(username: $username) {
    username
    submitStats: submitStatsGlobal {
      acSubmissionNum {
        difficulty
        count
      }
    }
    profile {
      ranking
    }
  }
}
"""

router = APIRouter(prefix="/api/leetcode", tags=["leetcode"])


def _build_response(data: dict) -> dict:
    matched = data.get("matchedUser")
    if not matched:
        raise ValueError("User not found")

    stats = matched.get("submitStats", {}).get("acSubmissionNum", [])
    solved = {s["difficulty"]: s["count"] for s in stats}

    return {
        "totalSolved": solved.get("All", 0),
        "easySolved": solved.get("Easy", 0),
        "mediumSolved": solved.get("Medium", 0),
        "hardSolved": solved.get("Hard", 0),
        "ranking": matched.get("profile", {}).get("ranking", 0),
        "lastUpdated": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/stats")
async def get_leetcode_stats():
    cached = cache.get(LEETCODE_USERNAME)
    if cached is not None:
        return cached

    try:
        async with AsyncClient(timeout=10) as client:
            resp = await client.post(
                LEETCODE_GRAPHQL,
                json={"query": QUERY, "variables": {"username": LEETCODE_USERNAME}},
                headers={"Content-Type": "application/json"},
            )
            resp.raise_for_status()
            body = resp.json()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"LeetCode API request failed: {e}")

    if "errors" in body:
        raise HTTPException(status_code=502, detail=f"LeetCode API error: {body['errors']}")

    try:
        result = _build_response(body.get("data", {}))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    cache[LEETCODE_USERNAME] = result
    return result
