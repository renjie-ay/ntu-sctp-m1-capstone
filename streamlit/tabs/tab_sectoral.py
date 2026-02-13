import streamlit as st
import pandas as pd
import plotly.express as px

from data_loader import load_skills_optimized


def get_demand_velocity(df):
    velocity_df = df[df["category"] != "Others"]
    top_10 = velocity_df.groupby("category")["num_vacancies"].sum().nlargest(10).index
    velocity_df = velocity_df[velocity_df["category"].isin(top_10)]
    agg_df = velocity_df.groupby(["month_year", "category"]).agg(
        num_applications=("num_applications", "sum"),
        num_vacancies=("num_vacancies", "sum"),
    ).reset_index()
    agg_df["bulk_factor"] = agg_df.apply(
        lambda x: x["num_applications"] / x["num_vacancies"] if x["num_vacancies"] > 0 else 0,
        axis=1,
    )
    return agg_df


def get_bulk_hiring_data(df):
    bulk_df = df[df["category"] != "Others"]
    top_sectors = bulk_df.groupby("category")["num_vacancies"].sum().nlargest(12).index
    bulk_filtered = bulk_df[bulk_df["category"].isin(top_sectors)]
    apps = bulk_filtered.pivot_table(index="category", columns="month_year",
                                     values="num_applications", aggfunc="sum").fillna(0)
    vacs = bulk_filtered.pivot_table(index="category", columns="month_year",
                                     values="num_vacancies", aggfunc="sum").fillna(0)
    return (apps / vacs.replace(0, 1)).fillna(0)


def render(df):
    st.subheader("🏭 Sectoral Demand & Momentum")
    st.markdown("Objective: Identify \"What\" to teach by tracking the velocity of industry needs.")

    st.markdown("#### 📈 Demand Velocity (Bulk Factor)")
    st.caption("Bulk Factor = Applications ÷ Vacancies. Higher values indicate stronger competition.")

    velocity_df = get_demand_velocity(df)
    if len(velocity_df) > 1:
        fig_vel = px.line(velocity_df, x="month_year", y="bulk_factor", color="category",
                          markers=True, line_shape="spline",
                          title="Top 10 Sectors: Bulk Factor Trend Over Time",
                          labels={"month_year": "Posting Date",
                                  "bulk_factor": "Bulk Factor (Apps/Vacancies)",
                                  "category": "Sector"})
        st.plotly_chart(fig_vel, use_container_width=True, key="demand_velocity_chart")
    else:
        st.warning("Not enough data points for time-series velocity.")

    st.markdown("#### 🗺️ Bulk Hiring Map")
    st.caption("Competition intensity by sector and time. Darker = higher bulk factor.")

    bulk_pivot = get_bulk_hiring_data(df)
    fig_bulk = px.imshow(bulk_pivot, aspect="auto", color_continuous_scale="YlOrRd",
                         labels=dict(x="Month", y="Sector", color="Bulk Factor"))
    st.plotly_chart(fig_bulk, use_container_width=True, key="bulk_hiring_map")

    # Skills in High Demand
    st.markdown("#### High Demand Skills")
    st.caption("Top 10 skills by unique job postings over time.")

    skills_df = load_skills_optimized()

    if not skills_df.empty:
        available_months = sorted(skills_df["month_year"].unique())
        month_labels = {}
        for month in available_months:
            date_obj = pd.to_datetime(month)
            month_labels[month] = date_obj.strftime("%b %Y")

        if len(available_months) > 0:
            st.markdown("### 📈 Skill Demand Timeline - Top 10 Most Popular Skills")

            skills_sectors = ["All"] + sorted(skills_df["category"].dropna().unique().tolist())
            col_skills_filter, col_skills_space = st.columns([1, 3])
            with col_skills_filter:
                st.markdown("**Filter by Sector**")
            with col_skills_space:
                selected_skills_sector = st.selectbox("", skills_sectors,
                                                      key="skills_sector_filter",
                                                      label_visibility="collapsed")

            skills_filtered = skills_df.copy()
            if selected_skills_sector != "All":
                skills_filtered = skills_filtered[skills_filtered["category"] == selected_skills_sector]

            top_skills = skills_filtered.groupby("skill")["job_count"].sum().nlargest(10).index.tolist()

            if top_skills:
                timeline_df = skills_filtered[skills_filtered["skill"].isin(top_skills)].copy()
                timeline_df = timeline_df.groupby(["skill", "month_year"])["job_count"].sum().reset_index()
                timeline_df["month_label"] = timeline_df["month_year"].map(month_labels)

                fig = px.line(
                    timeline_df, x="month_label", y="job_count", color="skill", markers=True,
                    title=("Skill Demand Timeline - Top 10 Most Popular Skills"
                           if selected_skills_sector == "All"
                           else f"Top 10 Skills in {selected_skills_sector}"),
                    labels={"month_label": "Month-Year Period",
                            "job_count": "Number of Unique Job Postings",
                            "skill": "Skill"},
                )
                fig.update_layout(
                    height=600, hovermode="x unified",
                    legend=dict(title="Skills", orientation="v",
                                yanchor="top", y=1, xanchor="left", x=1.02),
                )
                fig.update_traces(line=dict(width=2.5))
                st.plotly_chart(fig, use_container_width=True, key="skills_demand_chart")
            else:
                st.info(f"No skills data available for {selected_skills_sector}")
        else:
            st.info("No date information available in skills data.")
    else:
        st.info("Skills data file not found or empty.")
