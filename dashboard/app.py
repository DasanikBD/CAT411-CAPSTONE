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

st.set_page_config(
    page_title="Bridge Loss Assessment — Northridge 1994",
    page_icon="🌉",
    layout="wide",
    initial_sidebar_state="expanded"
)

BRIDGE_BG = """
<div id="bridge-bg" style="
    position: fixed; top: 0; left: 0; width: 100%; height: 100%;
    z-index: -999; overflow: hidden; pointer-events: none;">
  <svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%"
       viewBox="0 0 1440 800" preserveAspectRatio="xMidYMid slice">
    <defs>
      <linearGradient id="skyGrad" x1="0%" y1="0%" x2="0%" y2="100%">
        <stop offset="0%" style="stop-color:#0F172A;stop-opacity:1"/>
        <stop offset="100%" style="stop-color:#1E293B;stop-opacity:1"/>
      </linearGradient>
      <filter id="glow">
        <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
        <feMerge><feMergeNode in="coloredBlur"/><feMergeNode in="SourceGraphic"/></feMerge>
      </filter>
      <style>
        @keyframes sway { 0%,100% { transform: translateY(0px); } 50% { transform: translateY(-4px); } }
        @keyframes shimmer { 0%,100% { opacity: 0.15; } 50% { opacity: 0.3; } }
        @keyframes scan { 0% { transform: translateX(-200px); opacity: 0; } 10% { opacity: 0.4; } 90% { opacity: 0.4; } 100% { transform: translateX(1600px); opacity: 0; } }
        .cable { animation: sway 6s ease-in-out infinite; }
        .tower { animation: shimmer 4s ease-in-out infinite; }
        .scan-line { animation: scan 12s linear infinite; }
      </style>
    </defs>
    <rect width="1440" height="800" fill="url(#skyGrad)" opacity="0.98"/>
    <g opacity="0.4">
      <circle cx="100" cy="80" r="1" fill="#E2E8F0"/>
      <circle cx="250" cy="50" r="1.5" fill="#E2E8F0"/>
      <circle cx="400" cy="120" r="1" fill="#E2E8F0"/>
      <circle cx="600" cy="40" r="1.2" fill="#E2E8F0"/>
      <circle cx="800" cy="90" r="1" fill="#E2E8F0"/>
      <circle cx="1000" cy="60" r="1.5" fill="#E2E8F0"/>
      <circle cx="1200" cy="110" r="1" fill="#E2E8F0"/>
      <circle cx="1350" cy="45" r="1.2" fill="#E2E8F0"/>
    </g>
    <rect x="0" y="620" width="1440" height="180" fill="#0F172A" opacity="0.9"/>
    <rect x="0" y="580" width="1440" height="12" fill="#1E293B" opacity="0.8"/>
    <rect x="0" y="590" width="1440" height="3" fill="#065A82" opacity="0.5"/>
    <g class="tower" filter="url(#glow)">
      <rect x="295" y="320" width="18" height="270" fill="#1C7293" opacity="0.35"/>
      <rect x="303" y="300" width="3" height="290" fill="#38BDF8" opacity="0.15"/>
      <rect x="270" y="440" width="70" height="8" fill="#1C7293" opacity="0.3"/>
      <circle cx="304" cy="315" r="4" fill="#38BDF8" opacity="0.6"/>
      <circle cx="304" cy="315" r="8" fill="#38BDF8" opacity="0.15"/>
    </g>
    <g class="tower" filter="url(#glow)" style="animation-delay:2s">
      <rect x="1127" y="320" width="18" height="270" fill="#1C7293" opacity="0.35"/>
      <rect x="1135" y="300" width="3" height="290" fill="#38BDF8" opacity="0.15"/>
      <rect x="1102" y="440" width="70" height="8" fill="#1C7293" opacity="0.3"/>
      <circle cx="1136" cy="315" r="4" fill="#38BDF8" opacity="0.6"/>
      <circle cx="1136" cy="315" r="8" fill="#38BDF8" opacity="0.15"/>
    </g>
    <g class="cable" opacity="0.3">
      <path d="M0,560 Q304,300 720,420 Q1136,300 1440,560" stroke="#38BDF8" stroke-width="2" fill="none"/>
    </g>
    <g opacity="0.12" stroke="#38BDF8" stroke-width="0.8">
      <line x1="304" y1="440" x2="304" y2="582"/>
      <line x1="720" y1="420" x2="720" y2="582"/>
      <line x1="1136" y1="440" x2="1136" y2="582"/>
    </g>
    <text x="30" y="780" font-family="monospace" font-size="11" fill="#1C7293" opacity="0.4">
      NORTHRIDGE 1994 · 2,008 BRIDGES · LOSS ASSESSMENT
    </text>
  </svg>
</div>
"""

