# Research Integrity

## Purpose

This document defines the integrity standards used in this independent
portfolio optimization research project.

## No Fabricated Results

No empirical result, performance statistic, figure, table, or conclusion is
reported unless it has been generated from the stated research pipeline using
historical market data.

The repository deliberately distinguishes between:

- research design;
- executable analysis code;
- empirical outputs;
- interpretation of results.

Until the empirical pipeline has been executed and audited, numerical findings
must not be presented as research findings.

## Information Timing

Portfolio weights at evaluation date `t` may use only information available
through date `t`.

Portfolio returns are evaluated over the subsequent period `t+1`.

This prevents look-ahead bias in the baseline backtest.

## Transaction Costs

Transaction costs are applied proportionally to portfolio turnover at actual
rebalance dates.

The baseline transaction-cost assumption is 15 basis points.

No transaction cost is charged at the initial portfolio formation unless
explicitly stated in the empirical design.

## Out-of-Sample Evaluation

The empirical analysis uses rolling historical estimation windows and evaluates
subsequent portfolio performance out of sample.

The baseline estimation window is 60 months.

Alternative estimation windows are treated as robustness tests rather than
being selected after observing performance.

## Robustness

The study evaluates sensitivity to:

- estimation-window length;
- transaction costs;
- rebalancing frequency;
- covariance estimation;
- risk-aversion assumptions;
- market regimes;
- risk-free-rate assumptions.

Results should not be interpreted as robust merely because one specification
produces a favorable outcome.

## Reproducibility

All reported empirical results should be traceable to:

1. the research design;
2. the source code;
3. the input data;
4. the specified parameters;
5. the generated outputs.

Any material change to the methodology should be documented before results
are presented as final.

## Research Status

This is independent research. It is not presented as peer-reviewed or
published academic research unless that status is independently established.
