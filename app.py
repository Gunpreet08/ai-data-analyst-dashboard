import streamlit as st
import pandas as pd

from utils.clean_data import remove_duplicates, fill_missing_values
from utils.generate_insights import generate_basic_insights, generate_correlation_insight
from utils.ai_summary import generate_ai_summary
from utils.load_data import load_csv
from utils.ai_prep_assistant import generate_prep_plan
from utils.prep_validator import validate_prep_plan
from utils.prep_executor import execute_prep_plan
from utils.analyze_data import (
    get_shape,
    get_columns,
    get_dtypes,
    get_missing_values,
    get_numeric_summary,
    get_numeric_columns,
)
from utils.visualize_data import plot_histogram, plot_scatter
from utils.ai_dashboard_generator import generate_dashboard_plan
from utils.dashboard_renderer import render_chart
from utils.kpi_renderer import render_kpi_value
from utils.pdf_report_generator import generate_pdf_report
from io import BytesIO
import matplotlib.pyplot as plt
st.set_page_config(page_title="AI Data Analyst Dashboard", layout="wide")


# ---------------- SESSION STATE ----------------

if "prep_plan" not in st.session_state:
    st.session_state.prep_plan = None

if "prep_plan_error" not in st.session_state:
    st.session_state.prep_plan_error = None

if "valid_prep_actions" not in st.session_state:
    st.session_state.valid_prep_actions = []

if "invalid_prep_actions" not in st.session_state:
    st.session_state.invalid_prep_actions = []

if "prepared_df" not in st.session_state:
    st.session_state.prepared_df = None

if "prep_execution_log" not in st.session_state:
    st.session_state.prep_execution_log = []

if "ai_summary" not in st.session_state:
    st.session_state.ai_summary = None

if "ai_summary_error" not in st.session_state:
    st.session_state.ai_summary_error = None

if "dashboard_plan" not in st.session_state:
    st.session_state.dashboard_plan = None

if "dashboard_plan_error" not in st.session_state:
    st.session_state.dashboard_plan_error = None

if "last_uploaded_file" not in st.session_state:
    st.session_state.last_uploaded_file = None
