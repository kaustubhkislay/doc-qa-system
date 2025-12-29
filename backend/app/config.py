from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # GCP Settings
    project_id: str = "doc-qa-482703"
    bucket_name: str = "doc-qa-482703-pdfs"
    region: str = "us-central1"
    
    # Vector store settings
    chroma_persist_dir: str = "./chroma_db"
    
    # LLM settings
    embedding_model: str = "text-embedding-004"
    llm_model: str = "gemini-2.5-flash"
    
    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    """Cache and return settings singleton."""
    return Settings()