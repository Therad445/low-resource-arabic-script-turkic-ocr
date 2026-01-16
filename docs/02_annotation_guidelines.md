# Annotation guidelines (v0)

Goal: produce consistent line-level transcriptions for OCR/HTR training and evaluation.

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
- If diacritics are clearly printed, keep them.
- If diacritics are absent in the source, do not add.

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
