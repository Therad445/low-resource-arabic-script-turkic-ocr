# Real OCR Sanity Subset

This folder contains a small real-OCR sanity subset for the Arabic-script Turkic OCR/post-correction project.

The subset is based on selected scanned pages from:

`أوقرانيا، روسيه وتوركيه (مقالەلر مجموعەسى)`, 1915.

The goal is not to provide a full OCR benchmark yet. The goal is to add a small external-validity check beyond synthetic OCR-like noise.

## Pipeline

Scanned page image -> real OCR engine output -> manually checked clean reference -> CER/WER evaluation.

## Files

- `images/pages/` — selected scanned page images.
- `ocr_outputs/tesseract_ara/` — raw Tesseract OCR outputs.
- `real_ocr_sanity.csv` — line-level OCR output and clean reference pairs.

## Current engine

- `tesseract_ara_eng_psm6`: Tesseract with Arabic and English language models, page segmentation mode 6.

## Current sample

The current starter subset contains lines from `page_044`.

This page was selected because it is relatively neutral and mostly cultural/literary in content.

## Notes

The clean reference is derived from corrected Wikisource transcription and lightly manually checked for selected lines.

The subset is intentionally small and should be treated as a real-OCR sanity check, not as a final benchmark.

More pages can be added later, preferably from less politically sensitive educational, literary, geographical, botanical, or cultural texts.
