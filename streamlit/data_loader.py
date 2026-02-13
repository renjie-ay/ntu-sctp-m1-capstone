import json

import streamlit as st
import pandas as pd


@st.cache_data(ttl=3600, show_spinner="Loading data...")
def load_exploded_data():
    """Load the pre-exploded dataset (categories already expanded)."""
    df = pd.read_parquet("data/cleaned-sgjobdata-exploded.parquet")
    df["posting_date"] = pd.to_datetime(df["posting_date"])
    df["month_year"] = df["posting_date"].dt.to_period("M").dt.to_timestamp()
    df["average_salary"] = df["average_salary_cleaned"]
    df["exp_segment"] = pd.cut(
        df["min_exp"],
        bins=[0, 2, 5, 10, float("inf")],
        labels=["0-2 yrs (Entry/Junior)", ">2-5 yrs (Mid-Level)",
                ">5-10 yrs (Senior)", "10+ yrs (Expert)"],
        right=True,
    )
    return df


@st.cache_data(ttl=3600, show_spinner="Loading skills data...")
def load_skills_optimized():
    """Load pre-aggregated skills timeline data."""
    try:
        return pd.read_parquet("data/skills_optimized.parquet")
    except FileNotFoundError:
        st.info("Skills data file not found. Run scripts/build_skills_optimized.py first.")
        return pd.DataFrame()


@st.cache_data(ttl=3600, show_spinner="Loading skills detail data...")
def load_withskills_data():
    """Load the full skills-enriched dataset (on-demand for Tab 4)."""
    return pd.read_parquet(
        "data/cleaned-sgjobdata-withskills.parquet",
        columns=["job_id", "jobtitle_cleaned", "skill"],
    )


def _extract_category(cat_json):
    """Parse JSON categories field to extract the first category name."""
    try:
        return json.loads(cat_json)[0]["category"]
    except Exception:
        return None


@st.cache_data(ttl=3600, show_spinner="Loading skills analysis data...")
def load_skills_analysis_data():
    """Load the skills-enriched dataset with columns needed for skills analysis."""
    df = pd.read_parquet(
        "data/cleaned-sgjobdata-withskills.parquet",
        columns=[
            "job_id", "posting_date", "min_exp", "num_applications",
            "num_views", "num_vacancies", "categories",
            "average_salary_cleaned", "jobtitle_cleaned", "skill",
        ],
    )
    df["posting_date"] = pd.to_datetime(df["posting_date"])
    df["year_month"] = df["posting_date"].dt.to_period("M")
    df["category_name"] = df["categories"].apply(_extract_category)
    return df
