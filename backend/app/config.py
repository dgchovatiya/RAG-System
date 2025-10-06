"""
Application configuration management using Pydantic settings.
Loads configuration from environment variables with sensible defaults.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # OpenAI Configuration
    openai_api_key: str
    embedding_model: str = "text-embedding-3-small"
    embedding_dimension: int = 1536
    llm_model: str = "gpt-4-turbo-preview"
    llm_temperature: float = 0.7
    max_tokens: int = 500
    
    # Qdrant Configuration
    qdrant_host: str = "qdrant"
    qdrant_port: int = 6333
    qdrant_collection_name: str = "legal_faqs"
    
    # Retrieval Configuration
    top_k_results: int = 2
    similarity_threshold: float = 0.6  # Lowered from 0.7 to catch semantic variations
    
    # Application Configuration
    environment: str = "development"
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """
    Create cached instance of settings.
    Using lru_cache ensures we only load settings once.
    """
    return Settings()
