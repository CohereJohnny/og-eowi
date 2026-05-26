# Sprint 1 Test Plan

## Scope

Validate the project foundation, data acquisition scaffolding, extraction/parsing pipeline, and mock corpus.

## Checks

- [ ] `docker compose config` validates service definitions.
- [ ] Backend health endpoint returns `ok`.
- [ ] Frontend development server starts.
- [ ] `scripts/fetch_volve_databricks.py --help` documents required inputs.
- [ ] `scripts/extract_text.py` can process a mock text document into the expected JSON schema.
- [ ] `scripts/parse_sections.py` creates sectioned chunks with `section_path`.
- [ ] Mock corpus has chunks with `chunk_id`, page references, and bbox data.

## Manual Review

- [ ] Open the app and confirm the three-pane layout loads.
- [ ] Confirm the mock corpus reflects the demo narrative: Hugin planning, stuck pipe, mud weight, BHA, lessons learned.
