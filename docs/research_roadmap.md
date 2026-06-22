# Research Roadmap

This roadmap summarizes how to move the project from the current course/research pilot toward a stronger workshop paper, master thesis, or benchmark/resource paper.

For the detailed long-term plan, see [`docs/future_work.md`](future_work.md).

## Current state

The repository currently contains:

- a reproducible synthetic OCR-like post-correction benchmark;
- identity, rule-based, train-derived character-confusion and ByT5-small baselines;
- aggregate metrics on the synthetic test split;
- whitespace and no-space sanity analysis;
- synthetic robustness analysis;
- worst-case and conservative fallback analysis;
- a small real-OCR sanity subset;
- Tesseract Arabic-only real-OCR baseline;
- ByT5 synthetic-to-real transfer evaluation;
- qualitative examples for improved, unchanged and worsened real-OCR lines;
- scripts, tables and analysis documents;
- CI checks for the repository.

The current result is a post-correction pilot, not a full OCR/HTR system.

## Safe project claim

> We present a reproducible pilot benchmark for line-level OCR post-correction of Arabic-script Turkic historical text. The project evaluates synthetic OCR-like noise, simple and neural baselines, robustness checks, conservative fallback behavior, and a small real-OCR sanity subset. ByT5-small shows partial transfer to real OCR output, but character-level correction remains limited.

## Claims to avoid

Do not claim:

- global OCR or OCR post-correction state of the art;
- solved Arabic-script Turkic OCR/HTR;
- robust production-ready real-OCR correction;
- validated performance on large real archive collections;
- final benchmark quality for the current 90-line real-OCR subset.

## Completed milestones

- [x] Synthetic post-correction benchmark.
- [x] Identity baseline.
- [x] Rule-based baseline.
- [x] Train-derived char-confusion baseline.
- [x] ByT5-small post-correction model.
- [x] Synthetic test metrics.
- [x] Whitespace / NoSpaceCER sanity check.
- [x] Synthetic noise robustness checks.
- [x] Worst-case analysis and conservative fallback.
- [x] Real-OCR sanity subset.
- [x] Tesseract Arabic-only OCR baseline.
- [x] ByT5 evaluation on real OCR output.
- [x] Real-OCR qualitative examples.
- [x] Real-OCR transfer analysis.
- [x] CI green after experiment and documentation updates.

## Priority 0: Course-project packaging

Goal: finish the current HSE course-project version.

Tasks:

- [ ] Update README with real-OCR sanity results.
- [ ] Link `docs/future_work.md` from README.
- [ ] Update course-paper text with final real-OCR results.
- [ ] Add real-OCR result table to the presentation.
- [ ] Add qualitative examples to slides or appendix.
- [ ] Prepare a 7-8 minute defense script.
- [ ] Send supervisor a compact update.
- [ ] Prepare title page, review and anti-plagiarism package.

## Priority 1: Clean real benchmark

Goal: replace the current sanity-level real-OCR subset with a cleaner line-level benchmark.

Tasks:

- [ ] Verify existing 90 real-OCR line pairs.
- [ ] Mark `alignment_quality`: good / suspicious / bad.
- [ ] Remove bad-alignment pairs from the main benchmark.
- [ ] Expand to 300-500 verified lines.
- [ ] Later expand to 1000+ verified lines.
- [ ] Add domain-expert validation if possible.
- [ ] Document transcription guidelines.

## Priority 2: Line crops and structured annotations

Goal: support real OCR/HTR evaluation, not only text-only post-correction.

Tasks:

- [ ] Create line crops for selected pages.
- [ ] Link each line crop to `clean_text` and `ocr_text`.
- [ ] Preserve page ID, line ID and reading order.
- [ ] Export or support PAGE XML, hOCR or ALTO where feasible.
- [ ] Store annotation guidelines.

## Priority 3: OCR engine baselines

Goal: compare post-correction against stronger OCR pipelines.

Tasks:

- [ ] Keep Tesseract Arabic-only as a baseline.
- [ ] Compare Tesseract `psm6` vs `psm7` on line crops.
- [ ] Add Kraken / eScriptorium OCR baseline.
- [ ] If sufficient line-level ground truth exists, fine-tune a small Kraken model.
- [ ] Evaluate OCR-only and OCR + post-correction.

## Priority 4: Real-error-aware synthetic noise

Goal: improve synthetic-to-real transfer.

Tasks:

- [ ] Build real OCR confusion statistics from verified pairs.
- [ ] Model character substitutions, insertions and deletions.
- [ ] Model whitespace, punctuation and digit errors.
- [ ] Add Arabic-script glyph-similarity substitutions.
- [ ] Add RoundTripOCR-style generation:
  - clean line;
  - render as image;
  - degrade image;
  - run OCR;
  - use OCR output as noisy input.
- [ ] Compare generic synthetic noise vs real-error-aware synthetic noise.

## Priority 5: Model comparison

Goal: make ByT5 one strong baseline among several methods.

Tasks:

- [ ] Keep identity, rule-based and char-confusion baselines.
- [ ] Keep ByT5-small as the main byte-level baseline.
- [ ] Add mT5-small as a multilingual subword baseline.
- [ ] Try ByT5-base if compute and data allow.
- [ ] Train ByT5-small on real-error-aware synthetic noise.
- [ ] Tune conservative fallback on a real dev set.
- [ ] Optionally test an LLM/multimodal LLM upper-bound on a small manually checked sample.

## Priority 6: Error taxonomy and diagnostics

Goal: explain what the models do and fail to do.

Tasks:

- [ ] Categorize errors:
  - whitespace;
  - punctuation;
  - glyph substitutions;
  - missing or extra dots;
  - digit errors;
  - insertions and deletions;
  - hallucinations;
  - alignment errors.
- [ ] Report line improved / unchanged / worsened.
- [ ] Report page-level and engine-level breakdowns.
- [ ] Report good-alignment-only metrics.
- [ ] Add qualitative examples for each important error category.

## Priority 7: Paper / thesis trajectory

### Workshop or short paper

Minimum target:

- 300-500 verified real lines;
- clean line-level alignment;
- Tesseract and at least one stronger OCR baseline or configuration;
- ByT5-small and simple baselines;
- real-error-aware synthetic noise ablation;
- error taxonomy and qualitative analysis.

### Master thesis

Target:

> Benchmark and methods for OCR and post-OCR correction of Arabic-script Tatar / Turkic historical printed texts.

Expected components:

- verified real benchmark;
- line crops;
- OCR engine comparison;
- post-correction model comparison;
- real-error-aware synthetic data;
- domain-expert validation;
- reproducible dataset and code release.

## Estimated effort

| Goal | Approximate effort |
|---|---:|
| Course-project packaging | 10-20 h |
| Clean 300-500 line real benchmark | 40-100 h |
| Line crops and structured annotations | 30-80 h |
| OCR engine comparison | 30-80 h |
| Real-error-aware synthetic noise | 40-100 h |
| Model comparison | 30-80 h |
| Workshop-style paper | 40-100 h |
| Master-thesis-level version | 200+ h |
