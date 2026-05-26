from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from .agent import run_agent
from .db import get_chunk, get_documents, list_wells
from .models import ChatRequest

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
    return StreamingResponse(
        run_agent(request.message, request.session_id, request.well_id),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
