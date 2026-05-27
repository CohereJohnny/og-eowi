# End-of-Well Intelligence Demo

EOWI is a Cohere-powered demo that answers drilling questions about Volve well 15/9-F-11 and offset wells with grounded engineering briefings, visible tool traces, and PDF citation drill-down.

## Quick Start

1. Copy environment variables:

```bash
cp .env.example .env.local
```

2. Add `COHERE_API_KEY` to `.env.local` when live Cohere calls are needed. The demo also runs against the bundled mock corpus without the key.

3. Start the demo:

```bash
docker compose up --build
```

4. Open `http://localhost:3001`.

The backend is published on `http://localhost:8001` for direct debugging. The frontend still proxies to the backend over the Compose network.

## Local Development

Backend:

```bash
uv sync --all-groups
uv run uvicorn app.main:app --app-dir backend --reload --port 8001
```

Frontend:

```bash
pnpm --dir frontend install
pnpm --dir frontend run dev -- -p 3001
```

## Data Flow

```mermaid
flowchart LR
    Databricks[DatabricksVolume] --> Export[fetch_volve_databricks.py]
    Export --> Raw[data/raw]
    Raw --> Curate[curate_volve_pdfs.py]
    Curate --> Curated[data/curated/pdfs]
    Curated --> NorthSetup[north_setup.py]
    NorthSetup --> North[NorthLibraryAndAgent]
    North --> Backend[FastAPIProxy]
    Backend --> Frontend[NextJSUI]
```

### Real Volve data (Sprint 3.5)

1. Mount or copy the Databricks volume path from `scripts/wells.yaml` (default: `/Volumes/equinor_asa_volve_data_village/public/volve`).
2. Export: `uv run python scripts/fetch_volve_databricks.py`
3. Curate: `uv run python scripts/curate_volve_pdfs.py`
4. North ingest: `uv run python scripts/north_setup.py` (requires `NORTH_BEARER_TOKEN` in `.env.local`)
5. Copy `library_id` and `agent_id` from `data/north/state.json` into `.env.local`.

## Demo Questions

- "I'm planning a new well in the Hugin Formation. What are the three things I most need to know from how 15/9-F-11 was drilled?"
- "Of those issues, which were avoidable through better well design vs. better execution?"
- "Compare drilling performance on F-11 vs F-14."

## Specifications

The authoritative specs live in `specs/`. The master sprint plan lives in `sprints/sprintplan.md`.
