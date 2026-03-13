# Project Charter (Sprint 1)

## Working title

**Historically grounded benchmark and low-resource OCR pipeline for Turkic texts in Arabic script**

## Problem statement

Existing OCR/HTR systems may partially support Arabic-script Turkic material, but there is no widely adopted, reproducible benchmark protocol tailored to historical printed Turkic sources in Arabic script. The first milestone is therefore not a “best model”, but a clean experimental foundation.

## Sprint 1 goals

1. Define the canonical line-level dataset manifest.
2. Enforce document-level splitting and validation rules.
3. Standardize conservative text normalization for GT checks.
4. Establish written protocol documents so future annotation is consistent.

## Non-goals for Sprint 1

- No final OCR model training.
- No synthetic data generation yet.
- No handwritten support.
- No normalization/transliteration experiments beyond storage hooks.

## Deliverables

- `schemas/line_gt.schema.json`
- `src/data/manifest.py`
- `src/data/normalization.py`
- `scripts/validate_manifest.py`
- `scripts/make_doc_splits.py`
- strengthened `scripts/validate_gt.py`
- updated `data/README.md`
- data selection and split protocol docs

## Acceptance criteria

Sprint 1 is complete when the project can:

- read a canonical line manifest (`.csv` or `.tsv`),
- detect manifest problems early,
- create deterministic document-level splits,
- keep GT normalization rules in one place,
- and explain the protocol to a future annotator without guessing.

## Research value of Sprint 1

This sprint turns the repository from an idea skeleton into a benchmark-ready foundation. It reduces hidden leakage, annotation drift, and format chaos before expensive manual labeling begins.