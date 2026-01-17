# Annotation guidelines (v0)

Goal: produce consistent line-level transcriptions for OCR/HTR training and evaluation.

## Text normalization policy (v1) — FIXED

Goal: make CER/WER comparable across experiments.

1) Unicode normalization: NFC.
2) Whitespace:
   - Replace any sequence of whitespace with a single ASCII space.
   - Trim leading/trailing spaces.
3) Remove invisible formatting marks if present:
   - U+200C (ZWNJ), U+200D (ZWJ), U+200E (LRM), U+200F (RLM),
     U+202A..U+202E (embedding/override marks), U+2066..U+2069 (isolate marks).
4) Diacritics/harakat (Phase A / printed):
   - Do NOT add diacritics if absent.
   - If diacritics are inconsistently printed, omit them in transcription (v1).
5) Unknown/unclear character:
   - Use the replacement character `�` for a single unknown glyph.
6) No modernization:
   - Preserve original spelling/orthography; do not convert to modern Tatar/Bashkir.


## Unit of annotation
- Prefer **line-level** transcription aligned with a line crop image.

## Text normalization policy
- Preserve original spelling as written in the source.
- Do not modernize orthography unless explicitly stated.

## Spaces and punctuation
- Keep spaces as in the printed line when visible.
- Preserve punctuation marks as seen.
- If punctuation is unclear, omit rather than hallucinate.

## Diacritics / dots
- Dots that differentiate letters are part of the letter and must be kept.
- Optional vocalization diacritics (harakat) are omitted in v1 if not consistently printed.

## Numbers
- Preserve numbers as printed.
- If Arabic-Indic digits appear, transcribe them as-is (do not convert) unless project policy changes.

## Unclear characters
- Use a placeholder token: `�` for unknown character.
- Avoid guessing.

## Quality control
- Double-check a random 5–10% sample.
- Maintain an "edge cases" section below.

## Edge cases log
- (Fill in as you annotate)
