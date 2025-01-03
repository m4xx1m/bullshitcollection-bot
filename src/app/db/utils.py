from sqlalchemy.ext.asyncio import (
    AsyncSession, 
    AsyncEngine, 
    create_async_engine, 
    async_sessionmaker,
)

from app.config import DatabaseConfig


def create_connection_string(config: DatabaseConfig, _async_fallback: bool = False) -> str:
    result = (
        f"postgresql+asyncpg://{config.user}:{config.password}"
        f"@{config.host}:{config.port}/{config.name}"
    )
    if _async_fallback:
        result += "?async_fallback=True"
    return result


def create_engine(config: DatabaseConfig) -> AsyncEngine:
    return create_async_engine(create_connection_string(config), echo=False)


def create_sessionmaker(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(bind=engine, expire_on_commit=False)
