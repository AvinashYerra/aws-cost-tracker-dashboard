from sqlalchemy import text
from db.connection import engine

queries = {
    "cost_by_service": """
        SELECT
            service_name,
            ROUND(SUM(estimated_cost)::numeric,2) total_cost
        FROM cloud_metrics
        GROUP BY service_name
        ORDER BY total_cost DESC
    """,

    "records_by_service": """
        SELECT
            service_name,
            COUNT(*) records
        FROM cloud_metrics
        GROUP BY service_name
        ORDER BY records DESC
    """,

    "cost_by_environment": """
        SELECT
            environment,
            ROUND(SUM(estimated_cost)::numeric,2) total_cost
        FROM cloud_metrics
        GROUP BY environment
        ORDER BY total_cost DESC
    """
}

with engine.connect() as conn:

    for name, query in queries.items():

        print(f"\n{name.upper()}")
        print("-" * 50)

        result = conn.execute(text(query))

        for row in result:
            print(row)