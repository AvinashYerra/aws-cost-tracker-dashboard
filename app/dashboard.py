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
    page_title="AWS Cost Tracker",
    page_icon="☁️",
    layout="wide"
)

st.title("☁️ AWS Cost Tracker")
st.caption("Monitoring simulated AWS infrastructure costs using TimescaleDB")

# Data Loaders
@st.cache_data(ttl=60)
def load_metrics():

    query = """
    SELECT *
    FROM cloud_metrics
    ORDER BY ts DESC
    """

    with engine.connect() as conn:
        return pd.read_sql(text(query), conn)


@st.cache_data(ttl=60)
def load_cost_trend():

    query = """
    SELECT
        time_bucket('1 minute', ts) AS bucket,
        SUM(estimated_cost) AS total_cost
    FROM cloud_metrics
    GROUP BY bucket
    ORDER BY bucket
    """

    with engine.connect() as conn:
        return pd.read_sql(text(query), conn)


# Load Data
df = load_metrics()
trend_df = load_cost_trend()

if df.empty:
    st.warning("No data found in cloud_metrics table.")
    st.stop()

# KPIs
total_cost = round(df["estimated_cost"].sum(), 2)

total_records = len(df)

service_cost = (
    df.groupby("service_name")["estimated_cost"]
      .sum()
      .reset_index()
)

top_service = service_cost.sort_values(
    by="estimated_cost",
    ascending=False
).iloc[0]

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Cost",
        f"${total_cost:,.2f}"
    )

with col2:
    st.metric(
        "Total Records",
        f"{total_records:,}"
    )

with col3:
    st.metric(
        "Top Service",
        top_service["service_name"]
    )

with col4:
    st.metric(
        "Top Service Cost",
        f"${top_service['estimated_cost']:,.2f}"
    )


st.divider()


# Cost By Service
col1, col2 = st.columns(2)

with col1:

    fig = px.bar(
        service_cost,
        x="service_name",
        y="estimated_cost",
        title="Cost by Service"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# Environment Distribution
with col2:

    env_cost = (
        df.groupby("environment")["estimated_cost"]
          .sum()
          .reset_index()
    )

    fig = px.pie(
        env_cost,
        names="environment",
        values="estimated_cost",
        title="Environment Cost Distribution"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# Cost Trend
st.subheader("Cost Trend")

fig = px.line(
    trend_df,
    x="bucket",
    y="total_cost",
    markers=True,
    title="Infrastructure Cost Trend"
)

st.plotly_chart(
    fig,
    use_container_width=True
)



# Raw Data
with st.expander("View Raw Metrics"):

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )