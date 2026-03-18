
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    OPENAI_API_KEY: str
    APP_NAME: str
    APP_VERSION: str

    class Config:
        env_file = ".env"


def get_settings():
    return Settings()