import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        # `.env.prod` takes priority over `.env`:
        # Even when using a dotenv file, pydantic will still read environment variables
        # as well as the dotenv file, environment variables will always take priority
        # over values loaded from a dotenv file.
        # https://docs.pydantic.dev/latest/concepts/pydantic_settings/#dotenv-env-support
        env_file=os.getenv("TAGGING_DASHBOARD_ENV", (".env", ".env.prod")),
        extra='allow'
    )
    # Application settings
    APP_NAME: str = Field("Tagging Dashboard", env="APP_NAME")
    DEBUG: bool = Field(False, env="DEBUG")
    # Paths
    TAG_PATH: str = Field("./tags", env="CSV_PATH")
    CSV_PATH: str = Field("data", env="CSV_PATH")
    VIDEO_PATH: str = Field("videos", env="VIDEO_PATH")
    SPRITE_FOLDER: str = Field("./sprites", env="SPRITE_FOLDER")

    # Derived upload paths
    @property
    def CSV_UPLOAD_DIR(self) -> Path:
        path = Path("uploaded/csv")
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def VIDEO_UPLOAD_DIR(self) -> Path:
        path = Path("uploaded/videos")
        path.mkdir(parents=True, exist_ok=True)
        return path
