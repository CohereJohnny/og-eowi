# Sprint 1 Tasks — Foundation + Data Acquisition

## Goals

- Create the runnable FastAPI + Next.js + Docker Compose foundation.
- Implement local data acquisition and extraction scaffolding.
- Build a mock corpus so agent and UI work can proceed before real Volve export finishes.

## Tasks

- [x] Create sprint artifact structure.
- [x] Create backend project scaffold.
- [x] Create frontend project scaffold.
- [x] Add Docker Compose and environment template.
- [x] Add v1 `wells.yaml` subset.
- [x] Implement Databricks export script.
- [x] Implement extraction script with pdfplumber path and vision placeholder.
- [x] Implement DDR/EOWR section parser.
- [x] Add mock corpus and manifest.
- [x] Add bbox conversion helper for block-level highlights.

## Progress

Sprint 1 implementation was completed as part of the initial demo build. The real Databricks export path is implemented as a script, while a curated mock corpus keeps downstream retrieval, agent, UI, and eval work runnable without requiring the external volume during local validation.
