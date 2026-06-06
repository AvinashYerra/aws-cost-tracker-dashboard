from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()

engine = create_engine(os.getenv("DATABASE_URL"))

query = """
SELECT table_name
FROM information_schema.tables
WHERE table_name='cloud_metrics';
"""

with engine.connect() as conn:
    result = conn.execute(text(query))

    for row in result:
        print(row)