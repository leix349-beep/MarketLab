"""Portfolio landing page backed by the published research archives."""
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parent / "published_research"
zh = st.sidebar.radio("Language / 语言", ["English", "中文"], horizontal=True, key="global_language") == "中文"

with st.container(key="portfolio_hero"):
    st.caption("XIANG  /  RESEARCH PORTFOLIO")
    st.title("MarketLab")
    st.markdown("读懂市场，检验策略。" if zh else "Explore markets. Test strategies.")
    st.caption("探索股票与板块、比较风险，并复现历史策略实验。" if zh else
               "Explore stocks and sectors, compare risk, and reproduce historical strategy experiments.")

for col, path, label in zip(st.columns(3), (
    "stock_research.py", "pages/1_Sector_Research.py", "pages/5_Validation_Lab.py",
), ("研究股票", "浏览板块", "检验策略") if zh else ("Research a stock", "Explore sectors", "Test a strategy")):
    col.page_link(path, label=label, width="stretch")

market, evidence = st.tabs(["市场快照", "策略实证"] if zh else ["Market snapshot", "Strategy evidence"])

with market:
    snapshots = sorted((ROOT / "daily").glob("????-??-??.csv"))
    if snapshots:
        snapshot = pd.read_csv(snapshots[-1])
        st.subheader("市场快照" if zh else "Market snapshot")
        st.caption(("存档交易日 " if zh else "Archived session ") + snapshots[-1].stem)
        windows = {"1D": "return_1d", "5D": "return_5d", "1M": "return_21d"}
        window = st.radio("比较区间" if zh else "Return window", list(windows), horizontal=True)
        column = windows[window]
        data = snapshot.dropna(subset=[column]).sort_values(column)
        fig = px.bar(data, x=column, y="ticker", orientation="h",
                     color=data[column].ge(0), color_discrete_map={True: "#087e75", False: "#b34f48"},
                     template="marketlab")
        fig.update_layout(showlegend=False, height=420, xaxis_title=None, yaxis_title=None,
                          margin=dict(t=12, b=24, l=12, r=24))
        fig.update_xaxes(tickformat=".1%")
        fig.update_traces(hovertemplate="%{y}: %{x:+.2%}<extra></extra>")
        st.plotly_chart(fig, theme=None, width="stretch")
    else:
        st.info("暂无市场快照。" if zh else "No archived market snapshots yet.")

with evidence:
    folder = ROOT / "baseline_v2"
    series = pd.read_csv(folder / "daily_returns.csv", parse_dates=["execution_date"]).set_index("execution_date")
    metrics = pd.read_csv(folder / "metrics.csv")
    stress = st.toggle("压力成本" if zh else "Stress costs")
    cost = "adverse" if stress else "base"
    row = metrics[(metrics.strategy == "trend_relative_momentum") & (metrics.cost_scenario == cost)].iloc[0]
    for col, label, value in zip(st.columns(3), (
        "历史年化", "最大回撤", "夏普比率"
    ) if zh else ("Historical CAGR", "Maximum drawdown", "Sharpe ratio"),
        (f"{row.annual_return:.2%}", f"{row.maximum_drawdown:.2%}", f"{row.sharpe:.2f}")):
        col.metric(label, value)
    columns = {f"trend_relative_momentum__{cost}": "趋势动量" if zh else "Trend momentum",
               f"spy_vol_target__{cost}": "波动目标 SPY" if zh else "Volatility-targeted SPY"}
    wealth = (1 + series[list(columns)]).cumprod().mul(100).rename(columns=columns)
    fig = px.line(wealth, template="marketlab")
    fig.update_layout(height=390, xaxis_title=None, yaxis_title="起始值 100" if zh else "Growth of 100",
                      legend_title_text=None, legend=dict(orientation="h", y=1.1),
                      margin=dict(t=28, b=24, l=12, r=12))
    st.plotly_chart(fig, theme=None, width="stretch")
    st.caption("历史模拟结果。候选策略未通过完整验证门槛，无真实交易收益。" if zh else
               "Historical simulation. The candidate fell short of the validation gates. No live trading returns.")
    st.download_button("下载历史收益" if zh else "Download historical returns",
                       (folder / "daily_returns.csv").read_bytes(), "marketlab-daily-returns.csv", "text/csv")
