# Data layout

This repo does not commit raw scans or derived heavy artifacts.

## Folders
- `data/raw/` — original scans (DO NOT COMMIT)
- `data/interim/` — intermediate files (line crops, temporary outputs)
- `data/processed/` — processed datasets ready for training
- `data/splits/` — text files listing train/val/test identifiers

## Splits format
Each split file contains one sample ID per line (e.g., relative path to line image).
Example:
`printed_book_1905/page_001/line_0001.png`

## Reproducing locally
1) Obtain permissioned scans and place them in `data/raw/`
2) Run preprocessing and line cropping scripts to populate `data/processed/`
3) Generate splits in `data/splits/v1/`
