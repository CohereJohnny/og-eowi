# End-of-Well Intelligence Agent — Demo Specification

**Version:** 1.0 (monolith — see split specs below)  
**Purpose:** Buildable specification for a Cohere-powered agentic demo using the Equinor Volve dataset, targeting oil & gas executive audiences (Drilling VP, COO, CTO, subsurface leadership).  
**Build mode:** Vibe-code with Cursor (or equivalent), targeting a working demo in 3–4 weeks solo.

> **Authoritative v1 specs:** This document is the original comprehensive specification. Build decisions resolved in the May 2026 grill session are captured in the [split specification hierarchy](README.md): [prd.md](prd.md), [personas.md](personas.md), [userstories.md](userstories.md), [demoguide.md](demoguide.md), [techstack.md](techstack.md), [architecture.md](architecture.md), [datamodel.md](datamodel.md), [uiux.md](uiux.md), [roadmap.md](roadmap.md). **Where they diverge, the split docs win.**

---

## 1. Executive Summary

### 1.1 What we're building

A single-purpose agentic application that lets a user ask natural-language questions about a real North Sea well (Volve 15/9-F-11 and offset wells) and receive **grounded, cited, structured engineering briefings** drawn from the actual daily drilling reports (DDRs), end-of-well report (EOWR), formation tops, completion records, and well headers in the Volve open dataset.

The demo's primary audience is an O&G executive who must be convinced in under 5 minutes that agentic AI can compress the work of a drilling engineering team while producing audit-quality output their QA process would trust.

### 1.2 What it must do on stage

1. Accept a free-form question phrased the way a drilling engineer would phrase it.
2. Visibly plan its approach (tool-call trace streamed to a side panel).
3. Retrieve from a corpus of real Volve documents using hybrid search (BM25 + Embed v4) followed by Rerank 3.5.
4. Synthesize a structured engineering brief with **paragraph-level citations** to the actual source PDFs.
5. Render citations as clickable chips that open the source PDF to the cited page with the relevant text highlighted.
6. Explicitly surface uncertainty when evidence is thin or absent.
7. Produce output formatted as engineering work product (sections, severity ratings, evidence basis), not as a chatbot reply.

### 1.3 What it must NOT do

- Use any data not in the Volve open dataset (no synthetic fabrications).
- Hallucinate citations — every citation must resolve to a real chunk containing the grounding substring.
- Use classical-ML wrappers (anomaly detection, similarity scoring) as the headline value. Reasoning over text is the value.
- Depend on infrastructure the audience can't extrapolate to their own stack (no exotic vector DBs, no proprietary frameworks).

---

## 2. Demo Narrative (the script the build must support)

This is the canonical demo flow. Every architectural decision should be evaluated against whether it makes this flow more credible.

### 2.1 Opening (presenter speaks, no UI yet) — 30 seconds

> "Your senior drilling superintendent retires next year. He's drilled 200 wells. Every lesson he's learned is in his head and in 40,000 PDFs nobody reads end-to-end. When the next well kicks off, what does your team actually do with those 40,000 reports?"

### 2.2 Framing the data (10 seconds)

> "What you're about to see runs on the Equinor Volve dataset — a real, complete North Sea well dataset Equinor released for research. Same document formats, same engineering vocabulary, same operational reality as your wells."

### 2.3 First question — 90 seconds

Presenter types in the UI:
> *"I'm planning a new well in the Hugin Formation. What are the three things I most need to know from how 15/9-F-11 was drilled?"*

**On screen:**
- Tool-call timeline streams in side panel: `search_drilling_reports(...)`, `get_formation_tops(...)`, `get_well_header(...)`, `rerank_results(...)`, `read_document_chunks(...)`.
- Main panel streams the agent's reasoning summary, then renders the final brief.
- Final output: three-point briefing, each point with a severity tag, an evidence-basis section, and 2–4 citation chips.

### 2.4 The aha question — 60 seconds

Presenter:
> *"Of those issues, which were avoidable through better well design vs. better execution?"*

This question is engineered to defeat the "this is just XGBoost" objection. Pattern-matching can't answer it. The agent must:
- Re-read evidence with a different framing
- Reason causally
- Make a defensible judgment
- Cite evidence for the judgment

**On screen:** Updated brief with a "Design vs. Execution" classification per issue, each with a confidence level and rationale.

### 2.5 Citation drill-down — 30 seconds

Presenter clicks a citation chip. A PDF viewer opens to the cited DDR page with the supporting sentence highlighted. Closes it. Clicks another. Same precision.

> "Every claim is one click from the source. Your QA process already trusts these documents — now they're queryable."

### 2.6 The bridge (one slide) — 60 seconds

Architecture slide. Left: the demo as shown. Right: same agent, same tools, with adapters relabeled — `search_drilling_reports` → "OpenWells + your DDR SharePoint + your unstructured archive," `get_well_header` → "your EDM / corporate well master," etc. Cohere stack identical; data connectors swap.

> "We don't need you to consolidate your data estate first. The agent gets value from what's connected today and grows from there."

### 2.7 Close — 15 seconds

> "One well today. Same agent across your full field history tomorrow. Your new drilling engineer has your retiring superintendent's brain available 24/7, with citations to the source documents your QA process already trusts."

**Total demo runtime target: 4 minutes 15 seconds.**

---

## 3. System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          BROWSER (Next.js App)                          │
│  ┌──────────────┐  ┌──────────────────┐  ┌──────────────────────────┐  │
│  │ Chat Input   │  │ Streaming Brief  │  │ Tool-Call Timeline       │  │
│  │              │  │ + Citation Chips │  │ (side panel)             │  │
│  └──────┬───────┘  └────────▲─────────┘  └──────────▲───────────────┘  │
│         │                   │                       │                  │
│         │                   │                       │                  │
│  ┌──────▼───────────────────┴───────────────────────┴────────────────┐ │
│  │              PDF Viewer Modal (page + highlight)                  │ │
│  └────────────────────────────▲──────────────────────────────────────┘ │
└─────────────────────────────────────────────┬───────────────────────────┘
                                              │ SSE stream
                                              │
