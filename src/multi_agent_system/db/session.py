from __future__ import annotations

import os
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from .models import Base

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./aents.db")

engine = create_async_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False}) if DATABASE_URL.startswith("sqlite") else create_async_engine(DATABASE_URL, echo=False, pool_size=10, max_overflow=20)

AsyncSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False, autoflush=False)


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
