"""
Destructive database reset — drops all tables then recreates them.
Run manually on host ONLY. Never call from bot startup.

  python -m Database.reset_db
"""
import asyncio
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy_utils import create_database, database_exists

from db.models import Base
from bot.Global_Functions import build_async_db_uri

load_dotenv()
DATABASE_URI = os.getenv('DATABASE_URI')


async def init_database() -> None:
    sync_engine = create_engine(DATABASE_URI, echo=False)
    if not database_exists(sync_engine.url):
        create_database(sync_engine.url)
    async_engine = create_async_engine(build_async_db_uri(DATABASE_URI), echo=False)
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    await async_engine.dispose()


if __name__ == "__main__":
    asyncio.run(init_database())
