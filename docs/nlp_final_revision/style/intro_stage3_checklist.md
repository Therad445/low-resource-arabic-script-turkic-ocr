# Stage 3 intro/abstract style checklist

This package changes only:

- Аннотация
- Введение
- 1.1 Актуальность
- 1.2 Постановка проблемы

It does not modify:

- Section 2 related work
- results
- conclusion
- DOCX
- slides

## What improved

- Less generic "актуальность определяется несколькими обстоятельствами".
- More concrete boundary: post-correction, not full OCR/HTR.
- Clearer distinction: Ottoman Turkish source is a related Arabic-script Turkic test case, not Old Tatar/Bashkir.
- More honest synthetic-to-real framing from the beginning.
- More author's research logic, fewer template transitions.

## Check after applying

```bash
git diff -- docs/course_paper_final.md docs/course_paper_hse_export.md | sed -n '1,260p'

grep -nE "в рамках данной работы|таким образом|актуальность темы определяется|готов.*система|старотатарским.*датасетом|старобашкирским.*датасетом"   docs/course_paper_final.md docs/course_paper_hse_export.md || true
```

Expected: the Old Tatar/Bashkir dataset phrase may appear only as a negation/disclaimer.
