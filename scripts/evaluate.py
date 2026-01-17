from __future__ import annotations

import argparse
from statistics import mean

from scripts._bootstrap import ROOT  # noqa: F401
from src.data.io import read_tsv_rows, align_gt_pred
from src.metrics.cer import cer
from src.metrics.wer import wer


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gt", required=True, help="GT TSV: 3-col (preferred) or 2-col format")
    ap.add_argument("--pred", required=True, help="Pred TSV: 3-col (preferred) or 2-col format")
    ap.add_argument("--limit", type=int, default=0, help="Optional limit for quick runs")
    args = ap.parse_args()

    gt_rows = read_tsv_rows(args.gt)
    pr_rows = read_tsv_rows(args.pred)
    pairs = align_gt_pred(gt_rows, pr_rows)

    if args.limit and args.limit > 0:
        pairs = pairs[: args.limit]

    if not pairs:
        raise SystemExit("No overlapping image_id keys between GT and predictions.")

    cers = [cer(gt_text, pred_text) for _, _, gt_text, pred_text in pairs]
    wers = [wer(gt_text, pred_text) for _, _, gt_text, pred_text in pairs]

    print(f"Samples: {len(pairs)}")
    print(f"CER mean: {mean(cers):.4f}")
    print(f"WER mean: {mean(wers):.4f}")


if __name__ == "__main__":
    main()
