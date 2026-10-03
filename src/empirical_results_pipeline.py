"""Audited empirical-results pipeline.

Run from repository root:
    python src/empirical_results_pipeline.py

This layer deliberately owns the backtest accounting, performance metrics,
bootstrap inference, regime construction, validation, and provenance. The
repository's optimizer/data-loader remain the only upstream dependencies.
"""
from pathlib import Path
import io, json, platform, sys, zipfile, hashlib
from datetime import datetime, timezone
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
import requests

from portfolio_research_reproducibility import (
    TICKERS, WINDOWS, COSTS_BPS, GAMMAS, BASELINE_WINDOW,
    BASELINE_COST_BPS, BASELINE_GAMMA, MAX_WEIGHT,
    BOOTSTRAP_REPETITIONS, BOOTSTRAP_BLOCK_LENGTH, BOOTSTRAP_SEED,
    get_returns, make_weights,
)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "portfolio_research_output"
FIG = OUT / "figures"
OUT.mkdir(exist_ok=True)
FIG.mkdir(exist_ok=True)
STRATEGIES = ["EW", "MINVAR", "MV", "ERC"]
OPTIMIZED = ["MINVAR", "MV", "ERC"]
HAC_LAGS = 6
FF5_URL = "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Research_Data_5_Factors_2x3_CSV.zip"


def _assert_weights(w, tol=1e-8):
    w = np.asarray(w, dtype=float)
    if w.ndim != 1 or len(w) != len(TICKERS) or not np.isfinite(w).all():
        raise AssertionError("Invalid portfolio weights.")
    if abs(w.sum() - 1.0) > tol:
        raise AssertionError("Portfolio weights do not sum to one.")
    if (w < -tol).any():
        raise AssertionError("Negative portfolio weight detected.")
    if (w > MAX_WEIGHT + tol).any():
        raise AssertionError("Target portfolio exceeds MAX_WEIGHT.")


def validate_monthly_returns(r):
    """Reject malformed/incomplete data before any statistical calculation."""
    r = r.copy()
    if not isinstance(r.index, pd.DatetimeIndex):
        r.index = pd.to_datetime(r.index)
    r = r.sort_index()
    if r.index.has_duplicates:
        raise AssertionError("Duplicate return dates.")
    missing_cols = [c for c in TICKERS if c not in r.columns]
    if missing_cols:
        raise AssertionError(f"Missing tickers: {missing_cols}")
    r = r[TICKERS].apply(pd.to_numeric, errors="coerce")
    if r.isna().any().any() or not np.isfinite(r.to_numpy()).all():
        raise AssertionError("Monthly return matrix contains NaN/inf values.")
    periods = r.index.to_period("M")
    if len(periods) and not periods.is_monotonic_increasing:
        raise AssertionError("Return dates are not ordered.")
    expected = pd.period_range(periods.min(), periods.max(), freq="M")
    if len(periods) != len(expected) or not periods.equals(expected):
        raise AssertionError("Monthly return series contains gaps; HAC inference requires consecutive observations.")
    # Never use a partial current calendar month.
    current_period = pd.Timestamp.now(tz="UTC").to_period("M")
    if len(r) and periods[-1] == current_period:
        r = r.iloc[:-1]
    if len(r) <= max(WINDOWS):
        raise AssertionError("Insufficient observations for the largest estimation window.")
    return r


def annualized_return(x):
    x = pd.Series(x).dropna().astype(float)
    if len(x) == 0 or (1.0 + x <= 0).any():
        return np.nan
    return float(np.prod(1.0 + x) ** (12.0 / len(x)) - 1.0)


def annualized_volatility(x):
    x = pd.Series(x).dropna().astype(float)
    return float(x.std(ddof=1) * np.sqrt(12.0)) if len(x) > 1 else np.nan


def zero_rf_sharpe(x):
    x = pd.Series(x).dropna().astype(float)
    if len(x) < 2:
        return np.nan
    s = x.std(ddof=1)
    return float(np.sqrt(12.0) * x.mean() / s) if s > 0 else np.nan


