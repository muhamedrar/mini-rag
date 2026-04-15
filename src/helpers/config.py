
from pydantic_settings import BaseSettings
from typing import Optional
class Settings(BaseSettings):
    
    APP_NAME: str
    APP_VERSION: str

    FILE_ALLOWED_TYPE: list
    FILE_ALLOWED_SIZE: int
    FILE_DEFAULT_CHUNK_SIZE: int

    MONGODB_URL : str
    MONGODB_db : str

    GENERATION_BACKEND : str
    EMBEDING_BACKEND : str

    OPENAI_API_KEY: Optional[str] = None
    OPENAI_URI: Optional[str] = None
    COHERE_API_KEY: Optional[str] = None
    OLLAMA_API_KEY: Optional[str] = None
    OLLAMA_API_URL: Optional[str] = None
    GENERATION_MODEL_ID: Optional[str] = None
    EMBEDDING_MODEL_ID: Optional[str] = None
    EMBEDDING_MODEL_SIZE: Optional[int] = None
    INPUT_DEFAULT_MAX_CHARACTERS: Optional[int] = None
    GENERATION_DEFAULT_MAX_TOKEN: Optional[int] = None
    DEFAULT_TEMPERATURE: Optional[float] = None

    VECTOR_DISTANCE_METHOD: Optional[str] = None
    VECTOR_DB_BACKEND: str
    VECTOR_DB_PATH: str 


    DEFAULT_LANG: str = "en"
    PRIMARY_LANG : str = "en"
    
    


    class Config:
        env_file = ".env"


def get_settings():
    return Settings()