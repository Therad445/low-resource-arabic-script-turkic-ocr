# gold_test_v1

A small, high-quality evaluation set used as the fixed benchmark.

## Structure
- `labels/gt.tsv`: `image_path<TAB>transcription`
- `images/`: optional; only if allowed to distribute

## Notes
- Keep this set stable over time.
- Prefer diverse documents but avoid leakage from training sources.
