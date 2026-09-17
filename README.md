# Portfolio Optimization Research

## Does Portfolio Optimization Add Value?

### An Out-of-Sample Analysis of Estimation Risk, Market Regimes, and Transaction Costs

**Independent Quantitative Finance Research Project**

---

## Research Overview

This project investigates whether portfolio optimization generates economically meaningful benefits when evaluated under estimation uncertainty, market-regime variation, portfolio turnover, transaction costs, and realistic portfolio constraints.

The study is designed as an empirical research project rather than a demonstration of optimization techniques alone. Its central objective is to examine whether theoretically attractive portfolio allocations remain robust when evaluated under a disciplined out-of-sample framework.

The project combines portfolio theory, quantitative finance, empirical asset-pricing concepts, statistical inference, and implementation-aware portfolio analysis.

---

## Research Question

> **Does portfolio optimization add value once realistic implementation constraints and estimation uncertainty are incorporated into an out-of-sample investment framework?**

Traditional portfolio optimization depends on estimated expected returns and covariance matrices. Because these parameters are uncertain, optimized portfolio weights can become unstable and may fail to deliver the characteristics suggested by in-sample optimization.

This research therefore examines:

- estimation risk;
- covariance uncertainty;
- out-of-sample performance;
- market regimes;
- portfolio turnover;
- transaction costs;
- rebalancing frequency;
- portfolio concentration;
- tail risk; and
- implementation constraints.

---

## Research Motivation

Modern portfolio theory provides a formal framework for allocating capital across risky assets.

However, the parameters required by optimization are estimated rather than known. This creates a fundamental distinction between a portfolio that is mathematically optimal under estimated parameters and a portfolio that performs well when those estimates are confronted with future observations.

The project therefore asks whether additional model complexity translates into robust economic value.

The analysis compares established portfolio construction methods using a common:

- asset universe;
- information set;
- estimation framework;
- investment constraint set;
- rebalancing framework; and
- out-of-sample evaluation procedure.

The objective is to evaluate portfolio construction from both a statistical and an investment-implementation perspective.

---

## Hypotheses

### H1 — Out-of-Sample Performance

Portfolio optimization does not necessarily generate superior out-of-sample risk-adjusted performance relative to equal weighting.

### H2 — Estimation Risk

Strategies that rely more heavily on estimated parameters are more sensitive to estimation uncertainty.

### H3 — Transaction Costs

Higher portfolio turnover reduces the economic attractiveness of optimized portfolios after transaction costs.

### H4 — Market Regimes

The relative performance and risk characteristics of portfolio construction strategies vary across different market environments.

### H5 — Covariance Estimation

Covariance shrinkage can improve portfolio stability by reducing sensitivity to noisy sample covariance estimates.

---

# Portfolio Strategies

The baseline analysis compares four portfolio construction approaches.

## 1. Equal Weight

Each asset receives an equal portfolio allocation.

For `N` assets:

`w_i = 1 / N`

Equal weighting provides a transparent benchmark that does not require expected-return or covariance estimation.

Its simplicity makes it an appropriate reference point for assessing whether optimization provides sufficient additional value to justify its estimation requirements.

---

## 2. Global Minimum Variance

The global minimum variance portfolio solves:

`min_w w' Σ w`

subject to:

`sum_i w_i = 1`

and:

`0 <= w_i <= 0.30`

where:

- `w` is the portfolio-weight vector;
- `Σ` is the estimated covariance matrix.

The strategy attempts to minimize estimated portfolio variance subject to the implementation constraints.

---

## 3. Mean-Variance Optimization

The mean-variance strategy solves:

`max_w [w' μ - (γ / 2) w' Σ w]`

subject to the portfolio constraints.

Here:

- `μ` is the estimated expected-return vector;
- `Σ` is the estimated covariance matrix;
- `γ` is the risk-aversion parameter.

The baseline specification uses:

`γ = 3`

Robustness specifications consider:

`γ ∈ {1, 3, 5, 10}`

Because both expected returns and covariances are estimated from historical observations, mean-variance optimization provides a direct framework for studying estimation risk.

---

## 4. Equal Risk Contribution

The equal-risk-contribution strategy seeks to allocate portfolio risk approximately equally across assets.

Rather than relying primarily on expected-return forecasts, the approach focuses on the covariance structure and the contribution of each asset to overall portfolio risk.

This provides a useful contrast with both equal weighting and mean-variance optimization.

---

# Asset Universe

The baseline universe consists of seven exchange-traded funds:

| Ticker | Broad Exposure |
|---|---|
| SPY | U.S. equities |
| EFA | Developed-market equities excluding the U.S. |
| EEM | Emerging-market equities |
| TLT | Long-duration U.S. Treasuries |
| GLD | Gold |
| DBC | Broad commodities |
| VNQ | U.S. real estate |

The universe provides exposure across:

- domestic equities;
- developed international equities;
- emerging-market equities;
- government bonds;
- precious metals;
- commodities; and
- real estate.

The multi-asset structure allows the research to examine portfolio construction beyond a single equity market.

---

# Baseline Research Design

| Parameter | Baseline |
|---|---|
| Estimation window | 60 months |
| Rebalancing | Monthly |
| Portfolio type | Long-only |
| Investment constraint | Fully invested |
| Maximum individual weight | 30% |
| Leverage | None |
| Short selling | None |
| Transaction cost | 15 bps |
| Mean-variance risk aversion | 3 |
| Baseline annual risk-free rate | 0% |

Portfolio weights are formed using information available no later than the end of the preceding observation period.

The portfolio return for the evaluation period is subsequently observed out of sample.

This chronology is designed to prevent look-ahead bias.

---

