from typing import Any, Literal

from pydantic import BaseModel, Field


class BBox(BaseModel):
    x: float
    y: float
    width: float
    height: float


class Chunk(BaseModel):
    chunk_id: str
    doc_id: str
    well_id: str | None = None
    doc_type: str
    chunk_seq: int
    page_start: int
    page_end: int
    section_path: str
    depth_md_start_m: float | None = None
    depth_md_end_m: float | None = None
    chunk_text: str
    bbox: list[float] = Field(default_factory=lambda: [96, 210, 520, 318])
    token_count: int = 0
    score: float = 0.0


class Document(BaseModel):
    doc_id: str
    well_id: str | None = None
    doc_type: str
    title: str
    doc_date: str | None = None
    source_path: str
    page_count: int = 1
    extraction_method: str = "mock"
    quality_flag: str = "good"
    demo_critical: bool = False


class ToolEvent(BaseModel):
    type: Literal["thinking", "tool_call", "tool_result", "final", "warning"]
    text: str | None = None
    name: str | None = None
    params: dict[str, Any] | None = None
    summary: str | None = None
    data: dict[str, Any] | None = None


class ChatRequest(BaseModel):
    message: str
    session_id: str = "demo"
    well_id: str | None = "15/9-F-11"


class NorthSettingsRequest(BaseModel):
    base_url: str | None = None
    bearer_token: str | None = None
    agent_id: str | None = None
    library_id: str | None = None
    mode: Literal["auto", "north", "local"] | None = None


class NorthStatus(BaseModel):
    mode: Literal["auto", "north", "local"]
    active_mode: Literal["north", "local"]
    base_url: str
    token_configured: bool
    agent_id: str | None = None
    library_id: str | None = None
    north_ready: bool
    source: Literal["env", "runtime"]
    message: str


class NorthCitationSource(BaseModel):
    chunk_id: str
    doc_id: str
    page_start: int = 1
    page_end: int = 1
    section_path: str
    chunk_text: str
    bbox: list[float] = Field(default_factory=lambda: [96, 210, 520, 318])
