# Stage 2 related work update checklist

This package changes only:

- docs/course_paper_final.md
- docs/course_paper_hse_export.md

It replaces Section 2 and appends references 15–22.

## What to check after running

1. The section still says that the work is post-correction, not full OCR/HTR.
2. Ottoman Turkish is presented as a related Arabic-script Turkic test case, not as Old Tatar/Bashkir.
3. Synthetic data is presented as a valid pilot strategy, but not as a replacement for real OCR validation.
4. Kanerva et al. 2025 supports the "no universal transfer" interpretation.
5. Naiman 2023, Guan & Greene 2024, RoundTripOCR 2024 support the synthetic-data / low-resource framing.
6. Lyu 2021 and Rijhwani 2021 support historical/low-resource OCR post-correction framing.

## Suggested commit

docs: expand related work with modern OCR correction sources
