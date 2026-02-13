import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns


def render(df):
    st.subheader("🛠️ Experience Analysis")
    st.markdown('Objective: Align the "Level" of training with market reality to ensure graduate ROI.')

    exp_comp_sectors = ["All"] + sorted(df["category"].unique().tolist())
    selected_exp_sector = st.selectbox("Filter by Sector:", exp_comp_sectors, key="tab3_sector_filter")

    df_exp = df.copy() if selected_exp_sector == "All" else df[df["category"] == selected_exp_sector]

    c3_new1, c3_new2 = st.columns(2)

    with c3_new1:
        st.markdown("#### Experience Level Distribution")
        st.caption("Distribution of total vacancies by experience level")

        exp_dist = df_exp.groupby("exp_segment")["num_vacancies"].sum().reset_index()
        exp_dist = exp_dist.sort_values("num_vacancies", ascending=False)
        max_idx = exp_dist["num_vacancies"].idxmax()
        explode = [0.1 if idx == max_idx else 0 for idx in exp_dist.index]

        distinct_colors = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#FFA07A", "#98D8C8", "#F7DC6F", "#BB8FCE"]
        fig_pie = go.Figure(data=[go.Pie(
            labels=exp_dist["exp_segment"],
            values=exp_dist["num_vacancies"],
            pull=explode, hole=0.3,
            marker=dict(colors=distinct_colors),
            textinfo="label+percent",
            textposition="auto",
            insidetextorientation="horizontal",
        )])
        fig_pie.update_layout(title="Vacancy Distribution by Experience Level",
                              height=400, showlegend=False)
        st.plotly_chart(fig_pie, use_container_width=True, key="exp_distribution_pie")

    with c3_new2:
        st.markdown("#### Average Salary Distribution by Experience")
        st.caption("Weighted salary ranges across experience levels")

        bins = [0, 2, 5, 10, float("inf")]
        labels = ["0-2 yrs (Entry)", ">2-5 yrs (Mid-Level)",
                  ">5-10 yrs (Senior)", "10+ yrs (Expert)"]
        colors = ["#FFB6C1", "#87CEEB", "#90EE90", "#FFD700"]

        df_plot = df_exp.copy()
        df_plot["exp_group"] = pd.cut(df_plot["min_exp"], bins=bins, labels=labels, right=False)
        df_plot["weight_cap"] = df_plot["num_vacancies"].clip(upper=5)
        df_expanded = df_plot.loc[df_plot.index.repeat(df_plot["weight_cap"].astype(int))].reset_index(drop=True)
        plot_df = df_expanded.dropna(subset=["exp_group", "average_salary"]).copy()

        vacancy_totals = df_plot.groupby("exp_group")["num_vacancies"].sum()

        fig, ax = plt.subplots(figsize=(12, 6))
        sns.boxplot(data=plot_df, x="exp_group", y="average_salary", palette=colors, linewidth=1, ax=ax)
        xticklabels = [f"{grp}\n(Total vacancies: {int(vacancy_totals.get(grp, 0))})" for grp in labels]
        ax.set_xticklabels(xticklabels)
        ax.set_xlabel("Experience (Years)", fontsize=12)
        ax.set_ylabel("Average Salary (SGD)", fontsize=12)
        ax.set_title("Average Salary Distribution by Experience Group (weighted by num_vacancies)",
                     fontsize=14, fontweight="bold")
        plt.grid(True, axis="y", which="major", linestyle="--", alpha=0.6)
        plt.minorticks_on()
        plt.grid(True, which="minor", axis="y", linestyle=":", alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
