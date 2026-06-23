# Supervisor update: OCR post-correction for Arabic-script Turkic historical texts

## Current status

The project has been brought to a reproducible final course-project state.

Repository: https://github.com/Therad445/low-resource-arabic-script-turkic-ocr

The current version includes:

- a line-level OCR post-correction pipeline for Arabic-script Turkic historical text;
- a controlled synthetic noisy-clean benchmark;
- train/valid/test split without clean-line leakage;
- identity baseline;
- rule-based normalizer baseline;
- train-derived character-confusion baseline;
- ByT5-small 512 / 2 epochs model;
- CER, WER, NoSpaceCER and ExactMatch evaluation;
- per-example error analysis;
- whitespace sanity check for WER interpretation;
- synthetic-noise robustness and fallback analysis;
- a small real-OCR sanity subset;
- Arabic-only Tesseract real-OCR baseline;
- ByT5 synthetic-to-real transfer evaluation;
- final Russian HSE course paper DOCX;
- defense slides, PDF fallback and speaker notes.

## Main synthetic benchmark results

Final comparison on the synthetic test set:

| Method | CER | WER | ExactMatch | N |
|---|---:|---:|---:|---:|
| Identity baseline | 0.086005 | 0.519006 | 0.001250 | 800 |
| Rule-based normalizer | 0.151932 | 0.684408 | 0.000000 | 800 |
| Train-derived char-confusion baseline | 0.082520 | 0.506189 | 0.001250 | 800 |
| ByT5-small 512 / 2 epochs | 0.079913 | 0.368540 | 0.003750 | 800 |

ByT5-small gives the best result among the evaluated methods on the controlled synthetic benchmark.

## Real-OCR sanity result

A small real-OCR sanity check was added to test synthetic-to-real transfer.

Setup:

- 90 line-level real-OCR samples;
- 8 source pages;
- Arabic-only Tesseract baseline: `tesseract_ara_psm6`;
- same synthetic-trained ByT5 model;
- no real-domain fine-tuning.

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

Interpretation: the model shows partial transfer to real Tesseract OCR output. WER improves more clearly than CER, while NoSpaceCER changes only marginally. Therefore, this should be presented as a sanity-level transfer check, not as a solved real-OCR correction system.

## Important interpretation

The result should be interpreted cautiously.

This is not a full OCR/HTR system and not a production archive OCR evaluation. The current work evaluates line-level post-correction under controlled synthetic OCR-like noise and adds a small real-OCR sanity check.

The large synthetic WER reduction is partly amplified by synthetic whitespace / word-boundary noise, but it is not only a whitespace artifact. A separate sanity check shows:

- raw WER improvement: 0.159354;
- raw CER improvement: 0.013507;
- no-space CER improvement: 0.010374;
- only 9.5% of examples show WER improvement without no-space CER improvement.

Thus, the model improves not only word boundaries but also non-whitespace character-level quality on the synthetic benchmark. On real OCR output, transfer is visible but weaker and unstable.

## Main limitations

- The corpus is small.
- The synthetic benchmark uses limited source material.
- Most training data is synthetic, not real OCR/HTR output.
- The synthetic noise generator is not based on an empirical OCR confusion matrix.
- The real-OCR subset is small and should be treated as a sanity check.
- Some real-OCR line pairs may still contain alignment noise.
- The current model is a pilot ByT5-small experiment, not a final production model.

## Next steps

The most important next steps are:

1. Expand the verified real-OCR benchmark:
   - 300–500 manually checked line-level samples as a near-term target;
   - line crops or page coordinates;
   - clean reference and OCR output alignment.

2. Compare OCR/HTR engines and configurations:
   - Tesseract page-level and line-level modes;
   - Kraken/eScriptorium where feasible;
   - OCR-specific error profiles.

3. Build real-error-aware synthetic noise:
   - confusion matrix from verified real OCR/reference pairs;
   - glyph-similarity and spacing error patterns;
   - better synthetic-to-real transfer.

4. Prepare a short workshop/conference-style paper:
   - frame as a reproducible pilot benchmark;
   - avoid claims of global OCR post-correction state of the art;
   - emphasize low-resource Arabic-script Turkic historical text processing.

## Current cautious claim

A safe formulation is:

> We present a reproducible pilot benchmark for line-level OCR post-correction of Arabic-script Turkic historical text. The project includes controlled synthetic OCR-like noise, simple and neural baselines, robustness and fallback analysis, and a small real-OCR sanity evaluation. ByT5-small outperforms the baselines on the synthetic benchmark and shows partial transfer to real Tesseract OCR output, but robust character-level real-OCR correction remains future work.
