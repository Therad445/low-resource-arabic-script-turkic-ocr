#!/usr/bin/env python3
from __future__ import annotations

import csv
import html
import re
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIG_DIR = ROOT / "docs" / "figures"

FINAL_METRICS = ROOT / "docs" / "nlp_final_revision" / "tables" / "final_metrics.csv"
SYNTH_EXAMPLES = ROOT / "docs" / "nlp_final_revision" / "samples" / "dataset_examples.csv"

REAL_PAGE_SUMMARY = ROOT / "outputs" / "real_ocr_audit" / "current_sanity_90_fixed" / "page_summary.csv"
REAL_EXAMPLES = ROOT / "outputs" / "real_ocr_ukr_rus_tur_eval_for_colab" / "page_level_real_ocr_ukr_rus_tur_v1_eval.csv"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def ensure_matplotlib():
    try:
        import matplotlib.pyplot as plt  # type: ignore
    except Exception as e:
        raise SystemExit(
            "matplotlib is required for PNG figures. Install it or run in the existing project env.\n"
            f"Original import error: {e}"
        )
    return plt


def clean_text(s: str, limit: int = 260) -> str:
    s = re.sub(r"\s+", " ", str(s or "")).strip()
    if len(s) > limit:
        return s[: limit - 1] + "…"
    return s


def wrap_for_box(s: str, width: int = 62) -> str:
    # For Arabic-script text this is not perfect, but it is enough for a compact visual example.
    return "\n".join(textwrap.wrap(clean_text(s), width=width, break_long_words=False))


def save_pipeline_svg() -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    path = FIG_DIR / "fig01_postcorrection_process.svg"

    boxes = [
        (35, 55, 170, 70, "Исходный текст", "чистый корпус"),
        (260, 55, 190, 70, "Синтетический шум", "OCR-подобные искажения"),
        (505, 55, 190, 70, "Модель коррекции", "ByT5-small / baseline"),
        (750, 55, 170, 70, "Эталонный текст", "оценка CER/WER"),
        (260, 185, 190, 70, "Real-OCR sanity", "Tesseract, страницы"),
        (505, 185, 190, 70, "Проверка переноса", "synthetic → real"),
    ]

    def rect(x, y, w, h, title, sub):
        return f'''
  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" ry="12"
        fill="white" stroke="black" stroke-width="1.5"/>
  <text x="{x + w/2}" y="{y + 30}" font-size="18" font-weight="700"
        text-anchor="middle">{html.escape(title)}</text>
  <text x="{x + w/2}" y="{y + 54}" font-size="13"
        text-anchor="middle">{html.escape(sub)}</text>'''

    def arrow(x1, y1, x2, y2):
        return f'''
  <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"
        stroke="black" stroke-width="1.8" marker-end="url(#arrow)"/>'''

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="960" height="300" viewBox="0 0 960 300">
  <defs>
    <marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3"
            orient="auto" markerUnits="strokeWidth">
      <path d="M0,0 L0,6 L9,3 z" fill="black"/>
    </marker>
  </defs>
  <rect x="1" y="1" width="958" height="298" fill="white" stroke="none"/>
  <text x="480" y="28" font-size="22" font-weight="700" text-anchor="middle">
    Процесс проверки OCR-посткоррекции
  </text>
  {''.join(rect(*b) for b in boxes)}
  {arrow(205, 90, 260, 90)}
  {arrow(450, 90, 505, 90)}
  {arrow(695, 90, 750, 90)}
  {arrow(355, 125, 355, 185)}
  {arrow(450, 220, 505, 220)}
  {arrow(600, 185, 600, 125)}
  <text x="480" y="282" font-size="13" text-anchor="middle">
    Главная проверка: насколько модель, обученная на синтетических искажениях, переносится на реальный OCR.
  </text>