st.markdown("""
<style>
    .stApp { 
        background: 
            linear-gradient(135deg, rgba(15,23,42,0.82) 0%, rgba(30,41,59,0.80) 50%, rgba(15,23,42,0.82) 100%),
            url('./assets/bridge_bg.jpg');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        color: #E2E8F0; 
    }
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #065A82 0%, #021B2E 100%); border-right: 1px solid #1C7293; }
    [data-testid="stSidebar"] * { color: #E2E8F0 !important; }
    [data-testid="metric-container"] { background: linear-gradient(135deg, #1E293B, #0F2744); border: 1px solid #1C7293; border-radius: 12px; padding: 16px; }
    [data-testid="metric-container"] label { color: #94A3B8 !important; font-size: 0.85rem !important; font-weight: 600 !important; text-transform: uppercase !important; }
    [data-testid="metric-container"] [data-testid="stMetricValue"] { color: #38BDF8 !important; font-size: 1.8rem !important; font-weight: 700 !important; }
    h1 { color: #F1F5F9 !important; font-weight: 800 !important; }
    h2 { color: #E2E8F0 !important; } h3 { color: #CBD5E1 !important; }
    hr { border-color: #1C7293 !important; opacity: 0.4; }
    .stTabs [data-baseweb="tab-list"] { background: #1E293B; border-radius: 8px; border: 1px solid #1C7293; }
    .stTabs [aria-selected="true"] { color: #38BDF8 !important; background: #065A82 !important; border-radius: 6px !important; }
</style>
""", unsafe_allow_html=True)

# ── Load data ──────────────────────────────────────────────────
@st.cache_data
def load_data():
    base = Path(__file__).parent
    sm   = pd.read_csv(base / "shakemap_results.csv")
    gmpe = pd.read_csv(base / "gmpe_results.csv")
    return sm, gmpe

sm_df, gmpe_df = load_data()
st.markdown(BRIDGE_BG, unsafe_allow_html=True)

DS_COLORS = {"none":"#64748B","slight":"#EAB308","moderate":"#F97316","extensive":"#EF4444","complete":"#7F1D1D"}
DS_ORDER  = ["none","slight","moderate","extensive","complete"]

