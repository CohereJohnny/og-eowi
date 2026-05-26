# End-of-Well Intelligence Demo

EOWI is a Cohere-powered demo that answers drilling questions about Volve well 15/9-F-11 and offset wells with grounded engineering briefings, visible tool traces, and PDF citation drill-down.

## Quick Start

1. Copy environment variables:

```bash
cp .env.example .env
```

2. Add `COHERE_API_KEY` to `.env` when live Cohere calls are needed. The demo also runs against the bundled mock corpus without the key.

3. Start the demo:

```bash
docker compose up --build
```

4. Open `http://localhost:3001`.

The backend is private to the Compose network by default. For direct backend debugging, run it locally with Uvicorn or add a temporary host port mapping.

## Local Development

Backend:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Frontend:

```bash
cd frontend
npm install
npm run dev
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
