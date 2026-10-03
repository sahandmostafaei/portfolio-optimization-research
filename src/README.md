# Analysis Code

This directory contains the reproducible Python implementation of the research methodology and the empirical-results pipeline.

## Source Files

### portfolio_research_reproducibility.py

Core research implementation containing:

- Return construction and validation
- Rolling estimation
- Portfolio optimization
- Covariance estimation
- Portfolio constraints
- Portfolio weighting
- Baseline backtesting
- Performance measurement
- Transaction-cost inputs
- Regime analysis
- Robustness and reproducibility utilities
- Bootstrap procedures

### empirical_results_pipeline.py

Audited empirical-results pipeline for executing the out-of-sample research design using historical market data.

The pipeline implements:

- Strict rolling out-of-sample backtesting
- Monthly portfolio rebalancing
- Transaction-cost accounting
- Annualized return and volatility
- Sharpe ratios
- Maximum drawdown
- Turnover and realized-weight tracking
- HAC-based statistical inference
- Paired moving-block bootstrap inference
- Holm multiple-testing adjustment
- Market-regime analysis
- Fama-French five-factor regression analysis
- Transaction-cost break-even analysis
- Covariance-estimation robustness testing
- Estimation-window and risk-aversion robustness analysis
- Reproducibility metadata and data provenance
- Automated research figures and result tables

The empirical pipeline uses the core optimizer and data-loading functionality from `portfolio_research_reproducibility.py`.

## Research Integrity

The presence of the empirical pipeline does not imply that numerical empirical findings have already been generated.

The research is explicitly designed to avoid fabricated or unverified empirical results. Numerical findings should only be reported after the pipeline has been executed successfully using validated historical market data.

The backtesting framework is out-of-sample in its information chronology: portfolio weights for each evaluation month are estimated using information available through the preceding estimation window and are then applied to the subsequent out-of-sample period.

## Execution

From the repository root, run:

`python src/empirical_results_pipeline.py`

The pipeline writes generated empirical outputs to the repository's `portfolio_research_output/` directory when execution is completed successfully.

The core reproducibility implementation can be executed separately when required:

`python src/portfolio_research_reproducibility.py`

## Validation

The source files should pass Python syntax compilation before execution:

`python -m py_compile src/portfolio_research_reproducibility.py`

`python -m py_compile src/empirical_results_pipeline.py`

Empirical execution requires access to the historical market data sources used by the research specification and, for the factor analysis, the specified Fama-French data source.

No numerical empirical result should be added to the repository unless it can be traced to an actual successful execution of the specified research pipeline.
