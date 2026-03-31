"""Wrapper around myspellchecker library."""

from __future__ import annotations

import difflib
import logging

from myspellchecker.core import ConfigPresets, SpellCheckerBuilder, ValidationLevel

logger = logging.getLogger(__name__)

# Initialize checker once at module level — models load here, not per-request.
_checker = (
    SpellCheckerBuilder()
    .with_config(ConfigPresets.DEFAULT)
    .with_phonetic(True)
    .build()
)


def check(text: str) -> dict:
    """Spell-check Myanmar text.

    Returns:
        {"corrected": str, "changes": list[tuple[str, str]], "has_errors": bool}
    """
    result = _checker.check(text, level=ValidationLevel.WORD)
    corrected = result.corrected_text
    changes = _extract_changes(text, corrected)
    return {
        "corrected": corrected,
        "changes": changes,
        "has_errors": len(changes) > 0,
    }


def segment(text: str) -> list[tuple[str, str]]:
    """Segment Myanmar text into words with POS tags.

    Returns:
        List of (word, pos_tag) tuples.
    """
    words, tags = _checker.segment_and_tag(text)
    return list(zip(words, tags))


def detect_zawgyi(text: str) -> tuple[bool, str]:
    """Detect Zawgyi encoding and convert to Unicode if needed.

    Returns:
        (is_zawgyi, converted_text)
    """
    # myspellchecker handles Zawgyi detection/conversion internally.
    # We check by running the text through the checker — if it performs
    # Zawgyi conversion, the output will differ from input at the
    # encoding level.
    result = _checker.check(text)
    converted = result.corrected_text
    is_zawgyi = _has_zawgyi_conversion(text, converted)
    return is_zawgyi, converted


def _extract_changes(original: str, corrected: str) -> list[tuple[str, str]]:
    """Extract word-level changes between original and corrected text."""
    if original == corrected:
        return []

    # Use SequenceMatcher to find differing segments
    matcher = difflib.SequenceMatcher(None, original, corrected)
    changes = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "replace":
            changes.append((original[i1:i2], corrected[j1:j2]))
        elif tag == "delete":
            changes.append((original[i1:i2], ""))
        elif tag == "insert":
            changes.append(("", corrected[j1:j2]))
    return changes


def _has_zawgyi_conversion(original: str, converted: str) -> bool:
    """Heuristic: check if the conversion involved Zawgyi-specific characters."""
    # Common Zawgyi-specific code points that don't exist in Unicode Myanmar
    zawgyi_indicators = {
        "\u1033",
        "\u1034",
        "\u103A",
        "\u106A",
        "\u106B",
        "\u1090",
        "\u1091",
        "\u1092",
        "\u1097",
    }
    return any(c in original for c in zawgyi_indicators) and original != converted
