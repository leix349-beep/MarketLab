import os
from datetime import date, timedelta
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
import yfinance as yf
from strategy import backtest, grid_search
from analytics import risk_metrics, monthly_returns
from journal import save_experiment
from data_archive import archive_market_data, archive_experiment, archive_parameter_experiment, archive_daily_report
from universe import ASSETS, asset_label, sector_etf_for

st.markdown("""<style>
[data-testid="stAppViewContainer"] {background: linear-gradient(145deg,#ffffff 0%,#f8fbff 55%,#f4f1ff 100%);}
[data-testid="stSidebar"] {background: linear-gradient(180deg,#f2f6fc 0%,#eef1f8 100%);}
h1 {letter-spacing:-0.035em;} h2,h3 {letter-spacing:-0.018em;}
[data-testid="stMetric"] {background:rgba(255,255,255,.72);border:1px solid rgba(80,100,140,.12);padding:14px;border-radius:14px;}
[data-testid="stTabs"] button {font-weight:600;}
</style>""", unsafe_allow_html=True)

language = st.sidebar.radio("Language / 语言", ["English", "中文"], horizontal=True,key="global_language")
zh = language == "中文"
T = {
 "title": "MarketLab · 美股模拟交易研究台" if zh else "MarketLab · US Equity Research Lab",
 "caption": "研究与教育用途｜默认不发送任何订单｜先回测，再模拟" if zh else "Student research project · No orders are sent · Backtest before paper trading",
 "params": "研究参数" if zh else "Research Parameters", "asset": "股票 / ETF" if zh else "Stock / ETF",
 "years": "历史年数" if zh else "History (years)", "fast": "短期均线" if zh else "Fast Moving Average",
 "slow": "长期均线" if zh else "Slow Moving Average", "rsi": "买入 RSI 上限" if zh else "Maximum Buy RSI",
 "stop": "止损 %" if zh else "Stop Loss %", "take": "止盈 %" if zh else "Take Profit %",
 "cost": "手续费/滑点 %" if zh else "Fees / Slippage %", "run": "运行研究" if zh else "Run Analysis",
}
st.title(T["title"]); st.caption(T["caption"])

with st.sidebar:
    st.subheader("分析设置" if zh else "Analysis Setup")
    symbol=st.selectbox(T["asset"], list(ASSETS), format_func=asset_label)
    years=st.slider(T["years"], 1, 10, 5)
    with st.expander("策略参数" if zh else "Strategy Parameters",expanded=False):
        fast=st.slider(T["fast"], 5, 40, 20)
        slow=st.slider(T["slow"], 30, 200, 60)
        rsi=st.slider(T["rsi"], 25, 70, 55)
        stop=st.slider(T["stop"], 1, 20, 5)/100
        take=st.slider(T["take"], 2, 40, 10)/100
        fee=st.number_input(T["cost"], 0.0, 1.0, .10, .05)/100
    run=st.button(T["run"], type="primary", use_container_width=True)

if run:
    st.session_state.pop("grid_result", None)
    st.session_state.analysis_params = {
        "symbol": symbol, "years": years, "fast": fast, "slow": slow,
        "rsi": rsi, "stop": stop, "take": take, "fee": fee,
    }

@st.cache_data(ttl=3600)
def prices(ticker, start):
    d=yf.download(ticker, start=start, auto_adjust=True, progress=False)
    if isinstance(d.columns, pd.MultiIndex): d.columns=d.columns.get_level_values(0)
    return d

