# Whitespace sanity check for WER improvement

This check evaluates whether the large WER improvement of ByT5-small is mainly caused by synthetic whitespace / word-boundary noise.

## Key results

- Raw WER improvement: 0.159354
- Raw CER improvement: 0.013507
- No-space CER improvement: 0.010374
- Share of examples where WER improved but no-space CER did not improve: 9.50%

## Interpretation

The WER improvement is partially affected by whitespace and word-boundary errors, but it is not only a whitespace artifact. After removing all whitespace, no-space CER still improves by 0.010374. In 75.1% of test examples, WER improves together with no-space CER. Only 9.5% of examples show WER improvement without no-space CER improvement.

The effect is stronger when the noisy input changes word count:

- same_word_count: WER improvement = 0.111426, no-space CER improvement = 0.015576
- changed_word_count: WER improvement = 0.183986, no-space CER improvement = 0.007731

Therefore, the cautious conclusion is:

> The large WER reduction is partly amplified by synthetic whitespace / word-boundary noise, but the model also improves non-whitespace character-level quality. The result should be interpreted as evidence for a controlled synthetic benchmark, not as proof of equivalent performance on real OCR/HTR outputs.
