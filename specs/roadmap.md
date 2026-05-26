# EOWI Demo — Roadmap & v1 Limitations

This document captures what v1 deliberately does **not** include, and the planned path to full capability.

## v1 limitations (explicit)

### Data coverage

| Limitation | v1 state | Future plan |
|---|---|---|
| Well corpus | F-11 + 5 offsets (F-1, F-4, F-7, F-10, F-14) | Index remaining wells from [wells.yaml](../scripts/wells.yaml) (full 17-well list) |
| Field-campaign questions | Partial — agent must acknowledge coverage gaps | Full field index enables campaign-wide NPT and formation queries |
| Document types | DDR, EOWR, completion reports, formation tops | Seismic, production, WITSML, reservoir models deferred |
| Databricks at runtime | Not used — data exported locally once | Optional: pre-build indexes on Databricks (Option B acquisition) for faster refresh |

### Product & UX

| Limitation | v1 state | Future plan |
|---|---|---|
| Multi-turn refinement | Not supported ("redo excluding F-15") | Cohere memory capabilities; explicit refinement UI |
| Conversation thread UI | Latest brief prominent; prior turn collapsed optional | Full thread view (Option B session UI) |
| Well selector | Indexed wells only | Expand as corpus grows |
| Authentication | None | Basic auth if demo ships outside controlled environments |
| Self-serve demo URL | Not supported | Hosted multi-session demo for prospects |
| Open-mic / full off-script | One off-script question tolerated | Eval harness + 10 rehearsed weird questions; broader graceful handling |

### Citation & PDF

| Limitation | v1 state | Future plan |
|---|---|---|
| PDF highlight fidelity | Page + paragraph block-level bbox | Char-level highlight with precise coordinate conversion |
| Citation verification | chunk_id existence check | Semantic overlap / embedding similarity check |
| OCR quality on tables | Vision extraction; table reading order may be imperfect | Table-aware vision prompts; dedicated table parser |

### Validation

| Limitation | v1 state | Future plan |
|---|---|---|
| SME review | Internal reviewer for v1 launch | External drilling SME sign-off before first customer meeting |
| Eval suite | ~20 seed questions + harness | Expand to 50+ with SME-contributed questions |

## Future enhancements (post-v1)

### Near-term (Phase 5 stretch / v1.1)

- [ ] Char-level PDF highlight
- [ ] Full 17-well index
- [ ] Recorded canonical demo replay mode (API failure fallback)
- [ ] External drilling SME review cycle
- [ ] Bridge slide customization per buyer stack

### Medium-term

- [ ] Cohere memory integration for persistent session context
- [ ] Multi-turn refinement commands
- [ ] Cohere Compass evaluation as LanceDB+BM25 replacement
- [ ] Snowflake-backed structured store (DuckDB schema is portable)
- [ ] MCP adapters for production data sources (OpenWells, EDM, OSDU)
- [ ] Pre-build indexes on Databricks; export artifacts to local demo bundle

### Long-term

- [ ] Cross-field analysis
- [ ] WITSML time-series integration
- [ ] Production data integration
- [ ] Self-serve prospect demo URL with auth
- [ ] Multilingual query support
- [ ] Authentication / multi-tenancy

## Delivery mode roadmap

| Mode | Status |
|---|---|
| A — Live, presenter-controlled | **v1 primary** |
| B — Live, one off-script question | **v1 secondary** |
| C — Pre-recorded / async only | Roadmap (marketing enablement) |
| D — Self-serve URL | Roadmap (requires auth, hosting, stability) |

## CTO / COO influencer roadmap

v1 serves CTO and COO through the **bridge slide** and presenter script beats only. Future:

- **CTO:** Dedicated security / VPC deployment one-pager; adapter catalog with shipped MCP servers
- **COO:** ROI calculator slide; field-wide coverage metrics once full corpus indexed
