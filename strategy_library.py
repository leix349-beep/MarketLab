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

def volatility_target_weights(df: pd.DataFrame, fast=20, slow=60,
                              target_vol=.12, vol_window=20) -> pd.Series:
    """Trend exposure scaled down when recent volatility is high."""
    x=indicators(df,fast,slow)
    realized=df.Close.pct_change().rolling(vol_window).std()*np.sqrt(252)
    weights=(target_vol/realized.replace(0,np.nan)).clip(lower=0,upper=1)
    return weights.where(x.fast>x.slow,0).fillna(0)

def _metrics(curve: pd.Series, initial: float, actions: int, exposure: float):
    ret=curve.pct_change().dropna(); years=max(len(ret)/252,1/252)
    total=curve.iloc[-1]/initial-1
    annual=(curve.iloc[-1]/initial)**(1/years)-1
    drawdown=(curve/curve.cummax()-1).min()
    sharpe=np.sqrt(252)*ret.mean()/ret.std() if ret.std() else 0.0
    calmar=annual/abs(drawdown) if drawdown else 0.0
    return {"Total Return":total,"Annualized Return":annual,"Maximum Drawdown":drawdown,
            "Sharpe Ratio":sharpe,"Calmar Ratio":calmar,"Average Exposure":exposure,
            "Trade Actions":actions}

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
    return curve,_metrics(curve,initial,actions,float(target.iloc[1:].mean()))

def simulate_weights(df: pd.DataFrame, weights: pd.Series, fee=.001,
                     initial=10000.0, rebalance_band=.05):
    """Execute yesterday's target weight at today's open with trading costs."""
    weights=weights.reindex(df.index).fillna(0).clip(0,1)
    cash,shares=initial,0.0; values=[]; actions=0; realized_weights=[]
    for i in range(1,len(df)):
        open_price=float(df.Open.iloc[i]); close_price=float(df.Close.iloc[i])
        portfolio_open=cash+shares*open_price
        current_weight=(shares*open_price/portfolio_open) if portfolio_open else 0.0
        desired=float(weights.iloc[i-1])
        if abs(desired-current_weight)>=rebalance_band or (desired==0 and shares):
            target_value=desired*portfolio_open
            trade_value=target_value-shares*open_price
            cash-=trade_value+abs(trade_value)*fee
            shares=target_value/open_price
            actions+=1
        value=cash+shares*close_price
        values.append((df.index[i],value))
        realized_weights.append((shares*close_price/value) if value else 0.0)
    curve=pd.Series(dict(values),dtype=float)
    exposure=float(np.mean(realized_weights)) if realized_weights else 0.0
    return curve,_metrics(curve,initial,actions,exposure)

def compare_strategies(df: pd.DataFrame, **kwargs):
    signal_keys={"fast","slow","rsi_entry","rsi_exit","breakout_window"}
    signals=strategy_signals(df,**{k:v for k,v in kwargs.items() if k in signal_keys})
    warmup=max(int(kwargs.get("slow",60)),int(kwargs.get("breakout_window",55)),20)+1
    eval_df=df.iloc[warmup:].copy()
    curves={}; rows=[]
    for name,signal in signals.items():
        curve,metrics=simulate_target(eval_df,signal.reindex(eval_df.index),fee=kwargs.get("fee",.001))
        curves[name]=curve; rows.append({"Strategy":name,**metrics})
    vol_weights=volatility_target_weights(df,fast=int(kwargs.get("fast",20)),slow=int(kwargs.get("slow",60)),
                                          target_vol=float(kwargs.get("target_vol",.12)))
    vol_curve,vol_metrics=simulate_weights(eval_df,vol_weights.reindex(eval_df.index),fee=kwargs.get("fee",.001))
    curves["Vol-Target Trend"]=vol_curve
    rows.append({"Strategy":"Vol-Target Trend",**vol_metrics})
    base_shares=10000*(1-kwargs.get("fee",.001))/float(eval_df.Open.iloc[1])
    base=eval_df.Close.iloc[1:]*base_shares
    base_ret=base.pct_change().dropna(); years=max(len(base_ret)/252,1/252)
    base_metrics=_metrics(base,10000,1,1.0)
    rows.append({"Strategy":"Buy & Hold",**base_metrics})
    curves["Buy & Hold"]=base
    return pd.DataFrame(rows).sort_values("Sharpe Ratio",ascending=False),pd.DataFrame(curves).dropna()

