import asyncio
import logging
from tavily import AsyncTavilyClient
from backend.config import settings

logger = logging.getLogger(__name__)

_client = AsyncTavilyClient(api_key=settings.tavily_api_key)
_semaphore = asyncio.Semaphore(3)


async def search(query: str, max_results: int = 5) -> list[dict]:
    async with _semaphore:
        try:
            response = await asyncio.wait_for(
                _client.search(
                    query=query,
                    max_results=max_results,
                    search_depth="basic",
                    include_answer=True,
                ),
                timeout=15.0,
            )
            results = response.get("results", [])
            return [
                {
                    "title": r.get("title", ""),
                    "url": r.get("url", ""),
                    "content": r.get("content", ""),
                    "score": r.get("score", 0.0),
                }
                for r in results
            ]
        except asyncio.TimeoutError:
            logger.warning(f"Tavily timeout for query: {query[:80]}")
            return []
        except Exception as e:
            logger.warning(f"Tavily error ({type(e).__name__}): {e}")
            return []


async def search_many(queries: list[str], max_results: int = 5) -> list[list[dict]]:
    """Run multiple searches concurrently, throttled to 3 at a time."""
    return await asyncio.gather(*[search(q, max_results) for q in queries])
