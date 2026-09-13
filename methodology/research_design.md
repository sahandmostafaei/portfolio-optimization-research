# Research Design

## Does Portfolio Optimization Add Value?

### An Out-of-Sample Analysis of Estimation Risk, Market Regimes, and Transaction Costs

---

## 1. Research Question

The central research question is:

> Does portfolio optimization add value once realistic implementation
> constraints and estimation uncertainty are incorporated into an out-of-sample
> investment framework?

The study examines whether established portfolio construction methods provide
economically meaningful benefits relative to a simple equal-weight benchmark
after accounting for:

- estimation risk;
- covariance uncertainty;
- turnover;
- transaction costs;
- market-regime variation; and
- implementation constraints.

---

## 2. Research Motivation

Modern portfolio theory provides a formal framework for allocating capital
across risky assets using expected returns, variances, and covariances.

However, these parameters are not known with certainty and must be estimated
from historical observations.

Consequently, a portfolio that appears efficient using estimated parameters
may not remain efficient when evaluated using future data.

The research therefore distinguishes between:

- theoretical portfolio efficiency;
- in-sample optimization;
- parameter estimation;
- out-of-sample performance; and
- economic implementability.

The central empirical issue is whether additional optimization complexity
generates robust value after these considerations are incorporated.

---

## 3. Hypotheses

### H1 — Out-of-Sample Optimization

Portfolio optimization does not necessarily generate superior out-of-sample
risk-adjusted performance relative to equal weighting.

### H2 — Estimation Risk

Strategies that rely more heavily on estimated parameters are more sensitive to
estimation uncertainty.

### H3 — Transaction Costs

Higher portfolio turnover reduces the economic attractiveness of optimized
portfolios after transaction costs.

### H4 — Market Regimes

The relative performance of portfolio construction strategies differs across
bull, neutral, and bear market environments.

### H5 — Covariance Shrinkage

Covariance shrinkage can improve portfolio stability by reducing sensitivity
to noisy sample covariance estimates.

---

## 4. Portfolio Strategies

Four portfolio construction strategies are evaluated.

### 4.1 Equal Weight

Each asset receives an equal portfolio allocation.

For `N` assets:

`w_i = 1 / N`

Equal weighting serves as the principal benchmark because it does not require
estimated expected returns or a covariance matrix.

Its simplicity makes it an important benchmark for assessing whether
optimization provides sufficient additional value to justify its estimation
requirements.

---

### 4.2 Global Minimum Variance

The global minimum variance portfolio solves:

`min_w w' Σ w`

subject to:

`sum_i w_i = 1`

and:

`0 <= w_i <= 0.30`

where:

- `w` is the vector of portfolio weights;
- `Σ` is the estimated covariance matrix.

The strategy attempts to minimize estimated portfolio variance subject to the
baseline implementation constraints.

---

### 4.3 Mean-Variance Optimization

The mean-variance strategy solves:

`max_w [w' μ - (γ / 2) w' Σ w]`

subject to the portfolio constraints.

Here:

- `μ` is the estimated expected-return vector;
- `Σ` is the estimated covariance matrix;
- `γ` is the risk-aversion parameter.

The baseline specification uses:

`γ = 3`

Alternative values:

`γ ∈ {1, 3, 5, 10}`

are evaluated as predefined robustness specifications.

Because both expected returns and covariances are estimated from historical
data, this strategy is particularly relevant to the study of estimation risk.

---

### 4.4 Equal Risk Contribution

The equal-risk-contribution strategy seeks to allocate portfolio risk
approximately equally across assets.

For asset `i`, the contribution to portfolio risk depends on its weight and
the covariance structure of the portfolio.

The strategy therefore focuses on risk allocation rather than expected-return
forecasting.

This provides a useful contrast with mean-variance optimization.

---

## 5. Asset Universe

The baseline universe consists of seven exchange-traded funds:

| Ticker | Exposure |
|---|---|
| SPY | U.S. equities |
| EFA | Developed-market equities excluding U.S. |
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

The purpose is to evaluate portfolio construction in a diversified multi-asset
setting rather than within a single equity market.

---

## 6. Baseline Parameters

The baseline specification is:

| Parameter | Baseline |
|---|---|
| Estimation window | 60 months |
| Rebalancing frequency | Monthly |
| Portfolio type | Long-only |
| Investment constraint | Fully invested |
| Maximum individual weight | 30% |
| Leverage | None |
| Short selling | None |
| Transaction cost | 15 bps |
| Mean-variance gamma | 3 |
| Baseline annual risk-free rate | 0% |

These parameters are fixed for the baseline comparison.

Alternative values are introduced only through explicitly identified
robustness specifications.

---

## 7. Information Timing

Avoiding look-ahead bias is a central methodological requirement.

