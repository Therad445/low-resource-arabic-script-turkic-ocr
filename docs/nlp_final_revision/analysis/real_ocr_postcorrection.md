# Real-OCR post-correction transfer analysis

This note summarizes a small real-OCR sanity evaluation for the synthetic-trained ByT5 post-correction model.

The model was trained on synthetic OCR-like noise and evaluated on a small real-OCR subset produced with Arabic-only Tesseract (`tesseract_ara_psm6`). The goal is not to claim a final production-level OCR correction benchmark, but to test whether the synthetic post-correction model transfers at all to real OCR errors.

## Aggregate results

| Method | CER | WER | NoSpaceCER | N |
|---|---:|---:|---:|---:|
| Real OCR identity (`tesseract_ara_psm6`) | 0.4508 | 1.0888 | 0.4468 | 90 |
| Synthetic-trained ByT5 on real OCR | 0.4361 | 0.9660 | 0.4454 | 90 |
| Synthetic-trained ByT5 + conservative fallback | 0.4361 | 0.9660 | 0.4454 | 90 |

The model improves WER more clearly than character-level metrics. CER improves modestly, while NoSpaceCER changes only marginally. This suggests partial but limited synthetic-to-real transfer: the model captures some spacing, formatting, and local normalization patterns, but does not yet robustly solve real character-level OCR errors.

## Per-line CER behavior

| Category | Count |
|---|---:|
| CER improved | 40 |
| CER unchanged | 33 |
| CER worsened | 17 |
| Total | 90 |

The model improves more lines than it worsens, but the behavior is not stable enough to claim robust real-OCR correction. The result is best interpreted as a sanity-level transfer check and a diagnostic for the synthetic-noise setup.

## Page-level CER breakdown

| Page | N | Identity CER | ByT5 CER | Delta |
|---|---:|---:|---:|---:|
| page_044 | 15 | 0.5746 | 0.5659 | +0.0087 |
| page_045 | 15 | 0.4201 | 0.3964 | +0.0238 |
| page_046 | 10 | 0.3793 | 0.3769 | +0.0024 |
| page_047 | 10 | 0.3091 | 0.3061 | +0.0031 |
| page_051 | 11 | 0.3755 | 0.3677 | +0.0078 |
| page_052 | 9 | 0.2895 | 0.2839 | +0.0055 |
| page_053 | 9 | 0.4278 | 0.4121 | +0.0157 |
| page_056 | 11 | 0.7435 | 0.6982 | +0.0453 |

All evaluated pages show a positive average CER delta, although the magnitude varies substantially by page.

## Qualitative examples

### 1. Improved example

Sample: `real_056_002`

| Version | Text |
|---|---|
| OCR | `( بولتاوا ) » ( حهرنيهوف ) و (خارقوف) أبالتلرنى احتوا ابدر .` |
| ByT5 prediction | `(بولتاوا) » (حرنيهوف) و (خارقوف) أبالتلرنى احتوا ابدر.` |
| Clean reference | `(پولتاوا)، (چەرنيهوف) و(خارقوف) أيالتلريني احتوا ايدر.` |

Metrics:

| Metric | Value |
|---|---:|
| Identity CER | 0.2778 |
| Prediction CER | 0.1852 |

The model removes some spurious spaces around parentheses and moves the OCR output closer to the reference structure. It does not fully restore the correct Arabic-script Turkic spelling, but the CER improvement is meaningful for this line.

### 2. Mostly unchanged example

Sample: `real_051_003`

| Version | Text |
|---|---|
| OCR | `شبرنده» كتاب طبع ونشريه اشتغال ابدر درت بوبوك اوقراينا` |
| ByT5 prediction | `شبرنده» كتاب طبع ونشريه اشتغال ابدر درت بوبوك اوقراينا` |
| Clean reference | `شهرنده، کتاب طبع ونشريله اشتغال ایدر درت بويوك اوقراينا` |

Metrics:

| Metric | Value |
|---|---:|
| Identity CER | 0.1091 |
| Prediction CER | 0.1091 |

The model leaves the line unchanged. This is useful because it shows that the model is not always destructive, but it also means that it fails to correct real character-level OCR errors in this example.

### 3. Worsened example

Sample: `real_044_004`

| Version | Text |
|---|---|
| OCR | `قادار ح.قارمش وعنى زمانده اوقراينا اقفكار مله وسساسهدسنك` |
| ByT5 prediction | `قادار ح. قارمش وعنى زمانده اوقراينا اقفكار مله وساسهدنك` |
| Clean reference | `قادار چیقارمش وعينى زمانده اوقراينا افكار مليه وسياسيەسنك` |

Metrics:

| Metric | Value |
|---|---:|
| Identity CER | 0.1404 |
| Prediction CER | 0.1754 |

The model introduces local formatting and spelling changes, but does not fix the important character-level OCR errors. The prediction becomes worse by CER. This illustrates the risk of destructive correction when a model trained on synthetic noise is applied to real OCR outputs without real-domain adaptation.

## Interpretation

The real-OCR evaluation shows partial but unstable transfer. ByT5 improves 40 out of 90 lines by CER and reduces average CER on every evaluated page, but it also worsens 17 lines. Since NoSpaceCER is almost unchanged, much of the observed improvement likely comes from spacing, formatting, and word-level normalization rather than robust correction of character-level OCR errors.

This is therefore not a final solution to real Arabic-script Turkic OCR post-correction. Instead, it is evidence that synthetic training provides a useful but incomplete starting point. A stronger real-OCR system would require more manually checked real OCR pairs, better synthetic noise modeling based on real OCR confusions, and possibly small-scale fine-tuning or validation on real-domain data.

## Limitations

- The real-OCR subset is small: 90 line-level samples.
- The subset is based on one historical source and one OCR engine.
- Some line pairs may still contain noisy alignment between OCR output and reference text.
- The model was trained only on synthetic noise, not on real OCR pairs.
- Results should be interpreted as a real-OCR sanity check, not as a final benchmark.

## Future work

- Expand the real-OCR subset to several hundred manually verified lines.
- Add page and line crops to support full OCR/HTR benchmarking.
- Compare multiple OCR engines and OCR configurations.
- Build a real-error confusion profile and use it to improve synthetic noise generation.
- Evaluate small real-domain fine-tuning or validation-based fallback strategies.
