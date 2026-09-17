# Repository Manifest

This manifest records the principal files included in the portfolio optimization research repository.

---

## Research Documentation

- `README.md` — Repository overview, research question, methodology summary, project structure, and research status.
- `methodology/research_design.md` — Detailed research design, hypotheses, portfolio construction methodology, information timing, performance measures, robustness framework, and limitations.
- `literature/literature_review.md` — Literature foundation covering portfolio optimization, estimation risk, covariance estimation, diversification, statistical inference, and related empirical finance research.
- `docs/academic_contribution.md` — Statement of the project's academic motivation and intended contribution.
- `docs/research_integrity.md` — Research-integrity framework distinguishing research design from completed empirical evidence.
- `docs/reproducibility.md` — Reproducibility and project-structure documentation.

---

## Research Manuscript

- `paper/research_paper.pdf` — Primary PDF version of the independent finance research manuscript.
- `paper/research_paper.docx` — Editable Word version of the independent finance research manuscript.

---

## Source Code

- `src/portfolio_research_reproducibility.py` — Python research pipeline implementing the portfolio construction and out-of-sample research framework.
- `src/README.md` — Documentation for the research source-code directory.

---

## Data

- `data/README.md` — Documentation of the data requirements and data-handling framework.

The repository does not embed fabricated empirical observations or manually created numerical findings.

---

## Results

- `results/README.md` — Documentation of the intended empirical-results structure and research-integrity requirements.

Numerical empirical results are not represented as completed findings unless generated through the research pipeline.

---

## Figures

- `figures/README.md` — Documentation for research figures and visualization outputs.

---

## Automation

- `.github/workflows/research_pipeline.yml` — GitHub Actions workflow for repository and source-code validation.

---

## Project Metadata

- `requirements.txt` — Python package dependencies required by the research pipeline.
- `references.bib` — Bibliographic database supporting the research literature.
- `CITATION.cff` — Citation metadata for the repository.
- `LICENSE` — Repository license.

---

## Repository Structure

    portfolio-optimization-research/
    |
    |-- .github/
    |   `-- workflows/
    |       `-- research_pipeline.yml
    |
    |-- data/
    |   `-- README.md
    |
    |-- docs/
    |   |-- academic_contribution.md
    |   |-- research_integrity.md
    |   `-- reproducibility.md
    |
    |-- figures/
    |   `-- README.md
    |
    |-- literature/
    |   `-- literature_review.md
    |
    |-- methodology/
    |   `-- research_design.md
    |
    |-- paper/
    |   |-- research_paper.docx
    |   `-- research_paper.pdf
    |
    |-- results/
    |   `-- README.md
    |
    |-- src/
    |   |-- README.md
    |   `-- portfolio_research_reproducibility.py
    |
    |-- CITATION.cff
    |-- LICENSE
    |-- MANIFEST.md
    |-- README.md
    |-- references.bib
    `-- requirements.txt

---

## Research Status

**Research design finalized. Empirical execution framework established.**

The repository is intended to document a complete independent quantitative-finance research project, including its research question, theoretical motivation, literature foundation, hypotheses, methodology, portfolio construction framework, robustness design, reproducibility structure, source code, and manuscript.

No unverified numerical findings are presented as completed empirical evidence.

---

## Principal Research Question

> Does portfolio optimization add value once realistic implementation constraints and estimation uncertainty are incorporated into an out-of-sample investment framework?

---

## Baseline Research Specification

- Asset universe: SPY, EFA, EEM, TLT, GLD, DBC, VNQ
- Estimation window: 60 months
- Rebalancing frequency: monthly
- Portfolio: long-only
- Investment constraint: fully invested
- Maximum individual weight: 30%
- Leverage: none
- Short selling: none
- Transaction cost: 15 bps
- Mean-variance risk aversion: 3
- Baseline annual risk-free rate: 0%

---

## Portfolio Strategies

The research framework compares:

1. Equal Weight
2. Global Minimum Variance
3. Mean-Variance Optimization
4. Equal Risk Contribution

---

## Robustness Framework

The research framework includes:

- 36-, 60-, and 120-month estimation windows;
- 0, 5, 10, 15, and 30 bps transaction-cost assumptions;
- mean-variance gamma values of 1, 3, 5, and 10;
- Ledoit-Wolf covariance shrinkage;
- monthly versus quarterly rebalancing;
- 0% versus 2% annual risk-free-rate sensitivity;
- market-regime analysis; and
- moving-block bootstrap inference.

---

## File Integrity Note

The two authoritative manuscript files are:

- `paper/research_paper.pdf`
- `paper/research_paper.docx`

These filenames should be used consistently throughout the repository.
