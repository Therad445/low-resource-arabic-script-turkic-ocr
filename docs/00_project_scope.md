# Project scope

## Working title
Methods of AI for recognition and analysis of historical texts in Arabic-script Turkic.

## Motivation
Historical Turkic texts in Arabic script remain hard to search and analyze at scale.
OCR/HTR is the first necessary step for digital access, indexing, and further NLP.

## Research question
How far can we push OCR quality for Arabic-script Turkic historical sources in a low-resource setting,
and what methods improve robustness under limited labeled data?

## Primary task (Phase A)
- OCR/HTR on **printed** sources (first).
- Output: line-level transcription (Arabic script).
- Metrics: CER/WER.

## Optional task (Phase B)
- Normalization/transliteration to Cyrillic/Latin for search and downstream tasks.

## Not in scope (for this semester)
- Full end-to-end genealogy graph extraction.
- Large-scale handwritten HTR without adequate labels.

## Deliverables
- Reproducible pipeline + configs.
- Gold test set protocol.
- Baselines + improvements + error analysis.
- Course paper + draft for submission.
