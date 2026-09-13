# Portfolio Optimization Research

## Does Portfolio Optimization Add Value?

### An Out-of-Sample Analysis of Estimation Risk, Market Regimes, and Transaction Costs

**Independent Quantitative Finance Research Project**

This project investigates whether portfolio optimization generates
economically meaningful benefits when evaluated under estimation uncertainty,
market-regime variation, portfolio turnover, transaction costs, and realistic
portfolio constraints.

The study is designed as an empirical research project rather than a
demonstration of optimization techniques alone. Its central objective is to
determine whether theoretically attractive portfolio allocations remain
robust when evaluated strictly out of sample.

---

## Research Question

> Does portfolio optimization add value once realistic implementation
> constraints and estimation uncertainty are incorporated into an out-of-sample
> investment framework?

Traditional portfolio optimization depends on estimated expected returns and
covariance matrices. Both are uncertain and can produce unstable portfolio
weights.

This research evaluates portfolio construction methods using a rolling
out-of-sample framework and examines:

- estimation risk;
- covariance uncertainty;
- market regimes;
- portfolio turnover;
- transaction costs;
- rebalancing frequency;
- portfolio concentration;
- tail risk; and
- implementation constraints.

---

## Research Motivation

Modern portfolio theory provides a formal framework for allocating capital
across risky assets.

However, the practical performance of an optimized portfolio can differ
substantially from its theoretical characteristics because the parameters used
by the optimizer must be estimated from historical data.

This creates a fundamental empirical question:

> Does additional model complexity translate into superior out-of-sample
> investment performance?

The project therefore compares established portfolio construction methods
under a common information set, common asset universe, common implementation
constraints, and common out-of-sample evaluation procedure.

The analysis focuses not only on returns, but also on whether any observed
advantage survives transaction costs, estimation uncertainty, turnover, and
different market conditions.

---

## Hypotheses

### H1 — Out-of-Sample Performance

Portfolio optimization does not necessarily outperform simple equal weighting
when evaluated strictly out of sample.

### H2 — Estimation Risk

Strategies that depend more heavily on estimated parameters are more sensitive
to estimation uncertainty and may exhibit weaker out-of-sample performance.

### H3 — Transaction Costs

Higher portfolio turnover reduces the economic attractiveness of optimized
strategies after transaction costs.

### H4 — Market Regimes

The relative performance of portfolio construction strategies varies across
bull, neutral, and bear market environments.

### H5 — Covariance Estimation

Covariance shrinkage can improve the stability of optimized portfolios by
reducing sensitivity to noisy sample covariance estimates.

---

## Portfolio Strategies

The baseline analysis compares four portfolio construction approaches.

### 1. Equal Weight

Each asset receives the same portfolio weight.

Equal weighting provides a transparent benchmark that does not require
estimation of expected returns or covariance matrices.

### 2. Global Minimum Variance

The portfolio minimizes estimated variance subject to the investment
constraints.

### 3. Mean-Variance Optimization

The portfolio balances estimated expected return against estimated portfolio
variance using a risk-aversion parameter.

### 4. Equal Risk Contribution

The portfolio attempts to allocate portfolio risk approximately equally
across assets.

These four strategies represent different approaches to portfolio
construction and allow the research to examine whether greater model
complexity produces greater economic value.

---

## Asset Universe

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

The universe is intentionally multi-asset and includes exposures to:

- domestic equities;
- international developed equities;
- emerging-market equities;
- government bonds;
- precious metals;
- commodities; and
- real estate.

---

## Baseline Research Design

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
| Baseline risk-free rate | 0% |

Portfolio weights are formed using information available no later than the end
of the preceding observation period.

The portfolio return for the evaluation period is then observed out of sample.

This chronology is intended to prevent look-ahead bias.

---

## Out-of-Sample Framework

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

The return during month `t` is never used to determine the portfolio weights
that are evaluated during that same month.

This chronological separation is a central component of the research design.

---

## Performance Evaluation

The study evaluates both investment performance and implementation
characteristics.

### Return and Risk

