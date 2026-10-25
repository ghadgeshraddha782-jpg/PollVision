
import re
from collections import Counter

import pandas as pd
import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS


# =========================================================
# 1. PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="PollVision | Poll Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# =========================================================
# 2. PROFESSIONAL THEME
# =========================================================


st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
    --teal: #123B3A;
    --teal-light: #1D5550;
    --mint: #35B88F;
    --mint-light: #E4F7EF;
    --page: #F4F8F7;
    --text: #183C3A;
    --muted: #718582;
    --border: #DFEAE6;
}

/* Global typography */
html,
body,
[class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Main application background */
.stApp {
    background: var(--page);
    color: var(--text);
}

/* Keep the Streamlit app content inside the viewport */
[data-testid="stAppViewContainer"] {
    background: var(--page);
}

[data-testid="stMain"] {
    overflow: visible;
}

/* Main content spacing — prevent the top content from being clipped */
.block-container,
[data-testid="stAppViewBlockContainer"] {
    max-width: 1450px;
    padding-top: 2.5rem !important;
    padding-bottom: 3rem !important;
    margin-left: auto;
    margin-right: auto;
    overflow: visible !important;
}

/* Headings */
h1,
h2,
h3 {
    color: var(--teal) !important;
}

p,
label {
    color: var(--text);
}

/* Radio navigation container */
div[data-testid="stRadio"] > div {
    display: flex;
    flex-direction: row;
    flex-wrap: wrap;
    gap: 7px;
    padding: 10px;
    background: white;
    border: 1px solid var(--border);
    border-radius: 14px;
}

/* Navigation labels */
div[data-testid="stRadio"] label {
    border-radius: 9px;
    padding: 7px 12px;
    font-weight: 600;
    font-size: 13px;
}

/* Selected navigation item */
div[data-testid="stRadio"] label:has(input:checked) {
    background: var(--teal);
    color: white !important;
}

div[data-testid="stRadio"] label:has(input:checked) p,
div[data-testid="stRadio"] label:has(input:checked) span {
    color: white !important;
}

/* Home page hero card */
.hero-card {
    background: linear-gradient(125deg, #123B3A, #236B5D);
    border-radius: 22px;
    padding: 35px;
    color: white;
    margin: 12px 0 24px;
    overflow-wrap: anywhere;
}

.hero-card h1 {
    color: white !important;
    font-size: 36px;
    line-height: 1.3;
    margin-top: 0;
}

.hero-card p {
    color: #D7F0E8;
    line-height: 1.8;
}

/* Feature cards */
.feature-card {
    background: white;
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 21px;
    min-height: 130px;
    margin-bottom: 12px;
}

/* Metric cards */
[data-testid="stMetric"] {
    background: white;
    padding: 17px;
    border: 1px solid var(--border);
    border-radius: 14px;
}

/* Primary buttons */
.stButton > button {
    background-color: #0F4C45 !important;
    color: #FFFFFF !important;
    border: 1px solid #0F4C45 !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
}

.stButton > button p,
.stButton > button span {
    color: #FFFFFF !important;
}

.stButton > button:hover {
    background-color: #176B5B !important;
    border-color: #176B5B !important;
}

/* Download buttons */
.stDownloadButton > button {
    background: #E4F7EF !important;
    color: #123B3A !important;
    border: 1px solid #B8E8D4 !important;
    border-radius: 10px !important;
}

.stDownloadButton > button p,
.stDownloadButton > button span {
    color: #123B3A !important;
}

/* Inputs and dropdowns */
.stSelectbox,
.stMultiSelect,
.stTextInput,
.stNumberInput,
.stTextArea,
.stDateInput {
    color: var(--text);
}

/* Dataframes and tables */
[data-testid="stDataFrame"],
[data-testid="stTable"] {
    border-radius: 12px;
    overflow: hidden;
}

/* Images and charts should fit their container */
[data-testid="stImage"],
[data-testid="stPlotlyChart"] {
    max-width: 100%;
}

/* Hide Streamlit footer */
footer {
    visibility: hidden;
}

/* Responsive layout */
@media (max-width: 700px) {
    .block-container,
    [data-testid="stAppViewBlockContainer"] {
        padding-top: 1.5rem !important;
        padding-bottom: 2rem !important;
    }

    .hero-card {
        padding: 23px;
        border-radius: 16px;
    }

    .hero-card h1 {
        font-size: 28px;
    }

    div[data-testid="stRadio"] > div {
        gap: 5px;
        padding: 8px;
    }

    div[data-testid="stRadio"] label {
        padding: 6px 9px;
        font-size: 12px;
    }

    .feature-card {
        padding: 16px;
    }
}
</style>
""", unsafe_allow_html=True)



# =========================================================
# 3. SESSION STATE
# =========================================================

defaults = {
    "source_df": None,
    "source_name": None,
    "cleaned_poll_data": None,
    "cleaning_summary": None,
    "dataset_signature": None,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# =========================================================
# 4. HELPER FUNCTIONS
# =========================================================

def normalize_column_name(column):
    """Normalize common column-name variations."""

    name = str(column).strip()
    key = re.sub(r"[_\-]+", " ", name.lower())
    key = re.sub(r"\s+", " ", key).strip()

    aliases = {
        "timestamp": [
            "timestamp", "time stamp", "response date",
            "submitted at", "submission date"
        ],
        "age": ["age group", "age range", "age category"],
        "gender": ["sex"],
        "country": ["nation", "country name"],
        "feedback": [
            "comments", "comment", "review",
            "suggestion", "open feedback"
        ],
        "satisfaction": [
            "satisfaction rating", "rating out of 5"
        ],
    }

    # Preserve original labels such as Q1, Q2, Q7_Part_1.
    for standard, variations in aliases.items():
        if key == standard or key in variations:
            return standard.title() if standard != "age" else "Age Group"

    return name


def standardize_columns(data):
    """Normalize recognizable names without destroying unknown columns."""

    data = data.copy()
    new_columns = []
    counts = Counter()

    for column in data.columns:
        name = normalize_column_name(column)
        counts[name] += 1

        if counts[name] > 1:
            name = f"{name}_{counts[name]}"

        new_columns.append(name)

    data.columns = new_columns
    return data


def create_sample_dataset():
    return pd.DataFrame({
        "Timestamp": pd.date_range("2026-10-01", periods=20, freq="D"),
        "Age Group": [
            "18-25", "18-25", "26-35", "18-25", "36-45",
            "26-35", "18-25", "26-35", "18-25", "36-45",
            "18-25", "26-35", "36-45", "18-25", "26-35",
            "18-25", "36-45", "26-35", "18-25", "26-35"
        ],
        "Gender": [
            "Male", "Female", "Male", "Female", "Male",
            "Female", "Male", "Male", "Female", "Female",
            "Male", "Female", "Male", "Female", "Male",
            "Female", "Male", "Female", "Male", "Female"
        ],
        "Preferred Tool": [
            "Python", "Excel", "Python", "Power BI", "Tableau",
            "Excel", "Python", "Power BI", "Python", "Tableau",
            "Excel", "Python", "Power BI", "Excel", "Python",
            "Tableau", "Python", "Excel", "Power BI", "Python"
        ],
        "Satisfaction": [
            5, 4, 5, 3, 4, 4, 5, 3, 4, 5,
            2, 4, 5, 3, 4, 5, 4, 3, 5, 4
        ],
        "Feedback": [
            "Very useful", "Easy to use", "Excellent experience",
            "Needs improvement", "Good dashboard", "Helpful analysis",
            "Very useful", "More features needed", "Easy to understand",
            "Excellent tool", "Could be better", "Good experience",
            "Useful features", "Simple and effective", "Great analysis",
            "Needs improvement", "Very helpful", "Easy to use",
            "Good dashboard", "Excellent experience"
        ]
    })


def column_info(data):
    return pd.DataFrame({
        "Column": data.columns,
        "Data Type": data.dtypes.astype(str).values,
        "Missing Values": data.isna().sum().values,
        "Unique Values": [
            data[col].nunique(dropna=True) for col in data.columns
        ]
    })


def detect_column_types(data):
    """Classify columns using pandas data types and simple heuristics."""

    numeric_columns = []
    categorical_columns = []
    date_columns = []
    text_columns = []

    for col in data.columns:
        series = data[col]
        non_null = series.dropna()

        if non_null.empty:
            continue

        if pd.api.types.is_datetime64_any_dtype(series):
            date_columns.append(col)

        elif pd.api.types.is_bool_dtype(series):
            categorical_columns.append(col)

        elif pd.api.types.is_numeric_dtype(series):
            # ID-like columns are not very useful as numeric metrics.
            name = str(col).lower()
            unique_ratio = series.nunique(dropna=True) / max(len(non_null), 1)

            if (
                name == "id"
                or name.endswith("_id")
                or name in {"respondent", "respondent id"}
            ) and unique_ratio > 0.8:
                categorical_columns.append(col)
            else:
                numeric_columns.append(col)

        else:
            values = non_null.astype(str)
            name = str(col).lower()

            # Attempt date detection only when the header suggests dates.
            if any(word in name for word in ["date", "time", "timestamp"]):
                parsed = pd.to_datetime(values, errors="coerce")
                if parsed.notna().mean() >= 0.7:
                    date_columns.append(col)
                    continue

            unique_count = values.nunique()
            unique_ratio = unique_count / max(len(values), 1)

            if unique_count <= 40 or unique_ratio <= 0.05:
                categorical_columns.append(col)
            else:
                text_columns.append(col)

    return {
        "numeric": numeric_columns,
        "categorical": categorical_columns,
        "date": date_columns,
        "text": text_columns,
    }


def prepare_cleaned_data(data, remove_duplicates, trim_spaces, missing_strategy):
    cleaned = data.copy()

    if trim_spaces:
        for col in cleaned.select_dtypes(
            include=["object", "string"]
        ).columns:
            cleaned[col] = (
                cleaned[col].astype("string")
                .str.strip()
                .str.replace(r"\s+", " ", regex=True)
            )
            cleaned[col] = cleaned[col].replace("", pd.NA)

    duplicates_removed = 0

    if remove_duplicates:
        before = len(cleaned)
        cleaned = cleaned.drop_duplicates()
        duplicates_removed = before - len(cleaned)

    if missing_strategy == "Remove rows with missing values":
        cleaned = cleaned.dropna()

    elif missing_strategy == "Fill numeric with median and text with Unknown":
        for col in cleaned.columns:
            if pd.api.types.is_numeric_dtype(cleaned[col]):
                median = cleaned[col].median()
                if pd.notna(median):
                    cleaned[col] = cleaned[col].fillna(median)

            elif pd.api.types.is_datetime64_any_dtype(cleaned[col]):
                # Preserve date type; do not fill dates with text.
                continue

            else:
                cleaned[col] = cleaned[col].fillna("Unknown")

    return cleaned, duplicates_removed


def most_common(series):
    values = series.dropna()
    if values.empty:
        return None

    modes = values.mode()
    return modes.iloc[0] if not modes.empty else None


def section_header(kicker, title, description=None):
    st.caption(kicker.upper())
    st.header(title)

    if description:
        st.write(description)


def show_footer():
    st.divider()
    st.markdown(
        "<div style='text-align:center;color:#718582;font-size:12px;'>"
        "PollVision · Upload · Clean · Analyze · Visualize</div>",
        unsafe_allow_html=True,
    )


def make_chart(data, column, chart_type):
    """Create a chart based on the selected column and chart type."""

    series = data[column]

    if chart_type == "Histogram":
        values = pd.to_numeric(series, errors="coerce").dropna()
        if values.empty:
            st.info("This column has no usable numeric values.")
            return

        fig = px.histogram(
            pd.DataFrame({column: values}),
            x=column,
            title=f"Distribution of {column}",
            template="plotly_white",
        )

    elif chart_type == "Box plot":
        values = pd.to_numeric(series, errors="coerce").dropna()
        if values.empty:
            st.info("This column has no usable numeric values.")
            return

        fig = px.box(
            pd.DataFrame({column: values}),
            y=column,
            points="outliers",
            title=f"Spread of {column}",
            template="plotly_white",
        )

    elif chart_type == "Line chart":
        values = pd.to_numeric(series, errors="coerce").dropna()
        if values.empty:
            st.info("This column has no usable numeric values.")
            return

        fig = px.line(
            pd.DataFrame({column: values}).reset_index(),
            x="index",
            y=column,
            title=f"{column} by row order",
            template="plotly_white",
        )

    else:
        counts = (
            series.fillna("Missing")
            .astype(str)
            .value_counts()
            .head(30)
            .rename_axis("Value")
            .reset_index(name="Responses")
        )

        if counts.empty:
            st.info("No values available for this chart.")
            return

        if chart_type == "Pie chart":
            fig = px.pie(
                counts,
                names="Value",
                values="Responses",
                title=f"Share of {column}",
                template="plotly_white",
            )
        else:
            fig = px.bar(
                counts.sort_values("Responses", ascending=True),
                x="Responses",
                y="Value",
                orientation="h",
                title=f"Responses by {column} (top 30)",
                template="plotly_white",
            )

    fig.update_layout(margin=dict(l=10, r=10, t=60, b=10))
    st.plotly_chart(fig, use_container_width=True)


# =========================================================
# 5. BRAND HEADER AND NAVIGATION
# =========================================================

brand_col, status_col = st.columns([4, 1])

with brand_col:
    st.markdown("""
    <div style="display:flex;align-items:center;gap:12px;">
      <div style="background:#123B3A;color:#9BE8CA;width:45px;height:45px;
      border-radius:13px;display:flex;align-items:center;justify-content:center;
      font-size:24px;">📊</div>
      <div>
        <div style="font-size:24px;font-weight:800;color:#123B3A;">PollVision</div>
        <div style="font-size:12px;color:#718582;">Poll Results & Analytics</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

with status_col:
    if st.session_state.source_df is not None:
        st.success("Dataset loaded")
    else:
        st.caption("No dataset loaded")

st.write("")

sections = [
    "Home", "Upload Data", "Clean Data",
    "Dashboard", "Feedback", "Insights"
]

current_page = st.radio(
    "Main navigation",
    sections,
    horizontal=True,
    label_visibility="collapsed",
    key="main_navigation",
)


# =========================================================
# 6. HOME PAGE
# =========================================================

if current_page == "Home":
    st.markdown("""
    <div class="hero-card">
      <div style="color:#9BE8CA;font-weight:700;letter-spacing:2px;">
      POLL ANALYTICS PLATFORM</div>
      <h1>Understand your poll data.</h1>
      <p>Upload CSV files, clean data, discover patterns and create
      interactive visual reports using a flexible analytics workspace.</p>
    </div>
    """, unsafe_allow_html=True)

    section_header(
        "GET STARTED",
        "Everything in one workspace",
        "Choose a section from the navigation bar."
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("""
        <div class="feature-card">
        <h3>📂 Upload Data</h3>
        Import CSV files from Kaggle, Google Forms or other sources.
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div class="feature-card">
        <h3>🧹 Clean Data</h3>
        Remove duplicates, trim text and handle missing values.
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown("""
        <div class="feature-card">
        <h3>📈 Explore Insights</h3>
        Discover distributions, trends and common responses.
        </div>
        """, unsafe_allow_html=True)

    source_df = st.session_state.source_df

    if source_df is not None:
        st.subheader("Your workspace")
        c1, c2, c3 = st.columns(3)
        c1.metric("Original Responses", len(source_df))
        c2.metric("Total Columns", len(source_df.columns))
        c3.metric("Missing Cells", int(source_df.isna().sum().sum()))
        st.caption(f"Current dataset: {st.session_state.source_name}")
    else:
        st.info("Start by opening Upload Data.")


# =========================================================
# 7. UPLOAD DATA PAGE
# =========================================================

elif current_page == "Upload Data":
    section_header(
        "DATA WORKSPACE",
        "Upload your dataset",
        "Upload a CSV file or load the sample dataset."
    )

    choice = st.radio(
        "Choose data source",
        ["Upload CSV", "Use Sample Dataset"],
        horizontal=True,
        key="upload_source_choice",
    )

    if choice == "Upload CSV":
        uploaded_file = st.file_uploader(
            "Choose a CSV file",
            type=["csv"],
            key="poll_csv_uploader",
        )

        if uploaded_file is not None:
            try:
                raw_bytes = uploaded_file.getvalue()

                try:
                    new_df = pd.read_csv(
                        pd.io.common.BytesIO(raw_bytes),
                        low_memory=False,
                    )
                except UnicodeDecodeError:
                    new_df = pd.read_csv(
                        pd.io.common.BytesIO(raw_bytes),
                        encoding="latin-1",
                        low_memory=False,
                    )

                new_df = standardize_columns(new_df)

                if new_df.empty or len(new_df.columns) == 0:
                    st.error("The CSV file is empty or has no usable columns.")
                else:
                    signature = (
                        uploaded_file.name,
                        len(new_df),
                        tuple(new_df.columns),
                        len(raw_bytes),
                    )

                    if st.session_state.dataset_signature != signature:
                        st.session_state.source_df = new_df.copy()
                        st.session_state.source_name = uploaded_file.name
                        st.session_state.dataset_signature = signature
                        st.session_state.cleaned_poll_data = None
                        st.session_state.cleaning_summary = None

                    st.success(f"Dataset loaded: {uploaded_file.name}")

            except Exception as error:
                st.error(f"Could not read the CSV: {error}")

    else:
        if st.button("Load Sample Dataset", type="primary"):
            sample = standardize_columns(create_sample_dataset())

            st.session_state.source_df = sample.copy()
            st.session_state.source_name = "Built-in Sample Dataset"
            st.session_state.dataset_signature = (
                "sample", len(sample), tuple(sample.columns)
            )
            st.session_state.cleaned_poll_data = None
            st.session_state.cleaning_summary = None
            st.success("Sample dataset loaded successfully.")

    source_df = st.session_state.source_df

    if source_df is not None:
        st.divider()
        section_header(
            "PREVIEW",
            "Original dataset",
            f"Current source: {st.session_state.source_name}",
        )

        c1, c2, c3 = st.columns(3)
        c1.metric("Total Responses", len(source_df))
        c2.metric("Total Columns", len(source_df.columns))
        c3.metric("Missing Cells", int(source_df.isna().sum().sum()))

        st.dataframe(source_df.head(50), use_container_width=True, hide_index=True)

        with st.expander("View column information"):
            st.dataframe(column_info(source_df), use_container_width=True, hide_index=True)

        with st.expander("Automatically detected column types"):
            detected = detect_column_types(source_df)
            for kind, columns in detected.items():
                st.write(f"**{kind.title()} columns ({len(columns)}):**")
                st.write(", ".join(map(str, columns)) if columns else "None detected")

        st.download_button(
            "Download Original CSV",
            data=source_df.to_csv(index=False).encode("utf-8"),
            file_name="original_poll_data.csv",
            mime="text/csv",
        )
    else:
        st.info("Upload a CSV file or select Use Sample Dataset to begin.")


# =========================================================
# 8. CLEAN DATA PAGE
# =========================================================

elif current_page == "Clean Data":
    section_header(
        "DATA PREPARATION",
        "Clean your dataset",
        "Select cleaning operations and apply them to your original data.",
    )

    source_df = st.session_state.source_df

    if source_df is None:
        st.warning("First load a dataset from Upload Data.")
    else:
        st.caption(
            f"Source: {st.session_state.source_name} · "
            f"{len(source_df)} original rows"
        )

        remove_duplicates = st.checkbox(
            "Remove duplicate rows", value=True, key="clean_duplicates"
        )
        trim_spaces = st.checkbox(
            "Trim extra spaces in text", value=True, key="clean_spaces"
        )
        missing_strategy = st.selectbox(
            "Missing-value strategy",
            [
                "Keep as is",
                "Remove rows with missing values",
                "Fill numeric with median and text with Unknown",
            ],
            key="missing_strategy",
        )

        if st.button("Clean Data", type="primary", key="run_cleaning"):
            try:
                cleaned, duplicates_removed = prepare_cleaned_data(
                    source_df,
                    remove_duplicates,
                    trim_spaces,
                    missing_strategy,
                )

                st.session_state.cleaned_poll_data = cleaned.copy()
                st.session_state.cleaning_summary = {
                    "original_rows": len(source_df),
                    "cleaned_rows": len(cleaned),
                    "duplicates_removed": duplicates_removed,
                }
                st.success("Data cleaning completed successfully!")
            except Exception as error:
                st.error(f"Cleaning failed: {error}")

        cleaned_df = st.session_state.cleaned_poll_data
        summary = st.session_state.cleaning_summary

        if cleaned_df is not None and summary is not None:
            st.divider()
            section_header(
                "CLEANING REPORT",
                "Cleaning results",
                "Review and download the cleaned dataset.",
            )

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Original Rows", summary["original_rows"])
            c2.metric("Cleaned Rows", summary["cleaned_rows"])
            c3.metric("Duplicates Removed", summary["duplicates_removed"])
            c4.metric("Missing Cells", int(cleaned_df.isna().sum().sum()))

            st.subheader("Cleaned data preview")
            st.dataframe(cleaned_df.head(50), use_container_width=True, hide_index=True)

            st.download_button(
                "Download Cleaned CSV",
                data=cleaned_df.to_csv(index=False).encode("utf-8"),
                file_name="cleaned_poll_data.csv",
                mime="text/csv",
            )

            with st.expander("View cleaned column information"):
                st.dataframe(column_info(cleaned_df), use_container_width=True, hide_index=True)
        else:
            st.info("Choose your cleaning options and click Clean Data.")


# =========================================================
# 9. DYNAMIC DASHBOARD
# =========================================================

elif current_page == "Dashboard":
    section_header(
        "ANALYTICS",
        "Dynamic analytics dashboard",
        "Choose columns and explore data from different CSV datasets.",
    )

    data = st.session_state.cleaned_poll_data

    if data is None:
        st.warning("Clean your dataset first, or open Clean Data to begin.")
    elif data.empty:
        st.warning("The cleaned dataset contains no rows.")
    else:
        detected = detect_column_types(data)
        filtered = data.copy()

        st.subheader("Filter responses")

        filter_candidates = (
            detected["categorical"] + detected["date"]
        )
        filter_candidates = [
            c for c in filter_candidates
            if data[c].nunique(dropna=True) <= 100
        ][:5]

        if filter_candidates:
            filter_widgets = st.columns(min(3, len(filter_candidates)))

            for i, column in enumerate(filter_candidates):
                options = sorted(
                    data[column].dropna().astype(str).unique().tolist()
                )

                if len(options) > 1:
                    selected = filter_widgets[i % len(filter_widgets)].multiselect(
                        str(column),
                        options=options,
                        default=options,
                        key=f"dynamic_filter_{column}",
                    )

                    filtered = filtered[
                        filtered[column].astype(str).isin(selected)
                    ]

        st.divider()
        st.subheader("Key statistics")

        c1, c2, c3 = st.columns(3)
        c1.metric("Filtered Responses", len(filtered))
        c2.metric("Columns Analyzed", len(data.columns))
        c3.metric(
            "Missing Cells",
            f"{int(filtered.isna().sum().sum()):,}"
        )

        if filtered.empty:
            st.info("No responses match the selected filters.")
        else:
            numeric_cols = detected["numeric"]
            categorical_cols = detected["categorical"]

            if numeric_cols:
                st.subheader("Numeric summary")

                numeric_summary = filtered[numeric_cols].describe().T
                st.dataframe(numeric_summary, use_container_width=True)

                metric_col = st.selectbox(
                    "Select a numeric metric",
                    numeric_cols,
                    key="numeric_metric",
                )

                values = pd.to_numeric(
                    filtered[metric_col], errors="coerce"
                ).dropna()

                a, b, c = st.columns(3)
                a.metric("Average", f"{values.mean():,.2f}" if not values.empty else "N/A")
                b.metric("Median", f"{values.median():,.2f}" if not values.empty else "N/A")
                c.metric("Unique Values", int(values.nunique()))

            st.divider()
            st.subheader("Interactive visualizations")

            available_cols = list(filtered.columns)

            chart_col = st.selectbox(
                "Choose a column to visualize",
                available_cols,
                key="dynamic_chart_column",
            )

            is_numeric = (
                chart_col in detected["numeric"]
                or pd.api.types.is_numeric_dtype(filtered[chart_col])
            )

            chart_options = (
                ["Histogram", "Box plot", "Line chart", "Bar chart"]
                if is_numeric
                else ["Bar chart", "Pie chart"]
            )

            chart_type = st.selectbox(
                "Chart type",
                chart_options,
                key="dynamic_chart_type",
            )

            make_chart(filtered, chart_col, chart_type)

            if categorical_cols:
                st.subheader("Categorical summaries")

                category_col = st.selectbox(
                    "Choose a category",
                    categorical_cols,
                    key="category_summary_column",
                )

                counts = (
                    filtered[category_col]
                    .fillna("Missing")
                    .astype(str)
                    .value_counts()
                    .head(30)
                    .rename_axis("Category")
                    .reset_index(name="Responses")
                )

                st.dataframe(counts, use_container_width=True, hide_index=True)

                fig = px.bar(
                    counts.sort_values("Responses", ascending=True),
                    x="Responses",
                    y="Category",
                    orientation="h",
                    title=f"Responses by {category_col}",
                    template="plotly_white",
                )
                st.plotly_chart(fig, use_container_width=True)

            if detected["date"]:
                date_col = st.selectbox(
                    "Choose a date column",
                    detected["date"],
                    key="trend_date_column",
                )

                dates = pd.to_datetime(filtered[date_col], errors="coerce").dropna()

                if not dates.empty:
                    trend = dates.dt.date.value_counts().sort_index()
                    trend_df = trend.rename_axis("Date").reset_index(name="Responses")

                    fig = px.line(
                        trend_df,
                        x="Date",
                        y="Responses",
                        markers=True,
                        title=f"Response trend by {date_col}",
                        template="plotly_white",
                    )
                    st.plotly_chart(fig, use_container_width=True)


# =========================================================
# 10. FEEDBACK EXPLORER
# =========================================================

elif current_page == "Feedback":
    section_header(
        "TEXT ANALYTICS",
        "Feedback explorer",
        "Select a text column to explore commonly used words.",
    )

    data = st.session_state.cleaned_poll_data

    if data is None:
        st.warning("Clean your dataset first.")
    else:
        detected = detect_column_types(data)
        candidates = detected["text"]

        if "Feedback" in data.columns and "Feedback" not in candidates:
            candidates = ["Feedback"] + candidates

        if not candidates:
            st.info(
                "No suitable text column was detected. "
                "This dataset may contain only numeric or categorical values."
            )
        else:
            text_col = st.selectbox(
                "Choose a text column",
                candidates,
                key="feedback_column",
            )

            text_values = (
                data[text_col]
                .dropna()
                .astype(str)
                .str.strip()
            )
            text_values = text_values[text_values != ""]

            c1, c2 = st.columns(2)
            c1.metric("Text Entries", len(text_values))
            c2.metric(
                "Average Length",
                f"{text_values.str.len().mean():.1f} characters"
                if not text_values.empty else "N/A",
            )

            if not text_values.empty:
                st.subheader("Word Cloud")

                combined_text = " ".join(text_values.tolist())
                stopwords = set(STOPWORDS)

                try:
                    cloud = WordCloud(
                        width=1200,
                        height=500,
                        background_color="white",
                        colormap="viridis",
                        stopwords=stopwords,
                        collocations=False,
                    ).generate(combined_text)

                    fig, ax = plt.subplots(figsize=(13, 5))
                    ax.imshow(cloud, interpolation="bilinear")
                    ax.axis("off")
                    st.pyplot(fig)
                    plt.close(fig)

                except ValueError:
                    st.info("There are not enough usable words for a word cloud.")

                lengths = pd.DataFrame({
                    "Text Length": text_values.str.len()
                })

                fig = px.histogram(
                    lengths,
                    x="Text Length",
                    nbins=20,
                    title="Text Length Distribution",
                    template="plotly_white",
                )
                st.plotly_chart(fig, use_container_width=True)

                with st.expander("View text entries"):
                    st.dataframe(
                        text_values.rename(text_col).reset_index(drop=True),
                        use_container_width=True,
                        hide_index=True,
                    )


# =========================================================
# 11. INSIGHTS AND DATA QUALITY
# =========================================================

elif current_page == "Insights":
    section_header(
        "FINDINGS & QUALITY",
        "Insights and data quality",
        "Review dataset quality and automatically calculated findings.",
    )

    data = st.session_state.cleaned_poll_data

    if data is None:
        st.warning("Clean your dataset first.")
    elif data.empty:
        st.warning("No rows are available for analysis.")
    else:
        detected = detect_column_types(data)

        st.subheader("Data quality checks")

        missing = int(data.isna().sum().sum())
        duplicate_count = int(data.duplicated().sum())

        c1, c2, c3 = st.columns(3)
        c1.metric("Missing Cells", missing)
        c2.metric("Duplicate Rows Remaining", duplicate_count)
        c3.metric("Columns", len(data.columns))

        if missing:
            st.warning(f"{missing:,} missing cells remain.")
        else:
            st.success("No missing cells remain.")

        if duplicate_count:
            st.warning(f"{duplicate_count:,} duplicate rows remain.")
        else:
            st.success("No duplicate rows detected.")

        st.subheader("Missing values by column")

        missing_by_col = data.isna().sum()
        missing_by_col = missing_by_col[missing_by_col > 0].sort_values(ascending=False)

        if not missing_by_col.empty:
            missing_df = missing_by_col.rename_axis("Column").reset_index(name="Missing Cells")
            st.dataframe(missing_df, use_container_width=True, hide_index=True)

            fig = px.bar(
                missing_df.head(30),
                x="Missing Cells",
                y="Column",
                orientation="h",
                title="Columns with the Most Missing Values",
                template="plotly_white",
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("There are no missing values to display.")

        st.divider()
        st.subheader("Automatic insights")

        st.write(f"**Responses analyzed:** {len(data):,}")
        st.write(f"**Numeric columns detected:** {len(detected['numeric'])}")
        st.write(f"**Categorical columns detected:** {len(detected['categorical'])}")
        st.write(f"**Date columns detected:** {len(detected['date'])}")
        st.write(f"**Text columns detected:** {len(detected['text'])}")

        for col in detected["numeric"][:5]:
            values = pd.to_numeric(data[col], errors="coerce").dropna()

            if not values.empty:
                st.write(
                    f"**{col}:** mean = {values.mean():,.2f}, "
                    f"median = {values.median():,.2f}"
                )

        for col in detected["categorical"][:5]:
            value = most_common(data[col])

            if value is not None:
                count = int(data[col].eq(value).sum())
                share = count / max(int(data[col].notna().sum()), 1) * 100

                st.write(
                    f"**Most common {col}:** {value} "
                    f"({count:,} responses, {share:.1f}% of non-missing values)"
                )

        st.divider()
        st.subheader("Download analysis data")

        st.download_button(
            "Download Cleaned Dataset",
            data=data.to_csv(index=False).encode("utf-8"),
            file_name="cleaned_poll_data.csv",
            mime="text/csv",
            key="download_insights_csv",
        )


# =========================================================
# 12. FOOTER
# =========================================================

show_footer()
