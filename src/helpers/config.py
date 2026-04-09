
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

    GENERATION_BACKEND : str
    EMBEDING_BACKEND : str

    OPENAI_API_KEY: str = None
    OPENAI_URI: str = None
    COHERE_API_KEY: str = None
    OLLAMA_API_KEY: str = None
    OLLAMA_API_URL: str = None
    GENERATION_MODEL_ID: str = None
    EMBEDDING_MODEL_ID: str = None
    EMBEDDING_MODEL_SIZE: int = None
    INPUT_DEFAULT_MAX_CHARACTERS: int = None
    DEFAULT_OUTPUT_MAX_TOKENS: int = None
    DEFAULT_TEMPERATURE: float = None


    class Config:
        env_file = ".env"


def get_settings():
    return Settings()