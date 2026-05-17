# Course paper outline

## Working title

Artificial intelligence methods for recognition and analysis of historical Arabic-script Turkic texts

Russian title:

Методы искусственного интеллекта для распознавания и анализа исторических текстов на арабско-тюркской графике

## Core idea

The course paper presents a reproducible pilot pipeline for OCR post-correction of historical Turkic texts written in Arabic script.

The current implementation focuses on a controlled post-correction benchmark:

1. collect clean Arabic-script Turkic text;
2. generate synthetic OCR-like corruptions;
3. build leakage-free train/valid/test splits;
4. compare identity and rule-based baselines;
5. fine-tune ByT5-small for neural post-correction;
6. evaluate with CER, WER, ExactMatch;
7. analyze per-sample improvements and failures.

This pilot is intended as a first technical component of a larger thesis project on recognition and computational analysis of Arabic-script Turkic historical documents.

## Research problem

Historical Turkic texts written in Arabic script are difficult to process automatically because of:

- orthographic variation;
- old print and manuscript quality;
- limited availability of annotated data;
- script-specific ambiguities;
- OCR errors;
- lack of ready-made models and benchmarks for low-resource Arabic-script Turkic materials.

The project investigates whether neural OCR post-correction can improve noisy Arabic-script Turkic text in a low-resource setting.

## Object and subject

### Object

Historical Turkic texts written in Arabic script.

### Subject

Methods of automatic OCR post-correction and text normalization for Arabic-script Turkic historical materials.

## Goal

To design and evaluate a pilot AI-based pipeline for OCR post-correction of historical Arabic-script Turkic texts.

## Tasks

1. Review the problem of processing historical Arabic-script Turkic texts.
2. Select and collect a small topic-aligned Arabic-script Turkic corpus.
3. Build a synthetic OCR post-correction dataset.
4. Ensure train/valid/test separation without clean-line leakage.
5. Implement baseline methods for post-correction.
6. Fine-tune a byte-level sequence-to-sequence model.
7. Evaluate models using CER, WER, and ExactMatch.
8. Analyze qualitative and quantitative error patterns.
9. Formulate limitations and future directions for a larger benchmark, thesis, and article.

## Research questions

1. Can neural post-correction improve synthetic OCR-like errors in Arabic-script Turkic text?
2. Is simple rule-based normalization sufficient for this material?
3. How important is sequence length for byte-level models such as ByT5?
4. Does the neural model improve most samples, or only the aggregate score?

## Hypotheses

### H1

Naive rule-based normalization may be harmful for Arabic-script Turkic historical text because it can distort meaningful orthographic features.

### H2

A byte-level sequence-to-sequence model can improve OCR-like corrupted Arabic-script Turkic text over the identity baseline.

### H3

For Arabic-script text, increasing ByT5 sequence length from 256 to 512 is important because byte-level tokenization can otherwise truncate source or target sequences.

## Proposed structure

## 1. Introduction

### 1.1 Relevance

Historical Arabic-script Turkic texts are valuable for cultural, linguistic, and historical research, but they remain difficult to process automatically. Recognition and correction tools for such materials are less mature than for modern high-resource languages.

### 1.2 Problem statement

The main technical difficulty is the lack of robust OCR and post-correction pipelines for low-resource Arabic-script Turkic materials.

### 1.3 Goal and tasks

State the goal and tasks listed above.

### 1.4 Contribution

The course paper contributes:

- a small Arabic-script Turkic post-correction corpus;
- a synthetic OCR-noise benchmark;
- baseline and neural post-correction experiments;
- an error analysis of ByT5-small results;
- a reproducible repository that can be expanded for thesis and article work.

## 2. Background and related work

### 2.1 OCR and HTR for historical documents

Discuss OCR/HTR difficulties: noise, old orthography, font variation, layout, degradation.

### 2.2 Arabic-script historical text processing

Discuss script-specific issues: connected writing, diacritics, orthographic variants, mixed Arabic/Persian/Turkic conventions.

### 2.3 Turkic texts in Arabic script

Explain why Ottoman/Tatar/other Turkic Arabic-script texts are computationally challenging and underrepresented.

### 2.4 OCR post-correction

Describe post-correction as a sequence-to-sequence task: noisy text to clean text.

### 2.5 Byte-level models and ByT5

Explain why ByT5 is relevant: byte-level input, no need for language-specific tokenizer, useful for noisy and low-resource text.

## 3. Data

### 3.1 Source corpus

Current pilot corpus:

- source: Ottoman Turkish Arabic-script Wikisource text;
- text: `أوقرانيا، روسيه وتوركيه (مقالەلر مجموعەسى)`;
- page range: 5–71;
- clean text blocks: 400.

