import streamlit as st

st.set_page_config(page_title="Xiang's MarketLab", page_icon="📈", layout="wide")

page = st.navigation([
    st.Page("stock_research.py", title="Stock Research", icon="📈", default=True),
    st.Page("pages/1_Sector_Research.py", title="Sector Research", icon="🧭"),
    st.Page("pages/2_Comparison_Lab.py", title="Comparison Lab", icon="📊"),
    st.Page("pages/3_Strategy_Lab.py", title="Strategy Lab", icon="🧪"),
    st.Page("pages/4_Regression_Lab.py", title="Regression Lab", icon="📐"),
])
page.run()
