from logger import setup_logging, get_logger
from bot import create_app

from telegram import Update


def main() -> None:
    setup_logging()
    logger = get_logger(__name__)

    app = create_app()

    logger.info("Bot is running. Press Ctrl+C to stop.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
