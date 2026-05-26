from functools import lru_cache
from pathlib import Path
from pydantic import BaseModel
import os


class Settings(BaseModel):
    data_dir: Path = Path(os.getenv("DATA_DIR", "../data"))
    cohere_api_key: str | None = os.getenv("COHERE_API_KEY")
    cohere_agent_model: str = os.getenv("COHERE_AGENT_MODEL", "command-a-03-2025")
    cohere_vision_model: str = os.getenv("COHERE_VISION_MODEL", "command-a-plus-05-2026")
    cohere_embed_model: str = os.getenv("COHERE_EMBED_MODEL", "embed-v4.0")
    cohere_rerank_model: str = os.getenv("COHERE_RERANK_MODEL", "rerank-v3.5")


@lru_cache
def get_settings() -> Settings:
    return Settings()
