# Sprint 3 Report — North Agent And Library Integration

## Summary

Sprint 3 implemented the North platform runtime path for the EOWI demo. The local deterministic agent remains available as fallback, but the primary integration path now uses Cohere North for Library-backed retrieval, a North-hosted agent, and a FastAPI proxy that adapts North responses into the existing SSE contract used by the Next.js UI.

## Completed Work

- Added the North Python SDK from `https://demo.north.cohere.com/api/v1/sdk/python-latest.tar.gz`.
- Extended backend configuration for `NORTH_BASE_URL`, `NORTH_BEARER_TOKEN`, `NORTH_AGENT_ID`, `NORTH_LIBRARY_ID`, `NORTH_MODE`, and request timeouts.
- Implemented `NorthEowiClient` for Library jobs, agent creation, non-streaming chat, and streaming chat.
- Added `scripts/north_setup.py` to upload curated PDFs, poll Library jobs, and create a North agent.
- Added FastAPI `/north/status`, `/north/settings`, and `/north/check` endpoints with server-side token handling.
- Added a frontend North settings panel; bearer tokens are submitted server-side only and are not stored in browser storage.
- Routed `/chat` through North when configured, with local fallback preserved on missing config, timeout, or stream errors.
- Implemented `NorthStreamAdapter` to map North stream events (`thinking`, tool calls, tool results, citations) into the existing `ToolEvent` timeline.
- Added backend tests for settings, client URL handling, stream adaptation, agent fallback, and citation normalization.
- Validated against the North demo instance with a generated validation PDF and confirmed streaming behavior.

## Demo Readiness

The demo can run in North mode when `NORTH_BEARER_TOKEN`, `NORTH_AGENT_ID`, and `NORTH_LIBRARY_ID` are configured. The UI still falls back to the local mock agent when North is unavailable or times out. Answers and citations are still limited to the documents present in the active North Library.

## Remaining Risks

- The active North Library currently contains validation/mock PDFs rather than a full Volve DDR/EOWR corpus.
- PDF drill-down still uses mock page rendering until real PDFs are mounted under `data/curated/pdfs/`.
- Structured well metadata tools on North remain a follow-up if North custom tools are required beyond My Drive search.

## Next Steps

Sprint 3.5 should fetch and curate real Volve documents, rebuild the North Library from those PDFs, and point runtime configuration at the new `library_id` and `agent_id`.
