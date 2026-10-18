from datetime import date
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from monitoring import breadth_history, build_forward_scorecard, load_snapshot_history, trading_day_lag

language = st.sidebar.radio("Language / 语言", ["English", "中文"], horizontal=True, key="global_language")
zh = language == "中文"
st.title("Xiang’s MarketLab · 每日监控" if zh else "Xiang’s MarketLab · Daily Monitor")
st.caption("把每天自动保存的观察放在同一张可审计的时间线上。" if zh else
           "An auditable timeline of the observations saved automatically each day.")

history = load_snapshot_history()
if history.empty:
    st.warning("尚未找到每日记录。" if zh else "No daily snapshots have been saved yet.")
    st.stop()

latest_date = history["date"].max()
latest = history.loc[history["date"] == latest_date].copy()
breadth = breadth_history(history)
lag = trading_day_lag(latest_date, date.today())
above = int((latest["trend_state"] == "Above MA20/60").sum())

a, b, c, d = st.columns(4)
a.metric("最新行情日期" if zh else "Latest Market Date", latest_date.strftime("%Y-%m-%d"))
b.metric("监控标的" if zh else "Assets Monitored", str(len(latest)))
c.metric("双均线上方" if zh else "Above Both Averages", f"{above} / {len(latest)}")
d.metric("数据延迟" if zh else "Data Freshness", ("当天" if lag == 0 else f"{lag} 个交易日") if zh else ("Current" if lag == 0 else f"{lag} trading day(s) behind"))

if lag:
    st.warning(("行情源尚未提供最新完整日线；页面保留最后一个已确认交易日，不会用重复数据冒充新记录。" if zh else
                "The data source has not supplied the latest complete daily bar. The page keeps the last confirmed market day rather than presenting duplicate data as new."))

paper_dir = Path("published_research/paper_tracking")
signal_paths = sorted((paper_dir / "signals").glob("????-??-??.csv"))
if signal_paths:
    signals = pd.read_csv(signal_paths[-1])
    if "candidate" not in signals:
        signals["candidate"] = "growth_50"
    signal_date = str(signals["signal_date"].iloc[0])
    scorecard_path = paper_dir / "scorecard.csv"
    scorecard_status = pd.read_csv(scorecard_path) if scorecard_path.exists() else pd.DataFrame()

    st.subheader("纸面候选" if zh else "Paper Candidates")
    st.caption(("冻结权重只用于前瞻验证，不会发送订单。" if zh else
                "Frozen allocations are for prospective validation only; no order is sent."))
    p1, p2, p3 = st.columns(3)
    p1.metric("最新信号日" if zh else "Latest Signal Date", signal_date)
    p2.metric("候选数量" if zh else "Candidates", str(signals["candidate"].nunique()))
    if scorecard_status.empty:
        mature_text = "0"
        status_text = "收集中" if zh else "Collecting"
    else:
        mature_text = str(int(scorecard_status["non_overlapping_observations"].max()))
        statuses = sorted(set(scorecard_status["review_status"].astype(str)))
        status_text = ", ".join(statuses)
    p3.metric("不重叠成熟样本" if zh else "Mature Non-Overlapping", mature_text,
              help=status_text)

    allocation = signals[["candidate", "ticker", "weight"]].copy()
    allocation["candidate"] = allocation["candidate"].replace({
        "growth_25": "25% Conservative" if not zh else "25% 保守",
        "growth_50": "50% Current" if not zh else "50% 现行",
    })
    allocation_chart = px.bar(
        allocation, x="ticker", y="weight", color="candidate", barmode="group",
        labels={"ticker": "资产" if zh else "Asset",
                "weight": "权重" if zh else "Weight",
                "candidate": "候选" if zh else "Candidate"},
    )
    allocation_chart.update_yaxes(tickformat=".0%")
    allocation_chart.update_layout(height=330, margin=dict(l=10, r=10, t=20, b=10),
                                   legend_title_text=None)
    st.plotly_chart(allocation_chart, width="stretch")
    if scorecard_status.empty:
        st.info("首批5日结果尚未成熟，当前不会评价优劣。" if zh else
                "The first five-session outcomes are not mature yet; no ranking is shown.")
    else:
        paper_shown = scorecard_status[["candidate", "non_overlapping_observations",
                                        "non_overlapping_average_excess",
                                        "non_overlapping_spy_win_rate", "review_status"]].copy()
        paper_shown["non_overlapping_average_excess"] *= 100
        paper_shown["non_overlapping_spy_win_rate"] *= 100
        st.dataframe(paper_shown, width="stretch", hide_index=True,
                     column_config={
                         "non_overlapping_average_excess": st.column_config.NumberColumn(
                             "平均超额" if zh else "Avg Excess", format="%.2f%%"),
                         "non_overlapping_spy_win_rate": st.column_config.NumberColumn(
                             "跑赢SPY" if zh else "Beat SPY", format="%.1f%%"),
                     })

