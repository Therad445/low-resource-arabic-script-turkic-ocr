# Low-resource Arabic-script Turkic OCR Post-Correction

![CI](https://github.com/Therad445/low-resource-arabic-script-turkic-ocr/actions/workflows/ci.yml/badge.svg)

This repository contains a reproducible pilot project for **line-level OCR post-correction of low-resource Arabic-script Turkic historical texts**.

The current project is not a full image-based OCR/HTR system. It focuses on the post-correction stage:

```text
noisy OCR-like Arabic-script Turkic text -> clean historical text
```

The main goal is to build a controlled benchmark, compare simple and neural baselines, analyze errors, and prepare the project for a stronger real-OCR/HTR validation stage.

## Current status

The project currently includes:

- Arabic-script Turkic / Ottoman Turkish clean text collection;
- synthetic OCR-like noisy-clean benchmark construction;
- train/valid/test split without clean-line leakage;
- identity baseline;
- rule-based normalizer baseline;
- train-derived character-confusion baseline;
- ByT5-small 512 / 2 epochs post-correction model;
- CER, WER and ExactMatch evaluation;
- per-example error analysis;
- whitespace sanity check for WER interpretation;
- final Russian HSE course paper DOCX;
- supervisor-oriented project update.

## Main result

Evaluation on the synthetic test split:

| Method | CER ↓ | WER ↓ | ExactMatch ↑ | N |
|---|---:|---:|---:|---:|
| Identity baseline | 0.086005 | 0.519006 | 0.001250 | 800 |
| Rule-based normalizer | 0.151932 | 0.684408 | 0.000000 | 800 |
| Train-derived char-confusion baseline | 0.082520 | 0.506189 | 0.001250 | 800 |
| **ByT5-small 512 / 2 epochs** | **0.079913** | **0.368540** | **0.003750** | 800 |

ByT5-small gives the best result among the evaluated methods on the controlled synthetic benchmark.

## Important interpretation

The result should be interpreted cautiously.

This project does **not** claim:

- global state of the art for OCR post-correction;
- solved OCR/HTR for Arabic-script Turkic historical documents;
- validated performance on real scanned archive pages.

The current result shows that ByT5-small can improve line-level synthetic OCR-like noisy text under a controlled benchmark.

A separate whitespace sanity check was added because WER is sensitive to synthetic whitespace and word-boundary noise.

Key sanity-check findings:

| Check | Value |
|---|---:|
| Raw WER improvement | 0.159354 |
| Raw CER improvement | 0.013507 |
| No-space CER improvement | 0.010374 |
| WER improved but no-space CER did not improve | 9.50% |

Conclusion: the large WER reduction is partly amplified by whitespace / word-boundary correction, but it is not only a whitespace artifact. The model also improves non-whitespace character-level quality.

## Dataset summary

The processed benchmark contains:

| Split | Unique clean lines | Noisy-clean pairs |
|---|---:|---:|
| train | 320 | 6400 |
| valid | 40 | 800 |
| test | 40 | 800 |

The split is performed by original clean lines. No noisy variants of the same clean line appear across different splits.

## Main files

### Project documentation

- [`docs/supervisor_update_june2026.md`](docs/supervisor_update_june2026.md) — compact project status for supervisor discussion.
- [`docs/research_roadmap.md`](docs/research_roadmap.md) — next research steps.
- [`DATASET_CARD.md`](DATASET_CARD.md) — dataset description and limitations.
- [`MODEL_CARD.md`](MODEL_CARD.md) — model, baselines, metrics and risks.
- [`REPRODUCE.md`](REPRODUCE.md) — reproduction guide.

### Course paper

- [`docs/course_paper_final.md`](docs/course_paper_final.md) — final course paper source in Markdown.
- [`docs/course_paper_hse_export.md`](docs/course_paper_hse_export.md) — HSE DOCX export Markdown source.
- [`outputs/course_paper_hse_final.docx`](outputs/course_paper_hse_final.docx) — final Russian HSE course paper DOCX.

### NLP final revision artifacts

- [`docs/nlp_final_revision/tables/final_metrics.csv`](docs/nlp_final_revision/tables/final_metrics.csv)
- [`docs/nlp_final_revision/tables/wer_vs_no_space_cer_dependency.csv`](docs/nlp_final_revision/tables/wer_vs_no_space_cer_dependency.csv)
- [`docs/nlp_final_revision/tables/whitespace_sanity_summary_by_word_count_group.csv`](docs/nlp_final_revision/tables/whitespace_sanity_summary_by_word_count_group.csv)
- [`docs/nlp_final_revision/analysis/whitespace_sanity.md`](docs/nlp_final_revision/analysis/whitespace_sanity.md)
- [`docs/nlp_final_revision/samples/best_examples.md`](docs/nlp_final_revision/samples/best_examples.md)
- [`docs/nlp_final_revision/samples/worst_examples.md`](docs/nlp_final_revision/samples/worst_examples.md)

## Data files

Raw collected corpus:

```text
data/postcorrection/raw/arabic_turkic_clean_text.txt
data/postcorrection/raw/SOURCES.md
```

Processed benchmark:

```text
data/postcorrection/processed/train.csv
data/postcorrection/processed/valid.csv
data/postcorrection/processed/test.csv
data/postcorrection/processed/dataset_stats.csv
```

## Key commands

Install post-correction dependencies:

```bash
python3 -m pip install -r requirements-postcorrection.txt
```

Build the synthetic dataset:

```bash
python3 -m src.postcorrection.make_dataset \
  --input data/postcorrection/raw/arabic_turkic_clean_text.txt \
  --out_dir data/postcorrection/processed \
  --variants 20 \
  --seed 42
```

Run baseline evaluation:

```bash
python3 -m src.postcorrection.run_baselines \
  --test data/postcorrection/processed/test.csv \
  --out outputs/postcorrection/baseline_predictions.csv \
  --metrics outputs/postcorrection/baseline_metrics.csv
```

Run error analysis:

```bash
python3 scripts/postcorrection_error_analysis.py \
  --predictions outputs/postcorrection/byt5_arabic_turkic_512_2ep_predictions.csv \
  --out_dir outputs/postcorrection/error_analysis
```

Run whitespace sanity check:

```bash
python3 scripts/postcorrection_whitespace_sanity.py
```

## Limitations

Current limitations:

- the corpus is small;
- the current benchmark uses one main source;
- the noise is synthetic;
- the noise generator is not based on an empirical OCR/HTR confusion matrix;
- there is no manually validated real-OCR/HTR subset yet;
- automatic metrics do not fully capture historical-linguistic validity;
- model predictions can sometimes be worse than the noisy input.

## Next steps

The most important next steps are:

1. Update repository documentation and presentation layer.
2. Run robustness checks with alternative synthetic noise settings.
3. Analyze worst cases and add a conservative fallback rule.
4. Build a small real-OCR/HTR sanity subset.
5. Prepare a short workshop/conference-style paper.

A safe project claim is:

> We present a reproducible pilot benchmark for line-level OCR post-correction of Arabic-script Turkic historical text under controlled synthetic OCR-like noise. ByT5-small outperforms identity, rule-based normalization, and a train-derived character-confusion baseline on this benchmark. However, the results should be interpreted as controlled pilot evidence, not as proof of practical performance on real OCR/HTR outputs.

## License

Code: MIT, see [`LICENSE`](LICENSE).

Data: source-dependent. The current post-correction pilot uses text collected from Wikisource; attribution and source notes are stored in [`data/postcorrection/raw/SOURCES.md`](data/postcorrection/raw/SOURCES.md).
