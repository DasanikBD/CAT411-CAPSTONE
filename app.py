"""
app.py — CAT411 Loss Assessment Dashboard
Author: Anik Das

Run with:  streamlit run app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# ── Page config ────────────────────────────────────────────────
st.set_page_config(
    page_title="Bridge Loss Assessment — Northridge 1994",
    page_icon="🌉",
    layout="wide"
)

# ── Load data ──────────────────────────────────────────────────
@st.cache_data
def load_data():
    base = Path(__file__).parent
    sm   = pd.read_csv(base / "shakemap_results.csv")
    gmpe = pd.read_csv(base / "gmpe_results.csv")
    return sm, gmpe

sm_df, gmpe_df = load_data()

# ── Colour map ──────────────────────────────────────────────────
DS_COLORS = {
    "none"     : "#94A3B8",
    "slight"   : "#FCD34D",
    "moderate" : "#F97316",
    "extensive": "#EF4444",
    "complete" : "#7F1D1D",
}
DS_ORDER = ["none", "slight", "moderate", "extensive", "complete"]

# ── Sidebar ─────────────────────────────────────────────────────
st.sidebar.title("🌉 Loss Assessment Tool")
st.sidebar.markdown("**Northridge 1994 · 2,008 Bridges**")
st.sidebar.markdown("---")

mode = st.sidebar.radio(
    "Select Hazard Input",
    ["ShakeMap", "GMPE"],
    help="ShakeMap = recorded shaking. GMPE = model-predicted shaking."
)

if mode == "GMPE":
    gmpe_model = st.sidebar.selectbox(
        "GMPE Model",
        ["ASK14", "BSSA14", "CB14", "CY14"]
    )

st.sidebar.markdown("---")
st.sidebar.markdown("**Fragility Parameters**")
st.sidebar.markdown(f"k = 2.07 · β = 0.20 *(calibrated)*")
st.sidebar.markdown("---")
st.sidebar.markdown("**HAZUS Damage Ratios**")
st.sidebar.markdown("Slight: 3% · Moderate: 8%")
st.sidebar.markdown("Extensive: 25% · Complete: 100%")

# ── Select active dataset ───────────────────────────────────────
if mode == "ShakeMap":
    active = sm_df.copy()
    active['sa1s_display'] = active['sa1s_shakemap']
    hazard_label = "ShakeMap Sa(1.0s)"
    title_label  = "ShakeMap"
else:
    active = gmpe_df[gmpe_df['gmpe_model'] == gmpe_model].copy()
    active['sa1s_display'] = active['sa1s_used']
    hazard_label = f"{gmpe_model} Sa(1.0s)"
    title_label  = f"GMPE — {gmpe_model}"

active['ds_color'] = active['predicted_ds'].map(DS_COLORS)

# ── Title ────────────────────────────────────────────────────────
st.title(f"Bridge Loss Assessment — {title_label}")
st.markdown(f"Northridge 1994 Earthquake · {len(active):,} bridges · Calibrated HAZUS fragility (k=2.07, β=0.20)")

# ══════════════════════════════════════════════════════════════
# ROW 1 — KPI cards
# ══════════════════════════════════════════════════════════════
st.markdown("---")
k1, k2, k3, k4, k5 = st.columns(5)

total_cost  = active['repair_cost_usd'].sum()
damaged     = active[active['predicted_ds'] != 'none']
n_damaged   = len(damaged)
avg_cost    = damaged['repair_cost_usd'].mean() if len(damaged) > 0 else 0
max_cost_row = active.loc[active['repair_cost_usd'].idxmax()]

k1.metric("Total Repair Cost",     f"${total_cost/1e6:.1f}M")
k2.metric("Bridges with Damage",   f"{n_damaged:,}")
k3.metric("% Damaged",             f"{n_damaged/len(active)*100:.1f}%")
k4.metric("Avg Cost (damaged)",    f"${avg_cost/1e3:.0f}K")
k5.metric("Costliest Bridge",      f"${max_cost_row['repair_cost_usd']/1e6:.1f}M",
           delta=max_cost_row['structure_number'], delta_color="off")

# ══════════════════════════════════════════════════════════════
# ROW 2 — Map + Damage distribution
# ══════════════════════════════════════════════════════════════
st.markdown("---")
col_map, col_dist = st.columns([3, 2])

with col_map:
    st.subheader("Bridge Locations — Predicted Damage State")

    fig_map = px.scatter_mapbox(
        active,
        lat="latitude", lon="longitude",
        color="predicted_ds",
        color_discrete_map=DS_COLORS,
        category_orders={"predicted_ds": DS_ORDER},
        hover_name="structure_number",
        hover_data={
            "predicted_ds"       : True,
            "year_built"         : True,
            "hwb_class"          : True,
            "sa1s_display"       : ":.3f",
            "repair_cost_usd"    : ":,.0f",
            "replacement_cost_usd": ":,.0f",
            "latitude"           : False,
            "longitude"          : False,
        },
        labels={
            "predicted_ds"       : "Damage State",
            "sa1s_display"       : hazard_label,
            "repair_cost_usd"    : "Repair Cost ($)",
            "replacement_cost_usd": "Replacement Cost ($)",
        },
        zoom=9,
        center={"lat": 34.2, "lon": -118.5},
        mapbox_style="carto-positron",
        height=500,
    )
    fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0},
                          legend_title_text="Damage State")
    st.plotly_chart(fig_map, use_container_width=True)

with col_dist:
    st.subheader("Damage State Distribution")

    # Observed vs Predicted
    obs_counts  = active['obs'].str.lower().value_counts().reindex(DS_ORDER, fill_value=0)
    pred_counts = active['predicted_ds'].value_counts().reindex(DS_ORDER, fill_value=0)
    n = len(active)

    fig_dist = go.Figure()
    fig_dist.add_trace(go.Bar(
        name="Observed",
        x=[d.capitalize() for d in DS_ORDER],
        y=[obs_counts[ds]/n*100 for ds in DS_ORDER],
        marker_color="#22C55E", opacity=0.85
    ))
    fig_dist.add_trace(go.Bar(
        name="Predicted",
        x=[d.capitalize() for d in DS_ORDER],
        y=[pred_counts[ds]/n*100 for ds in DS_ORDER],
        marker_color="#3B82F6", opacity=0.85
    ))
    fig_dist.update_layout(
        barmode="group", height=240,
        yaxis_title="% of Bridges",
        legend=dict(orientation="h", y=1.1),
        margin=dict(t=10,b=40,l=40,r=10)
    )
    st.plotly_chart(fig_dist, use_container_width=True)

    # Repair cost by damage state
    st.subheader("Repair Cost by Damage State")
    cost_by_ds = active.groupby('predicted_ds')['repair_cost_usd'].sum().reindex(DS_ORDER, fill_value=0)
    fig_cost = go.Figure(go.Bar(
        x=[d.capitalize() for d in DS_ORDER],
        y=[cost_by_ds[ds]/1e6 for ds in DS_ORDER],
        marker_color=[DS_COLORS[ds] for ds in DS_ORDER],
        text=[f"${cost_by_ds[ds]/1e6:.1f}M" for ds in DS_ORDER],
        textposition="outside"
    ))
    fig_cost.update_layout(
        height=220, yaxis_title="Repair Cost ($M)",
        margin=dict(t=10,b=40,l=40,r=10),
        showlegend=False
    )
    st.plotly_chart(fig_cost, use_container_width=True)

# ══════════════════════════════════════════════════════════════
# ROW 3 — Top 10 + full table
# ══════════════════════════════════════════════════════════════
st.markdown("---")
col_top, col_scatter = st.columns([2, 3])

with col_top:
    st.subheader("Top 10 Costliest Bridges")
    top10 = (active[active['repair_cost_usd'] > 0]
             .nlargest(10, 'repair_cost_usd')
             [['structure_number','hwb_class','year_built',
               'predicted_ds','repair_cost_usd']]
             .copy())
    top10['repair_cost_usd'] = top10['repair_cost_usd'].apply(lambda x: f"${x:,.0f}")
    top10.columns = ['Bridge ID','HWB','Year','Damage State','Repair Cost']
    st.dataframe(top10, hide_index=True, use_container_width=True)

with col_scatter:
    st.subheader(f"Sa(1.0s) vs Repair Cost")
    fig_sc = px.scatter(
        active,
        x="sa1s_display", y="repair_cost_usd",
        color="predicted_ds",
        color_discrete_map=DS_COLORS,
        category_orders={"predicted_ds": DS_ORDER},
        hover_name="structure_number",
        labels={
            "sa1s_display"   : hazard_label,
            "repair_cost_usd": "Repair Cost ($)",
            "predicted_ds"   : "Damage State",
        },
        height=320,
        opacity=0.7
    )
    fig_sc.update_layout(margin=dict(t=10,b=40,l=60,r=10),
                          legend_title_text="Damage State")
    st.plotly_chart(fig_sc, use_container_width=True)

# ══════════════════════════════════════════════════════════════
# ROW 4 — Full data table with filters
# ══════════════════════════════════════════════════════════════
st.markdown("---")
st.subheader("Full Bridge Data Table")

f1, f2, f3 = st.columns(3)
ds_filter  = f1.multiselect("Filter by Damage State",
                             options=[d.capitalize() for d in DS_ORDER],
                             default=[d.capitalize() for d in DS_ORDER])
hwb_filter = f2.multiselect("Filter by HWB Class",
                              options=sorted(active['hwb_class'].unique()),
                              default=sorted(active['hwb_class'].unique()))
min_cost   = f3.number_input("Min Repair Cost ($)", min_value=0, value=0, step=10000)

filtered = active[
    (active['predicted_ds'].str.capitalize().isin(ds_filter)) &
    (active['hwb_class'].isin(hwb_filter)) &
    (active['repair_cost_usd'] >= min_cost)
].copy()

show_cols = ['structure_number','latitude','longitude','year_built',
             'hwb_class','material','design_era','sa1s_display',
             'predicted_ds','replacement_cost_usd','repair_cost_usd','obs']
col_labels = {'structure_number':'Bridge ID','sa1s_display':hazard_label,
              'predicted_ds':'Pred. DS','replacement_cost_usd':'RCV ($)',
              'repair_cost_usd':'Repair Cost ($)','obs':'Observed DS'}

st.markdown(f"Showing **{len(filtered):,}** bridges")
st.dataframe(
    filtered[show_cols].rename(columns=col_labels),
    hide_index=True, use_container_width=True, height=350
)

# Download button
csv = filtered[show_cols].rename(columns=col_labels).to_csv(index=False)
st.download_button(
    label="Download filtered results (CSV)",
    data=csv,
    file_name=f"loss_results_{title_label.replace(' ','_').replace('—','')}.csv",
    mime="text/csv"
)

st.markdown("---")
st.caption("CAT411 Catastrophe Modeling Capstone · Lehigh University · "
           "Calibrated HAZUS fragility (k=2.07, β=0.20) · "
           "GMPE data: Kubilay Albayrak · RCV: Wenyu Chiou · "
           "Calibration: Sirisha Kedarsetty · Dashboard: Anik Das")
