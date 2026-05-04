import asyncio
import os
import sys


async def check():
    import asyncpg
    dsn = os.environ["DATABASE_URI"].replace("postgresql+asyncpg://", "postgresql://")
    conn = await asyncpg.connect(dsn)
    await conn.execute("SELECT 1")
    await conn.close()


try:
    asyncio.run(check())
    sys.exit(0)
except Exception as e:
    print(f"Health check failed: {e}", file=sys.stderr)
    sys.exit(1)