At evaluation month `t`, all portfolio parameters must be estimated using
historical observations available no later than the end of month `t-1`.

The chronology is:

    Observations through t-1
              |
              v
       Rolling estimation
              |
              v
       Parameter estimation
              |
              v
       Portfolio optimization
              |
              v
       Portfolio weights for t
              |
              v
       Out-of-sample return during t

The return during month `t` is therefore not available when the portfolio
weights for month `t` are determined.

This chronological separation is intended to prevent look-ahead bias.

---

## 8. Rolling Estimation

The baseline estimation window contains 60 months of historical returns.

At each portfolio formation date:

1. select the preceding 60 monthly observations;
2. estimate the parameters required by each strategy;
3. construct portfolio weights;
4. apply those weights during the subsequent evaluation month;
5. record gross and net portfolio performance;
6. calculate turnover and implementation measures;
7. move the estimation window forward.

The same information-timing convention is applied across all strategies.

---

## 9. Rebalancing

The baseline strategy rebalances monthly.

At a rebalance date, turnover is defined as:

`Turnover_t = sum_i |w_i,t - w_i,t-1|`

where:

- `w_i,t` is the newly constructed portfolio weight;
- `w_i,t-1` is the previous portfolio weight.

Transaction costs are calculated as:

`TC_t = c × Turnover_t`

where the baseline transaction cost is:

`c = 0.0015`

or 15 basis points.

Net portfolio return is:

`R_t(net) = R_t(gross) - TC_t`

Transaction costs are charged only at actual rebalancing dates.

---

## 10. Initial Portfolio Convention

No transaction cost is charged on the initial portfolio formation.

This avoids introducing an arbitrary starting portfolio solely for the purpose
of calculating an initial turnover value.

From the second portfolio formation onward, turnover is measured relative to
the preceding portfolio weights.

The convention is applied consistently across strategies.

---

## 11. Return Construction

The empirical analysis uses monthly observations derived from adjusted market
prices.

The analysis should maintain a consistent return construction throughout:

    Historical adjusted prices
              |
              v
       Month-end observations
              |
              v
         Monthly returns
              |
              v
       Rolling estimation
              |
              v
    Out-of-sample evaluation

The precise data transformation should remain identical between the executable
research pipeline and the reported methodology.

---

## 12. Performance Measures

The research evaluates both returns and risk.

### 12.1 Annualized Return

For monthly observations:

`R_ann = [product(1 + R_t)]^(12/T) - 1`

---

### 12.2 Annualized Volatility

`σ_ann = σ_monthly × sqrt(12)`

---

### 12.3 Sharpe Ratio

The annualized Sharpe ratio is:

`SR = [mean(R - R_f) / σ_R] × sqrt(12)`

The baseline specification uses a 0% annual risk-free rate.

A 2% annual risk-free rate is considered as a sensitivity analysis.

---

### 12.4 Sortino Ratio

The Sortino ratio evaluates return relative to downside deviation rather than
total volatility.

The analysis uses a downside-risk framework based on returns below the
selected minimum acceptable return.

The risk-free-rate assumption is kept consistent with the corresponding
Sharpe-ratio sensitivity.

---

### 12.5 Maximum Drawdown

Maximum drawdown is defined as the largest percentage decline in cumulative
portfolio wealth from a previous peak.

---

### 12.6 Value at Risk

Historical monthly Value at Risk is estimated using the 5th percentile of
observed monthly portfolio returns.

---

### 12.7 Conditional Value at Risk

Conditional Value at Risk is estimated as the average return among observations
at or below the historical 5% VaR threshold.

---

## 13. Portfolio Concentration

Portfolio concentration is evaluated using maximum asset weight and effective
number of holdings.

The effective number of holdings is:

`N_eff = 1 / sum_i(w_i^2)`

A lower value indicates greater portfolio concentration.

These measures help distinguish raw performance from the concentration and
implementation characteristics of the portfolio.

---

## 14. Market-Regime Analysis

Market regimes are defined using trailing 12-month SPY performance.

### Bull

`R_12m(SPY) > 10%`

### Bear

`R_12m(SPY) < -10%`

### Neutral

All remaining observations.

The regime signal is shifted by one observation.

Therefore, the return during the evaluation month cannot influence the regime
classification used for that same month.

The analysis asks whether portfolio construction strategies exhibit different
performance characteristics under different market environments.

---

## 15. Estimation-Window Robustness

The baseline 60-month estimation window is compared with:

- 36 months;
- 120 months.

The purpose is to test whether conclusions depend materially on the length of
the historical estimation sample.

---

## 16. Transaction-Cost Robustness

The following transaction-cost assumptions are evaluated:

- 0 bps;
- 5 bps;
- 10 bps;
- 15 bps;
- 30 bps.

This allows the analysis to distinguish between gross performance and
performance that remains attractive after increasingly demanding
implementation assumptions.

