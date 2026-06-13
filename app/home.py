import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

import pandas as pd
import plotly.express as px
import streamlit as st
from sqlalchemy import text

from db.connection import engine

st.set_page_config(
    page_title="AWS Cost Tracker",
    page_icon="☁️",
    layout="wide"
)

st.title("☁️ AWS Services Cost Tracker")
st.caption("Executive Infrastructure Overview")

query = """
SELECT *
FROM cloud_metrics
"""

with engine.connect() as conn:
    df = pd.read_sql(text(query), conn)

total_cost = round(df["estimated_cost"].sum(), 2)

total_records = len(df)

env_count = df["environment"].nunique()

top_service = (
    df.groupby("service_name")
      ["estimated_cost"]
      .sum()
      .idxmax()
)

c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Cost", f"${total_cost:,.2f}")
c2.metric("Records", f"{total_records:,}")
c3.metric("Environments", env_count)
c4.metric("Top Service", top_service)

st.divider()

left, right = st.columns(2)

with left:

    env_cost = (
        df.groupby("environment")
        ["estimated_cost"]
        .sum()
        .reset_index()
    )

    fig = px.pie(
        env_cost,
        names="environment",
        values="estimated_cost",
        title="Cost by Environment"
    )

    st.plotly_chart(fig, use_container_width=True)

with right:

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
        title="Cost by Service"
    )

    st.plotly_chart(fig, use_container_width=True)

env_summary = (
    df.groupby("environment")
      .agg(
          total_cost=("estimated_cost", "sum"),
          records=("service_name", "count"),
          avg_metric=("metric_value", "mean")
      )
      .reset_index()
)

env_summary["total_cost"] = env_summary["total_cost"].round(2)
env_summary["avg_metric"] = env_summary["avg_metric"].round(2)

st.subheader("Environment Summary")

st.dataframe(
    env_summary,
    use_container_width=True,
    hide_index=True
)


trend_df = (
    df.groupby(
        [
            "ts",
            "environment"
        ]
    )["estimated_cost"]
    .sum()
    .reset_index()
)

fig = px.line(
    trend_df,
    x="ts",
    y="estimated_cost",
    color="environment",
    title="Cost Trend by Environment"
)

st.plotly_chart(
    fig,
    use_container_width=True
)



st.subheader("Top Cost Drivers")

leaderboard = (
    df.groupby("service_name")
      ["estimated_cost"]
      .sum()
      .reset_index()
      .sort_values(
          by="estimated_cost",
          ascending=False
      )
)

leaderboard["estimated_cost"] = (
    leaderboard["estimated_cost"]
    .round(2)
)

st.dataframe(
    leaderboard,
    use_container_width=True,
    hide_index=True
)


st.subheader("Environment Health")

health = (
    df.groupby("environment")
      ["metric_value"]
      .mean()
      .reset_index()
)

cols = st.columns(3)

for idx, row in health.iterrows():

    score = max(
        0,
        min(
            100,
            int(100 - row["metric_value"])
        )
    )

    with cols[idx]:
        st.metric(
            row["environment"],
            f"{score}%"
        )

        st.progress(score / 100)


latest_ts = df["ts"].max()

latest_snapshot = (
    df[df["ts"] == latest_ts]
    .sort_values("service_name")
)

st.subheader("Latest Infrastructure Snapshot")

st.dataframe(
    latest_snapshot,
    use_container_width=True,
    hide_index=True
)