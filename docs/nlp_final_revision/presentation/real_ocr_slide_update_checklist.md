# Real-OCR slide update checklist

Use this deck instead of older slides that claimed partial real-OCR transfer on 90 line-level samples.

## Must say

- The project is framed as Arabic-script Turkic OCR post-correction.
- Old Tatar and Old Bashkir are the motivating future target domains.
- The current real-OCR benchmark is Ottoman Turkish in Arabic script.
- The real-OCR benchmark has 72 pages and 68 filtered evaluation pages.
- Raw Tesseract mean CER is 0.3539.
- ByT5 chunked mean CER is 0.4564, so it is worse by CER.
- Strict guarded ByT5 mean CER is 0.3828: safer, but still worse than raw Tesseract.
- Main conclusion: synthetic-to-real gap; real-domain adaptation is needed.

## Avoid saying

- “The model is ready for practical OCR correction.”
- “We built an Old Tatar/Bashkir dataset.”
- “ByT5 reliably improves real OCR.”
- “The result proves robustness.”

## Safe final sentence

The work provides a reproducible pilot pipeline and a useful negative/mixed transfer result: synthetic training helps in the controlled benchmark, but real page-level OCR requires aligned real OCR/reference data and domain adaptation.
