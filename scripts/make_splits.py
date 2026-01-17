from __future__ import annotations

import argparse
import random
from pathlib import Path


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--items", required=True, help="Text file with one sample ID per line")
    ap.add_argument("--out_dir", required=True, help="Output directory for splits")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--train", type=float, default=0.8)
    ap.add_argument("--val", type=float, default=0.1)
    args = ap.parse_args()

    items_path = Path(args.items)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    items = [ln.strip() for ln in items_path.read_text(encoding="utf-8").splitlines() if ln.strip()]
    random.Random(args.seed).shuffle(items)

    n = len(items)
    n_train = int(n * args.train)
    n_val = int(n * args.val)
    train_items = items[:n_train]
    val_items = items[n_train : n_train + n_val]
    test_items = items[n_train + n_val :]

    (out_dir / "train.txt").write_text(
        "\n".join(train_items) + ("\n" if train_items else ""), encoding="utf-8"
    )
    (out_dir / "val.txt").write_text(
        "\n".join(val_items) + ("\n" if val_items else ""), encoding="utf-8"
    )
    (out_dir / "test.txt").write_text(
        "\n".join(test_items) + ("\n" if test_items else ""), encoding="utf-8"
    )

    print(
        f"Saved splits to {out_dir} (n={n}, train={len(train_items)}, val={len(val_items)}, test={len(test_items)})"
    )


if __name__ == "__main__":
    main()
