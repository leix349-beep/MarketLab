from datetime import date, timedelta
import pandas as pd
import plotly.express as px
import streamlit as st
import yfinance as yf
from universe import SECTOR_ETFS
from data_archive import archive_sector_snapshot
from ui_theme import render_empty_state

language=st.sidebar.radio("Language / 语言",["English","中文"],horizontal=True,key="global_language")
zh=language=="中文"
st.title("Xiang’s MarketLab · 板块研究" if zh else "Xiang’s MarketLab · Sector Research")
st.caption("独立的市场级研究空间，不依赖个股分析选择。" if zh else "A market-level research workspace independent of the selected stock analysis.")

@st.cache_data(ttl=3600)
def load_sector_data():
    rows=[]; start=date.today()-timedelta(days=400)
    for sector,ticker in SECTOR_ETFS.items():
        d=yf.download(ticker,start=start,auto_adjust=True,progress=False)
        if isinstance(d.columns,pd.MultiIndex): d.columns=d.columns.get_level_values(0)
        if d.empty: continue
        close=d.Close.dropna(); daily=close.pct_change().dropna()
        def trailing(days):
            return close.iloc[-1]/close.iloc[-min(days,len(close))]-1
        rows.append({"Sector":sector,"ETF":ticker,"1M":trailing(22),"3M":trailing(66),
                     "6M":trailing(126),"12M":trailing(252),"Volatility":daily.std()*(252**.5)})
    return pd.DataFrame(rows)

period=st.segmented_control("排名周期" if zh else "Ranking Period",["1M","3M","6M","12M"],default="3M")
if st.button("加载板块研究" if zh else "Load Sector Research",type="primary"):
    st.session_state.sector_page_result=load_sector_data()
    archive_sector_snapshot(st.session_state.sector_page_result,"all-periods")

if "sector_page_result" in st.session_state:
    sectors=st.session_state.sector_page_result.sort_values(period,ascending=False).copy()
    best,worst=sectors.iloc[0],sectors.iloc[-1]
    a,b,c=st.columns(3)
    a.metric("最强板块" if zh else "Strongest Sector",best.Sector,f"{best[period]:.1%}")
    b.metric("最弱板块" if zh else "Weakest Sector",worst.Sector,f"{worst[period]:.1%}")
    c.metric("板块收益差" if zh else "Sector Spread",f"{best[period]-worst[period]:.1%}")
    chart=px.bar(sectors,x=period,y="Sector",orientation="h",color=period,color_continuous_scale="RdYlGn",
                 labels={period:(period+" 收益") if zh else period+" Return","Sector":"板块" if zh else "Sector"})
    chart.update_layout(height=480,yaxis={"categoryorder":"total ascending"},margin=dict(l=10,r=10,t=25,b=10))
    st.plotly_chart(chart,width="stretch")
    shown=sectors.rename(columns={"Sector":"板块","Volatility":"年化波动率"} if zh else {})
    pct=["1M","3M","6M","12M","年化波动率" if zh else "Volatility"]
    shown[pct]=shown[pct]*100
    st.dataframe(shown,width="stretch",hide_index=True,
        column_config={col:st.column_config.NumberColumn(format="%.2f%%") for col in pct})
else:
    render_empty_state(
        "板块轮动" if zh else "Sector rotation",
        "比较市场内部的强弱变化" if zh else "See where market leadership is shifting",
        ("一次加载11个标准行业 ETF，并在同一周期内比较收益与波动率。" if zh else
         "Load 11 standard sector ETFs and compare return and volatility over one consistent period."),
        (["选择1至12个月的排名周期", "加载板块研究", "比较领先、落后与板块收益差"] if zh else
         ["Choose a 1–12 month ranking period", "Load sector research", "Compare leaders, laggards, and dispersion"]),
    )
