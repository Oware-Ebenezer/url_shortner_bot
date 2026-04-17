import pytest
from unittest.mock import AsyncMock, patch

from handlers import (
    cmd_start,
    cmd_help,
    cmd_shorten,
    handle_plain_text,
    _process_url
)

class TestCmdStart:
    @pytest.mark.asyncio
    async def test_replies_once(self, mock_update,mock_context):
        await cmd_start(mock_update, mock_context)
        mock_update.message.reply_text.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_reply_contains_welcome(self,mock_update,mock_context):
        await cmd_start(mock_update, mock_context)
        text = mock_update.message.reply_text.call_args[0][0]
        assert "Welcome" in text
        
    @pytest.mark.asyncio
    async def test_reply_mentions_shorten_command(self, mock_update, mock_context):
        await cmd_start(mock_update, mock_context)
        text = mock_update.message.reply_text.call_args[0][0]
        assert "/shorten" in text
    
    @pytest.mark.asyncio
    async def test_uses_html_parse_mode(self, mock_update, mock_context):
        await cmd_start(mock_update, mock_context)
        kwargs = mock_update.message.reply_text.call_args[1]
        assert "HTML" in str(kwargs.get("parse_mode", ""))
        

# /help 

class TestCmdHelp:

    @pytest.mark.asyncio
    async def test_help_replies_once(self, mock_update, mock_context):
        """/help must produce exactly one reply."""
        await cmd_help(mock_update, mock_context)
        mock_update.message.reply_text.assert_called_once()

    @pytest.mark.asyncio
    async def test_help_same_content_as_start(self, mock_update, mock_context):
        """The /help reply must contain the same welcome text as /start."""
        await cmd_help(mock_update, mock_context)
        text = mock_update.message.reply_text.call_args[0][0]
        assert "Welcome" in text


# /shorten 

class TestCmdShorten:

    @pytest.mark.asyncio
    async def test_no_args_asks_for_url(self, mock_update, make_context):
        """If the user types /shorten with no URL, ask them to provide one."""
        ctx = make_context([])           # empty args
        await cmd_shorten(mock_update, ctx)
        mock_update.message.reply_text.assert_called_once()
        text = mock_update.message.reply_text.call_args[0][0]
        assert "provide" in text.lower() or "example" in text.lower()

    @pytest.mark.asyncio
    async def test_valid_url_arg_triggers_processing(self, mock_update, make_context):
        ctx = make_context(["https://example.com"])
        short = "https://tinyurl.com/abc"

        with patch("handlers.shorten_url", new=AsyncMock(return_value=short)):
            await cmd_shorten(mock_update, ctx)

        # processing_msg.edit_text is called with the short URL
        edit_call = mock_update.message.reply_text.return_value.edit_text
        edit_call.assert_called_once()
        result_text = edit_call.call_args[0][0]
        assert short in result_text

    @pytest.mark.asyncio
    async def test_invalid_url_arg_rejected(self, mock_update, make_context):
        ctx = make_context(["not-a-url"])

        with patch("handlers.shorten_url", new=AsyncMock()) as mock_service:
            await cmd_shorten(mock_update, ctx)
            mock_service.assert_not_called()


# Plain text messages

class TestHandlePlainText:

    @pytest.mark.asyncio
    async def test_valid_url_is_shortened(self, make_update, mock_context):
        update = make_update("https://example.com/long/path")
        short  = "https://tinyurl.com/xyz"

        with patch("handlers.shorten_url", new=AsyncMock(return_value=short)):
            await handle_plain_text(update, mock_context)

        edit_call = update.message.reply_text.return_value.edit_text
        edit_call.assert_called_once()
        assert short in edit_call.call_args[0][0]

    @pytest.mark.asyncio
    async def test_non_url_text_prompts_correction(self, make_update, mock_context):
        """Random text must prompt the user to send a proper URL."""
        update = make_update("hello world")
        await handle_plain_text(update, mock_context)
        text = update.message.reply_text.call_args[0][0]
        assert "http" in text.lower() or "url" in text.lower()

    @pytest.mark.asyncio
    async def test_non_url_does_not_call_service(self, make_update, mock_context):
        update = make_update("just some words")

        with patch("handlers.shorten_url", new=AsyncMock()) as mock_service:
            await handle_plain_text(update, mock_context)
            mock_service.assert_not_called()


# _process_url (shared core logic) 

class TestProcessUrl:

    @pytest.mark.asyncio
    async def test_shows_processing_message(self, mock_update, mock_context):
        short = "https://tinyurl.com/abc"
        with patch("handlers.shorten_url", new=AsyncMock(return_value=short)):
            await _process_url(mock_update, "https://example.com")

        first_reply = mock_update.message.reply_text.call_args[0][0]
        assert "⏳" in first_reply or "Shortening" in first_reply

    @pytest.mark.asyncio
    async def test_edits_message_with_short_url_on_success(self, mock_update, mock_context):
        short = "https://tinyurl.com/success"
        with patch("handlers.shorten_url", new=AsyncMock(return_value=short)):
            await _process_url(mock_update, "https://example.com")

        edit_call = mock_update.message.reply_text.return_value.edit_text
        edit_call.assert_called_once()
        assert short in edit_call.call_args[0][0]

    @pytest.mark.asyncio
    async def test_edits_message_with_error_on_failure(self, mock_update, mock_context):
        """On service failure (None returned) the user must see an error message."""
        with patch("handlers.shorten_url", new=AsyncMock(return_value=None)):
            await _process_url(mock_update, "https://example.com")

        edit_call = mock_update.message.reply_text.return_value.edit_text
        edit_call.assert_called_once()
        result_text = edit_call.call_args[0][0]
        assert "Could not" in result_text

    @pytest.mark.asyncio
    async def test_rejects_invalid_url_before_service(self, mock_update, mock_context):
        """An invalid URL must be rejected immediately — service never called."""
        with patch("handlers.shorten_url", new=AsyncMock()) as mock_service:
            await _process_url(mock_update, "not-a-url")
            mock_service.assert_not_called()
