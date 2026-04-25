from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="database_", env_file=".env", extra="ignore")

    url: str = "sqlite:///./library.db"


db_settings = DatabaseSettings()
