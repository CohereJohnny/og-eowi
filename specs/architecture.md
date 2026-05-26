# EOWI Demo — System Architecture

System design for the End-of-Well Intelligence demo: acquisition, ingestion, retrieval, agent loop, and streaming.

See [techstack.md](techstack.md) · [datamodel.md](datamodel.md) · [uiux.md](uiux.md)

---

## System diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          BROWSER (Next.js App)                          │
│  ┌──────────────┐  ┌──────────────────┐  ┌──────────────────────────┐  │
│  │ Chat Input   │  │ Streaming Brief  │  │ Tool-Call Timeline       │  │
│  └──────┬───────┘  └────────▲─────────┘  └──────────▲───────────────┘  │
│  ┌──────▼───────────────────┴───────────────────────┴────────────────┐ │
│  │              PDF Viewer Modal (page + highlight)                  │ │
│  └────────────────────────────▲──────────────────────────────────────┘ │
└─────────────────────────────────────────────┬───────────────────────────┘
                                              │ SSE
┌─────────────────────────────────────────────▼───────────────────────────┐
│                       AGENT SERVICE (FastAPI)                           │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  Agent Loop (~200 LOC) — Command A, tool-use, citation verify   │    │
│  └────┬───────────┬────────────┬─────────────┬───────────┬─────────┘    │
│   search_drill  get_well    get_form    get_offset   read_doc           │
│   _reports      _header     _ation_tops _wells       _chunks             │
└───────┬─────────────┬──────────────┬──────────────┬──────────┬──────────┘
        │             └──────┬───────┘              │          │
┌───────▼────┐      ┌────────▼─────────┐    ┌───────▼──────────▼────────┐
│ Hybrid     │      │ DuckDB           │    │ Local PDF store           │
│ Retrieval  │      │ wells, tops,     │    │ data/curated/pdfs/        │
│ BM25+Embed │      │ completion, docs │    └───────────────────────────┘
│ + Rerank   │      └──────────────────┘
│ LanceDB    │
└────────────┘
```

### Design principles

- **Single VM-deployable** — Docker Compose, no Kubernetes
- **Each tool has one job** — five narrow tools, no fat tools
- **Hybrid retrieval is non-negotiable** — lexical + semantic + rerank
- **Citation verification is a hard gate** — before final answer streams
- **No Databricks at runtime** — local indexes only during demo

---

## Data acquisition

### Source

Databricks Marketplace: `/Volumes/equinor_asa_volve_data_village/public/volve`

Registered access (May 2026). Fallback: [data.equinor.com](https://data.equinor.com) via azcopy.

### Export script

`scripts/fetch_volve_databricks.py`:

- Input: `scripts/wells.yaml` (v1 subset: F-11 + 5 offsets)
- Output: `data/raw/{well_id}/...` preserving source path metadata
- Idempotent: skip files with matching size + hash
- Log failures; never abort batch

### Folder mapping

| Databricks | Purpose |
|---|---|
| `Reports/` | DDR, EOWR, completion PDFs |
| `Well_Logs/` | Formation tops |
| `Well_technical_data/` | Headers, completion |

### Parallel dev strategy (Week 0)

While export runs, build agent/UI against **mock chunks** (hand-crafted or sample extracts). Swap real index when ingestion completes.

---

## Ingestion pipeline

```
raw PDFs → text + layout extraction → section parsing → chunking → enrichment → embedding → indexing
```

Each stage: separate script, idempotent, checkpointed, output persisted to disk.

### Stage 1: Text + layout extraction

**Path selection (automatic per document):**

1. **Native text PDF** → `pdfplumber` (primary) — preserves char bboxes, page numbers, layout blocks
2. **Image/scan PDF** → **Command A Plus vision** (`command-a-plus-05-2026`) — batch ingestion only

**Vision extraction flow:**

```
PDF page → render to image → Command A Plus vision prompt → structured text + layout blocks
```

Vision prompt returns page text and block bboxes equivalent to pdfplumber output schema. Store with `extraction_method='vision'`, `quality_flag='vision_extracted'`.

**Fallback:** PyMuPDF for simple text PDFs if pdfplumber fails.

**Output per document** (`data/extracted/{doc_id}.json`):

```json
{
  "doc_id": "...",
  "extraction_method": "pdfplumber | vision",
  "pages": [
    {
      "page_no": 1,
      "text": "...",
      "char_bboxes": [["c", x0, y0, x1, y1]],
      "layout_blocks": [{"bbox": [], "text": "...", "type": "heading|paragraph|table"}]
    }
  ]
}
```

**Spike (day one):** Prototype bbox coordinate conversion for PDF viewer — see [uiux.md](uiux.md).

### Stage 2: Section parsing

DDR sections:

```python
DDR_SECTIONS = [
    "header", "operations_summary", "problems_encountered",
    "npt_breakdown", "next_24h_plan", "mud_properties",
    "bha_description", "depth_progress", "personnel_on_board",
]
```

EOWR: executive summary, drilling summary, formations encountered, completion summary, NPT analysis, lessons learned.

Parsing: heading regex + layout heuristics. On failure → whole-page chunks with `quality_flag='partial'`.

### Stage 3: Chunking

~500 tokens, ~50 token overlap, sentence boundaries, never split mid-table.

`section_path` example: `"DDR 2008-04-15 > Problems Encountered"`

### Stage 4: Enrichment

Regex extract: depth ranges, NPT codes, date references → chunk metadata for tool filters.

### Stage 5: Embedding

Cohere Embed v4, `input_type=search_document`, text = `{section_path}\n\n{chunk_text}`

### Stage 6: Indexing

Write LanceDB embeddings, build BM25, persist DuckDB → `data/index/`

### Ingestion success criteria

- [ ] Every v1 demo well has ≥1 DDR and ≥1 EOWR indexed
- [ ] Spot-check 20 chunks: section_path correct, text clean, pages correct
- [ ] "stuck pipe" query returns "Problems Encountered" sections
- [ ] Citation roundtrip: chunk_id → PDF page + bbox

---

## Retrieval pipeline

```
query → parallel(BM25 top-50, Embed top-50)
      → merge + dedupe (top 80)
      → Rerank 3.5 (top 8)
      → return to agent with metadata
