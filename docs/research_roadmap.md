# Research Roadmap

This document lists the next steps required to move the project from a strong course/research pilot toward a workshop or conference-style paper.

## Current State

The project currently has:

- a reproducible synthetic OCR post-correction benchmark;
- identity, rule-based, train-derived character-confusion and ByT5-small baselines;
- aggregate metrics;
- per-example error analysis;
- whitespace sanity check;
- final HSE course paper DOCX;
- supervisor update.

The current result is a controlled pilot result, not a final real-OCR/HTR evaluation.

## Priority 1: Repository Presentation

Goal: make the repository understandable in 2 minutes.

Tasks:

- [x] Update README with current results and limitations.
- [x] Update DATASET_CARD.
- [x] Update MODEL_CARD.
- [x] Add supervisor update.
- [x] Add research roadmap.
- [ ] Check all links from README.
- [ ] Check CI after documentation updates.

## Priority 2: Robustness to Synthetic Noise

Goal: test whether the result depends too strongly on the current synthetic-noise distribution.

Tasks:

- [ ] Add a reduced-whitespace synthetic noise configuration.
- [ ] Add a no-whitespace or near-no-whitespace synthetic noise configuration.
- [ ] Add an alternative random seed.
- [ ] Recompute identity, char-confusion baseline and ByT5 evaluation where feasible.
- [ ] Compare WER, CER and no-space CER across settings.
- [ ] Document whether ByT5 remains better than baselines.

Expected output:

```text
docs/nlp_final_revision/analysis/synthetic_noise_robustness.md
docs/nlp_final_revision/tables/synthetic_noise_robustness_summary.csv
```

## Priority 3: Worst-Case Analysis and Fallback

Goal: understand when the model is unsafe.

Tasks:

- [ ] Identify examples where prediction is much longer than clean/noisy.
- [ ] Identify examples where ByT5 worsens CER.
- [ ] Identify examples where ByT5 worsens WER.
- [ ] Inspect repeated-fragment generation.
- [ ] Test a conservative fallback rule:
  - if prediction is too long;
  - if prediction has abnormal repetition;
  - if prediction changes word count too aggressively;
  - then return noisy input.
- [ ] Compare raw ByT5 vs ByT5+fallback.

Expected output:

```text
docs/nlp_final_revision/analysis/worst_case_analysis.md
docs/nlp_final_revision/tables/fallback_metrics.csv
```

## Priority 4: Real OCR/HTR Sanity Subset

Goal: add external validity beyond synthetic noise.

Tasks:

- [ ] Find 10–30 real page or line-level samples.
- [ ] Obtain real OCR/HTR output.
- [ ] Create manually checked clean reference.
- [ ] Evaluate identity OCR output.
- [ ] Evaluate ByT5 post-correction.
- [ ] Compare synthetic vs real error patterns.

Expected output:

```text
data/postcorrection/real_sanity/
docs/nlp_final_revision/analysis/real_ocr_sanity.md
docs/nlp_final_revision/tables/real_ocr_sanity_metrics.csv
```

## Priority 5: Paper Draft

Goal: prepare a short workshop/conference-style paper.

Safe framing:

> A reproducible pilot benchmark for line-level OCR post-correction of Arabic-script Turkic historical texts under controlled synthetic OCR-like noise.

Claims to avoid:

- global OCR post-correction state of the art;
- solved Arabic-script Turkic OCR;
- validated performance on real archive scans;
- production-ready automatic transcription.

Paper structure:

1. Introduction.
2. Related work.
3. Dataset and synthetic-noise protocol.
4. Baselines and ByT5-small.
5. Results.
6. Whitespace sanity check.
7. Limitations.
8. Real-OCR sanity subset, if ready.
9. Conclusion.

Expected output:

```text
paper/workshop_draft.md
paper/tables/
paper/figures/
```

## Estimated Remaining Work

Approximate remaining effort:

| Goal | Hours |
|---|---:|
| Repository presentation | 5–10 |
| Synthetic robustness | 20–40 |
| Worst-case analysis + fallback | 10–20 |
| Real-OCR sanity subset | 20–60 |
| Paper draft | 30–60 |

Minimum to show supervisor confidently: 10–20 hours.

Minimum for stronger paper trajectory: 60–120 hours.

Stronger submission-ready version: 100–180 hours.
