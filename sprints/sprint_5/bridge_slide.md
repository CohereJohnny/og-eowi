# EOWI Demo — Bridge Slide

## Demo (Volve)

| Agent tool | Demo data source |
|---|---|
| North Library retrieval | North Library over Volve DDRs/EOWRs |
| `get_well_header` | Local or North function tool over Volve well master |
| `get_formation_tops` | Local or North function tool over Volve stratigraphy |
| `get_offset_wells` | Local or North function tool over Volve field subset |
| Source citation lookup | North citation metadata plus local PDF/source mapping |

## Production

| Agent tool | Production adapter |
|---|---|
| North Library retrieval | OpenWells + DDR SharePoint + unstructured archive |
| `get_well_header` | EDM / corporate well master |
| `get_formation_tops` | Subsurface DB / Petrel / OSDU work product |
| `get_offset_wells` | Asset portfolio / OSDU spatial index |
| Source citation lookup | Enterprise search / document management system |

## Presenter Talk Track

"We do not need you to consolidate your data estate first. The agent gets value from what is connected today and grows from there."

## CTO Beat

- Same agent pattern, different connected repositories.
- Local demo proxy maps cleanly to a VPC or controlled enterprise deployment.
- North Libraries remove the need for a custom vector service in the pilot.

## COO Beat

- One well today, full field history tomorrow.
- Severity-rated findings turn tribal report archives into operational risk visibility.