def rf2_sharpe(x):
    """Annualized Sharpe ratio using a fixed 2% annual risk-free benchmark."""
    x = pd.Series(x).dropna().astype(float)
    if len(x) < 2:
        return np.nan
    monthly_rf = 0.02 / 12.0
    excess = x - monthly_rf
    s = excess.std(ddof=1)
    return float(np.sqrt(12.0) * excess.mean() / s) if s > 0 else np.nan


def maximum_drawdown(x):
    x = pd.Series(x).dropna().astype(float)
    if len(x) == 0 or (1.0 + x <= 0).any():
        return np.nan
    wealth = (1.0 + x).cumprod()
    return float((wealth / wealth.cummax() - 1.0).min())


def performance_summary(bt):
    rows = []
    for s, g in bt.groupby("strategy", sort=False):
        x = g["net"]
        rows.append([
            s, annualized_return(x), annualized_volatility(x), zero_rf_sharpe(x),
            rf2_sharpe(x), maximum_drawdown(x), float(g["turnover"].mean()),
            float(g.loc[g["rebalance"], "turnover"].mean()) if g["rebalance"].any() else 0.0,
            float(g["transaction_cost_rate"].sum()), float(g.loc[g["rebalance"], "target_max_weight"].max()) if g["rebalance"].any() else np.nan,
            float(g["realized_max_weight"].max()), int(len(g)),
        ])
    return pd.DataFrame(rows, columns=[
        "strategy", "ann_return", "ann_vol", "sharpe_zero_rf", "sharpe_rf2", "max_drawdown",
        "avg_monthly_turnover", "avg_rebalance_turnover", "cumulative_transaction_cost_rate",
        "max_target_weight", "max_realized_weight", "n_months"
    ]).set_index("strategy")


def pivot(bt, value="net"):
    return bt.pivot_table(index=bt.index, columns="strategy", values=value).sort_index()


def audited_backtest(returns, window, cost_bps, gamma, shrink=False, rebalance_step=1):
    """Strict rolling OOS backtest with actual drifted pre-trade holdings."""
    if window <= 0 or len(returns) <= window:
        raise ValueError("Invalid estimation window or insufficient observations.")
    if cost_bps < 0 or rebalance_step <= 0:
        raise ValueError("Invalid transaction cost or rebalance step.")

    previous_post_return = {s: None for s in STRATEGIES}
    rows = []
    for i in range(window, len(returns)):
        rebalance = ((i - window) % rebalance_step == 0)
        training = returns.iloc[i-window:i]
        targets = make_weights(training, gamma=gamma, shrink=shrink) if rebalance else None
        r_t = returns.iloc[i].to_numpy(dtype=float)
        if not np.isfinite(r_t).all():
            raise AssertionError("Non-finite OOS return encountered.")

        if targets is not None:
            for s in STRATEGIES:
                _assert_weights(targets[s])

        for s in STRATEGIES:
            if previous_post_return[s] is None:
                if targets is None:
                    raise AssertionError("First OOS observation must be a rebalance date.")
                target = np.asarray(targets[s], dtype=float).copy()
                pretrade = target.copy()
                turnover = 0.0  # starting portfolio is treated as already funded
                weights = target.copy()
            elif rebalance:
                pretrade = previous_post_return[s]
                weights = np.asarray(targets[s], dtype=float).copy()
                turnover = float(np.abs(weights - pretrade).sum())
            else:
                pretrade = previous_post_return[s]
                weights = pretrade.copy()
                turnover = 0.0

            gross = float(r_t @ weights)
            cost_rate = float(cost_bps / 10000.0 * turnover)
            if 1.0 + gross <= 0:
                raise RuntimeError("Gross portfolio return implies non-positive wealth.")
            if cost_rate < 0 or cost_rate >= 1.0:
                raise RuntimeError("Transaction cost rate must be in [0,1) for positive investable wealth.")

            # Exact beginning-of-period rebalancing convention:
            # transaction cost is paid from wealth immediately before the
            # month's market return. Thus 1 + net = (1 + gross) * (1 - cost_rate).
            net = (1.0 + gross) * (1.0 - cost_rate) - 1.0
            net_valid = bool(1.0 + net > 0)

            post = weights * (1.0 + r_t) / (1.0 + gross)
            if not np.isfinite(post).all() or abs(post.sum() - 1.0) > 1e-8:
                raise RuntimeError("Invalid post-return holdings.")
            if (post < -1e-8).any():
                raise RuntimeError("Post-return holdings became negative.")

            realized_max = float(post.max())
            previous_post_return[s] = post
            target_max = float(weights.max()) if rebalance else np.nan
            rows.append([
                returns.index[i], s, gross, net, turnover, cost_rate, rebalance,
                net_valid, target_max, realized_max, *weights
            ])

    cols = ["date", "strategy", "gross", "net", "turnover", "transaction_cost_rate",
            "rebalance", "net_wealth_valid", "target_max_weight", "realized_max_weight", *TICKERS]
    return pd.DataFrame(rows, columns=cols).set_index("date")


