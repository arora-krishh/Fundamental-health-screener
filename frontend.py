import streamlit as st
from backend import SECTOR_TICKERS, PRESET_PROFILES, run_screener

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Stock Health Screener", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=Epilogue:wght@400;700;900&display=swap');

html, body, [class*="css"] {
    font-family: 'Epilogue', sans-serif;
    background-color: #0a0a0a;
    color: #e8e8e8;
}
h1, h2, h3 { font-family: 'Epilogue', sans-serif; font-weight: 900; }
section[data-testid="stSidebar"] { background-color: #111 !important; border-right: 1px solid #1f1f1f; }
div[data-testid="metric-container"] { background: #111; border: 1px solid #1f1f1f; border-radius: 8px; padding: 16px; }
div[data-testid="stDataFrame"] { border: 1px solid #1f1f1f; border-radius: 8px; overflow: hidden; }
label { font-family: 'IBM Plex Mono', monospace !important; font-size: 11px !important; color: #555 !important; }
details { background: #111; border: 1px solid #1f1f1f; border-radius: 8px; }
.stButton > button {
    background: #b8ff3c; color: #000;
    font-family: 'IBM Plex Mono', monospace; font-weight: 600;
    border: none; border-radius: 6px; padding: 10px 24px; width: 100%;
}
.stButton > button:hover { background: #ceff55; }
div[data-testid="stSelectbox"] > div { background: #111; border: 1px solid #1f1f1f; border-radius: 6px; }
.ticker-badge {
    display: inline-block; background: #111; border: 1px solid #1f1f1f;
    border-radius: 4px; padding: 2px 8px;
    font-family: 'IBM Plex Mono', monospace; font-size: 11px;
    color: #b8ff3c; margin: 2px;
}
.eyebrow {
    font-family: 'IBM Plex Mono', monospace; font-size: 11px;
    color: #b8ff3c; text-transform: uppercase; letter-spacing: 3px;
}
.muted { font-family: 'IBM Plex Mono', monospace; font-size: 10px; color: #555; text-transform: uppercase; letter-spacing: 2px; }
</style>
""", unsafe_allow_html=True)


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<p class="eyebrow">Equity Screener</p>', unsafe_allow_html=True)
    st.markdown("## Stock Ranking Tool")
    st.markdown("---")

    st.markdown('<p class="muted">Sector</p>', unsafe_allow_html=True)
    sector = st.selectbox("", list(SECTOR_TICKERS.keys()), label_visibility="collapsed")

    st.markdown("---")

    st.markdown('<p class="muted">Investor Profile</p>', unsafe_allow_html=True)
    profile = st.selectbox("", ["Custom"] + list(PRESET_PROFILES.keys()), label_visibility="collapsed")

    st.markdown("---")

    st.markdown('<p class="muted">Ratio Weights</p>', unsafe_allow_html=True)

    defaults = PRESET_PROFILES[profile] if profile != "Custom" else {"P/E": 25, "D/E": 25, "ROE": 25, "Current Ratio": 25}

    pe_w  = st.slider("P/E Ratio Weight",     0, 100, defaults["P/E"])
    de_w  = st.slider("D/E Ratio Weight",     0, 100, defaults["D/E"])
    roe_w = st.slider("ROE Weight",           0, 100, defaults["ROE"])
    cr_w  = st.slider("Current Ratio Weight", 0, 100, defaults["Current Ratio"])

    total_w = pe_w + de_w + roe_w + cr_w
    if total_w == 0:
        st.error("At least one weight must be > 0")
    else:
        st.markdown(f'<p class="muted">Total: {total_w} — auto-normalised</p>', unsafe_allow_html=True)

    st.markdown("---")
    run = st.button("Run Screener →", disabled=(total_w == 0))


# ── Main ───────────────────────────────────────────────────────────────────────
st.markdown('<p class="eyebrow">Equity Screener</p>', unsafe_allow_html=True)
st.markdown("# Stock Ranking Tool")
st.markdown(f'<p class="muted">Sector → {sector}</p>', unsafe_allow_html=True)

tickers_html = " ".join(
    f'<span class="ticker-badge">{t}</span>' for t in SECTOR_TICKERS[sector]
)
st.markdown(tickers_html, unsafe_allow_html=True)
st.markdown("---")

if run:
    with st.spinner("Fetching live data from Yahoo Finance..."):
        df = run_screener(sector, pe_w, de_w, roe_w, cr_w)   # ← only backend call

    if df.empty:
        st.error("No data returned. Try a different sector.")
    else:
        # ── Top 3 ──
        st.markdown('<p class="muted">Top Picks</p>', unsafe_allow_html=True)
        top3   = df.head(3)
        medals = ["🥇", "🥈", "🥉"]
        cols   = st.columns(3)

        for i, (ticker, row) in enumerate(top3.iterrows()):
            with cols[i]:
                st.metric(
                    label=f"{medals[i]} {ticker}",
                    value=row["Name"],
                    delta=f"Score {row['Total score']}",
                )

        st.markdown("---")

        # ── Full table ──
        st.markdown('<p class="muted">Full Rankings</p>', unsafe_allow_html=True)

        display_df = df[["Name", "P/E ratio", "D/E ratio", "ROE", "Current ratio", "Total score"]].copy()
        display_df["ROE"] = (display_df["ROE"] * 100).round(2).astype(str) + "%"

        st.dataframe(
            display_df,
            use_container_width=True,
            column_config={
                "Total score": st.column_config.ProgressColumn(
                    "Score (lower = better)",
                    min_value=float(df["Total score"].min()),
                    max_value=float(df["Total score"].max()),
                    format="%.2f",
                ),
                "P/E ratio":     st.column_config.NumberColumn(format="%.2f"),
                "D/E ratio":     st.column_config.NumberColumn(format="%.2f"),
                "Current ratio": st.column_config.NumberColumn(format="%.2f"),
            },
        )

        st.markdown("---")

        with st.expander("📖 How are ratios interpreted?"):
            st.markdown("""
| Ratio | Direction | What it tells you |
|---|---|---|
| **P/E Ratio** | Lower is better | How expensive the stock is relative to earnings |
| **D/E Ratio** | Lower is better | How leveraged the company is |
| **ROE** | Higher is better | How efficiently equity generates profit |
| **Current Ratio** | Higher is better | Short-term liquidity — ability to cover liabilities |
            """)

else:
    st.info("👈 Select a sector, set your weights, and click **Run Screener**.")
