from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    """Application settings with validation and defaults."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    # Database
    database_url: str = "sqlite:///./data/cvforge.db"
    
    # Paths
    data_dir: Path = Path("./data")
    generated_dir: Path = Path("./data/generated")
    profile_path: Path = Path("./config/profile.json")
    templates_dir: Path = Path("./templates")
    
    # AI Model
    embedding_model: str = "paraphrase-multilingual-MiniLM-L12-v2"
    
    # CV Generation
    max_projects_per_cv: int = 5
    similarity_threshold: float = 0.3
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Ensure directories exist
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.generated_dir.mkdir(parents=True, exist_ok=True)

# Singleton instance
settings = Settings()