---

## 17. Covariance Robustness

The baseline covariance matrix is estimated using the sample covariance
matrix.

A robustness specification uses the Ledoit-Wolf shrinkage estimator.

The objective is to examine whether portfolio allocation and performance are
sensitive to covariance-estimation noise.

---

## 18. Rebalancing Robustness

Monthly rebalancing is compared with quarterly rebalancing.

This tests the trade-off between:

- portfolio responsiveness;
- turnover;
- transaction costs; and
- implementation efficiency.

Quarterly rebalancing changes the timing of portfolio updates but does not
change the underlying asset universe or portfolio constraints.

---

## 19. Risk-Aversion Robustness

Mean-variance optimization is evaluated under:

`γ ∈ {1, 3, 5, 10}`

The purpose is to determine whether mean-variance results depend materially on
the chosen risk-aversion parameter.

The baseline value remains:

`γ = 3`

---

## 20. Risk-Free-Rate Sensitivity

The baseline Sharpe-ratio calculation uses a 0% annual risk-free rate.

A 2% annual risk-free rate is evaluated as a sensitivity specification.

This prevents conclusions about relative Sharpe ratios from depending entirely
on one arbitrary risk-free-rate assumption.

---

## 21. Bootstrap Inference

Moving-block bootstrap procedures are used to assess uncertainty around
performance statistics and pairwise strategy differences.

The baseline bootstrap specification uses:

- 2,000 bootstrap repetitions;
- six-month blocks;
- fixed random seed for reproducibility.

Block resampling is used because financial return observations may exhibit
temporal dependence.

Bootstrap intervals should be interpreted as measures of statistical
uncertainty rather than as evidence of causality.

---

## 22. Multiple Comparisons

The study evaluates multiple strategies and multiple robustness
specifications.

Consequently, isolated favorable findings should be interpreted cautiously.

The empirical analysis should emphasize:

- consistency across specifications;
- magnitude of economic differences;
- uncertainty around estimates;
- sensitivity to implementation assumptions.

A strategy should not be declared universally superior based on a single
favorable statistic.

---

## 23. Economic Significance

Statistical significance is not sufficient to establish investment value.

The analysis evaluates whether differences are economically meaningful after
considering:

- transaction costs;
- turnover;
- volatility;
- drawdown;
- tail risk;
- concentration;
- effective holdings;
- parameter sensitivity.

A small statistical improvement that requires substantially higher turnover
may have limited practical value.

---

## 24. Research Workflow

The intended research workflow is:

    Research question
            |
            v
    Literature review
            |
            v
    Hypotheses
            |
            v
    Research design
            |
            v
    Historical data
            |
            v
    Rolling estimation
            |
            v
    Portfolio construction
            |
            v
    Out-of-sample evaluation
            |
            v
    Transaction costs
            |
            v
    Performance analysis
            |
            v
    Robustness tests
            |
            v
    Statistical inference
            |
            v
    Economic interpretation
            |
            v
    Research conclusions

---

## 25. Research Integrity

The empirical analysis must not contain fabricated findings.

Until historical-data analysis has actually been performed, the repository
must not report numerical performance rankings or strategy conclusions as
completed empirical evidence.

The distinction between:

- planned analysis; and
- completed empirical evidence

must remain explicit.

---

## 26. Expected Research Contribution

The project is not intended to propose a new optimization algorithm.

Instead, it evaluates whether established portfolio construction methods
retain their theoretical and practical advantages under realistic conditions.

The integrated framework considers:

- estimation uncertainty;
- rolling out-of-sample evaluation;
- transaction costs;
- portfolio turnover;
- market regimes;
- covariance shrinkage;
- alternative estimation windows;
- alternative rebalancing frequencies; and
- implementation constraints.

The central contribution is therefore an empirical examination of whether
portfolio optimization produces robust economic value relative to simple
diversification.

---

## 27. Limitations

The study has several limitations.

### Asset Universe

The ETF universe is relatively small and cannot represent the full global
investment opportunity set.

### Historical Dependence

Historical backtests cannot establish that future performance will replicate
historical outcomes.

### Parameter Estimation

Expected-return and covariance estimates are inherently uncertain.

### Transaction Costs

The transaction-cost framework is simplified relative to real-world execution,
where bid-ask spreads, market impact, taxes, liquidity, and trading conditions
may vary.

### Regime Definition

The bull, neutral, and bear classifications depend on the selected SPY
thresholds and trailing-window definition.

### Model Risk

Different portfolio construction methods, covariance estimators, or parameter
choices may produce different conclusions.

These limitations should be acknowledged when interpreting the empirical
results.

---

## 28. Research Status

**Research design finalized. Empirical execution pending.**

No numerical findings should be presented as empirical conclusions until the
analysis has been executed and audited.
