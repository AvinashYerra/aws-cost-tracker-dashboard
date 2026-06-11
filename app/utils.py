import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

import pandas as pd
from sqlalchemy import text
from db.connection import engine


def get_environment_data(environment):

    query = """
    SELECT *
    FROM cloud_metrics
    WHERE environment = :environment
    ORDER BY ts
    """

    with engine.connect() as conn:
        return pd.read_sql(
            text(query),
            conn,
            params={"environment": environment}
        )


def get_cost_trend(environment):

    query = """
    SELECT
        time_bucket('5 minute', ts) AS bucket,
        SUM(estimated_cost) AS total_cost
    FROM cloud_metrics
    WHERE environment = :environment
    GROUP BY bucket
    ORDER BY bucket
    """

    with engine.connect() as conn:
        return pd.read_sql(
            text(query),
            conn,
            params={"environment": environment}
        )