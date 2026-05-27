# Sprint 3 Tasks — North Agent And Library Integration

## Goals

- Implement the North runtime path planned in Sprint 2.
- Programmatically create/sync a North Library from curated Volve PDFs.
- Configure or select a North-hosted EOWI agent.
- Route the existing demo UI through a FastAPI North proxy while preserving local fallback mode.
- Keep North bearer tokens server-side and out of browser storage.

## Tasks

- [x] Add the North Python SDK dependency and backend North configuration.
- [x] Implement a backend North client wrapper with server-side bearer token handling.
- [x] Implement programmatic Library upload-job creation, polling, and agent create/select setup.
- [x] Add secure settings/status endpoints and frontend settings UI.
- [x] Route `/chat` through North when configured, with local fallback preserved.
- [x] Adapt North responses into the existing SSE `ToolEvent` contract.
- [x] Normalize North citations into the current citation chip/source display contract.
- [x] Add backend tests for config, client errors, event adaptation, citation normalization, and fallback mode.
- [x] Run backend tests, frontend typecheck, frontend build, and live/manual North validation where credentials allow.

## Progress

Sprint 3 starts from the Sprint 1 local deterministic agent and Sprint 2 North platform architecture pivot. The local agent remains the fallback path; the primary Sprint 3 work is North Library ingestion, North agent setup, FastAPI proxy integration, settings/status support, and citation/event adaptation.

North integration progress:

- Added the North Python SDK from `https://demo.north.cohere.com/api/v1/sdk/python-latest.tar.gz`.
- Added server-side `NORTH_BASE_URL`, `NORTH_BEARER_TOKEN`, `NORTH_AGENT_ID`, `NORTH_LIBRARY_ID`, and `NORTH_MODE` configuration.
- Added FastAPI North status/settings endpoints that never return the raw bearer token.
- Added a frontend North settings panel; bearer token input is one-time submission only and is not persisted in browser storage.
- Added `scripts/north_setup.py` to create Library upload jobs, poll status, and create a North agent.
- Validated SDK connectivity against `https://demo.north.cohere.com/api`.
- Created a generated ignored validation PDF, uploaded it through a North Library job, and received a completed `library_id`.
- Created a validation North agent and confirmed North chat returns text plus normalizable citation/source data when Library artifact file IDs are passed.

Validation completed:

- `uv run ruff check backend scripts`
- `uv run ruff format --check backend scripts`
- `uv run pytest`
- `pnpm --dir frontend run typecheck`
- `pnpm --dir frontend run build`

## Sprint Review

### Demo Readiness

Sprint 3 delivered the North integration path: SDK client, Library setup script, secure settings UI, streaming chat adapter, and fallback behavior. The demo can answer through North when credentials and IDs are configured.

### Gaps/Issues

- North streaming works, but the active Library still contains only the Sprint 3 validation PDF, not real Volve DDR/EOWR documents.
- PDF modal still shows mock pages until real files exist under `data/curated/pdfs/`.

### Next Steps

Proceed with Sprint 3.5 to fetch real Volve data, curate demo-critical PDFs, and rebuild the North Library before Sprint 4 UI polish.
