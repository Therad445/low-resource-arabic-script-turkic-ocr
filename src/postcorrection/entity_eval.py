"""
Simple entity preservation analysis.

The script measures how many known entities from a small dictionary are found
in each text version.

Expected predictions CSV columns:
- clean
- noisy
- prediction

Entities CSV:
- entity
- type

Example:
python src/entity_eval.py --predictions results/byt5_predictions.csv --entities data/entity_list.csv --out results/entity_metrics.csv
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def contains_entity(text: str, entity: str) -> bool:
    return entity in text


def entity_recall(texts: list[str], refs: list[str], entities: list[str]) -> float:
    total = 0
    found = 0

    for text, ref in zip(texts, refs):
        gold_entities = [e for e in entities if contains_entity(ref, e)]
        total += len(gold_entities)
        found += sum(1 for e in gold_entities if contains_entity(text, e))

    if total == 0:
        return 0.0
    return found / total


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--predictions", type=Path, required=True)
    parser.add_argument("--entities", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    df = pd.read_csv(args.predictions).fillna("")
    entities = pd.read_csv(args.entities)["entity"].dropna().astype(str).tolist()

    refs = df["clean"].astype(str).tolist()

    rows = []
    for name, col in [
        ("Noisy OCR text", "noisy"),
        ("Corrected prediction", "prediction"),
    ]:
        rows.append(
            {
                "text_version": name,
                "entity_recall": entity_recall(df[col].astype(str).tolist(), refs, entities),
            }
        )

    out_df = pd.DataFrame(rows)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    out_df.to_csv(args.out, index=False)

    print(out_df.to_string(index=False))


if __name__ == "__main__":
    main()