### 3.2 Dataset construction

Clean text lines are transformed into synthetic noisy variants using OCR-like corruptions.

### 3.3 Splits

| Split | Rows | Unique clean lines |
|---|---:|---:|
| train | 6400 | 320 |
| valid | 800 | 40 |
| test | 800 | 40 |

### 3.4 Leakage control

The split is performed by clean source lines. Variants of the same clean line do not appear across train, valid, and test.

| Overlap | Count |
|---|---:|
| train ∩ valid clean lines | 0 |
| train ∩ test clean lines | 0 |
| valid ∩ test clean lines | 0 |

## 4. Methodology

### 4.1 Task formulation

Input: noisy Arabic-script Turkic text.

Output: corrected clean text.

This is treated as a text-to-text post-correction problem.

### 4.2 Baselines

1. Identity baseline: returns noisy input unchanged.
2. Rule-based normalizer: applies simple Arabic-script normalization.

### 4.3 Neural model

Model: ByT5-small.

Experiments:

- ByT5-small with sequence length 256;
- ByT5-small with sequence length 512.

The final model uses:

- max source length: 512;
- max target length: 512;
- epochs: 2.

### 4.4 Metrics

- CER: Character Error Rate;
- WER: Word Error Rate;
- ExactMatch: share of exactly restored lines.

## 5. Results

### 5.1 Final metrics

| Method | CER | WER | ExactMatch | N |
|---|---:|---:|---:|---:|
| Identity baseline | 0.086005 | 0.519006 | 0.001250 | 800 |
| Rule-based normalizer | 0.151932 | 0.684408 | 0.000000 | 800 |
| ByT5-small 512 / 2 epochs | 0.079913 | 0.368540 | 0.003750 | 800 |

### 5.2 Interpretation

The rule-based normalizer performs worse than the identity baseline.

ByT5-small 512 improves over the identity baseline:

- CER: 0.086005 → 0.079913;
- WER: 0.519006 → 0.368540.

The improvement is moderate on character level and stronger on word level.

### 5.3 Sequence length effect

The 512-token setting is better suited for Arabic-script text because ByT5 uses byte-level tokenization. A visible Arabic-script character may require multiple bytes, so 256-token limits can truncate long examples.

## 6. Error analysis

### 6.1 Aggregate per-sample analysis

| Criterion | Improved | Unchanged | Worse | Total |
|---|---:|---:|---:|---:|
| CER | 682 | 60 | 58 | 800 |
| WER | 677 | 63 | 60 | 800 |

Mean per-sample improvements:

- CER improvement: 0.006092;
- WER improvement: 0.150467.

### 6.2 Interpretation

The model improves most test lines, so the result is not caused by only a few outliers. However, the model worsens some examples, so it is not uniformly safe.

### 6.3 Qualitative examples

Use examples from:

- `outputs/postcorrection/error_analysis/byt5_512_best_examples.csv`;
- `outputs/postcorrection/error_analysis/byt5_512_worst_examples.csv`.

## 7. Limitations

Current limitations:

- small corpus: 400 clean text blocks;
- one main source;
- synthetic OCR noise instead of real OCR output;
- no manual linguistic validation yet;
- no comparison with larger models yet;
- no full OCR from images in this pilot stage.

## 8. Future work

### 8.1 For the course paper

- finalize text;
- add examples and tables;
- add related work;
- prepare final PDF.

### 8.2 For the thesis

- expand corpus;
- add real OCR/HTR outputs;
- compare multiple models;
- add named entity recognition or historical text analysis;
- connect post-correction to a larger pipeline for historical document processing.

### 8.3 For a future article

Possible article framing:

A pilot benchmark for OCR post-correction of historical Arabic-script Turkic texts.

Needed improvements:

- more sources;
- clearer benchmark protocol;
- manual validation subset;
- model comparison;
- public dataset card;
- stronger discussion of linguistic and historical relevance.

## 9. Conclusion

The pilot demonstrates that neural OCR post-correction with a byte-level sequence-to-sequence model can improve synthetic OCR-like errors in historical Arabic-script Turkic text. The ByT5-small 512-token model outperforms the identity baseline on both CER and WER and improves the majority of test samples.

At the same time, the experiment remains a pilot: the corpus is small, the noise is synthetic, and the results require further validation on larger and more diverse historical materials.

## Immediate writing plan

### Day 1

- polish introduction;
- write goal/tasks/object/subject;
- insert dataset description.

### Day 2

- write methodology;
- describe baselines and ByT5.

### Day 3

- write results and error analysis;
- insert tables.

### Day 4

- write related work draft.

### Day 5

- write limitations and conclusion.

### Day 6+

- polish, format, references, final PDF.
