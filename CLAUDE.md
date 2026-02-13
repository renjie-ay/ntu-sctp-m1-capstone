# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

NTU SCTP Capstone project analyzing ~1M Singapore job postings. The pipeline cleans raw job data, matches job titles to the government SkillsFuture taxonomy using sentence-transformer embeddings, attaches skills, and presents interactive visualizations via Streamlit.

## Commands

```bash
# Environment setup (requires uv package manager)
uv venv .venv --python 3.12
source .venv/bin/activate
uv sync   # installs from uv.lock

# Run the Streamlit app (MUST run from project root — data paths are relative)
streamlit run streamlit/app.py

# Lock dependencies (maintainer only)
uv lock
```

No test runner, linter, or CI/CD is configured.

## Architecture

### Data Pipeline

```
data/SGJobData.csv.xz (raw, compressed)
  → [notebooks/sgjobdata-eda.ipynb] cleaning & processing
  → data/cleaned-sgjobdata.parquet          (base cleaned data)
  → data/cleaned-sgjobdata-exploded.parquet  (categories exploded into rows)
  → data/cleaned-sgjobdata-withskills.parquet (skills-enriched, 6.2M rows)
  → data/skills_optimized.parquet            (pre-aggregated skills timeline)
```

### Key Processing Steps (in sgjobdata-eda.ipynb)

1. **strip_clean_drop()** — normalizes columns, handles unicode, drops empty rows
2. **winsorize_salary_log_iqr()** — caps salary outliers via log-scale IQR (bounds: 1,110–19,783)
3. **explode_categories()** — parses JSON category strings into separate rows
4. **build_title_matcher() / match_titles_embedding()** — semantic matching of job titles to SkillsFuture taxonomy using all-MiniLM-L6-v2 + fuzzy string matching (thresholds: min_sim=0.72, min_margin=0.05, min_fuzzy=85)
5. **attach_skills()** — merges matched titles with government skill taxonomy

Note: The notebook requires heavy dependencies (torch, sentence-transformers, thefuzz) that are in uv.lock but not in pyproject.toml's runtime deps.

### Streamlit App

```
streamlit/
  app.py              # Entry point: page config, global CSS, tab shell, main()
  chart_style.py      # Shared Plotly styling + render helper
  data_loader.py      # All @st.cache_data loading functions
  tabs/
    tab_executive.py   # Tab 1: KPI metrics, top-10 sector bar chart
    tab_sectoral.py    # Tab 2: bulk-factor velocity, hiring heatmap, competition snapshot
    tab_experience.py  # Tab 3: vacancy pie chart, salary boxplot by experience
    tab_opportunity.py # Tab 4: supply-vs-demand treemap, hidden-demand quadrant scatter
    tab_skills.py      # Tab 5: popularity, emerging/declining, premium salary, transferability
```

**Key conventions:**
- Each tab module exposes a `render(df)` function called from `app.py`. Exception: `tab_skills.render()` takes no args and loads its own data via `load_skills_analysis_data()`.
- All charts use Plotly. Always use `render_plotly_chart(fig, key=...)` from `chart_style.py` instead of calling `st.plotly_chart` directly — this applies consistent typography, spacing, grid, hover labels, and modebar config.
- Imports inside tab modules use bare module names (e.g., `from data_loader import ...`, `from chart_style import ...`) because Streamlit runs with `streamlit/` as the working directory.
- Data loading is centralized in `data_loader.py` with `@st.cache_data(ttl=3600)`. The three loaders serve different tabs: `load_exploded_data()` → Tabs 1-4, `load_skills_optimized()` → Tab 2, `load_skills_analysis_data()` → Tab 5.
- Streamlit theme is configured in `.streamlit/config.toml` (light base, red primary color).

### Data Schema

Cleaned dataset (1,044,597 rows): job_id, title, company, min_exp, positionlevels, posting_date, num_applications, num_views, num_vacancies, categories (JSON), average_salary_cleaned. The skills-enriched version adds jobtitle_cleaned and skill columns (6.2M rows after explosion). The exploded version adds a flat `categories` column.

### Other Notebooks

- **notebooks/sgjobdata-eda-ml.ipynb** — abandoned first trial using LLM for skill generation (can ignore)
- **notebooks/analysis.ipynb** — comprehensive skills analysis with visualizations
- **data/jobsandskills-skillsfuture-skills-framework-dataset.xlsx** — government skills taxonomy source

## Known Data Issues

- Salary field has user-input quality problems (skipped entries, annual vs monthly confusion)
- Semantic title matching loses cultural context (e.g., "Driver" → "Engine Driver" instead of "Transport Operator")
- Earlier LLM-based skill generation was abandoned in favor of the government taxonomy (legacy files: `data/sgjobdata_titleskills*.parquet`)
