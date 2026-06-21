# Model Card: ByT5-small OCR Post-Correction Model

## Model Summary

The main neural model is `google/byt5-small` fine-tuned for line-level OCR post-correction of low-resource Arabic-script Turkic historical text.

The model receives a noisy OCR-like text line and generates a corrected clean text line.

```text
Input:  noisy Arabic-script Turkic text
Output: corrected clean Arabic-script Turkic text
```

## Task

The task is OCR post-correction, not image-based OCR/HTR.

The model does not read scanned pages. It only corrects already extracted text.

## Compared Methods

The project compares four methods:

1. Identity baseline.
2. Rule-based normalizer.
3. Train-derived character-confusion baseline.
4. ByT5-small 512 / 2 epochs.

## Training / Inference Setup

Main neural configuration:

| Parameter | Value |
|---|---|
| Base model | `google/byt5-small` |
| Task | sequence-to-sequence post-correction |
| Max source length | 512 |
| Max target length | 512 |
| Epochs | 2 |
| Evaluation split | synthetic test set |
| Test size | 800 noisy-clean pairs |

Model weights are not stored in git.

## Metrics

The model is evaluated with:

- CER: Character Error Rate;
- WER: Word Error Rate;
- ExactMatch;
- per-example improved / unchanged / worse analysis;
- no-space CER sanity check for WER interpretation.

## Main Result

Evaluation on the controlled synthetic test split:

| Method | CER ↓ | WER ↓ | ExactMatch ↑ | N |
|---|---:|---:|---:|---:|
| Identity baseline | 0.086005 | 0.519006 | 0.001250 | 800 |
| Rule-based normalizer | 0.151932 | 0.684408 | 0.000000 | 800 |
| Train-derived char-confusion baseline | 0.082520 | 0.506189 | 0.001250 | 800 |
| **ByT5-small 512 / 2 epochs** | **0.079913** | **0.368540** | **0.003750** | 800 |

ByT5-small 512 achieves the best CER and WER among the evaluated methods on this controlled synthetic benchmark.

## Error Analysis

Compared to the identity baseline, ByT5-small improves most test samples:

| Criterion | Improved | Unchanged | Worse | Total |
|---|---:|---:|---:|---:|
| CER | 682 | 60 | 58 | 800 |
| WER | 677 | 63 | 60 | 800 |

The model is not uniformly safe: some predictions are worse than the noisy input.

## Whitespace Sanity Check

The benchmark includes synthetic whitespace / word-boundary errors, so WER improvement requires caution.

A separate sanity check gives:

| Check | Value |
|---|---:|
| Raw WER improvement | 0.159354 |
| Raw CER improvement | 0.013507 |
| No-space CER improvement | 0.010374 |
| WER improved but no-space CER did not improve | 9.50% |

Interpretation:

- WER improvement is partly amplified by whitespace correction.
- The effect is not only a whitespace artifact.
- No-space CER still improves, so the model also improves non-whitespace character-level quality.

## Risks and Failure Modes

Observed risks:

- some predictions are worse than the noisy input;
- the model can over-normalize or introduce new errors;
- some worst cases show unsafe generation behavior;
- the current evaluation is synthetic and may not transfer to real OCR/HTR;
- automatic metrics do not fully capture historical-linguistic validity.

## Appropriate Use

Appropriate use:

- controlled research experiments;
- baseline comparison;
- pilot OCR post-correction studies;
- analysis of Arabic-script Turkic historical text processing.

Inappropriate use:

- fully automatic scholarly transcription without human validation;
- claims of validated real-OCR performance;
- production archive correction;
- legal, genealogical, or historical conclusions without manual review.

## Limitations

- The model was trained and evaluated on synthetic OCR-like noise.
- It has not yet been validated on real OCR/HTR output.
- The corpus is small and source-limited.
- No expert linguistic validation is included yet.
- Model weights are not published in this repository.

## Next Model Steps

Recommended next steps:

1. Evaluate on a small real-OCR/HTR sanity subset.
2. Test alternative synthetic-noise settings.
3. Add fallback rules for suspicious predictions.
4. Compare with larger ByT5 variants and other sequence-to-sequence models.
5. Add manual qualitative evaluation by domain experts.