def hac_mean_test(x):
    x = pd.Series(x).dropna().astype(float)
    if len(x) < max(12, HAC_LAGS + 2):
        return len(x), np.nan, np.nan, np.nan
    m = sm.OLS(x.to_numpy(), np.ones(len(x))).fit(
        cov_type="HAC", cov_kwds={"maxlags": min(HAC_LAGS, len(x) - 2)}
    )
    return len(x), float(x.mean()), float(m.tvalues[0]), float(m.pvalues[0])


def hac_difference(a, b):
    z = pd.concat([pd.Series(a), pd.Series(b)], axis=1).dropna()
    return hac_mean_test(z.iloc[:, 0] - z.iloc[:, 1])


def paired_block_bootstrap_sharpe_diff(a, b, repetitions, block_length, seed):
    """Paired moving-block bootstrap of Sharpe(a)-Sharpe(b)."""
    a = np.asarray(a, dtype=float); b = np.asarray(b, dtype=float)
    if len(a) != len(b) or len(a) < block_length:
        raise ValueError("Paired bootstrap requires equal series and adequate length.")
    if repetitions <= 0 or block_length <= 0:
        raise ValueError("Bootstrap repetitions and block length must be positive.")
    rng = np.random.default_rng(seed)
    n = len(a)
    starts = np.arange(n - block_length + 1)
    vals = np.empty(repetitions)
    for j in range(repetitions):
        pieces = []
        while sum(len(x) for x in pieces) < n:
            st = int(rng.choice(starts))
            pieces.append(np.arange(st, min(st + block_length, n)))
        idx = np.concatenate(pieces)[:n]
        vals[j] = zero_rf_sharpe(a[idx]) - zero_rf_sharpe(b[idx])
    q = np.quantile(vals, [0.025, 0.5, 0.975])
    return float(q[0]), float(q[1]), float(q[2])


def bootstrap_sharpe_table(b):
    rows=[]
    rng_seed = BOOTSTRAP_SEED
    for s in STRATEGIES:
        a=b[s].to_numpy(dtype=float)
        # Paired with itself is unnecessary; this table is descriptive.
        rng=np.random.default_rng(rng_seed)
        n=len(a); starts=np.arange(n-BOOTSTRAP_BLOCK_LENGTH+1)
        vals=np.empty(BOOTSTRAP_REPETITIONS)
        for j in range(BOOTSTRAP_REPETITIONS):
            idx=[]
            while len(idx)<n:
                st=int(rng.choice(starts)); idx.extend(range(st,min(st+BOOTSTRAP_BLOCK_LENGTH,n)))
            vals[j]=zero_rf_sharpe(a[np.asarray(idx[:n])])
        q=np.quantile(vals,[.025,.5,.975])
        rows.append([s,*q])
    return pd.DataFrame(rows,columns=["strategy","lower_95","median","upper_95"]).set_index("strategy")


