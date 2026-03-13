from __future__ import annotations

import unicodedata

INVISIBLE_FORMATTING_MARKS = {
    "\u200c",  # ZWNJ
    "\u200d",  # ZWJ
    "\u200e",  # LRM
    "\u200f",  # RLM
    "\u202a",
    "\u202b",
    "\u202c",
    "\u202d",
    "\u202e",  # embeddings/overrides
    "\u2066",
    "\u2067",
    "\u2068",
    "\u2069",  # isolates
}


def normalize_text_v1(text: str) -> str:
    """Repository-wide conservative normalization for GT and predictions.

    This function intentionally avoids script-specific substitutions. It only:
    - applies NFC;
    - removes invisible formatting marks;
    - collapses whitespace.
    """
    normalized = unicodedata.normalize("NFC", text or "")
    for ch in INVISIBLE_FORMATTING_MARKS:
        normalized = normalized.replace(ch, "")
    normalized = " ".join(normalized.split())
    return normalized.strip()