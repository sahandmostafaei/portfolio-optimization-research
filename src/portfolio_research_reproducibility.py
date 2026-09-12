# Portfolio Optimization Research — Reproducibility Pipeline
#
# Research question:
# Does portfolio optimization add value after accounting for estimation risk,
# market regimes, turnover, and transaction costs?
#
# Baseline:
# - 60-month rolling estimation window
# - Monthly rebalancing
# - Long-only
# - Fully invested
# - Maximum 30% per asset
# - No leverage
# - 15 bps transaction costs
# - Strict out-of-sample t -> t+1 information timing
#
# Strategies:
# - Equal Weight
# - Global Minimum Variance
# - Mean-Variance Optimization
# - Equal Risk Contribution
#
# Robustness:
# - Estimation windows: 36 / 60 / 120 months
# - Transaction costs: 0 / 5 / 10 / 15 / 30 bps
# - Ledoit-Wolf covariance shrinkage
# - Risk-aversion parameter: 1 / 3 / 5 / 10
# - Quarterly rebalancing
# - Market-regime analysis
# - Moving-block bootstrap
#
# No empirical results are embedded in this source file.
# All numerical results must be generated from actual historical data.

from pathlib import Path
import json
import platform
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yfinance as yf
from scipy.optimize import minimize
from sklearn.covariance import LedoitWolf


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

TICKERS = [
    "SPY",
    "EFA",
    "EEM",
    "TLT",
    "GLD",
    "DBC",
    "VNQ",
]

WINDOWS = [36, 60, 120]
COSTS_BPS = [0, 5, 10, 15, 30]
GAMMAS = [1, 3, 5, 10]

MAX_WEIGHT = 0.30
BASELINE_WINDOW = 60
BASELINE_COST_BPS = 15
BASELINE_GAMMA = 3

