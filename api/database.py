import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

URL_BANCO = os.getenv("DATABASE_URL", "postgresql+asyncpg://movieuser:moviepass@db:5432/moviedb")

motor = create_async_engine(URL_BANCO, echo=True)
SessaoLocal = async_sessionmaker(motor, expire_on_commit=False)
