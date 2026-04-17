import pytest
import httpx
from unittest.mock import AsyncMock, MagicMock, patch

from services import shorten_url


# Helpers
def _mock_http_response(text: str, status_code: int = 200) -> MagicMock:
    """Build a fake httpx.Response."""
    response = MagicMock()
    response.text = text
    response.status_code = status_code
    response.raise_for_status = MagicMock()   # no-op by default (success)
    return response


def _mock_client(response: MagicMock) -> MagicMock:
    """Wrap a fake response in a fake async context-manager client."""
    client = MagicMock()
    client.get = AsyncMock(return_value=response)
    # Support `async with httpx.AsyncClient() as client:`
    async_cm = MagicMock()
    async_cm.__aenter__ = AsyncMock(return_value=client)
    async_cm.__aexit__  = AsyncMock(return_value=False)
    return async_cm


# ── Tests ──────────────────────────────────────────────────────────────────────

class TestShortenUrlSuccess:

    @pytest.mark.asyncio
    async def test_returns_short_url_on_success(self):
        short = "https://tinyurl.com/abc123"
        mock_cm = _mock_client(_mock_http_response(short))

        with patch("services.httpx.AsyncClient", return_value=mock_cm):
            result = await shorten_url("https://www.example.com/very/long/path")

        assert result == short

    @pytest.mark.asyncio
    async def test_passes_correct_url_to_api(self):
        """The original URL must be forwarded as the `url` query parameter."""
        long_url = "https://www.example.com/page"
        short    = "https://tinyurl.com/xyz"
        mock_response = _mock_http_response(short)
        mock_cm = _mock_client(mock_response)

        with patch("services.httpx.AsyncClient", return_value=mock_cm):
            await shorten_url(long_url)

        # Extract what .get() was called with
        call_kwargs = mock_cm.__aenter__.return_value.get.call_args
        assert call_kwargs.kwargs["params"]["url"] == long_url

    @pytest.mark.asyncio
    async def test_strips_whitespace_from_response(self):
        """TinyURL sometimes returns trailing newlines — we must strip them."""
        short = "https://tinyurl.com/abc123"
        mock_cm = _mock_client(_mock_http_response(f"  {short}\n"))

        with patch("services.httpx.AsyncClient", return_value=mock_cm):
            result = await shorten_url("https://example.com")

        assert result == short


class TestShortenUrlFailures:

    @pytest.mark.asyncio
    async def test_returns_none_on_timeout(self):
        mock_client = MagicMock()
        mock_client.get = AsyncMock(side_effect=httpx.TimeoutException("timed out"))
        async_cm = MagicMock()
        async_cm.__aenter__ = AsyncMock(return_value=mock_client)
        async_cm.__aexit__  = AsyncMock(return_value=False)

        with patch("services.httpx.AsyncClient", return_value=async_cm):
            result = await shorten_url("https://example.com")

        assert result is None

    @pytest.mark.asyncio
    async def test_returns_none_on_http_error(self):
        response = _mock_http_response("", status_code=500)
        response.raise_for_status = MagicMock(
            side_effect=httpx.HTTPStatusError(
                "server error",
                request=MagicMock(),
                response=response,
            )
        )
        mock_cm = _mock_client(response)

        with patch("services.httpx.AsyncClient", return_value=mock_cm):
            result = await shorten_url("https://example.com")

        assert result is None

    @pytest.mark.asyncio
    async def test_returns_none_on_unexpected_response(self):
        """If TinyURL returns something that isn't a URL, return None."""
        mock_cm = _mock_client(_mock_http_response("Error: invalid URL"))

        with patch("services.httpx.AsyncClient", return_value=mock_cm):
            result = await shorten_url("https://example.com")

        assert result is None

    @pytest.mark.asyncio
    async def test_returns_none_on_network_error(self):
        mock_client = MagicMock()
        mock_client.get = AsyncMock(side_effect=Exception("network down"))
        async_cm = MagicMock()
        async_cm.__aenter__ = AsyncMock(return_value=mock_client)
        async_cm.__aexit__  = AsyncMock(return_value=False)

        with patch("services.httpx.AsyncClient", return_value=async_cm):
            result = await shorten_url("https://example.com")

        assert result is None
