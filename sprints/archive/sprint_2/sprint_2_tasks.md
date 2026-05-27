# Sprint 2 Tasks — North Platform Architecture Pivot

## Goals

- Replan Sprint 2 around Cohere North as the agent and retrieval runtime.
- Update product and architecture specs so North Libraries own document ingestion, indexing, retrieval, and citation grounding.
- Define the Sprint 3 implementation path for North Library ingestion, North-hosted agent configuration, backend proxying, streaming adaptation, and citation mapping.
- Preserve local retrieval work only as fallback/mock scaffolding, not as the primary v1 plan.

## Tasks

- [x] Research North API contracts for authentication, Library creation, Library upload jobs, job polling, agent creation, streaming, and citation payloads.
- [x] Update `specs/architecture.md` to make North the agent and retrieval runtime.
- [x] Update `specs/techstack.md` for North Agents, Files, Libraries, and the FastAPI proxy role.
- [x] Update `specs/datamodel.md` around North IDs, Library status, artifact mapping, and citation mapping.
- [x] Update `specs/userstories.md` to replace local indexing/retrieval stories with North Library and North agent stories.
- [x] Update `sprints/sprintplan.md` so Sprint 2 is the North pivot and Sprint 3 is North integration implementation.
- [x] Create `specs/north-integration.md` to capture API contracts, environment variables, Sprint 3 success criteria, go/no-go gates, and open risks.
- [x] Update `sprints/sprint_2/sprint_2_testplan.md` for feasibility checks and API contract validation.

## Progress

Sprint 2 is no longer a local indexing implementation sprint. The architecture now targets North Libraries for PDF ingestion/retrieval and a North-hosted EOWI agent for runtime reasoning. FastAPI remains as a thin secure proxy, streaming adapter, and fallback orchestrator for the existing UI.

North API research completed:

- North API base: `https://{north-hostname}/api` with bearer authentication.
- Existing My Drive artifacts can create a Library through `POST /v1/libraries`.
- Uploaded files can create a Library through `POST /v1/libraries/jobs`.
- Library upload jobs are polled with `GET /v1/libraries/jobs/{job_id}` until completion and `library_id` availability.
- Agents can be created through `POST /v1/agents` with name, visibility, preamble, model, hosted tools, and optional function tools.
- Streaming event shape and final citation payload shape still require live validation before Sprint 3 implementation is considered low risk.

## Sprint Review

### Demo Readiness

The Sprint 1 demo UI remains usable against mock/local backend behavior. Sprint 2 has clarified that the next implementation target is North platform integration rather than local retrieval infrastructure.

### Gaps/Issues

- Exact North chat/streaming event shape must be validated against the target North instance.
- Citation payload compatibility with the current PDF viewer/citation chip UX is not yet proven.
- North-hosted custom tool support for structured well metadata needs validation.

### Next Steps

Begin Sprint 3 only after the go/no-go checklist in `specs/north-integration.md` is satisfied or each unresolved risk has an accepted fallback.
