from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path

from scripts._bootstrap import ROOT  # noqa: F401
from src.data.io import align_gt_pred, read_tsv_rows
from src.metrics.cer import cer


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gt", required=True)
    ap.add_argument("--pred", required=True)
    ap.add_argument("--out", default="outputs/error_report.tsv")
    ap.add_argument("--topk", type=int, default=50)
    args = ap.parse_args()

    gt_rows = read_tsv_rows(args.gt)
    pr_rows = read_tsv_rows(args.pred)
    pairs = align_gt_pred(gt_rows, pr_rows)
    if not pairs:
        raise SystemExit("No overlapping image_id keys between GT and predictions.")

    scored = []
    for image_id, image_path, gt_text, pred_text in pairs:
        scored.append((cer(gt_text, pred_text), image_id, image_path, gt_text, pred_text))
    scored.sort(reverse=True, key=lambda x: x[0])

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    lines = ["cer\timage_id\timage_path\tgt\tpred"]
    for s, image_id, image_path, gt_text, pred_text in scored[: args.topk]:
        lines.append(f"{s:.6f}\t{image_id}\t{image_path}\t{gt_text}\t{pred_text}")
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    # rough char diff stats
    diff_counter = Counter()
    for _, _, _, gt_text, pred_text in scored[: args.topk]:
        for ch in set(gt_text) ^ set(pred_text):
            diff_counter[ch] += 1

    print(f"Saved: {out_path}")
    if diff_counter:
        print("Top differing chars (rough):")
        for ch, cnt in diff_counter.most_common(20):
            print(f"{repr(ch)}\t{cnt}")


if __name__ == "__main__":
    main()
