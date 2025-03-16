from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        # `.env.prod` takes priority over `.env`
        env_file=('.env', '.env.prod'),
        extra='allow'
    )
    # Application settings
    APP_NAME: str = Field("Tagging Dashboard", env="APP_NAME")
    DEBUG: bool = Field(False, env="DEBUG")

    # Paths
    CSV_PATH: str = Field("data", env="CSV_PATH")
    VIDEO_PATH: str = Field("videos", env="VIDEO_PATH")
    SPRITE_FOLDER: str = Field("./sprites", env="SPRITE_FOLDER")
