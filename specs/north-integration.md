# EOWI Demo — North Integration

## Overview

This document defines the required North platform integration behavior for the End-of-Well Intelligence demo. North is the primary runtime for the hosted agent and document retrieval. The local backend remains a secure proxy and compatibility layer for the existing demo UI.

Related specs: [architecture.md](architecture.md), [techstack.md](techstack.md), [datamodel.md](datamodel.md), [userstories.md](userstories.md).

## North API Contracts

### Authentication

**Requirement:** Server-side calls to North must use bearer authentication against the configured North API base URL.

**Required configuration:**

- `NORTH_BASE_URL`: North API base URL for the target instance. Sprint 3 target: `https://demo.north.cohere.com/api`.
- `NORTH_BEARER_TOKEN`: Server-side bearer token.
- `NORTH_AGENT_ID`: Active EOWI agent identifier.
- `NORTH_LIBRARY_ID`: Active EOWI Library identifier.

**Business rules:**

- North tokens must never be sent to the browser.
- The preferred token source is `.env.local` or deployment secrets consumed only by the backend.
- A UI settings page may configure non-secret values such as active mode, agent ID, or library ID, but must not persist or expose the raw bearer token in browser storage.
- If user-entered North credentials are required later, the UI must hand them to a server-side secret/session mechanism or token exchange flow before North calls are made.
- Missing North configuration must produce a clear backend error or activate explicit local fallback mode.
- If the target deployment requires additional identity headers, the backend proxy owns those headers.

### Libraries From Existing Artifacts

**Requirement:** The demo must support creating or selecting a North Library from files/folders that already exist in My Drive.

**Confirmed contract:**

- Endpoint: `POST /v1/libraries`
- Required fields: `tool_id`, `name`
- Supported tool association: `my_drive`
- Optional fields: `description`, `artifacts`
- Response includes `id`, `name`, `tool_id`, `status`, artifact counts, artifacts, and recent failed-file details.

**Acceptance criteria:**

- Existing artifacts can be attached to a Library.
- The created Library ID is recorded as the active EOWI Library.
- Failed artifacts are visible before demo readiness is declared.

### Libraries From Uploaded Files

**Requirement:** The demo must support creating a North Library by uploading curated Volve PDFs.

**Confirmed contract:**

- Endpoint: `POST /v1/libraries/jobs`
- Request type: multipart form data
- Required fields: `name`, `files`
- Optional fields: `description`, `overwrite_files`, `attach_existing_files`
- Response includes `id`, `state`, file counts, failed-file details, and eventually `library_id`.

**Acceptance criteria:**

- Curated files can be submitted as an async Library job.
- The job ID is recorded while indexing is running.
- The created Library ID is recorded when the job completes.
- Failed demo-critical files block demo-ready status.

### Library Job Polling

**Requirement:** The backend or setup script must poll Library upload jobs until completion or failure.

**Confirmed contract:**

- Endpoint: `GET /v1/libraries/jobs/{job_id}`
- States: `RUNNING`, `COMPLETED`, `FAILED`
- Completed responses include `library_id`.
- Responses include total, indexed, failed, and failed-file detail fields.

**Acceptance criteria:**

- Polling continues until the job reaches a terminal state.
- `COMPLETED` jobs yield a usable `library_id`.
- `FAILED` jobs produce a visible setup error with failed-file details.

### Agent Creation And Configuration

**Requirement:** The EOWI agent must run on North and must be configured with the correct drilling behavior and document access.

**Confirmed contract:**

- Endpoint: `POST /v1/agents`
- Required fields: `name`, `visibility`
- Optional fields: `description`, `preamble`, `temperature`, `tools`, `icebreakers`, `model`, `reasoning_options`
- Tool definitions can include North hosted tools and function tools.

**Acceptance criteria:**

