from __future__ import annotations

import argparse
from statistics import mean

from src.data.io import read_tsv, align_gt_pred
from src.metrics.cer import cer
from src.metrics.wer import wer

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gt", required=True, help="GT TSV: image_path<TAB>text")
    ap.add_argument("--pred", required=True, help="Pred TSV: image_path<TAB>text")
    ap.add_argument("--limit", type=int, default=0, help="Optional limit for quick runs")
    args = ap.parse_args()

    gt = read_tsv(args.gt)
    pr = read_tsv(args.pred)
    pairs = align_gt_pred(gt, pr)

    if args.limit and args.limit > 0:
        pairs = pairs[: args.limit]

    if not pairs:
        raise SystemExit("No overlapping keys between GT and predictions.")

    cers = [cer(g, p) for _, g, p in pairs]
    wers = [wer(g, p) for _, g, p in pairs]

    print(f"Samples: {len(pairs)}")
    print(f"CER mean: {mean(cers):.4f}")
    print(f"WER mean: {mean(wers):.4f}")

if __name__ == "__main__":
    main()