┌─────────────────────────────────────────────▼───────────────────────────┐
│                       AGENT SERVICE (FastAPI, Python)                   │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │            Agent Loop (~200 LOC, hand-rolled)                   │    │
│  │  - System prompt enforces structured output + citation rules    │    │
│  │  - Cohere Command A / Command A+ via tool-use API               │    │
│  │  - Citation verification pass before final answer ships          │    │
│  └────┬───────────┬────────────┬─────────────┬───────────┬─────────┘    │
│       │           │            │             │           │              │
│   ┌───▼───┐  ┌────▼────┐  ┌────▼────┐  ┌─────▼────┐ ┌────▼─────┐         │
│   │search_│  │get_well_│  │get_form │  │get_offset│ │read_doc_  │        │
│   │drill_ │  │header   │  │ation_   │  │_wells    │ │chunks     │        │
│   │reports│  │         │  │tops     │  │          │ │           │        │
│   └───┬───┘  └────┬────┘  └────┬────┘  └─────┬────┘ └────┬──────┘        │
└───────┼───────────┼────────────┼─────────────┼───────────┼───────────────┘
        │           │            │             │           │
        │           └────────────┴─────────────┘           │
        │                    │                             │
        │                    │                             │
┌───────▼────┐      ┌────────▼─────────┐         ┌────────▼────────┐
│ Hybrid     │      │ DuckDB (or       │         │ Object store    │
│ Retrieval  │      │ SQLite)          │         │ (local FS)      │
│  - BM25    │      │  - well_master   │         │  - source PDFs  │
│  - Embed v4│      │  - formation_    │         │    (indexed by  │
│  - Rerank  │      │    tops          │         │    doc_id)      │
│  - LanceDB │      │  - completion_   │         │                 │
│            │      │    record        │         │                 │
└────────────┘      └──────────────────┘         └─────────────────┘
```

### 3.1 Why this shape

- **Single VM-deployable.** Whole thing runs on one workstation or one cloud VM for the demo. No Kubernetes, no managed services.
- **Each tool has one job.** Agent reasoning quality drops when tools overlap or do too much. Five narrow tools beat one fat tool.
- **Hybrid retrieval is non-negotiable.** Drilling reports are full of well-specific identifiers (depth intervals, BHA component numbers, mud chemical names) where lexical match matters as much as semantic.
- **Citation verification is a hard gate.** Before the agent's response is streamed to the user, every citation is programmatically checked. If a cited chunk doesn't contain the substring grounding the claim, the agent is forced to revise.

---

## 4. Data Acquisition Strategy

### 4.1 Source

Equinor Volve dataset, registered access via [data.equinor.com](https://data.equinor.com). License: Equinor Open Data License (academic/research use permitted).

### 4.2 Subset to download

We do NOT pull the full 5 TB. Target subset: **~2–5 GB**, covering enough wells to support demo questions and offset-well reasoning.

**Wells in scope:**
- 15/9-F-1 A, B, C
- 15/9-F-4
- 15/9-F-5
- 15/9-F-7
- 15/9-F-9 A
- 15/9-F-10
- 15/9-F-11 A, B, T2 (primary demo well)
- 15/9-F-12
- 15/9-F-14
- 15/9-F-15 A, B, C, D

**Folders to pull per well:**
| Volve folder | What we want | Rough size |
|---|---|---|
| `WELL_REPORTS/` | Daily Drilling Reports (PDF), End-of-Well Reports (PDF), Completion Reports (PDF) | ~1.5 GB |
| `WELL_LOGS/` | Formation tops files, header logs (LAS) | ~500 MB |
| `WELL_HEADERS/` | Spud date, TD, KB elevation, surface coords, well name aliases | ~50 MB |

**Folders to skip for v1:**
- `SEISMIC/` — SEGY not useful for this demo
- `GEOPHYSICAL_INTERPRETATIONS/` — defer
- `RESERVOIR_MODEL/` — defer (Eclipse decks)
- `GEOLOGICAL_INTERPRETATIONS/` — partial pull only if narrative reports are present
- `PRODUCTION/` — defer (not on the critical path for an end-of-well brief)
- `PETROPHYSICAL_INTERPRETATIONS/` — defer

### 4.3 Download mechanics

Build a one-shot Python script (`scripts/fetch_volve.py`) using `azcopy` or Azure SDK. Inputs: `wells.yaml` listing wells and folder patterns. Outputs: `data/raw/{well_id}/{folder}/...` preserving Equinor's directory structure.

Idempotency: skip files already on disk with matching size + hash. Log failures, never abort the batch.

### 4.4 Curation pass

After raw download, manual review of **20–30 documents** to:
1. Confirm PDFs are text-extractable (some Volve scans are image-only — flag these for OCR or exclude).
2. Identify the canonical EOWR for each demo well.
3. Validate DDR coverage (we want continuous daily coverage for at least one well).

Output: `data/curated/manifest.json` listing every document with `doc_id`, `well_id`, `doc_type`, `date_range`, `extraction_method`, `quality_flag`.

---

## 5. Data Model

### 5.1 Structured store (DuckDB)

DuckDB is chosen over Postgres for the demo because:
- Zero-install, embeddable, single-file
- Excellent for analytic queries the agent will run
- Trivial to migrate to Postgres/Snowflake later — the SQL is portable

```sql
-- 5.1.1 Wells
CREATE TABLE wells (
    well_id          TEXT PRIMARY KEY,         -- e.g. '15/9-F-11'
    well_name        TEXT NOT NULL,
    field            TEXT NOT NULL,            -- 'Volve'
    operator         TEXT,                     -- 'Equinor (Statoil)'
    spud_date        DATE,
    td_date          DATE,
    kb_elevation_m   DOUBLE,
    td_md_m          DOUBLE,                   -- measured depth at TD
    td_tvd_m         DOUBLE,                   -- true vertical depth at TD
    surface_lat      DOUBLE,
    surface_lon      DOUBLE,
    well_purpose     TEXT,                     -- 'production', 'injection', 'appraisal'
    well_status      TEXT,
    parent_well_id   TEXT,                     -- for sidetracks/laterals
    aliases          TEXT[]                    -- array of alternate names
);

