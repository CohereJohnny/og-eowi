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
    Raw --> Extract[extract_text.py]
    Extract --> Parse[parse_sections.py]
    Parse --> Chunk[chunk_and_enrich.py]
    Chunk --> Index[embed_and_index.py]
    Index --> Backend[FastAPIAgent]
    Backend --> Frontend[NextJSUI]
```

## Demo Questions

- "I'm planning a new well in the Hugin Formation. What are the three things I most need to know from how 15/9-F-11 was drilled?"
- "Of those issues, which were avoidable through better well design vs. better execution?"
- "Compare drilling performance on F-11 vs F-14."

## Specifications

The authoritative specs live in `specs/`. The master sprint plan lives in `sprints/sprintplan.md`.
