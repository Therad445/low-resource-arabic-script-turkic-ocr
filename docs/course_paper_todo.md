# Course paper TODO

This checklist tracks only the remaining finalization steps for the course paper.
Most drafting, polishing, source grounding, methodology, results, limitations, and conclusion work has already been completed.

## 1. Repository and artifact consistency

- [ ] Check that all files mentioned in `docs/course_paper_draft.md` exist in the repository.
- [ ] Check that `docs/postcorrection_pilot.md` is consistent with `docs/course_paper_draft.md`.
- [ ] Check that README commands for corpus collection, dataset generation, baseline evaluation, and error analysis still work or are clearly documented.
- [ ] Check that large model artifacts are not stored in git.

## 2. Metrics and result verification

- [ ] Re-check the final metric values against the stored CSV artifacts.
- [ ] Re-check the train/valid/test split counts.
- [ ] Re-check the improved/unchanged/worse error-analysis counts.
- [ ] If time permits, add 2–3 qualitative examples from best/worst predictions to the course paper or appendix.

## 3. References and academic formatting

- [ ] Ensure that every cited work from section 2 appears in `docs/course_paper_references.md`.
- [ ] Format the bibliography according to the required university style.
- [ ] Check whether inline citations should stay in author-year style or be converted to the required format.

## 4. Submission packaging

- [ ] Add title page if required.
- [ ] Add table of contents if required.
- [ ] Convert Markdown to DOCX or PDF.
- [ ] Check page numbering, table formatting, headings, and bibliography formatting.

## 5. Final human reading

- [ ] Read the abstract, introduction, section conclusions, and final conclusion aloud.
- [ ] Check that the work is presented as a pilot post-correction study, not as a finished OCR/HTR system.
- [ ] Check that all strong claims are supported by metrics or explicitly limited as pilot findings.

## Critical sanity checks after synthetic benchmark criticism

- [ ] Проверить, какая часть WER improvement связана с ошибками пробелов и границ слов.
- [ ] Посчитать no-space CER для noisy input и ByT5 prediction.
- [ ] Разделить test examples на группы `word_count(noisy) == word_count(clean)` и `word_count(noisy) != word_count(clean)` и сравнить CER/WER improvement.
- [ ] Проверить robustness на alternative synthetic noise: другие вероятности шума, меньше whitespace noise, больше substitution/deletion noise.
- [ ] Добавить небольшой real-OCR/HTR sanity check, если появятся реальные OCR-выходы и ручной clean reference.
- [ ] Не интерпретировать WER improvement как доказательство качества на real OCR без отдельной проверки.
