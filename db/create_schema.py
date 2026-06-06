from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()

engine = create_engine(os.getenv("DATABASE_URL"))

with open("db/schema.sql", "r") as f:
    sql = f.read()

with engine.connect() as conn:
    for stmt in sql.split(";"):
        if stmt.strip():
            conn.execute(text(stmt))
    conn.commit()

print("Schema created successfully!")