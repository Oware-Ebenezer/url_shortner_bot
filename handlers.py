
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from services import shorten_url
from utils import is_valid_url


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
   
    await update.message.reply_text(
        "<b>Welcome to Bingi Bot URL Shortener Bot!</b>\n\n"
        "Created by Ebenezer Kwabena Oware under <b>PIXEL&LOGIC community</b>\n\n"
        "To perform a simple task, just send me any long URL and I'll shrink it for you.\n"
        "Send me any long URL and I'll shrink it for you.\n\n"
        "Commands:\n"
        "• /shorten &lt;url&gt; — shorten a specific URL\n"
        "• /help — show this message",
        parse_mode=ParseMode.HTML,
    )


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await cmd_start(update, context)


async def cmd_shorten(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text(
            "Please provide a URL after the command.\n"
            "Example: <code>/shorten https://www.example.com/very/long/path</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    await _process_url(update, context.args[0])


async def handle_plain_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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
    from logger import get_logger
    logger = get_logger(__name__)
    logger.error("Unhandled exception: %s", context.error, exc_info=context.error)


# Private helpers 

async def _process_url(update: Update, url: str) -> None:
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
            "Could not shorten that URL right now. "
            "Please check the link and try again in a moment."
        )