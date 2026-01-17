# gold_test_v1

Fixed, high-quality evaluation set for printed Arabic-script Turkic OCR.

## TSV schema (canonical)
`datasets/gold_test_v1/labels/gt.tsv` uses 3 columns:

`image_id<TAB>image_path<TAB>transcription`

- `image_id` — stable unique id, e.g. `srcA_page001_line0012`
- `image_path` — relative path, e.g. `images/srcA/page001/line0012.png`
- `transcription` — normalized according to `docs/02_annotation_guidelines.md` (Normalization v1)

## Images
- `images/` is optional.
- If redistribution is not allowed, keep `images/` empty and store scans privately.
  The `image_path` can still point to your local layout.

## Stability rules
- Do not change this set after results are reported.
- If you need updates, create `gold_test_v2/`.
