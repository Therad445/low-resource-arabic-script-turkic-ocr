# Synthetic Noise Robustness Check

This document summarizes a lightweight robustness check for the synthetic OCR-like
noise generator.

The check regenerates train/test noisy-clean pairs under several noise settings
and evaluates non-neural baselines. It does **not** retrain or run ByT5; neural
robustness requires a separate model rerun.

## Setup

- Variants per clean line: 20
- Base seed: 2026
- Train/test clean-line split: inherited from existing processed train/test CSV files.
- Evaluated methods:
  - identity baseline;
  - rule-based normalizer;
  - train-derived character-confusion baseline.

## Summary

| config                   | method                                |       CER |      WER |   NoSpaceCER |   ExactMatch |   N |   mean_noisy_clean_word_delta |   same_word_count_share |
|:-------------------------|:--------------------------------------|----------:|---------:|-------------:|-------------:|----:|------------------------------:|------------------------:|
| default_reseed           | Identity baseline                     | 0.0871342 | 0.522079 |    0.0838803 |      0.00125 | 800 |                       0.67625 |                 0.32875 |
| default_reseed           | Rule-based normalizer                 | 0.153074  | 0.688873 |    0.160803  |      0       | 800 |                       0.67625 |                 0.32875 |
| default_reseed           | Train-derived char-confusion baseline | 0.0815628 | 0.503243 |    0.0774054 |      0       | 800 |                       0.67625 |                 0.32875 |
| reduced_whitespace       | Identity baseline                     | 0.0788676 | 0.442753 |    0.085928  |      0       | 800 |                       0.22125 |                 0.61125 |
| reduced_whitespace       | Rule-based normalizer                 | 0.144621  | 0.621371 |    0.162488  |      0       | 800 |                       0.22125 |                 0.61125 |
| reduced_whitespace       | Train-derived char-confusion baseline | 0.0736607 | 0.42262  |    0.079892  |      0       | 800 |                       0.22125 |                 0.61125 |
| no_whitespace            | Identity baseline                     | 0.0744568 | 0.39452  |    0.0862955 |      0.00125 | 800 |                      -0.0075  |                 0.9925  |
| no_whitespace            | Rule-based normalizer                 | 0.140534  | 0.583904 |    0.163211  |      0       | 800 |                      -0.0075  |                 0.9925  |
| no_whitespace            | Train-derived char-confusion baseline | 0.071182  | 0.381869 |    0.0825    |      0.0025  | 800 |                      -0.0075  |                 0.9925  |
| low_noise                | Identity baseline                     | 0.0456298 | 0.314039 |    0.0438782 |      0.015   | 800 |                       0.39    |                 0.46875 |
| low_noise                | Rule-based normalizer                 | 0.117705  | 0.556675 |    0.127888  |      0       | 800 |                       0.39    |                 0.46875 |
| low_noise                | Train-derived char-confusion baseline | 0.0440255 | 0.305717 |    0.0420267 |      0.015   | 800 |                       0.39    |                 0.46875 |
| char_heavy_no_whitespace | Identity baseline                     | 0.0940163 | 0.472328 |    0.109028  |      0       | 800 |                      -0.015   |                 0.985   |
| char_heavy_no_whitespace | Rule-based normalizer                 | 0.156296  | 0.625567 |    0.18139   |      0       | 800 |                      -0.015   |                 0.985   |
| char_heavy_no_whitespace | Train-derived char-confusion baseline | 0.0864513 | 0.443633 |    0.100212  |      0       | 800 |                      -0.015   |                 0.985   |

## Interpretation Guide

The key question is whether the benchmark difficulty and baseline behavior change
substantially when whitespace noise is reduced or removed.

Important columns:

- `CER`: character-level error rate.
- `WER`: word-level error rate.
- `NoSpaceCER`: CER after removing all whitespace before evaluation.
- `mean_noisy_clean_word_delta`: average word-count difference between noisy and clean text.
- `same_word_count_share`: share of examples where noisy and clean have the same number of words.

## Current Conclusion

This is a baseline-only robustness scaffold. It helps quantify how much synthetic
whitespace noise changes dataset difficulty. The next stronger step is to run
ByT5 prediction on the same regenerated test sets or retrain/evaluate models under
the alternative noise settings.

A safe wording is:

> The current synthetic-noise robustness check shows how baseline difficulty changes
> when whitespace noise is reduced or removed. It does not yet prove neural robustness,
> but it provides the scaffold for a controlled ByT5 rerun.
