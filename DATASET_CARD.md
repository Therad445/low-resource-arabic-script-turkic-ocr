# Dataset Card: Arabic-Script Turkic OCR Post-Correction Benchmark

## Dataset Summary

This repository contains a pilot benchmark for OCR post-correction of historical Turkic text written in Arabic script.

The main synthetic task is formulated as line-level sequence-to-sequence correction:

```text
noisy -> clean
```

The clean text was collected from an Ottoman Turkish / Arabic-script Turkic Wikisource source. Synthetic OCR-like corruptions were then generated to create noisy-clean pairs.

The repository also includes a small **real-OCR sanity subset**. In that subset, Arabic-only Tesseract output is used as the noisy OCR input, and manually aligned clean text is used as the reference for evaluation.

The dataset is intended for controlled pilot experiments and sanity-level transfer analysis. It is **not** a final real-OCR benchmark and should not be used to claim production OCR quality.

## Dataset Structure

Each processed synthetic split is stored as a CSV file with the following columns:

- `line_id`: identifier of the original clean text line;
- `variant_id`: identifier of the synthetic noisy variant;
- `noisy`: synthetically corrupted OCR-like text;
- `clean`: original clean text.

The real-OCR sanity subset is stored as a CSV file with real OCR output and clean references. It is used to test whether a model trained on synthetic noise transfers to real OCR errors.

## Synthetic Splits

| Split | Unique clean lines | Noisy-clean pairs |
|---|---:|---:|
| train | 320 | 6400 |
| valid | 40 | 800 |
| test | 40 | 800 |

The split is performed by original clean lines. Different noisy variants of the same clean line do not appear across different splits.

## Real-OCR Sanity Subset

The current real-OCR sanity subset contains:

| Property | Value |
|---|---:|
| Source pages | 8 |
| Line-level samples | 90 |
| OCR engine | `tesseract_ara_psm6` |
| Use | sanity-level synthetic-to-real transfer check |

The subset should be treated as a small validation sample, not as a final benchmark. It is useful for identifying domain-gap behavior between synthetic OCR-like noise and real Tesseract OCR output.

Current real-OCR baseline and transfer results:

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

Interpretation: the synthetic-trained model shows partial transfer to real OCR output, but robust real character-level OCR correction remains future work.

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
docs/nlp_final_revision/tables/real_ocr_postcorrection_predictions.csv
```

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

The synthetic dataset split is performed at the level of original clean lines.

This prevents the same clean line from appearing in train and test through different noisy variants.

Recorded clean-line overlap:

| Overlap | Count |
|---|---:|
| train ∩ valid | 0 |
| train ∩ test | 0 |
| valid ∩ test | 0 |

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
- the synthetic generator is not calibrated against a real OCR confusion matrix;
- the real-OCR subset is small and should be treated as a sanity check;
- some real-OCR line pairs may still contain alignment noise;
- no line-crop or PAGE XML / hOCR / ALTO annotations are included yet;
- automatic CER/WER/NoSpaceCER metrics do not fully capture historical-linguistic correctness.

## Recommended Next Dataset Step

The next required dataset improvement is an expanded verified real-OCR benchmark:

- 300–500 manually checked line-level samples as a near-term target;
- 1000+ lines for a stronger benchmark/resource-paper version;
- page or line crops connected to OCR output and clean reference;
- multiple OCR engine/configuration outputs;
- real OCR confusion analysis for real-error-aware synthetic noise.

## Ethical and Legal Notes

Raw source information is documented in:

```text
data/postcorrection/raw/SOURCES.md
```

Before redistributing the dataset outside this repository, source permissions and attribution requirements should be checked.
