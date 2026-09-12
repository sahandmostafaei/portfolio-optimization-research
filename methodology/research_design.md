# Research Design

## Research Question

Does portfolio optimization add value once estimation risk, market regimes,
portfolio turnover, and transaction costs are incorporated into a genuinely
out-of-sample investment framework?

## Strategies

The study compares four portfolio construction approaches:

1. Equal Weight
2. Global Minimum Variance
3. Mean-Variance Optimization
4. Equal Risk Contribution

## Asset Universe

The baseline universe consists of:

- SPY
- EFA
- EEM
- TLT
- GLD
- DBC
- VNQ

## Baseline Design

- Monthly portfolio formation
- 60-month rolling estimation window
- Long-only portfolios
- Fully invested portfolios
- Maximum 30% allocation to any individual asset
- No leverage
- No short selling
- 15 basis points proportional transaction costs
- Strict one-period information lag

## Robustness Tests

The research design includes:

- 36-, 60-, and 120-month estimation windows
- Alternative transaction costs
- Ledoit-Wolf covariance shrinkage
- Monthly versus quarterly rebalancing
- Alternative risk-aversion parameters
- Risk-free-rate sensitivity
- Market-regime analysis
- Factor regressions
- Moving-block bootstrap inference
- Turnover and concentration analysis

## Research Integrity

No empirical result is reported unless it is generated from the
corresponding reproducible analysis pipeline.

At the current stage, the repository documents the complete research design
and does not claim completed empirical findings.
