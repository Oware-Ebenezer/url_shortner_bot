"""
handlers.py
-----------
All Telegram update handlers live here.
Each handler is a single async function that reads from the update,
calls the service layer, and writes back to Telegram.
No config, no regex, no HTTP — only bot interaction logic.

NOTE: All messages use ParseMode.HTML instead of Markdown.
HTML is stricter and more predictable — Telegram's Markdown parser
breaks on characters like < > _ * inside inline code spans.
HTML formatting tags: <b>bold</b>  <i>italic</i>  <code>monospace</code>
"""

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from services import shorten_url
from utils import is_valid_url


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start — send a welcome message explaining how to use the bot."""
    await update.message.reply_text(
        "<b>Welcome to Bingi Bot Shortener Bot!</b>\n\n"
        "Created by Ebenezer Kwabena Oware\n\n"
        "To perform a simple task, just send me any long URL and I'll shrink it for you.\n\n"
        "Send me any long URL and I'll shrink it for you.\n\n"
        "Commands:\n"
        "• /shorten &lt;url&gt; — shorten a specific URL\n"
        "• /help — show this message",
        parse_mode=ParseMode.HTML,
    )


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help — reuse the start message."""
    await cmd_start(update, context)


async def cmd_shorten(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /shorten <url> — extract the URL argument and process it."""
    if not context.args:
        await update.message.reply_text(
            "Please provide a URL after the command.\n"
            "Example: <code>/shorten https://www.example.com/very/long/path</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    await _process_url(update, context.args[0])


async def handle_plain_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle plain text messages (not commands).
    If the message looks like a URL, shorten it.
    Otherwise prompt the user to send a proper link.
    """
    text = update.message.text.strip()

    if is_valid_url(text):
        await _process_url(update, text)
    else:
        await update.message.reply_text(
            "That doesn't look like a URL.\n"
            "Please send a full link starting with <code>https://</code> or <code>http://</code>.",
            parse_mode=ParseMode.HTML,
        )


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Catch and log any unhandled exception so the bot never crashes silently."""
    from logger import get_logger
    logger = get_logger(__name__)
    logger.error("Unhandled exception: %s", context.error, exc_info=context.error)


# ── Private helpers ────────────────────────────────────────────────────────────

async def _process_url(update: Update, url: str) -> None:
    """
    Core flow shared by both the /shorten command and plain-text handler:
      1. Validate the URL
      2. Show a processing indicator
      3. Call the service layer
      4. Edit the message in-place with the result
    """
    if not is_valid_url(url):
        await update.message.reply_text(
            "Invalid URL. Make sure it starts with <code>https://</code> or <code>http://</code>.",
            parse_mode=ParseMode.HTML,
        )
        return

    processing_msg = await update.message.reply_text("⏳ Shortening your URL…")
    short_url = await shorten_url(url)

    if short_url:
        await processing_msg.edit_text(
            f"✅ Here's your short URL:\n\n<code>{short_url}</code>",
            parse_mode=ParseMode.HTML,
        )
    else:
        await processing_msg.edit_text(
            "❌ Could not shorten that URL right now. "
            "Please check the link and try again in a moment."
        )