import httpx

from config import TINYURL_API, HTTP_TIMEOUT
from logger import get_logger

logger = get_logger(__name__)


async def shorten_url(long_url: str) -> str | None:
    try:
        async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
            response = await client.get(TINYURL_API, params={"url": long_url})
            response.raise_for_status()
            short = response.text.strip()
            if short.startswith("http"):
                return short
            logger.warning("Unexpected TinyURL response: %r", short)
    except httpx.TimeoutException:
        logger.warning("TinyURL request timed out for URL: %s", long_url)
    except httpx.HTTPStatusError as exc:
        logger.warning("TinyURL HTTP error %s for URL: %s", exc.response.status_code, long_url)
    except Exception as exc:
        logger.warning("Unexpected error while shortening URL: %s", exc)

    return None
