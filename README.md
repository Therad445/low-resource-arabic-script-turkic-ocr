# Low-resource Arabic-script Turkic OCR Post-Correction

![CI](https://github.com/Therad445/low-resource-arabic-script-turkic-ocr/actions/workflows/ci.yml/badge.svg)

This repository contains a reproducible pilot project for **line-level OCR post-correction of low-resource Arabic-script Turkic historical texts**.

The current project is not a full image-based OCR/HTR system. It focuses on the post-correction stage:

```text
noisy OCR-like / OCR text -> post-correction model -> cleaner historical text
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
- CER, WER, NoSpaceCER and ExactMatch evaluation;
- per-example error analysis;
- whitespace sanity check for WER interpretation;
- synthetic-noise robustness analysis;
- worst-case and conservative fallback analysis;
- small real-OCR sanity subset;
- Tesseract Arabic-only real-OCR baseline;
- ByT5 synthetic-to-real transfer evaluation;
- real-OCR qualitative examples and transfer analysis;
- final Russian HSE course paper DOCX;
- supervisor-oriented project update.

## Synthetic benchmark result

Evaluation on the synthetic test split:

| Method | CER ↓ | WER ↓ | ExactMatch ↑ | N |
|---|---:|---:|---:|---:|
| Identity baseline | 0.086005 | 0.519006 | 0.001250 | 800 |
| Rule-based normalizer | 0.151932 | 0.684408 | 0.000000 | 800 |
| Train-derived char-confusion baseline | 0.082520 | 0.506189 | 0.001250 | 800 |
| **ByT5-small 512 / 2 epochs** | **0.079913** | **0.368540** | **0.003750** | 800 |

ByT5-small gives the best result among the evaluated methods on the controlled synthetic benchmark.

## Real-OCR sanity result

A small real-OCR sanity subset was added after the synthetic benchmark. Arabic-only Tesseract (`tesseract_ara_psm6`) was used as an open-source OCR baseline, and the synthetic-trained ByT5 model was evaluated on the resulting OCR output.

| Method | CER ↓ | WER ↓ | NoSpaceCER ↓ | N |
|---|---:|---:|---:|---:|
| Real OCR identity (`tesseract_ara_psm6`) | 0.4508 | 1.0888 | 0.4468 | 90 |
| Synthetic-trained ByT5 on real OCR | 0.4361 | 0.9660 | 0.4454 | 90 |

Line-level CER behavior:

| Category | Count |
|---|---:|
| CER improved | 40 |
| CER unchanged | 33 |
| CER worsened | 17 |

Interpretation: the synthetic-trained ByT5 model shows partial transfer to real OCR output. The WER improvement is clearer than the NoSpaceCER improvement, so the current model should not be presented as robust real-OCR character-level correction. The result is a sanity-level transfer check and a motivation for cleaner real line-level data and real-error-aware synthetic noise.

## Important interpretation

The result should be interpreted cautiously.

This project does **not** claim:

- global state of the art for OCR post-correction;
- solved OCR/HTR for Arabic-script Turkic historical documents;
- validated performance on large real scanned archive pages;
- production-ready automatic archive transcription.

The current result shows that ByT5-small can improve line-level synthetic OCR-like noisy text under a controlled benchmark and shows partial transfer to a small real-OCR sanity subset.

A separate whitespace sanity check was added because WER is sensitive to synthetic whitespace and word-boundary noise.

Key sanity-check findings:

| Check | Value |
|---|---:|
| Raw WER improvement | 0.159354 |
| Raw CER improvement | 0.013507 |
| No-space CER improvement | 0.010374 |
| WER improved but no-space CER did not improve | 9.50% |

Conclusion: the large synthetic WER reduction is partly amplified by whitespace / word-boundary correction, but it is not only a whitespace artifact. The model also improves non-whitespace character-level quality on the synthetic benchmark.

## Dataset summary

The processed synthetic benchmark contains:

| Split | Unique clean lines | Noisy-clean pairs |
|---|---:|---:|
| train | 320 | 6400 |
| valid | 40 | 800 |
| test | 40 | 800 |

The split is performed by original clean lines. No noisy variants of the same clean line appear across different splits.

The real-OCR sanity subset currently contains 90 line-level samples. It should be treated as a small transfer check, not as a final benchmark.

## Main files

### Project documentation

- [`docs/supervisor_update_june2026.md`](docs/supervisor_update_june2026.md) — compact project status for supervisor discussion.
- [`docs/research_roadmap.md`](docs/research_roadmap.md) — current roadmap from course-project pilot to stronger benchmark.
- [`docs/future_work.md`](docs/future_work.md) — consolidated future-work plan for real OCR/HTR, benchmark, data and publication directions.
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
- [`docs/nlp_final_revision/analysis/real_ocr_postcorrection.md`](docs/nlp_final_revision/analysis/real_ocr_postcorrection.md)
- [`docs/nlp_final_revision/tables/real_ocr_postcorrection_metrics.csv`](docs/nlp_final_revision/tables/real_ocr_postcorrection_metrics.csv)
- [`docs/nlp_final_revision/tables/real_ocr_postcorrection_predictions.csv`](docs/nlp_final_revision/tables/real_ocr_postcorrection_predictions.csv)
- [`docs/nlp_final_revision/samples/best_examples.md`](docs/nlp_final_revision/samples/best_examples.md)
- [`docs/nlp_final_revision/samples/worst_examples.md`](docs/nlp_final_revision/samples/worst_examples.md)

## Data files

Raw collected corpus:

```text
data/postcorrection/raw/arabic_turkic_clean_text.txt
data/postcorrection/raw/SOURCES.md
```

Processed synthetic benchmark:

```text
data/postcorrection/processed/train.csv
data/postcorrection/processed/valid.csv
data/postcorrection/processed/test.csv
data/postcorrection/processed/dataset_stats.csv
```

Real-OCR sanity subset:

```text
data/postcorrection/real_sanity/real_ocr_sanity.csv
docs/nlp_final_revision/tables/real_ocr_postcorrection_metrics.csv
docs/nlp_final_revision/tables/real_ocr_postcorrection_predictions.csv
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

Run real-OCR post-correction evaluation when a trained ByT5 checkpoint is available:

```bash
python3 scripts/evaluate_real_ocr_postcorrection.py \
  --model-path /path/to/byt5-arabic-turkic-512-2ep \
  --input data/postcorrection/real_sanity/real_ocr_sanity.csv \
  --output-dir docs/nlp_final_revision/tables \
  --num-beams 1
```

## Limitations

Current limitations:

- the corpus is small;
- the current synthetic benchmark uses limited source material;
- the synthetic-noise generator is not yet based on an empirical OCR/HTR confusion matrix;
- the real-OCR subset is small and should be treated as a sanity check;
- some real-OCR line pairs may still contain noisy OCR/reference alignment;
- there are no line crops or PAGE XML / hOCR / ALTO-style annotations yet;
- only one OCR engine configuration is currently evaluated for the real-OCR subset;
- automatic metrics do not fully capture historical-linguistic validity;
- model predictions can sometimes be worse than the noisy input.

## Next steps

The most important next steps are:

1. Finish course-project packaging: paper text, presentation, supervisor update and defense script.
2. Clean and expand the real-OCR benchmark to 300-500 verified line-level pairs.
3. Add line crops and structured annotations such as PAGE XML, hOCR or ALTO where feasible.
4. Compare OCR engines and configurations, especially Tesseract line-level settings and Kraken/eScriptorium.
5. Build real-error-aware synthetic noise from verified OCR/reference pairs.
6. Compare additional post-correction baselines such as mT5-small, ByT5-base and real-domain fallback tuning.
7. Prepare a workshop/resource-paper version only after the real benchmark is cleaner.

A safe project claim is:

> We present a reproducible pilot benchmark for line-level OCR post-correction of Arabic-script Turkic historical text. The project includes controlled synthetic OCR-like noise, simple and neural baselines, robustness and fallback analysis, and a small real-OCR sanity evaluation. ByT5-small outperforms the baselines on the synthetic benchmark and shows partial transfer to real Tesseract OCR output, but robust character-level real-OCR correction remains future work.

## License

Code: MIT, see [`LICENSE`](LICENSE).

Data: source-dependent. The current post-correction pilot uses text collected from Wikisource; attribution and source notes are stored in [`data/postcorrection/raw/SOURCES.md`](data/postcorrection/raw/SOURCES.md).
