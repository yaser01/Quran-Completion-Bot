import os
import sys
from sqlalchemy import create_engine, text

try:
    uri = os.environ["DATABASE_URI"].replace("+asyncpg", "")
    engine = create_engine(uri)
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    sys.exit(0)
except Exception as e:
    print(f"Health check failed: {e}", file=sys.stderr)
    sys.exit(1)
