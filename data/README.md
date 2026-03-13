# Data layout

This repository does **not** commit raw scans or heavy derived artifacts. The benchmark is driven by a light-weight manifest and document-level split files.

## Local folders

* `data/raw/` — original scans or page images obtained with permission (**DO NOT COMMIT**)
* `data/interim/` — temporary exports such as PAGE XML, line crops, OCR outputs (**DO NOT COMMIT heavy files**)
* `data/processed/` — local training-ready artifacts derived from raw data
* `data/metadata/` — small text files that *can* be versioned: manifests, document metadata, source tables
* `data/splits/` — document-level split files (`train_docs.txt`, `dev_docs.txt`, `test_docs.txt`)

## Canonical manifest

Sprint 1 introduces a single canonical line manifest. Store it under `data/metadata/line_manifest_v1.tsv` or `.csv`.

Required columns:

* `line_id` — globally unique stable line identifier
* `doc_id` — globally unique document identifier; **this is the split unit**
* `page_id` — page identifier within the corpus
* `source_id` — source collection / archive / edition identifier
* `image_relpath` — relative path to the local line image or page crop
* `transcription_diplomatic` — diplomatic transcription used for OCR evaluation

Optional columns:

* `transcription_normalized`
* `quality_flag`
* `notes`

Example:

```tsv
line_id	doc_id	page_id	source_id	image_relpath	transcription_diplomatic	quality_flag
kazan_1905_p001_l0001	kazan_1905	kazan_1905_p001	archive_a	processed/lines/kazan_1905/p001/l0001.png	سلام عليكم	ok
```

## Split philosophy

Splits are made **by document, not by line**. Never place lines from the same document in both train and test.

Create split files with:

```bash
python scripts/make_doc_splits.py \
  --manifest data/metadata/line_manifest_v1.tsv \
  --out_dir data/splits/v1 \
  --seed 42
```

Expected outputs:

* `data/splits/v1/train_docs.txt`
* `data/splits/v1/dev_docs.txt`
* `data/splits/v1/test_docs.txt`

Each file contains one `doc_id` per line.

## Validation commands

Validate the line manifest:

```bash
python scripts/validate_manifest.py --manifest data/metadata/line_manifest_v1.tsv
```

Validate a legacy GT TSV used by evaluation scripts:

```bash
python scripts/validate_gt.py --gt datasets/gold_test_v1/labels/gt.tsv
```

## Publishing policy

We aim to publish small text metadata, annotation guidelines, splits, and evaluation code. Whether images or line crops can be released depends on source permissions.