def kpi_card(label, value):
    if isinstance(value, (int, float)):
        if float(value).is_integer():
            display_value = f"{int(value):,}"
        else:
            display_value = f"{value:,.2f}"
    else:
        display_value = value
    st.markdown(
        f"""
        <div style="
            padding: 18px;
            border-radius: 12px;
            background-color: #1f2937;
            border: 1px solid #374151;
            margin-bottom: 10px;
        ">
            <div style="font-size:14px; color:#cbd5e1;">{label}</div>
            <div style="font-size:32px; font-weight:700; color:white;">{value}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

def fig_to_image_buffer(fig):
    buffer = BytesIO()
    fig.savefig(buffer, format="png", bbox_inches="tight")
    buffer.seek(0)
    return buffer

def kpi_to_image(title, value):
    fig, ax = plt.subplots(figsize=(4, 2))

    ax.text(0.5, 0.6, str(value), fontsize=20, ha='center')
    ax.text(0.5, 0.3, title, fontsize=10, ha='center')

    ax.axis('off')

    buffer = BytesIO()
    fig.savefig(buffer, format="png", bbox_inches="tight")
    buffer.seek(0)

    plt.close(fig)

    return buffer

# ---------------- TITLE ----------------

st.title("AI-Powered Data Analyst Dashboard")
st.markdown("<br>", unsafe_allow_html=True)
st.caption("Analyze your data with AI-powered insights, dashboards, and reports.")

uploaded_file = st.file_uploader("Upload your dataset (CSV format)", type=["csv"])
st.markdown("<br>", unsafe_allow_html=True)
# st.divider()
# # st.markdown("<br>", unsafe_allow_html=True)
# st.markdown("### What you'll get")
# st.markdown("<br>", unsafe_allow_html=True)

# col1, col2, col3, col4 = st.columns(4)

# st.markdown("<br>", unsafe_allow_html=True)

# with col1:
#     st.markdown("📊 **Smart KPIs**")
#     st.caption("Automatically calculated insights like averages, totals, trends")

# with col2:
#     st.markdown("📈 **Auto Charts**")
#     st.caption("Relevant visualizations generated based on your data")

# with col3:
#     st.markdown("🧠 **AI Insights**")
#     st.caption("Get smart summary of your data")

# with col4:
#     st.markdown("📄 **Downloadable Report**")
#     st.caption("Export your dashboard as a professional PDF")

# ---------------- MAIN APP ----------------

if uploaded_file is not None:
    current_file_id = (uploaded_file.name, uploaded_file.size)

    if st.session_state.last_uploaded_file != current_file_id:
        st.session_state.prep_plan = None
        st.session_state.prep_plan_error = None
        st.session_state.valid_prep_actions = []
        st.session_state.invalid_prep_actions = []
        st.session_state.prepared_df = None
        st.session_state.prep_execution_log = []
        st.session_state.ai_summary = None
        st.session_state.ai_summary_error = None
        st.session_state.dashboard_plan = None
        st.session_state.dashboard_plan_error = None
        st.session_state.last_uploaded_file = current_file_id

    raw_df, error = load_csv(uploaded_file)
    

    if error:
        st.error(f"Error loading file: {error}")
    else:
        # Automatic cleaning
        cleaned_df, duplicates_removed = remove_duplicates(raw_df)
        cleaned_df = fill_missing_values(cleaned_df)

        # Use prepared data if user applied AI preparation
        if st.session_state.prepared_df is not None:
            analysis_df = st.session_state.prepared_df
        else:
            analysis_df = cleaned_df

        rows, cols = get_shape(analysis_df)
        numeric_cols = get_numeric_columns(analysis_df)
        insights = generate_basic_insights(analysis_df)
        correlation_insight = None

        tab1, tab2, tab3, tab4 = st.tabs(
            ["📂 Overview", "🛠️ Preparation", "📊 Analysis", "🤖 AI Features"]
        )

        # ---------------- TAB 1: OVERVIEW ----------------

        with tab1:
            st.header("📂 Dataset Overview")

            kpi1, kpi2, kpi3, kpi4 = st.columns(4)

            total_rows = analysis_df.shape[0]
            total_cols = analysis_df.shape[1]
            numeric_cols_count = len(analysis_df.select_dtypes(include="number").columns)
            missing_values = int(analysis_df.isnull().sum().sum())

            with kpi1:
                st.metric("Rows", total_rows)

            with kpi2:
                st.metric("Columns", total_cols)

            with kpi3:
                st.metric("Numeric Columns", numeric_cols_count)

            with kpi4:
                st.metric("Missing Values", missing_values)

            with st.expander("Raw Dataset Preview (Before Cleaning)"):
                st.dataframe(raw_df.head(10))

            st.subheader("Current Dataset Preview")

            if st.session_state.prepared_df is not None:
                st.caption("Showing prepared dataset after AI data preparation.")
            else:
                st.caption("Showing automatically cleaned dataset.")

            st.dataframe(analysis_df.head(10))

            # st.subheader("Dataset Shape")
            # st.write(f"Rows: {rows}, Columns: {cols}")

        # ---------------- TAB 2: PREPARATION ----------------

        with tab2:
            st.header("🛠️ Data Preparation")

            st.subheader("Automatic Data Cleaning")
            st.write(f"Duplicates removed: {duplicates_removed}")
            st.write("Missing values handled automatically: numeric → mean, categorical → mode")

            with st.expander("Cleaned Dataset Preview"):
                st.dataframe(cleaned_df.head(10))

            st.subheader("AI Data Preparation Assistant")

            user_prep_request = st.text_area(
                "Describe how you want to prepare the data",
                placeholder="Example: Drop Salary column, convert Age to float, and keep only rows where Experience > 2",
            )

            if st.button("Generate Preparation Plan"):
                if user_prep_request.strip():
                    st.session_state.prepared_df = None
                    st.session_state.prep_execution_log = []
                    st.session_state.valid_prep_actions = []
                    st.session_state.invalid_prep_actions = []

                    st.session_state.ai_summary = None
                    st.session_state.ai_summary_error = None
                    st.session_state.dashboard_plan = None
                    st.session_state.dashboard_plan_error = None

                    with st.spinner("Generating preparation plan..."):
                        prep_plan, prep_error = generate_prep_plan(cleaned_df, user_prep_request)

                    st.session_state.prep_plan = prep_plan
                    st.session_state.prep_plan_error = prep_error

                    if prep_plan:
                        valid_actions, invalid_actions = validate_prep_plan(prep_plan, cleaned_df)
                        st.session_state.valid_prep_actions = valid_actions
                        st.session_state.invalid_prep_actions = invalid_actions

                        if valid_actions:
                            unsupported_hints = [
                                "merge",
                                "create",
                                "category",
                                "combine",
                                "new column",
                                "bucket",
                                "transform",
                            ]

                            if any(word in user_prep_request.lower() for word in unsupported_hints):
                                st.info(
                                    "Only the supported part of your request was converted into executable actions."
                                )
                else:
                    st.warning("Please describe the data preparation request first.")

            if st.session_state.prep_plan_error:
                st.warning(
                    f"Preparation plan could not be generated: {st.session_state.prep_plan_error}"
                )

            if st.session_state.valid_prep_actions:
                st.subheader("Valid Actions")
                for action in st.session_state.valid_prep_actions:
                    st.json(action)

            if st.session_state.invalid_prep_actions:
                st.subheader("Invalid / Unsupported Actions")
                for item in st.session_state.invalid_prep_actions:
                    st.write(f"Reason: {item['reason']}")
                    st.json(item["action"])

            if st.session_state.valid_prep_actions and st.session_state.prepared_df is None:
                if st.button("Apply Preparation Plan"):
                    prepared_df, execution_log = execute_prep_plan(
                        cleaned_df, st.session_state.valid_prep_actions
                    )
                    st.session_state.prepared_df = prepared_df
                    st.session_state.prep_execution_log = execution_log

                    st.session_state.ai_summary = None
                    st.session_state.ai_summary_error = None
                    st.session_state.dashboard_plan = None
                    st.session_state.dashboard_plan_error = None

                    st.rerun()

            if st.session_state.prepared_df is not None:
                st.subheader("Prepared Dataset Preview")
                st.dataframe(analysis_df.head(10))

                if st.session_state.prep_execution_log:
                    st.subheader("Preparation Execution Log")
                    for log_item in st.session_state.prep_execution_log:
                        st.markdown(f"- {log_item}")

        # ---------------- TAB 3: ANALYSIS ----------------

        with tab3:
            st.header("📊 Data Analysis")

            with st.expander("Column Names"):
                columns_df = pd.DataFrame({"Column Names": get_columns(analysis_df)})
                st.dataframe(columns_df)

            with st.expander("Data Types"):
                dtype_df = get_dtypes(analysis_df).astype(str).reset_index()
                dtype_df.columns = ["Column", "Data Type"]
                st.dataframe(dtype_df)

            with st.expander("Missing Values"):
                missing_df = get_missing_values(analysis_df).reset_index()
                missing_df.columns = ["Column", "Missing Values"]
                st.dataframe(missing_df)

            with st.expander("Summary Statistics"):
                summary = get_numeric_summary(analysis_df)
                if summary is not None:
                    st.write(summary)
                else:
                    st.warning("No numeric columns found for summary statistics.")

            st.subheader("Generated Insights")
            for insight in insights:
                st.markdown(f"- {insight}")

            st.header("📈 Visual Analysis")

            if numeric_cols:
                chart_col1, chart_col2 = st.columns(2)

                with chart_col1:
                    st.subheader("Histogram")
                    selected_col = st.selectbox("Select column", numeric_cols, key="hist_col")
                    hist_fig = plot_histogram(analysis_df, selected_col)
                    st.pyplot(hist_fig, width="content")

                with chart_col2:
                    if len(numeric_cols) >= 2:
                        st.subheader("Scatter Plot")

                        row1, row2 = st.columns(2)

                        with row1:
                            x_col = st.selectbox("X-axis", numeric_cols, key="x_axis")

                        y_options = [col for col in numeric_cols if col != x_col]

                        if len(y_options) == 0:
                            st.warning("Need at least 2 different numeric columns for scatter plot.")
                        else:
                            with row2:
                                y_col = st.selectbox("Y-axis", y_options, key="y_axis")

                            scatter_fig = plot_scatter(analysis_df, x_col, y_col)
                            st.pyplot(scatter_fig, width="content")

                            correlation_insight = generate_correlation_insight(
                                analysis_df, x_col, y_col
                            )
                    else:
                        st.info("Need at least 2 numeric columns for scatter plot.")

                if correlation_insight:
                    st.subheader("Correlation Insight")
                    st.info(correlation_insight)
            else:
                st.warning("No numeric columns available for visualization.")

        # ---------------- TAB 4: AI FEATURES ----------------

        with tab4:
            st.header("🤖 AI Features")

            st.subheader("AI Summary")

            if st.button("Generate AI Summary"):
                with st.spinner("Generating AI summary..."):
                    ai_summary, ai_error = generate_ai_summary(
                        analysis_df, insights, correlation_insight
                    )
                    st.session_state.ai_summary = ai_summary
                    st.session_state.ai_summary_error = ai_error

            if st.session_state.ai_summary_error:
                st.warning(
                    f"AI summary could not be generated: {st.session_state.ai_summary_error}"
                )
                st.info("Make sure Ollama is installed, running, and the llama3.2 model is available.")
            elif st.session_state.ai_summary:
                st.success("AI-generated summary ready")
                st.write(st.session_state.ai_summary)

            st.subheader("AI Dashboard Generator")

            if st.button("Generate AI Dashboard Plan"):
                with st.spinner("Generating dashboard recommendations..."):
                    dashboard_plan, dashboard_error = generate_dashboard_plan(analysis_df)
                    st.session_state.dashboard_plan = dashboard_plan
                    st.session_state.dashboard_plan_error = dashboard_error

            if st.session_state.dashboard_plan_error:
                st.warning(
                    f"Dashboard plan could not be generated: {st.session_state.dashboard_plan_error}"
                )

            elif st.session_state.dashboard_plan:
                st.success("AI dashboard plan generated successfully")

                dashboard_plan = st.session_state.dashboard_plan
                filtered_dashboard_df = analysis_df.copy()

                st.subheader("Dashboard Filters")

                numeric_filter_cols = filtered_dashboard_df.select_dtypes(
                    include="number"
                ).columns.tolist()

                if numeric_filter_cols:
                    filter_cols = st.multiselect(
                        "Select numeric columns to filter",
                        numeric_filter_cols,
                        default=[]
                    )

                    for col in filter_cols:
                        min_val = float(filtered_dashboard_df[col].min())
                        max_val = float(filtered_dashboard_df[col].max())

                        selected_range = st.slider(
                            f"{col} range",
                            min_value=min_val,
                            max_value=max_val,
                            value=(min_val, max_val),
                            key=f"filter_{col}"
                        )

                        filtered_dashboard_df = filtered_dashboard_df[
                            (filtered_dashboard_df[col] >= selected_range[0]) &
                            (filtered_dashboard_df[col] <= selected_range[1])
                        ]

                    if filter_cols:
                        st.caption(
                            f"Showing {len(filtered_dashboard_df)} out of {len(analysis_df)} rows after filtering."
                    )
                    else:
                        st.caption("No filters applied. Showing all rows.")
                else:
                    st.info("No numeric columns available for filtering.")

                if filtered_dashboard_df.empty:
                    st.warning("No data available after applying filters.")
                else:
                    st.markdown(
                        f"### {dashboard_plan.get('dashboard_title', 'Recommended Dashboard')}"
                    )

                    st.markdown("#### Key Metrics")

                    kpis = dashboard_plan.get("kpis", [])

                    if kpis:
                        kpi_cols = st.columns(min(len(kpis), 4))

                        for i, kpi in enumerate(kpis[:4]):
                            with kpi_cols[i]:
                                value = render_kpi_value(filtered_dashboard_df, kpi)
                                # st.metric(label=kpi, value=value)
                                kpi_card(kpi, value)
                                # kpi_img = kpi_to_image(kpi, value)

                                # st.download_button(
                                #     label="⬇️",
                                #     data=kpi_img,
                                #     file_name=f"{kpi}.png",
                                #     mime="image/png",
                                #     key=f"kpi_download_{i}"
                                # )
                    else:
                        st.info("No KPIs recommended.")

                    # st.markdown("#### Recommended Sections")
                    # for section in dashboard_plan.get("sections", []):
                    #     st.markdown(f"**{section.get('section_title', 'Section')}**")
                    #     st.write(section.get("purpose", ""))

                    st.markdown("#### Visual Insights")

                    charts = dashboard_plan.get("charts", [])
                    chart_images = []
                    if len(filtered_dashboard_df) < 3:
                        st.warning("Too few data points after filtering to generate meaningful charts.")
                    else:
                        # chart_images = []
                        valid_charts = []

                        for chart in charts:
                            chart_type = chart.get("chart_type")
                            x = chart.get("x")

                            if chart_type == "bar" and x in filtered_dashboard_df.columns:
                                if filtered_dashboard_df[x].nunique() > len(filtered_dashboard_df) * 0.6:
                                    continue

                            valid_charts.append(chart)
                        if valid_charts:
                            chart_cols = st.columns(2)
                            
                            for i, chart in enumerate(charts):
                                with chart_cols[i % 2]:
                                    chart_type = chart.get("chart_type")
                                    x = chart.get("x")

                                    if chart_type == "bar" and x in filtered_dashboard_df.columns:
                                        unique_count = filtered_dashboard_df[x].nunique()

                                        if unique_count > 10 or unique_count > len(filtered_dashboard_df) * 0.4:
                                            continue
                                    st.markdown(
                                        f"**{chart.get('title', 'Chart')}** ({chart.get('chart_type', 'unknown')})"
                                    )

                                    fig = render_chart(filtered_dashboard_df, chart)

                                    if fig:
                                        st.pyplot(fig, width="content")
                                        chart_title = chart.get("title", "Chart")
                                        img_buffer = fig_to_image_buffer(fig)
                                        chart_images.append((chart_title, img_buffer))
                                    else:
                                        st.warning("Could not render this chart")

                                    st.caption(f"X: {chart.get('x')} | Y: {chart.get('y')}")
                                    st.caption(chart.get("reason", ""))
                        else:
                            st.info("No meaningful charts available for this dataset.")
                    st.subheader("Export Report")

                    pdf_buffer = generate_pdf_report(
                        df=filtered_dashboard_df,
                        duplicates_removed=duplicates_removed,
                        insights=insights,
                        ai_summary=st.session_state.ai_summary,
                        dashboard_plan=st.session_state.dashboard_plan,
                        prep_execution_log=st.session_state.prep_execution_log,
                        chart_images=chart_images
                    )

                    st.download_button(
                        label="Download PDF Report",
                        data=pdf_buffer,
                        file_name="ai_data_analyst_report.pdf",
                        mime="application/pdf"
                    )

else:
    st.divider()

    st.markdown("### What you'll get")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("📊 **Smart KPIs**")
        st.caption("Automatically calculated insights like averages, totals, trends")

    with col2:
        st.markdown("📈 **Auto Charts**")
        st.caption("Relevant visualizations generated based on your data")

    with col3:
        st.markdown("🧠 **AI Insights**")
        st.caption("Get smart summary of your data")

    with col4:
        st.markdown("📄 **Downloadable Report**")
        st.caption("Export your dashboard as a professional PDF")
