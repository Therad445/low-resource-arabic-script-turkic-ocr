from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path

from src.data.io import read_tsv, align_gt_pred
from src.metrics.cer import cer

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gt", required=True)
    ap.add_argument("--pred", required=True)
    ap.add_argument("--out", default="outputs/error_report.tsv")
    ap.add_argument("--topk", type=int, default=50)
    args = ap.parse_args()

    gt = read_tsv(args.gt)
    pr = read_tsv(args.pred)
    pairs = align_gt_pred(gt, pr)
    if not pairs:
        raise SystemExit("No overlapping keys between GT and predictions.")

    # rank by CER
    scored = []
    for k, g, p in pairs:
        scored.append((cer(g, p), k, g, p))
    scored.sort(reverse=True, key=lambda x: x[0])

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    lines = ["cer\timage_path\tgt\tpred"]
    for s, k, g, p in scored[: args.topk]:
        lines.append(f"{s:.6f}\t{k}\t{g}\t{p}")
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    # very rough char confusion stats (not alignment-based, just counts)
    diff_counter = Counter()
    for _, _, g, p in scored[: args.topk]:
        for ch in set(g) ^ set(p):
            diff_counter[ch] += 1

    print(f"Saved: {out_path}")
    if diff_counter:
        print("Top differing chars (rough):")
        for ch, cnt in diff_counter.most_common(20):
            print(f"{repr(ch)}\t{cnt}")

if __name__ == "__main__":
    main()
