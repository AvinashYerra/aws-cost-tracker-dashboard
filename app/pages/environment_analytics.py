import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

import pandas as pd
import streamlit as st
import plotly.express as px
from sqlalchemy import text

from db.connection import engine


st.set_page_config(
    page_title="Environment Analytics",
    page_icon="📊",
    layout="wide"
)

st.title("Environment Analytics")
st.caption("Analyze infrastructure usage, utilization and cost by environment")


@st.cache_data(ttl=60)
def load_data():

    query = """
    SELECT *
    FROM cloud_metrics
    ORDER BY ts
    """

    with engine.connect() as conn:
        return pd.read_sql(
            text(query),
            conn
        )


df = load_data()

if df.empty:
    st.warning("No data available.")
    st.stop()


# Environment Selector
selected_env = st.selectbox(
    "Select Environment",
    ["DEV", "QA", "PROD"]
)

env_df = df[
    df["environment"] == selected_env
].copy()

if env_df.empty:
    st.warning("No data found for selected environment.")
    st.stop()



# KPI SECTION
total_cost = round(
    env_df["estimated_cost"].sum(),
    2
)

total_records = len(env_df)

service_cost = (
    env_df.groupby("service_name")
    ["estimated_cost"]
    .sum()
    .reset_index()
)

top_service = (
    service_cost
    .sort_values(
        "estimated_cost",
        ascending=False
    )
    .iloc[0]["service_name"]
)

avg_metric = round(
    env_df["metric_value"].mean(),
    2
)

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Total Cost",
    f"${total_cost:,.2f}"
)

c2.metric(
    "Records",
    f"{total_records:,}"
)

c3.metric(
    "Top Service",
    top_service
)

c4.metric(
    "Avg Metric",
    avg_metric
)

st.divider()

# COST TREND
st.subheader("Cost Trend")

cost_trend = (
    env_df.groupby("ts")
    ["estimated_cost"]
    .sum()
    .reset_index()
)

fig = px.line(
    cost_trend,
    x="ts",
    y="estimated_cost",
    markers=True,
    title=f"{selected_env} Cost Trend"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# SERVICE COST & USAGE
col1, col2 = st.columns(2)

with col1:

    service_cost = (
        env_df.groupby("service_name")
        ["estimated_cost"]
        .sum()
        .reset_index()
    )

    fig = px.bar(
        service_cost,
        x="service_name",
        y="estimated_cost",
        title="Service Cost Breakdown"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

with col2:

    usage_distribution = (
        env_df.groupby("service_name")
        ["metric_value"]
        .mean()
        .reset_index()
    )

    fig = px.pie(
        usage_distribution,
        names="service_name",
        values="metric_value",
        title="Usage Distribution"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

st.divider()


# CPU / MEMORY TRENDS
st.subheader("Resource Utilization")

left, right = st.columns(2)

with left:

    cpu_df = env_df[
        env_df["metric_name"] == "CPU_UTILIZATION"
    ]

    if not cpu_df.empty:

        fig = px.line(
            cpu_df,
            x="ts",
            y="metric_value",
            title="CPU Utilization Trend"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

with right:

    memory_df = env_df[
        env_df["metric_name"] == "MEMORY_UTILIZATION"
    ]

    if not memory_df.empty:

        fig = px.line(
            memory_df,
            x="ts",
            y="metric_value",
            title="Memory Utilization Trend"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

st.divider()

# HEALTH SCORE
st.subheader("Infrastructure Health")

cpu_avg = (
    cpu_df["metric_value"].mean()
    if not cpu_df.empty
    else 0
)

memory_avg = (
    memory_df["metric_value"].mean()
    if not memory_df.empty
    else 0
)

health_score = max(
    0,
    min(
        100,
        int(
            100 -
            (
                cpu_avg * 0.30 +
                memory_avg * 0.20
            )
        )
    )
)

col1, col2 = st.columns([1, 4])

with col1:
    st.metric(
        "Health Score",
        f"{health_score}%"
    )

with col2:
    st.progress(
        health_score / 100
    )

st.divider()

# SERVICE HEATMAP
st.subheader("Service Activity Heatmap")

heatmap_df = env_df.copy()

heatmap_df["hour"] = pd.to_datetime(
    heatmap_df["ts"]
).dt.hour

pivot_df = (
    heatmap_df.pivot_table(
        index="service_name",
        columns="hour",
        values="metric_value",
        aggfunc="mean"
    )
    .fillna(0)
)

fig = px.imshow(
    pivot_df,
    aspect="auto",
    title="Average Activity by Hour"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.divider()

# SERVICE SUMMARY
st.subheader("Service Utilization Summary")

summary_df = (
    env_df.groupby("service_name")
    .agg(
        avg_metric=("metric_value", "mean"),
        max_metric=("metric_value", "max"),
        avg_cost=("estimated_cost", "mean"),
        total_cost=("estimated_cost", "sum")
    )
    .reset_index()
)

summary_df = summary_df.round(2)

st.dataframe(
    summary_df,
    use_container_width=True,
    hide_index=True
)

st.divider()

# RECENT ACTIVITY
with st.expander("Recent Metrics"):

    recent_df = (
        env_df.sort_values(
            "ts",
            ascending=False
        )
        .head(50)
    )

    st.dataframe(
        recent_df,
        use_container_width=True,
        hide_index=True
    )