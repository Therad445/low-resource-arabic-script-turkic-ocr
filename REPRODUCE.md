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
python3 scripts/collect_wikisource_ottoman_ukraine.py   --start 5   --end 71   --out data/postcorrection/raw/arabic_turkic_clean_text.txt   --sources data/postcorrection/raw/SOURCES.md
```

## 3. Synthetic Dataset Construction

```bash
python3 -m src.postcorrection.make_dataset   --input data/postcorrection/raw/arabic_turkic_clean_text.txt   --out_dir data/postcorrection/processed   --variants 20   --seed 42
```

## 4. Baseline Evaluation

```bash
python3 -m src.postcorrection.run_baselines   --test data/postcorrection/processed/test.csv   --out outputs/postcorrection/baseline_predictions.csv   --metrics outputs/postcorrection/baseline_metrics.csv
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
python3 scripts/postcorrection_error_analysis.py   --predictions outputs/postcorrection/byt5_arabic_turkic_512_2ep_predictions.csv   --out_dir outputs/postcorrection/error_analysis
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

## 8. Earlier Line-Level Real-OCR Post-Correction Evaluation

A trained ByT5 checkpoint is required for this step.

```bash
python3 scripts/evaluate_real_ocr_postcorrection.py   --model-path /path/to/byt5-arabic-turkic-512-2ep   --input data/postcorrection/real_sanity/real_ocr_sanity.csv   --predictions-out docs/nlp_final_revision/tables/real_ocr_postcorrection_predictions.csv   --metrics-out docs/nlp_final_revision/tables/real_ocr_postcorrection_metrics.csv   --num-beams 1   --max-length 512
```

Earlier line-level sanity result:

| Method | CER | WER | NoSpaceCER | N |
|---|---:|---:|---:|---:|
| Real OCR identity (`tesseract_ara_psm6`) | 0.4508 | 1.0888 | 0.4468 | 90 |
| Synthetic-trained ByT5 on real OCR | 0.4361 | 0.9660 | 0.4454 | 90 |

## 9. Page-Level Ottoman Turkish Real-OCR Dataset Preparation

The page-level real-OCR workspace is local-only and should not be committed:

```text
data/real_ocr_dataset_v1/quarantine/WIKI_UKR_RUS_TUR/
```

The source is an Ottoman Turkish printed text in Arabic script. It is a related Arabic-script Turkic source, not an Old Tatar or Old Bashkir dataset.

Typical local workflow:

```bash
# Build or update manifest with local rendered page images.
python3 scripts/build_page_level_real_ocr_dataset.py   --manifest data/real_ocr_dataset_v1/quarantine/WIKI_UKR_RUS_TUR/wikisource_pages_with_images_manifest.csv   --ocr-dir data/real_ocr_dataset_v1/quarantine/WIKI_UKR_RUS_TUR/ocr/tesseract_ara_psm6   --out data/real_ocr_dataset_v1/quarantine/WIKI_UKR_RUS_TUR/exports/page_level_real_ocr_ukr_rus_tur_v1.csv
```

Filter short or empty pages locally before model evaluation. The current filtered eval subset contains 68 pages, 90,457 clean characters and 81,593 OCR characters.

## 10. Page-Level Chunked ByT5 Transfer Evaluation

A trained ByT5 checkpoint and a local filtered page-level CSV are required.

```bash
python3 scripts/evaluate_real_ocr_postcorrection_chunked.py   --model-path /path/to/byt5-arabic-turkic-512-2ep   --input /path/to/page_level_real_ocr_ukr_rus_tur_v1_eval.csv   --predictions-out outputs/real_ocr_ukr_rus_tur/byt5_chunked_predictions.csv   --metrics-out outputs/real_ocr_ukr_rus_tur/byt5_chunked_metrics.csv   --num-beams 1   --batch-size 4
```

Current page-level result summary:

| System | N | Mean CER | Median CER | Mean WER | Median WER | Mean NoSpaceCER |
|---|---:|---:|---:|---:|---:|---:|
| raw_tesseract | 68 | 0.3539 | 0.2983 | 0.9238 | 0.8943 | 0.3421 |
| byt5_chunked | 68 | 0.4564 | 0.4206 | 0.8919 | 0.8579 | 0.4658 |
| strict_guarded_byt5 | 68 | 0.3828 | 0.3442 | 0.9039 | 0.8605 | 0.3830 |

Only the summary table is safe to commit. Do not commit raw predictions or source-derived text outputs.

## 11. Main Result Files

```text
outputs/postcorrection/final_metrics.csv
outputs/postcorrection/error_analysis/byt5_512_error_summary.csv
outputs/postcorrection/error_analysis/byt5_512_best_examples.csv
outputs/postcorrection/error_analysis/byt5_512_worst_examples.csv
docs/nlp_final_revision/tables/real_ocr_postcorrection_metrics.csv
docs/nlp_final_revision/analysis/real_ocr_postcorrection.md
docs/nlp_final_revision/tables/real_ocr_ukr_rus_tur_chunked_summary.csv
docs/nlp_final_revision/analysis/real_ocr_ukr_rus_tur_chunked_transfer.md
```

## 12. Course Paper Artifacts

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

pandoc docs/course_paper_hse_export.md   --from markdown+yaml_metadata_block+raw_tex   --to docx   --reference-doc=/tmp/hse_reference.docx   --resource-path=.:docs:outputs:report   -o outputs/course_paper_hse_final.docx
```

## 13. Defense Slides

Defense slides and speaker notes are stored in:

```text
slides/course_paper_defense_mtc_style_10slides_beautiful_v2.pptx
slides/course_paper_defense_mtc_style_10slides_beautiful_v2.pdf
slides/course_paper_defense_mtc_style_10slides_speaker_notes.md
```

The slides should be updated to reflect the new page-level real-OCR result and the synthetic-to-real transfer gap.

## 14. Report

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
