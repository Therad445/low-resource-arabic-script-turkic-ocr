# Model Card: ByT5-small OCR Post-Correction Model

## Model Summary

The main model is a ByT5-small sequence-to-sequence model fine-tuned for OCR post-correction of low-resource Arabic-script Turkic historical text.

The model receives a noisy OCR-like text line and generates a corrected clean text line.

## Task

```text
Input:  noisy Arabic-script Turkic text
Output: corrected clean Arabic-script Turkic text
```

## Compared Methods

The project compares:

1. Identity baseline.
2. Rule-based normalizer.
3. ByT5-small with 512-token source/target length.

## Metrics

The model is evaluated with:

- CER: Character Error Rate;
- WER: Word Error Rate;
- Exact Match.

## Main Result

| Method | CER | WER | ExactMatch |
|---|---:|---:|---:|
| Identity baseline | 0.086005 | 0.519006 | 0.001250 |
| Rule-based normalizer | 0.151932 | 0.684408 | 0.000000 |
| ByT5-small 512 / 2 epochs | 0.079913 | 0.368540 | 0.003750 |

The ByT5-small 512-token configuration achieves the best CER and WER among the evaluated methods on the proposed benchmark.

## Error Analysis

Compared to the identity baseline, the ByT5 model improves most test samples:

| Criterion | Improved | Unchanged | Worse | Total |
|---|---:|---:|---:|---:|
| CER | 682 | 60 | 58 | 800 |
| WER | 677 | 63 | 60 | 800 |

## Limitations

- The model was trained and evaluated on synthetic OCR-like noise.
- It has not yet been validated on real OCR/HTR output.
- Some predictions are worse than the noisy input.
- The model should not be used for fully automatic scholarly transcription without human validation.