def holm_adjust(p_values):
    p=np.asarray(p_values,dtype=float); out=np.full(len(p),np.nan)
    valid=np.isfinite(p); idx=np.where(valid)[0]
    if len(idx)==0: return out
    order=idx[np.argsort(p[idx])]; m=len(order); running=0.0
    for rank,j in enumerate(order):
        running=max(running,min(1.0,(m-rank)*p[j])); out[j]=running
    return out


def regime_table(b, r):
    """Report regime-conditioned monthly return/risk statistics.

    Annualized compound returns are not reported because regime observations
    are non-contiguous; compounding them as if consecutive would be misleading.
    """
    spy = r["SPY"]
    signal = ((1.0 + spy).rolling(12).apply(np.prod, raw=True) - 1.0).shift(1)
    # Months without 12 prior completed observations have no valid regime
    # signal and must not be silently classified as Neutral.
    reg = pd.Series(pd.NA, index=r.index, dtype="string")
    reg.loc[signal.notna() & (signal > .10)] = "Bull"
    reg.loc[signal.notna() & (signal < -.10)] = "Bear"
    reg.loc[signal.notna() & (signal >= -.10) & (signal <= .10)] = "Neutral"
    rows = []
    for regime in ["Bull", "Neutral", "Bear"]:
        idx = reg.index[reg == regime].intersection(b.index)
        for st in STRATEGIES:
            x = b.loc[idx, st].dropna()
            rows.append([regime, st, len(x), float(x.mean()), annualized_volatility(x),
                         zero_rf_sharpe(x), maximum_drawdown(x)])
    return pd.DataFrame(rows, columns=["regime", "strategy", "n_months",
                                       "mean_monthly_return", "ann_vol",
                                       "sharpe_zero_rf", "max_drawdown"])


def robust_ff5(b):
    resp=requests.get(FF5_URL,timeout=60,headers={"User-Agent":"Mozilla/5.0"}); resp.raise_for_status()
    ff5_sha256 = hashlib.sha256(resp.content).hexdigest()
    with zipfile.ZipFile(io.BytesIO(resp.content)) as z:
        csvs=[n for n in z.namelist() if n.lower().endswith(".csv")]
        if not csvs: raise RuntimeError("FF5 ZIP contains no CSV.")
        selected = None
        for name in csvs:
            candidate = z.read(name).decode("latin1").splitlines()
            if any("Mkt-RF" in line and "SMB" in line and "HML" in line and "RF" in line for line in candidate[:80]):
                selected = candidate
                break
        if selected is None: raise RuntimeError("FF5 monthly factor CSV not found.")
        raw = selected
    h=next((i for i,l in enumerate(raw) if "Mkt-RF" in l and "SMB" in l and "HML" in l and "RF" in l),None)
    if h is None: raise RuntimeError("FF5 monthly header not found.")
    rows=[]
    for line in raw[h+1:]:
        first=line.split(",",1)[0].strip()
        if len(first)==6 and first.isdigit(): rows.append(line)
        elif rows: break
    f=pd.read_csv(io.StringIO(raw[h]+"\n"+"\n".join(rows)))
    f=f.rename(columns={f.columns[0]:"Date"})
    f["Date"]=pd.to_datetime(f["Date"].astype(str).str.strip(),format="%Y%m",errors="coerce")
    f=f.dropna(subset=["Date"]).set_index("Date")
    need=["Mkt-RF","SMB","HML","RMW","CMA","RF"]
    if any(c not in f.columns for c in need): raise RuntimeError("FF5 fields missing.")
    f[need]=f[need].apply(pd.to_numeric,errors="coerce")/100.0
    f.index=f.index.to_period("M").to_timestamp("M")
    p=b.copy(); p.index=p.index.to_period("M").to_timestamp("M")
    d=p.join(f[need],how="inner").dropna()
    rows=[]
    X=sm.add_constant(d[["Mkt-RF","SMB","HML","RMW","CMA"]])
    for s in STRATEGIES:
        y=d[s]-d["RF"]
        if len(y) <= X.shape[1]+HAC_LAGS: raise RuntimeError("Insufficient FF5 observations.")
        m=sm.OLS(y,X).fit(cov_type="HAC",cov_kwds={"maxlags":min(HAC_LAGS,len(d)-2)})
        rows.append([s,float(m.params["const"]),12*float(m.params["const"]),float(m.tvalues["const"]),float(m.pvalues["const"]),*map(float,[m.params["Mkt-RF"],m.params["SMB"],m.params["HML"],m.params["RMW"],m.params["CMA"]]),float(m.rsquared),int(m.nobs)])
    out=pd.DataFrame(rows,columns=["strategy","alpha_monthly","alpha_annualized_linear","alpha_t","alpha_p","MKT_beta","SMB_beta","HML_beta","RMW_beta","CMA_beta","R_squared","n"]).set_index("strategy")
    out["alpha_p_holm"] = holm_adjust(out["alpha_p"].to_numpy())
    out.attrs["source_sha256"] = ff5_sha256
    return out


