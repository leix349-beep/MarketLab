from datetime import date, timedelta
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
import yfinance as yf
from universe import ASSETS, asset_label

st.markdown("""<style>
[data-testid="stAppViewContainer"] {background:linear-gradient(145deg,#fff 0%,#f7fbff 55%,#f4f1ff 100%);}
[data-testid="stSidebar"] {background:linear-gradient(180deg,#f2f6fc 0%,#eef1f8 100%);}
h1 {letter-spacing:-.035em;} [data-testid="stMetric"] {background:rgba(255,255,255,.72);border:1px solid rgba(80,100,140,.12);padding:14px;border-radius:14px;}
</style>""",unsafe_allow_html=True)

language=st.sidebar.radio("Language / 语言",["English","中文"],horizontal=True,key="global_language")
zh=language=="中文"
st.title("MarketLab · 多资产对比" if zh else "MarketLab · Comparison Lab")
st.caption("最多同时比较4个资产；所有曲线使用相同日期范围。" if zh else "Compare up to four assets over one synchronized date range.")

selected=st.sidebar.multiselect("对比资产" if zh else "Assets",list(ASSETS),default=["SPY","QQQ","AAPL"],
                                max_selections=4,format_func=asset_label)
years=st.sidebar.slider("历史年数" if zh else "History (years)",1,10,5)
run=st.sidebar.button("运行对比" if zh else "Run Comparison",type="primary",width="stretch")

@st.cache_data(ttl=3600)
def load(tickers,start):
    series={}
    for ticker in tickers:
        d=yf.download(ticker,start=start,auto_adjust=True,progress=False)
        if isinstance(d.columns,pd.MultiIndex): d.columns=d.columns.get_level_values(0)
        if not d.empty: series[ticker]=d.Close
    return pd.DataFrame(series).dropna()

if run:
    st.session_state.comparison_request={"selected":selected,"years":years}

if "comparison_request" in st.session_state:
    request=st.session_state.comparison_request
    if len(request["selected"])<2:
        st.warning("请至少选择两个资产。" if zh else "Select at least two assets.")
    else:
        close=load(tuple(request["selected"]),date.today()-timedelta(days=request["years"]*365+30))
        returns=close.pct_change().dropna()
        growth=close/close.iloc[0]*100
        drawdown=close/close.cummax()-1
        rolling_vol=returns.rolling(21).std()*np.sqrt(252)
        total=growth.iloc[-1]/100-1; vol=returns.std()*np.sqrt(252)
        summary=pd.DataFrame({"Asset":total.index,"Total Return":total.values,"Annualized Volatility":vol.values})
        best=summary.sort_values("Total Return",ascending=False).iloc[0]
        a,b,c=st.columns(3)
        a.metric("最佳表现" if zh else "Top Performer",best.Asset,f"{best['Total Return']:.1%}")
        b.metric("资产数量" if zh else "Assets Compared",str(len(summary)))
        c.metric("共同交易日" if zh else "Common Trading Days",str(len(close)))
        left,right=st.columns(2)
        with left:
            fig=px.line(growth,labels={"value":"起点=100" if zh else "Growth of $100","index":"日期" if zh else "Date","variable":"资产" if zh else "Asset"},title="归一化表现" if zh else "Normalized Performance")
            fig.update_layout(height=390,margin=dict(l=10,r=10,t=45,b=10)); st.plotly_chart(fig,width="stretch")
        with right:
            fig=px.line(drawdown,labels={"value":"回撤" if zh else "Drawdown","index":"日期" if zh else "Date","variable":"资产" if zh else "Asset"},title="回撤" if zh else "Drawdown")
            fig.update_yaxes(tickformat=".0%")
            fig.update_layout(height=390,margin=dict(l=10,r=10,t=45,b=10)); st.plotly_chart(fig,width="stretch")
        left,right=st.columns(2)
        with left:
            fig=px.line(rolling_vol,labels={"value":"年化波动率" if zh else "Annualized Volatility","index":"日期" if zh else "Date","variable":"资产" if zh else "Asset"},title="21日滚动波动率" if zh else "21-Day Rolling Volatility")
            fig.update_yaxes(tickformat=".0%")
            fig.update_layout(height=390,margin=dict(l=10,r=10,t=45,b=10)); st.plotly_chart(fig,width="stretch")
        with right:
            corr=returns.corr()
            fig=px.imshow(corr,text_auto=".2f",zmin=-1,zmax=1,color_continuous_scale="RdBu_r",title="相关矩阵" if zh else "Correlation Matrix")
            fig.update_layout(height=390,margin=dict(l=10,r=10,t=45,b=10)); st.plotly_chart(fig,width="stretch")
        display=summary.copy(); display[["Total Return","Annualized Volatility"]]*=100
        if zh: display=display.rename(columns={"Asset":"资产","Total Return":"累计收益","Annualized Volatility":"年化波动率"})
        pct=["累计收益","年化波动率"] if zh else ["Total Return","Annualized Volatility"]
        st.dataframe(display,width="stretch",hide_index=True,column_config={c:st.column_config.NumberColumn(format="%.2f%%") for c in pct})
else:
    st.info("选择2至4个资产并运行对比。" if zh else "Choose two to four assets and run the comparison.")
