# Sprint 3.5 Updates

## 2026-05-27

- Sprint 3 archived to `sprints/archive/sprint_3/` with report and completed task list.
- Added `scripts/curate_volve_pdfs.py` to build `data/curated/manifest.json` and copy PDFs from `data/raw/` or export manifest.
- **Blocker:** Databricks volume is not mounted on this machine (`/Volumes/equinor_asa_volve_data_village/public/volve`). Run export from a Databricks workspace with the Volve volume attached, or pass `--source` to a local copy of the volume.

### Export (when volume is available)

```bash
uv run python scripts/fetch_volve_databricks.py
```

### Curation

```bash
uv run python scripts/curate_volve_pdfs.py
```

### North Library rebuild

```bash
uv run python scripts/north_setup.py
```

Then set `NORTH_LIBRARY_ID` and `NORTH_AGENT_ID` in `.env.local` from `data/north/state.json`.
