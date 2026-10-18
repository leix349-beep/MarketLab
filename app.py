import streamlit as st
from ui_theme import apply_theme

st.set_page_config(page_title="Xiang's MarketLab", page_icon=":material/monitoring:", layout="wide")
apply_theme()

page = st.navigation([
    st.Page("stock_research.py", title="Stock Research", icon=":material/monitoring:", default=True),
    st.Page("pages/1_Sector_Research.py", title="Sector Research", icon=":material/donut_large:"),
    st.Page("pages/2_Comparison_Lab.py", title="Comparison Lab", icon=":material/compare_arrows:"),
    st.Page("pages/3_Strategy_Lab.py", title="Strategy Lab", icon=":material/science:"),
    st.Page("pages/4_Regression_Lab.py", title="Regression Lab", icon=":material/functions:"),
    st.Page("pages/5_Validation_Lab.py", title="Validation Lab", icon=":material/verified:"),
    st.Page("pages/6_Daily_Monitor.py", title="Daily Monitor", icon=":material/calendar_month:"),
])
page.run()
