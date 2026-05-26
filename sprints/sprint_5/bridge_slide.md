# EOWI Demo — Bridge Slide

## Demo (Volve)

| Agent tool | Demo data source |
|---|---|
| `search_drilling_reports` | LanceDB + BM25 over Volve DDRs/EOWRs |
| `get_well_header` | DuckDB Volve well master |
| `get_formation_tops` | DuckDB Volve stratigraphy |
| `get_offset_wells` | DuckDB Volve field subset |
| `read_document_chunks` | Local curated PDF/chunk store |

## Production

| Agent tool | Production adapter |
|---|---|
| `search_drilling_reports` | OpenWells + DDR SharePoint + unstructured archive |
| `get_well_header` | EDM / corporate well master |
| `get_formation_tops` | Subsurface DB / Petrel / OSDU work product |
| `get_offset_wells` | Asset portfolio / OSDU spatial index |
| `read_document_chunks` | Enterprise search / document management system |

## Presenter Talk Track

"We do not need you to consolidate your data estate first. The agent gets value from what is connected today and grows from there."

## CTO Beat

- Same tool contracts, different adapters.
- Docker Compose v1 maps cleanly to a VPC deployment.
- No Kubernetes or exotic vector service required for the pilot.

## COO Beat

- One well today, full field history tomorrow.
- Severity-rated findings turn tribal report archives into operational risk visibility.