- annualized return;
- annualized volatility;
- Sharpe ratio;
- Sortino ratio;
- maximum drawdown;
- skewness;
- excess kurtosis.

### Tail Risk

- historical Value at Risk;
- Conditional Value at Risk.

### Implementation

- portfolio turnover;
- transaction costs;
- maximum individual portfolio weight;
- effective number of holdings;
- portfolio concentration.

### Robustness

- alternative estimation windows;
- alternative transaction-cost assumptions;
- covariance shrinkage;
- alternative risk-aversion parameters;
- quarterly versus monthly rebalancing;
- market-regime analysis;
- risk-free-rate sensitivity;
- bootstrap inference.

---

## Market-Regime Analysis

Market regimes are defined using trailing 12-month SPY performance.

The baseline classification is:

- **Bull:** trailing 12-month SPY return above +10%;
- **Neutral:** trailing 12-month SPY return between -10% and +10%;
- **Bear:** trailing 12-month SPY return below -10%.

The regime signal is lagged by one observation so that information from the
evaluation period cannot enter its own regime classification.

The purpose is to determine whether portfolio construction strategies exhibit
different performance and risk characteristics across market environments.

---

## Robustness Analysis

A central objective is to determine whether conclusions depend on a particular
parameter choice.

### Estimation Window

- 36 months;
- 60 months;
- 120 months.

### Transaction Costs

- 0 bps;
- 5 bps;
- 10 bps;
- 15 bps;
- 30 bps.

### Mean-Variance Risk Aversion

- gamma = 1;
- gamma = 3;
- gamma = 5;
- gamma = 10.

### Covariance Estimation

The baseline sample covariance matrix is compared with Ledoit-Wolf covariance
shrinkage.

### Rebalancing Frequency

Monthly rebalancing is compared with quarterly rebalancing.

### Statistical Inference

Moving-block bootstrap procedures are used to examine uncertainty around
performance statistics and pairwise strategy differences.

---

## Academic Contribution

The project addresses the gap between theoretical portfolio optimization and
practical investment implementation.

Rather than evaluating optimization methods solely through in-sample
portfolio characteristics, the study asks whether their potential benefits
survive:

1. rolling out-of-sample evaluation;
2. estimation uncertainty;
3. transaction costs;
4. portfolio turnover;
5. market-regime variation;
6. covariance-estimation uncertainty; and
7. alternative model specifications.

The intended contribution is not the proposal of a new optimization algorithm.

Instead, the project provides a disciplined empirical comparison of established
portfolio construction methods under a consistent and implementation-aware
framework.

See [`docs/academic_contribution.md`](docs/academic_contribution.md) for the
full contribution statement.

---

## Research Integrity

No empirical finding is reported unless it has been generated from actual
historical data through the research pipeline.

The repository separates:

- research design;
- methodology;
- source code;
- data requirements;
- empirical outputs; and
- interpretation.

The current repository therefore does not fabricate numerical findings merely
to make the research appear complete.

See [`docs/research_integrity.md`](docs/research_integrity.md) for the
research-integrity protocol.

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
    |   |-- MSc_Finance_Research_Project_FINAL.docx
    |   `-- MSc_Finance_Research_Project_FINAL.pdf
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

## Research Status

**Research design finalized. Empirical execution pending.**

The repository does not currently claim empirical findings that have not been
generated and audited.

The next research stage is:

1. empirical execution;
2. result auditing;
3. robustness analysis;
4. statistical inference;
5. integration of verified results into the manuscript.

---

## Paper

The research manuscript is available in the `paper/` directory.

The manuscript develops:

- research motivation;
- theoretical background;
- literature foundation;
- hypotheses;
- research methodology;
- empirical framework;
- robustness design; and
- research-integrity standards.

---

## Reproducibility

The project is implemented in Python and follows a reproducible research
structure.

Research assumptions are documented separately from executable analysis code.

Required Python packages are listed in
[`requirements.txt`](requirements.txt).

The repository is structured so that the research design, methodology,
analysis code, and empirical outputs can be examined independently.

---

## Author

**Sahand Mostafaei**

Independent Research — Quantitative Finance, Portfolio Optimization &
Risk Management

2026
