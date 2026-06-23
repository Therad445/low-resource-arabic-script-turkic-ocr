# Reproduction Guide

This document describes how to reproduce the main artifacts of the OCR post-correction pilot project.

## 1. Environment

Install post-correction dependencies:

```bash
python3 -m pip install -r requirements-postcorrection.txt
```

Development dependencies are listed in:

```text
requirements-dev.txt
```

Model weights are not stored in git. Real-OCR ByT5 evaluation requires an external trained model checkpoint passed with `--model-path`.

## 2. Corpus Collection

```bash
python3 scripts/collect_wikisource_ottoman_ukraine.py \
  --start 5 \
  --end 71 \
  --out data/postcorrection/raw/arabic_turkic_clean_text.txt \
  --sources data/postcorrection/raw/SOURCES.md
```

## 3. Synthetic Dataset Construction

```bash
python3 -m src.postcorrection.make_dataset \
  --input data/postcorrection/raw/arabic_turkic_clean_text.txt \
  --out_dir data/postcorrection/processed \
  --variants 20 \
  --seed 42
```

## 4. Baseline Evaluation

```bash
python3 -m src.postcorrection.run_baselines \
  --test data/postcorrection/processed/test.csv \
  --out outputs/postcorrection/baseline_predictions.csv \
  --metrics outputs/postcorrection/baseline_metrics.csv
```

## 5. ByT5 Evaluation Artifacts

The current repository stores prediction and metric artifacts for the ByT5-small 512-token synthetic benchmark experiment:

```text
outputs/postcorrection/byt5_arabic_turkic_512_2ep_predictions.csv
outputs/postcorrection/byt5_arabic_turkic_512_2ep_metrics.csv
outputs/postcorrection/byt5_arabic_turkic_512_2ep_examples.csv
```

Model weights are not stored in git.

## 6. Error Analysis

```bash
python3 scripts/postcorrection_error_analysis.py \
  --predictions outputs/postcorrection/byt5_arabic_turkic_512_2ep_predictions.csv \
  --out_dir outputs/postcorrection/error_analysis
```

## 7. Whitespace Sanity Check

```bash
python3 scripts/postcorrection_whitespace_sanity.py
```

Key output files:

```text
docs/nlp_final_revision/analysis/whitespace_sanity.md
docs/nlp_final_revision/tables/wer_vs_no_space_cer_dependency.csv
docs/nlp_final_revision/tables/whitespace_sanity_summary_by_word_count_group.csv
```

## 8. Real-OCR Post-Correction Evaluation

A trained ByT5 checkpoint is required for this step.

Example command:

```bash
python3 scripts/evaluate_real_ocr_postcorrection.py \
  --model-path /path/to/byt5-arabic-turkic-512-2ep \
  --input data/postcorrection/real_sanity/real_ocr_sanity.csv \
  --output-dir docs/nlp_final_revision/tables \
  --num-beams 1
```

Real-OCR output files currently stored in the repository:

```text
data/postcorrection/real_sanity/real_ocr_sanity.csv
docs/nlp_final_revision/tables/real_ocr_postcorrection_metrics.csv
docs/nlp_final_revision/tables/real_ocr_postcorrection_predictions.csv
docs/nlp_final_revision/analysis/real_ocr_postcorrection.md
```

Current real-OCR sanity result:

| Method | CER | WER | NoSpaceCER | N |
|---|---:|---:|---:|---:|
| Real OCR identity (`tesseract_ara_psm6`) | 0.4508 | 1.0888 | 0.4468 | 90 |
| Synthetic-trained ByT5 on real OCR | 0.4361 | 0.9660 | 0.4454 | 90 |

## 9. Main Result Files

```text
outputs/postcorrection/final_metrics.csv
outputs/postcorrection/error_analysis/byt5_512_error_summary.csv
outputs/postcorrection/error_analysis/byt5_512_best_examples.csv
outputs/postcorrection/error_analysis/byt5_512_worst_examples.csv
docs/nlp_final_revision/tables/real_ocr_postcorrection_metrics.csv
docs/nlp_final_revision/tables/real_ocr_postcorrection_predictions.csv
```

## 10. Course Paper Artifacts

Main course-paper sources and export:

```text
docs/course_paper_final.md
docs/course_paper_hse_export.md
outputs/course_paper_hse_final.docx
```

The DOCX file is rebuilt from `docs/course_paper_hse_export.md`.

A typical rebuild command is:

```bash
cp outputs/course_paper_hse_final.docx /tmp/hse_reference.docx

pandoc docs/course_paper_hse_export.md \
  --from markdown+yaml_metadata_block+raw_tex \
  --to docx \
  --reference-doc=/tmp/hse_reference.docx \
  --resource-path=.:docs:outputs:report \
  -o outputs/course_paper_hse_final.docx
```

## 11. Defense Slides

Defense slides and speaker notes are stored in:

```text
slides/course_paper_defense_mtc_style_10slides_beautiful_v2.pptx
slides/course_paper_defense_mtc_style_10slides_beautiful_v2.pdf
slides/course_paper_defense_mtc_style_10slides_speaker_notes.md
```

The PDF is included as a fallback for online defense.

## 12. Report

The older LaTeX report is located in:

```text
report/main.tex
report/lit.bib
report/final_report.pdf
```

Generated LaTeX tables are located in:

```text
report/tables/
```
