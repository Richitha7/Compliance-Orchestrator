from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_ENV: str = "dev"
    SECRET_KEY: str = "dev"
    MONGODB_URI: str | None = None
    MONGODB_DB: str = "stremly_orchestrator"
    REDIS_URL: str | None = None
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    VECTOR_DB: str = "faiss"
    RAG_TOP_K: int = 4
    RISK_THRESHOLD: float = 0.5
    TIMEOUT_SECONDS: int = 20
    ARTIFACT_DIR: str = "./data/artifacts"
    INDEX_DIR: str = "./data/index"

    class Config:
        env_file = ".env"

settings = Settings()
