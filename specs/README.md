# End-of-Well Intelligence (EOWI) — Specifications

This directory contains the buildable specification for the Cohere-powered End-of-Well Intelligence demo on the Equinor Volve dataset.

## Document hierarchy

| Document | Purpose |
|---|---|
| [prd.md](prd.md) | Product requirements, goals, functional requirements, success criteria |
| [personas.md](personas.md) | Primary and secondary audience personas |
| [userstories.md](userstories.md) | User stories with acceptance criteria, grouped by epic |
| [demoguide.md](demoguide.md) | Canonical demo script and rehearsal checklist |
| [techstack.md](techstack.md) | Technology choices and rejected alternatives |
| [architecture.md](architecture.md) | System design, agent loop, retrieval, ingestion |
| [datamodel.md](datamodel.md) | DuckDB, LanceDB, BM25, and document schemas |
| [uiux.md](uiux.md) | Layout, streaming, citation chips, PDF viewer |
| [roadmap.md](roadmap.md) | v1 limitations, deferred features, future enhancements |

## Grill session decisions (May 2026)

These decisions were resolved in a structured review of [eowi-demo-spec.md](eowi-demo-spec.md):

- **Primary audience:** Drilling VP / Head of Drilling Operations
- **Secondary audiences:** CTO and COO (Pattern A — VP-first live demo; opening + bridge slide nods)
- **Session model:** Sequential follow-up questions in one session (backend chat history); no refinement UI in v1
- **Delivery mode:** Live presenter-controlled primary; one off-script question tolerated; self-serve URL deferred
- **Data corpus v1:** F-11 + 5 offset wells; full 17-well field on roadmap
- **Stack:** Python FastAPI backend + Next.js frontend, Docker Compose
- **Data acquisition:** Databricks Marketplace export → local pipeline (no Databricks at runtime)
- **Citations UI:** Page + block-level highlight v1; char-level highlight stretch
- **SME review:** Internal sign-off for v1 launch; external drilling SME before first customer meeting
- **OCR / scan PDFs:** Command A Plus vision extraction at ingestion time (batch); pdfplumber for native text PDFs

## Legacy monolith

[eowi-demo-spec.md](eowi-demo-spec.md) remains as the original comprehensive specification. The split documents above are the **authoritative source** for v1 build decisions. Where they diverge, the split docs win.