def transaction_cost_break_even(r, gamma):
    gross=audited_backtest(r,BASELINE_WINDOW,0,gamma,False,1)
    ew=gross[gross.strategy=="EW"]
    out=[]
    for st in OPTIMIZED:
        a=gross[gross.strategy==st]
        common=a.index.intersection(ew.index); a=a.loc[common]; e=ew.loc[common]
        def adv(c):
            ar=(1+a.gross)*(1-c/10000*a.turnover)-1
            er=(1+e.gross)*(1-c/10000*e.turnover)-1
            if (1+ar<=0).any() or (1+er<=0).any(): return np.nan
            return annualized_return(ar)-annualized_return(er)
        lo=0.0
        if not np.isfinite(adv(0)): be=np.nan
        elif adv(0)<=0: be=0.0
        else:
            max_turnover=max(float(a.turnover.max()),float(e.turnover.max()))
            hi=min(5000.0, 10000.0/max_turnover*0.999999) if max_turnover>0 else 5000.0
            # Locate the first sign change on a fine grid; the return-difference
            # objective need not be globally monotone because strategies have
            # different turnover paths. Refine only the first valid bracket.
            grid=np.linspace(lo,hi,501); vals=np.array([adv(x) for x in grid])
            bracket=None
            for j in range(len(grid)-1):
                if np.isfinite(vals[j]) and np.isfinite(vals[j+1]) and vals[j]>=0 and vals[j+1]<=0:
                    bracket=(grid[j],grid[j+1]); break
            if bracket is None:
                be=np.nan
            else:
                lo,hi=bracket
                for _ in range(80):
                    mid=(lo+hi)/2; val=adv(mid)
                    if not np.isfinite(val): hi=mid
                    elif val>0: lo=mid
                    else: hi=mid
                be=(lo+hi)/2
        out.append([st,be])
    return pd.DataFrame(out,columns=["strategy","break_even_cost_bps"]).set_index("strategy")


