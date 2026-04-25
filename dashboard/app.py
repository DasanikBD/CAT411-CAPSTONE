"""
app.py — CAT411 Loss Assessment Dashboard
Author: Anik Das | Lehigh University | Spring 2026
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
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ─────────────────────────────────────────────────
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 50%, #0F172A 100%);
        color: #E2E8F0;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #065A82 0%, #021B2E 100%);
        border-right: 1px solid #1C7293;
    }
    [data-testid="stSidebar"] * {
        color: #E2E8F0 !important;
    }

    /* KPI Cards */
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, #1E293B, #0F2744);
        border: 1px solid #1C7293;
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 4px 15px rgba(28, 114, 147, 0.2);
    }
    [data-testid="metric-container"] label {
        color: #94A3B8 !important;
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.05em !important;
        text-transform: uppercase !important;
    }
    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: #38BDF8 !important;
        font-size: 1.8rem !important;
        font-weight: 700 !important;
    }
    [data-testid="metric-container"] [data-testid="stMetricDelta"] {
        color: #94A3B8 !important;
    }

    /* Section headers */
    h1 { color: #F1F5F9 !important; font-weight: 800 !important; }
    h2 { color: #E2E8F0 !important; font-weight: 700 !important; }
    h3 { color: #CBD5E1 !important; font-weight: 600 !important; }

    /* Divider */
    hr { border-color: #1C7293 !important; opacity: 0.4; }

    /* Dataframe */
    [data-testid="stDataFrame"] {
        border: 1px solid #1C7293;
        border-radius: 8px;
    }

    /* Selectbox and radio */
    [data-testid="stSelectbox"] > div,
    [data-testid="stRadio"] > div {
        background: #1E293B;
        border-radius: 8px;
        border: 1px solid #1C7293;
    }

    /* Download button */
    [data-testid="stDownloadButton"] button {
        background: linear-gradient(135deg, #065A82, #1C7293) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 0.5rem 1.5rem !important;
        box-shadow: 0 4px 12px rgba(28, 114, 147, 0.3) !important;
    }
    [data-testid="stDownloadButton"] button:hover {
        background: linear-gradient(135deg, #1C7293, #065A82) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 16px rgba(28, 114, 147, 0.4) !important;
    }

    /* Multiselect */
    [data-testid="stMultiSelect"] > div {
        background: #1E293B;
        border: 1px solid #1C7293;
        border-radius: 8px;
    }

    /* Caption / footer text */
    .stCaption { color: #475569 !important; }

    /* Info boxes */
    .stAlert {
        background: #1E293B !important;
        border: 1px solid #1C7293 !important;
        border-radius: 8px !important;
    }

    /* Plotly chart backgrounds */
    .js-plotly-plot {
        border-radius: 12px;
        overflow: hidden;
    }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        background: #1E293B;
        border-radius: 8px;
        border: 1px solid #1C7293;
    }
    .stTabs [data-baseweb="tab"] {
        color: #94A3B8 !important;
    }
    .stTabs [aria-selected="true"] {
        color: #38BDF8 !important;
        background: #065A82 !important;
        border-radius: 6px !important;
    }

    /* Number input */
    input[type="number"] {
        background: #1E293B !important;
        color: #E2E8F0 !important;
        border: 1px solid #1C7293 !important;
        border-radius: 6px !important;
    }
</style>
""", unsafe_allow_html=True)

# ── Plotly dark template ────────────────────────────────────────
PLOT_TEMPLATE = dict(
    layout=dict(
        paper_bgcolor="rgba(15,23,42,0)",
        plot_bgcolor="rgba(30,41,59,0.6)",
        font=dict(color="#E2E8F0", family="Inter, sans-serif"),
        title_font=dict(color="#F1F5F9", size=16),
        legend=dict(bgcolor="rgba(15,23,42,0.8)", bordercolor="#1C7293", borderwidth=1),
        xaxis=dict(gridcolor="#1E3A5F", linecolor="#1C7293", tickcolor="#94A3B8"),
        yaxis=dict(gridcolor="#1E3A5F", linecolor="#1C7293", tickcolor="#94A3B8"),
    )
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
    "none"     : "#64748B",
    "slight"   : "#EAB308",
    "moderate" : "#F97316",
    "extensive": "#EF4444",
    "complete" : "#7F1D1D",
}
DS_ORDER = ["none", "slight", "moderate", "extensive", "complete"]

