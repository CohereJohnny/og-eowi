import os
from functools import lru_cache
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from pydantic import BaseModel, Field

REPO_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(REPO_ROOT / ".env", override=False)
load_dotenv(REPO_ROOT / ".env.local", override=False)


class Settings(BaseModel):
    data_dir: Path = Field(default_factory=lambda: Path(os.getenv("DATA_DIR", "../data")))
    cohere_api_key: str | None = Field(default_factory=lambda: os.getenv("COHERE_API_KEY"))
    cohere_agent_model: str = Field(default_factory=lambda: os.getenv("COHERE_AGENT_MODEL", "command-a-03-2025"))
    cohere_vision_model: str = Field(default_factory=lambda: os.getenv("COHERE_VISION_MODEL", "command-a-plus-05-2026"))
    cohere_embed_model: str = Field(default_factory=lambda: os.getenv("COHERE_EMBED_MODEL", "embed-v4.0"))
    cohere_rerank_model: str = Field(default_factory=lambda: os.getenv("COHERE_RERANK_MODEL", "rerank-v3.5"))
    north_base_url: str = Field(
        default_factory=lambda: os.getenv("NORTH_BASE_URL", "https://demo.north.cohere.com/api")
    )
    north_bearer_token: str | None = Field(default_factory=lambda: os.getenv("NORTH_BEARER_TOKEN"))
    north_agent_id: str | None = Field(default_factory=lambda: os.getenv("NORTH_AGENT_ID"))
    north_library_id: str | None = Field(default_factory=lambda: os.getenv("NORTH_LIBRARY_ID"))
    north_mode: Literal["auto", "north", "local"] = Field(default_factory=lambda: os.getenv("NORTH_MODE", "auto"))  # type: ignore[assignment]
    north_request_timeout_seconds: float = Field(
        default_factory=lambda: float(os.getenv("NORTH_REQUEST_TIMEOUT_SECONDS", "30"))
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
