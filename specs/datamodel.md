# EOWI Demo — Data Model

Schemas for structured store (DuckDB), vector store (LanceDB), BM25 index, and document registry.

See [architecture.md](architecture.md) for ingestion flow that populates these stores.

---

## Design principles

- **DuckDB** for analytic/structured queries the agent runs via tools
- **LanceDB** for embedding search with metadata prefilter
- **bm25s** for lexical search over the same chunk corpus
- **chunks** table is the unit of retrieval and citation
- Schemas portable to Postgres/Snowflake later (swap connection layer only)

---

## DuckDB — structured store

### wells

**Purpose:** Well master — header data for `get_well_header` and `get_offset_wells`.

| Field | Type | Constraints | Description |
|---|---|---|---|
| well_id | TEXT | PK | e.g. `15/9-F-11` |
| well_name | TEXT | NOT NULL | Display name |
| field | TEXT | NOT NULL | `Volve` |
| operator | TEXT | | `Equinor (Statoil)` |
| spud_date | DATE | | |
| td_date | DATE | | |
| kb_elevation_m | DOUBLE | | |
| td_md_m | DOUBLE | | Measured depth at TD |
| td_tvd_m | DOUBLE | | True vertical depth at TD |
| surface_lat | DOUBLE | | |
| surface_lon | DOUBLE | | |
| well_purpose | TEXT | | production, injection, appraisal |
| well_status | TEXT | | |
| parent_well_id | TEXT | | Sidetracks/laterals link to parent |
| aliases | TEXT[] | | Alternate names |

**Business rules:**

- Sidetracks (F-11 A, B, T2) are separate wells with `parent_well_id` pointing to F-11
- v1 indexes subset only — see [roadmap.md](roadmap.md)

---

### formation_tops

**Purpose:** Stratigraphy for `get_formation_tops`.

| Field | Type | Constraints | Description |
|---|---|---|---|
| well_id | TEXT | PK (composite) | |
| formation_name | TEXT | PK (composite) | Hugin, Heather, Skagerrak, … |
| top_md_m | DOUBLE | PK (composite) | |
| top_tvd_m | DOUBLE | | |
| base_md_m | DOUBLE | | |
| lithology | TEXT | | sandstone, shale, … |
| interpreted_by | TEXT | | |
| interpretation_date | DATE | | |
| source_doc_id | TEXT | FK → documents | |

---

### completion_record

**Purpose:** Simplified completion components from available Volve data.

| Field | Type | Constraints | Description |
|---|---|---|---|
| well_id | TEXT | PK (composite) | |
| component_seq | INTEGER | PK (composite) | |
| component_type | TEXT | NOT NULL | casing, liner, screen, packer, tubing |
| od_inches | DOUBLE | | |
| id_inches | DOUBLE | | |
| top_md_m | DOUBLE | | |
| bottom_md_m | DOUBLE | | |
| grade | TEXT | L80, P110, … | |
| weight_lbft | DOUBLE | | |
| notes | TEXT | | |
| source_doc_id | TEXT | FK → documents | |

---

### documents

**Purpose:** Canonical document registry.

| Field | Type | Constraints | Description |
|---|---|---|---|
| doc_id | TEXT | PK | Deterministic hash of path |
| well_id | TEXT | nullable | Some docs span wells |
| doc_type | TEXT | NOT NULL | DDR, EOWR, COMPLETION_RPT, GEO_RPT |
| title | TEXT | | |
| doc_date | DATE | | |
| date_range_start | DATE | | Multi-day docs |
| date_range_end | DATE | | |
| source_path | TEXT | NOT NULL | Relative to data/raw/ |
| page_count | INTEGER | | |
| extraction_method | TEXT | pdfplumber, pymupdf, vision | |
| quality_flag | TEXT | good, vision_extracted, partial, failed | |
| demo_critical | BOOLEAN | default false | v1 corpus tag |

**quality_flag values:**

| Value | Meaning |
|---|---|
| good | Native text extraction via pdfplumber |
| vision_extracted | Scan PDF processed by Command A Plus at ingestion |
| partial | Section parse failed; whole-page chunks used |
| failed | Excluded from index |

---

### chunks

**Purpose:** Unit of retrieval and citation.

| Field | Type | Constraints | Description |
|---|---|---|---|
| chunk_id | TEXT | PK | `{doc_id}::{section}::{seq}` |
| doc_id | TEXT | NOT NULL, FK | |
| well_id | TEXT | denormalized | Filter speed |
| doc_type | TEXT | NOT NULL | |
| chunk_seq | INTEGER | NOT NULL | |
| page_start | INTEGER | NOT NULL | |
| page_end | INTEGER | NOT NULL | |
| section_path | TEXT | | e.g. `DDR 2008-04-15 > Problems Encountered` |
| depth_md_start_m | DOUBLE | | From enrichment regex |
| depth_md_end_m | DOUBLE | | |
| chunk_text | TEXT | NOT NULL | |
| char_offset_in_page | INTEGER | | Highlight reconstruction |
| token_count | INTEGER | | |

**Indexes:** `well_id`, `doc_type`, `doc_id`

---

## LanceDB — vector store

Single table embedded alongside the app.

| Field | Type | Description |
|---|---|---|
| chunk_id | string | FK to chunks.chunk_id |
| well_id | string | Prefilter |
| doc_type | string | Prefilter |
| embedding | vector(1024) | Cohere Embed v4 |
| text | string | Denormalized for inspection |

- Index: HNSW (LanceDB default)
- Embed input: `{section_path}\n\n{chunk_text}` with `input_type=search_document`

---

## BM25 store

In-process `bm25s` index over `chunks.chunk_text`.

**Token pattern** (preserves drilling identifiers):

```python
TOKEN_PATTERN = r"""(?x)
    \d+(?:\.\d+)?    # numbers including decimals
    | \d+/\d+        # fractions like 9/5
    | \d+-\d+        # ranges
    | \"             # inch marks
    | [A-Za-z]+(?:-[A-Za-z0-9]+)*   # words and hyphenated compounds
"""
```

---

## Source PDF store

Filesystem: `data/curated/pdfs/{doc_id}.pdf`

PDF viewer reads originals directly. No transformation.

---

## Databricks folder mapping

| Databricks volume path | Maps to doc_type / usage |
|---|---|
| `Reports/` | DDR, EOWR, completion reports |
| `Well_Logs/` | Formation tops source files |
| `Well_technical_data/` | Well headers, completion data |
| `Well_logs_pr_WELL/` | Per-well log bundles |

Exact path conventions documented in `data/curated/manifest.json` after first export.

---

## manifest.json (curation output)

```json
{
  "doc_id": "...",
  "well_id": "15/9-F-11",
  "doc_type": "DDR",
  "date_range": ["2008-04-01", "2008-04-30"],
  "extraction_method": "pdfplumber",
  "quality_flag": "good",
  "demo_critical": true,
  "source_path": "Reports/...",
  "databricks_source": "/Volumes/equinor_asa_volve_data_village/public/volve/Reports/..."
}
```

---

## Extension points (designed-for)

- New `doc_type` values — extend enum + parser registry
- New structured tools — add DuckDB tables + tool definition
- Snowflake backend — portable SQL from DuckDB schema
- Cohere Compass — replace LanceDB+BM25 if outgrown

See [roadmap.md](roadmap.md).
