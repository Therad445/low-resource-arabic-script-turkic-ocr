# Split Protocol v1

## Core rule

**Train / dev / test splits are made by `doc_id`, never by line.**

This prevents leakage from identical typography, scanning artifacts, and document-specific layout patterns appearing in both training and evaluation.

## Default target ratios

- train: 70%
- dev: 15%
- test: 15%

These ratios are approximate and should be interpreted primarily in terms of **line counts**, while preserving document integrity.

## Additional rule: preserve source coverage when possible

Documents are first grouped by `source_id`. The split script assigns documents within each source so that no single source is entirely absent from evaluation unless the source contains too few documents.

## Gold test freeze

Once the first article-grade `test_docs.txt` is agreed upon, it should be frozen and versioned. Later experiments may add new train/dev data, but the frozen test set should not be reshuffled unless there is a documented reason.

## Recommended checks after split generation

1. No document appears in more than one split.
2. No split is empty.
3. Each split contains more than one source whenever possible.
4. The line count imbalance is acceptable.
5. Extremely difficult or damaged documents are not all concentrated in one split unless this was intentional.

## Output files

Generated split directory should contain:

- `train_docs.txt`
- `dev_docs.txt`
- `test_docs.txt`

Each file stores one `doc_id` per line.

## Reproducibility

Split generation must record:

- manifest version,
- seed,
- generation date,
- script version / git commit.

The initial Sprint 1 script stores deterministic outputs given the same manifest and seed.