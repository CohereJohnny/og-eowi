import json
from functools import lru_cache
from pathlib import Path

from .config import get_settings
from .models import Chunk, Document


def _repo_data_dir() -> Path:
    settings = get_settings()
    data_dir = settings.data_dir
    if data_dir.exists():
        return data_dir
    return Path(__file__).resolve().parents[2] / "data"


@lru_cache
def load_corpus() -> dict:
    data_dir = _repo_data_dir()
    index_file = data_dir / "index" / "corpus.json"
    mock_file = data_dir / "mock" / "corpus.json"
    source = index_file if index_file.exists() else mock_file
    with source.open("r", encoding="utf-8") as f:
        return json.load(f)


def get_chunks() -> list[Chunk]:
    return [Chunk(**chunk) for chunk in load_corpus().get("chunks", [])]


def get_documents() -> list[Document]:
    return [Document(**doc) for doc in load_corpus().get("documents", [])]


def get_document(doc_id: str) -> Document | None:
    return next((doc for doc in get_documents() if doc.doc_id == doc_id), None)


def get_chunk(chunk_id: str) -> Chunk | None:
    return next((chunk for chunk in get_chunks() if chunk.chunk_id == chunk_id), None)


def get_well(well_id: str) -> dict | None:
    return next((well for well in load_corpus().get("wells", []) if well["well_id"] == well_id), None)


def get_formation_tops_for_well(well_id: str) -> list[dict]:
    return [top for top in load_corpus().get("formation_tops", []) if top["well_id"] == well_id]


def list_wells() -> list[dict]:
    return load_corpus().get("wells", [])
