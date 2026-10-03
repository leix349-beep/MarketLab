from __future__ import annotations
import numpy as np
import pandas as pd

def indicators(df: pd.DataFrame, fast=20, slow=50, rsi_n=14) -> pd.DataFrame:
    x = df.copy()
    x["fast"] = x["Close"].rolling(fast).mean()
    x["slow"] = x["Close"].rolling(slow).mean()
    d = x["Close"].diff()
    gain = d.clip(lower=0).rolling(rsi_n).mean()
    loss = (-d.clip(upper=0)).rolling(rsi_n).mean()
    x["rsi"] = 100 - 100 / (1 + gain / loss.replace(0, np.nan))
    return x

def backtest(df: pd.DataFrame, fast=20, slow=50, rsi_buy=55, stop_loss=.05,
             take_profit=.10, fee=.001, initial=10000.0, news=None):
    x = indicators(df, fast, slow).dropna().copy()
    cash, shares, entry = initial, 0.0, 0.0
    values, trades = [], []
    # Signals are formed after the previous close and executed at the next open.
    # This prevents using information that was not yet available at execution time.
    for i in range(1, len(x)):
        dt, row = x.index[i], x.iloc[i]
        signal_dt, signal = x.index[i-1], x.iloc[i-1]
        price = float(row.Open)
        sentiment = 0 if news is None else float(news.get(signal_dt.date(), 0))
        buy = signal.fast > signal.slow and signal.rsi < rsi_buy and sentiment >= -.2
        reason = None
        if shares and float(signal.Close) <= entry * (1-stop_loss): reason = "stop_loss"
        elif shares and float(signal.Close) >= entry * (1+take_profit): reason = "take_profit"
        elif shares and signal.fast < signal.slow: reason = "trend_reversal"
        if shares and reason:
            cash = shares * price * (1-fee); trades.append((dt, "sell", price, reason)); shares = 0
        elif not shares and buy:
            shares = cash * (1-fee) / price; cash = 0; entry = price
            trades.append((dt, "buy", price, "trend_rsi"))
        values.append((dt, cash + shares*float(row.Close)))
    curve = pd.Series(dict(values), name="策略净值")
    ret = curve.pct_change().dropna()
    metrics = {
        "总收益": curve.iloc[-1]/initial-1 if len(curve) else 0,
        "最大回撤": (curve/curve.cummax()-1).min() if len(curve) else 0,
        "夏普比率": np.sqrt(252)*ret.mean()/ret.std() if ret.std() else 0,
        "交易次数": len(trades),
    }
    return curve, pd.DataFrame(trades, columns=["date","action","price","reason"]), metrics

def grid_search(df, fasts=(10,20,30), slows=(40,60,100)):
    rows=[]
    for f in fasts:
        for s in slows:
            if f >= s: continue
            _,_,m=backtest(df, fast=f, slow=s)
            rows.append({"短均线":f,"长均线":s,**m})
    return pd.DataFrame(rows).sort_values("夏普比率", ascending=False)

