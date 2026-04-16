from telegram import Update
from telegram.ext import ContextTypes

from services import shorten_url
from utils import is_valid_url

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "*Welcome to URL Shortner Bot!*\n\n"
        "I am Bingi_bot, created by Oware Ebenezer Kwabena\n"
        "To perform a simple task, just send me any long URL and I'll shrink it for you.\n"
        "Commands:\n"
        "• /shorten `<url>` — shorten a specific URL\n"
        "• /help — show this message",
        parse_mode="Markdown",
    )
    
async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help — reuse the start message."""
    await cmd_start(update, context)


async def cmd_shorten(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /shorten <url> — extract the URL argument and process it."""
    if not context.args:
        await update.message.reply_text(
            "Please provide a URL after the command.\n"
            "Example: `/shorten https://www.example.com/very/long/path`",
            parse_mode="Markdown",
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
            "That doesn't look like a URL. "
            "Please send a full link starting with `https://` or `http://`.",
            parse_mode="Markdown",
        )


from logger import get_logger


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Catch and log any unhandled exception so the bot never crashes silently."""
    logger = get_logger(__name__)
    logger.error("Unhandled exception: %s", context.error, exc_info=context.error)


# ── Private helpers ────────────────────────────────────────────────────────────

async def _process_url(update: Update, url: str) -> None:
    """
    Core flow shared by both the /shorten command and plain-text handler:
    Assumes URL is already validated by caller.
      1. Show a processing indicator
      2. Call the service layer
      3. Edit the message in-place with the result
    """
    processing_msg = await update.message.reply_text("Shortening your URL…")
    short_url = await shorten_url(url)

    if short_url:
        await processing_msg.edit_text(
            f"Here's your short URL:\n\n`{short_url}`",
            parse_mode="Markdown",
        )
    else:
        await processing_msg.edit_text(
            "Could not shorten that URL right now. "
            "Please check the link and try again in a moment."
        )
