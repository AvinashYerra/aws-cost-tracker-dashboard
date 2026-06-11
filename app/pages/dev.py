import streamlit as st
import plotly.express as px

from app.utils import (
    get_environment_data,
    get_cost_trend
)

st.set_page_config(layout="wide")

st.title("Development Environment")

df = get_environment_data("DEV")

trend_df = get_cost_trend("DEV")

avg_cpu = round(
    df[df.metric_name=="CPU_UTILIZATION"]
    ["metric_value"]
    .mean(),
    2
)

avg_memory = round(
    df[df.metric_name=="MEMORY_UTILIZATION"]
    ["metric_value"]
    .mean(),
    2
)

cost = round(
    df["estimated_cost"].sum(),
    2
)

c1,c2,c3 = st.columns(3)

c1.metric("DEV Cost", f"${cost}")
c2.metric("Avg CPU", f"{avg_cpu}%")
c3.metric("Avg Memory", f"{avg_memory}%")

fig = px.line(
    trend_df,
    x="bucket",
    y="total_cost",
    title="DEV Cost Trend"
)

st.plotly_chart(fig, use_container_width=True)

service_cost = (
    df.groupby("service_name")
      ["estimated_cost"]
      .sum()
      .reset_index()
)

fig = px.bar(
    service_cost,
    x="service_name",
    y="estimated_cost",
    title="DEV Service Consumption"
)

st.plotly_chart(fig, use_container_width=True)

st.info(
    "Development workloads focus on experimentation, feature development, and infrastructure validation."
)