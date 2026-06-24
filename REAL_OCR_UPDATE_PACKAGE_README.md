# Real-OCR documentation update package

This archive is meant to be unpacked from the root of the repository.

It updates repository documentation to reflect the new page-level Ottoman Turkish real-OCR experiment and adds two safe result files:

- `docs/nlp_final_revision/tables/real_ocr_ukr_rus_tur_chunked_summary.csv`
- `docs/nlp_final_revision/analysis/real_ocr_ukr_rus_tur_chunked_transfer.md`

It also replaces:

- `README.md`
- `DATASET_CARD.md`
- `MODEL_CARD.md`
- `REPRODUCE.md`
- `docs/nlp_final_revision/analysis/real_ocr_postcorrection.md`

It does not include raw PDF files, page images, OCR outputs, gold text, or prediction files.

## How to unpack from WSL

Assuming the zip is in your Windows Downloads folder:

```bash
cd ~/projects/low-resource-arabic-script-turkic-ocr
cp /mnt/c/Users/$USER/Downloads/real_ocr_docs_update_package.zip /tmp/ 2>/dev/null || true
```

If `$USER` does not match your Windows username, find the folder:

```bash
ls /mnt/c/Users
```

Then copy manually, for example:

```bash
cp /mnt/c/Users/YOUR_WINDOWS_USER/Downloads/real_ocr_docs_update_package.zip /tmp/
```

Unpack into the repo root:

```bash
unzip -o /tmp/real_ocr_docs_update_package.zip -d .
```

## Safety checks before commit

```bash
git status --short

git diff --name-only | grep -E 'data/real_ocr_dataset_v1|page_level_real_ocr|predictions|page_images|ocr/tesseract|source.pdf' || echo "ok: no raw data in diff"
```

Only commit documentation and summary files:

```bash
git add README.md DATASET_CARD.md MODEL_CARD.md REPRODUCE.md   docs/nlp_final_revision/tables/real_ocr_ukr_rus_tur_chunked_summary.csv   docs/nlp_final_revision/analysis/real_ocr_ukr_rus_tur_chunked_transfer.md   docs/nlp_final_revision/analysis/real_ocr_postcorrection.md   docs/course_paper_real_ocr_update_snippets.md

git commit -m "docs: update real OCR transfer results"
git push
```
