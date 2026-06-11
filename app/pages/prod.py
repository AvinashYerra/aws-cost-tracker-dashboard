import streamlit as st
import plotly.express as px

from app.utils import (
    get_environment_data,
    get_cost_trend
)

st.set_page_config(layout="wide")

st.title("Production Environment")

df = get_environment_data("PROD")

trend_df = get_cost_trend("PROD")

prod_cost = round(
    df["estimated_cost"].sum(),
    2
)

service_cost = (
    df.groupby("service_name")
      ["estimated_cost"]
      .sum()
      .reset_index()
)

top_service = service_cost.sort_values(
    by="estimated_cost",
    ascending=False
).iloc[0]

health_score = round(
    100 - (
        df["metric_value"].std()
        / df["metric_value"].mean()
    ) * 10,
    1
)

c1,c2,c3 = st.columns(3)

c1.metric("Production Cost", f"${prod_cost}")
c2.metric("Top Service", top_service["service_name"])
c3.metric("Health Score", f"{health_score}%")

fig = px.line(
    trend_df,
    x="bucket",
    y="total_cost",
    markers=True,
    title="Production Cost Trend"
)

st.plotly_chart(fig, use_container_width=True)

fig = px.bar(
    service_cost,
    x="service_name",
    y="estimated_cost",
    title="Production Cost Breakdown"
)

st.plotly_chart(fig, use_container_width=True)

st.success(
    "Production environment represents live business workloads and cost governance metrics."
)