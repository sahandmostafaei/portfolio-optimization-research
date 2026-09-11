# Portfolio Optimization Research

## Does Portfolio Optimization Add Value?

### An Out-of-Sample Analysis of Estimation Risk, Market Regimes, and Transaction Costs

**Independent research project — 2026**

This project investigates whether portfolio optimization provides economically
meaningful benefits once estimation risk, market regimes, portfolio turnover,
and transaction costs are incorporated into an out-of-sample investment
framework.

> **Research status:** The research design and manuscript are finalized.
> Numerical empirical findings are intentionally not reported because the
> historical-data backtest has not been executed and audited. No empirical
> result in this repository should be interpreted as a completed finding.

---

## Research Question

Does portfolio optimization add value once estimation uncertainty, market
regimes, transaction costs, and implementation constraints are incorporated
into a genuinely out-of-sample framework?

## Strategies

The study compares four portfolio construction approaches:

1. Equal Weight
2. Global Minimum Variance
3. Mean-Variance Optimization
4. Equal Risk Contribution

## Baseline Design

- Multi-asset ETF universe: SPY, EFA, EEM, TLT, GLD, DBC, VNQ
- Monthly portfolio formation and rebalancing
- 60-month rolling estimation window
- Long-only portfolios
- Fully invested portfolios
- Maximum 30% weight per asset
- No leverage or short selling
- 15 basis points proportional transaction costs
- Strict one-period information lag

## Robustness Design

The research framework specifies tests for:

- 36-, 60-, and 120-month estimation windows
- 0, 5, 10, 15, and 30 basis points transaction costs
- Ledoit-Wolf covariance shrinkage
- Monthly versus quarterly rebalancing
- Alternative mean-variance risk-aversion parameters
- Risk-free-rate sensitivity
- Market-regime analysis
- Factor attribution
- Moving-block bootstrap inference
- Turnover and concentration
- Effective number of holdings
- Implementation cost-performance trade-offs

## Performance Measures

The intended analysis evaluates:

- Annualized return
- Annualized volatility
- Sharpe ratio
- Sortino ratio
- Maximum drawdown
- VaR and CVaR
- Terminal wealth
- Turnover
- Maximum position weight
- Effective holdings
- Risk contributions
- Regime-specific performance
- Factor exposures

## Repository Structure

```text
portfolio-optimization-research/
├── README.md
├── LICENSE
├── CITATION.cff
├── requirements.txt
├── paper/
│   ├── MSc_Finance_Research_Project_FINAL.pdf
│   └── MSc_Finance_Research_Project_FINAL.docx
├── methodology/
│   └── research_design.md
├── src/
│   ├── portfolio_research_reproducibility.py
│   └── README.md
├── data/
│   └── README.md
├── results/
│   └── README.md
├── figures/
│   └── README.md
└── docs/
    ├── research_integrity.md
    └── reproducibility.md
```

## Research Integrity

This repository deliberately separates **research design** from **empirical
findings**.

The manuscript specifies the empirical procedures, but numerical results are
not inserted until the required historical data have been obtained, the
backtest has been executed, and the outputs have been checked for timing,
weight, turnover, transaction-cost, and statistical-inference errors.

This is intentional: the project does not present simulated or invented
statistics as observed evidence.

## Reproducibility

The Python script in `src/` contains the baseline portfolio construction and
core robustness framework. It is designed to retrieve historical market data,
construct monthly returns, estimate portfolios using rolling windows, apply
transaction costs, and produce performance outputs.

Because the empirical pipeline has not yet been executed in this project
package, the repository does **not** contain fabricated CSV results or
empirical figures.

## Paper

The complete research manuscript is available in [`paper/`](paper/).

## Author

**Sahand Mostafaei**

Independent Research — Portfolio Optimization & Risk Management

2026