</svg>
'''
    path.write_text(svg, encoding="utf-8")
    print(f"created {path.relative_to(ROOT)}")


def save_synthetic_metrics() -> None:
    if not FINAL_METRICS.exists():
        print(f"skip: missing {FINAL_METRICS.relative_to(ROOT)}")
        return

    plt = ensure_matplotlib()
    rows = read_csv(FINAL_METRICS)
    rows = [r for r in rows if r.get("method")]
    methods = [r["method"] for r in rows]
    cer = [float(r["CER"]) for r in rows]
    wer = [float(r["WER"]) for r in rows]

    x = list(range(len(methods)))
    width = 0.35

    fig, ax = plt.subplots(figsize=(11, 5.8))
    ax.bar([i - width / 2 for i in x], cer, width, label="CER")
    ax.bar([i + width / 2 for i in x], wer, width, label="WER")
    ax.set_title("Синтетический тестовый набор: сравнение методов")
    ax.set_ylabel("Ошибка, доля")
    ax.set_xticks(x)
    ax.set_xticklabels(methods, rotation=20, ha="right")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()

    path = FIG_DIR / "fig02_synthetic_metrics.png"
    fig.savefig(path, dpi=220)
    plt.close(fig)
    print(f"created {path.relative_to(ROOT)}")


def save_text_example_png(src: Path, out_name: str, title: str, left_col: str, right_col: str, left_label: str, right_label: str) -> None:
    if not src.exists():
        print(f"skip: missing {src.relative_to(ROOT)}")
        return

    plt = ensure_matplotlib()
    rows = read_csv(src)
    rows = [r for r in rows if r.get(left_col) and r.get(right_col)]
    bad_fragments = ("body.ns-0", "mw-parser-output", "text-indent:", "margin-top:")
    if out_name == "fig04_real_ocr_example.png":
        rows = [
            r for r in rows
            if not any(b in r.get(left_col, "") for b in bad_fragments)
            and not any(b in r.get(right_col, "") for b in bad_fragments)
            and len(clean_text(r.get(left_col, ""))) > 80
            and len(clean_text(r.get(right_col, ""))) > 80
        ]
    if not rows:
        print(f"skip: no usable rows in {src.relative_to(ROOT)}")
        return

    # Pick a relatively short row so it is legible in the paper.
    if out_name == "fig04_real_ocr_example.png":
        row = next((r for r in rows if r.get("page_id") == "wiki_pdf_003"), rows[0])
    else:
        row = min(rows, key=lambda r: len(r.get(left_col, "")) + len(r.get(right_col, "")))

    left = wrap_for_box(row[left_col], width=64)
    right = wrap_for_box(row[right_col], width=64)

    fig, ax = plt.subplots(figsize=(12, 5.6))
    ax.axis("off")
    ax.set_title(title, fontsize=16, pad=16)

    ax.text(0.02, 0.86, left_label, fontsize=13, fontweight="bold", transform=ax.transAxes)
    ax.text(
        0.02, 0.76, left, fontsize=15, transform=ax.transAxes,
        va="top", ha="left", bbox=dict(boxstyle="round,pad=0.55", fc="white", ec="black")
    )

    ax.text(0.02, 0.41, right_label, fontsize=13, fontweight="bold", transform=ax.transAxes)
    ax.text(
        0.02, 0.31, right, fontsize=15, transform=ax.transAxes,
        va="top", ha="left", bbox=dict(boxstyle="round,pad=0.55", fc="white", ec="black")
    )

    path = FIG_DIR / out_name
    fig.tight_layout()
    fig.savefig(path, dpi=220)
    plt.close(fig)
    print(f"created {path.relative_to(ROOT)}")


def save_real_page_metrics() -> None:
    if not REAL_PAGE_SUMMARY.exists():
        print(f"skip: missing {REAL_PAGE_SUMMARY.relative_to(ROOT)}")
        return

    plt = ensure_matplotlib()
    rows = read_csv(REAL_PAGE_SUMMARY)
    rows = [r for r in rows if r.get("_page_id")]
    if not rows:
        print(f"skip: no rows in {REAL_PAGE_SUMMARY.relative_to(ROOT)}")
        return

    pages = [r["_page_id"] for r in rows]
    mean_cer = [float(r["mean_cer"]) for r in rows]
    mean_wer = [float(r["mean_wer"]) for r in rows]
    mean_nospace = [float(r["mean_no_space_cer"]) for r in rows]

    x = list(range(len(pages)))

    fig, ax = plt.subplots(figsize=(11.5, 5.8))
    ax.plot(x, mean_cer, marker="o", label="mean CER")
    ax.plot(x, mean_wer, marker="o", label="mean WER")
    ax.plot(x, mean_nospace, marker="o", label="mean NoSpaceCER")
    ax.set_title("Real-OCR sanity: средние ошибки по страницам")
    ax.set_ylabel("Ошибка, доля")
    ax.set_xticks(x)
    ax.set_xticklabels(pages, rotation=25, ha="right")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()

    path = FIG_DIR / "fig05_real_ocr_page_metrics.png"
    fig.savefig(path, dpi=220)
    plt.close(fig)
    print(f"created {path.relative_to(ROOT)}")


def main() -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    save_pipeline_svg()
    save_synthetic_metrics()

    save_text_example_png(
        SYNTH_EXAMPLES,
        "fig03_synthetic_example.png",
        "Пример синтетического искажения",
        "noisy",
        "clean",
        "Вход с OCR-подобным шумом",
        "Эталонный текст",
    )

    save_text_example_png(
        REAL_EXAMPLES,
        "fig04_real_ocr_example.png",
        "Пример реального OCR-фрагмента",
        "ocr_text",
        "clean_text",
        "Вывод Tesseract",
        "Проверенный эталонный текст",
    )

    save_real_page_metrics()

    print("\nDone. Generated figures are in docs/figures/")
    print("Next check:")
    print("  git status --short")
    print("  find docs/figures -maxdepth 1 -type f | sort")


if __name__ == "__main__":
    main()
