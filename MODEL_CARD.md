# Model Card: ByT5-small OCR Post-Correction Model

## Model Summary

The main neural model is `google/byt5-small` fine-tuned for line-level OCR post-correction of low-resource Arabic-script Turkic historical text.

The model receives a noisy OCR-like or real OCR text line and generates a corrected clean text line.

```text
Input:  noisy Arabic-script Turkic OCR/OCR-like text
Output: corrected clean Arabic-script Turkic text
```

## Task

The task is OCR post-correction, not image-based OCR/HTR.

The model does not read scanned pages. It only corrects already extracted text.

## Compared Methods

The project compares four main methods:

1. Identity baseline.
2. Rule-based normalizer.
3. Train-derived character-confusion baseline.
4. ByT5-small 512 / 2 epochs.

Additional analyses include a conservative fallback check, synthetic-noise robustness checks, whitespace sanity analysis, and a small real-OCR transfer sanity check.

## Training / Inference Setup

Main neural configuration:

| Parameter | Value |
|---|---|
| Base model | `google/byt5-small` |
| Task | sequence-to-sequence post-correction |
| Max source length | 512 |
| Max target length | 512 |
| Epochs | 2 |
| Main evaluation split | synthetic test set |
| Synthetic test size | 800 noisy-clean pairs |
| Real-OCR sanity subset | 90 line-level pairs |
| Real OCR engine | `tesseract_ara_psm6` |

Model weights are not stored in git.

## Metrics

The model is evaluated with:

- CER: Character Error Rate;
- WER: Word Error Rate;
- NoSpaceCER;
- ExactMatch;
- per-example improved / unchanged / worse analysis;
- qualitative example analysis.

## Main Synthetic Result

Evaluation on the controlled synthetic test split:

| Method | CER ↓ | WER ↓ | ExactMatch ↑ | N |
|---|---:|---:|---:|---:|
| Identity baseline | 0.086005 | 0.519006 | 0.001250 | 800 |
| Rule-based normalizer | 0.151932 | 0.684408 | 0.000000 | 800 |
| Train-derived char-confusion baseline | 0.082520 | 0.506189 | 0.001250 | 800 |
| **ByT5-small 512 / 2 epochs** | **0.079913** | **0.368540** | **0.003750** | 800 |

ByT5-small 512 achieves the best CER and WER among the evaluated methods on this controlled synthetic benchmark.

## Synthetic Error Analysis

Compared to the identity baseline, ByT5-small improves most synthetic test samples:

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
- No-space CER still improves on the synthetic benchmark, so the model also improves non-whitespace character-level quality there.

## Real-OCR Transfer Sanity Check

A small real-OCR sanity evaluation was added after the synthetic benchmark.

Setup:

- source: Arabic-script Turkic historical pages;
- OCR engine: Arabic-only Tesseract (`tesseract_ara_psm6`);
- evaluation unit: line-level OCR/reference pairs;
- sample size: 90 lines;
- model: the same ByT5-small model trained on synthetic noise;
- no real-domain fine-tuning.

Results:

| Method | CER ↓ | WER ↓ | NoSpaceCER ↓ | N |
|---|---:|---:|---:|---:|
| Real OCR identity (`tesseract_ara_psm6`) | 0.4508 | 1.0888 | 0.4468 | 90 |
| Synthetic-trained ByT5 on real OCR | 0.4361 | 0.9660 | 0.4454 | 90 |
| Synthetic-trained ByT5 + conservative fallback | 0.4361 | 0.9660 | 0.4454 | 90 |

Line-level CER behavior:

| Category | Count |
|---|---:|
| CER improved | 40 |
| CER unchanged | 33 |
| CER worsened | 17 |
| Total | 90 |

Interpretation:

- the synthetic-trained model shows partial transfer to real OCR output;
- WER improves more clearly than CER;
- NoSpaceCER changes only marginally;
- robust real character-level OCR correction is not solved yet;
- real-error-aware synthetic noise and a larger verified real benchmark are the next main steps.

## Risks and Failure Modes

Observed risks:

- some predictions are worse than the noisy input;
- the model can over-normalize or introduce new errors;
- some worst cases show unsafe generation behavior;
- synthetic training noise does not fully match real OCR errors;
- real-OCR transfer is partial and unstable;
- automatic metrics do not fully capture historical-linguistic validity.

## Appropriate Use

Appropriate use:

- controlled research experiments;
- baseline comparison;
- pilot OCR post-correction studies;
- analysis of Arabic-script Turkic historical text processing;
- sanity-level synthetic-to-real transfer analysis.

Inappropriate use:

- fully automatic scholarly transcription without human validation;
- claims of production-ready real-OCR performance;
- production archive correction;
- legal, genealogical, or historical conclusions without manual review.

## Limitations

- The model was trained mainly on synthetic OCR-like noise.
- The real-OCR evaluation is small and should be treated as a sanity check.
- The corpus is small and source-limited.
- No expert linguistic validation is included yet.
- Model weights are not published in this repository.
- The model should be treated as a baseline, not as a final OCR post-correction system.

## Next Model Steps

Recommended next steps:

1. Expand the verified real-OCR benchmark.
2. Build a real OCR confusion profile from OCR/reference pairs.
3. Train or tune on real-error-aware synthetic noise.
4. Compare with larger ByT5 variants and other sequence-to-sequence models.
5. Add manual qualitative evaluation by domain experts.
6. Tune conservative fallback rules on a real validation subset.
