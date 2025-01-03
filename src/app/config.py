import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Base(BaseSettings):
    model_config = SettingsConfigDict(env_nested_delimiter="__", extra="ignore")


class BotConfig(Base):
    token: str
    api_path: str | None = None
    skip_updates: bool = True
    superusers: list[int]
    
    
class DatabaseConfig(Base):
    user: str
    password: str
    host: str
    port: int
    name: str
    

class Config(Base):
    bot: BotConfig
    database: DatabaseConfig
    log_level: str
    bullshit_channel_id: int


def load_config() -> Config:
    return Config(_env_file=os.environ.get("ENV_FILE", ".env"))
