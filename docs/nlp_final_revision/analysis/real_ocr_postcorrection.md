# Real-OCR post-correction analysis

This file summarizes two real-OCR sanity checks used in the project.

## 1. Earlier line-level sanity subset

The earlier real-OCR sanity subset contained 90 line-level OCR/reference pairs. It was used as a first transfer check after training ByT5 on synthetic OCR-like noise.

| Method | CER | WER | NoSpaceCER | N |
|---|---:|---:|---:|---:|
| Real OCR identity (`tesseract_ara_psm6`) | 0.4508 | 1.0888 | 0.4468 | 90 |
| Synthetic-trained ByT5 on real OCR | 0.4361 | 0.9660 | 0.4454 | 90 |

Line-level CER behavior:

| Category | Count |
|---|---:|
| Improved | 40 |
| Unchanged | 33 |
| Worsened | 17 |

This earlier result suggested partial transfer, but the subset was small and line-level.

## 2. New page-level Ottoman Turkish sanity benchmark

A stronger page-level real-OCR sanity benchmark was later constructed from an Ottoman Turkish printed source in Arabic script. This source is a related Arabic-script Turkic test case and should not be presented as Old Tatar or Old Bashkir.

Filtered evaluation subset:

- 68 page-level examples;
- 90,457 clean/reference characters;
- 81,593 OCR characters;
- Tesseract OCR with the Arabic model (`tesseract_ara_psm6`).

| System | N | Mean CER | Median CER | Mean WER | Median WER | Mean NoSpaceCER |
|---|---:|---:|---:|---:|---:|---:|
| raw_tesseract | 68 | 0.3539 | 0.2983 | 0.9238 | 0.8943 | 0.3421 |
| byt5_chunked | 68 | 0.4564 | 0.4206 | 0.8919 | 0.8579 | 0.4658 |
| strict_guarded_byt5 | 68 | 0.3828 | 0.3442 | 0.9039 | 0.8605 | 0.3830 |

Page-level CER behavior:

| System | Improved | Same | Worse |
|---|---:|---:|---:|
| byt5_chunked | 6 | 0 | 62 |
| strict_guarded_byt5 | 33 | 3 | 32 |

## Interpretation

The page-level experiment changes the main interpretation. The synthetic-trained model does not robustly transfer to full-page real OCR. It improves WER slightly but worsens CER and NoSpaceCER. The strict fallback reduces the damage but still does not beat raw Tesseract on average by CER.

This is a useful negative/mixed transfer finding: synthetic OCR-like noise is not enough to model real page-level OCR errors for Ottoman Turkish Arabic-script text. Future work should build aligned real OCR/reference chunks and fine-tune on real-domain errors.
