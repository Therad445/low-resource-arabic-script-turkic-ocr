# Low-resource Arabic-script Turkic OCR Post-Correction

![CI](https://github.com/Therad445/low-resource-arabic-script-turkic-ocr/actions/workflows/ci.yml/badge.svg)

This repository contains a reproducible pilot project for **OCR post-correction of low-resource Arabic-script Turkic historical texts**.

The current project is not a full image-based OCR/HTR system. It focuses on the post-correction stage:

```text
noisy OCR-like / OCR text -> post-correction model -> cleaner historical text
```

The long-term motivation includes Old Tatar and Old Bashkir materials, but the current open real-OCR benchmark is broader: it uses an **Ottoman Turkish printed source in Arabic script** as a related Arabic-script Turkic test case. It should not be described as an Old Tatar or Old Bashkir dataset.

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
- earlier 90-line real-OCR sanity subset;
- local page-level Ottoman Turkish real-OCR sanity benchmark;
- Tesseract Arabic-only real-OCR baseline;
- chunked ByT5 synthetic-to-real transfer evaluation;
- strict fallback analysis;
- final Russian HSE course paper draft and defense materials.

## Synthetic benchmark result

Evaluation on the synthetic test split:

| Method | CER ↓ | WER ↓ | ExactMatch ↑ | N |
|---|---:|---:|---:|---:|
| Identity baseline | 0.086005 | 0.519006 | 0.001250 | 800 |
| Rule-based normalizer | 0.151932 | 0.684408 | 0.000000 | 800 |
| Train-derived char-confusion baseline | 0.082520 | 0.506189 | 0.001250 | 800 |
| **ByT5-small 512 / 2 epochs** | **0.079913** | **0.368540** | **0.003750** | 800 |

ByT5-small gives the best result among the evaluated methods on the controlled synthetic benchmark.

## Real-OCR results

### Earlier line-level sanity subset

The earlier real-OCR sanity subset contains 90 line-level examples. It is retained as a small transfer check.

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

### Page-level Ottoman Turkish sanity benchmark

A newer local page-level benchmark was built from an Ottoman Turkish printed source in Arabic script. Raw page images, OCR outputs, page-level transcriptions, and prediction files are kept local and are not redistributed in this repository.

Filtered evaluation subset:

| Property | Value |
|---|---:|
| Rendered source pages | 72 |
| Filtered eval pages | 68 |
| Clean/reference chars | 90,457 |
| OCR chars | 81,593 |
| OCR engine | `tesseract_ara_psm6` |

Page-level results:

| System | N | Mean CER ↓ | Median CER ↓ | Mean WER ↓ | Median WER ↓ | Mean NoSpaceCER ↓ |
|---|---:|---:|---:|---:|---:|---:|
| raw_tesseract | 68 | 0.3539 | 0.2983 | 0.9238 | 0.8943 | 0.3421 |
| byt5_chunked | 68 | 0.4564 | 0.4206 | 0.8919 | 0.8579 | 0.4658 |
| strict_guarded_byt5 | 68 | 0.3828 | 0.3442 | 0.9039 | 0.8605 | 0.3830 |

Page-level CER status counts:

| System | Improved | Same | Worse |
|---|---:|---:|---:|
| byt5_chunked | 6 | 0 | 62 |
| strict_guarded_byt5 | 33 | 3 | 32 |

Interpretation: the synthetic-trained ByT5 model does **not** robustly transfer to full-page real OCR for the Ottoman Turkish source. It slightly improves WER but worsens CER and NoSpaceCER. The strict fallback reduces the damage but still does not outperform raw Tesseract on average by CER. This is a realistic synthetic-to-real gap and motivates real-domain adaptation.

## Important interpretation

The result should be interpreted cautiously.

This project does **not** claim:

- global state of the art for OCR post-correction;
- solved OCR/HTR for Arabic-script Turkic historical documents;
- solved Old Tatar or Old Bashkir OCR;
- validated performance on large real scanned archive pages;
- production-ready automatic archive transcription.

A safe project claim is:

> We present a reproducible pilot benchmark for OCR post-correction of Arabic-script Turkic historical text. The project includes controlled synthetic OCR-like noise, simple and neural baselines, robustness and fallback analysis, and real-OCR sanity evaluation. ByT5-small improves the controlled synthetic benchmark, but the page-level Ottoman Turkish real-OCR experiment shows that synthetic-only training does not reliably transfer to real full-page OCR without real-domain adaptation.

## Dataset summary

The processed synthetic benchmark contains:

| Split | Unique clean lines | Noisy-clean pairs |
|---|---:|---:|
| train | 320 | 6400 |
| valid | 40 | 800 |
| test | 40 | 800 |

The split is performed by original clean lines. No noisy variants of the same clean line appear across different splits.

## Main files

### Project documentation

- [`docs/supervisor_update_june2026.md`](docs/supervisor_update_june2026.md) — compact project status for supervisor discussion.
- [`docs/research_roadmap.md`](docs/research_roadmap.md) — current roadmap from course-project pilot to stronger benchmark.
- [`docs/future_work.md`](docs/future_work.md) — consolidated future-work plan for real OCR/HTR, benchmark, data and publication directions.
- [`DATASET_CARD.md`](DATASET_CARD.md) — dataset description and limitations.
- [`MODEL_CARD.md`](MODEL_CARD.md) — model, baselines, metrics and risks.
- [`REPRODUCE.md`](REPRODUCE.md) — reproduction guide.

### NLP final revision artifacts

- [`docs/nlp_final_revision/tables/final_metrics.csv`](docs/nlp_final_revision/tables/final_metrics.csv)
- [`docs/nlp_final_revision/tables/real_ocr_postcorrection_metrics.csv`](docs/nlp_final_revision/tables/real_ocr_postcorrection_metrics.csv)
- [`docs/nlp_final_revision/analysis/real_ocr_postcorrection.md`](docs/nlp_final_revision/analysis/real_ocr_postcorrection.md)
- [`docs/nlp_final_revision/tables/real_ocr_ukr_rus_tur_chunked_summary.csv`](docs/nlp_final_revision/tables/real_ocr_ukr_rus_tur_chunked_summary.csv)
- [`docs/nlp_final_revision/analysis/real_ocr_ukr_rus_tur_chunked_transfer.md`](docs/nlp_final_revision/analysis/real_ocr_ukr_rus_tur_chunked_transfer.md)

## Key commands

Install post-correction dependencies:

```bash
python3 -m pip install -r requirements-postcorrection.txt
```

Build the synthetic dataset:

```bash
python3 -m src.postcorrection.make_dataset   --input data/postcorrection/raw/arabic_turkic_clean_text.txt   --out_dir data/postcorrection/processed   --variants 20   --seed 42
```

Run synthetic baseline evaluation:

```bash
python3 -m src.postcorrection.run_baselines   --test data/postcorrection/processed/test.csv   --out outputs/postcorrection/baseline_predictions.csv   --metrics outputs/postcorrection/baseline_metrics.csv
```

Run chunked real-OCR post-correction evaluation when a trained ByT5 checkpoint and the local page-level CSV are available:

```bash
python3 scripts/evaluate_real_ocr_postcorrection_chunked.py   --model-path /path/to/byt5-arabic-turkic-512-2ep   --input /path/to/page_level_real_ocr_ukr_rus_tur_v1_eval.csv   --predictions-out outputs/real_ocr_ukr_rus_tur/byt5_chunked_predictions.csv   --metrics-out outputs/real_ocr_ukr_rus_tur/byt5_chunked_metrics.csv   --num-beams 1   --batch-size 4
```

## Limitations

Current limitations:

- the corpus is small;
- the current synthetic benchmark uses limited source material;
- the page-level real-OCR benchmark currently uses one Ottoman Turkish source, not Old Tatar or Old Bashkir;
- raw real-OCR source data and predictions are kept local and are not redistributed;
- the synthetic-noise generator is not yet based on an empirical OCR/HTR confusion matrix;
- there are no line crops or PAGE XML / hOCR / ALTO-style annotations yet;
- only one OCR engine configuration is currently evaluated for the page-level real-OCR subset;
- automatic metrics do not fully capture historical-linguistic validity;
- model predictions can be worse than the noisy input.

## Next steps

The most important next steps are:

1. Update the course paper and slides to use the broader Arabic-script Turkic framing.
2. Build aligned real OCR/reference chunks from page-level OCR and page-level gold.
3. Fine-tune or adapt ByT5 on real OCR chunks using page-level train/dev/test splits.
4. Add Old Tatar / Old Bashkir manually checked samples when available.
5. Compare OCR engines and configurations, especially Tesseract, Kraken, and eScriptorium pipelines.
6. Build real-error-aware synthetic noise from verified OCR/reference pairs.
7. Prepare a workshop/resource-paper version only after the real benchmark is cleaner.

## License

Code: MIT, see [`LICENSE`](LICENSE).

Data: source-dependent. Raw real-OCR data, page images, transcriptions, and model prediction files are not redistributed in this repository unless source permissions and attribution requirements are checked.