# ── Sidebar ─────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 1rem 0;'>
        <div style='font-size:2.5rem;'>🌉</div>
        <div style='font-size:1.1rem; font-weight:800; color:#F1F5F9; 
                    letter-spacing:0.05em;'>LOSS ASSESSMENT</div>
        <div style='font-size:0.75rem; color:#94A3B8; margin-top:4px;'>
            Northridge 1994 · 2,008 Bridges
        </div>
    </div>
    <hr style='border-color:#1C7293; opacity:0.4; margin:0.5rem 0;'/>
    """, unsafe_allow_html=True)

    mode = st.radio("**Select Hazard Input**", ["ShakeMap", "GMPE"])

    if mode == "GMPE":
        gmpe_model = st.selectbox("**GMPE Model**", ["ASK14", "BSSA14", "CB14", "CY14"])

    st.markdown("<hr style='border-color:#1C7293; opacity:0.4;'/>", unsafe_allow_html=True)

    st.markdown("**Fragility Parameters**")
    st.markdown("""
    <div style='background:rgba(6,90,130,0.3); border:1px solid #1C7293; 
                border-radius:8px; padding:10px; font-size:0.9rem;'>
        k = 2.07 &nbsp;·&nbsp; β = 0.20<br>
        <span style='color:#94A3B8; font-size:0.8rem;'>Calibrated · Sirisha Kedarsetty</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr style='border-color:#1C7293; opacity:0.4;'/>", unsafe_allow_html=True)

    st.markdown("**HAZUS Damage Ratios**")
    st.markdown("""
    <div style='background:rgba(6,90,130,0.2); border-radius:8px; 
                padding:10px; font-size:0.85rem; line-height:1.8;'>
        🟡 Slight &nbsp;&nbsp;&nbsp; 3%<br>
        🟠 Moderate &nbsp; 8%<br>
        🔴 Extensive &nbsp; 25%<br>
        🔴 Complete &nbsp; 100%
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr style='border-color:#1C7293; opacity:0.4;'/>", unsafe_allow_html=True)
    st.markdown("""
    <div style='font-size:0.75rem; color:#475569; text-align:center;'>
        CAT411 Capstone · Lehigh University<br>
        Spring 2026 · Anik Das
    </div>
    """, unsafe_allow_html=True)

# ── Select active dataset ───────────────────────────────────────
if mode == "ShakeMap":
    active = sm_df.copy()
    active['sa1s_display'] = active['sa1s_shakemap']
    hazard_label = "ShakeMap Sa(1.0s)"
    title_label  = "ShakeMap"
    title_color  = "#38BDF8"
else:
    active = gmpe_df[gmpe_df['gmpe_model'] == gmpe_model].copy()
    active['sa1s_display'] = active['sa1s_used']
    hazard_label = f"{gmpe_model} Sa(1.0s)"
    title_label  = f"GMPE — {gmpe_model}"
    title_color  = "#A78BFA"

active['ds_color'] = active['predicted_ds'].map(DS_COLORS)

# ── Header ───────────────────────────────────────────────────────
st.markdown(f"""
<div style='padding: 1.5rem 0 0.5rem 0;'>
    <h1 style='margin:0; font-size:2.2rem; background: linear-gradient(90deg, #38BDF8, #818CF8);
               -webkit-background-clip:text; -webkit-text-fill-color:transparent;'>
        Bridge Loss Assessment — {title_label}
    </h1>
    <p style='color:#64748B; margin:4px 0 0 0; font-size:0.9rem;'>
        Northridge 1994 Earthquake &nbsp;·&nbsp; {len(active):,} bridges &nbsp;·&nbsp; 
        Calibrated HAZUS fragility (k=2.07, β=0.20)
    </p>
</div>
<hr style='border-color:#1C7293; opacity:0.3; margin:0.8rem 0;'/>
""", unsafe_allow_html=True)

# ── KPI Cards ────────────────────────────────────────────────────
total_cost   = active['repair_cost_usd'].sum()
damaged      = active[active['predicted_ds'] != 'none']
n_damaged    = len(damaged)
avg_cost     = damaged['repair_cost_usd'].mean() if n_damaged > 0 else 0
max_row      = active.loc[active['repair_cost_usd'].idxmax()]
total_rcv    = active['replacement_cost_usd'].sum()

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total Repair Cost",      f"${total_cost/1e6:.1f}M")
k2.metric("Bridges with Damage",    f"{n_damaged:,}")
k3.metric("% Damaged",              f"{n_damaged/len(active)*100:.1f}%")
k4.metric("Avg Cost (damaged)",     f"${avg_cost/1e3:.0f}K")
k5.metric("Costliest Bridge",       f"${max_row['repair_cost_usd']/1e6:.1f}M",
           delta=str(max_row['structure_number']), delta_color="off")

st.markdown("<hr style='border-color:#1C7293; opacity:0.2; margin:0.8rem 0;'/>",
            unsafe_allow_html=True)

# ── Map + Distribution ──────────────────────────────────────────
col_map, col_dist = st.columns([3, 2])

with col_map:
    st.markdown("### 🗺 Bridge Locations — Predicted Damage State")
    fig_map = px.scatter_mapbox(
        active, lat="latitude", lon="longitude",
        color="predicted_ds",
        color_discrete_map=DS_COLORS,
        category_orders={"predicted_ds": DS_ORDER},
        hover_name="structure_number",
        hover_data={"predicted_ds":True,"year_built":True,"hwb_class":True,
                    "sa1s_display":":.3f","repair_cost_usd":":,.0f",
                    "replacement_cost_usd":":,.0f",
                    "latitude":False,"longitude":False},
        labels={"predicted_ds":"Damage State","sa1s_display":hazard_label,
                "repair_cost_usd":"Repair Cost ($)",
                "replacement_cost_usd":"Replacement Cost ($)"},
        zoom=9, center={"lat":34.2,"lon":-118.5},
        mapbox_style="carto-darkmatter",
        height=480,
    )
    fig_map.update_layout(
        margin={"r":0,"t":0,"l":0,"b":0},
        legend_title_text="Damage State",
        paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(bgcolor="rgba(15,23,42,0.8)",
                    bordercolor="#1C7293", borderwidth=1,
                    font=dict(color="#E2E8F0"))
    )
    st.plotly_chart(fig_map, use_container_width=True)

with col_dist:
    st.markdown("### 📊 Damage State Distribution")
    obs_counts  = active['obs'].str.lower().value_counts().reindex(DS_ORDER, fill_value=0)
    pred_counts = active['predicted_ds'].value_counts().reindex(DS_ORDER, fill_value=0)
    n = len(active)

    fig_dist = go.Figure()
    fig_dist.add_trace(go.Bar(
        name="Observed",
        x=[d.capitalize() for d in DS_ORDER],
        y=[obs_counts[ds]/n*100 for ds in DS_ORDER],
        marker_color="#22C55E", opacity=0.85,
        marker_line_color="#16A34A", marker_line_width=1
    ))
    fig_dist.add_trace(go.Bar(
        name="Predicted",
        x=[d.capitalize() for d in DS_ORDER],
        y=[pred_counts[ds]/n*100 for ds in DS_ORDER],
        marker_color="#38BDF8", opacity=0.85,
        marker_line_color="#0EA5E9", marker_line_width=1
    ))
    fig_dist.update_layout(
        **PLOT_TEMPLATE["layout"],
        barmode="group", height=210,
        yaxis_title="% of Bridges",
        legend=dict(orientation="h", y=1.12, bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#E2E8F0")),
        margin=dict(t=10,b=40,l=50,r=10)
    )
    st.plotly_chart(fig_dist, use_container_width=True)

    st.markdown("### 💰 Repair Cost by Damage State")
    cost_by_ds = active.groupby('predicted_ds')['repair_cost_usd'].sum().reindex(DS_ORDER, fill_value=0)
    fig_cost = go.Figure(go.Bar(
        x=[d.capitalize() for d in DS_ORDER],
        y=[cost_by_ds[ds]/1e6 for ds in DS_ORDER],
        marker_color=[DS_COLORS[ds] for ds in DS_ORDER],
        marker_line_color="#1E293B", marker_line_width=1,
        text=[f"${cost_by_ds[ds]/1e6:.1f}M" for ds in DS_ORDER],
        textposition="outside", textfont=dict(color="#E2E8F0", size=11)
    ))
    fig_cost.update_layout(
        **PLOT_TEMPLATE["layout"],
        height=200, yaxis_title="Repair Cost ($M)",
        margin=dict(t=10,b=40,l=50,r=10), showlegend=False
    )
    st.plotly_chart(fig_cost, use_container_width=True)

# ── Top 10 + Scatter ────────────────────────────────────────────
st.markdown("<hr style='border-color:#1C7293; opacity:0.2;'/>", unsafe_allow_html=True)
col_top, col_scatter = st.columns([2, 3])

with col_top:
    st.markdown("### 🏆 Top 10 Costliest Bridges")
    top10 = (active[active['repair_cost_usd'] > 0]
             .nlargest(10, 'repair_cost_usd')
             [['structure_number','hwb_class','year_built','predicted_ds','repair_cost_usd']]
             .copy())
    top10['repair_cost_usd'] = top10['repair_cost_usd'].apply(lambda x: f"${x:,.0f}")
    top10.columns = ['Bridge ID','HWB','Year','Damage State','Repair Cost']
    st.dataframe(top10, hide_index=True, use_container_width=True)

with col_scatter:
    st.markdown(f"### 📈 Sa(1.0s) vs Repair Cost")
    fig_sc = px.scatter(
        active, x="sa1s_display", y="repair_cost_usd",
        color="predicted_ds",
        color_discrete_map=DS_COLORS,
        category_orders={"predicted_ds": DS_ORDER},
        hover_name="structure_number",
        labels={"sa1s_display":hazard_label,"repair_cost_usd":"Repair Cost ($)",
                "predicted_ds":"Damage State"},
        height=300, opacity=0.75,
        template="plotly_dark"
    )
    fig_sc.update_layout(
        **PLOT_TEMPLATE["layout"],
        margin=dict(t=10,b=40,l=60,r=10),
        legend_title_text="Damage State"
    )
    st.plotly_chart(fig_sc, use_container_width=True)

# ── Full table ──────────────────────────────────────────────────
st.markdown("<hr style='border-color:#1C7293; opacity:0.2;'/>", unsafe_allow_html=True)
st.markdown("### 📋 Full Bridge Data Table")

f1, f2, f3 = st.columns(3)
ds_filter  = f1.multiselect("Filter by Damage State",
                             [d.capitalize() for d in DS_ORDER],
                             default=[d.capitalize() for d in DS_ORDER])
hwb_filter = f2.multiselect("Filter by HWB Class",
                              sorted(active['hwb_class'].unique()),
                              default=sorted(active['hwb_class'].unique()))
min_cost   = f3.number_input("Min Repair Cost ($)", min_value=0, value=0, step=10000)

filtered = active[
    (active['predicted_ds'].str.capitalize().isin(ds_filter)) &
    (active['hwb_class'].isin(hwb_filter)) &
    (active['repair_cost_usd'] >= min_cost)
].copy()

show_cols = ['structure_number','latitude','longitude','year_built',
             'hwb_class','material','sa1s_display',
             'predicted_ds','replacement_cost_usd','repair_cost_usd','obs']
col_labels = {'structure_number':'Bridge ID','sa1s_display':hazard_label,
              'predicted_ds':'Pred. DS','replacement_cost_usd':'RCV ($)',
              'repair_cost_usd':'Repair Cost ($)','obs':'Observed DS'}

st.markdown(f"<p style='color:#64748B; font-size:0.85rem;'>Showing <b style='color:#38BDF8'>{len(filtered):,}</b> bridges</p>",
            unsafe_allow_html=True)
st.dataframe(filtered[show_cols].rename(columns=col_labels),
             hide_index=True, use_container_width=True, height=350)

csv = filtered[show_cols].rename(columns=col_labels).to_csv(index=False)
st.download_button(
    "⬇ Download filtered results (CSV)", csv,
    f"loss_results_{title_label.replace(' ','_').replace('—','')}.csv",
    "text/csv"
)

# ── Footer ──────────────────────────────────────────────────────
st.markdown("""
<hr style='border-color:#1C7293; opacity:0.2; margin-top:2rem;'/>
<div style='text-align:center; color:#334155; font-size:0.78rem; padding:0.5rem 0;'>
    CAT411 Catastrophe Modeling Capstone &nbsp;·&nbsp; Lehigh University &nbsp;·&nbsp;
    Calibrated HAZUS fragility (k=2.07, β=0.20) &nbsp;·&nbsp;
    GMPE: Kubilay Albayrak &nbsp;·&nbsp; RCV: Wenyu Chiou &nbsp;·&nbsp;
    Calibration: Sirisha Kedarsetty &nbsp;·&nbsp; Dashboard: Anik Das
</div>
""", unsafe_allow_html=True)
