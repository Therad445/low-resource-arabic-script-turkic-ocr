# Real-OCR transfer evaluation on an Ottoman Turkish source

## Scope

This note reports a page-level real-OCR transfer experiment for the OCR post-correction model. The real source is an Ottoman Turkish printed text in Arabic script. It is used as a related Arabic-script Turkic test case, not as an Old Tatar or Old Bashkir dataset.

The broader target of the project is OCR post-correction for low-resource historical Turkic texts written in Arabic-based scripts. Old Tatar and Old Bashkir remain the motivating target domains, while this real-OCR experiment uses an available Ottoman Turkish source with page images and page-level transcriptions.

## Dataset

The local real-OCR benchmark contains:

- 72 rendered page images from the source PDF;
- 72 Tesseract OCR outputs using the Arabic OCR model;
- 71 non-empty Wikisource page-level transcriptions;
- 68 filtered evaluation pages after removing short or empty pages.

The filtered evaluation subset contains 90,457 clean/reference characters and 81,593 OCR characters.

Raw source data, page images, OCR outputs, page-level transcriptions, and prediction files are kept local and are not redistributed in the repository.

## Systems

The experiment compares:

1. **raw_tesseract**: raw Tesseract OCR output;
2. **byt5_chunked**: synthetic-trained ByT5 applied to page OCR split into model-length chunks;
3. **guarded_byt5**: the script-level conservative fallback;
4. **strict_guarded_byt5**: a stricter non-oracle fallback applied after generation.

## Results

| System | N | Mean CER | Median CER | Mean WER | Median WER | Mean NoSpaceCER | Median NoSpaceCER |
|---|---:|---:|---:|---:|---:|---:|---:|
| raw_tesseract | 68 | 0.3539 | 0.2983 | 0.9238 | 0.8943 | 0.3421 | 0.2810 |
| byt5_chunked | 68 | 0.4564 | 0.4206 | 0.8919 | 0.8579 | 0.4658 | 0.4280 |
| guarded_byt5 | 68 | 0.4564 | 0.4206 | 0.8919 | 0.8579 | 0.4658 | 0.4280 |
| strict_guarded_byt5 | 68 | 0.3828 | 0.3442 | 0.9039 | 0.8605 | 0.3830 | 0.3425 |

Page-level CER status counts:

| System | Improved | Same | Worse |
|---|---:|---:|---:|
| byt5_chunked | 6 | 0 | 62 |
| guarded_byt5 | 6 | 0 | 62 |
| strict_guarded_byt5 | 33 | 3 | 32 |

## Interpretation

The synthetic-trained ByT5 model does not reliably transfer to full-page real OCR for the Ottoman Turkish source. It slightly improves WER, but substantially worsens CER and NoSpaceCER. Since character-level accuracy is central for OCR post-correction in Arabic script, the main result is negative or mixed transfer rather than a successful real-OCR improvement.

The strict fallback reduces the damage and improves more pages than the unguarded model, but it still does not outperform raw Tesseract on average. This suggests that robust real-OCR correction requires real-domain adaptation, aligned OCR/reference chunks, and real-error-aware training data.

## Takeaway

The experiment strengthens the paper by showing a realistic synthetic-to-real gap:

- ByT5 learns synthetic OCR-like corrections in-domain.
- Real page-level Ottoman Turkish OCR has a different error distribution.
- Synthetic-only training is insufficient for reliable real-OCR post-correction.
- Future work should train or adapt on aligned real OCR chunks.
