from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application Settings
    """

    APP_NAME: str = Field(default="voice-automation")
    APP_DESCRIPTION: str = Field(default="Record Filter Application Backend")
    APP_ENVIRONMENT: str = Field(default="local")
    APP_DEBUG: bool = Field(default=True)
    APP_ROOT_PATH: str = Field(default="")
    API_STR: str = Field(default="")

    APP_LOGGER_NAME: str = Field(default="VOICE_AUTOMATION")
    APP_LOG_LEVEL: str = Field(default="DEBUG")

    API_TOKEN: str = Field(description="API Token for access")

    MONGO_DB_HOST: str = Field(default="localhost")
    MONGO_DB_PORT: int = Field(default=27017)

    SQL_DB_HOST: str = Field(default="localhost")
    SQL_DB_USERNAME: str = Field(default="root")
    SQL_DB_PASSWORD: str = Field(default="")

    model_config = SettingsConfigDict(
        case_sensitive=True, env_file=".env", extra="allow"
    )


settings = Settings()
