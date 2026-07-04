import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.intelligence import PenaltyIntelligenceEngine, KeeperArchetype, PressureProfile
from src.adapters import CSVAdapter

st.set_page_config(page_title="Penalty Intelligence System", layout="wide")
if 'compare_mode' not in st.session_state: st.session_state.compare_mode = False

engine = PenaltyIntelligenceEngine()
data_path = os.path.join(os.path.dirname(__file__), "../data/demo_penalties.csv")
adapter = CSVAdapter(data_path)

st.sidebar.title("Penalty Intelligence")
source = st.sidebar.selectbox("Data Source", ["Demo Dataset", "Upload Custom CSV"])
if source == "Upload Custom CSV":
    uploaded_file = st.sidebar.file_uploader("Choose CSV file", type=['csv'])
    df = pd.read_csv(uploaded_file) if uploaded_file else adapter.fetch_penalties()
else: df = adapter.fetch_penalties()

st.sidebar.markdown("---")
st.sidebar.subheader("Shooter Profile")
shooter_foot = st.sidebar.selectbox("Dominant Foot", ["Right", "Left", "Either"])
match_context = st.sidebar.selectbox("Match Context", ["Normal", "Shootout", "Elimination"])
st.sidebar.markdown("---")
if st.sidebar.button("Toggle Compare All"): st.session_state.compare_mode = not st.session_state.compare_mode

if st.session_state.compare_mode:
    st.title("Goalkeeper Comparison")
    all_k = df['goalkeeper'].unique()
    sel_k = st.multiselect("Select Keepers", all_k, default=list(all_k[:3]))
    if sel_k:
        comp_df = engine.compare_keepers(df, sel_k)
        st.table(comp_df)
        comp_df['Save Rate Float'] = comp_df['Save Rate'].str.rstrip('%').astype('float') / 100.0
        st.bar_chart(comp_df.set_index('Keeper')['Save Rate Float'])
else:
    keeper_name = st.selectbox("Select Goalkeeper", df['goalkeeper'].unique())
    profile = engine.analyze_goalkeeper(df, keeper_name)
    strategy = engine.generate_shooter_strategy(profile, shooter_foot, "high" if match_context != "Normal" else "normal")
    cols = st.columns(5)
    cols[0].metric("Penalties Faced", profile.total_penalties)
    cols[1].metric("Goals Conceded", profile.goals_conceded)
    cols[2].metric("Save Rate", f"{profile.overall_save_rate:.1%}")
    cols[3].metric("Archetype", profile.archetype.value)
    cols[4].metric("Confidence", f"{profile.recommendation_confidence:.0%}")
    tabs = st.tabs(["Heatmap", "Zone Breakdown", "Tactical Intelligence", "Scouting Report"])
    with tabs[0]:
        st.subheader(f"Vulnerability Heatmap: {keeper_name}")
        goals = df[(df['goalkeeper'] == keeper_name) & (df['outcome'] == 'Goal')]
        saves = df[(df['goalkeeper'] == keeper_name) & (df['outcome'] == 'Saved')]
        missed = df[(df['goalkeeper'] == keeper_name) & (df['outcome'] == 'Missed')]
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot([-4, 4], [2.67, 2.67], color='black', linewidth=3)
        ax.plot([-4, -4], [0, 2.67], color='black', linewidth=3)
        ax.plot([4, 4], [0, 2.67], color='black', linewidth=3)
        if len(goals) > 2:
            y, z = np.mgrid[-4:4:100j, 0:2.67:100j]
            kernel = gaussian_kde(np.vstack([goals['goal_y'], goals['goal_z']]))
            f = np.reshape(kernel(np.vstack([y.ravel(), z.ravel()])).T, y.shape)
            ax.contourf(y, z, f, cmap='YlOrRd', alpha=0.7)
        ax.scatter(goals['goal_y'], goals['goal_z'], color='red', label='Goal')
        ax.scatter(saves['goal_y'], saves['goal_z'], color='blue', marker='x', label='Saved')
        ax.scatter(missed['goal_y'], missed['goal_z'], color='gray', marker='^', label='Missed')
        if profile.primary_weakness:
            wy, wz = engine._zone_to_coords(profile.primary_weakness)
            ax.text(wy, wz, "PRIMARY", color='white', weight='bold', bbox=dict(facecolor='red', alpha=0.8))
        ax.legend(); st.pyplot(fig)
        st.markdown("### Coach Instruction Cards")
        c1, c2 = st.columns(2)
        with c1: st.error(f"**Primary Target: {profile.primary_weakness}**")
        with c2: st.warning(f"**Side Guidance: {strategy['side_guidance']}**")
    with tabs[1]:
        z_data = []
        for zone, data in profile.zones.items():
            z_data.append({"Zone": zone, "Total": data.total_shots, "Conceded": data.goals_conceded, "Saves": data.saves, "Rate": f"{data.concession_rate:.1%}", "Sig": "✅" if data.statistical_significance else "❌"})
        st.table(pd.DataFrame(z_data).sort_values("Conceded", ascending=False))
        st.markdown("### Vulnerability Grid (3x3)")
        for r in ["T", "M", "B"]:
            c1, c2, c3 = st.columns(3)
            for i, c in enumerate(["L", "C", "R"]):
                z = f"{r}{c}"; rate = profile.zones[z].concession_rate
                [c1, c2, c3][i].metric(z, f"{rate:.0%}"); [c1, c2, c3][i].progress(rate)
    with tabs[2]:
        st.info(f"**Archetype: {profile.archetype.value}**")
        st.write(f"**Pressure Profile: {profile.pressure_profile.value}**")
        for t in strategy['tactics']: st.write(f"- {t}")
    with tabs[3]:
        report = engine.generate_pre_match_briefing(profile)
        st.text_area("Full Report", report, height=400)
        st.download_button("Export Report", report, file_name=f"{keeper_name}_scouting_report.txt")
