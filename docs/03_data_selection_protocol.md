# Data Selection Protocol v1

## Purpose

Select a small but methodologically useful corpus for historical OCR experiments on Turkic texts in Arabic script.

## Unit of selection

The benchmark split unit is the **document**. A document may contain one or many pages. Lines inherit document metadata.

## Inclusion rules for Sprint 1 / early Sprint 2

Prefer documents that satisfy most of the following:

1. **Printed first** — avoid handwriting in the first benchmark release.
2. **Legible page structure** — regular lines, limited marginalia, limited tables.
3. **Clear provenance** — known source, archive, collection, or edition.
4. **Stable dating** — exact year preferred; approximate range acceptable.
5. **Reasonable scan quality** — enough resolution and contrast for line extraction.
6. **Rights clarity** — it should be possible to store local scans and publish at least metadata + transcriptions.

## Diversity targets

Aim for diversity across:

- source collections / archives,
- publication years,
- typefaces / print styles,
- scan quality buckets,
- orthographic variation where identifiable.

Avoid building the first benchmark from only one book or one source collection.

## Exclusion rules

Exclude from the first benchmark release if a document is dominated by:

- severe bleed-through or overexposure,
- handwritten corrections across most pages,
- complex tables or multi-column layouts,
- rights restrictions that block even local research use,
- extremely fragmentary text that cannot be consistently transcribed.

## Metadata to record per document

Required document metadata:

- `doc_id`
- `source_id`
- `title_short`
- `year`
- `language_note`
- `script_note`
- `print_or_handwritten`
- `scan_quality_bucket`
- `layout_complexity`
- `rights_note`
- `local_storage_note`

## Sampling strategy

### Pilot phase

- 8–12 documents
- 15–20 pages total
- 200–300 manually transcribed lines

### First benchmark phase

- 10–15 documents
- 800–1000 manually transcribed lines

### Article-grade phase

- 15–30 documents
- 1500–2500 manually transcribed lines

## Logging decisions

Every rejected candidate should be logged briefly. A good benchmark is shaped as much by exclusions as by inclusions.