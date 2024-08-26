import asyncio
import logging

from sqlalchemy.ext.asyncio import create_async_engine
from app.shared.models import Base

logger = logging.getLogger()
db_url = "postgresql+asyncpg://admin:changethis@localhost:5432/load"


async def migrate_tables() -> None:
    logger.info("Starting to migrate")

    engine = create_async_engine(db_url)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    logger.info("Done migrating")


if __name__ == "__main__":
    asyncio.run(migrate_tables())
