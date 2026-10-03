from __future__ import annotations
import numpy as np
import pandas as pd
from strategy import indicators

def _stateful_signal(entry: pd.Series, exit_: pd.Series) -> pd.Series:
    holding=False; values=[]
    for enter, leave in zip(entry.fillna(False),exit_.fillna(False)):
        if not holding and enter: holding=True
        elif holding and leave: holding=False
        values.append(holding)
    return pd.Series(values,index=entry.index,dtype=bool)

def strategy_signals(df: pd.DataFrame, fast=20, slow=60, rsi_entry=35,
                     rsi_exit=55, breakout_window=55) -> dict[str,pd.Series]:
    x=indicators(df,fast,slow)
    trend=(x.fast>x.slow).fillna(False)
    mean_reversion=_stateful_signal(x.rsi<rsi_entry,x.rsi>rsi_exit)
    prior_high=x.Close.rolling(breakout_window).max().shift(1)
    breakout=_stateful_signal(x.Close>prior_high,x.Close<x.Close.rolling(20).mean())
    hybrid=_stateful_signal((x.fast>x.slow)&(x.rsi<55),x.fast<x.slow)
    return {"Trend":trend,"Mean Reversion":mean_reversion,"Breakout":breakout,"Trend + RSI":hybrid}

def simulate_target(df: pd.DataFrame, target: pd.Series, fee=.001, initial=10000.0):
    target=target.reindex(df.index).fillna(False)
    cash,shares=initial,0.0; values=[]; actions=0
    for i in range(1,len(df)):
        open_price=float(df.Open.iloc[i]); close_price=float(df.Close.iloc[i])
        desired=bool(target.iloc[i-1])
        if desired and not shares:
            shares=cash*(1-fee)/open_price; cash=0; actions+=1
        elif not desired and shares:
            cash=shares*open_price*(1-fee); shares=0; actions+=1
        values.append((df.index[i],cash+shares*close_price))
    curve=pd.Series(dict(values),dtype=float)
    ret=curve.pct_change().dropna()
    years=max(len(ret)/252,1/252)
    total=curve.iloc[-1]/initial-1
    annual=(curve.iloc[-1]/initial)**(1/years)-1
    drawdown=(curve/curve.cummax()-1).min()
    sharpe=np.sqrt(252)*ret.mean()/ret.std() if ret.std() else 0.0
    return curve,{"Total Return":total,"Annualized Return":annual,"Maximum Drawdown":drawdown,
                  "Sharpe Ratio":sharpe,"Trade Actions":actions}

def compare_strategies(df: pd.DataFrame, **kwargs):
    signals=strategy_signals(df,**{k:v for k,v in kwargs.items() if k!="fee"})
    warmup=max(int(kwargs.get("slow",60)),int(kwargs.get("breakout_window",55)),20)+1
    eval_df=df.iloc[warmup:].copy()
    curves={}; rows=[]
    for name,signal in signals.items():
        curve,metrics=simulate_target(eval_df,signal.reindex(eval_df.index),fee=kwargs.get("fee",.001))
        curves[name]=curve; rows.append({"Strategy":name,**metrics})
    base_shares=10000*(1-kwargs.get("fee",.001))/float(eval_df.Open.iloc[1])
    base=eval_df.Close.iloc[1:]*base_shares
    base_ret=base.pct_change().dropna(); years=max(len(base_ret)/252,1/252)
    rows.append({"Strategy":"Buy & Hold","Total Return":base.iloc[-1]/10000-1,
                 "Annualized Return":(base.iloc[-1]/10000)**(1/years)-1,
                 "Maximum Drawdown":(base/base.cummax()-1).min(),
                 "Sharpe Ratio":np.sqrt(252)*base_ret.mean()/base_ret.std(),"Trade Actions":1})
    curves["Buy & Hold"]=base
    return pd.DataFrame(rows).sort_values("Sharpe Ratio",ascending=False),pd.DataFrame(curves).dropna()

