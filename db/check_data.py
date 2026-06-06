from sqlalchemy import text
from db.connection import engine

query = """
SELECT count(*)
FROM cloud_metrics
"""

with engine.connect() as conn:
    result = conn.execute(text(query))

    for row in result:
        print(row)