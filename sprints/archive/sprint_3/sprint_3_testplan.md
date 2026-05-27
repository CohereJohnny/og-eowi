# Sprint 3 Test Plan — North Agent And Library Integration

## Purpose

Validate that the EOWI demo can run through Cohere North for document retrieval and agent responses while preserving the existing local fallback mode.

## Automated Checks

- [x] `uv run pytest`
- [x] `uv run ruff check backend scripts`
- [x] `uv run ruff format --check backend scripts`
- [x] `pnpm --dir frontend run typecheck`
- [x] `pnpm --dir frontend run build`

## Backend Validation

- [x] Missing North configuration returns local fallback status, not a crash.
- [x] `NORTH_BASE_URL=https://demo.north.cohere.com/api` is accepted.
- [x] `NORTH_BEARER_TOKEN` is read only server-side and is never returned by status/settings endpoints.
- [x] North client wrapper reports authentication and network failures as safe warnings/errors.
- [x] Programmatic Library job creation can submit a curated file when credentials and source files are available.
- [x] Library job polling reaches `COMPLETED` or `FAILED` with file-level status details.
- [x] North agent create/select flow records a usable `agent_id`.
- [x] `/chat` can route to North when required IDs and token are configured.
- [x] `/chat` falls back to the local deterministic agent when North is unavailable or explicitly disabled.

## Frontend Validation

- [x] Settings UI can submit North configuration without storing the bearer token in browser storage.
- [x] Settings/status UI clearly shows North ready, missing config, or fallback mode.
- [x] Existing demo question still renders a brief through the current UI.
- [x] Tool timeline displays North progress events or fallback tool events.
- [x] Citation chips render source name and snippet at minimum for North responses.
- [x] PDF/source modal degrades gracefully when page or bbox data is unavailable.

## Live North Validation

- [x] Authenticate against `https://demo.north.cohere.com/api`.
- [x] Upload at least one curated Volve PDF or mock PDF through the North Library job flow.
- [x] Poll the job until a terminal state.
- [x] Create or select the EOWI North agent.
- [x] Ask one F-11 question through the backend proxy.
- [x] Confirm the response includes grounded source/citation metadata.

## Acceptance Criteria

- [x] North-backed chat path works with server-side credentials.
- [x] Local fallback path remains reliable.
- [x] No raw bearer token is exposed to the frontend response payloads or browser storage.
- [x] Citation/source display remains usable even without page-level North citation metadata.
