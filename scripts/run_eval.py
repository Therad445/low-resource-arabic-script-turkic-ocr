from __future__ import annotations

import argparse
from pathlib import Path
from statistics import mean
from datetime import datetime

from src.data.io import read_tsv_rows, align_gt_pred
from src.metrics.cer import cer
from src.metrics.wer import wer
from src.utils.logging import write_json


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gt", required=True)
    ap.add_argument("--pred", required=True)
    ap.add_argument("--exp_dir", required=True, help="e.g., experiments/2026-01-17_baseline0_print")
    ap.add_argument("--tag", default="baseline", help="short tag to store in metrics.json")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    exp_dir = Path(args.exp_dir)
    exp_dir.mkdir(parents=True, exist_ok=True)

    gt_rows = read_tsv_rows(args.gt)
    pr_rows = read_tsv_rows(args.pred)
    pairs = align_gt_pred(gt_rows, pr_rows)
    if args.limit and args.limit > 0:
        pairs = pairs[: args.limit]

    if not pairs:
        raise SystemExit("No overlapping image_id keys between GT and predictions.")

    cers = [cer(gt_text, pred_text) for _, _, gt_text, pred_text in pairs]
    wers = [wer(gt_text, pred_text) for _, _, gt_text, pred_text in pairs]

    metrics = {
        "tag": args.tag,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "samples": len(pairs),
        "cer_mean": float(mean(cers)),
        "wer_mean": float(mean(wers)),
        "gt_path": args.gt,
        "pred_path": args.pred,
    }

    write_json(exp_dir / "metrics.json", metrics)

    # Keep a copy of predictions for reproducibility (small files only!)
    pred_copy = exp_dir / "predictions.tsv"
    pred_copy.write_text(Path(args.pred).read_text(encoding="utf-8"), encoding="utf-8")

    notes = exp_dir / "notes.md"
    if not notes.exists():
        notes.write_text(
            "# Run notes\n\n"
            f"- tag: {args.tag}\n"
            f"- gt: {args.gt}\n"
            f"- pred: {args.pred}\n"
            "\nNext:\n- inspect worst errors (scripts/error_analysis.py)\n",
            encoding="utf-8",
        )

    print(f"Saved metrics: {exp_dir / 'metrics.json'}")
    print(f"CER mean: {metrics['cer_mean']:.4f}")
    print(f"WER mean: {metrics['wer_mean']:.4f}")


if __name__ == "__main__":
    main()
