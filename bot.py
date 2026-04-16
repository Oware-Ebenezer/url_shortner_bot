
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
)

from config import BOT_TOKEN
from handlers import (
    cmd_start,
    cmd_help,
    cmd_shorten,
    handle_plain_text,
    error_handler,
)


def create_app() -> Application:
    """
    Build and return a fully configured Telegram Application.
    Raises ValueError if BOT_TOKEN is missing.
    """
    if not BOT_TOKEN:
        raise ValueError(
            "BOT_TOKEN environment variable is not set.\n"
            "Get a token from @BotFather on Telegram, then run:\n"
            "  export BOT_TOKEN='your_token_here'"
        )

    app = Application.builder().token(BOT_TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start",   cmd_start))
    app.add_handler(CommandHandler("help",    cmd_help))
    app.add_handler(CommandHandler("shorten", cmd_shorten))

    # Plain text messages (URLs sent without a command)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_plain_text))

    # Global error handler
    app.add_error_handler(error_handler)

    return app
