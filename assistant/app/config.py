from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).parent.parent


class Settings(BaseSettings):
    LLM_MODEL: str = Field(default="qwen:3b")
    LLM_TEMPERATURE: int = Field(default=0)
    LLM_EMBEDDING_MODEL: str = Field(default="bge-m3")
    PERSISTENT_DIRECTORY: str = Field(default="./chroma_db")
    COLLECTION_NAME: str = Field(default="assistant")


settings = Settings()
