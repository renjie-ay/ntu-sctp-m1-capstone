import streamlit as st

from data_loader import load_exploded_data
from tabs import tab_executive, tab_sectoral, tab_experience, tab_opportunity, tab_skills

st.set_page_config(
    page_title="SG Job Market Dashboard for Curriculum Design",
    layout="wide",
    page_icon="📊",
)

st.markdown("""
<style>
    .metric-card {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 8px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .metric-value {
        font-size: 24px;
        font-weight: 700;
        color: #2c3e50 !important;
    }
    .metric-label {
        font-size: 14px;
        color: #6c757d !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .insight-box {
        background-color: #e3f2fd;
        border-left: 5px solid #2196f3;
        padding: 15px;
        border-radius: 4px;
        margin-top: 10px;
        margin-bottom: 20px;
        height: 100%;
    }
    .insight-text {
        color: #000000 !important;
        font-size: 16px;
        line-height: 1.5;
    }
    .finding-title {
        font-weight: bold;
        color: #0d47a1 !important;
        margin-bottom: 5px;
        font-size: 18px;
    }
    li {
        color: #000000 !important;
        margin-bottom: 5px;
    }
    b {
        font-weight: 700;
        color: #000;
    }
    [data-testid="stSelectbox"] label, [data-testid="stSelectbox"] p {
        color: #1e293b !important;
    }
    [data-testid="stSelectbox"] div[data-baseweb="select"] {
        background-color: #ffffff !important;
        color: #1e293b !important;
    }
    [data-baseweb="select"] > div {
        background-color: #ffffff !important;
        color: #1e293b !important;
    }
    [data-baseweb="popover"] li, [data-baseweb="popover"] [role="option"] {
        background-color: #ffffff !important;
        color: #1e293b !important;
    }
    [data-baseweb="popover"] li:hover, [data-baseweb="popover"] [role="option"]:hover {
        background-color: #f1f5f9 !important;
        color: #0f172a !important;
    }
    option {
        background-color: #ffffff !important;
        color: #1e293b !important;
    }
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 0rem !important;
    }
    header {
        visibility: hidden;
    }
</style>
""", unsafe_allow_html=True)


def run_dashboard(df):
    if df.empty:
        st.error("No valid data found after loading. Please check your data files.")
        st.stop()

    min_d = df["posting_date"].min().strftime("%d %b %Y")
    max_d = df["posting_date"].max().strftime("%d %b %Y")

    st.title("🎓 SG Job Market Dashboard for Curriculum Design")
    st.markdown("Aligning Curriculum with Real-Time Market Structure")
    st.write(f"**Data Period:** {min_d} - {max_d}")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Executive Summary",
        "🏭 Sectoral Demand & Momentum",
        "🛠️ Experience Level",
        "🎓 Opportunity",
        "🔬 Skills Analysis",
    ])

    with tab1:
        tab_executive.render(df)
    with tab2:
        tab_sectoral.render(df)
    with tab3:
        tab_experience.render(df)
    with tab4:
        tab_opportunity.render(df)
    with tab5:
        tab_skills.render()


def main():
    df = load_exploded_data()
    run_dashboard(df)


if __name__ == "__main__":
    main()
