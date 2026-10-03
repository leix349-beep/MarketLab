from datetime import date,timedelta
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf
from analytics import market_model
from universe import ASSETS,asset_label
from data_archive import archive_parameter_experiment

st.markdown("""<style>
[data-testid="stAppViewContainer"] {background:linear-gradient(145deg,#fff 0%,#f7fbff 55%,#f4f1ff 100%);}
[data-testid="stSidebar"] {background:linear-gradient(180deg,#f2f6fc 0%,#eef1f8 100%);}
h1 {letter-spacing:-.035em;} [data-testid="stMetric"] {background:rgba(255,255,255,.72);border:1px solid rgba(80,100,140,.12);padding:14px;border-radius:14px;}
</style>""",unsafe_allow_html=True)

language=st.sidebar.radio("Language / 语言",["English","中文"],horizontal=True,key="global_language")
zh=language=="中文"
st.title("Xiang’s MarketLab · 回归实验室" if zh else "Xiang’s MarketLab · Regression Lab")
st.caption("用市场模型区分系统性风险与标的特有变化。" if zh else "Use a market model to separate systematic exposure from asset-specific variation.")

symbol=st.sidebar.selectbox("研究标的" if zh else "Research Asset",list(ASSETS),index=list(ASSETS).index("AAPL"),format_func=asset_label)
benchmark=st.sidebar.selectbox("市场基准" if zh else "Market Benchmark",["SPY","QQQ","IWM"],index=0)
years=st.sidebar.slider("历史年数" if zh else "History (years)",1,10,5)
run=st.sidebar.button("运行回归" if zh else "Run Regression",type="primary",width="stretch")

@st.cache_data(ttl=3600)
def prices(ticker,start):
    d=yf.download(ticker,start=start,auto_adjust=True,progress=False)
    if isinstance(d.columns,pd.MultiIndex): d.columns=d.columns.get_level_values(0)
    return d.Close

if run:
    st.session_state.regression_request={"symbol":symbol,"benchmark":benchmark,"years":years}

if "regression_request" in st.session_state:
    q=st.session_state.regression_request; start=date.today()-timedelta(days=q["years"]*365+30)
    asset=prices(q["symbol"],start); market=prices(q["benchmark"],start)
    metrics,detail,rolling_beta=market_model(asset,market)
    if run:
        archive_parameter_experiment(pd.DataFrame([{"Asset":q["symbol"],"Benchmark":q["benchmark"],**metrics}]),q["symbol"]+"_regression")
    a,b,c,d=st.columns(4)
    a.metric("Beta",f"{metrics['beta']:.2f}")
    b.metric("年化 Alpha" if zh else "Annualized Alpha",f"{metrics['alpha_annual']:.2%}")
    c.metric("决定系数 R²" if zh else "R-Squared",f"{metrics['r_squared']:.2%}")
    d.metric("样本数量" if zh else "Observations",f"{metrics['observations']:,}")
    st.caption((f"Beta 95% bootstrap置信区间：{metrics['beta_ci_low']:.2f} 至 {metrics['beta_ci_high']:.2f}" if zh else
                f"Beta 95% bootstrap confidence interval: {metrics['beta_ci_low']:.2f} to {metrics['beta_ci_high']:.2f}"))
    left,right=st.columns(2)
    with left:
        ordered=detail.sort_values("market")
        scatter=go.Figure()
        scatter.add_scatter(x=detail["market"],y=detail["asset"],mode="markers",name="Daily observations" if not zh else "每日观测",
                            marker=dict(size=6,color="#4f86c6",opacity=.42))
        scatter.add_scatter(x=ordered["market"],y=ordered["predicted"],mode="lines",name="OLS fit" if not zh else "OLS拟合",
                            line=dict(color="#ef5350",width=3))
        scatter.update_layout(title="市场收益与标的收益" if zh else "Market vs Asset Returns",
                              xaxis_title=q["benchmark"]+(" 日收益" if zh else " Daily Return"),
                              yaxis_title=q["symbol"]+(" 日收益" if zh else " Daily Return"))
        scatter.update_xaxes(tickformat=".1%"); scatter.update_yaxes(tickformat=".1%")
        scatter.update_layout(height=430,margin=dict(l=10,r=10,t=45,b=10)); st.plotly_chart(scatter,width="stretch")
    with right:
        rb=px.line(rolling_beta,labels={"value":"Beta","index":"日期" if zh else "Date"},title="63日滚动 Beta" if zh else "63-Day Rolling Beta")
        rb.add_hline(y=metrics["beta"],line_dash="dash",line_color="#ef4444")
        rb.update_layout(height=430,showlegend=False,margin=dict(l=10,r=10,t=45,b=10)); st.plotly_chart(rb,width="stretch")
    left,right=st.columns(2)
    with left:
        hist=px.histogram(detail,x="residual",nbins=50,title="残差分布" if zh else "Residual Distribution",
                          labels={"residual":"无法被市场解释的日收益" if zh else "Unexplained Daily Return"})
        hist.update_xaxes(tickformat=".1%"); hist.update_layout(height=360,margin=dict(l=10,r=10,t=45,b=10)); st.plotly_chart(hist,width="stretch")
    with right:
        abnormal=(1+detail.residual).cumprod()-1
        car=px.line(abnormal,labels={"value":"累计异常收益" if zh else "Cumulative Abnormal Return","index":"日期" if zh else "Date"},title="累计异常收益" if zh else "Cumulative Abnormal Return")
        car.update_yaxes(tickformat=".0%"); car.update_layout(height=360,showlegend=False,margin=dict(l=10,r=10,t=45,b=10)); st.plotly_chart(car,width="stretch")
    st.markdown("### "+("数学模型" if zh else "Mathematical Model"))
    st.latex(r"r_{asset,t}=\alpha+\beta r_{market,t}+\varepsilon_t")
    if zh:
        st.markdown("- **Beta**：标的对市场变化的敏感度。\n- **Alpha**：模型无法由市场暴露解释的平均收益。\n- **R²**：标的收益变化中，可被市场模型解释的比例。\n- **残差 ε**：公司、行业、新闻和随机因素留下的未解释部分。\n- **Bootstrap区间**：反复重抽样，衡量Beta估计的不确定性。")
    else:
        st.markdown("- **Beta:** sensitivity to market returns.\n- **Alpha:** average return not explained by market exposure.\n- **R²:** fraction of asset-return variation explained by the model.\n- **Residual ε:** unexplained company, sector, news and random variation.\n- **Bootstrap interval:** repeated resampling used to quantify uncertainty in Beta.")
    st.warning("回归描述历史关系，不证明因果关系，也不保证未来保持稳定。" if zh else "Regression describes historical association; it does not establish causality or guarantee stability.")
else:
    st.info("选择标的和基准，然后运行回归。" if zh else "Choose an asset and benchmark, then run the regression.")

