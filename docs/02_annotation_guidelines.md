# Annotation guidelines (v1)

Goal: produce consistent line-level transcriptions for OCR training and evaluation on historical Turkic texts in Arabic script.

## 1. Annotation unit

The primary annotation unit is a **single visual text line** aligned with a line crop image.

Annotate one line per row.

## 2. General principle

Transcribe what is visibly present in the source.

Do not modernize spelling.  
Do not silently repair damaged text.  
Do not invent punctuation or letters that are not visible.

## 3. Normalization policy

### Diplomatic transcription
`transcription_diplomatic` should preserve the visible line as faithfully as practical.

### Normalized transcription
`transcription_normalized` may be identical to diplomatic transcription in Sprint 2.
Later it can be used for downstream experiments.

### Repository normalization v1
For metric stability, project-level normalization is conservative:

1. Unicode normalization: NFC
2. Collapse repeated whitespace to a single ASCII space
3. Trim leading/trailing spaces
4. Remove invisible formatting marks:
   - U+200C, U+200D, U+200E, U+200F
   - U+202A..U+202E
   - U+2066..U+2069

## 4. Spelling policy

- Preserve original orthography.
- Do not convert to modern Tatar/Bashkir.
- Do not transliterate to Cyrillic or Latin in this field.

## 5. Spaces

- Preserve visible spaces between words.
- If spacing is unclear but a separation is strongly visible, use one ASCII space.
- Do not insert decorative spacing for visual alignment.

## 6. Punctuation

- Preserve punctuation marks when clearly visible.
- If punctuation is ambiguous, omit rather than hallucinate.
- Decorative separators that are not part of the text should be omitted and noted in `notes` if needed.

## 7. Numbers

- Preserve digits exactly as printed.
- Do not convert Arabic-Indic digits to Western digits.
- Do not spell out numbers.

## 8. Diacritics and dots

- Dots that distinguish letters are part of the letter and must be reflected through the correct character choice.
- Optional vocalization marks / harakat:
  - if consistently printed and clearly legible, keep them;
  - if inconsistent or unclear in this phase, omit them consistently.
- Do not add diacritics that are absent.

## 9. Unclear or damaged text

### Single unclear glyph
Use:
`�`

Example:
`كت�ب`

### Multiple unclear glyphs
Use one replacement character per unknown glyph when count is visually estimable.

Example:
`س��م`

### Large unreadable span
If a span cannot be reliably counted, use the best readable context and explain in `notes`.

Avoid guessing.

## 10. Hyphenation / line breaks

- Treat each visual line independently.
- Do not merge with the next line.
- If a word is broken across lines in print, transcribe only what is visible in the current line.

## 11. Non-text elements

Omit:
- page ornaments
- decorative frames
- non-text flourishes
- stains and paper defects

If a non-text mark interferes with reading, mention it in `notes`.

## 12. Mixed-language content

If Arabic / Persian / Turkic material appears in the same line, transcribe what is visible without language switching in the annotation format.

If language identity matters, record it later in metadata, not inside transcription.

## 13. Review status

Use:

- `draft` — first pass, not yet checked
- `reviewed` — checked once against image
- `frozen` — accepted for benchmark/pilot use

## 14. Quality flag

Use one of:

- `ok`
- `needs_review`
- `illegible`
- `partial`
- `damaged`

## 15. Annotator behavior

Before marking a line as `reviewed`:
- reread against the image,
- confirm spaces,
- confirm unclear glyph handling,
- confirm that no modernization slipped in.

## 16. Examples

### Good
Visible line:
`السلام عليكم`

Diplomatic:
`السلام عليكم`

### Good with damage
Visible line:
`الحمـد لله` with one unreadable glyph

Diplomatic:
`الحم� لله`

### Bad
- modernized spelling
- guessed punctuation
- omitted visible word
- merged two lines into one transcription

## 17. Sprint 2 policy

For Sprint 2:
- printed sources only,
- line-level only,
- diplomatic transcription required,
- normalized transcription may equal diplomatic transcription.