```

Prefilter LanceDB on `well_id` and `doc_type` when tool params provide them.

**Why all three stages:** BM25 catches identifiers; embeddings catch semantics; rerank makes citations precise.

---

## Agent architecture

### Model

Primary: `command-a-03-2025` (or latest Command A). Fallback: `command-r-plus-08-2024`.

### Tool definitions

Five tools — schemas unchanged from [eowi-demo-spec.md](eowi-demo-spec.md) §8.2:

1. `search_drilling_reports` — hybrid retrieval over narrative reports
2. `get_well_header` — DuckDB well master
3. `get_formation_tops` — DuckDB stratigraphy
4. `get_offset_wells` — formation overlap query
5. `read_document_chunks` — fetch by chunk_id

### System prompt

Canonical prompt enforces:

- Ground every claim in retrieved evidence
- Cite at chunk level `[chunk_id]`
- Search before answering operational questions
- Structured tools before search where applicable
- Explicit confidence labels
- Distinguish engineering judgment from quotation
- Structured output template (Summary, Key Findings, Caveats, Follow-ups)
- Precise drilling vocabulary; no marketing language

Full text: [eowi-demo-spec.md](eowi-demo-spec.md) §8.3 (unchanged).

### Agent loop

```
user query → chat with tools → stream thinking
  → if tool_calls: execute, cache chunks, stream timeline
  → if no tool_calls: verify citations
      → if ok: stream final
      → if fail: correction pass (internal, max 8 iterations)
```

**Session continuity:** `messages[]` persists within browser session for Q1→Q2 demo. No refinement UI in v1.

Future: Cohere memory capabilities — see [roadmap.md](roadmap.md).

### Citation verification (v1)

1. Extract `[chunk_id]` markers from answer
2. Verify each id exists in retrieved chunk cache
3. Verify each id exists in database
4. On failure → force correction pass (never shown to user)

v2 stretch: semantic overlap check between claim and chunk text.

---

## Streaming (backend → frontend)

SSE event types:

| Type | Payload |
|---|---|
| `thinking` | Model reasoning text |
| `tool_call` | name, params |
| `tool_result` | name, summary |
| `final` | verified brief text |
| `warning` | max iterations exceeded |

Next.js API route proxies SSE to browser. See [uiux.md](uiux.md).

---

## Project structure

```
og-eowi/
├── docker-compose.yml
├── data/                    # gitignored
├── scripts/
│   ├── fetch_volve_databricks.py
│   ├── extract_text.py      # pdfplumber + vision path
│   ├── parse_sections.py
│   ├── chunk_and_enrich.py
│   ├── embed_and_index.py
│   ├── load_structured.py
│   └── wells.yaml
├── backend/
│   └── app/                 # FastAPI: agent, tools, retrieval, verification
├── frontend/                # Next.js: UI, SSE proxy, PDF viewer
└── eval/
    └── questions.yaml
```

---

## Build phases

| Phase | Week | Deliverable |
|---|---|---|
| 1 — Data foundation | 1 | Export, curation, extraction for F-11 |
| 2 — Indexing + retrieval | 1.5 | Indexes populated; CLI retrieve works |
| 3 — Agent + verification | 2 | Five tools, agent loop, citation verify |
| 4 — UI | 2.5–3.5 | Streaming, chips, PDF viewer, timeline |
| 5 — Polish + eval | 4 | Eval harness, dry runs, recorded fallback |

See [prd.md](prd.md) success criteria and [demoguide.md](demoguide.md) rehearsal checklist.
