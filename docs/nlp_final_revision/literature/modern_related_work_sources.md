# Stage 1: карта современных источников для усиления related work

Цель этого этапа: не переписывать курсовую сразу, а сначала зафиксировать, какие источники действительно нужны, какую мысль они усиливают и куда их вставлять.

## Как читать карту

- **Priority A** — почти точно добавлять в курсовую.
- **Priority B** — полезно добавить, если не перегрузит related work.
- **Priority C** — держать как резерв / использовать в future work или README, но не обязательно в основном тексте.

---

## 1. Historical OCR / workflow / ground truth

### 1.1 Reul et al. 2019 — OCR4all
**Priority:** уже есть, оставить и использовать активнее.  
**Current role:** historical OCR workflow, reproducibility, semi-automatic OCR processing for historical printings.  
**Where to cite:** 2.1, 6.4.  
**Use in text:** показать, что OCR исторических источников — это не только модель распознавания, а workflow: preprocessing, layout/segmentation, ground truth, OCR, correction, validation.  
**Reference line:** Reul C. et al. OCR4all -- An Open-Source Tool Providing a (Semi-)Automatic OCR Workflow for Historical Printings. 2019. arXiv:1909.04032.

### 1.2 Springmann et al. 2018 — GT4HistOCR
**Priority:** уже есть, оставить.  
**Current role:** ground truth для исторического OCR.  
**Where to cite:** 2.1, 3.3, 6.4.  
**Use in text:** обосновать, что без выровненного ground truth нельзя честно оценивать OCR/HTR и post-correction.  
**Reference line:** Springmann U. et al. Ground Truth for training OCR engines on historical documents in German Fraktur and Early Modern Latin. 2018. arXiv:1809.05501.

---

## 2. Arabic-script OCR / line segmentation / OCR tooling

### 2.1 Kasem et al. 2023 — Arabic OCR survey
**Priority:** уже есть, оставить.  
**Current role:** обзор проблем Arabic OCR.  
**Where to cite:** 2.2.  
**Use in text:** позиционные формы букв, связное письмо, точки, похожие графемы, сложность переноса OCR-подходов с латиницы.  
**Reference line:** Kasem M. S. et al. Advancements and Challenges in Arabic Optical Character Recognition: A Comprehensive Survey. 2023. arXiv:2312.11812.

### 2.2 Osman et al. 2020 — multi-font OCR for Arabic script
**Priority:** уже есть, оставить.  
**Current role:** многошрифтовость и language-independent OCR для арабской графики.  
**Where to cite:** 2.2.  
**Use in text:** печатные арабографичные материалы зависят от шрифта, начертания и близости графем.  
**Reference line:** Osman H. et al. An Efficient Language-Independent Multi-Font OCR for Arabic Script. 2020. arXiv:2009.09115.

### 2.3 eScriptorium / Kraken
**Priority:** A, добавить в related work аккуратно, но лучше не как arXiv-исследование, а как tool/workflow context.  
**Where to cite:** 2.1 или 6.4.  
**Use in text:** open-source workflow для segmentation/text recognition исторических рукописей и печатных источников; Kraken/eScriptorium поддерживает RTL scripts вроде Arabic/Hebrew; это напрямую связано с будущим этапом image → line crop → OCR/HTR → reference.  
**Risk:** не делать его центральным научным источником, потому что это скорее software/workflow reference.  
**Reference line:** eScriptorium documentation / Kraken project, use as software-workflow source rather than core theoretical reference.

---

## 3. Ottoman Turkish / Arabic-script Turkic material

### 3.1 Kirmizialtin & Wrisley 2020 — Ottoman Turkish print archive
**Priority:** уже есть, сделать центральным для объяснения Ottoman Turkish benchmark.  
**Where to cite:** 2.3, 5.12, 6.4.  
**Use in text:** Ottoman Turkish is relevant as Arabic-script Turkic printed material and as a non-Latin script archive digitization case, but it must not be presented as Old Tatar/Bashkir.  
**Reference line:** Kirmizialtin S., Wrisley D. Automated Transcription of Non-Latin Script Periodicals: A Case Study in the Ottoman Turkish Print Archive. 2020. arXiv:2011.01139.

### 3.2 Özateş et al. 2025 — Historical Turkish NLP
**Priority:** уже есть, оставить.  
**Where to cite:** 2.3.  
**Use in text:** modern resource-building for Historical Turkish NLP; supports the claim that historical Turkic/Ottoman material is under-resourced and needs corpora/models/tools.  
**Reference line:** Özateş Ş. B. et al. Building Foundations for Natural Language Processing of Historical Turkish: Resources and Models. 2025. arXiv:2501.04828.

