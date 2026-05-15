The dataset is located in:

```text
data/postcorrection/processed/
```

## Methods

The following methods were evaluated:

1. Identity baseline: returns the noisy input unchanged.
2. Rule-based normalizer: applies deterministic Arabic-script normalization rules.
3. ByT5-small 128 / 1 epoch: neural byte-level sequence-to-sequence model.
4. ByT5-small 128 train / 256 decode: the same trained model decoded with a larger generation limit.
5. ByT5-small 256 / 2 epochs: neural model trained with longer input/output length and two epochs.

## Metrics

The evaluation uses:

- CER: Character Error Rate.
- WER: Word Error Rate.
- Exact Match: share of predictions exactly equal to the target line.

Lower CER and WER are better. Higher Exact Match is better.

## Results

| Method | CER | WER | Exact Match |
|---|---:|---:|---:|
| Identity baseline | 0.0812 | 0.3655 | 0.0193 |
| Rule-based normalizer | 0.0906 | 0.3932 | 0.0164 |
| ByT5-small 128 / 1 epoch | 0.1290 | 0.3731 | 0.0156 |
| ByT5-small 128 train / 256 decode | 0.0812 | 0.3268 | 0.0171 |
| ByT5-small 256 / 2 epochs | 0.0552 | 0.2368 | 0.0506 |

## Main Finding

The best model is ByT5-small trained with sequence length 256 for two epochs. It reduces CER from 0.0812 for the identity baseline to 0.0552.

This corresponds to approximately 32% relative CER reduction compared with the identity baseline.

## Interpretation

The pilot shows that a byte-level neural model can learn useful post-correction patterns for Arabic-script historical text. The improvement is especially visible in character-level accuracy.

However, the current setup is still a pilot. The noise is synthetic, and the dataset is not yet a full Arabic-Turkic historical benchmark. For the course paper, this is a strong experimental core. For a future article, the next step is to expand the dataset with real OCR outputs and Arabic-Turkic materials.

## Limitations

- The current dataset is based on synthetic OCR-like noise.
- The experiment does not yet evaluate real OCR engine outputs.
- The linguistic scope should be expanded toward Arabic-Turkic historical texts.
- More detailed error analysis is needed.

## Next Steps

1. Add error analysis with successful and failed correction examples.
2. Compare performance across line length groups.
3. Add real OCR outputs if available.
4. Expand the dataset toward Tatar and broader Arabic-Turkic historical materials.
5. Prepare the course paper as an early version of a future benchmark/article.
