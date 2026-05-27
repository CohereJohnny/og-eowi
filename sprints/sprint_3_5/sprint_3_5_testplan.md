# Sprint 3.5 Test Plan — Volve Data Fetch And Curation

## Purpose

Validate that real Volve documents can be exported, curated locally, and ingested into a North Library used by the demo agent.

## Prerequisites

- Databricks volume mounted at path in `scripts/wells.yaml` (default: `/Volumes/equinor_asa_volve_data_village/public/volve`).
- `NORTH_BEARER_TOKEN` configured for North upload.
- Sufficient disk space for `data/raw/` and `data/curated/pdfs/`.

## Feasibility Checks

- [ ] `scripts/fetch_volve_databricks.py --help` runs and documents required mount path.
- [ ] Export completes with `data/curated/export_manifest.json` listing copied files.
- [ ] At least one F-11 DDR and one EOWR (or equivalent) present under `data/raw/15/9-F-11/`.

## Curation Checks

- [ ] `scripts/curate_volve_pdfs.py` produces `data/curated/manifest.json` with non-mock `source_path` values.
- [ ] Demo-critical documents copied to `data/curated/pdfs/{doc_id}.pdf`.
- [ ] Manifest entries include `well_id`, `doc_type`, and `demo_critical` flags.

## North Ingestion Checks

- [ ] `scripts/north_setup.py` completes with a new `library_id`.
- [ ] `data/north/state.json` records library and agent IDs.
- [ ] North chat on Hugin/F-11 question returns answers grounded in real uploaded PDFs.

## Acceptance Criteria

- [ ] Demo no longer depends solely on the Sprint 3 validation PDF.
- [ ] PDF drill-down can use real files from `data/curated/pdfs/` once mounted.
- [ ] `.env.local` updated with new `NORTH_LIBRARY_ID` and `NORTH_AGENT_ID` (optional if reusing agent).
