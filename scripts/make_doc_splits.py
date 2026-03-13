from __future__ import annotations

import argparse
import random
from dataclasses import dataclass
from pathlib import Path

from src.data.manifest import (
    DocumentStats,
    read_line_manifest,
    summarize_documents,
    write_split_file,
)


@dataclass(frozen=True)
class DocBucket:
    name: str
    target_ratio: float
    priority: int


BUCKETS = (
    DocBucket("train", 0.70, 0),
    DocBucket("dev", 0.15, 1),
    DocBucket("test", 0.15, 2),
)


def assign_small_corpus(doc_stats: list[DocumentStats]) -> dict[str, str]:
    """Deterministic fallback for tiny corpora where a 3-way split is impossible or unstable."""
    docs = sorted(doc_stats, key=lambda d: (-d.n_lines, d.doc_id))
    n = len(docs)

    if n == 0:
        return {}
    if n == 1:
        return {docs[0].doc_id: "train"}
    if n == 2:
        return {
            docs[0].doc_id: "train",
            docs[1].doc_id: "test",
        }
    if n == 3:
        return {
            docs[0].doc_id: "train",
            docs[1].doc_id: "dev",
            docs[2].doc_id: "test",
        }

    raise ValueError("assign_small_corpus should only be used for n <= 3")


def assign_docs_balanced(
    *,
    doc_stats: list[DocumentStats],
    seed: int,
) -> dict[str, str]:
    """Assign documents to train/dev/test with sensible behavior on both tiny and normal corpora.

    Strategy:
    - for <=3 docs, use deterministic fallback;
    - for larger corpora, assign globally;
    - first ensure empty buckets get filled when possible;
    - then minimize relative overflow against target ratios;
    - prefer train over dev over test on perfect ties.
    """
    if len(doc_stats) <= 3:
        return assign_small_corpus(doc_stats)

    rng = random.Random(seed)
    docs = list(doc_stats)
    rng.shuffle(docs)
    docs.sort(key=lambda d: (-d.n_lines, d.doc_id))

    total_lines = sum(d.n_lines for d in docs)
    target_lines = {bucket.name: total_lines * bucket.target_ratio for bucket in BUCKETS}
    current_lines = {bucket.name: 0 for bucket in BUCKETS}
    current_docs = {bucket.name: 0 for bucket in BUCKETS}

    assignments: dict[str, str] = {}

    for doc in docs:
        doc_n_lines = doc.n_lines
        empty_buckets = [b for b in BUCKETS if current_docs[b.name] == 0]
        if empty_buckets:
            chosen = sorted(empty_buckets, key=lambda b: b.priority)[0]
        else:

            def bucket_score(
                bucket: DocBucket, doc_n_lines: int = doc_n_lines
            ) -> tuple[float, int, int]:
                projected = current_lines[bucket.name] + doc_n_lines
                target = max(target_lines[bucket.name], 1.0)
                overflow_ratio = projected / target
                return (overflow_ratio, current_docs[bucket.name], bucket.priority)

            chosen = sorted(BUCKETS, key=bucket_score)[0]

        assignments[doc.doc_id] = chosen.name
        current_lines[chosen.name] += doc.n_lines
        current_docs[chosen.name] += 1

    return assignments


def main() -> None:
    ap = argparse.ArgumentParser(description="Create document-level train/dev/test splits.")
    ap.add_argument("--manifest", required=True, help="Line manifest (.csv or .tsv)")
    ap.add_argument("--out_dir", required=True, help="Directory for split txt files")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    records = read_line_manifest(args.manifest)
    stats = summarize_documents(records)
    assignments = assign_docs_balanced(doc_stats=stats, seed=args.seed)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    for split_name in ("train", "dev", "test"):
        doc_ids = sorted(doc_id for doc_id, split in assignments.items() if split == split_name)
        write_split_file(out_dir / f"{split_name}_docs.txt", doc_ids)

    print(f"Documents: {len(stats)}")
    print(f"Sources: {len({stat.source_id for stat in stats})}")
    for split_name in ("train", "dev", "test"):
        doc_ids = [doc_id for doc_id, split in assignments.items() if split == split_name]
        n_lines = sum(stat.n_lines for stat in stats if stat.doc_id in doc_ids)
        print(f"{split_name}: {len(doc_ids)} docs, {n_lines} lines")

    if len(stats) < 3:
        print("[INFO] Fewer than 3 documents: a full train/dev/test split is impossible.")
    elif any(
        not [doc_id for doc_id, split in assignments.items() if split == split_name]
        for split_name in ("train", "dev", "test")
    ):
        print(
            "[WARN] At least one split is empty; add more documents for a stable benchmark split."
        )


if __name__ == "__main__":
    main()
