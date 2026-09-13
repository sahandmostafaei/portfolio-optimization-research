# Research Integrity

## Purpose

This document defines the research-integrity standards governing the
portfolio optimization research project.

The objective is to maintain a clear distinction between:

- proposed research design;
- executed empirical analysis;
- observed empirical findings; and
- interpretation of results.

The project must not present planned analysis as completed empirical evidence.

---

## 1. No Fabricated Results

No empirical result, performance statistic, table, figure, confidence
interval, or research conclusion should be presented as an observed finding
unless it has been generated from actual historical data through the stated
research methodology.

The repository therefore distinguishes between:

- research questions;
- hypotheses;
- research design;
- executable analysis code;
- empirical data;
- empirical outputs; and
- interpretation.

A numerical result must not be inserted into the manuscript merely because it
would make the research appear more complete or persuasive.

---

## 2. Research Status

The project is an independent research study.

The research design has been specified, but empirical execution and auditing
are separate stages of the research process.

The repository must not describe the study as:

- published;
- peer-reviewed;
- accepted for publication;
- institutionally supervised;
- externally validated;

unless such a status actually exists.

The project should be presented as independent quantitative finance research.

---

## 3. Information Timing

Preventing look-ahead bias is a central methodological requirement.

At evaluation month `t`, all parameters and portfolio weights must be
constructed using information available no later than the end of the preceding
observation period, `t-1`.

The intended chronology is:

    Information through t-1
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
    Out-of-sample return during t

The return observed during month `t` must not influence the portfolio weights
used to evaluate month `t`.

---

## 4. Rolling Estimation

The baseline estimation window contains 60 months of historical observations.

The estimation window rolls forward through time.

Alternative estimation windows of:

- 36 months; and
- 120 months

are predefined robustness specifications.

These alternatives should not be selected after observing which specification
produces the most favorable result.

---

## 5. Portfolio Construction

The baseline portfolio framework imposes:

- long-only positions;
- full investment;
- maximum 30% weight per asset;
- no leverage;
- no short selling.

These constraints apply consistently across the baseline strategy comparison.

If a robustness experiment changes a constraint, the change must be explicitly
identified as a separate specification.

---

## 6. Transaction Costs

The baseline transaction-cost assumption is 15 basis points.

Transaction costs are proportional to portfolio turnover.

Turnover is measured at actual portfolio rebalancing dates according to:

`Turnover_t = sum_i |w_i,t - w_i,t-1|`

Transaction costs are then:

`TC_t = c × Turnover_t`

where the baseline cost is:

`c = 0.0015`

or 15 basis points.

Transaction costs must be charged only when portfolio weights are actually
changed through a scheduled rebalance.

Months without a rebalance should not generate an artificial transaction-cost
charge.

---

## 7. Initial Portfolio Convention

The initial portfolio formation does not receive an arbitrary transaction-cost
charge.

This avoids defining an artificial pre-existing portfolio solely to calculate
initial turnover.

From the second portfolio formation onward, turnover is measured relative to
the preceding portfolio weights.

The convention should remain consistent across strategies.

---

## 8. Robustness and Specification Discipline

The research includes predefined robustness tests covering:

- estimation-window length;
- transaction costs;
- covariance estimation;
- risk-aversion parameters;
- rebalancing frequency;
- market regimes;
- risk-free-rate assumptions;
- bootstrap inference.

Robustness analysis must not be used selectively to report only favorable
specifications.

If conclusions vary materially across specifications, that variation is itself
important empirical evidence and should be reported.

---

## 9. Statistical Inference

Performance differences should not be interpreted as economically or
statistically meaningful solely because one strategy has a higher point
estimate.

Where appropriate, the analysis should distinguish:

- point estimates;
- confidence intervals;
- economic significance;
- statistical significance.

Bootstrap procedures may be used to quantify uncertainty around performance
statistics and pairwise strategy comparisons.

The bootstrap should not be interpreted as proof of causality.

---

## 10. Multiple Comparisons

The project compares several strategies across multiple parameter
specifications.