# ── Sidebar ────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 1rem 0;'>
        <div style='font-size:2.5rem;'>🌉</div>
        <div style='font-size:1.1rem; font-weight:800; color:#F1F5F9;'>LOSS ASSESSMENT</div>
        <div style='font-size:0.75rem; color:#94A3B8; margin-top:4px;'>Northridge 1994 · 2,008 Bridges</div>
    </div>
    <hr style='border-color:#1C7293; opacity:0.4;'/>
    """, unsafe_allow_html=True)

    mode = st.radio("**Select Hazard Input**", ["ShakeMap", "GMPE"])
    if mode == "GMPE":
        gmpe_model = st.selectbox("**GMPE Model**", ["ASK14","BSSA14","CB14","CY14"])

    st.markdown("**Fragility Parameters**")
    st.markdown("""
    <div style='background:rgba(6,90,130,0.3); border:1px solid #1C7293; border-radius:8px; padding:10px; font-size:0.9rem;'>
        k = 2.07 · Calibrated<br>
        <span style='color:#94A3B8; font-size:0.8rem;'>HAZUS lognormal fragility model</span>
    </div>""", unsafe_allow_html=True)

    st.markdown("**HAZUS Damage Ratios**")
    st.markdown("""
    <div style='background:rgba(6,90,130,0.2); border-radius:8px; padding:10px; font-size:0.85rem; line-height:1.8;'>
        🟡 Slight &nbsp; 3%<br>🟠 Moderate &nbsp; 8%<br>🔴 Extensive &nbsp; 25%<br>🔴 Complete &nbsp; 100%
    </div>""", unsafe_allow_html=True)

    st.markdown("""
    <hr/>
    <div style='font-size:0.75rem; color:#475569; text-align:center;'>
        CAT411 Capstone · Lehigh University<br>Spring 2026 · Anik Das
    </div>""", unsafe_allow_html=True)

# ── Active dataset ─────────────────────────────────────────────
if mode == "ShakeMap":
    active = sm_df.copy()
    active["sa1s_display"] = active["sa1s_shakemap"]
    hazard_label = "ShakeMap Sa(1.0s)"
    title_label  = "ShakeMap"
else:
    active = gmpe_df[gmpe_df["gmpe_model"] == gmpe_model].copy()
    active["sa1s_display"] = active["sa1s_used"]
    hazard_label = f"{gmpe_model} Sa(1.0s)"
    title_label  = f"GMPE — {gmpe_model}"

active["ds_color"] = active["predicted_ds"].map(DS_COLORS)

# ── Header ─────────────────────────────────────────────────────
st.markdown(f"""
<div style='padding: 1.5rem 0 0.5rem 0;'>
    <h1 style='margin:0; font-size:2.2rem; background: linear-gradient(90deg, #38BDF8, #818CF8);
               -webkit-background-clip:text; -webkit-text-fill-color:transparent;'>
        Bridge Loss Assessment — {title_label}
    </h1>
    <p style='color:#64748B; margin:4px 0 0 0; font-size:0.9rem;'>
        Northridge 1994 Earthquake · {len(active):,} bridges · Calibrated HAZUS fragility (k=2.07)
    </p>
