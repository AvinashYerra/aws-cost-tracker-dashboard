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

st.title("☁️ AWS Cost Tracker")
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