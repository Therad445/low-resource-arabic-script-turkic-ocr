# Experiment plan

## Metrics
- CER (character error rate)
- WER (word error rate)

## Baselines
B0: "Off-the-shelf" OCR (if applicable, e.g., Kraken default model)  
B1: Domain-specific preprocessing + baseline OCR  
B2: Fine-tuning on small labeled set (LoRA/finetune depending on tool)

## Proposed improvements
I1: Better line segmentation / cropping
I2: Image preprocessing (deskew, denoise, contrast)
I3: Fine-tuning on target font/domain
I4: Decoding constraints (optional; lexicon-aware postprocessing)

## Evaluation protocol
- Split by **document**, not by line, to avoid leakage.
- Maintain a fixed `gold_test_v1`.
- Report mean + variance if multiple seeds.

## Ablations
- Remove preprocessing → measure delta
- Reduce training labels (100%, 50%, 20%) → low-resource curve

## Deliverable tables/figures for paper
- Table: baseline vs improved CER/WER
- Figure: label size vs CER (learning curve)
- Table: error taxonomy distribution
