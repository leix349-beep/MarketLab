"""Shared visual system for the MarketLab Streamlit interface."""
from html import escape

import plotly.io as pio
import streamlit as st


def apply_theme() -> None:
    marketlab = pio.templates["plotly_white"]
    marketlab.layout.update(
        colorway=["#477B9E", "#79A895", "#E7A977", "#7C6FA7", "#5F9EA0", "#D96767"],
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#20242A"),
        title=dict(font=dict(color="#111318")),
        xaxis=dict(gridcolor="#E7ECEF", linecolor="#DDE4E8", zerolinecolor="#DDE4E8"),
        yaxis=dict(gridcolor="#E7ECEF", linecolor="#DDE4E8", zerolinecolor="#DDE4E8"),
        hoverlabel=dict(bgcolor="#FFFFFF", bordercolor="#DDE4E8", font=dict(color="#20242A")),
    )
    pio.templates["marketlab"] = marketlab
    pio.templates.default = "marketlab"

    st.markdown(
        """
        <style>
        :root {
          --ml-heading: #111318;
          --ml-ink: #20242a;
          --ml-muted: #6b7280;
          --ml-accent: #477b9e;
          --ml-accent-soft: #eaf1f5;
          --ml-sage: #79a895;
          --ml-apricot: #e7a977;
          --ml-danger: #d96767;
          --ml-line: #dde4e8;
          --ml-paper: rgba(255, 255, 255, .94);
          --ml-ease: cubic-bezier(.22, 1, .36, 1);
        }

        html { scroll-behavior: smooth; }
        body, [data-testid="stAppViewContainer"] {
          font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans SC", sans-serif;
          color: var(--ml-ink);
        }
        [data-testid="stAppViewContainer"] {
          background: #fafaf7;
        }
        [data-testid="stHeader"] { background: rgba(250, 250, 247, .84); backdrop-filter: blur(14px); }
        [data-testid="stSidebar"] {
          background: #f1f5f7;
          border-right: 1px solid var(--ml-line);
        }
        [data-testid="stSidebarContent"] { padding-top: 1.2rem; }

        h1 { letter-spacing: -.045em; font-weight: 680; color: var(--ml-heading); }
        h2, h3 { letter-spacing: -.025em; color: var(--ml-heading); }
        [data-testid="stCaptionContainer"], .stCaption { color: var(--ml-muted); }

        [data-testid="stSidebarNav"] a,
        a[data-testid="stPageLink-NavLink"] {
          min-height: 2.65rem;
          margin: .18rem .55rem;
          padding: .62rem .72rem;
          border: 1px solid transparent;
          border-radius: 12px;
          transition: transform 240ms var(--ml-ease), background-color 240ms var(--ml-ease),
                      border-color 240ms var(--ml-ease), box-shadow 240ms var(--ml-ease);
        }
        [data-testid="stSidebarNav"] a:hover,
        a[data-testid="stPageLink-NavLink"]:hover {
          transform: translateX(3px);
          background: rgba(255, 255, 255, .82);
          border-color: var(--ml-line);
          box-shadow: 0 7px 24px rgba(36, 50, 58, .07);
        }
        [data-testid="stSidebarNav"] a[aria-current="page"],
        a[data-testid="stPageLink-NavLink"][aria-current="page"] {
          background: #eaf1f5;
          border-color: rgba(71, 123, 158, .22);
          box-shadow: inset 3px 0 0 var(--ml-accent);
        }

        [data-testid="stMetric"], [data-testid="stPlotlyChart"] {
          background: var(--ml-paper);
          border: 1px solid var(--ml-line);
          border-radius: 16px;
          box-shadow: 0 10px 36px rgba(36, 50, 58, .045);
          transition: transform 260ms var(--ml-ease), box-shadow 260ms var(--ml-ease),
                      border-color 260ms var(--ml-ease);
        }
        [data-testid="stMetric"] { padding: 15px 17px; }
        [data-testid="stMetric"]:hover, [data-testid="stPlotlyChart"]:hover {
          transform: translateY(-2px);
          border-color: rgba(71, 123, 158, .24);
          box-shadow: 0 16px 42px rgba(36, 50, 58, .075);
        }

        .stButton > button, [data-testid="stFormSubmitButton"] button,
        [data-baseweb="select"] > div, [data-testid="stExpander"] details {
          border-radius: 12px;
          transition: transform 220ms var(--ml-ease), box-shadow 220ms var(--ml-ease),
                      border-color 220ms var(--ml-ease), background-color 220ms var(--ml-ease);
        }
        .stButton > button:hover, [data-testid="stFormSubmitButton"] button:hover {
          transform: translateY(-1px);
          box-shadow: 0 10px 24px rgba(71, 123, 158, .18);
        }
        .stButton > button:active, [data-testid="stFormSubmitButton"] button:active {
          transform: translateY(0) scale(.99);
          transition-duration: 80ms;
        }
        [data-baseweb="select"] > div:hover, [data-testid="stExpander"] details:hover {
          border-color: rgba(71, 123, 158, .36);
        }
        [data-testid="stTabs"] button { font-weight: 600; letter-spacing: -.01em; }
        [data-testid="stDataFrame"] { border: 1px solid var(--ml-line); border-radius: 14px; overflow: hidden; }

        .ml-empty-state {
          margin-top: 1.35rem;
          padding: 1.35rem 1.45rem 1.2rem;
          background: rgba(255, 255, 255, .78);
          border: 1px solid var(--ml-line);
          border-radius: 18px;
          box-shadow: 0 12px 34px rgba(36, 50, 58, .045);
        }
        .ml-empty-kicker {
          color: var(--ml-accent);
          font-size: .76rem;
          font-weight: 700;
          letter-spacing: .08em;
          text-transform: uppercase;
        }
        .ml-empty-state h3 { margin: .35rem 0 .3rem; font-size: 1.18rem; }
        .ml-empty-state p { margin: 0; color: var(--ml-muted); max-width: 48rem; }
        .ml-empty-steps {
          display: grid;
          grid-template-columns: repeat(3, minmax(0, 1fr));
          gap: .7rem;
          margin-top: 1rem;
        }
        .ml-empty-step {
          padding: .78rem .85rem;
          color: var(--ml-ink);
          background: #f7f9fa;
          border: 1px solid #e7ecef;
          border-radius: 12px;
          font-size: .88rem;
        }
        .ml-empty-step span {
          display: block;
          margin-bottom: .2rem;
          color: var(--ml-accent);
          font-size: .72rem;
          font-weight: 700;
        }
        @media (max-width: 720px) {
          .ml-empty-steps { grid-template-columns: 1fr; }
          .ml-empty-state { padding: 1.05rem; }
        }

        ::selection { background: rgba(71, 123, 158, .20); }
        ::-webkit-scrollbar { width: 10px; height: 10px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: rgba(107, 114, 128, .28); border: 3px solid transparent; background-clip: padding-box; border-radius: 999px; }
        ::-webkit-scrollbar-thumb:hover { background: rgba(71, 123, 158, .45); border: 2px solid transparent; background-clip: padding-box; }

        @media (prefers-reduced-motion: reduce) {
          html { scroll-behavior: auto; }
          *, *::before, *::after { transition-duration: .01ms !important; animation-duration: .01ms !important; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_empty_state(kicker: str, title: str, description: str, steps: list[str]) -> None:
    """Render a compact, bilingual-ready first-run guide without fetching data."""
    cards = "".join(
        f'<div class="ml-empty-step"><span>{index:02d}</span>{escape(step)}</div>'
        for index, step in enumerate(steps, start=1)
    )
    st.markdown(
        f"""
        <section class="ml-empty-state">
          <div class="ml-empty-kicker">{escape(kicker)}</div>
          <h3>{escape(title)}</h3>
          <p>{escape(description)}</p>
          <div class="ml-empty-steps">{cards}</div>
        </section>
        """,
        unsafe_allow_html=True,
    )
