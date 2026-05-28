# NLP Course Final Project

## Title

**A Reproducible Benchmark for OCR Post-Correction of Low-Resource Arabic-Script Turkic Historical Texts**

## Task

The project studies OCR post-correction as a sequence-to-sequence NLP task:

```text
noisy OCR-like text -> clean historical text
```

The work focuses on historical Turkic texts written in Arabic script. It does **not** claim to solve full OCR/HTR from document images. Instead, it isolates the post-correction stage and evaluates whether neural sequence-to-sequence correction improves noisy text compared with simple baselines.

## Main Artifacts

- Report source: [`report/main.tex`](report/main.tex)
- Submission PDF: [`report/final_report.pdf`](report/final_report.pdf)
- Dataset card: [`DATASET_CARD.md`](DATASET_CARD.md)
- Model card: [`MODEL_CARD.md`](MODEL_CARD.md)
- Reproduction guide: [`REPRODUCE.md`](REPRODUCE.md)

## Dataset

| Split | Clean lines | Noisy-clean pairs | Avg. clean chars | Avg. noisy chars |
|---|---:|---:|---:|---:|
| train | 320 | 6400 | 113.94 | 113.51 |
| valid | 40 | 800 | 112.75 | 112.24 |
| test | 40 | 800 | 122.25 | 121.70 |

The split is performed by original clean lines, so noisy variants of the same clean line do not appear in different splits.

## Methods

The project compares:

1. **Identity baseline** — returns noisy input unchanged.
2. **Rule-based normalizer** — applies simple Arabic-script normalization rules.
3. **ByT5-small 512 / 2 epochs** — byte-level sequence-to-sequence post-correction model.

## Main Results

| Method | CER ↓ | WER ↓ | Exact Match ↑ | N |
|---|---:|---:|---:|---:|
| Identity baseline | 0.086005 | 0.519006 | 0.001250 | 800 |
| Rule-based normalizer | 0.151932 | 0.684408 | 0.000000 | 800 |
| **ByT5-small 512 / 2 epochs** | **0.079913** | **0.368540** | **0.003750** | 800 |

**Main claim:** ByT5-small 512 achieves the best CER and WER among the evaluated methods on the proposed benchmark.

## Error Analysis

| Criterion | Improved | Unchanged | Worse | Total |
|---|---:|---:|---:|---:|
| CER | 682 | 60 | 58 | 800 |
| WER | 677 | 63 | 60 | 800 |

The model improves most test examples, but not all of them. Therefore, it should be treated as an assistive post-correction component rather than a fully automatic scholarly transcription system.

## Limitations

- The corpus is small.
- The current dataset uses one main source.
- The errors are synthetic, not real OCR/HTR output.
- Manual linguistic validation is still required.
- The project is a pilot benchmark, not a finished production OCR system.