OUTPUT_DIR = Path("portfolio_research_output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------

def get_returns():
    """
    Download adjusted historical prices and construct monthly returns.

    yfinance auto_adjust=True is used so that the price series incorporates
    applicable splits and distributions available through the data provider.
    """

    data = yf.download(
        TICKERS,
        period="max",
        auto_adjust=True,
        progress=False,
    )

    if data.empty:
        raise RuntimeError("No market data were downloaded.")

    if isinstance(data.columns, pd.MultiIndex):
        prices = data["Close"]
    else:
        prices = data

    missing = [ticker for ticker in TICKERS if ticker not in prices.columns]
    if missing:
        raise RuntimeError(
            f"Required tickers are missing from downloaded data: {missing}"
        )

    prices = prices[TICKERS].dropna(how="all")

    # Month-end observations.
    monthly_prices = prices.resample("ME").last()

    returns = monthly_prices.pct_change()

    # Require a complete observation across the research universe.
    returns = returns.dropna(how="any")

    if returns.empty:
        raise RuntimeError("No complete monthly return observations available.")

    return returns


# ---------------------------------------------------------------------------
# Portfolio constraints and basic strategies
# ---------------------------------------------------------------------------

def constraints(n_assets):
    """
    Long-only, fully invested, maximum-weight constraints.
    """

    bounds = [(0.0, MAX_WEIGHT)] * n_assets

    equality_constraint = {
        "type": "eq",
        "fun": lambda weights: np.sum(weights) - 1.0,
    }

    return bounds, equality_constraint


def equal_weight(n_assets):
    """
    Equal-weight portfolio.
    """

    return np.ones(n_assets) / n_assets


# ---------------------------------------------------------------------------
# Optimization
# ---------------------------------------------------------------------------

def optimize_portfolio(
    covariance,
    expected_returns=None,
    gamma=None,
    erc=False,
):
    """
    Optimize a long-only portfolio under the maximum-weight constraint.

    If erc=True:
        Equal Risk Contribution objective.

    If expected_returns is None:
        Global Minimum Variance objective.

    Otherwise:
        Mean-Variance objective:
            maximize mu'w - 0.5 * gamma * w'Σw
    """

    n_assets = covariance.shape[0]

    bounds, equality_constraint = constraints(n_assets)

    initial_weights = equal_weight(n_assets)

    if erc:

        def objective(weights):
            portfolio_volatility = np.sqrt(
                max(weights @ covariance @ weights, 1e-16)
            )

            risk_contributions = (
                weights * (covariance @ weights) / portfolio_volatility
            )

            return np.sum(
                (risk_contributions - risk_contributions.mean()) ** 2
            )

    elif expected_returns is None:

        def objective(weights):
            return weights @ covariance @ weights

    else:

        if gamma is None or gamma <= 0:
            raise ValueError("gamma must be positive for mean-variance optimization.")

        def objective(weights):
            portfolio_return = weights @ expected_returns
            portfolio_variance = weights @ covariance @ weights

            return -(
                portfolio_return
                - 0.5 * gamma * portfolio_variance
            )

    result = minimize(
        objective,
        initial_weights,
        method="SLSQP",
        bounds=bounds,
        constraints=equality_constraint,
        options={
            "maxiter": 2000,
            "ftol": 1e-13,
        },
    )

    if not result.success:
        raise RuntimeError(
            f"Portfolio optimization failed: {result.message}"
        )

    weights = np.asarray(result.x, dtype=float)

    # Numerical cleanup.
    weights[weights < 0] = 0.0

    total = weights.sum()

    if total <= 0:
        raise RuntimeError("Optimization produced invalid portfolio weights.")

    weights /= total

    if np.max(weights) > MAX_WEIGHT + 1e-6:
        raise RuntimeError("Portfolio violates maximum-weight constraint.")

    return weights


def make_weights(
    training_returns,
    gamma=BASELINE_GAMMA,
    shrink=False,
):
    """
    Estimate expected returns and covariance using only the training window.
    """

    expected_returns = training_returns.mean().values

    if shrink:
        covariance = LedoitWolf().fit(
            training_returns.values
        ).covariance_
    else:
        covariance = training_returns.cov().values

    return {
        "EW": equal_weight(len(TICKERS)),
        "MINVAR": optimize_portfolio(covariance),
        "MV": optimize_portfolio(
            covariance,
            expected_returns=expected_returns,
            gamma=gamma,
        ),
        "ERC": optimize_portfolio(
            covariance,
            erc=True,
        ),
    }


# ---------------------------------------------------------------------------
# Backtest
# ---------------------------------------------------------------------------

def run_backtest(
    returns,
    window=BASELINE_WINDOW,
    cost_bps=BASELINE_COST_BPS,
    gamma=BASELINE_GAMMA,
    shrink=False,
    rebalance_step=1,
):
    """
    Run an out-of-sample portfolio backtest.

    Information timing:
        training data end immediately before the evaluation month.

    For example, at evaluation month t, the estimation window consists of
    observations ending at t-1.

    Transaction costs are charged only when a rebalance actually occurs.

    Initial portfolio formation is not charged a transaction cost because
    there is no arbitrary pre-existing portfolio against which to measure
    turnover.
    """

    if window <= 0:
        raise ValueError("window must be positive.")

    if rebalance_step <= 0:
        raise ValueError("rebalance_step must be positive.")

    if len(returns) <= window:
        raise ValueError(
            "Insufficient observations for the requested estimation window."
        )

    strategies = ["EW", "MINVAR", "MV", "ERC"]

    previous_weights = {
        strategy: equal_weight(len(TICKERS))
        for strategy in strategies
    }

    rows = []

    for i in range(window, len(returns)):

        # Rebalance at the baseline frequency.
        is_rebalance_month = ((i - window) % rebalance_step) == 0

        if is_rebalance_month:
            training_returns = returns.iloc[i - window:i]

            current_weights = make_weights(
                training_returns,
                gamma=gamma,
                shrink=shrink,
            )
        else:
            current_weights = previous_weights

        evaluation_returns = returns.iloc[i]

        for strategy, weights in current_weights.items():

            if is_rebalance_month:
                turnover = float(
                    np.abs(weights - previous_weights[strategy]).sum()
                )
            else:
                turnover = 0.0

            gross_return = float(
                evaluation_returns.values @ weights
            )

            transaction_cost = (
                cost_bps / 10000.0
            ) * turnover

            net_return = gross_return - transaction_cost

            rows.append(
                [
                    returns.index[i],
                    strategy,
                    gross_return,
                    net_return,
                    turnover,
                    transaction_cost,
                    is_rebalance_month,
                    *weights,
                ]
            )

        previous_weights = current_weights

    columns = [
        "date",
        "strategy",
        "gross",
        "net",
        "turnover",
        "transaction_cost",
        "rebalance",
        *TICKERS,
    ]

    output = pd.DataFrame(rows, columns=columns)

    return output.set_index("date")


# ---------------------------------------------------------------------------
# Performance statistics
# ---------------------------------------------------------------------------

def sharpe_ratio(returns, annual_risk_free_rate=0.0):
    """
    Annualized Sharpe ratio using monthly observations.
    """

    if len(returns) < 2:
        return np.nan

    monthly_rf = annual_risk_free_rate / 12.0

    excess_returns = returns - monthly_rf

    volatility = excess_returns.std(ddof=1)

    if volatility == 0 or pd.isna(volatility):
        return np.nan

    return np.sqrt(12.0) * excess_returns.mean() / volatility


def maximum_drawdown(returns):
    """
    Maximum drawdown from a monthly return series.
    """

    wealth = (1.0 + returns).cumprod()

    running_maximum = wealth.cummax()

    drawdown = wealth / running_maximum - 1.0

    return float(drawdown.min())


def annualized_return(returns):
    """
    Compound annualized return.
    """

    if len(returns) == 0:
        return np.nan

    total_growth = (1.0 + returns).prod()

    return total_growth ** (12.0 / len(returns)) - 1.0


def annualized_volatility(returns):
    """
    Annualized volatility from monthly returns.
    """

    if len(returns) < 2:
        return np.nan

    return returns.std(ddof=1) * np.sqrt(12.0)


def sortino_ratio(returns, annual_risk_free_rate=0.0):
    """
    Annualized Sortino ratio using monthly downside deviation.
    """

    if len(returns) == 0:
        return np.nan

    monthly_rf = annual_risk_free_rate / 12.0
    excess_returns = returns - monthly_rf

    downside = np.minimum(excess_returns.values, 0.0)

    downside_deviation = np.sqrt(
        np.mean(downside ** 2)
    ) * np.sqrt(12.0)

    if downside_deviation == 0:
        return np.nan

    return (
        excess_returns.mean() * 12.0
    ) / downside_deviation


def value_at_risk(returns, probability=0.05):
    """
    Historical monthly VaR quantile.
    """

    if len(returns) == 0:
        return np.nan

    return float(returns.quantile(probability))


def conditional_value_at_risk(returns, probability=0.05):
    """
    Historical monthly CVaR.

    Defined as the mean return among observations at or below the
    historical VaR threshold.
    """

    if len(returns) == 0:
        return np.nan

    var_threshold = returns.quantile(probability)

    tail = returns[returns <= var_threshold]

    if tail.empty:
        return np.nan

    return float(tail.mean())


def effective_holdings(weight_data):
    """
    Effective number of holdings:

        1 / sum(w_i^2)

    Calculated for each observation and then averaged.
    """

    if weight_data.empty:
        return np.nan

    concentration = (
        weight_data ** 2
    ).sum(axis=1)

    return float(
        (1.0 / concentration).mean()
    )


# ---------------------------------------------------------------------------
# Summary statistics
# ---------------------------------------------------------------------------

def performance_summary(output):
    """
    Generate the main performance summary table.
    """

    records = []

    for strategy, group in output.groupby("strategy"):

        returns = group["net"].dropna()

        if returns.empty:
            continue

        rebalance_turnover = group.loc[
            group["rebalance"],
            "turnover",
        ]

        records.append(
            [
                strategy,
                annualized_return(returns),
                annualized_volatility(returns),
                sharpe_ratio(returns, 0.00),
                sharpe_ratio(returns, 0.02),
                sortino_ratio(returns, 0.00),
                maximum_drawdown(returns),
                value_at_risk(returns, 0.05),
                conditional_value_at_risk(returns, 0.05),
                returns.skew(),
                returns.kurt(),
                group["turnover"].mean(),
                (
                    rebalance_turnover.mean()
                    if not rebalance_turnover.empty
                    else 0.0
                ),
                group["transaction_cost"].sum(),
                group[TICKERS].max().max(),
                effective_holdings(group[TICKERS]),
            ]
        )

    columns = [
        "strategy",
        "ann_return",
        "ann_vol",
        "sharpe_rf0",
        "sharpe_rf2",
        "sortino_rf0",
        "max_drawdown",
        "VaR_5pct_monthly",
        "CVaR_5pct_monthly",
        "skewness",
        "excess_kurtosis",
        "avg_monthly_turnover",
        "avg_rebalance_turnover",
        "total_transaction_cost",
        "max_weight",
        "effective_holdings",
    ]

    return pd.DataFrame(
        records,
        columns=columns,
    ).set_index("strategy")


# ---------------------------------------------------------------------------
# Moving-block bootstrap
# ---------------------------------------------------------------------------

def moving_block_bootstrap(
    observations,
    statistic,
    bootstrap_repetitions=2000,
    block_length=6,
    seed=42,
):
    """
    Moving-block bootstrap confidence interval.

    The block structure partially preserves serial dependence in monthly
    financial return observations.
    """

    observations = np.asarray(observations, dtype=float)

    observations = observations[
        np.isfinite(observations)
    ]

    n = len(observations)

    if n < 2:
        return np.array([np.nan, np.nan, np.nan])

    rng = np.random.default_rng(seed)

    bootstrap_values = []

    number_of_blocks = int(
        np.ceil(n / block_length)
    )

    for _ in range(bootstrap_repetitions):

        starts = rng.integers(
            0,
            n,
            size=number_of_blocks,
        )

        sampled_indices = []

        for start in starts:
            block_indices = (
                np.arange(start, start + block_length)
                % n
            )

            sampled_indices.extend(block_indices.tolist())

        sampled_indices = sampled_indices[:n]

        sample = observations[sampled_indices]

        bootstrap_values.append(
            statistic(sample)
        )

    return np.quantile(
        bootstrap_values,
        [0.025, 0.50, 0.975],
    )


# ---------------------------------------------------------------------------
# Regime analysis
# ---------------------------------------------------------------------------

def build_market_regimes(returns):
    """
    Classify market regimes using trailing 12-month SPY performance.

    The regime signal is shifted by one month so that the label assigned to
    evaluation month t only uses information available before month t.
    """

    spy_returns = returns["SPY"]

    trailing_12m_return = (
        (1.0 + spy_returns)
        .rolling(12)
        .apply(np.prod, raw=True)
        - 1.0
    )

    signal = trailing_12m_return.shift(1)

    regimes = pd.Series(
        "Neutral",
        index=returns.index,
        dtype="object",
    )

    regimes.loc[signal > 0.10] = "Bull"
    regimes.loc[signal < -0.10] = "Bear"

    return regimes


def regime_analysis(backtest_output, returns):
    """
    Calculate performance by strategy and market regime.
    """

    regimes = build_market_regimes(returns)

    output = backtest_output.copy()

    output["regime"] = regimes.reindex(
        output.index
    ).values

    records = []

    for (strategy, regime), group in output.groupby(
        ["strategy", "regime"]
    ):

        series = group["net"].dropna()

        if series.empty:
            continue

        records.append(
            [
                strategy,
                regime,
                len(series),
                annualized_return(series),
                sharpe_ratio(series),
                maximum_drawdown(series),
            ]
        )

    return pd.DataFrame(
        records,
        columns=[
            "strategy",
            "regime",
            "months",
            "ann_return",
            "sharpe",
            "max_drawdown",
        ],
    )


# ---------------------------------------------------------------------------
# Main empirical pipeline
# ---------------------------------------------------------------------------

def main():

    print("Downloading historical market data...")

    returns = get_returns()

    returns.to_csv(
        OUTPUT_DIR / "monthly_returns.csv"
    )

    print(
        f"Data period: {returns.index.min()} "
        f"to {returns.index.max()}"
    )

    print(
        f"Monthly observations: {len(returns)}"
    )

    # -----------------------------------------------------------------------
    # Baseline
    # -----------------------------------------------------------------------

    print("Running baseline backtest...")

    baseline = run_backtest(
        returns,
        window=BASELINE_WINDOW,
        cost_bps=BASELINE_COST_BPS,
        gamma=BASELINE_GAMMA,
        shrink=False,
        rebalance_step=1,
    )

    performance_summary(
        baseline
    ).to_csv(
        OUTPUT_DIR / "baseline_performance.csv"
    )

    # -----------------------------------------------------------------------
    # Estimation-window robustness
    # -----------------------------------------------------------------------

    print("Running estimation-window robustness tests...")

    for window in WINDOWS:

        result = run_backtest(
            returns,
            window=window,
            cost_bps=BASELINE_COST_BPS,
            gamma=BASELINE_GAMMA,
            shrink=False,
            rebalance_step=1,
        )

        performance_summary(
            result
        ).to_csv(
            OUTPUT_DIR / f"window_{window}.csv"
        )

    # -----------------------------------------------------------------------
    # Transaction-cost robustness
    # -----------------------------------------------------------------------

    print("Running transaction-cost robustness tests...")

    for cost_bps in COSTS_BPS:

        result = run_backtest(
            returns,
            window=BASELINE_WINDOW,
            cost_bps=cost_bps,
            gamma=BASELINE_GAMMA,
            shrink=False,
            rebalance_step=1,
        )

        performance_summary(
            result
        ).to_csv(
            OUTPUT_DIR / f"cost_{cost_bps}bps.csv"
        )

    # -----------------------------------------------------------------------
    # Mean-variance risk-aversion robustness
    # -----------------------------------------------------------------------

    print("Running risk-aversion robustness tests...")

    for gamma in GAMMAS:

        result = run_backtest(
            returns,
            window=BASELINE_WINDOW,
            cost_bps=BASELINE_COST_BPS,
            gamma=gamma,
            shrink=False,
            rebalance_step=1,
        )

        performance_summary(
            result
        ).to_csv(
            OUTPUT_DIR / f"gamma_{gamma}.csv"
        )

    # -----------------------------------------------------------------------
    # Covariance shrinkage
    # -----------------------------------------------------------------------

    print("Running Ledoit-Wolf covariance robustness test...")

    shrinkage_result = run_backtest(
        returns,
        window=BASELINE_WINDOW,
        cost_bps=BASELINE_COST_BPS,
        gamma=BASELINE_GAMMA,
        shrink=True,
        rebalance_step=1,
    )

    performance_summary(
        shrinkage_result
    ).to_csv(
        OUTPUT_DIR / "ledoit_wolf.csv"
    )

    # -----------------------------------------------------------------------
    # Quarterly rebalancing
    # -----------------------------------------------------------------------

    print("Running quarterly-rebalancing robustness test...")

    quarterly_result = run_backtest(
        returns,
        window=BASELINE_WINDOW,
        cost_bps=BASELINE_COST_BPS,
        gamma=BASELINE_GAMMA,
        shrink=False,
        rebalance_step=3,
    )

    performance_summary(
        quarterly_result
    ).to_csv(
        OUTPUT_DIR / "quarterly_rebalance.csv"
    )

    # -----------------------------------------------------------------------
    # Market regimes
    # -----------------------------------------------------------------------

    print("Running market-regime analysis...")

    regime_result = regime_analysis(
        baseline,
        returns,
    )

    regime_result.to_csv(
        OUTPUT_DIR / "regime_performance.csv",
        index=False,
    )

    # -----------------------------------------------------------------------
    # Bootstrap confidence intervals
    # -----------------------------------------------------------------------

    print("Running moving-block bootstrap...")

    return_matrix = baseline.pivot_table(
        index=baseline.index,
        columns="strategy",
        values="net",
    ).dropna()

    bootstrap_sharpe = {}

    for strategy in return_matrix.columns:

        bootstrap_sharpe[strategy] = moving_block_bootstrap(
            return_matrix[strategy].values,
            sharpe_ratio,
        )

    pd.DataFrame(
        bootstrap_sharpe,
        index=[
            "lower_95",
            "median",
            "upper_95",
        ],
    ).T.to_csv(
        OUTPUT_DIR / "bootstrap_sharpe_ci.csv"
    )

    # Pairwise Sharpe-difference bootstrap.
    pairwise_results = {}

    strategies = list(
        return_matrix.columns
    )

    for i, strategy_a in enumerate(strategies):

        for strategy_b in strategies[i + 1:]:

            difference = (
                return_matrix[strategy_a]
                - return_matrix[strategy_b]
            )

            pairwise_results[
                f"{strategy_a}-{strategy_b}"
            ] = moving_block_bootstrap(
                difference.values,
                sharpe_ratio,
            )

    pd.DataFrame(
        pairwise_results,
        index=[
            "lower_95",
            "median",
            "upper_95",
        ],
    ).T.to_csv(
        OUTPUT_DIR / "bootstrap_pairwise_sharpe_difference.csv"
    )

    # -----------------------------------------------------------------------
    # Cumulative wealth figures
    # -----------------------------------------------------------------------

    print("Generating figures...")

    for strategy, group in baseline.groupby("strategy"):

        wealth = (
            1.0 + group["net"]
        ).cumprod()

        plt.figure(
            figsize=(8, 4.5)
        )

        wealth.plot()

        plt.title(
            f"Cumulative Net Wealth — {strategy}"
        )

        plt.ylabel(
            "Growth of $1"
        )

        plt.xlabel(
            "Date"
        )

        plt.tight_layout()

        plt.savefig(
            OUTPUT_DIR / f"wealth_{strategy}.png",
            dpi=180,
        )

        plt.close()

    # -----------------------------------------------------------------------
    # Provenance metadata
    # -----------------------------------------------------------------------

    metadata = {
        "python": sys.version,
        "platform": platform.platform(),
        "tickers": TICKERS,
        "sample_start": str(returns.index.min()),
        "sample_end": str(returns.index.max()),
        "monthly_observations": int(len(returns)),
        "baseline": {
            "window_months": BASELINE_WINDOW,
            "transaction_cost_bps": BASELINE_COST_BPS,
            "mean_variance_gamma": BASELINE_GAMMA,
            "maximum_weight": MAX_WEIGHT,
            "rebalance_frequency": "monthly",
            "long_only": True,
            "fully_invested": True,
            "leverage": False,
            "short_selling": False,
            "information_timing": (
                "weights at evaluation month t use observations "
                "ending at t-1"
            ),
            "initial_turnover_charged": False,
        },
        "regime_definition": {
            "bull": "Trailing 12-month SPY return > +10%",
            "bear": "Trailing 12-month SPY return < -10%",
            "neutral": "Otherwise",
            "information_timing": (
                "Regime signal shifted one month before evaluation"
            ),
        },
        "bootstrap": {
            "method": "moving block bootstrap",
            "block_length_months": 6,
            "repetitions": 2000,
            "seed": 42,
        },
    }

    with open(
        OUTPUT_DIR / "provenance.json",
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            metadata,
            file,
            indent=2,
        )

    print()
    print("Research pipeline completed successfully.")
    print(
        f"Outputs written to: {OUTPUT_DIR.resolve()}"
    )


if __name__ == "__main__":
    main()
