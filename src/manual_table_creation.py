import asyncio
import logging

from sqlalchemy.ext.asyncio import create_async_engine

from .async_db import ASYNC_DB, Base

logger = logging.getLogger()


async def migrate_tables() -> None:
    logger.info("Starting to migrate")

    engine = create_async_engine(ASYNC_DB)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    logger.info("Done migrating")


if __name__ == "__main__":
    asyncio.run(migrate_tables())
