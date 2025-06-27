import os
from pathlib import Path
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from project root .env file
ENV_PATH = Path(__file__).parent.parent.parent.parent / ".env"
load_dotenv(dotenv_path=ENV_PATH)

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Prime Time Medical Research Opportunities"
    
    # Database settings
    DATABASE_HOST: str = os.getenv("DATABASE_HOST", "localhost")
    DATABASE_PORT: str = os.getenv("DATABASE_PORT", "5432")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "prime_time")
    DATABASE_USERNAME: str = os.getenv("DATABASE_USERNAME", "postgres")
    DATABASE_PASSWORD: str = os.getenv("DATABASE_PASSWORD", "")
    
    # CORS settings
    BACKEND_CORS_ORIGINS: list[str] = ["*"]
    
    # PubMed settings
    PUBMED_EMAIL: str = os.getenv("PUBMED_EMAIL", "maia.marin94@e-uvt.ro")
    
    # Model paths
    MODEL_DIR: Path = Path(__file__).parent.parent.parent.parent / "src" / "model"
    
    class Config:
        case_sensitive = True

settings = Settings()