-- 5.1.2 Formation tops
CREATE TABLE formation_tops (
    well_id          TEXT NOT NULL,
    formation_name   TEXT NOT NULL,            -- 'Hugin', 'Heather', 'Skagerrak', ...
    top_md_m         DOUBLE NOT NULL,
    top_tvd_m        DOUBLE,
    base_md_m        DOUBLE,
    lithology        TEXT,                     -- 'sandstone', 'shale', ...
    interpreted_by   TEXT,
    interpretation_date DATE,
    source_doc_id    TEXT,                     -- FK to documents
    PRIMARY KEY (well_id, formation_name, top_md_m)
);

-- 5.1.3 Completion record (simplified — flatten what's available)
CREATE TABLE completion_record (
    well_id          TEXT NOT NULL,
    component_seq    INTEGER NOT NULL,
    component_type   TEXT NOT NULL,            -- 'casing', 'liner', 'screen', 'packer', 'tubing'
    od_inches        DOUBLE,
    id_inches        DOUBLE,
    top_md_m         DOUBLE,
    bottom_md_m      DOUBLE,
    grade            TEXT,                     -- 'L80', 'P110', ...
    weight_lbft      DOUBLE,
    notes            TEXT,
    source_doc_id    TEXT,
    PRIMARY KEY (well_id, component_seq)
);

-- 5.1.4 Documents (the canonical registry)
CREATE TABLE documents (
    doc_id           TEXT PRIMARY KEY,         -- deterministic hash of path
    well_id          TEXT,                     -- nullable; some docs span wells
    doc_type         TEXT NOT NULL,            -- 'DDR', 'EOWR', 'COMPLETION_RPT', 'GEO_RPT'
    title            TEXT,
    doc_date         DATE,
    date_range_start DATE,                     -- for multi-day docs
    date_range_end   DATE,
    source_path      TEXT NOT NULL,            -- relative to data/raw/
    page_count       INTEGER,
    extraction_method TEXT,                    -- 'pdfplumber', 'pymupdf', 'ocr'
    quality_flag     TEXT                      -- 'good', 'partial', 'ocr_required'
);

-- 5.1.5 Document chunks (the unit of retrieval and citation)
CREATE TABLE chunks (
    chunk_id         TEXT PRIMARY KEY,         -- deterministic: {doc_id}::{section}::{seq}
    doc_id           TEXT NOT NULL REFERENCES documents(doc_id),
    well_id          TEXT,                     -- denormalized for filter speed
    doc_type         TEXT NOT NULL,
    chunk_seq        INTEGER NOT NULL,
    page_start       INTEGER NOT NULL,
    page_end         INTEGER NOT NULL,
    section_path     TEXT,                     -- e.g. 'Day 23 > Problems Encountered'
    depth_md_start_m DOUBLE,                   -- if section references a depth range
    depth_md_end_m   DOUBLE,
    chunk_text       TEXT NOT NULL,
    char_offset_in_page INTEGER,               -- for highlight reconstruction
    token_count      INTEGER
);

CREATE INDEX idx_chunks_well ON chunks(well_id);
CREATE INDEX idx_chunks_doctype ON chunks(doc_type);
CREATE INDEX idx_chunks_doc ON chunks(doc_id);
```

### 5.2 Vector store (LanceDB)

Single LanceDB table, embedded alongside the app. No separate service.

```python
# Schema (LanceDB / PyArrow)
schema = {
    "chunk_id":      "string",          # FK to chunks.chunk_id
    "well_id":       "string",          # for prefiltered search
    "doc_type":      "string",          # for prefiltered search
    "embedding":     "vector(1024)",    # Cohere Embed v4 dim
    "text":          "string",          # denormalized for inspection only
}
```

- Embeddings: `embed-v4.0`, input_type=`search_document` for indexing, `search_query` for retrieval.
- Index: HNSW (LanceDB default).
- Prefilter on `well_id` and `doc_type` when the agent's tool call provides them.

### 5.3 BM25 store

Use `bm25s` (lightweight, in-process Python). Index built over the same `chunks.chunk_text` corpus, tokenized with a custom regex that preserves drilling identifiers (e.g., `12-1/4"`, `9-5/8"`, `2,950m`, `15/9-F-11`).

```python
TOKEN_PATTERN = r"""(?x)
    \d+(?:\.\d+)?    # numbers including decimals
    | \d+/\d+        # fractions like 9/5
    | \d+-\d+        # ranges
    | \"             # inch marks
    | [A-Za-z]+(?:-[A-Za-z0-9]+)*   # words and hyphenated compounds
"""
```

### 5.4 Source PDF store

Plain filesystem: `data/curated/pdfs/{doc_id}.pdf`. The PDF viewer reads these directly. No transformation — preserve the original document the user clicks through to.

---

## 6. Ingestion Pipeline

### 6.1 Pipeline stages

```
raw PDFs → text + layout extraction → section parsing → chunking → enrichment → embedding → indexing
```

Each stage is a separate script, idempotent, with checkpointing. Re-runnable per stage. Output of each stage is persisted to disk.

### 6.2 Stage 1: Text + layout extraction

**Primary library:** `pdfplumber` (preserves layout, page numbers, character bboxes — essential for highlight reconstruction later).
**Fallback for image PDFs:** `ocrmypdf` (Tesseract) — but flag these documents with `quality_flag='ocr_required'` and exclude from v1 corpus.

Output per document: a JSON file with:
```json
{
  "doc_id": "...",
  "pages": [
    {
      "page_no": 1,
      "text": "...",
      "char_bboxes": [[char, x0, y0, x1, y1], ...],
      "layout_blocks": [{"bbox": [...], "text": "...", "type": "heading|paragraph|table"}, ...]
    }
  ]
}
```

The `char_bboxes` are what makes page-accurate highlighting possible later. Don't skip this.

### 6.3 Stage 2: Section parsing (the part that determines retrieval quality)

DDRs follow a predictable structure: header (well, date, day no., depth in/out), operational summary, problems encountered, next 24-hour plan, NPT codes, mud properties, BHA description, personnel.

**Build a DDR parser that extracts sections by name.** This is worth manual effort — generic chunking destroys retrieval quality for these documents.

```python
DDR_SECTIONS = [
    "header",
    "operations_summary",       # narrative of the day's work
    "problems_encountered",     # the gold for our agent
    "npt_breakdown",
    "next_24h_plan",
    "mud_properties",
    "bha_description",
    "depth_progress",
    "personnel_on_board",
]
```

For each DDR, the parser produces a dict mapping section name → text + page range. Use a combination of:
- Heading regex matches (`r"Problems\s+Encountered|Operational\s+Summary"`)
- Vertical position heuristics from layout blocks
- A small handful of well-specific quirks discovered during curation

For EOWRs, similar approach with different sections (executive summary, drilling summary, formations encountered, completion summary, NPT analysis, lessons learned).

If parsing fails for a section, fall back to whole-page chunks for that page rather than discarding.

### 6.4 Stage 3: Chunking

Within each parsed section, chunk to **~500 tokens** with **~50-token overlap**. Respect sentence boundaries. Never split mid-table.

`section_path` field captures the parsing context: `"DDR 2008-04-15 > Problems Encountered"` or `"EOWR > Lessons Learned > Drilling"`. This is fed into embeddings as a prefix and shown to the agent on retrieval — it dramatically improves rerank precision.

### 6.5 Stage 4: Enrichment

For each chunk, extract and store:
- `depth_md_start_m`, `depth_md_end_m` if a depth range appears in the chunk (regex over patterns like `2,950m MD`, `3,120 m`).
- Operation codes / NPT codes if present (regex over Equinor's NPT taxonomy).
- Date references.

This metadata is what the agent's tool filters operate on.

### 6.6 Stage 5: Embedding

Batch-embed chunks via Cohere Embed v4 with `input_type="search_document"`. The text fed to embed is:
```
{section_path}\n\n{chunk_text}
```
Section path as prefix substantially improves retrieval for documents where the same vocabulary appears in different operational contexts.

### 6.7 Stage 6: Indexing

Write embeddings to LanceDB. Build BM25 index. Persist both to `data/index/`.

### 6.8 Ingestion success criteria

Before declaring ingestion complete, run a checklist:
- [ ] Every demo well has at least one DDR and one EOWR in the index.
- [ ] Spot-check 20 random chunks: section_path is correct, text is clean, page references are correct.
- [ ] Sample queries return chunks with appropriate `section_path` (e.g., "stuck pipe" returns chunks from "Problems Encountered" sections).
- [ ] Citation verification roundtrip works: given any chunk_id, can retrieve PDF page + bbox for highlight.

---

## 7. Retrieval Pipeline

### 7.1 Hybrid retrieval flow

```
query → parallel(BM25 top-50, Embed top-50)
      → merge + dedupe (top 80)
      → Rerank 3.5 (returns top 8)
      → return to agent with full metadata
```

### 7.2 Implementation

```python
async def hybrid_retrieve(
    query: str,
    well_filter: list[str] | None = None,
    doc_type_filter: list[str] | None = None,
    top_k: int = 8,
) -> list[Chunk]:
    # 1. BM25 — top 50, with filters applied post-search
    bm25_hits = bm25_index.search(query, k=200)
    bm25_hits = apply_filters(bm25_hits, well_filter, doc_type_filter)[:50]

    # 2. Embedding search — top 50, with metadata prefilter
    query_emb = cohere.embed(
        texts=[query],
        model="embed-v4.0",
        input_type="search_query",
    ).embeddings[0]
    vec_hits = lance_table.search(query_emb).where(
        build_lance_filter(well_filter, doc_type_filter)
    ).limit(50).to_list()

    # 3. Merge + dedupe by chunk_id
    merged = dedupe_by_id(bm25_hits + vec_hits)[:80]

    # 4. Rerank
    rerank_resp = cohere.rerank(
        model="rerank-v3.5",
        query=query,
        documents=[f"{c.section_path}\n\n{c.text}" for c in merged],
        top_n=top_k,
    )
    return [merged[r.index] for r in rerank_resp.results]
```

### 7.3 Why each stage matters

- **BM25** catches exact identifier matches the embedding model glosses over (specific well numbers, BHA component IDs, NPT codes).
- **Embeddings** catch semantic matches (e.g., "differential sticking" finds chunks discussing "pack-off" or "tight hole").
- **Rerank** is what makes citations precise. The merged top-80 contains many marginally-relevant chunks; rerank promotes the ones that actually answer the query.

Don't skip any of the three. Without rerank specifically, the citation chips degrade from "click and the right paragraph is highlighted" to "click and the cited section is sort of relevant" — and that gap is where executive trust evaporates.

---

## 8. Agent Architecture

### 8.1 Model selection

**Primary:** `command-a-03-2025` (or the latest Command A available at build time).
**Fallback for cost-controlled runs:** `command-r-plus-08-2024`.

Why Command A:
- Tool-use is first-class and well-tuned
- Strong on grounded RAG output (citations, structured responses)
- Cohere-native, which is the right story to tell

### 8.2 Tool definitions (exact schemas)

```python
TOOLS = [
    {
        "name": "search_drilling_reports",
        "description": (
            "Search across daily drilling reports (DDRs), end-of-well reports (EOWRs), "
            "and completion reports for content matching a query. Use this for any "
            "question requiring narrative content about what happened during drilling, "
            "problems encountered, decisions made, or lessons learned. Returns ranked "
            "chunks with citations."
        ),
        "parameter_definitions": {
            "query": {
                "description": "Natural-language search query. Use specific drilling terms.",
                "type": "str",
                "required": True,
            },
            "well_id": {
                "description": (
                    "Restrict search to a specific well, e.g. '15/9-F-11'. Omit to "
                    "search across all wells."
                ),
                "type": "str",
                "required": False,
            },
            "doc_type": {
                "description": (
                    "Filter to a specific report type. One of: 'DDR', 'EOWR', "
                    "'COMPLETION_RPT', 'GEO_RPT'. Omit for all types."
                ),
                "type": "str",
                "required": False,
            },
        },
    },
    {
        "name": "get_well_header",
        "description": (
            "Retrieve structured header data for a well: spud date, TD, KB elevation, "
            "surface coordinates, purpose, status, parent well."
        ),
        "parameter_definitions": {
            "well_id": {"description": "Well identifier", "type": "str", "required": True},
        },
    },
    {
        "name": "get_formation_tops",
        "description": (
            "Retrieve all formation tops for a well with measured depth, true vertical "
            "depth, and lithology where available."
        ),
        "parameter_definitions": {
            "well_id": {"description": "Well identifier", "type": "str", "required": True},
        },
    },
    {
        "name": "get_offset_wells",
        "description": (
            "Find wells that share a target formation with a given well. Returns wells "
            "ordered by formation overlap. Use when the user asks about analogous wells, "
            "comparing problems across wells, or lessons from similar wells."
        ),
        "parameter_definitions": {
            "reference_well_id": {"description": "Well to find offsets for", "type": "str", "required": True},
            "formation": {
                "description": "Optional: restrict to wells with this formation in their stratigraphy",
                "type": "str",
                "required": False,
            },
            "limit": {"description": "Max offset wells to return (default 5)", "type": "int", "required": False},
        },
    },
    {
        "name": "read_document_chunks",
        "description": (
            "Retrieve full text for specific chunks by chunk_id. Use this when you need "
            "to read additional context around a chunk you've already retrieved, or to "
            "confirm a citation before including it in your final answer."
        ),
        "parameter_definitions": {
            "chunk_ids": {
                "description": "List of chunk_ids to retrieve",
                "type": "list[str]",
                "required": True,
            },
        },
    },
]
```

### 8.3 System prompt (canonical version)

```
You are the End-of-Well Intelligence Agent — a drilling and subsurface engineering
assistant for E&P operators. You answer questions by retrieving evidence from real
drilling reports and producing structured engineering briefings.

## Your operating rules

1. **Ground every factual claim in retrieved evidence.** Never assert an operational
   fact unless you have retrieved a chunk that supports it.

2. **Cite at the chunk level.** Every factual claim in your final answer must be
   followed by one or more citation markers of the form [chunk_id]. Use the exact
   chunk_id values returned by your tools. Never invent chunk_ids.

3. **Search before answering.** For any question about what happened on a well,
   what problems were encountered, or what was recommended, your first action is
   ALWAYS a search_drilling_reports call. Do not answer from prior knowledge.

4. **Use structured tools before search where applicable.** If the user asks about
   formation depths, well coordinates, or completion design, call the relevant
   structured tool first. These are authoritative.

5. **Acknowledge uncertainty.** If retrieved evidence is thin, contradictory, or
   absent, say so explicitly. Use one of:
   - "High confidence — multiple consistent sources"
   - "Medium confidence — single source"
   - "Low confidence — indirect evidence only"
   - "Insufficient evidence — the available reports do not cover this"

6. **Distinguish judgment from quotation.** When you are making an engineering
   judgment (e.g., classifying issues as design vs. execution), label it as
   "Engineering judgment based on:" and list the supporting evidence.

## Output format

Your final answer must be structured. Use this template, omitting sections that
don't apply:

---

**Summary**
One-paragraph answer to the user's actual question.

**Key findings**

1. **[Finding title]** — Severity: [High/Medium/Low] — Confidence: [High/Medium/Low]
   - What happened: [factual description] [chunk_id]
   - Why it matters: [implication for the user's question]
   - Evidence basis: [list of chunk_ids supporting this finding]

2. ...

**Caveats and uncertainty**
[Anything the available evidence does not address; anything contradictory.]

**Suggested follow-up questions**
[Two or three questions the user might want to ask next.]

---

## Domain vocabulary

Always use precise drilling and subsurface terminology. Examples of correct usage:
- "differential sticking in the Hugin Formation at 2,950m MD"
  NOT "potential well problem at depth"
- "ECD exceeded the fracture gradient at the 12-1/4 inch section TD"
  NOT "the pressure was too high"
- "BHA #4 with PDC bit on a rotary steerable"
  NOT "the drilling assembly used"

If you do not know a domain term, say so rather than approximating.

## What you must never do

- Never invent well names, depths, formations, or events not in retrieved evidence.
- Never produce citations that don't exist or that don't support the claim they're attached to.
- Never apologize for lacking information — state it factually and suggest a next step.
- Never use marketing language. No "exciting," "leverage," "robust," "synergies."
- Never produce bullet points without a parent finding structure.
```

### 8.4 Agent loop (the actual control flow)

```python
async def run_agent(user_query: str, stream_callback):
    messages = [{"role": "user", "message": user_query}]
    max_iterations = 8
    all_retrieved_chunks = {}  # chunk_id -> Chunk

    for iteration in range(max_iterations):
        response = await cohere.chat(
            model="command-a-03-2025",
            preamble=SYSTEM_PROMPT,
            chat_history=messages[:-1],
            message=messages[-1]["message"] if messages[-1]["role"] == "user" else None,
            tools=TOOLS,
            tool_results=last_tool_results if iteration > 0 else None,
        )

        # Stream model output to UI as it arrives
        await stream_callback({"type": "thinking", "text": response.text})

        # No more tool calls → final answer
        if not response.tool_calls:
            verified = await verify_citations(response.text, all_retrieved_chunks)
            if verified.ok:
                await stream_callback({"type": "final", "text": verified.text})
                return verified
            else:
                # Citation failed verification — force a correction pass
                messages.append({
                    "role": "user",
                    "message": (
                        f"Citation verification failed for: {verified.failures}. "
                        f"Revise your answer using only verified chunks."
                    ),
                })
                continue

        # Execute tool calls
        tool_results = []
        for call in response.tool_calls:
            await stream_callback({"type": "tool_call", "name": call.name, "params": call.parameters})
            result = await execute_tool(call)
            tool_results.append({"call": call, "outputs": result})

            # Cache retrieved chunks for citation verification
            if call.name in ("search_drilling_reports", "read_document_chunks"):
                for chunk in result.get("chunks", []):
                    all_retrieved_chunks[chunk["chunk_id"]] = chunk

            await stream_callback({"type": "tool_result", "name": call.name, "summary": result.get("summary")})

        messages.append({"role": "chatbot", "message": response.text})
        last_tool_results = tool_results

    # Max iterations exceeded — return what we have with a flag
    await stream_callback({"type": "warning", "text": "Reached max reasoning iterations"})
    return {"text": response.text, "incomplete": True}
```

### 8.5 Citation verification (the unglamorous critical piece)

```python
def verify_citations(answer_text: str, available_chunks: dict[str, Chunk]) -> VerificationResult:
    # Extract all [chunk_id] markers from the answer
    cited_ids = re.findall(r"\[([^\]]+)\]", answer_text)
    failures = []

    for cid in cited_ids:
        if cid not in available_chunks:
            failures.append({"chunk_id": cid, "reason": "chunk_id not in retrieved set"})
            continue

        # Lighter check: does the chunk exist in the database at all?
        if not chunk_exists_in_db(cid):
            failures.append({"chunk_id": cid, "reason": "chunk_id does not exist"})
            continue

        # Optional stronger check: does the claim's surrounding sentence overlap
        # meaningfully with the chunk text? Use a small embedding similarity check
        # or a substring overlap heuristic. For v1, skip this and rely on prompt
        # discipline + the existence check.

    return VerificationResult(
        ok=(len(failures) == 0),
        failures=failures,
        text=answer_text,
    )
```

In v1, the existence check is sufficient. The stronger semantic verification is a v2 hardening pass.

---

## 9. UI/UX Specifications

### 9.1 Layout

Three-pane layout, desktop-optimized (this is a demo, not a mobile app).

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│  Header: "End-of-Well Intelligence" | well selector | Cohere logo                │
├────────────────────────────────────────────────────────┬─────────────────────────┤
│                                                        │                         │
│  Main: chat input at top, brief output below           │  Tool-call timeline     │
│                                                        │  (auto-scrolling)       │
│  ┌──────────────────────────────────────────────────┐  │                         │
│  │ Ask about drilling, formations, or lessons...   ▶│  │  [search_drilling..]    │
│  └──────────────────────────────────────────────────┘  │   query: stuck pipe     │
│                                                        │   well: 15/9-F-11       │
│  Summary                                               │   → 8 chunks            │
│  ----------------------------------------------        │                         │
│  Well 15/9-F-11 was drilled with three significant     │  [get_formation_tops]   │
│  operational issues, two of which were avoidable...    │   well: 15/9-F-11       │
│                                                        │   → 12 formations       │
│  Key Findings                                          │                         │
│                                                        │  [rerank_results]       │
│  1. Differential sticking in Hugin sands               │   → top 8 by relevance  │
│     Severity: High | Confidence: High                  │                         │
│     What happened: Drillstring became stuck at         │                         │
│     2,950m MD on Day 23. [F11_DDR23_PROB_002]          │                         │
│     ...                                                │                         │
│                                                        │                         │
└────────────────────────────────────────────────────────┴─────────────────────────┘
```

### 9.2 Citation chip behavior

Citations rendered inline as small pills with the chunk_id (abbreviated for readability):

```
... stuck at 2,950m MD on Day 23. [DDR-23 ●]
```

Hover → tooltip shows section_path + first 200 chars of chunk text.
Click → modal opens with PDF viewer scrolled to the chunk's page, with the chunk's text highlighted via bbox overlay.

**Critical UI investment:** spend the time on the PDF viewer. Use `react-pdf` (`pdfjs-dist` under the hood). Render the source PDF, navigate to the correct page, draw a semi-transparent highlight rectangle over the chunk's bbox region. This single interaction sells the demo.

### 9.3 Streaming behavior

- Tool calls appear in the timeline as they happen, with their parameters visible.
- Tool results in the timeline show a one-line summary (e.g., "8 chunks retrieved").
- The main brief streams in via SSE, building progressively. Citation chips become clickable as soon as they're rendered (don't wait for stream completion).

### 9.4 Empty / error states

- **No results:** "I couldn't find evidence in the available reports to answer that. The Volve corpus covers wells 15/9-F-1 through 15/9-F-15 — would you like to rephrase or pick a different well?"
- **Citation verification failure:** never shown to user. Triggers internal retry.
- **Tool failure:** "Encountered an issue retrieving [tool]. Continuing with available evidence."

### 9.5 Design language

- Typography: a serious sans (Inter or IBM Plex Sans). No playful fonts.
- Color: muted (slate / stone neutrals), single accent for citations.
- No emojis anywhere in the UI. Not in placeholders, not in tooltips, not in error states.
- The aesthetic target is "enterprise engineering tool," not "consumer AI chat."

---

## 10. Tech Stack

| Layer | Choice | Rationale |
|---|---|---|
| **LLM** | Cohere Command A (`command-a-03-2025`) | Best Cohere reasoning + tool-use model; matches the Cohere-native story |
| **Embeddings** | Cohere Embed v4 (`embed-v4.0`) | 1024-dim, strong on technical text |
| **Reranking** | Cohere Rerank 3.5 (`rerank-v3.5`) | The differentiator for citation precision |
| **Agent framework** | None (hand-rolled loop, ~200 LOC) | Frameworks add debug overhead the demo doesn't need |
| **Vector DB** | LanceDB | Embedded, no service, fast enough |
| **BM25** | bm25s (Python) | In-process, simple |
| **Structured DB** | DuckDB | Embedded, SQL, trivial to port later |
| **Backend** | FastAPI + Uvicorn | SSE streaming, async-native |
| **PDF parsing** | pdfplumber + PyMuPDF (fallback) | pdfplumber preserves bboxes |
| **Frontend** | Next.js 14 (App Router) + Tailwind + shadcn/ui | Matches your existing patterns |
| **PDF viewer** | react-pdf (pdfjs-dist) | De-facto standard, supports bbox overlay |
| **State** | React Server Components + streaming | Native to Next.js 14 |
| **Deployment** | Single Docker Compose, or Vercel (frontend) + Fly.io / Railway (backend) | Simple, presenter can run locally too |

### 10.1 What's deliberately NOT in the stack

- **LangChain / LlamaIndex / CrewAI / LangGraph.** Five tools and a linear loop don't need a framework. Frameworks become debugging surface during a live demo.
- **Pinecone / Weaviate / Qdrant.** Adds a service for no demo benefit.
- **Snowflake (in the demo itself).** Add it later for the "this scales" slide; not required to run.
- **Authentication.** It's a demo. Add basic auth only if it ships outside controlled environments.

---

## 11. Project Structure

```
eowi-demo/
├── README.md
├── docker-compose.yml
├── .env.example
│
├── data/
│   ├── raw/                          # original Volve PDFs (gitignored)
│   ├── curated/
│   │   ├── manifest.json
│   │   └── pdfs/                     # canonical doc_id-named PDFs
│   ├── extracted/                    # stage 1 output (JSON per doc)
│   ├── parsed/                       # stage 2 output (sectioned)
│   └── index/                        # LanceDB + BM25 + DuckDB files
│
├── scripts/
│   ├── fetch_volve.py                # one-shot download
│   ├── extract_text.py               # stage 1
│   ├── parse_sections.py             # stage 2
│   ├── chunk_and_enrich.py           # stages 3-4
│   ├── embed_and_index.py            # stages 5-6
│   ├── load_structured.py            # populates DuckDB from extracted data
│   ├── eval_run.py                   # runs the eval harness
│   └── wells.yaml                    # the well-list config
│
├── backend/
│   ├── app/
│   │   ├── main.py                   # FastAPI entry
│   │   ├── agent.py                  # the agent loop
│   │   ├── tools.py                  # the five tool implementations
│   │   ├── retrieval.py              # hybrid retrieval
│   │   ├── verification.py           # citation verification
│   │   ├── prompts.py                # the system prompt + few-shots
│   │   ├── streaming.py              # SSE plumbing
│   │   └── db.py                     # DuckDB + LanceDB connections
│   ├── tests/
│   └── pyproject.toml
│
├── frontend/
│   ├── app/
│   │   ├── page.tsx                  # main demo UI
│   │   ├── api/chat/route.ts         # SSE proxy to backend
│   │   └── layout.tsx
│   ├── components/
│   │   ├── ChatInput.tsx
│   │   ├── BriefRenderer.tsx
│   │   ├── CitationChip.tsx
│   │   ├── PdfViewerModal.tsx
│   │   ├── ToolCallTimeline.tsx
│   │   └── WellSelector.tsx
│   ├── lib/
│   │   ├── streaming.ts
│   │   └── citations.ts
│   ├── public/pdfs/                  # symlink to data/curated/pdfs
│   ├── package.json
│   └── tailwind.config.ts
│
└── eval/
    ├── questions.yaml                # 30-50 demo questions with expected behavior
    ├── runs/                         # eval run outputs
    └── README.md
```

---

## 12. Build Phases

### Phase 1 — Data foundation (week 1)

**Deliverables:**
- `wells.yaml` finalized
- `fetch_volve.py` runs end-to-end, produces `data/raw/`
- Curation pass complete; `manifest.json` produced
- `extract_text.py` + `parse_sections.py` produce clean per-document JSON for the demo well 15/9-F-11

**Done when:** you can open three random DDRs from F-11, look at the parsed JSON, and see clean sections with correct page references.

### Phase 2 — Indexing + retrieval (week 1.5)

**Deliverables:**
- `chunk_and_enrich.py` produces chunks with metadata
- `embed_and_index.py` populates LanceDB and BM25
- `load_structured.py` populates DuckDB
- A `retrieve.py` CLI that takes a query and returns top-8 reranked chunks with section_path printed

**Done when:** 10 sample queries return obviously-correct top chunks (eyeball test).

### Phase 3 — Agent + verification (week 2)

**Deliverables:**
- All five tools implemented and unit-tested
- Agent loop runs end-to-end
- Citation verification catches a deliberately-broken citation
- Outputs match the structured template

**Done when:** the three demo questions from section 2 produce coherent, cited briefings via CLI.

### Phase 4 — UI (weeks 2.5–3.5)

**Deliverables:**
- Next.js app skeleton with streaming
- Brief renderer with citation chips
- PDF viewer modal with bbox highlight
- Tool-call timeline panel

**Done when:** end-to-end demo runs in browser, all citations open the right page with correct highlight.

### Phase 5 — Polish + eval + dry runs (week 4)

**Deliverables:**
- Eval harness with 30+ questions and pass/fail criteria
- Demo script rehearsed end-to-end at least 5 times
- Fallback paths for the 3–5 most likely "weird questions" an exec will ask
- Architecture bridge slide

**Done when:** you can deliver the demo cold, on a fresh laptop, in under 5 minutes, without surprises.

---

## 13. Evaluation Harness

### 13.1 Question taxonomy

The eval set covers four categories:
1. **In-scope, well-evidenced.** Should produce confident, well-cited answers. (15 questions)
2. **In-scope, thin evidence.** Should produce low-confidence answers with explicit uncertainty. (8 questions)
3. **Out-of-scope.** Should refuse cleanly and suggest a viable follow-up. (5 questions)
4. **Adversarial / weird.** Should not derail the agent. (5 questions)

### 13.2 Eval format

```yaml
# eval/questions.yaml
- id: q001
  category: in_scope_evidenced
  question: "What were the three most costly operational issues on 15/9-F-11?"
  must_cite:
    - doc_type: DDR
      min_count: 2
    - doc_type: EOWR
      min_count: 1
  must_mention:
    - "stuck pipe" or "differential sticking"
  must_not_mention:
    - "I don't have access"
  expected_confidence: high

- id: q017
  category: out_of_scope
  question: "What's the current production rate on Volve?"
  expected_behavior: graceful_refusal
  must_mention:
    - "decommissioned" or "shut in" or "ceased production"
  must_suggest_alternative: true
```

### 13.3 Automated checks

For each eval question:
- All cited chunk_ids exist
- All cited chunks contain substring evidence for the surrounding claim (lexical or embedding-similarity)
- Output matches the structured template
- Latency under 30 seconds end-to-end
- Required terms present; forbidden terms absent

Run `python scripts/eval_run.py` to execute the full suite. Pass criteria: 90%+ on category 1, 80%+ on categories 2–3, no crashes on category 4.

---

## 14. Gotchas and Risks

### 14.1 PDF extraction quality varies

Some Volve DDRs are clean text-PDFs. Others are scans. Some are clean text but with tables that destroy reading order. **Plan for ~20% of documents to need special handling.** Exclude problem docs from v1 rather than fighting them. Document the exclusion in the manifest.

### 14.2 Citation rendering is harder than it looks

`pdfplumber` bboxes work in PDF coordinates (origin bottom-left, points). `react-pdf` renders in CSS coordinates (origin top-left, pixels). Conversion requires knowing the PDF's mediabox and the current render scale. **Prototype this on day one with a single page and a known phrase.** Don't discover it in week three.

### 14.3 Section parsing brittleness

DDR formats drift over a multi-year campaign. The parser will work on 80% of documents and fail on 20%. For the 20%, fall back to whole-page chunking with a `quality_flag` rather than dropping the document. Track parsing success rate as a metric.

### 14.4 The "weird question" problem

Execs ask questions that don't fit the demo's happy path. Examples observed in past demos:
- "Can it write me a drilling program for a new well?" — partially in scope, manage expectations
- "Does it know about [proprietary system X]?" — out of scope, bridge to the integration story
- "What if I asked it in [language X]?" — Cohere is multilingual; if you haven't tested this, don't promise it

Build a pre-meeting question rehearsal with 10 weird questions, see what the agent does, and add fallback paths for the worst three.

### 14.5 Live demo failure modes

- **Cohere API hiccup.** Build a local recording of one canonical run that can be replayed if the live system fails. Disclosed honestly: "let me show you a recording from this morning."
- **Network failure.** Cache the demo data, embeddings, and rerank results locally; the only network dependency at demo time should be the Cohere chat API.
- **Slow response.** Pre-warm the API connection at app start.

### 14.6 Buyer pushback you should rehearse

- *"How does this know it's not hallucinating?"* → walk through the citation verification step and click a chip.
- *"How long to connect this to our data?"* → the integration story slide, specific to their stack if you know it.
- *"What about our security / data residency?"* → Cohere's private deployment / VPC story; have the one-liner ready.
- *"This is just RAG."* → "Correct — agentic RAG with structured tool use and citation verification. The distinction that matters is that the agent decides what to retrieve and how to reason over it, with audit trail."

---

## 15. Out-of-Scope (v1)

Explicitly NOT in v1, but designed for graceful extension:

- Multi-turn refinement ("now redo that comparison excluding F-15")
- Cross-field analysis (Volve is one field)
- Time-series data integration (WITSML channels)
- Seismic / SEGY anything
- Eclipse reservoir model integration
- Production data integration
- Authentication / multi-tenancy
- Snowflake-backed deployment (separate "scale" demo)

### 15.1 Designed-for extensions

The data model and tool schemas are deliberately set up so the following can be added without restructuring:
- New doc types (just extend `doc_type` enum and parser registry)
- New structured tools (add to TOOLS list, implement in tools.py)
- Snowflake backend (DuckDB schema is portable; swap connection layer in db.py)
- Cohere Compass for unified document indexing if you outgrow LanceDB

---

## 16. Open Questions to Resolve During Build

These are decisions deferred to implementation:

1. **OCR for image PDFs:** include or exclude? Recommendation: exclude in v1, add v2 if time permits.
2. **Sidetrack handling:** treat 15/9-F-11, 15/9-F-11 A, 15/9-F-11 B as one well group or three wells? Recommendation: three wells with a `parent_well_id` link, expose via offset_wells.
3. **Cohere Compass:** evaluate as a LanceDB+BM25 replacement once available. Defer the decision until phase 2.
4. **Multi-language:** Volve docs are English. Defer multilingual.
5. **Streaming granularity:** stream at token level or sentence level? Recommendation: sentence-level — looks more deliberate, less chatbot-y.

---

## 17. Success Criteria (the demo, not the code)

The build is "done" when, in a controlled run, all of the following are true:

- [ ] Demo runs end-to-end in under 5 minutes
- [ ] Three rehearsed questions produce structured briefings with valid citations
- [ ] Every citation chip opens the source PDF to the correct page with the correct highlight
- [ ] One off-script question produces a graceful response, not a crash or hallucination
- [ ] The bridge slide names at least three of the buyer's actual systems credibly
- [ ] A drilling SME (find one and pay for an hour of their time) reviews three outputs and says "yes, an engineer would write this"
- [ ] The presenter can deliver the demo from a cold start on a clean laptop

The last bullet is the highest-leverage one. If the demo only runs on the developer's specific machine with their specific environment, it isn't a demo, it's a science project.

---

## Appendix A: Bridge Slide Content

For the architecture bridge slide referenced in section 2.6, the two columns should be:

**Demo (left):**
- search_drilling_reports → LanceDB + BM25 over Volve DDRs/EOWRs
- get_well_header → DuckDB (Volve well master)
- get_formation_tops → DuckDB (Volve stratigraphy)
- get_offset_wells → DuckDB (Volve field)
- read_document_chunks → LanceDB (Volve corpus)

**Production (right):**
- search_drilling_reports → MCP adapter over [OpenWells | WellView | DDR SharePoint | unstructured archive index]
- get_well_header → MCP adapter over [EDM | corporate well master | OSDU well registry]
- get_formation_tops → MCP adapter over [subsurface DB | Petrel project store | OSDU work product]
- get_offset_wells → MCP adapter over [asset team portfolio | OSDU spatial index]
- read_document_chunks → MCP adapter over [enterprise search | document management system]

Note: the right column doesn't claim shipped adapters — it claims the architecture. If specific adapters are shipped, name those specifically.

---

## Appendix B: First 20 Eval Questions (seed)

1. "What were the three most costly operational issues on 15/9-F-11?"
2. "Of the issues on 15/9-F-11, which were avoidable through better well design vs better execution?"
3. "I'm planning a well targeting the Hugin Formation. What lessons should I take from F-11?"
4. "What stuck pipe events occurred on Volve, and what was done to free the pipe?"
5. "Which wells encountered the Heather Formation, and what were the drilling challenges there?"
6. "What was the mud weight strategy through the reservoir section on F-11?"
7. "Describe the BHA changes on F-11 and the reasons for each change."
8. "What NPT codes appear most often across the Volve drilling campaign?"
9. "Was there evidence of wellbore instability on F-11? What zones?"
10. "What completion strategy was used on F-11 and what was its rationale?"
11. "Compare drilling performance on F-11 vs F-14."
12. "When was F-11 spudded and when did it reach TD?"
13. "What's the TVD of the top of the Hugin on F-11?"
14. "Which offset wells are best analogs for a new Hugin target?"
15. "Summarize the lessons-learned section of the F-11 EOWR."
16. "Did F-11 experience any losses? If so, where and how were they cured?"
17. "What was the directional plan on F-11 and did it execute as planned?"
18. "Show me anything related to differential sticking risk in the Volve campaign."
19. "What's the production rate on Volve right now?" (out-of-scope, expects graceful refusal)
20. "Write me a complete drilling program for a new Volve well." (partially out-of-scope, expects scoped response)

Add 10–30 more during build based on what the SME reviewer raises.
