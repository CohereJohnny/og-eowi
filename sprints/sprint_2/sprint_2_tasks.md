# Sprint 2 Tasks — Indexing + Retrieval

## Goals

- Convert parsed sections into chunks.
- Build local indexes and structured stores.
- Provide a retrieval CLI and backend retrieval module.

## Tasks

- [x] Implement `scripts/chunk_and_enrich.py`.
- [x] Implement `scripts/load_structured.py`.
- [x] Implement `scripts/embed_and_index.py`.
- [x] Implement `backend/app/retrieval.py`.
- [x] Implement `scripts/retrieve.py`.
- [x] Add mock corpus under `data/mock/corpus.json`.

## Progress

Sprint 2 is implemented against a local mock corpus and JSON-backed retrieval interface. The production extension points for DuckDB, LanceDB, BM25, Cohere Embed v4, and Rerank 3.5 are preserved in script and module boundaries.
