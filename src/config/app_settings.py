from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="app_", env_file=".env", extra="ignore"
    )

    name: str = "Library Management API"
    version: str = "0.1.0"
    debug: bool = False


app_settings = AppSettings()
