from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from .agent import run_agent
from .db import get_chunk, get_documents, list_wells
from .models import ChatRequest, NorthSettingsRequest, NorthStatus
from .north_agent import run_north_agent
from .north_client import NorthClientError, NorthEowiClient
from .north_settings import get_north_runtime_config, public_north_status, update_north_settings

app = FastAPI(title="End-of-Well Intelligence Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/north/status", response_model=NorthStatus)
def north_status() -> NorthStatus:
    return public_north_status()


@app.post("/north/settings", response_model=NorthStatus)
def north_settings(request: NorthSettingsRequest) -> NorthStatus:
    return update_north_settings(request)


@app.post("/north/check")
def north_check() -> dict:
    try:
        result = NorthEowiClient().check_connection()
    except NorthClientError as exc:
        return {"ok": False, "error": str(exc), "status": public_north_status().model_dump()}
    return {"ok": True, "result": result, "status": public_north_status().model_dump()}


@app.get("/wells")
def wells() -> dict:
    return {"wells": list_wells()}


@app.get("/documents")
def documents() -> dict:
    return {"documents": [doc.model_dump() for doc in get_documents()]}


@app.get("/chunks/{chunk_id:path}")
def chunk(chunk_id: str) -> dict:
    found = get_chunk(chunk_id)
    return {"chunk": found.model_dump() if found else None}


@app.post("/chat")
async def chat(request: ChatRequest) -> StreamingResponse:
    north_config = get_north_runtime_config()
    runner = run_agent
    if north_config.active_mode == "north":
        runner = run_north_agent

    return StreamingResponse(
        runner(request.message, request.session_id, request.well_id),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
