# Course paper update snippets for the real-OCR page-level experiment

Use these snippets to update `docs/course_paper_final.md` and `docs/course_paper_hse_export.md` if full automatic replacement is not desired.

## Safer problem framing

The project should be framed as OCR post-correction for low-resource historical Turkic texts written in Arabic-based scripts. Old Tatar and Old Bashkir are the motivating target domains, but the current real-OCR benchmark is an Ottoman Turkish printed source in Arabic script. Therefore, the real-OCR subset is a related Arabic-script Turkic test case, not an Old Tatar or Old Bashkir dataset.

## Real-OCR benchmark subsection

A local page-level real-OCR sanity benchmark was constructed from an Ottoman Turkish printed source in Arabic script. The benchmark contains 72 rendered page images, Tesseract OCR outputs for all pages, and 71 non-empty Wikisource page-level transcriptions. After excluding short or empty pages, the evaluation subset contains 68 pages, 90,457 reference characters and 81,593 OCR characters. Raw source data, images, OCR outputs, transcriptions and prediction files are kept local and are not redistributed in the repository.

## Results table

| System | N | Mean CER | Median CER | Mean WER | Median WER | Mean NoSpaceCER |
|---|---:|---:|---:|---:|---:|---:|
| Raw Tesseract | 68 | 0.3539 | 0.2983 | 0.9238 | 0.8943 | 0.3421 |
| Chunked ByT5 | 68 | 0.4564 | 0.4206 | 0.8919 | 0.8579 | 0.4658 |
| Strict guarded ByT5 | 68 | 0.3828 | 0.3442 | 0.9039 | 0.8605 | 0.3830 |

| System | Improved | Same | Worse |
|---|---:|---:|---:|
| Chunked ByT5 | 6 | 0 | 62 |
| Strict guarded ByT5 | 33 | 3 | 32 |

## Interpretation paragraph

The page-level real-OCR experiment shows that the synthetic-trained ByT5 model does not reliably transfer to real full-page OCR for the Ottoman Turkish source. Although chunked ByT5 slightly improves mean WER, it worsens mean CER and NoSpaceCER. Since character-level accuracy is central for Arabic-script OCR post-correction, the result should be interpreted as mixed or negative transfer rather than successful real-OCR correction. A stricter non-oracle fallback reduces the damage and improves 33 out of 68 pages, but it still does not outperform raw Tesseract on average. This suggests that robust real-OCR correction requires real-domain adaptation, aligned OCR/reference chunks, and real-error-aware training data.

## Updated conclusion sentence

The controlled synthetic benchmark confirms that ByT5-small can learn OCR-like correction patterns in-domain. However, the page-level Ottoman Turkish real-OCR benchmark reveals a strong synthetic-to-real gap: synthetic-only training is insufficient for robust character-level correction of real Arabic-script Turkic OCR. The next step is to build aligned real OCR/reference chunks and fine-tune the model on real OCR errors using page-level train/dev/test splits.
