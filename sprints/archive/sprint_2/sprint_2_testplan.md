# Sprint 2 Test Plan — North Platform Pivot

## Purpose

Validate that Sprint 3 can safely implement the North migration with known API contracts, known credentials, and a clear fallback path.

## Feasibility Checks

- [ ] Confirm `NORTH_BASE_URL=https://demo.north.cohere.com/api` is configured.
- [ ] Confirm `NORTH_BEARER_TOKEN` can authenticate server-side North API calls.
- [ ] Confirm the backend can call a simple North endpoint without exposing the token to the frontend.
- [ ] Confirm a North Library can be created from existing My Drive artifacts.
- [ ] Confirm a North Library upload job can ingest at least one curated Volve PDF.
- [ ] Confirm `GET /v1/libraries/jobs/{job_id}` returns completion status and `library_id`.
- [ ] Confirm failed-file details are returned for failed Library jobs.
- [ ] Confirm a North agent can be created or selected for the EOWI demo.
- [ ] Confirm the agent can be associated with the EOWI Library or an equivalent North hosted tool configuration.
- [ ] Confirm a North-backed agent response includes citation metadata suitable for UI display.
- [ ] Confirm North streaming or response events can map to the current SSE event types: `thinking`, `tool_call`, `tool_result`, `final`, and `warning`.

## Spec Validation

- [x] `specs/architecture.md` identifies North as the primary agent and retrieval runtime.
- [x] `specs/techstack.md` lists North Agents, Files, Libraries, and FastAPI proxy responsibilities.
- [x] `specs/datamodel.md` includes North resource IDs, Library job state, artifact mapping, and citation mapping.
- [x] `specs/userstories.md` rewrites local indexing/retrieval stories around North Libraries and North citations.
- [x] `sprints/sprintplan.md` makes Sprint 3 the North integration implementation sprint.
- [x] `specs/north-integration.md` documents open risks and go/no-go criteria.

## Acceptance Criteria

- [ ] Sprint 3 can begin with confirmed North endpoint paths and required environment variables.
- [ ] Sprint 3 can begin with a known ingestion path for curated PDFs.
- [ ] Sprint 3 can begin with a known agent configuration path.
- [ ] Sprint 3 can begin with a known citation display strategy.
- [ ] Any unresolved North API risk has a documented local fallback.
