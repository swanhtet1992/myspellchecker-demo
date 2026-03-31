"""Telegram bot handlers for mySpellChecker."""

from __future__ import annotations

import logging

from telegram import InlineQueryResultArticle, InputTextMessageContent, Update
from telegram.ext import ContextTypes

from bot.checker import check, detect_zawgyi, segment
from bot.formatter import (
    format_check_result,
    format_no_text,
    format_segment_result,
    format_zawgyi_result,
)
from bot.rate_limit import check_rate_limit

logger = logging.getLogger(__name__)

MAX_TEXT_LENGTH = 10_000
TELEGRAM_MSG_LIMIT = 4096


# -- /start and /help --


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send welcome message."""
    await update.message.reply_text(
        "🇲🇲 <b>mySpellChecker Bot</b>\n\n"
        "စာလုံးပေါင်းသတ်ပုံ စစ်ဆေးရန် မြန်မာစာ ရိုက်ထည့်ပါ။\n\n"
        "<b>Commands:</b>\n"
        "/segment - စာလုံးခွဲခြင်း (Word segmentation)\n"
        "/zawgyi - ဇော်ဂျီ စစ်ဆေးပြောင်းလဲခြင်း\n\n"
        "သို့မဟုတ် မည်သည့် chat မှမဆို inline mode သုံးပါ။\n\n"
        "<i>Powered by</i> <b>myspellchecker</b> · "
        "<code>pip install myspellchecker</code>",
        parse_mode="HTML",
    )


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send help message (same as start)."""
    await start(update, context)


# -- Default text handler (spellcheck) --


async def check_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Spell-check any text message sent to the bot."""
    user_id = update.effective_user.id
    if not check_rate_limit(user_id):
        await update.message.reply_text("ခဏစောင့်ပါ။ Too many requests.")
        return

    text = update.message.text
    if len(text) > MAX_TEXT_LENGTH:
        await update.message.reply_text(
            f"စာသား ရှည်လွန်းပါသည်။ ({MAX_TEXT_LENGTH:,} char limit)"
        )
        return

    try:
        result = check(text)
    except Exception:
        logger.exception("Spellcheck failed")
        await update.message.reply_text("စစ်ဆေး၍ မရပါ။ နောက်မှ ထပ်ကြိုးစားပါ။")
        return

    msg = format_check_result(text, result["corrected"], result["changes"])
    await _send_long_message(update, msg)


# -- /segment --


async def segment_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Segment Myanmar text into words with POS tags."""
    text = _extract_text(update, context)
    if not text:
        await update.message.reply_text(format_no_text(), parse_mode="HTML")
        return

    try:
        result = segment(text)
    except Exception:
        logger.exception("Segmentation failed")
        await update.message.reply_text("ခွဲခြမ်းစိတ်ဖြာ၍ မရပါ။ နောက်မှ ထပ်ကြိုးစားပါ။")
        return

    msg = format_segment_result(result)
    await _send_long_message(update, msg)


# -- /zawgyi --


async def zawgyi_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Detect and convert Zawgyi text to Unicode."""
    text = _extract_text(update, context)
    if not text:
        await update.message.reply_text(format_no_text(), parse_mode="HTML")
        return

    try:
        is_zawgyi, converted = detect_zawgyi(text)
    except Exception:
        logger.exception("Zawgyi detection failed")
        await update.message.reply_text("စစ်ဆေး၍ မရပါ။ နောက်မှ ထပ်ကြိုးစားပါ။")
        return

    msg = format_zawgyi_result(is_zawgyi, converted)
    await update.message.reply_text(msg, parse_mode="HTML")


# -- Inline mode --


async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle inline queries — users type @botname <text> in any chat."""
    query = update.inline_query.query
    if not query or len(query) < 2:
        return

    try:
        result = check(query)
    except Exception:
        logger.exception("Inline spellcheck failed")
        return

    corrected = result["corrected"]
    if result["has_errors"]:
        title = f"✓ {corrected}"
        description = f"မူရင်း: {query}"
    else:
        title = "✓ အမှားမရှိပါ"
        description = query

    results = [
        InlineQueryResultArticle(
            id="corrected",
            title=title,
            description=description,
            input_message_content=InputTextMessageContent(corrected),
        )
    ]
    await update.inline_query.answer(results, cache_time=60)


# -- Helpers --


def _extract_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str | None:
    """Extract text from command arguments or reply-to message."""
    if context.args:
        return " ".join(context.args)
    if update.message.reply_to_message and update.message.reply_to_message.text:
        return update.message.reply_to_message.text
    return None


async def _send_long_message(update: Update, msg: str) -> None:
    """Send a message, splitting at Myanmar sentence boundaries if too long."""
    if len(msg) <= TELEGRAM_MSG_LIMIT:
        await update.message.reply_text(msg, parse_mode="HTML")
        return

    # Split at Myanmar full stop (။) boundaries
    sentences = msg.split("။")
    chunk = ""
    for i, sentence in enumerate(sentences):
        sep = "။" if i < len(sentences) - 1 else ""
        candidate = chunk + sentence + sep
        if len(candidate) > TELEGRAM_MSG_LIMIT and chunk:
            await update.message.reply_text(chunk, parse_mode="HTML")
            chunk = sentence + sep
        else:
            chunk = candidate

    if chunk.strip():
        await update.message.reply_text(chunk, parse_mode="HTML")
