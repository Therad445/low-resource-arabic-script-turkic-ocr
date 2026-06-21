# Supervisor update: OCR post-correction for Arabic-script Turkic historical texts

## Current status

The project has been brought to a reproducible pilot-study state.

Repository: https://github.com/Therad445/low-resource-arabic-script-turkic-ocr

The current version includes:

- a line-level OCR post-correction pipeline for Arabic-script Turkic historical text;
- a controlled synthetic noisy-clean benchmark;
- train/valid/test split without clean-line leakage;
- identity baseline;
- rule-based normalizer baseline;
- train-derived character-confusion baseline;
- ByT5-small 512 / 2 epochs model;
- CER, WER, ExactMatch evaluation;
- per-example error analysis;
- whitespace sanity check for WER interpretation;
- final Russian HSE course paper DOCX.

## Main experimental results

Final comparison on the synthetic test set:

| Method | CER | WER | ExactMatch | N |
|---|---:|---:|---:|---:|
| Identity baseline | 0.086005 | 0.519006 | 0.001250 | 800 |
| Rule-based normalizer | 0.151932 | 0.684408 | 0.000000 | 800 |
| Train-derived char-confusion baseline | 0.082520 | 0.506189 | 0.001250 | 800 |
| ByT5-small 512 / 2 epochs | 0.079913 | 0.368540 | 0.003750 | 800 |

ByT5-small gives the best result among the evaluated methods on the controlled synthetic benchmark.

## Important interpretation

The result should be interpreted cautiously.

This is not a full OCR/HTR system and not a real archive OCR evaluation. The current work evaluates line-level post-correction under controlled synthetic OCR-like noise.

The large WER reduction is partly amplified by synthetic whitespace / word-boundary noise, but it is not only a whitespace artifact. A separate sanity check shows:

- raw WER improvement: 0.159354;
- raw CER improvement: 0.013507;
- no-space CER improvement: 0.010374;
- only 9.5% of examples show WER improvement without no-space CER improvement.

Thus, the model improves not only word boundaries but also non-whitespace character-level quality. Still, real OCR/HTR validation is required before making stronger claims.

## Main limitations

- The corpus is small: 400 clean text blocks.
- The benchmark uses one main Ottoman-Turkic source.
- Noise is synthetic, not produced by a real OCR/HTR system.
- The noise generator is not based on an empirical OCR confusion matrix.
- There is no manually validated real-OCR subset yet.
- The current model is a pilot ByT5-small experiment, not a final production model.

## Next steps

The most important next steps are:

1. Build a small real-OCR/HTR sanity subset:
   - 10–30 page or line-level samples;
   - OCR/HTR output;
   - manually checked clean reference.

2. Run the same evaluation protocol on real OCR/HTR output.

3. Add an alternative synthetic-noise robustness test:
   - reduced whitespace noise;
   - different substitution/deletion probabilities;
   - evaluation of whether ByT5 remains better than baselines.

4. Prepare a short workshop/conference-style paper:
   - frame as a reproducible pilot benchmark;
   - avoid claims of global OCR post-correction state of the art;
   - emphasize low-resource Arabic-script Turkic historical text processing.

## Current cautious claim

A safe formulation is:

> We present a reproducible pilot benchmark for line-level OCR post-correction of Arabic-script Turkic historical text under controlled synthetic OCR-like noise. ByT5-small outperforms identity, rule-based normalization, and a train-derived character-confusion baseline on this benchmark. However, the results should be interpreted as controlled pilot evidence, not as proof of practical performance on real OCR/HTR outputs.