def hypothesis_tests(r,b,s,window_returns):
    rows=[]
    h1=[]
    for st in OPTIMIZED:
        n,md,t,p=hac_difference(b[st],b.EW)
        common=b[[st,"EW"]].dropna(); ci=paired_block_bootstrap_sharpe_diff(common[st],common.EW,BOOTSTRAP_REPETITIONS,BOOTSTRAP_BLOCK_LENGTH,BOOTSTRAP_SEED)
        h1.append(["H1",f"{st} - EW","mean monthly return difference",n,md,t,p,np.nan,zero_rf_sharpe(common[st])-zero_rf_sharpe(common.EW),*ci])
    for x,padj in zip(h1,holm_adjust([x[6] for x in h1])): rows.append(x+[padj])
    h2=[]
    if 36 not in window_returns or 120 not in window_returns:
        raise KeyError("H2 requires 36-month and 120-month window results.")
    common_idx=window_returns[36].index.intersection(window_returns[120].index)
    for st in OPTIMIZED:
        a=window_returns[36].loc[common_idx,st]; z=window_returns[120].loc[common_idx,st]
        n,md,t,p=hac_difference(a,z)
        ci=paired_block_bootstrap_sharpe_diff(a,z,BOOTSTRAP_REPETITIONS,BOOTSTRAP_BLOCK_LENGTH,BOOTSTRAP_SEED)
        h2.append(["H2",f"{st}: 36m - 120m","mean monthly return difference",n,md,t,p,np.nan,zero_rf_sharpe(a)-zero_rf_sharpe(z),*ci])
    for x,padj in zip(h2,holm_adjust([x[6] for x in h2])): rows.append(x+[padj])
    be=transaction_cost_break_even(r,BASELINE_GAMMA)
    for st in be.index: rows.append(["H3",f"{st} vs EW","exact economic break-even cost (bps)",np.nan,np.nan,np.nan,np.nan,float(be.loc[st,"break_even_cost_bps"]),np.nan,np.nan,np.nan,np.nan,np.nan])
    h4=[]
    spy=r.SPY; signal=((1+spy).rolling(12).apply(np.prod,raw=True)-1).shift(1); reg=pd.Series(pd.NA,index=r.index,dtype="string"); reg.loc[signal.notna() & (signal>.10)]="Bull"; reg.loc[signal.notna() & (signal<-.10)]="Bear"; reg.loc[signal.notna() & (signal>=-.10) & (signal<=.10)]="Neutral"
    for st in OPTIMIZED:
        d=pd.DataFrame({"y":b[st]-b.EW,"bull":(reg.reindex(b.index)=="Bull").astype(int),"bear":(reg.reindex(b.index)=="Bear").astype(int)}).dropna()
        if len(d) <= HAC_LAGS + 2 or d[["bull","bear"]].nunique().min() < 2:
            raise RuntimeError(f"Insufficient variation for H4 regime regression: {st}")
        m=sm.OLS(d.y,sm.add_constant(d[["bull","bear"]])).fit(cov_type="HAC",cov_kwds={"maxlags":min(HAC_LAGS,len(d)-2)})
        h4.append(["H4",f"{st} - EW: Bull/Bear vs Neutral","joint test: bull=0 and bear=0",len(d),float(d.y.mean()),np.nan,float(m.f_pvalue),float(m.params.bull),float(m.params.bear),np.nan,np.nan,np.nan])
    for x,padj in zip(h4,holm_adjust([x[6] for x in h4])): rows.append(x+[padj])
    h5=[]; common=b.index.intersection(s.index)
    for st in OPTIMIZED:
        n,md,t,p=hac_difference(s.loc[common,st],b.loc[common,st]); ci=paired_block_bootstrap_sharpe_diff(s.loc[common,st],b.loc[common,st],BOOTSTRAP_REPETITIONS,BOOTSTRAP_BLOCK_LENGTH,BOOTSTRAP_SEED)
        h5.append(["H5",f"{st}: Ledoit-Wolf - Sample","mean monthly return difference",n,md,t,p,np.nan,zero_rf_sharpe(s.loc[common,st])-zero_rf_sharpe(b.loc[common,st]),*ci])
    for x,padj in zip(h5,holm_adjust([x[6] for x in h5])): rows.append(x+[padj])
    out=pd.DataFrame(rows,columns=["hypothesis","comparison","estimand","n","mean_monthly_diff","hac_t_or_nan","p_value_raw","economic_threshold_or_bull_coef","sharpe_diff_or_bear_coef","ci_low","ci_median_or_nan","ci_high","p_value_holm_within_family"])
    out["bull_coef"] = np.nan
    out["bear_coef"] = np.nan
    h4mask=out["hypothesis"].eq("H4")
    # H4 stores bull/bear coefficients in the two dedicated coefficient columns.
    out.loc[h4mask,"bull_coef"] = out.loc[h4mask,"economic_threshold_or_bull_coef"]
    out.loc[h4mask,"bear_coef"] = out.loc[h4mask,"sharpe_diff_or_bear_coef"]
    return out


