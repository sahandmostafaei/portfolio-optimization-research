# Portfolio Optimization Research

## Does Portfolio Optimization Add Value?

### An Out-of-Sample Analysis of Estimation Risk, Market Regimes, and Transaction Costs

Independent research project examining whether portfolio optimization
provides economically meaningful benefits after accounting for estimation
risk, market regimes, portfolio turnover, and transaction costs.

---

## Research Question

Does portfolio optimization add value once realistic implementation
constraints and estimation uncertainty are incorporated into an
out-of-sample investment framework?

---

## Research Design

The study compares four portfolio construction strategies:

- Equal Weight
- Global Minimum Variance
- Mean-Variance Optimization
- Equal Risk Contribution

The baseline design uses a diversified multi-asset ETF universe with:

- 60-month rolling estimation window
- Monthly rebalancing
- Long-only constraints
- 30% maximum position size
- No leverage
- 15 bps transaction costs
- Strict out-of-sample information timing

---

## Methodology

The research evaluates:

- portfolio returns
- volatility
- Sharpe ratio
- Sortino ratio
- maximum drawdown
- VaR and CVaR
- turnover
- concentration
- effective holdings
- market-regime performance
- factor exposures
- covariance-estimation sensitivity
- transaction-cost sensitivity
- estimation-window sensitivity
- bootstrap inference

---

## Research Status

**Research design finalized. Empirical execution pending.**

This repository intentionally does not report fabricated empirical findings.
Numerical results will only be included after the complete out-of-sample
analysis has been executed using historical market data and independently
audited.

---

## Paper

See [`paper/`](paper/) for the full research manuscript.

---

## Reproducibility

The project is designed around a reproducible research workflow in Python.
The repository separates research design, data requirements, analysis code,
and empirical outputs.

---

## Author

**Sahand Mostafaei**

Independent Research — Portfolio Optimization & Risk Management

2026
