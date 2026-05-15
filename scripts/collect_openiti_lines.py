"""
Collect clean line-level ground-truth texts from OpenITI OCR_GS_Data.

Recommended source folder:
external/OCR_GS_Data/AzTurkish/kulliyati

Example:
python scripts/collect_openiti_lines.py \
  --input_dir external/OCR_GS_Data/AzTurkish/kulliyati \
  --output data/raw/clean_text.txt \
  --limit 3000
"""

from __future__ import annotations

import argparse
from pathlib import Path


def is_good_line(line: str, min_chars: int, max_chars: int) -> bool:
    line = line.strip()
    if not line:
        return False
    if len(line) < min_chars:
        return False
    if len(line) > max_chars:
        return False
    # Keep lines that contain at least one Arabic-script character.
    return any("\u0600" <= ch <= "\u06FF" for ch in line)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--limit", type=int, default=3000)
    parser.add_argument("--min_chars", type=int, default=10)
    parser.add_argument("--max_chars", type=int, default=180)
    args = parser.parse_args()

    if not args.input_dir.exists():
        raise FileNotFoundError(f"Input directory does not exist: {args.input_dir}")

    lines: list[str] = []
    seen: set[str] = set()

    for path in sorted(args.input_dir.rglob("*.gt.txt")):
        try:
            text = path.read_text(encoding="utf-8").strip()
        except UnicodeDecodeError:
            text = path.read_text(encoding="utf-8-sig", errors="ignore").strip()

        # In line-level OCR ground truth files, there is usually one line per file.
        # Still, splitlines() makes the script robust to multiline files.
        for line in text.splitlines():
            line = " ".join(line.strip().split())
            if is_good_line(line, args.min_chars, args.max_chars) and line not in seen:
                lines.append(line)
                seen.add(line)

            if len(lines) >= args.limit:
                break

        if len(lines) >= args.limit:
            break

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Collected {len(lines)} lines")
    print(f"Saved to {args.output}")


if __name__ == "__main__":
    main()