def make_figures(r,b,costs,regime,boot,baseline):
    wealth=(1+b).cumprod(); ax=wealth.plot(figsize=(10,5)); ax.set_title("Cumulative Net Wealth — Baseline Backtest"); ax.set_ylabel("Growth of $1"); ax.figure.tight_layout(); ax.figure.savefig(FIG/"01_cumulative_wealth.png",dpi=220); plt.close(ax.figure)
    dd=wealth/wealth.cummax()-1; ax=dd.plot(figsize=(10,5)); ax.set_title("Portfolio Drawdowns — Baseline Backtest"); ax.set_ylabel("Drawdown"); ax.figure.tight_layout(); ax.figure.savefig(FIG/"02_drawdowns.png",dpi=220); plt.close(ax.figure)
    t=baseline.groupby("strategy").turnover.mean(); ax=t.plot(kind="bar",figsize=(8,4.5)); ax.set_title("Average Monthly Turnover (Two-Way)"); ax.set_ylabel("Two-way turnover"); ax.figure.tight_layout(); ax.figure.savefig(FIG/"03_turnover.png",dpi=220); plt.close(ax.figure)
    rows=[]
    for c,tab in costs.items():
        for st in STRATEGIES: rows.append([c,st,tab.loc[st,"ann_return"]])
    cd=pd.DataFrame(rows,columns=["cost_bps","strategy","ann_return"]); ax=cd.pivot(index="cost_bps",columns="strategy",values="ann_return").plot(marker="o",figsize=(9,5)); ax.set_title("Annualized Net Return vs Transaction Cost"); ax.set_xlabel("Transaction cost (bps)"); ax.set_ylabel("Annualized return"); ax.figure.tight_layout(); ax.figure.savefig(FIG/"04_transaction_cost_sensitivity.png",dpi=220); plt.close(ax.figure)
    rg=regime.pivot(index="regime",columns="strategy",values="sharpe_zero_rf"); ax=rg.plot(kind="bar",figsize=(9,5)); ax.set_title("Zero-Risk-Free Sharpe Ratio by Market Regime"); ax.set_ylabel("Sharpe ratio"); ax.figure.tight_layout(); ax.figure.savefig(FIG/"05_regime_sharpe.png",dpi=220); plt.close(ax.figure)
    fig,ax=plt.subplots(figsize=(9,5)); x=np.arange(len(boot)); med=boot.median.to_numpy(); ax.errorbar(x,med,yerr=[med-boot.lower_95.to_numpy(),boot.upper_95.to_numpy()-med],fmt="o"); ax.set_xticks(x,boot.index); ax.set_title("Bootstrap Sharpe Ratios with 95% CIs"); ax.set_ylabel("Sharpe ratio (Rf=0)"); fig.tight_layout(); fig.savefig(FIG/"06_bootstrap_sharpe_ci.png",dpi=220); plt.close(fig)
    corr=r.corr(); fig,ax=plt.subplots(figsize=(8,7)); im=ax.imshow(corr.values,vmin=-1,vmax=1,aspect="auto"); ax.set_xticks(range(len(corr)),corr.columns); ax.set_yticks(range(len(corr)),corr.index); ax.set_title("Monthly Return Correlation Matrix"); fig.colorbar(im,ax=ax,label="Correlation"); fig.tight_layout(); fig.savefig(FIG/"07_correlation_matrix.png",dpi=220); plt.close(fig)