registry_path = Path("published_research/model_training/experiment_registry.csv")
if registry_path.exists():
    registry = pd.read_csv(registry_path)
    provenance_path = Path("published_research/model_training/data_provenance.csv")
    provenance = pd.read_csv(provenance_path).iloc[0] if provenance_path.exists() else None
    provenance_history_path = Path("published_research/model_training/data_provenance_history.csv")
    provenance_history = (pd.read_csv(provenance_history_path)
                          if provenance_history_path.exists() else pd.DataFrame())
    revision_count = 0
    if provenance is not None and not provenance_history.empty:
        revision_count = int((provenance_history["end_date"].astype(str) ==
                              str(provenance["end_date"])).sum())
    st.subheader("研究纪律" if zh else "Research Discipline")
    st.caption(("失败实验同样保留，避免重复试错或只展示好结果。" if zh else
                "Failed experiments stay visible to prevent repeated testing and result cherry-picking."))
    r1, r2, r3, r4 = st.columns(4)
    r1.metric("已登记实验" if zh else "Registered Experiments", str(len(registry)))
    r2.metric("已拒绝" if zh else "Rejected", str(int((registry["decision"] == "REJECTED").sum())))
    r3.metric("纸面跟踪" if zh else "Paper Tracking",
              str(int((registry["decision"] == "PAPER_TRACKING").sum())))
    r4.metric("数据指纹" if zh else "Data Fingerprint",
              str(provenance["data_sha256"])[:10] if provenance is not None else "—",
              delta=((f"{revision_count} 个版本" if zh else f"{revision_count} version(s)")
                     if revision_count > 1 else None),
              delta_color="inverse",
              help=("历史数据若被供应商修订，这个指纹会改变。" if zh else
                    "This fingerprint changes when the provider revises the historical dataset."))
    if revision_count > 1:
        st.warning(("同一最新行情日期出现多个数据版本；比较模型结果时请检查供应商修订。" if zh else
                    "Multiple dataset versions exist for the same latest market date; check provider revisions before comparing model results."))
    with st.expander("查看实验账本" if zh else "View experiment ledger"):
        st.dataframe(registry[["experiment_id", "family", "validation_scope", "decision", "reason"]],
                     width="stretch", hide_index=True)
        if provenance is not None:
            st.caption((f"训练数据：{provenance['start_date']} 至 {provenance['end_date']} · "
                        f"{int(provenance['rows']):,} 行 · {int(provenance['tickers'])} 个标的") if zh else
                       (f"Training data: {provenance['start_date']} to {provenance['end_date']} · "
                        f"{int(provenance['rows']):,} rows · {int(provenance['tickers'])} assets"))

left, right = st.columns([1.05, 1])
with left:
    breadth_chart = px.line(breadth, x="date", y="breadth", markers=True,
                            title="市场广度：同时位于MA20和MA60上方的比例" if zh else "Market Breadth: Share Above MA20 and MA60")
    breadth_chart.update_yaxes(tickformat=".0%", range=[0, 1.05], title=None)
    breadth_chart.update_xaxes(title=None)
    breadth_chart.update_layout(height=380, margin=dict(l=10, r=10, t=50, b=10), showlegend=False)
    st.plotly_chart(breadth_chart, width="stretch")
with right:
    map_chart = px.scatter(latest, x="return_21d", y="rsi14", text="ticker", color="trend_state",
                           size="volatility_21d_annualized", size_max=28,
                           title="最新强弱地图" if zh else "Latest Strength Map",
                           labels={"return_21d": "21日收益" if zh else "21-Day Return",
                                   "rsi14": "RSI14", "trend_state": "趋势" if zh else "Trend"})
    map_chart.add_hline(y=70, line_dash="dot", line_color="#ef4444")
    map_chart.update_xaxes(tickformat=".0%")
    map_chart.update_traces(textposition="top center")
    map_chart.update_layout(height=380, margin=dict(l=10, r=10, t=50, b=10))
    st.plotly_chart(map_chart, width="stretch")

