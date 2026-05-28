# Building the NLP Final Project Report

The report source is stored in:

```text
report/main.tex
report/lit.bib
report/tables/
```

To compile locally from the repository root:

```bash
cd report
latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=build main.tex
cp build/main.pdf final_report.pdf
```

The submission-ready PDF is:

```text
report/final_report.pdf
```