---

## 4. Post-OCR correction

### 4.1 Hämäläinen & Hengchen 2019 — automatic NMT post-correction
**Priority:** уже есть, оставить.  
**Where to cite:** 2.4.  
**Use in text:** historical OCR correction can be framed as neural translation / seq2seq correction.  
**Reference line:** Hämäläinen M., Hengchen S. From the Paft to the Fiiture: a Fully Automatic NMT and Word Embeddings Method for OCR Post-Correction. 2019. arXiv:1910.05535.

### 4.2 Ramirez-Orta et al. 2021 — char seq2seq ensembles
**Priority:** уже есть, оставить и использовать активнее.  
**Where to cite:** 2.4, 4.2, 5.12.  
**Use in text:** character-level seq2seq models, long-string correction, post-OCR correction as sequence transformation. Особенно полезно рядом с твоим chunking page-level real OCR experiment.  
**Reference line:** Ramirez-Orta J. et al. Post-OCR Document Correction with large Ensembles of Character Sequence-to-Sequence Models. 2021. arXiv:2109.06264.

### 4.3 Lyu et al. 2021 — Neural OCR post-hoc correction of historical corpora
**Priority:** A, добавить.  
**Where to cite:** 2.4.  
**Use in text:** historical OCR errors come from orthographic variation, typefaces, scan quality, word segmentation and language evolution; correction should preserve input-output similarity and operate at character level.  
**Why useful:** очень близко к твоей аргументации про CER, NoSpaceCER and historical spelling.  
**Reference line:** Lyu L., Koutraki M., Krickl M., Fetahu B. Neural OCR Post-Hoc Correction of Historical Corpora. 2021. arXiv:2102.00583.

### 4.4 Rijhwani et al. 2021 — low-resource / endangered languages post-correction
**Priority:** A/B, добавить если related work не перегружается.  
**Where to cite:** 2.4 or 2.5.  
**Use in text:** neural post-correction for less-well-resourced languages depends on scarce manually curated correction data; self-training and lexical constraints can help.  
**Why useful:** напрямую поддерживает low-resource framing.  
**Reference line:** Rijhwani S., Rosenblum D., Anastasopoulos A., Neubig G. Lexically Aware Semi-Supervised Learning for OCR Post-Correction. 2021. arXiv:2111.02622.

### 4.5 Kanerva et al. 2025 — LLM post-correction: No Free Lunches
**Priority:** A, добавить обязательно.  
**Where to cite:** 2.4, 5.12, 6.5.  
**Use in text:** даже современные LLMs не дают универсального выигрыша; эффект зависит от языка, setup, segment length and prompt/correction strategy. Это защищает твой negative result как нормальный научный результат.  
**Reference line:** Kanerva J., Ledins C., Käpyaho S., Ginter F. OCR Error Post-Correction with LLMs in Historical Documents: No Free Lunches. 2025. arXiv:2502.01205.

### 4.6 Bourne 2024 — CLOCR-C
**Priority:** B.  
**Where to cite:** 2.4 or future work.  
**Use in text:** pretrained LMs can leverage broader context for OCR correction, but performance depends on prompts/context and can be sensitive to misleading context.  
**Reference line:** Bourne J. CLOCR-C: Context Leveraging OCR Correction with Pre-trained Language Models. 2024. arXiv:2408.17428.

---

## 5. Synthetic data for post-OCR correction

### 5.1 Suissa et al. 2023 — historical Hebrew OCR correction
**Priority:** уже есть, оставить.  
**Where to cite:** 2.5.  
**Use in text:** task-specific/artificial data for historical OCR correction, low-resource training, domain dependence.  
**Reference line:** Suissa O., Elmalech A., Zhitomirsky-Geffet M. Optimizing the Neural Network Training for OCR Error Correction of Historical Hebrew Texts. 2023. arXiv:2307.16220.

### 5.2 Naiman et al. 2023 — large synthetic dataset
**Priority:** A, добавить.  
**Where to cite:** 2.5.  
**Use in text:** synthetic ground truth/OCR pairs are a legitimate strategy for post-correction when real aligned data are scarce; however, their validity needs real-OCR validation.  
**Reference line:** Naiman J. P., Cosillo M. G., Williams P. K. G., Goodman A. Large Synthetic Data from the arXiv for OCR Post Correction of Historic Scientific Articles. 2023. arXiv:2309.11549.

### 5.3 Guan & Greene 2024 — comparative synthetic data
**Priority:** A, добавить.  
**Where to cite:** 2.5, 6.5.  
**Use in text:** compare data volume, augmentation and synthetic data generation methods; glyph similarity and low-resource languages; directly supports future work on real-error-aware/glyph-aware synthetic noise.  
**Reference line:** Guan S., Greene D. Advancing Post-OCR Correction: A Comparative Study of Synthetic Data. 2024. arXiv:2408.02253.

