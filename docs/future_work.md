# Future Work

This document summarizes the future-work strategy for the Arabic-script Turkic OCR post-correction project.

## Current scope

The current repository is a post-OCR correction pilot, not a full OCR/HTR system.

Current task:

```text
noisy OCR-like / OCR text -> post-correction model -> cleaner text
```

Full OCR/HTR is a larger future direction:

```text
page image -> line segmentation -> OCR/HTR recognition -> transcription
```

The current contribution is a reproducible pilot benchmark with:

- synthetic OCR-like post-correction data;
- identity, rule-based, char-confusion and ByT5-small baselines;
- whitespace and NoSpaceCER sanity analysis;
- synthetic robustness and fallback analysis;
- a small real-OCR sanity subset;
- Tesseract Arabic-only real-OCR baseline;
- ByT5 synthetic-to-real transfer evaluation;
- qualitative examples and error analysis.

## Current real-OCR finding

The current real-OCR sanity subset contains 90 line-level samples.

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
| Total | 90 |

Interpretation:

- ByT5 shows partial synthetic-to-real transfer.
- WER improves more clearly than character-level metrics.
- NoSpaceCER changes only marginally.
- The current model does not yet robustly solve real character-level OCR errors.
- The real-OCR subset should be treated as a sanity check, not as a final benchmark.

## Main bottleneck

The main bottleneck is not the lack of a newer model. The main bottleneck is the lack of clean real line-level ground truth.

The next strong version should move from:

```text
synthetic noisy text -> clean text
```

toward:

```text
page image / line crop -> OCR output -> verified clean line -> post-correction evaluation
```

## Phase 1: Clean real benchmark

Goal: build a reliable real-OCR benchmark.

Tasks:

- Collect 300-500 manually verified line-level pairs.
- Later expand to 1000+ verified lines.
- Store metadata:
  - `source_id`
  - `page_id`
  - `line_id`
  - `line_crop_path`
  - `ocr_engine`
  - `ocr_config`
  - `ocr_text`
  - `clean_text`
  - `script_type`
  - `alignment_quality`
  - `notes`
- Mark line pairs as `good`, `suspicious`, or `bad_alignment`.
- Evaluate metrics separately on the `good` subset.
- Remove or quarantine badly aligned pairs from the main benchmark.

## Phase 2: Line crops and structured annotations

Goal: move from text-only sanity checks to document-analysis-ready data.

Tasks:

- Create line crops for selected pages.
- Link each line crop to OCR output and clean transcription.
- Preserve page ID, line ID and reading order.
- Support PAGE XML, hOCR or ALTO where feasible.
- Document annotation rules.

Expected structure:

```text
data/images/pages/
data/images/line_crops/
data/annotations/
data/postcorrection/real_benchmark/
```

## Phase 3: OCR engine baselines

Goal: compare post-correction against stronger OCR pipelines.

Tasks:

- Keep Tesseract Arabic-only as a simple open-source baseline.
- Compare Tesseract page-level and line-level settings:
  - `psm6`
  - `psm7`
  - possibly `psm13`
- Add Kraken / eScriptorium baseline for historical Arabic-script material.
- If enough line-level ground truth exists, fine-tune a small Kraken model.
- Compare:
  - OCR output alone;
  - OCR output + post-correction.

## Phase 4: Better synthetic noise

Goal: make synthetic training data resemble real OCR errors.

Current limitation:

- Generic synthetic noise improves synthetic benchmarks but transfers weakly to real character-level OCR errors.

Future tasks:

- Build a real OCR confusion matrix from verified real OCR/reference pairs.
- Model character substitutions, insertions and deletions.
- Model whitespace, punctuation and digit errors.
- Add Arabic-script glyph-similarity substitutions.
- Add RoundTripOCR-style generation:
  - clean line;
  - render line as image;
  - degrade image;
  - run OCR;
  - use OCR output as noisy input.
