# Model Card: ByT5-small OCR Post-Correction Model

## Model Summary

The main neural model is `google/byt5-small` fine-tuned for line-level OCR post-correction of low-resource Arabic-script Turkic historical text.

The model receives noisy OCR-like or OCR text and generates corrected clean text.

```text
Input:  noisy Arabic-script Turkic OCR/OCR-like text
Output: corrected clean Arabic-script Turkic text
```

The model is a text post-correction model. It does not read scanned page images.

## Task

The task is OCR post-correction, not image-based OCR/HTR.

The long-term motivation includes Old Tatar and Old Bashkir materials, but the current page-level real-OCR test source is Ottoman Turkish in Arabic script. It should be treated as a related Arabic-script Turkic test case.

## Compared Methods

The project compares:

1. Identity baseline.
2. Rule-based normalizer.
3. Train-derived character-confusion baseline.
4. ByT5-small 512 / 2 epochs.
5. Chunked ByT5 transfer to page-level real OCR.
6. Conservative / strict fallback variants.

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
| Earlier real-OCR sanity subset | 90 line-level pairs |
| New page-level real-OCR subset | 68 filtered pages |
| Real OCR engine | `tesseract_ara_psm6` |

Model weights are not stored in git.

## Metrics

The model is evaluated with:

- CER: Character Error Rate;
- WER: Word Error Rate;
- NoSpaceCER;
- ExactMatch;
- per-example or per-page improved / unchanged / worse analysis;
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

## Earlier Line-Level Real-OCR Transfer Sanity Check

An earlier small real-OCR sanity evaluation was added after the synthetic benchmark.

Setup:

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

Line-level CER behavior:

| Category | Count |
|---|---:|
| CER improved | 40 |
| CER unchanged | 33 |
| CER worsened | 17 |
| Total | 90 |

This result suggested partial transfer, but it was based on a small line-level subset.

## Page-Level Real-OCR Transfer Evaluation

A stronger page-level real-OCR sanity benchmark was later built from an Ottoman Turkish printed source in Arabic script. The model was applied to page OCR split into model-length chunks and then concatenated back for page-level evaluation.

Setup:

- source: Ottoman Turkish printed text in Arabic script;
- OCR engine: Arabic-only Tesseract (`tesseract_ara_psm6`);
- evaluation unit: page-level OCR/reference pairs;
- filtered evaluation size: 68 pages;
- model: the same ByT5-small model trained on synthetic noise;
- no real-domain fine-tuning.

Results:

| System | N | Mean CER ↓ | Median CER ↓ | Mean WER ↓ | Median WER ↓ | Mean NoSpaceCER ↓ |
|---|---:|---:|---:|---:|---:|---:|
| raw_tesseract | 68 | 0.3539 | 0.2983 | 0.9238 | 0.8943 | 0.3421 |
| byt5_chunked | 68 | 0.4564 | 0.4206 | 0.8919 | 0.8579 | 0.4658 |
| strict_guarded_byt5 | 68 | 0.3828 | 0.3442 | 0.9039 | 0.8605 | 0.3830 |

Page-level CER behavior:

| System | Improved | Same | Worse |
|---|---:|---:|---:|
| byt5_chunked | 6 | 0 | 62 |
| strict_guarded_byt5 | 33 | 3 | 32 |

Interpretation:

- the synthetic-trained model does not reliably transfer to full-page real OCR;
- WER improves slightly, but CER and NoSpaceCER become worse;
- strict fallback reduces damage but still does not outperform raw Tesseract on average by CER;
- robust real-OCR correction requires real-domain adaptation and aligned OCR/reference chunks.

## Risks and Failure Modes

Observed risks:

- some predictions are worse than the noisy input;
- the model can over-normalize or introduce new errors;
- some worst cases show unsafe generation behavior;
- synthetic training noise does not fully match real OCR errors;
- real-OCR transfer is unstable and can be negative on page-level data;
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
- solved Old Tatar / Old Bashkir OCR claims;
- production archive correction;
- legal, genealogical, or historical conclusions without manual review.

## Limitations

- The model was trained mainly on synthetic OCR-like noise.
- The current page-level real-OCR source is Ottoman Turkish, not Old Tatar or Old Bashkir.
- The corpus is small and source-limited.
- No expert linguistic validation is included yet.
- Model weights are not published in this repository.
- The model should be treated as a baseline, not as a final OCR post-correction system.

## Next Model Steps

Recommended next steps:

1. Build aligned OCR/reference chunks from page-level OCR and page-level gold.
2. Split by pages into train/dev/test for real-domain adaptation.
3. Fine-tune ByT5 on real OCR chunks.
4. Build a real OCR confusion profile from OCR/reference pairs.
5. Train or tune on real-error-aware synthetic noise.
6. Compare with larger ByT5 variants and other sequence-to-sequence models.
7. Add manual qualitative evaluation by domain experts.
8. Tune conservative fallback rules on a real validation subset.
