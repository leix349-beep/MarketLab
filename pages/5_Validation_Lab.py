from datetime import date, timedelta

import pandas as pd
import plotly.express as px
import streamlit as st
import yfinance as yf

from universe import ASSETS, asset_label
from validation import walk_forward_validate

st.markdown("""<style>
[data-testid="stAppViewContainer"] {background:linear-gradient(145deg,#fff 0%,#f7fbff 55%,#f4f1ff 100%);}
[data-testid="stSidebar"] {background:linear-gradient(180deg,#f2f6fc 0%,#eef1f8 100%);}
h1 {letter-spacing:-.035em;} [data-testid="stMetric"] {background:rgba(255,255,255,.72);border:1px solid rgba(80,100,140,.12);padding:14px;border-radius:14px;}
</style>""", unsafe_allow_html=True)

language = st.sidebar.radio("Language / 语言", ["English", "中文"], horizontal=True, key="global_language")
zh = language == "中文"
st.title("Xiang’s MarketLab · 样本外验证" if zh else "Xiang’s MarketLab · Validation Lab")
st.caption("让参数只看过去，再用未见数据检验。" if zh else "Tune on the past, then test on data the model has never seen.")

symbol = st.sidebar.selectbox("研究标的" if zh else "Research Asset", list(ASSETS), format_func=asset_label)
years = st.sidebar.slider("历史年数" if zh else "History (years)", 3, 10, 7)
train_months = st.sidebar.select_slider("训练窗口" if zh else "Training Window", [12, 24, 36, 48], value=24,
                                        format_func=lambda x: f"{x} 个月" if zh else f"{x} months")
test_months = st.sidebar.select_slider("样本外窗口" if zh else "Unseen Test Window", [3, 6, 12], value=6,
                                       format_func=lambda x: f"{x} 个月" if zh else f"{x} months")
fee = st.sidebar.number_input("手续费/滑点 %" if zh else "Fees / Slippage %", 0.0, 1.0, .10, .05) / 100
run = st.sidebar.button("运行样本外验证" if zh else "Run Validation", type="primary", use_container_width=True)

@st.cache_data(ttl=3600)
def prices(ticker, start):
    data = yf.download(ticker, start=start, auto_adjust=True, progress=False)
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
    return data

if run:
    with st.spinner("正在按时间顺序重复训练与测试…" if zh else "Rolling through training and unseen test windows…"):
        try:
            start = date.today() - timedelta(days=years * 365 + 60)
            data = prices(symbol, start)
            result = walk_forward_validate(data, train_days=train_months * 21, test_days=test_months * 21, fee=fee)
            st.session_state.validation_result = result
            st.session_state.validation_symbol = symbol
        except Exception as exc:
            st.error(("无法完成验证：" if zh else "Validation could not be completed: ") + str(exc))

if "validation_result" not in st.session_state:
    st.info("选择窗口后运行验证。系统会重复执行：过去训练 → 锁定参数 → 未来测试。" if zh else
            "Choose the windows and run validation. Each round follows: train on past → lock parameters → test on future.")
else:
    result = st.session_state.validation_result
    summary, folds, curve = result["summary"], result["folds"].copy(), result["curve"]
    st.markdown("**过去数据训练　→　锁定参数　→　未见数据测试　→　时间向前滚动**" if zh else
                "**Past data training　→　Lock parameters　→　Unseen test　→　Roll forward**")

    a, b, c, d = st.columns(4)
    a.metric("样本外累计收益" if zh else "Out-of-Sample Return", f"{summary['return']:.1%}")
    b.metric("样本外最大回撤" if zh else "Out-of-Sample Drawdown", f"{summary['drawdown']:.1%}")
    c.metric("正收益窗口" if zh else "Positive Test Windows", f"{summary['positive_folds']} / {summary['folds']}")
    d.metric("跑赢持有窗口" if zh else "Windows Beating Hold", f"{summary['winning_folds']} / {summary['folds']}")

    chart = px.line(curve, labels={"value": "起始资金 = 100" if zh else "Starting Value = 100", "index": "日期" if zh else "Date", "variable": "方法" if zh else "Method"})
    chart.update_layout(height=430, margin=dict(l=10, r=10, t=25, b=10))
    st.plotly_chart(chart, use_container_width=True)

    bars = folds[["Fold", "Test Return", "Buy & Hold Return"]].melt("Fold", var_name="Method", value_name="Return")
    fold_chart = px.bar(bars, x="Fold", y="Return", color="Method", barmode="group",
                        title="每个未见窗口的真实考试结果" if zh else "Result in Each Unseen Test Window")
    fold_chart.update_yaxes(tickformat=".0%")
    fold_chart.update_layout(height=350, margin=dict(l=10, r=10, t=50, b=10))
    st.plotly_chart(fold_chart, use_container_width=True)

    with st.expander("查看每轮参数与结果" if zh else "Inspect Every Fold", expanded=False):
        shown = folds.copy()
        for col in ["Train Start", "Train End", "Test Start", "Test End"]:
            shown[col] = pd.to_datetime(shown[col]).dt.strftime("%Y-%m-%d")
        st.dataframe(shown, use_container_width=True, hide_index=True,
                     column_config={name: st.column_config.NumberColumn(format="%.1f%%") for name in ["Test Return", "Buy & Hold Return", "Test Drawdown"]})

    st.markdown("### " + ("如何判断" if zh else "How to Judge the Result"))
    if zh:
        st.markdown(f"- 样本外策略累计收益 **{summary['return']:.1%}**，同期持有收益 **{summary['benchmark_return']:.1%}**。\n"
                    f"- 最常用参数组合只占 **{summary['parameter_stability']:.0%}** 的窗口；越低说明参数越不稳定。\n"
                    "- 单次通过不等于可实盘。下一步仍需跨标的验证、压力测试和模拟交易。")
    else:
        st.markdown(f"- The strategy returned **{summary['return']:.1%}** out of sample versus **{summary['benchmark_return']:.1%}** for buy and hold.\n"
                    f"- The most common parameter pair appeared in **{summary['parameter_stability']:.0%}** of windows; a lower value suggests instability.\n"
                    "- One pass is not sufficient for live use. Cross-asset tests, stress tests, and paper trading still come next.")
    st.warning("历史样本外测试仍不能预测未来，也不构成投资建议。" if zh else
               "Historical out-of-sample testing still cannot predict the future and is not investment advice.")