- Compare:
  - current generic synthetic noise;
  - real-confusion noise;
  - glyph-similarity noise;
  - RoundTripOCR-style noise.

## Phase 5: Post-correction model comparison

Goal: make ByT5 one baseline among several, not the only model.

Required baselines:

- Identity OCR.
- Rule-based cleanup.
- Train-derived char-confusion baseline.
- ByT5-small.

Future model baselines:

- mT5-small as a multilingual subword seq2seq baseline.
- ByT5-base if compute and data allow.
- ByT5-small trained on real-error-aware synthetic noise.
- ByT5-small with small verified real-domain fine-tuning or dev tuning.
- Conservative fallback tuned on a real dev set.
- Optional LLM / multimodal LLM upper-bound on a small manually checked sample.

Non-priority for now:

- mBART / NLLB as primary correction models.
- Closed LLMs as the main benchmark method.
- Large model swaps before fixing the real benchmark.

## Phase 6: Evaluation and diagnostics

Goal: make evaluation harder to fool and easier to interpret.

Metrics:

- CER.
- WER.
- NoSpaceCER.
- Exact match where useful.
- Line improved / unchanged / worsened.
- Page-level breakdown.
- Engine-level breakdown.
- Good-alignment-only breakdown.

Error categories:

- whitespace and word-boundary errors;
- punctuation errors;
- Arabic-script glyph substitutions;
- missing or extra dots;
- digit errors;
- deletion and insertion errors;
- hallucinated fragments;
- alignment errors;
- destructive corrections.

## Phase 7: Domain collaboration

Goal: make the benchmark linguistically valid.

Tasks:

- Find a domain expert in Old Tatar / Arabic-script Tatar / Turkic historical texts.
- Start with 50-100 verified lines.
- Expand to 300-500 verified lines.
- Define transcription guidelines:
  - preserve original orthography vs normalize;
  - handle Arabic, Persian, Ottoman/Turkic spellings;
  - handle punctuation and digits;
  - handle uncertain readings.
- If the expert contributes transcription, validation, interpretation and paper writing, include them as co-author with clear CRediT roles.

## Phase 8: Publication path

### Course-project version

Claim:

> A reproducible pilot benchmark for OCR post-correction of Arabic-script Turkic historical text, with synthetic data, baselines, ByT5, robustness checks and a real-OCR sanity evaluation.

Do not claim:

- solved OCR;
- state of the art;
- production-ready archive transcription;
- robust character-level correction on real OCR.

### Workshop / short paper version

Minimum additions:

- 300-500 verified real lines;
- better line alignment;
- at least Tesseract + one stronger OCR baseline or configuration;
- real-error-aware synthetic noise ablation;
- clear qualitative examples and error taxonomy.

### Master thesis version

Target:

> Benchmark and methods for OCR and post-OCR correction of Arabic-script Tatar / Turkic historical printed texts.

Expected additions:

- line crops;
- PAGE XML / hOCR / ALTO-like structure;
- OCR engine comparison;
- post-correction model comparison;
- real-error-aware synthetic data;
- domain-expert validation;
- public or partially public dataset release, if licensing allows.

## Literature pointers

Relevant directions:

- Byte-level sequence-to-sequence post-correction:
  - https://arxiv.org/abs/2105.13626
- Synthetic data and glyph-similarity post-OCR correction:
  - https://arxiv.org/abs/2408.02253
- RoundTripOCR-style low-resource post-OCR data generation:
  - https://arxiv.org/abs/2412.15248
- Synthetic corruption for OCR correction:
  - https://arxiv.org/abs/2409.19735
- eScriptorium / Kraken for historical OCR/HTR workflows:
  - https://en.wikipedia.org/wiki/EScriptorium
- PAGE XML for page/line-level ground truth:
  - https://en.wikipedia.org/wiki/Page_Analysis_and_Ground_Truth_Elements
- hOCR for OCR layout and confidence output:
  - https://en.wikipedia.org/wiki/HOCR