st.subheader("标的时间线" if zh else "Asset Timeline")
ticker = st.selectbox("选择标的" if zh else "Select Asset", sorted(history["ticker"].unique()))
asset = history.loc[history["ticker"] == ticker].sort_values("date")
timeline = px.line(asset, x="date", y="close", markers=True,
                   labels={"date": "日期" if zh else "Date", "close": "收盘价" if zh else "Close"})
timeline.update_layout(height=330, margin=dict(l=10, r=10, t=20, b=10), showlegend=False)
st.plotly_chart(timeline, width="stretch")

st.subheader("最新观察" if zh else "Latest Observations")
shown = latest[["ticker", "close", "return_1d", "return_5d", "return_21d",
                "volatility_21d_annualized", "rsi14", "trend_state"]].copy()
shown = shown.sort_values("return_21d", ascending=False)
for column in ["return_1d", "return_5d", "return_21d", "volatility_21d_annualized"]:
    shown[column] = shown[column] * 100
if zh:
    shown["trend_state"] = shown["trend_state"].replace({"Above MA20/60": "位于MA20/60上方", "Below MA20/60": "位于MA20/60下方", "At MA20/60": "接近MA20/60"})
st.dataframe(shown, width="stretch", hide_index=True,
             column_config={
                 "return_1d": st.column_config.NumberColumn("1D", format="%.2f%%"),
                 "return_5d": st.column_config.NumberColumn("5D", format="%.2f%%"),
                 "return_21d": st.column_config.NumberColumn("21D", format="%.2f%%"),
                 "volatility_21d_annualized": st.column_config.NumberColumn("21D Vol", format="%.2f%%"),
             })

st.subheader("前瞻检查" if zh else "Prospective Check")
scorecard = build_forward_scorecard(history)
unique_days = history["date"].nunique()
if scorecard.empty:
    st.info("至少需要两个不同交易日才能开始检查信号。" if zh else "At least two distinct market days are required to begin checking signals.")
else:
    scorecard = scorecard.copy()
    scorecard["average_next_return"] = scorecard["average_next_return"] * 100
    scorecard["win_rate"] = scorecard["win_rate"] * 100
    st.dataframe(scorecard, width="stretch", hide_index=True,
                 column_config={
                     "average_next_return": st.column_config.NumberColumn("下一记录平均收益" if zh else "Avg. Next-Record Return", format="%.2f%%"),
                     "win_rate": st.column_config.NumberColumn("正收益比例" if zh else "Positive Return Rate", format="%.1f%%"),
                 })
    if unique_days < 20:
        st.warning((f"目前只有 {unique_days} 个交易日，统计结果非常早期，不能用来修改参数或指导实盘；至少积累20–30个交易日后再做第一次评价。" if zh else
                    f"Only {unique_days} market days are available. These statistics are preliminary and must not guide parameter changes or live trading; wait for at least 20–30 days."))

st.caption("RSI和均线描述当前状态，不单独构成买卖建议。" if zh else
           "RSI and moving averages describe current conditions; neither is a standalone trading recommendation.")

factor_path = Path("published_research/daily/global_factors") / f"{latest_date:%Y-%m-%d}.csv"
news_path = Path("published_research/daily/news_context") / f"{latest_date:%Y-%m-%d}.csv"
if factor_path.exists():
    factors = pd.read_csv(factor_path)
    st.subheader("全球市场因子" if zh else "Global Market Factors")
    global_shown = factors[["factor", "ticker", "return_1d", "return_5d", "return_21d", "volatility_21d"]].copy()
    for column in ["return_1d", "return_5d", "return_21d", "volatility_21d"]:
        global_shown[column] *= 100
    st.dataframe(global_shown, width="stretch", hide_index=True,
                 column_config={c: st.column_config.NumberColumn(format="%.2f%%") for c in ["return_1d", "return_5d", "return_21d", "volatility_21d"]})
if news_path.exists():
    news = pd.read_csv(news_path)
    st.subheader("国际局势观察" if zh else "International Situation Watch")
    st.caption("标题用于构建风险情景，不等同于已核实事实，也不会单独触发交易。" if zh else
               "Headlines support risk scenarios; they are not verified facts and never trigger trades alone.")
    for row in news.groupby("category", sort=False).head(2).itertuples(index=False):
        st.markdown(f"- **{row.category}:** [{row.title}]({row.url}) — {row.source}")
