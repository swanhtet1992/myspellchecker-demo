"""Format myspellchecker results as Telegram HTML messages."""

from __future__ import annotations

import html


def format_check_result(
    original: str, corrected: str, changes: list[tuple[str, str]]
) -> str:
    """Format spellcheck result with blockquote for easy copying."""
    if not changes:
        return (
            "✓ <b>အမှားမတွေ့ပါ</b>\n\n"
            f"<blockquote>{html.escape(original)}</blockquote>"
        )

    lines = [f"<blockquote>{html.escape(corrected)}</blockquote>"]
    lines.append("")
    lines.append("── ပြင်ဆင်ချက်များ ──")
    for orig_word, fixed_word in changes:
        orig_esc = html.escape(orig_word) if orig_word else "(ထည့်သွင်း)"
        fixed_esc = html.escape(fixed_word) if fixed_word else "(ဖယ်ရှား)"
        lines.append(f"  <s>{orig_esc}</s> → <b>{fixed_esc}</b>")

    return "\n".join(lines)


def format_segment_result(segments: list[tuple[str, str]]) -> str:
    """Format segmentation result with POS tags."""
    if not segments:
        return "စာသားကို ခွဲခြမ်းစိတ်ဖြာ မရပါ။"

    parts = []
    for word, tag in segments:
        parts.append(f"<b>{html.escape(word)}</b>  [{html.escape(tag)}]")

    return "  |  ".join(parts)


def format_zawgyi_result(is_zawgyi: bool, converted: str) -> str:
    """Format Zawgyi detection/conversion result."""
    if is_zawgyi:
        return (
            "⚠ <b>ဇော်ဂျီ ဖြစ်နေပါသည်</b>\n\n"
            "Unicode သို့ ပြောင်းထားသော စာသား -\n"
            f"<blockquote>{html.escape(converted)}</blockquote>"
        )
    return "✓ <b>Unicode စာသား ဖြစ်ပါသည်</b> (ဇော်ဂျီ မဟုတ်ပါ)"


def format_no_text() -> str:
    """Message when no text is provided to a command."""
    return "စာသား ထည့်ပါ။\n\nUsage: /segment မြန်မာစာသား\nသို့မဟုတ် စာတစ်ခုကို reply လုပ်ပါ။"
