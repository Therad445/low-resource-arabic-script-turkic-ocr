"""
Rule-based Persian/Arabic-script normalizer baseline.
"""

from __future__ import annotations

import re

CHAR_MAP = {
    "أ": "ا",
    "إ": "ا",
    "آ": "ا",
    "ٱ": "ا",
    "ي": "ی",
    "ى": "ی",
    "ئ": "ی",
    "ك": "ک",
    "ک": "ک",
    "ؤ": "و",
    "ة": "ه",
    "ۀ": "ه",
    "ـ": "",
}

ARABIC_DIACRITICS_RE = re.compile(r"[\u064B-\u065F\u0670\u06D6-\u06ED]")


def normalize_arabic_script(text: str) -> str:
    text = str(text)
    text = ARABIC_DIACRITICS_RE.sub("", text)

    for src, dst in CHAR_MAP.items():
        text = text.replace(src, dst)

    text = re.sub(r"\s+", " ", text).strip()
    return text


def identity(text: str) -> str:
    return str(text)
