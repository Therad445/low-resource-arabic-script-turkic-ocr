from __future__ import annotations

import argparse
import unicodedata
from collections import Counter

from scripts._bootstrap import ROOT  # noqa: F401
from src.data.io import read_tsv_rows

INVISIBLE = {
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


def normalize_v1(s: str) -> str:
    s = unicodedata.normalize("NFC", s or "")
    for ch in INVISIBLE:
        s = s.replace(ch, "")
    # collapse whitespace
    s = " ".join(s.split())
    return s.strip()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gt", required=True, help="GT TSV (2 or 3 columns)")
    ap.add_argument("--show_examples", type=int, default=10)
    args = ap.parse_args()

    rows = read_tsv_rows(args.gt)
    if not rows:
        raise SystemExit("No rows found (check file format).")

    seen = set()
    dup_ids = []
    empty_text = []
    changed_norm = []
    invisible_hits = Counter()

    for r in rows:
        if r.image_id in seen:
            dup_ids.append(r.image_id)
        seen.add(r.image_id)

        if not r.text.strip():
            empty_text.append(r.image_id)

        # invisible marks check
        for ch in INVISIBLE:
            if ch in r.text:
                invisible_hits[ch] += r.text.count(ch)

        n = normalize_v1(r.text)
        if n != r.text:
            changed_norm.append((r.image_id, r.text, n))

    print(f"Rows: {len(rows)}")
    print(f"Unique IDs: {len(seen)}")

    if dup_ids:
        print(f"[WARN] Duplicate image_id: {len(dup_ids)} (showing up to {args.show_examples})")
        for x in dup_ids[: args.show_examples]:
            print("  ", x)

    if empty_text:
        print(f"[WARN] Empty transcription: {len(empty_text)} (showing up to {args.show_examples})")
        for x in empty_text[: args.show_examples]:
            print("  ", x)

    if invisible_hits:
        print("[WARN] Invisible formatting marks found:")
        for ch, cnt in invisible_hits.most_common():
            print(f"  U+{ord(ch):04X} {repr(ch)}: {cnt}")

    if changed_norm:
        print(
            f"[INFO] Text differs from Normalization v1 in {len(changed_norm)} rows (showing up to {args.show_examples})"
        )
        for image_id, raw, normed in changed_norm[: args.show_examples]:
            print("---", image_id)
            print("RAW:  ", raw)
            print("NORM: ", normed)


if __name__ == "__main__":
    main()
