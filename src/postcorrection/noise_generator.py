"""
Synthetic OCR-like noise generator for Arabic-script texts.

The goal is not to perfectly simulate a particular OCR engine, but to create
controlled noisy-clean pairs for low-resource post-OCR correction experiments.
"""

from __future__ import annotations

import random
from dataclasses import dataclass


CONFUSION_GROUPS = [
    list("بتثني"),
    list("جحخ"),
    list("دذ"),
    list("رز"),
    list("سش"),
    list("صض"),
    list("طظ"),
    list("عغ"),
    list("فق"),
    list("هح"),
    list("ةه"),
    list("اى"),
    list("يكک"),
]

NORMALIZATION_CONFUSIONS = {
    "أ": "ا",
    "إ": "ا",
    "آ": "ا",
    "ى": "ي",
    "ي": "ى",
    "ة": "ه",
    "ه": "ة",
    "ك": "ک",
    "ک": "ك",
}

PUNCTUATION = "،؛؟.,:;!()[]{}«»\"'"


@dataclass
class NoiseConfig:
    substitute_prob: float = 0.06
    delete_prob: float = 0.025
    insert_prob: float = 0.015
    space_delete_prob: float = 0.035
    space_insert_prob: float = 0.015
    normalize_confusion_prob: float = 0.04
    punctuation_drop_prob: float = 0.02


def _build_confusion_map() -> dict[str, list[str]]:
    mapping: dict[str, list[str]] = {}
    for group in CONFUSION_GROUPS:
        for ch in group:
            mapping[ch] = [x for x in group if x != ch]
    return mapping


CONFUSION_MAP = _build_confusion_map()
ARABIC_CHARS = sorted(set("".join("".join(group) for group in CONFUSION_GROUPS) + "".join(NORMALIZATION_CONFUSIONS.keys())))


def inject_noise(text: str, config: NoiseConfig | None = None, rng: random.Random | None = None) -> str:
    """Return one noisy version of a clean line."""
    config = config or NoiseConfig()
    rng = rng or random.Random()

    out: list[str] = []

    for ch in text:
        if ch in PUNCTUATION and rng.random() < config.punctuation_drop_prob:
            continue

        if ch == " ":
            if rng.random() < config.space_delete_prob:
                continue
            out.append(ch)
            continue

        if rng.random() < config.delete_prob:
            continue

        new_ch = ch

        if ch in NORMALIZATION_CONFUSIONS and rng.random() < config.normalize_confusion_prob:
            new_ch = NORMALIZATION_CONFUSIONS[ch]
        elif ch in CONFUSION_MAP and rng.random() < config.substitute_prob:
            new_ch = rng.choice(CONFUSION_MAP[ch])

        out.append(new_ch)

        if rng.random() < config.insert_prob:
            out.append(rng.choice(ARABIC_CHARS))

        if ch != " " and rng.random() < config.space_insert_prob:
            out.append(" ")

    noisy = "".join(out)
    return " ".join(noisy.split())


def make_noisy_variants(text: str, n: int, seed: int = 42) -> list[str]:
    """Generate n noisy variants for one clean line."""
    rng = random.Random(seed)
    variants = []
    for _ in range(n):
        variants.append(inject_noise(text, rng=rng))
    return variants
