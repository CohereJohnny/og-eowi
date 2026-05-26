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

## Sprint Review

Demo Readiness: The project foundation is runnable with FastAPI, Next.js, Docker Compose, environment templates, data acquisition scaffolding, parsing scripts, and a mock corpus that unblocks downstream demo flows.

Gaps/Issues: The Databricks export path remains a local script scaffold until the live Volve export is connected. The mock corpus is intentionally narrow and should be expanded by later sprint indexing work.

Next Steps: Carry forward to Sprint 2 with structured loading, chunk enrichment, embeddings, hybrid retrieval, and retrieval smoke testing.
