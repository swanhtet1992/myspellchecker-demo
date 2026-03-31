"""mySpellChecker Telegram Bot — entry point."""

from __future__ import annotations

import logging
import os
import sys

from telegram.ext import (
    Application,
    CommandHandler,
    InlineQueryHandler,
    MessageHandler,
    filters,
)

from bot.handlers import (
    check_text,
    help_cmd,
    inline_query,
    segment_cmd,
    start,
    zawgyi_cmd,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def main() -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN environment variable is not set")
        sys.exit(1)

    app = Application.builder().token(token).build()

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("segment", segment_cmd))
    app.add_handler(CommandHandler("zawgyi", zawgyi_cmd))

    # Default: spell-check any text message
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_text))

    # Inline mode
    app.add_handler(InlineQueryHandler(inline_query))

    logger.info("Bot started")
    app.run_polling()


if __name__ == "__main__":
    main()
