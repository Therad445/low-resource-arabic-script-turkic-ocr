# Worst-Case Analysis and Conservative Fallback

This analysis inspects unsafe ByT5 post-correction cases and evaluates a simple
conservative fallback rule.

The fallback rule uses only the noisy input and model prediction. It does not use
the clean reference during decision-making. The clean reference is used only for
evaluation.

## Corpus-Level Metrics

| method                       |       CER |      WER |   NoSpaceCER |   ExactMatch |   N |
|:-----------------------------|----------:|---------:|-------------:|-------------:|----:|
| Identity baseline            | 0.0865235 | 0.514099 |    0.0838092 |      0.00125 | 800 |
| ByT5-small 512 / 2 epochs    | 0.0730164 | 0.354746 |    0.0734356 |      0.00375 | 800 |
| ByT5 + conservative fallback | 0.059908  | 0.340028 |    0.0607185 |      0.00375 | 800 |

## Fallback Rule

The fallback returns the original noisy input instead of the ByT5 prediction if
the prediction looks suspicious according to at least one of these signals:

- empty prediction;
- prediction is much longer than noisy input;
- prediction is much shorter than noisy input;
- large word-count change relative to noisy input;
- long repeated character run;
- repeated token bigram.

## Fallback Frequency

- Fallback applied: 10 / 800 examples (1.25%)
- ByT5 worse than identity by CER: 58 / 800
- ByT5 worse than identity by WER: 60 / 800
- Fallback prevented CER-worse cases: 10
- Fallback hurt examples by CER relative to raw ByT5: 0

## Fallback Reasons

| reason                  |   N |   share_of_all |
|:------------------------|----:|---------------:|
| large_word_count_change |  10 |        0.0125  |
| prediction_too_long     |   6 |        0.0075  |
| repeated_token_bigram   |   1 |        0.00125 |
| prediction_too_short    |   1 |        0.00125 |

## Interpretation

This is a deliberately conservative engineering check. A useful fallback should
reduce severe model failures without noticeably damaging aggregate CER/WER.

If fallback metrics are worse than raw ByT5, the current rule is too aggressive.
If fallback metrics are similar or slightly better while reducing severe failures,
the rule is a useful safety layer for real-OCR experiments.

A safe wording is:

> ByT5 improves most examples, but it is not uniformly safe. A conservative
> fallback based only on prediction-shape heuristics can be used as a diagnostic
> safety layer, although final acceptance still requires real OCR/HTR validation
> and human review.
