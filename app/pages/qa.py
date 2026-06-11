import streamlit as st
import plotly.express as px

from app.utils import (
    get_environment_data,
    get_cost_trend
)

st.set_page_config(layout="wide")

st.title("QA Environment")

df = get_environment_data("QA")

trend_df = get_cost_trend("QA")

qa_cost = round(
    df["estimated_cost"].sum(),
    2
)

avg_invocations = round(
    df[df.metric_name=="INVOCATIONS"]
    ["metric_value"]
    .mean(),
    0
)

avg_connections = round(
    df[df.metric_name=="ACTIVE_CONNECTIONS"]
    ["metric_value"]
    .mean(),
    0
)

c1,c2,c3 = st.columns(3)

c1.metric("QA Cost", f"${qa_cost}")
c2.metric("Avg Lambda Invocations", avg_invocations)
c3.metric("Avg DB Connections", avg_connections)

fig = px.line(
    trend_df,
    x="bucket",
    y="total_cost",
    title="QA Cost Trend"
)

st.plotly_chart(fig, use_container_width=True)

service_cost = (
    df.groupby("service_name")
      ["estimated_cost"]
      .sum()
      .reset_index()
)

fig = px.pie(
    service_cost,
    names="service_name",
    values="estimated_cost",
    title="QA Workload Distribution"
)

st.plotly_chart(fig, use_container_width=True)

st.info(
    "QA workloads simulate integration, regression, and performance testing activity."
)