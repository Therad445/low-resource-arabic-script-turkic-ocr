# Course paper references

This file contains a verified working bibliography for the course paper on OCR post-correction for historical Arabic-script Turkic texts.

The references are grouped by the role they play in the paper. The final bibliography in the course paper can later be formatted according to the required university style.

## 1. Core model and architecture references

### Transformer architecture

Vaswani, A., Shazeer, N., Parmar, N., Uszkoreit, J., Jones, L., Gomez, A. N., Kaiser, L., & Polosukhin, I. (2017). *Attention Is All You Need*. arXiv:1706.03762.

Use in the paper:

- background for Transformer-based sequence-to-sequence models;
- section 2 or section 4, when explaining the general neural architecture family.

URL: https://arxiv.org/abs/1706.03762

### T5 text-to-text framework

Raffel, C., Shazeer, N., Roberts, A., Lee, K., Narang, S., Matena, M., Zhou, Y., Li, W., & Liu, P. J. (2019). *Exploring the Limits of Transfer Learning with a Unified Text-to-Text Transformer*. arXiv:1910.10683.

Use in the paper:

- background for text-to-text formulation;
- section 4, before introducing ByT5.

URL: https://arxiv.org/abs/1910.10683

### ByT5 byte-level model

Xue, L., Barua, A., Constant, N., Al-Rfou, R., Narang, S., Kale, M., Roberts, A., & Raffel, C. (2021). *ByT5: Towards a token-free future with pre-trained byte-to-byte models*. arXiv:2105.13626.

Use in the paper:

- main reference for ByT5-small;
- justification for byte-level modeling;
- section 4.3 and section 5.5.

URL: https://arxiv.org/abs/2105.13626

## 2. OCR post-correction references

### Character sequence-to-sequence OCR post-correction

Ramirez-Orta, J., Xamena, E., Maguitman, A., Milios, E., & Soto, A. J. (2021). *Post-OCR Document Correction with large Ensembles of Character Sequence-to-Sequence Models*. arXiv:2109.06264.

Use in the paper:

- post-OCR correction as character-level/sequence-to-sequence task;
- section 2.4 and section 4.

URL: https://arxiv.org/abs/2109.06264

### Unsupervised OCR post-correction for historical corpora

Hämäläinen, M., & Hengchen, S. (2019). *From the Paft to the Fiiture: a Fully Automatic NMT and Word Embeddings Method for OCR Post-Correction*. arXiv:1910.05535.

Use in the paper:

- historical OCR error correction;
- character-based NMT/seq2seq post-correction;
- section 2.4.

URL: https://arxiv.org/abs/1910.05535

### OCR post-correction and spelling normalization

Duong, Q., Hämäläinen, M., & Hengchen, S. (2020). *An Unsupervised method for OCR Post-Correction and Spelling Normalisation for Finnish*. arXiv:2011.03502.

Use in the paper:

- discussion of post-correction and normalization;
- contrast with rule-based normalization;
- section 2.4 and limitations.

URL: https://arxiv.org/abs/2011.03502

### Historical Hebrew OCR post-correction with synthetic/task-specific data

Suissa, O., Elmalech, A., & Zhitomirsky-Geffet, M. (2023). *Optimizing the Neural Network Training for OCR Error Correction of Historical Hebrew Texts*. arXiv:2307.16220.

Use in the paper:

- synthetic or task-specific training data for historical OCR post-correction;
- low-resource historical-script scenario;
- section 2.4, section 3, section 6.

URL: https://arxiv.org/abs/2307.16220

### LLM-based OCR post-correction limitations

Kanerva, J., Ledins, C., Käpyaho, S., & Ginter, F. (2025). *OCR Error Post-Correction with LLMs in Historical Documents: No Free Lunches*. arXiv:2502.01205.

Use in the paper:

- cautionary reference for modern LLM-based post-correction;
- section 6 and future work.

URL: https://arxiv.org/abs/2502.01205

## 3. Historical OCR / HTR and ground truth references

### OCR workflow for historical printings

Reul, C., Christ, D., Hartelt, A., Balbach, N., Wehner, M., Springmann, U., Wick, C., Grundig, C., Büttner, A., & Puppe, F. (2019). *OCR4all -- An Open-Source Tool Providing a (Semi-)Automatic OCR Workflow for Historical Printings*. arXiv:1909.04032.

Use in the paper:

- historical OCR workflow;
- layout, typography, preprocessing, recognition and post-processing;
- section 2.1.

URL: https://arxiv.org/abs/1909.04032

### Ground truth for historical OCR

Springmann, U., Reul, C., Dipper, S., & Baiter, J. (2018). *Ground Truth for training OCR engines on historical documents in German Fraktur and Early Modern Latin*. arXiv:1809.05501.

Use in the paper:

- ground truth creation;
- historical OCR datasets;
- section 2.1 and section 3.

URL: https://arxiv.org/abs/1809.05501

## 4. Arabic-script OCR references

### Arabic OCR survey

Kasem, M. S., Mahmoud, M., & Kang, H.-S. (2023). *Advancements and Challenges in Arabic Optical Character Recognition: A Comprehensive Survey*. arXiv:2312.11812.

Use in the paper:

- overview of Arabic OCR challenges;
- section 2.2.

URL: https://arxiv.org/abs/2312.11812

### Arabic-script OCR system

Osman, H., Zaghw, K., Hazem, M., & Elsehely, S. (2020). *An Efficient Language-Independent Multi-Font OCR for Arabic Script*. arXiv:2009.09115.

Use in the paper:

- Arabic-script OCR as a technically difficult OCR setting;
- cursive script and overlapping letters;
- section 2.2.

URL: https://arxiv.org/abs/2009.09115

## 5. Ottoman Turkish / historical Turkish references

### Ottoman Turkish print archive and non-Latin script transcription

Kirmizialtin, S., & Wrisley, D. (2020). *Automated Transcription of Non-Latin Script Periodicals: A Case Study in the Ottoman Turkish Print Archive*. arXiv:2011.01139.

Use in the paper:

- Ottoman Turkish in Arabic script;
- script change and digitization gap;
- section 2.3 and section 3.

URL: https://arxiv.org/abs/2011.01139

### Historical Turkish NLP resources and models

Özateş, Ş. B., Tıraş, T. E., Adak, E. E., Doğan, B., Karagöz, F. B., Genç, E. E., & Bilgin Taşdemir, E. F. (2025). *Building Foundations for Natural Language Processing of Historical Turkish: Resources and Models*. arXiv:2501.04828.

Use in the paper:

- historical Turkish NLP as an underexplored area;
- future work: NER, parsing, larger corpora, downstream analysis;
- section 1.1, section 2.3, section 6.

URL: https://arxiv.org/abs/2501.04828

## 6. How to use these references in the draft

Minimum required insertions for the course paper:

1. Section 2.1: Reul et al. 2019; Springmann et al. 2018.
2. Section 2.2: Kasem et al. 2023; Osman et al. 2020.
3. Section 2.3: Kirmizialtin & Wrisley 2020; Özateş et al. 2025.
4. Section 2.4: Ramirez-Orta et al. 2021; Hämäläinen & Hengchen 2019; Duong et al. 2020; Suissa et al. 2023.
5. Section 4.3: Vaswani et al. 2017; Raffel et al. 2019; Xue et al. 2021.
6. Section 6: Kanerva et al. 2025; Özateş et al. 2025.

Priority for first editing pass:

1. ByT5: Xue et al. 2021.
2. Post-OCR correction: Ramirez-Orta et al. 2021; Hämäläinen & Hengchen 2019.
3. Historical OCR: Reul et al. 2019; Springmann et al. 2018.
4. Arabic/Ottoman context: Kasem et al. 2023; Kirmizialtin & Wrisley 2020.
