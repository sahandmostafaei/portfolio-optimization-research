# Portfolio Optimization Research — Reproducibility Pipeline v3
# Baseline: 60-month rolling window, monthly rebalance, 15 bps costs,
# long-only, fully invested, max weight 30%, strict t -> t+1 OOS timing.
# Robustness: windows 36/60/120, costs 0/5/10/15/30 bps,
# Ledoit-Wolf covariance shrinkage, gamma 1/3/5/10, quarterly rebalance.
# No empirical results are embedded in this script.

from pathlib import Path
import json, sys, platform
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
from scipy.optimize import minimize
from sklearn.covariance import LedoitWolf

TICKERS=["SPY","EFA","EEM","TLT","GLD","DBC","VNQ"]
WINDOWS=[36,60,120]; COSTS=[0,5,10,15,30]; GAMMAS=[1,3,5,10]
MAX_W=.30; OUT=Path("portfolio_research_output"); OUT.mkdir(exist_ok=True)

def get_returns():
    x=yf.download(TICKERS,period="max",auto_adjust=True,progress=False)
    px=x["Close"] if isinstance(x.columns,pd.MultiIndex) else x
    px=px[TICKERS].dropna(how="all")
    return px.resample("ME").last().pct_change().dropna(how="any")

def cons(n): return [(0,MAX_W)]*n,{"type":"eq","fun":lambda w:np.sum(w)-1}
def ew(n): return np.ones(n)/n

def opt(cov,mu=None,gamma=None,erc_flag=False):
    n=cov.shape[0]; b,c=cons(n); x=ew(n)
    if erc_flag:
        def f(w):
            s=np.sqrt(max(w@cov@w,1e-16)); rc=w*(cov@w)/s
            return np.sum((rc-rc.mean())**2)
    elif mu is None:
        f=lambda w:w@cov@w
    else:
        f=lambda w:-(w@mu-.5*gamma*(w@cov@w))
    z=minimize(f,x,method="SLSQP",bounds=b,constraints=c,
               options={"maxiter":2000,"ftol":1e-13})
    if not z.success: raise RuntimeError(z.message)
    return z.x

def make_weights(train,gamma=3,shrink=False):
    mu=train.mean().values
    cov=LedoitWolf().fit(train.values).covariance_ if shrink else train.cov().values
    return {"EW":ew(len(mu)),
            "MINVAR":opt(cov),
            "MV":opt(cov,mu,gamma),
            "ERC":opt(cov,erc_flag=True)}

def run(r,window=60,cost_bps=15,gamma=3,shrink=False,step=1):
    rows=[]; prev={s:ew(len(TICKERS)) for s in ["EW","MINVAR","MV","ERC"]}
    for i in range(window,len(r),step):
        w=make_weights(r.iloc[i-window:i],gamma,shrink)
        for j in range(i,min(i+step,len(r))):
            for s,a in w.items():
                to=np.abs(a-prev[s]).sum()
                gross=float(r.iloc[j].values@a)
                net=gross-cost_bps/10000*to
                rows.append([r.index[j],s,gross,net,to,*a])
            prev=w
    return pd.DataFrame(rows,columns=["date","strategy","gross","net","turnover"]+TICKERS).set_index("date")

def sharpe(x,rf=0):
    x=x-rf/12
    return np.sqrt(12)*x.mean()/x.std(ddof=1)

def mdd(x):
    w=(1+x).cumprod(); return (w/w.cummax()-1).min()

def summary(o):
    out=[]
    for s,g in o.groupby("strategy"):
        x=g.net
        out.append([s,(1+x).prod()**(12/len(x))-1,x.std(ddof=1)*np.sqrt(12),
                    sharpe(x),sharpe(x,.02),mdd(x),g.turnover.mean(),
                    g[TICKERS].max().max(),1/(g[TICKERS]**2).sum(axis=1).mean()])
    return pd.DataFrame(out,columns=["strategy","ann_return","ann_vol","sharpe_rf0",
        "sharpe_rf2","max_drawdown","avg_turnover","max_weight","effective_holdings"]).set_index("strategy")

def mbb(x,fn,B=2000,block=6,seed=42):
    rng=np.random.default_rng(seed); x=np.asarray(x); n=len(x); vals=[]
    for _ in range(B):
        starts=rng.integers(0,n,size=int(np.ceil(n/block)))
        idx=np.concatenate([np.arange(s,min(s+block,n)) for s in starts])[:n]
        vals.append(fn(x[idx]))
    return np.quantile(vals,[.025,.5,.975])

def main():
    r=get_returns(); r.to_csv(OUT/"monthly_returns.csv")
    base=run(r,60,15,3,False,1); summary(base).to_csv(OUT/"baseline_performance.csv")
    for w in WINDOWS: summary(run(r,w,15,3,False,1)).to_csv(OUT/f"window_{w}.csv")
    for c in COSTS: summary(run(r,60,c,3,False,1)).to_csv(OUT/f"cost_{c}bps.csv")
    for g in GAMMAS: summary(run(r,60,15,g,False,1)).to_csv(OUT/f"gamma_{g}.csv")
    summary(run(r,60,15,3,True,1)).to_csv(OUT/"ledoit_wolf.csv")
    summary(run(r,60,15,3,False,3)).to_csv(OUT/"quarterly_rebalance.csv")

    p=base.pivot_table(index=base.index,columns="strategy",values="net").dropna()
    ci={s:mbb(p[s].values,sharpe) for s in p}
    pd.DataFrame(ci,index=["lower_95","median","upper_95"]).T.to_csv(OUT/"bootstrap_sharpe_ci.csv")
    pairs={}
    ss=list(p.columns)
    for i,a in enumerate(ss):
        for b in ss[i+1:]:
            d=p[a]-p[b]
            pairs[f"{a}-{b}"]=mbb(d.values,sharpe)
    pd.DataFrame(pairs,index=["lower_95","median","upper_95"]).T.to_csv(OUT/"bootstrap_pairwise_sharpe_difference.csv")

    for s,g in base.groupby("strategy"):
        plt.figure(figsize=(8,4.5)); (1+g.net).cumprod().plot()
        plt.title(f"Cumulative Net Wealth — {s}"); plt.ylabel("Growth of $1"); plt.xlabel("Date")
        plt.tight_layout(); plt.savefig(OUT/f"wealth_{s}.png",dpi=180); plt.close()

    meta={"python":sys.version,"platform":platform.platform(),"tickers":TICKERS,
          "sample_start":str(r.index.min()),"sample_end":str(r.index.max()),
          "baseline":{"window":60,"cost_bps":15,"gamma":3,"max_weight":MAX_W,"rebalance":"monthly"}}
    (OUT/"provenance.json").write_text(json.dumps(meta,indent=2))

if __name__=="__main__": main()