if "analysis_params" in st.session_state:
    active = st.session_state.analysis_params
    symbol, years = active["symbol"], active["years"]
    fast, slow, rsi = active["fast"], active["slow"], active["rsi"]
    stop, take, fee = active["stop"], active["take"], active["fee"]
    try:
        start=date.today()-timedelta(days=years*365+30)
        df=prices(symbol, start)
        if df.empty: raise ValueError("没有取得行情数据")
        spy=prices("SPY", start); sector_symbol=sector_etf_for(symbol)
        sector=prices(sector_symbol, start)
        stats=risk_metrics(df["Close"],spy["Close"])
        curve,trades,m=backtest(df,fast,slow,rsi,stop,take,fee)
        if run:
            experiment_params={"history_years":years,"fast_ma":fast,"slow_ma":slow,"rsi_limit":rsi,
                               "stop_loss":stop,"take_profit":take,"cost":fee}
            experiment_metrics={"strategy_return":m["总收益"],"max_drawdown":m["最大回撤"],
                                "sharpe":m["夏普比率"],"trades":m["交易次数"]}
            save_experiment(symbol, years, experiment_params, experiment_metrics)
            snapshot=archive_market_data(df,symbol,{"source":"Yahoo Finance via yfinance","interval":"1d","auto_adjust":True})
            archive_experiment(symbol,snapshot,experiment_params,experiment_metrics)
        benchmark=df.loc[curve.index,"Close"]/df.loc[curve.index,"Close"].iloc[0]*10000
        a,b,c,d=st.columns(4)
        a.metric("策略收益" if zh else "Strategy Return",f"{m['总收益']:.1%}")
        b.metric("最大回撤" if zh else "Maximum Drawdown",f"{m['最大回撤']:.1%}")
        c.metric("夏普比率" if zh else "Sharpe Ratio",f"{m['夏普比率']:.2f}")
        d.metric("交易次数" if zh else "Number of Trades",str(m["交易次数"]))
        fig=go.Figure(); fig.add_scatter(x=curve.index,y=curve,name="策略" if zh else "Strategy")
        fig.add_scatter(x=benchmark.index,y=benchmark,name="买入并持有" if zh else "Buy and Hold")
        fig.update_layout(height=420,margin=dict(l=10,r=10,t=30,b=10),yaxis_title="账户价值（美元）" if zh else "Portfolio Value (USD)")
        st.plotly_chart(fig,use_container_width=True)

        st.subheader("标的资产风险与基准分析" if zh else "Underlying Asset Risk & Benchmark Analysis")
        e,f,g,h,i=st.columns(5)
        e.metric("标的年化收益" if zh else "Asset Annualized Return",f"{stats['annual_return']:.1%}")
        f.metric("标的年化波动率" if zh else "Asset Annualized Volatility",f"{stats['volatility']:.1%}")
        g.metric("Beta（对 SPY）" if zh else "Beta vs SPY",f"{stats['beta']:.2f}")
        h.metric("Alpha（年化）" if zh else "Annualized Alpha",f"{stats['alpha']:.1%}")
        i.metric("Sortino 比率" if zh else "Sortino Ratio",f"{stats['sortino']:.2f}")

        normalized=pd.concat({symbol:df.Close/df.Close.iloc[0]*100,
                              "SPY":spy.Close/spy.Close.iloc[0]*100,
                              sector_symbol:sector.Close/sector.Close.iloc[0]*100},axis=1).dropna()
        compare=px.line(normalized,labels={"value":"累计价值（起点=100）" if zh else "Growth of $100","index":"日期" if zh else "Date","variable":"资产" if zh else "Asset"})
        compare.update_layout(height=350,margin=dict(l=10,r=10,t=25,b=10))
        st.plotly_chart(compare,use_container_width=True)

        tabs=st.tabs(["市场图表" if zh else "Market Chart","数学实验室" if zh else "Math Lab","交易记录" if zh else "Trade Log","参数实验" if zh else "Parameter Experiments","每日研究报告" if zh else "Daily Research Report"])
        chart_tab,math_tab,tab1,tab2,tab3=tabs
        with chart_tab:
            candle=go.Figure(data=[go.Candlestick(x=df.index,open=df.Open,high=df.High,low=df.Low,close=df.Close,name=symbol)])
            candle.add_scatter(x=df.index,y=df.Close.rolling(fast).mean(),name=f"MA {fast}")
            candle.add_scatter(x=df.index,y=df.Close.rolling(slow).mean(),name=f"MA {slow}")
            candle.update_layout(height=500,xaxis_rangeslider_visible=False,margin=dict(l=10,r=10,t=30,b=10))
            st.plotly_chart(candle,use_container_width=True)
            volume=px.bar(df,x=df.index,y="Volume",labels={"Volume":"成交量" if zh else "Volume","index":"日期" if zh else "Date"})
            volume.update_layout(height=220,margin=dict(l=10,r=10,t=10,b=10)); st.plotly_chart(volume,use_container_width=True)
        with math_tab:
            st.markdown("### " + ("数学如何进入这个项目" if zh else "How mathematics enters the project"))
            st.markdown(("**Beta** = Cov(股票收益, 市场收益) / Var(市场收益)，衡量股票对市场变化的敏感度。\n\n"
                         "**Alpha** 是扣除市场风险解释后的年化超额收益。\n\n"
                         "**波动率** 是日收益标准差乘以 √252；这里使用一年约 252 个交易日。\n\n"
                         "**Sortino Ratio** 只把下跌波动视为风险，比普通夏普比率更关注不利结果。") if zh else
                        ("**Beta** = Cov(asset returns, market returns) / Var(market returns), measuring sensitivity to market movements.\n\n"
                         "**Alpha** is annualized return not explained by exposure to the market benchmark.\n\n"
                         "**Volatility** is the standard deviation of daily returns multiplied by √252.\n\n"
                         "**Sortino Ratio** treats only downside variation as risk, focusing on harmful outcomes."))
            returns=df.Close.pct_change().dropna()
            hist=px.histogram(returns,x="Close",nbins=50,labels={"Close":"日收益率" if zh else "Daily Return"})
            hist.add_vline(x=float(returns.mean()),line_dash="dash",line_color="#ef4444",
                           annotation_text="平均值" if zh else "Mean",annotation_position="top right")
            hist.update_layout(height=330,margin=dict(l=10,r=10,t=25,b=10)); st.plotly_chart(hist,use_container_width=True)
            heat=monthly_returns(df.Close)
            hm=px.imshow(heat,aspect="auto",color_continuous_scale="RdYlGn",color_continuous_midpoint=0,
                         labels={"x":"月份" if zh else "Month","y":"年份" if zh else "Year","color":"收益" if zh else "Return"})
            hm.update_layout(height=330,margin=dict(l=10,r=10,t=25,b=10)); st.plotly_chart(hm,use_container_width=True)
        zh_labels={"buy":"买入","sell":"卖出","stop_loss":"止损","take_profit":"止盈","trend_reversal":"趋势反转","trend_rsi":"趋势 + RSI"}
        en_labels={"buy":"Buy","sell":"Sell","stop_loss":"Stop loss","take_profit":"Take profit","trend_reversal":"Trend reversal","trend_rsi":"Trend + RSI"}
        shown=trades.copy()
        if len(shown):
            labels = zh_labels if zh else en_labels
            shown["action"]=shown["action"].replace(labels); shown["reason"]=shown["reason"].replace(labels)
            shown["date"] = pd.to_datetime(shown["date"]).dt.strftime("%Y-%m-%d")
        shown=shown.rename(columns={"date":"日期","action":"动作","price":"价格","reason":"原因"} if zh else {"date":"Date","action":"Action","price":"Price","reason":"Reason"})
        with tab1:
            price_col = "价格" if zh else "Price"
            st.dataframe(shown.sort_values("日期" if zh else "Date",ascending=False),use_container_width=True,hide_index=True,
                         column_config={price_col: st.column_config.NumberColumn(format="$%.2f")})
        with tab2:
            st.caption("比较多组均线参数；结果仅用于研究，不代表未来表现。" if zh else "Compare moving-average combinations. Historical results do not predict future performance.")
            if st.button("运行参数实验" if zh else "Run Parameter Experiment"):
                st.session_state.grid_result = grid_search(df)
                archive_parameter_experiment(st.session_state.grid_result,symbol)
            if "grid_result" in st.session_state:
                experiment = st.session_state.grid_result.copy()
                if not zh:
                    experiment = experiment.rename(columns={
                        "短均线":"Fast MA", "长均线":"Slow MA", "总收益":"Total Return",
                        "最大回撤":"Maximum Drawdown", "夏普比率":"Sharpe Ratio", "交易次数":"Number of Trades",
                    })
                    percent_cols = ["Total Return", "Maximum Drawdown"]
                else:
                    percent_cols = ["总收益", "最大回撤"]
                experiment[percent_cols] = experiment[percent_cols] * 100
                st.dataframe(experiment,use_container_width=True,hide_index=True,
                    column_config={name: st.column_config.NumberColumn(format="%.2f%%") for name in percent_cols})
        with tab3:
            last=float(df.Close.iloc[-1]); action_key="hold"
            if len(trades): action_key=str(trades.iloc[-1]["action"])
            benchmark_return=benchmark.iloc[-1]/10000-1
            action_zh={"buy":"买入","sell":"卖出","hold":"观望"}.get(action_key,action_key)
            action_en={"buy":"Buy","sell":"Sell","hold":"Hold"}.get(action_key,action_key)
            if zh:
                report=f"""# {date.today()} {symbol} 每日研究报告

- 最新收盘价：${last:.2f}
- 模型最近动作：{action_zh}
- 策略累计收益：{m['总收益']:.1%}
- 买入并持有累计收益：{benchmark_return:.1%}
- 策略最大回撤：{m['最大回撤']:.1%}
- 策略夏普比率：{m['夏普比率']:.2f}
- 参数：MA {fast}/{slow}，RSI < {rsi}，止损 {stop:.0%}，止盈 {take:.0%}

## 初步观察

当前策略相对买入并持有的收益差异为 {m['总收益']-benchmark_return:+.1%}。该结果来自历史回测，尚未经过样本外滚动验证。

> 本报告仅用于教育与研究，不构成投资建议。"""
            else:
                report=f"""# {date.today()} {symbol} Daily Research Report

- Latest close: ${last:.2f}
- Most recent model action: {action_en}
- Strategy cumulative return: {m['总收益']:.1%}
- Buy-and-hold cumulative return: {benchmark_return:.1%}
- Strategy maximum drawdown: {m['最大回撤']:.1%}
- Strategy Sharpe ratio: {m['夏普比率']:.2f}
- Parameters: MA {fast}/{slow}, RSI < {rsi}, stop loss {stop:.0%}, take profit {take:.0%}

## Preliminary Observation

The strategy's return difference versus buy and hold is {m['总收益']-benchmark_return:+.1%}. This historical backtest has not yet undergone walk-forward out-of-sample validation.

> This report is for education and research only and is not investment advice."""
            st.markdown(report)
            if run:
                archive_daily_report(report,symbol,"zh" if zh else "en")
            st.download_button("下载 Markdown 报告" if zh else "Download Markdown Report",report,file_name=f"{date.today()}-{symbol}-report.md")
    except Exception as e:
        st.error(f"暂时无法取得数据：{e}")
        st.info("请确认网络可用，然后重新运行。")



