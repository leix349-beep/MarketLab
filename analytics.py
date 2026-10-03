from __future__ import annotations
import numpy as np
import pandas as pd

def risk_metrics(asset: pd.Series, market: pd.Series, risk_free=0.0):
    pair = pd.concat([asset.pct_change(), market.pct_change()], axis=1).dropna()
    pair.columns = ["asset", "market"]
    annual_return = (1 + pair.asset).prod() ** (252 / len(pair)) - 1
    volatility = pair.asset.std() * np.sqrt(252)
    beta = pair.asset.cov(pair.market) / pair.market.var() if pair.market.var() else np.nan
    market_annual = (1 + pair.market).prod() ** (252 / len(pair)) - 1
    alpha = annual_return - (risk_free + beta * (market_annual-risk_free))
    downside = pair.loc[pair.asset < 0, "asset"].std() * np.sqrt(252)
    sortino = (annual_return-risk_free) / downside if downside else np.nan
    return {"annual_return":annual_return, "volatility":volatility,
            "beta":beta, "alpha":alpha, "sortino":sortino}

def monthly_returns(close: pd.Series):
    monthly = close.resample("ME").last().pct_change().dropna()
    table = monthly.to_frame("return")
    table["year"] = table.index.year; table["month"] = table.index.month
    return table.pivot(index="year", columns="month", values="return")

def market_model(asset: pd.Series, market: pd.Series, bootstrap_samples=1000, seed=42):
    pair=pd.concat([asset.pct_change(),market.pct_change()],axis=1).dropna()
    pair.columns=["asset","market"]
    x=pair.market.to_numpy(); y=pair.asset.to_numpy()
    beta=np.cov(x,y,ddof=1)[0,1]/np.var(x,ddof=1)
    alpha_daily=y.mean()-beta*x.mean()
    predicted=alpha_daily+beta*x
    residual=y-predicted
    ss_total=((y-y.mean())**2).sum(); ss_res=(residual**2).sum()
    r_squared=1-ss_res/ss_total if ss_total else np.nan
    rng=np.random.default_rng(seed); boot=[]; n=len(pair)
    for _ in range(bootstrap_samples):
        idx=rng.integers(0,n,n); bx=x[idx]; by=y[idx]
        variance=np.var(bx,ddof=1)
        if variance: boot.append(np.cov(bx,by,ddof=1)[0,1]/variance)
    low,high=np.percentile(boot,[2.5,97.5])
    detail=pair.copy(); detail["predicted"]=predicted; detail["residual"]=residual
    rolling_cov=pair.asset.rolling(63).cov(pair.market)
    rolling_beta=rolling_cov/pair.market.rolling(63).var()
    return {"alpha_daily":alpha_daily,"alpha_annual":alpha_daily*252,"beta":beta,
            "r_squared":r_squared,"beta_ci_low":low,"beta_ci_high":high,"observations":n},detail,rolling_beta
