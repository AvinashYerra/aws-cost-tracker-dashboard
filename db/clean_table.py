from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()

engine = create_engine(os.getenv("DATABASE_URL"))

query = """
DELETE FROM 
cloud_metrics
WHERE 1=1
"""

with engine.connect() as conn:
    conn.execute(text(query))

    # for row in result:
    #     print(row)