"""Shared visual system for the MarketLab Streamlit interface."""
import streamlit as st


def apply_theme() -> None:
    st.markdown(
        """
        <style>
        :root {
          --ml-ink: #172326;
          --ml-muted: #667275;
          --ml-accent: #176b70;
          --ml-accent-soft: #dcebea;
          --ml-line: rgba(23, 45, 48, .12);
          --ml-paper: rgba(255, 255, 252, .82);
          --ml-ease: cubic-bezier(.22, 1, .36, 1);
        }

        html { scroll-behavior: smooth; }
        body, [data-testid="stAppViewContainer"] {
          font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans SC", sans-serif;
          color: var(--ml-ink);
        }
        [data-testid="stAppViewContainer"] {
          background:
            radial-gradient(circle at 78% 4%, rgba(80, 142, 139, .10), transparent 31rem),
            linear-gradient(145deg, #fbfaf6 0%, #f6f7f3 48%, #edf3f1 100%);
        }
        [data-testid="stHeader"] { background: rgba(251, 250, 246, .72); backdrop-filter: blur(14px); }
        [data-testid="stSidebar"] {
          background: linear-gradient(180deg, #f1f2ee 0%, #e9efed 100%);
          border-right: 1px solid var(--ml-line);
        }
        [data-testid="stSidebarContent"] { padding-top: 1.2rem; }

        h1 { letter-spacing: -.045em; font-weight: 680; color: var(--ml-ink); }
        h2, h3 { letter-spacing: -.025em; color: var(--ml-ink); }
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
          background: rgba(255, 255, 252, .72);
          border-color: var(--ml-line);
          box-shadow: 0 7px 24px rgba(27, 55, 57, .07);
        }
        [data-testid="stSidebarNav"] a[aria-current="page"],
        a[data-testid="stPageLink-NavLink"][aria-current="page"] {
          background: #dfe9e6;
          border-color: rgba(23, 107, 112, .18);
          box-shadow: inset 3px 0 0 var(--ml-accent);
        }

        [data-testid="stMetric"], [data-testid="stPlotlyChart"] {
          background: var(--ml-paper);
          border: 1px solid var(--ml-line);
          border-radius: 16px;
          box-shadow: 0 10px 36px rgba(30, 55, 56, .045);
          transition: transform 260ms var(--ml-ease), box-shadow 260ms var(--ml-ease),
                      border-color 260ms var(--ml-ease);
        }
        [data-testid="stMetric"] { padding: 15px 17px; }
        [data-testid="stMetric"]:hover, [data-testid="stPlotlyChart"]:hover {
          transform: translateY(-2px);
          border-color: rgba(23, 107, 112, .22);
          box-shadow: 0 16px 42px rgba(30, 55, 56, .075);
        }

        .stButton > button, [data-testid="stFormSubmitButton"] button,
        [data-baseweb="select"] > div, [data-testid="stExpander"] details {
          border-radius: 12px;
          transition: transform 220ms var(--ml-ease), box-shadow 220ms var(--ml-ease),
                      border-color 220ms var(--ml-ease), background-color 220ms var(--ml-ease);
        }
        .stButton > button:hover, [data-testid="stFormSubmitButton"] button:hover {
          transform: translateY(-1px);
          box-shadow: 0 10px 24px rgba(23, 107, 112, .16);
        }
        .stButton > button:active, [data-testid="stFormSubmitButton"] button:active {
          transform: translateY(0) scale(.99);
          transition-duration: 80ms;
        }
        [data-baseweb="select"] > div:hover, [data-testid="stExpander"] details:hover {
          border-color: rgba(23, 107, 112, .32);
        }
        [data-testid="stTabs"] button { font-weight: 600; letter-spacing: -.01em; }
        [data-testid="stDataFrame"] { border: 1px solid var(--ml-line); border-radius: 14px; overflow: hidden; }

        ::selection { background: rgba(23, 107, 112, .18); }
        ::-webkit-scrollbar { width: 10px; height: 10px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: rgba(61, 88, 89, .24); border: 3px solid transparent; background-clip: padding-box; border-radius: 999px; }
        ::-webkit-scrollbar-thumb:hover { background: rgba(23, 107, 112, .42); border: 2px solid transparent; background-clip: padding-box; }

        @media (prefers-reduced-motion: reduce) {
          html { scroll-behavior: auto; }
          *, *::before, *::after { transition-duration: .01ms !important; animation-duration: .01ms !important; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
