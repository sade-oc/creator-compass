import streamlit as st
import pandas as pd
from utils.helpers import load_examples

st.title("Trend Discovery")

# Load data
df = load_examples()

if df.empty:
    st.info("No trends found. Try running the ingestor to populate `data/examples/trends.csv`.")
else:
    # Sidebar filters
    st.sidebar.header("Filters")
    niches = sorted([n for n in df["niche"].dropna().unique()])
    selected_niches = st.sidebar.multiselect("Niche", niches, default=niches)

    search = st.sidebar.text_input("Search topics", "").strip()

    # Date range filter (optional if timestamps exist)
    if "discovered_at" in df.columns and df["discovered_at"].notna().any():
        min_dt = pd.to_datetime(df["discovered_at"].min()).date()
        max_dt = pd.to_datetime(df["discovered_at"].max()).date()
        date_range = st.sidebar.date_input(
            "Date range",
            value=(min_dt, max_dt),
            min_value=min_dt,
            max_value=max_dt
        )
        if isinstance(date_range, tuple) and len(date_range) == 2:
            start_date, end_date = date_range
        else:
            start_date, end_date = None, None
    else:
        start_date, end_date = None, None

    # Build mask
    mask = pd.Series(True, index=df.index)
    if selected_niches:
        mask &= df["niche"].isin(selected_niches)
    if search:
        mask &= df["topic"].astype(str).str.contains(search, case=False, na=False)
    if start_date and end_date and "discovered_at" in df.columns:
        dts = pd.to_datetime(df["discovered_at"], errors="coerce")
        mask &= (dts.dt.date >= start_date) & (dts.dt.date <= end_date)

    filtered = df[mask].copy()
    if not filtered.empty:
        filtered = filtered.sort_values(by=["score", "discovered_at"], ascending=[False, False])

        # Summary
        left, mid, right = st.columns(3)
        left.metric("Topics", len(filtered))
        mid.metric("Niches", filtered["niche"].nunique())
        top_src = filtered["source"].mode().iat[0] if not filtered["source"].dropna().empty else "-"
        right.metric("Top Source", top_src)

        # Table
        show_cols = [c for c in ["topic", "score", "niche", "source", "discovered_at", "region"] if c in filtered.columns]
        st.dataframe(filtered[show_cols], use_container_width=True, hide_index=True)
    else:
        st.warning("No results match the current filters. Clear filters to see all.")