- The active agent can be created or selected by ID.
- The active agent has access to the active EOWI Library.
- The agent preamble preserves the EOWI answer policy: grounded claims, clear caveats, engineering tone, and citation-backed findings.
- Structured metadata tools are either available to the North agent or explicitly served through a local fallback path.

### Chat, Streaming, And Citations

**Requirement:** The backend proxy must adapt North agent responses to the existing demo UI contract or define a replacement UI contract.

**Known status:** Endpoint and payload shape require live validation against the target North instance.

**Required response capabilities:**

- Final answer text.
- Agent progress or tool activity suitable for the tool-call timeline.
- Citation metadata that resolves to source documents.
- Recoverable warning or error state for missing citation metadata.

**Acceptance criteria:**

- A North-backed answer can be displayed in the existing chat UI.
- Citation chips can show source name and snippet at minimum.
- Page-level PDF navigation is enabled if North citation payloads include page data or if local metadata can enrich citations.
- If streaming is unavailable or event shapes differ materially, the UI must still support a non-streaming final answer fallback for the demo.

## Sprint 3 Go/No-Go Checklist

Sprint 3 implementation may begin when all required items are true or each exception has an accepted fallback.

### Required Go Criteria

- [ ] `NORTH_BASE_URL=https://demo.north.cohere.com/api` and `NORTH_BEARER_TOKEN` are available server-side for the target instance.
- [ ] Library creation from uploaded files is validated with at least one curated PDF.
- [ ] Library job polling returns terminal states and a usable `library_id`.
- [ ] Existing-artifact Library creation is validated or explicitly deferred.
- [ ] Agent creation or agent selection is validated.
- [ ] The EOWI agent can be associated with the EOWI Library or equivalent hosted tool configuration.
- [ ] A test question returns a grounded response from the North Library.
- [ ] Citation metadata can be mapped to UI citation chips.
- [ ] Streaming or non-streaming response behavior is known and accepted.
- [ ] Local fallback mode remains available for demos without North access.

### No-Go Conditions

- North credentials are unavailable or cannot authenticate.
- Uploaded Library jobs cannot ingest PDFs from the curated corpus.
- The North agent cannot access a created Library.
- Citation payloads cannot be resolved to source documents at all.
- The backend cannot legally or safely proxy required North calls server-side.

## Open Risks

### Risk: File Upload And My Drive Semantics

**Scenario:** Uploaded files may collide with existing My Drive names or produce unexpected artifact mappings.

**Expected handling:** Use explicit overwrite/attach behavior during setup and record returned artifact IDs.

### Risk: Citation Payload Compatibility

**Scenario:** North citations may not include page numbers, bounding boxes, or the exact fields expected by the current PDF viewer.

**Expected handling:** Minimum viable citation display is source name plus snippet. Page/bbox highlighting can be restored through local enrichment if North provides stable file/page references.

### Risk: Structured Well Metadata Tools

**Scenario:** North-hosted agents may not be able to call the existing local structured-data tools directly.

**Expected handling:** Keep well headers, formation tops, and offset-well metadata behind the FastAPI proxy until North function tool support is validated.

### Risk: Streaming Event Shape

**Scenario:** North streaming events may not align with the current SSE event types.

**Expected handling:** Add a backend adapter that maps North events to the existing contract, or fall back to a final-answer event with warning/tool-summary support.

### Risk: Demo Dependency On North Availability

**Scenario:** North instance access is unavailable during rehearsal or live demo.

**Expected handling:** Preserve local mock/fallback mode and make the active mode visible in setup validation.

## Documentation References

- North API overview: `https://private.docs.cohere.com/reference/overview`
- Create Library: `https://private.docs.cohere.com/reference/libraries/create`
- Create Library upload job: `https://private.docs.cohere.com/reference/libraries/create-job`
- Get Library upload job status: `https://private.docs.cohere.com/reference/libraries/get-job`
- Create Agent: `https://private.docs.cohere.com/reference/agents/create`