# Out-of-Sample Framework

The empirical framework follows a rolling estimation procedure.

The information flow is:

    Historical observations through t-1
                    |
                    v
           Rolling estimation window
                    |
                    v
           Parameter estimation
                    |
                    v
           Portfolio construction
                    |
                    v
           Weights applied during t
                    |
                    v
           Out-of-sample return
                    |
                    v
           Performance evaluation

The return during month `t` is not used to determine the portfolio weights evaluated during that same month.

This chronological separation is a central component of the research design.

---

# Performance Evaluation

The study evaluates both investment performance and implementation characteristics.

## Return and Risk

- annualized return;
- annualized volatility;
- Sharpe ratio;
- Sortino ratio;
- maximum drawdown;
- skewness; and
- excess kurtosis.

## Tail Risk

- historical Value at Risk;
- Conditional Value at Risk.

## Implementation

- portfolio turnover;
- transaction costs;
- maximum individual portfolio weight;
- effective number of holdings; and
- portfolio concentration.

## Robustness

- alternative estimation windows;
- alternative transaction-cost assumptions;
- covariance shrinkage;
- alternative risk-aversion parameters;
- quarterly versus monthly rebalancing;
- market-regime analysis;
- risk-free-rate sensitivity; and
- moving-block bootstrap inference.

---

# Market-Regime Analysis

Market regimes are defined using trailing 12-month SPY performance.

The baseline classification is:

- **Bull:** trailing 12-month SPY return above +10%;
- **Neutral:** trailing 12-month SPY return between -10% and +10%;
- **Bear:** trailing 12-month SPY return below -10%.

The regime signal is lagged by one observation so that information from the evaluation period cannot enter its own classification.

The purpose is to examine whether portfolio construction methods exhibit different performance and risk characteristics across market environments.

---

# Robustness Analysis

A central objective of the project is to determine whether conclusions depend on a particular parameter choice.

## Estimation Window

- 36 months;
- 60 months;
- 120 months.

## Transaction Costs

- 0 bps;
- 5 bps;
- 10 bps;
- 15 bps;
- 30 bps.

## Mean-Variance Risk Aversion

- gamma = 1;
- gamma = 3;
- gamma = 5;
- gamma = 10.

## Covariance Estimation

The baseline sample covariance matrix is compared with Ledoit-Wolf covariance shrinkage.

The purpose is to examine whether optimized allocations are sensitive to covariance-estimation noise.

## Rebalancing Frequency

Monthly rebalancing is compared with quarterly rebalancing.

This allows the research to examine the trade-off between portfolio responsiveness, turnover, transaction costs, and implementation efficiency.

## Risk-Free Rate

Sharpe-ratio calculations consider both:

- 0% annual risk-free rate; and
- 2% annual risk-free rate.

## Statistical Inference

Moving-block bootstrap procedures are included to assess uncertainty around performance statistics and pairwise strategy differences while partially preserving serial dependence in monthly observations.

---

# Academic Contribution

The project addresses the gap between theoretical portfolio optimization and practical investment implementation.

Rather than evaluating optimization methods solely through in-sample portfolio characteristics, the study examines whether potential benefits survive:

1. rolling out-of-sample evaluation;
2. estimation uncertainty;
3. transaction costs;
4. portfolio turnover;
5. market-regime variation;
6. covariance-estimation uncertainty; and
7. alternative model specifications.

The intended contribution is not the development of a new optimization algorithm.

Instead, the project provides a structured empirical framework for evaluating established portfolio construction methods under common information, risk, and implementation constraints.

See [`docs/academic_contribution.md`](docs/academic_contribution.md) for the detailed contribution statement.

---

# Research Integrity

The project distinguishes explicitly between research design and empirical evidence.

No numerical empirical finding is represented as a completed result unless it has been generated from the research pipeline using historical market data.

The repository therefore separates:

- research design;
- methodology;
- source code;
- data requirements;
- empirical outputs; and
- interpretation.

This structure is intended to maintain a clear distinction between proposed analysis and completed evidence.

See [`docs/research_integrity.md`](docs/research_integrity.md) for the research-integrity framework.

---

# Repository Structure

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
    `-- requirements.txt

---

# Research Status

**Research design finalized. Empirical execution framework established.**

The repository is structured around a complete research design, executable analysis framework, supporting methodology, literature foundation, and manuscript.

The project is deliberately not presented as containing completed empirical findings that have not been generated and audited.

The research framework is designed to support:

1. empirical execution;
2. result auditing;
3. robustness analysis;
4. statistical inference; and
5. integration of verified evidence into the manuscript.

---

# Paper

The research manuscript is available in the `paper/` directory:

- [`research_paper.pdf`](paper/research_paper.pdf)
- [`research_paper.docx`](paper/research_paper.docx)

The manuscript develops:

- research motivation;
- theoretical background;
- literature foundation;
- hypotheses;
- portfolio construction methodology;
- empirical research design;
- robustness framework;
- statistical methodology;
- implementation considerations; and
- research-integrity standards.

---

# Reproducibility

The project is implemented in Python and follows a reproducible research structure.

Research assumptions are documented separately from executable analysis code.

Required Python packages are listed in [`requirements.txt`](requirements.txt).

The repository is structured so that the research question, methodology, source code, research documentation, and manuscript can be examined independently.

---

# Research Areas

This project combines concepts from:

- Modern Portfolio Theory;
- portfolio optimization;
- quantitative investment;
- asset allocation;
- risk management;
- empirical finance;
- financial econometrics;
- statistical inference; and
- investment implementation.

---

# Author

**Sahand Mostafaei**

Independent Research — Quantitative Finance, Portfolio Optimization & Risk Management

2026