</div>
<hr style='border-color:#1C7293; opacity:0.3;'/>
""", unsafe_allow_html=True)

# ── KPI Cards ──────────────────────────────────────────────────
total_cost = active["repair_cost_usd"].sum()
damaged    = active[active["predicted_ds"] != "none"]
n_damaged  = len(damaged)
avg_cost   = damaged["repair_cost_usd"].mean() if n_damaged > 0 else 0
max_row    = active.loc[active["repair_cost_usd"].idxmax()]

k1,k2,k3,k4,k5 = st.columns(5)
k1.metric("Total Repair Cost",   f"${total_cost/1e6:.1f}M")
k2.metric("Bridges with Damage", f"{n_damaged:,}")
k3.metric("% Damaged",           f"{n_damaged/len(active)*100:.1f}%")
k4.metric("Avg Cost (damaged)",  f"${avg_cost/1e3:.0f}K")
k5.metric("Costliest Bridge",    f"${max_row['repair_cost_usd']/1e6:.1f}M",
           delta=str(max_row["structure_number"]), delta_color="off")

st.markdown("<hr style='border-color:#1C7293; opacity:0.2;'/>", unsafe_allow_html=True)

# ── Map + Distribution ─────────────────────────────────────────
col_map, col_dist = st.columns([3, 2])

with col_map:
    # Bull's-eye toggle only available for ShakeMap (has observed data)
    if mode == "ShakeMap":
        map_mode = st.radio(
            "**Map View**",
            ["📍 Predicted Damage", "🎯 Prediction vs Observed"],
            horizontal=True,
            key="map_toggle"
        )
    else:
        map_mode = "📍 Predicted Damage"

    if map_mode == "📍 Predicted Damage":
        # ── Standard map (original) ───────────────────────────────
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
                    "repair_cost_usd":"Repair Cost ($)","replacement_cost_usd":"Replacement Cost ($)"},
            zoom=9, center={"lat":34.2,"lon":-118.5},
            mapbox_style="carto-darkmatter", height=480,
        )
        fig_map.update_layout(
            margin={"r":0,"t":0,"l":0,"b":0},
            legend_title_text="Damage State",
            paper_bgcolor="rgba(0,0,0,0)",
            legend=dict(bgcolor="rgba(15,23,42,0.8)", bordercolor="#1C7293",
                        borderwidth=1, font=dict(color="#E2E8F0"))
        )
        st.plotly_chart(fig_map, use_container_width=True)

    else:
        # ── Bull's-Eye Mismatch Map ───────────────────────────────
        st.markdown("### 🎯 Prediction vs Observed — Mismatch Map")
        st.caption("Outer ring size = magnitude of mismatch · Inner dot color = observed damage state")

        ds_idx_map = {ds:i for i,ds in enumerate(DS_ORDER)}
        plot_df = active.copy()
        plot_df["obs_clean"] = plot_df["obs"].str.lower().str.strip()
        plot_df["obs_idx"]   = plot_df["obs_clean"].map(ds_idx_map)
        plot_df["pred_idx"]  = plot_df["predicted_ds"].map(ds_idx_map)
        plot_df["gap"]       = plot_df["pred_idx"] - plot_df["obs_idx"]
        plot_df["match_type"] = plot_df["gap"].apply(
            lambda g: "✅ Match" if g == 0
                      else ("🔺 Overpredicted" if g > 0 else "🔻 Underpredicted")
        )

        MISMATCH_COLORS = {
            "✅ Match"         : "#64748B",
            "🔺 Overpredicted" : "#38BDF8",
            "🔻 Underpredicted": "#EF4444",
        }
        MISMATCH_ORDER = ["✅ Match", "🔺 Overpredicted", "🔻 Underpredicted"]

        # Outer ring size scales with gap magnitude
        plot_df["outer_size"] = (plot_df["gap"].abs() * 7 + 8).clip(upper=32)

        fig_bull = go.Figure()

        # Layer 1 — matched bridges as tiny green dots (no rings)
        matched = plot_df[plot_df["gap"] == 0]
        fig_bull.add_trace(go.Scattermapbox(
            lat=matched["latitude"], lon=matched["longitude"],
            mode="markers",
            marker=dict(size=3, color="#22C55E", opacity=0.45),
            name="✅ Match",
            hoverinfo="skip",
            showlegend=True,
        ))

        # Layer 2 — mismatched bridges: outer ring (size = gap magnitude)
        mismatched = plot_df[plot_df["gap"] != 0]
        for mtype in ["🔺 Overpredicted", "🔻 Underpredicted"]:
            sub = mismatched[mismatched["match_type"] == mtype]
            fig_bull.add_trace(go.Scattermapbox(
                lat=sub["latitude"], lon=sub["longitude"],
                mode="markers",
                marker=dict(
                    size=sub["outer_size"],
                    color=MISMATCH_COLORS[mtype],
                    opacity=0.35,
                ),
                name=mtype,
                hoverinfo="skip",
                showlegend=True,
            ))

        # Layer 3 — inner dot for mismatched only (observed DS color)
        for mtype in ["🔺 Overpredicted", "🔻 Underpredicted"]:
            sub = mismatched[mismatched["match_type"] == mtype]
            fig_bull.add_trace(go.Scattermapbox(
                lat=sub["latitude"], lon=sub["longitude"],
                mode="markers",
                marker=dict(
                    size=7,
                    color=[DS_COLORS.get(d, "#64748B") for d in sub["obs_clean"]],
                    opacity=1.0,
                ),
                customdata=sub[["structure_number","obs_clean","predicted_ds",
                                "year_built","hwb_class","repair_cost_usd","gap"]].values,
                hovertemplate=(
                    "<b>Bridge %{customdata[0]}</b><br>"
                    "─────────────────<br>"
                    "Observed DS : <b>%{customdata[1]}</b><br>"
                    "Predicted DS: <b>%{customdata[2]}</b><br>"
                    "DS Gap      : %{customdata[6]:+d} states<br>"
                    "─────────────────<br>"
                    "Year Built  : %{customdata[3]}<br>"
                    "HWB Class   : %{customdata[4]}<br>"
                    "Repair Cost : $%{customdata[5]:,.0f}"
                    "<extra></extra>"
                ),
                showlegend=False,
            ))

        fig_bull.update_layout(
            mapbox_style="carto-darkmatter",
            mapbox_zoom=9,
            mapbox_center={"lat":34.2,"lon":-118.5},
            margin={"r":0,"t":0,"l":0,"b":0},
            height=440,
            paper_bgcolor="rgba(0,0,0,0)",
            legend=dict(
                title="Prediction Match",
                bgcolor="rgba(15,23,42,0.85)",
                bordercolor="#1C7293", borderwidth=1,
                font=dict(color="#E2E8F0"),
                x=0.01, y=0.99,
            )
        )
        st.plotly_chart(fig_bull, use_container_width=True)

        # Summary mini-metrics below map
        n_match = (plot_df["gap"] == 0).sum()
        n_over  = (plot_df["gap"] >  0).sum()
        n_under = (plot_df["gap"] <  0).sum()
        m1, m2, m3 = st.columns(3)
        m1.metric("✅ Exact Match",    f"{n_match:,}", f"{n_match/len(plot_df)*100:.1f}%")
        m2.metric("🔺 Overpredicted",  f"{n_over:,}",  f"{n_over/len(plot_df)*100:.1f}%",  delta_color="off")
        m3.metric("🔻 Underpredicted", f"{n_under:,}", f"{n_under/len(plot_df)*100:.1f}%", delta_color="inverse")

with col_dist:
    st.markdown("### 📊 Damage State Distribution")
    obs_counts  = active["obs"].str.lower().value_counts().reindex(DS_ORDER, fill_value=0)
    pred_counts = active["predicted_ds"].value_counts().reindex(DS_ORDER, fill_value=0)
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
        paper_bgcolor="rgba(15,23,42,0)", plot_bgcolor="rgba(30,41,59,0.6)",
        font=dict(color="#E2E8F0"), barmode="group", height=210,
        yaxis_title="% of Bridges", xaxis_gridcolor="#1E3A5F", yaxis_gridcolor="#1E3A5F",
        legend=dict(orientation="h", y=1.12, bgcolor="rgba(0,0,0,0)", font=dict(color="#E2E8F0")),
        margin=dict(t=10,b=40,l=50,r=10)
    )
    st.plotly_chart(fig_dist, use_container_width=True)

    st.markdown("### 💰 Repair Cost by Damage State")
    cost_by_ds = active.groupby("predicted_ds")["repair_cost_usd"].sum().reindex(DS_ORDER, fill_value=0)
    fig_cost = go.Figure(go.Bar(
        x=[d.capitalize() for d in DS_ORDER],
        y=[cost_by_ds[ds]/1e6 for ds in DS_ORDER],
        marker_color=[DS_COLORS[ds] for ds in DS_ORDER],
        marker_line_color="#1E293B", marker_line_width=1,
        text=[f"${cost_by_ds[ds]/1e6:.1f}M" for ds in DS_ORDER],
        textposition="outside", textfont=dict(color="#E2E8F0", size=11)
    ))
    fig_cost.update_layout(
        paper_bgcolor="rgba(15,23,42,0)", plot_bgcolor="rgba(30,41,59,0.6)",
        font=dict(color="#E2E8F0"), height=200, yaxis_title="Repair Cost ($M)",
        xaxis_gridcolor="#1E3A5F", yaxis_gridcolor="#1E3A5F",
        margin=dict(t=10,b=40,l=50,r=10), showlegend=False
    )
    st.plotly_chart(fig_cost, use_container_width=True)

# ── Top 10 + Scatter ───────────────────────────────────────────
st.markdown("<hr style='border-color:#1C7293; opacity:0.2;'/>", unsafe_allow_html=True)
col_top, col_scatter = st.columns([2, 3])

with col_top:
    st.markdown("### 🏆 Top 10 Costliest Bridges")
    top10 = (active[active["repair_cost_usd"] > 0]
             .nlargest(10, "repair_cost_usd")
             [["structure_number","hwb_class","year_built","predicted_ds","repair_cost_usd"]]
             .copy())
    top10["repair_cost_usd"] = top10["repair_cost_usd"].apply(lambda x: f"${x:,.0f}")
    top10.columns = ["Bridge ID","HWB","Year","Damage State","Repair Cost"]
    st.dataframe(top10, hide_index=True, use_container_width=True)

with col_scatter:
    st.markdown("### 📈 Sa(1.0s) vs Repair Cost")
    fig_sc = px.scatter(
        active, x="sa1s_display", y="repair_cost_usd",
        color="predicted_ds", color_discrete_map=DS_COLORS,
        category_orders={"predicted_ds": DS_ORDER},
        hover_name="structure_number",
        labels={"sa1s_display":hazard_label,"repair_cost_usd":"Repair Cost ($)","predicted_ds":"Damage State"},
        height=300, opacity=0.75, template="plotly_dark"
    )
    fig_sc.update_layout(
        paper_bgcolor="rgba(15,23,42,0)", plot_bgcolor="rgba(30,41,59,0.6)",
        font=dict(color="#E2E8F0"), xaxis_gridcolor="#1E3A5F", yaxis_gridcolor="#1E3A5F",
        margin=dict(t=10,b=40,l=60,r=10), legend_title_text="Damage State"
    )
    st.plotly_chart(fig_sc, use_container_width=True)

# ── Full table ─────────────────────────────────────────────────
st.markdown("<hr style='border-color:#1C7293; opacity:0.2;'/>", unsafe_allow_html=True)
st.markdown("### 📋 Full Bridge Data Table")

f1, f2, f3 = st.columns(3)
ds_filter  = f1.multiselect("Filter by Damage State",
                             [d.capitalize() for d in DS_ORDER],
                             default=[d.capitalize() for d in DS_ORDER])
hwb_filter = f2.multiselect("Filter by HWB Class",
                              sorted(active["hwb_class"].dropna().unique()),
                              default=sorted(active["hwb_class"].dropna().unique()))
min_cost   = f3.number_input("Min Repair Cost ($)", min_value=0, value=0, step=10000)

filtered = active[
    (active["predicted_ds"].str.capitalize().isin(ds_filter)) &
    (active["hwb_class"].isin(hwb_filter)) &
    (active["repair_cost_usd"] >= min_cost)
].copy()

show_cols  = ["structure_number","latitude","longitude","year_built","hwb_class",
              "sa1s_display","predicted_ds","replacement_cost_usd","repair_cost_usd","obs"]
col_labels = {"structure_number":"Bridge ID","sa1s_display":hazard_label,
              "predicted_ds":"Pred. DS","replacement_cost_usd":"RCV ($)",
              "repair_cost_usd":"Repair Cost ($)","obs":"Observed DS"}

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

# ── Footer ─────────────────────────────────────────────────────
st.markdown("""
<hr style='border-color:#1C7293; opacity:0.2; margin-top:2rem;'/>
<div style='text-align:center; color:#334155; font-size:0.78rem; padding:0.5rem 0;'>
    CAT411 Catastrophe Modeling Capstone &nbsp;·&nbsp; Lehigh University &nbsp;·&nbsp;
    Calibrated HAZUS fragility (k=2.07) &nbsp;·&nbsp;
    GMPE: Kubilay Albayrak &nbsp;·&nbsp; RCV: Wenyu Chiou &nbsp;·&nbsp;
    Calibration: Sirisha Kedarsetty &nbsp;·&nbsp; Dashboard: Anik Das
</div>
""", unsafe_allow_html=True)
