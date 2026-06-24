# Dataset Card: Arabic-Script Turkic OCR Post-Correction Benchmark

## Dataset Summary

This repository contains a pilot benchmark for OCR post-correction of historical Turkic text written in Arabic-based scripts.

The main synthetic task is formulated as line-level sequence-to-sequence correction:

```text
noisy -> clean
```

The long-term motivation includes Old Tatar and Old Bashkir materials, but the current real-OCR source used in the project is an **Ottoman Turkish printed source in Arabic script**. Therefore, the real-OCR subset should be described as an Arabic-script Turkic / Ottoman Turkish sanity benchmark, not as an Old Tatar or Old Bashkir dataset.

The repository stores scripts, synthetic benchmark files, and small summary artifacts. The full page-level real-OCR source workspace, including PDF, rendered page images, Tesseract OCR outputs, page-level gold transcriptions, and prediction files, is kept local and is not redistributed in git.

## Dataset Structure

Each processed synthetic split is stored as a CSV file with the following columns:

- `line_id`: identifier of the original clean text line;
- `variant_id`: identifier of the synthetic noisy variant;
- `noisy`: synthetically corrupted OCR-like text;
- `clean`: original clean text.

The page-level real-OCR benchmark is stored locally as a CSV with page-level OCR output and page-level clean reference text. It is used to test whether a model trained on synthetic noise transfers to real OCR errors.

## Synthetic Splits

| Split | Unique clean lines | Noisy-clean pairs |
|---|---:|---:|
| train | 320 | 6400 |
| valid | 40 | 800 |
| test | 40 | 800 |

The split is performed by original clean lines. Different noisy variants of the same clean line do not appear across different splits.

## Earlier Real-OCR Line-Level Sanity Subset

An earlier small real-OCR subset contains:

| Property | Value |
|---|---:|
| Source pages | 8 |
| Line-level samples | 90 |
| OCR engine | `tesseract_ara_psm6` |
| Use | initial sanity-level synthetic-to-real transfer check |

Results:

| Method | CER | WER | NoSpaceCER | N |
|---|---:|---:|---:|---:|
| Real OCR identity (`tesseract_ara_psm6`) | 0.4508 | 1.0888 | 0.4468 | 90 |
| Synthetic-trained ByT5 on real OCR | 0.4361 | 0.9660 | 0.4454 | 90 |

Line-level CER behavior:

| Category | Count |
|---|---:|
| CER improved | 40 |
| CER unchanged | 33 |
| CER worsened | 17 |

## Page-Level Ottoman Turkish Real-OCR Sanity Benchmark

A newer and more realistic local real-OCR benchmark was constructed from an Ottoman Turkish printed source in Arabic script.

| Property | Value |
|---|---:|
| Source language | Ottoman Turkish |
| Script | Arabic-based script |
| Rendered source pages | 72 |
| Filtered evaluation pages | 68 |
| Clean/reference characters | 90,457 |
| OCR characters | 81,593 |
| OCR engine | `tesseract_ara_psm6` |
| Unit | page-level OCR/reference pairs |
| Repository distribution | summary only; raw data kept local |

Filtered pages exclude short or empty pages. This subset is a realistic sanity benchmark for Arabic-script Turkic real OCR, but it should not be treated as a final benchmark or as an Old Tatar / Old Bashkir dataset.

Page-level evaluation summary:

| System | N | Mean CER | Median CER | Mean WER | Median WER | Mean NoSpaceCER |
|---|---:|---:|---:|---:|---:|---:|
| raw_tesseract | 68 | 0.3539 | 0.2983 | 0.9238 | 0.8943 | 0.3421 |
| byt5_chunked | 68 | 0.4564 | 0.4206 | 0.8919 | 0.8579 | 0.4658 |
| strict_guarded_byt5 | 68 | 0.3828 | 0.3442 | 0.9039 | 0.8605 | 0.3830 |

Interpretation: the synthetic-trained model does not robustly transfer to page-level real OCR. It improves WER slightly but worsens CER and NoSpaceCER. This confirms a synthetic-to-real gap.

## Files

```text
data/postcorrection/raw/arabic_turkic_clean_text.txt
data/postcorrection/raw/SOURCES.md
data/postcorrection/processed/train.csv
data/postcorrection/processed/valid.csv
data/postcorrection/processed/test.csv
data/postcorrection/processed/dataset_stats.csv
data/postcorrection/real_sanity/real_ocr_sanity.csv
docs/nlp_final_revision/tables/real_ocr_postcorrection_metrics.csv
docs/nlp_final_revision/analysis/real_ocr_postcorrection.md
docs/nlp_final_revision/tables/real_ocr_ukr_rus_tur_chunked_summary.csv
docs/nlp_final_revision/analysis/real_ocr_ukr_rus_tur_chunked_transfer.md
```

Local-only page-level real-OCR workspace:

```text
data/real_ocr_dataset_v1/quarantine/WIKI_UKR_RUS_TUR/
```

This workspace is intentionally ignored and should not be committed.

## Synthetic Noise

The benchmark uses controlled synthetic OCR-like text-level noise.

The current noise generator includes:

- character substitution;
- character deletion;
- character insertion;
- whitespace split/merge errors;
- Arabic/Persian form confusion.

The noise generator is useful for a controlled pilot setup, but it does not fully model page-level or image-level OCR/HTR factors such as:

- scan quality;
- font;
- ligatures;
- layout;
- line segmentation;
- page damage;
- column mixing;
- reading order errors.

## Leakage Control

The synthetic dataset split is performed at the level of original clean lines. This prevents the same clean line from appearing in train and test through different noisy variants.

The page-level real-OCR benchmark should be split by page for any future real-domain training/adaptation to avoid chunk leakage across train/dev/test.

## Intended Use

The dataset is intended for:

- OCR post-correction experiments;
- low-resource historical NLP;
- sequence-to-sequence correction;
- baseline comparison;
- educational and reproducibility-focused research;
- sanity-level analysis of synthetic-to-real transfer.

## Out-of-Scope Use

This dataset should not be used to claim:

- solved Old Tatar or Old Bashkir OCR;
- final OCR/HTR quality on real scans;
- production-ready archive transcription;
- general Arabic OCR performance;
- global state of the art in OCR post-correction;
- safe fully automatic correction without human validation.

## Limitations

Current limitations:

- the corpus is small;
- the synthetic corpus is based on limited source material;
- most training/evaluation pairs use synthetic rather than real OCR/HTR errors;
- the real page-level subset currently uses one Ottoman Turkish source;
- the synthetic generator is not calibrated against a real OCR confusion matrix;
- raw page images, OCR, gold text and predictions are kept local and not redistributed;
- no line-crop or PAGE XML / hOCR / ALTO annotations are included yet;
- automatic CER/WER/NoSpaceCER metrics do not fully capture historical-linguistic correctness.

## Recommended Next Dataset Step

The next required dataset improvement is an expanded verified real-OCR benchmark:

- aligned real OCR/reference chunks from page-level OCR and page-level gold;
- page-level train/dev/test splits;
- Old Tatar / Old Bashkir manually checked samples;
- 300–500 manually checked line-level samples as a near-term target;
- 1000+ lines for a stronger benchmark/resource-paper version;
- page or line crops connected to OCR output and clean reference;
- multiple OCR engine/configuration outputs;
- real OCR confusion analysis for real-error-aware synthetic noise.

## Ethical and Legal Notes

Raw source information is documented where possible. Before redistributing any source-derived dataset outside this repository, source permissions and attribution requirements should be checked.
