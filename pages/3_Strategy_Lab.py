from datetime import date,timedelta
import pandas as pd
import plotly.express as px
import streamlit as st
import yfinance as yf
from universe import ASSETS,asset_label
from strategy_library import compare_strategies
from data_archive import archive_parameter_experiment

st.markdown("""<style>
[data-testid="stAppViewContainer"] {background:linear-gradient(145deg,#fff 0%,#f7fbff 55%,#f4f1ff 100%);}
[data-testid="stSidebar"] {background:linear-gradient(180deg,#f2f6fc 0%,#eef1f8 100%);}
h1 {letter-spacing:-.035em;} [data-testid="stMetric"] {background:rgba(255,255,255,.72);border:1px solid rgba(80,100,140,.12);padding:14px;border-radius:14px;}
</style>""",unsafe_allow_html=True)

language=st.sidebar.radio("Language / 语言",["English","中文"],horizontal=True,key="global_language")
zh=language=="中文"
st.title("Xiang’s MarketLab · 策略实验室" if zh else "Xiang’s MarketLab · Strategy Lab")
st.caption("在相同数据、成本和成交时点下公平比较不同规则。" if zh else "Compare rule-based strategies under identical data, cost and execution assumptions.")

symbol=st.sidebar.selectbox("股票 / ETF" if zh else "Stock / ETF",list(ASSETS),format_func=asset_label,key="strategy_symbol")
years=st.sidebar.slider("历史年数" if zh else "History (years)",1,10,5,key="strategy_years")
with st.sidebar.expander("模型参数" if zh else "Model Parameters",expanded=False):
    fast=st.slider("短期均线" if zh else "Fast MA",5,40,20)
    slow=st.slider("长期均线" if zh else "Slow MA",30,200,60)
    rsi_entry=st.slider("均值回归买入 RSI" if zh else "Mean-Reversion Entry RSI",15,45,30)
    rsi_exit=st.slider("均值回归退出 RSI" if zh else "Mean-Reversion Exit RSI",45,75,55)
    breakout=st.slider("突破窗口" if zh else "Breakout Window",20,120,55)
    fee=st.number_input("手续费/滑点 %" if zh else "Fees / Slippage %",0.0,1.0,.10,.05)/100
run=st.sidebar.button("比较策略" if zh else "Compare Strategies",type="primary",width="stretch")

@st.cache_data(ttl=3600)
def prices(ticker,start):
    d=yf.download(ticker,start=start,auto_adjust=True,progress=False)
    if isinstance(d.columns,pd.MultiIndex): d.columns=d.columns.get_level_values(0)
    return d

if run:
    st.session_state.strategy_request={"symbol":symbol,"years":years,"fast":fast,"slow":slow,
        "rsi_entry":rsi_entry,"rsi_exit":rsi_exit,"breakout_window":breakout,"fee":fee}

if "strategy_request" in st.session_state:
    q=st.session_state.strategy_request
    df=prices(q["symbol"],date.today()-timedelta(days=q["years"]*365+220))
    results,curves=compare_strategies(df,fast=q["fast"],slow=q["slow"],rsi_entry=q["rsi_entry"],
        rsi_exit=q["rsi_exit"],breakout_window=q["breakout_window"],fee=q["fee"])
    if run: archive_parameter_experiment(results,q["symbol"]+"_strategy_comparison")
    best=results.iloc[0]; top_return=results.sort_values("Total Return",ascending=False).iloc[0]
    passive=results[results.Strategy=="Buy & Hold"].iloc[0]
    a,b,c,d=st.columns(4)
    a.metric("最高夏普策略" if zh else "Highest-Sharpe Strategy",best.Strategy,f"{best['Sharpe Ratio']:.2f}")
    b.metric("最高收益策略" if zh else "Top-Return Strategy",top_return.Strategy)
    c.metric("最高累计收益" if zh else "Highest Total Return",f"{top_return['Total Return']:.1%}")
    d.metric("买入持有累计收益" if zh else "Buy & Hold Return",f"{passive['Total Return']:.1%}")
    normalized=curves/curves.iloc[0]*100
    fig=px.line(normalized,labels={"value":"起点=100" if zh else "Growth of $100","index":"日期" if zh else "Date","variable":"策略" if zh else "Strategy"})
    fig.update_layout(height=480,margin=dict(l=10,r=10,t=25,b=10)); st.plotly_chart(fig,width="stretch")
    shown=results.copy()
    if zh: shown=shown.rename(columns={"Strategy":"策略","Total Return":"累计收益","Annualized Return":"年化收益","Maximum Drawdown":"最大回撤","Sharpe Ratio":"夏普比率","Trade Actions":"交易动作数"})
    pct=["累计收益","年化收益","最大回撤"] if zh else ["Total Return","Annualized Return","Maximum Drawdown"]
    shown[pct]=shown[pct]*100
    st.dataframe(shown,width="stretch",hide_index=True,column_config={c:st.column_config.NumberColumn(format="%.2f%%") for c in pct})
    active=results[results.Strategy!="Buy & Hold"].sort_values("Sharpe Ratio",ascending=False).iloc[0]
    return_gap=active["Total Return"]-passive["Total Return"]
    drawdown_improvement=active["Maximum Drawdown"]-passive["Maximum Drawdown"]
    st.markdown("### "+("初步研究解读" if zh else "Preliminary Interpretation"))
    if zh:
        st.info(f"在当前样本中，风险调整表现最好的主动规则是 **{active.Strategy}**。其累计收益相对买入并持有为 {return_gap:+.1%}，最大回撤差异为 {drawdown_improvement:+.1%}。这说明降低下行风险可能伴随收益机会成本；结论仍需样本外验证。")
    else:
        st.info(f"In this sample, the highest-Sharpe active rule is **{active.Strategy}**. Its cumulative-return difference versus buy and hold is {return_gap:+.1%}, while its maximum-drawdown difference is {drawdown_improvement:+.1%}. Lower downside risk may carry an opportunity cost; this result still requires out-of-sample validation.")
    st.markdown("### "+("策略定义" if zh else "Strategy Definitions"))
    definitions=("- **趋势策略**：短均线高于长均线时持有。\n- **均值回归**：RSI低于阈值买入，高于退出阈值卖出。\n- **突破策略**：价格突破过去窗口高点后持有，跌破20日均线退出。\n- **趋势 + RSI**：趋势为正且RSI不过热时进入，趋势反转后退出。" if zh else
    "- **Trend:** hold while the fast moving average is above the slow moving average.\n- **Mean Reversion:** enter below the RSI threshold and exit above the recovery threshold.\n- **Breakout:** enter above the prior rolling high and exit below the 20-day average.\n- **Trend + RSI:** enter during a positive trend when RSI is not overheated; exit on trend reversal.")
    st.markdown(definitions)
    st.warning("所有策略均为历史模拟，尚未完成样本外滚动验证。" if zh else "All strategies are historical simulations and have not yet passed walk-forward out-of-sample validation.")
else:
    st.info("选择标的与参数，然后比较策略。" if zh else "Choose an asset and parameters, then compare strategies.")