### 5.4 Kashid & Bhattacharyya 2024 — RoundTripOCR
**Priority:** A, добавить.  
**Where to cite:** 2.5.  
**Use in text:** low-resource post-OCR correction can be treated as translation-like noisy-to-clean mapping; synthetic data generation can address scarcity of parallel correction datasets.  
**Reference line:** Kashid H., Bhattacharyya P. RoundTripOCR: A Data Generation Technique for Enhancing Post-OCR Error Correction in Low-Resource Devanagari Languages. 2024. arXiv:2412.15248.

### 5.5 Bourne 2024 — Scrambled text synthetic training
**Priority:** B.  
**Where to cite:** 2.5 or future work.  
**Use in text:** synthetic corruption strategies matter; under/over-corruption and non-uniform character-level corruption affect model quality.  
**Reference line:** Bourne J. Scrambled text: training Language Models to correct OCR errors using synthetic data. 2024. arXiv:2409.19735.

---

## 6. Transformer / byte-level / OCR recognition context

### 6.1 Vaswani et al. 2017 — Transformer
**Priority:** уже есть, keep.  
**Where to cite:** model section / background.  
**Use in text:** base architecture, not central.  
**Reference line:** Vaswani A. et al. Attention Is All You Need. 2017. arXiv:1706.03762.

### 6.2 Raffel et al. 2019 — T5
**Priority:** уже есть, keep.  
**Where to cite:** model section.  
**Use in text:** text-to-text framing behind T5/ByT5.  
**Reference line:** Raffel C. et al. Exploring the Limits of Transfer Learning with a Unified Text-to-Text Transformer. 2019. arXiv:1910.10683.

### 6.3 Xue et al. 2021 — ByT5
**Priority:** уже есть, central.  
**Where to cite:** 2.6 and model section.  
**Use in text:** byte-level/token-free modeling, useful for noisy and multilingual/low-resource scripts.  
**Reference line:** Xue L. et al. ByT5: Towards a token-free future with pre-trained byte-to-byte models. 2021. arXiv:2105.13626.

### 6.4 Li et al. 2021 — TrOCR
**Priority:** B.  
**Where to cite:** 2.1 or 2.6 as contrast.  
**Use in text:** modern OCR recognition itself uses transformer pretraining and synthetic data, but this project does not train OCR from images; it focuses on post-correction.  
**Reference line:** Li M. et al. TrOCR: Transformer-based Optical Character Recognition with Pre-trained Models. 2021. arXiv:2109.10282.

### 6.5 Ströbel et al. 2022 — Transformer-based HTR for historical documents
**Priority:** B.  
**Where to cite:** 2.1 or future work.  
**Use in text:** transformer OCR/HTR can adapt to historical documents, but it belongs to the recognition stage, not post-correction.  
**Reference line:** Ströbel P. B. et al. Transformer-based HTR for Historical Documents. 2022. arXiv:2203.11008.

### 6.6 Aradillas et al. 2020 — few labeled lines for historical HTR
**Priority:** B/C.  
**Where to cite:** future work.  
**Use in text:** real-domain adaptation can be feasible with limited labeled lines; useful if we later discuss line crops and small verified datasets.  
**Reference line:** Aradillas J. C., Murillo-Fuentes J. J., Olmos P. M. Boosting offline handwritten text recognition in historical documents with few labeled lines. 2020. arXiv:2012.02544.

---

## Recommended insertion plan for the paper

### Add as active citations in Section 2
1. Lyu et al. 2021
2. Rijhwani et al. 2021
3. Naiman et al. 2023
4. Guan & Greene 2024
5. Kashid & Bhattacharyya 2024
6. Kanerva et al. 2025

### Add as supporting / optional citations
7. Bourne 2024 CLOCR-C
8. Bourne 2024 Scrambled text
9. Li et al. 2021 TrOCR
10. Ströbel et al. 2022
11. eScriptorium/Kraken software context

### Do not overload the main text with all of them
The target is not to cite every related OCR paper. The target is to make the literature chain clear:
historical OCR workflow → Arabic-script/Ottoman material → post-OCR correction → synthetic data → byte-level models → synthetic-to-real gap.

## Minimal next step

For the next edit, update only:

- `docs/nlp_final_revision/literature/modern_related_work_sources.md`
- maybe `docs/nlp_final_revision/literature/related_work_insertion_plan.md`

Do **not** touch the course paper text yet.
