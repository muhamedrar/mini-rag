
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    OPENAI_API_KEY: str
    APP_NAME: str
    APP_VERSION: str

    FILE_ALLOWED_TYPE: list
    FILE_ALLOWED_SIZE: int
    FILE_DEFAULT_CHUNK_SIZE: int

    MONGODB_URL : str
    MONGODB_db : str

    class Config:
        env_file = ".env"


def get_settings():
    return Settings()