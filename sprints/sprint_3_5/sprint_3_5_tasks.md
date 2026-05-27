# Sprint 3.5 Tasks — Volve Data Fetch And Curation

## Goals

- Export the v1 Volve well subset from Databricks to local `data/raw/`.
- Curate demo-critical PDFs into `data/curated/pdfs/` with a real `data/curated/manifest.json`.
- Rebuild the North Library from curated real documents and record new `library_id` / `agent_id`.

## Tasks

- [ ] Document Databricks volume mount and credentials for `scripts/fetch_volve_databricks.py`.
- [ ] Run `scripts/fetch_volve_databricks.py` using `scripts/wells.yaml` and capture export manifest.
- [ ] Implement `scripts/curate_volve_pdfs.py` to select demo-critical files and populate `data/curated/`.
- [ ] Run `scripts/north_setup.py` against curated PDFs and update `.env.local` with new North IDs.
- [ ] Verify North chat uses real document content (not mock validation PDF only).

## Progress

Sprint 3.5 depends on Sprint 3 North integration being complete. The fetch script and wells config already exist from Sprint 1; this sprint executes them and bridges the gap to real North Library content.