def main():
    r=validate_monthly_returns(get_returns())
    returns_path = OUT/"monthly_returns.csv"
    r.to_csv(returns_path)
    returns_sha256 = hashlib.sha256(returns_path.read_bytes()).hexdigest()
    baseline=audited_backtest(r,BASELINE_WINDOW,BASELINE_COST_BPS,BASELINE_GAMMA,False,1)
    shrink=audited_backtest(r,BASELINE_WINDOW,BASELINE_COST_BPS,BASELINE_GAMMA,True,1)
    quarterly=audited_backtest(r,BASELINE_WINDOW,BASELINE_COST_BPS,BASELINE_GAMMA,False,3)
    b=pivot(baseline)
    performance_summary(baseline).to_csv(OUT/"table_01_baseline_performance.csv")
    rows=[]
    for a in r.columns:
        x=r[a]; rows.append([a,annualized_return(x),annualized_volatility(x),zero_rf_sharpe(x),rf2_sharpe(x),x.skew(),x.kurt(),maximum_drawdown(x),len(x)])
    pd.DataFrame(rows,columns=["asset","ann_return","ann_vol","sharpe_zero_rf","sharpe_rf2","skewness","excess_kurtosis","max_drawdown","n_months"]).set_index("asset").to_csv(OUT/"table_02_asset_descriptives.csv")
    r.corr().to_csv(OUT/"table_03_correlation_matrix.csv")
    windows={}; window_returns={}
    for w in WINDOWS:
        bt=audited_backtest(r,w,BASELINE_COST_BPS,BASELINE_GAMMA,False,1); windows[w]=performance_summary(bt); window_returns[w]=pivot(bt); windows[w].to_csv(OUT/f"table_window_{w}.csv")
    for g in GAMMAS: performance_summary(audited_backtest(r,BASELINE_WINDOW,BASELINE_COST_BPS,g,False,1)).to_csv(OUT/f"table_gamma_{g}.csv")
    costs={}
    for c in COSTS_BPS:
        costs[c]=performance_summary(audited_backtest(r,BASELINE_WINDOW,c,BASELINE_GAMMA,False,1)); costs[c].to_csv(OUT/f"table_cost_{c}bps.csv")
    performance_summary(shrink).to_csv(OUT/"table_06_ledoit_wolf.csv")
    performance_summary(quarterly).to_csv(OUT/"table_07_quarterly_rebalancing.csv")
    regime=regime_table(b,r); regime.to_csv(OUT/"table_08_regime_performance.csv",index=False)
    tests=hypothesis_tests(r,b,pivot(shrink),window_returns); tests.to_csv(OUT/"table_09_hypothesis_tests.csv",index=False)
    boot=bootstrap_sharpe_table(b); boot.to_csv(OUT/"table_10_bootstrap_sharpe.csv")
    ff=robust_ff5(b); ff.to_csv(OUT/"table_11_fama_french_5factor.csv")
    make_figures(r,b,costs,regime,boot,baseline)
    prov={"pipeline_version":"final-audited","retrieved_at_utc":datetime.now(timezone.utc).isoformat(),"sample_start":str(r.index.min()),"sample_end":str(r.index.max()),"n_months":len(r),"monthly_returns_sha256":returns_sha256,"tickers":TICKERS,"baseline":{"window":BASELINE_WINDOW,"cost_bps":BASELINE_COST_BPS,"gamma":BASELINE_GAMMA,"max_target_weight":MAX_WEIGHT,"turnover":"two-way sum(abs(target-pretrade_actual))","initial_transaction_cost_charged":False,"transaction_cost_timing":"beginning-of-period; net_return=(1+gross_return)*(1-cost_rate)-1","sharpe":"zero-risk-free monthly Sharpe annualized by sqrt(12)","sharpe_robustness":"2% annual fixed risk-free benchmark"},"bootstrap":{"repetitions":BOOTSTRAP_REPETITIONS,"block_length":BOOTSTRAP_BLOCK_LENGTH,"seed":BOOTSTRAP_SEED,"comparison_bootstrap":"paired moving-block bootstrap"},"hac":{"lags":HAC_LAGS,"kernel":"Bartlett/Newey-West","small_sample_correction":True},"fama_french_source":FF5_URL,"fama_french_zip_sha256":ff.attrs.get("source_sha256"),"statistical_notes":{"break_even":"economic threshold; not a hypothesis test","multiple_testing":"Holm within each pre-specified comparison family; FF5 alpha adjustment reported separately"},"python":sys.version,"platform":platform.platform()}
    (OUT/"empirical_provenance.json").write_text(json.dumps(prov,indent=2),encoding="utf-8")
    print(f"Completed. Results written to {OUT}")

if __name__ == "__main__": main()