This creates a risk that apparently favorable results arise from sampling
variation or specification selection.

The research should therefore emphasize:

- predefined specifications;
- consistency across robustness tests;
- transparent reporting of unfavorable results;
- cautious interpretation of isolated statistical findings.

A single favorable result should not be presented as decisive evidence when
other reasonable specifications produce materially different conclusions.

---

## 11. Data Integrity

The empirical analysis should document:

- data source;
- asset universe;
- sampling frequency;
- price or return construction;
- missing observations;
- estimation window;
- evaluation period;
- parameter assumptions;
- portfolio constraints;
- transaction-cost assumptions.

Data transformations should be reproducible from the research code and
consistent with the documented methodology.

---

## 12. Return Construction

The research should state clearly whether the analysis uses:

- adjusted prices;
- total returns;
- price returns; or
- another explicitly defined return measure.

The return definition must remain consistent between:

- the methodology;
- the source code;
- the empirical results; and
- the manuscript.

No return convention should be changed silently after observing empirical
results.

---

## 13. Market-Regime Classification

The baseline regime classification uses trailing 12-month SPY performance:

- Bull: above +10%;
- Neutral: between -10% and +10%;
- Bear: below -10%.

The regime signal must be lagged so that the evaluation-period return does not
enter the classification used for that same evaluation period.

The regime definition is a methodological choice, not an established
universal classification.

Results should therefore be interpreted conditionally on this specification.

---

## 14. Researcher Degrees of Freedom

Parameter choices should be specified before evaluating their empirical
consequences wherever practical.

If a methodological decision is changed after observing results, the change
must be documented and its rationale explained.

Post-hoc specification changes must not be presented as though they were part
of the original baseline research design.

---

## 15. Economic Interpretation

A strategy must not be described as superior merely because it produces a
higher historical return.

Performance should be considered jointly with:

- volatility;
- Sharpe ratio;
- Sortino ratio;
- maximum drawdown;
- tail risk;
- turnover;
- transaction costs;
- concentration;
- effective holdings;
- parameter sensitivity.

A statistically detectable difference may still have limited economic value if
the magnitude is small or implementation costs are substantial.

---

## 16. Hypothesis Evaluation

Results should be interpreted relative to the hypotheses established before
empirical evaluation.

The analysis should distinguish among:

### Evidence Supporting a Hypothesis

Observed results are broadly consistent with the predicted relationship.

### Evidence Inconsistent with a Hypothesis

Observed results materially contradict the predicted relationship.

### Inconclusive Evidence

The data do not provide sufficiently strong evidence in either direction.

The language of the conclusions should reflect the strength of the evidence.

---

## 17. Reproducibility

A reported empirical result should be traceable to:

1. the research question;
2. the literature foundation;
3. the methodology;
4. the source code;
5. the input data;
6. the parameter assumptions;
7. the execution procedure; and
8. the resulting output.

A reader should be able to understand how a reported empirical conclusion was
produced without relying on undocumented manual calculations.

---

## 18. Separation of Research Components

The repository intentionally separates:

    Research question
            |
            v
    Literature
            |
            v
    Methodology
            |
            v
    Source code
            |
            v
    Empirical data
            |
            v
    Results
            |
            v
    Interpretation
            |
            v
    Conclusion

This separation reduces the risk that methodological assumptions become
hidden inside empirical results or that results are interpreted independently
of the original research design.

---

## 19. Academic Honesty

The project should not imply:

- institutional affiliation;
- academic supervision;
- publication;
- peer review;
- external validation;
- professional investment-management status;

unless these statements are factually accurate.

The work should be presented as independent research.

Its purpose is to demonstrate:

- quantitative finance knowledge;
- empirical research design;
- statistical reasoning;
- methodological discipline;
- financial interpretation; and
- reproducibility.

---

## 20. Research Status Statement

Until empirical execution has been completed and audited, the repository should
use the following status:

> **Research design finalized. Empirical execution pending.**

After execution, the status may be updated to reflect the actual stage of the
research.

Any empirical conclusion added to the paper must correspond to an auditable
output from the research pipeline.
