# Experiments

Each experiment run should have its own folder:

`experiments/YYYY-MM-DD_<name>/`

Recommended files:
- `config.yaml` — config snapshot used for the run
- `metrics.json` — CER/WER and any other metrics
- `predictions.tsv` — model outputs (image_path<TAB>text)
- `notes.md` — what you did, what happened, what to try next

Avoid committing large model checkpoints unless necessary.
