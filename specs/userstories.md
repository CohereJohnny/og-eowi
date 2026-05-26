# EOWI Demo — User Stories

User stories grouped by epic. Form: **As a [persona], I want [capability], so that [outcome]**.

Persona IDs (P-1..P-5) reference [personas.md](personas.md). Requirement IDs (FR-*, NFR-*) reference [prd.md](prd.md).

Tag: **v1** = required for demo; **stretch** = Phase 5 optional.

---

## Epic 1 — Data acquisition & ingestion

### US-1.1 — Export Volve subset from Databricks (v1)

**As** Alex the Presenter (P-5), **I want** a script that copies the v1 well subset from the Databricks Marketplace volume to local storage, **so that** the demo runs without Databricks connectivity at presentation time.

**Acceptance criteria:**

- AC-1: `scripts/fetch_volve_databricks.py` reads `wells.yaml` and writes to `data/raw/`
- AC-2: Idempotent — skips files with matching size + hash
- AC-3: Logs failures without aborting batch
- AC-4: Output preserves path metadata for `manifest.json`

Satisfies: FR-10 (data path), NFR-3.

---

### US-1.2 — Extract text from native PDFs (v1)

**As** the ingestion pipeline, **I want** pdfplumber to extract text and layout bboxes from text-native PDFs, **so that** chunks have page-accurate highlight coordinates.

**Acceptance criteria:**

- AC-1: Output JSON includes `char_bboxes` and `layout_blocks` per page
- AC-2: Documents tagged `extraction_method=pdfplumber`, `quality_flag=good`
- AC-3: Failed extraction falls back to PyMuPDF or flags `failed`

Satisfies: FR-10.

---

### US-1.3 — Extract text from scan PDFs via vision (v1)

**As** the ingestion pipeline, **I want** Command A Plus to extract text and layout from image-only PDFs at batch time, **so that** scan DDRs are searchable without a separate OCR toolchain.

**Acceptance criteria:**

- AC-1: Scan PDFs detected and routed to vision path automatically
- AC-2: Uses `command-a-plus-05-2026`; **no vision calls at query time**
- AC-3: Output matches pdfplumber JSON schema
- AC-4: Documents tagged `extraction_method=vision`, `quality_flag=vision_extracted`

Satisfies: FR-10.

---

### US-1.4 — Parse DDR and EOWR sections (v1)

**As** the retrieval system, **I want** DDRs parsed into named sections, **so that** "stuck pipe" queries return "Problems Encountered" chunks.

**Acceptance criteria:**

- AC-1: DDR sections extracted per architecture spec
- AC-2: EOWR sections extracted with analogous parser
- AC-3: Parse failure → whole-page chunks with `quality_flag=partial`
- AC-4: `section_path` populated on every chunk

Satisfies: FR-3.

---

### US-1.5 — Index v1 well corpus (v1)

**As** Alex the Presenter (P-5), **I want** F-11 and five offset wells fully indexed, **so that** the demo and core eval questions work.

**Acceptance criteria:**

- AC-1: F-11, F-1, F-4, F-7, F-10, F-14 each have ≥1 DDR and ≥1 EOWR
- AC-2: LanceDB, BM25, and DuckDB populated under `data/index/`
- AC-3: `manifest.json` tags `demo_critical` documents
- AC-4: Ingestion checklist in [architecture.md](architecture.md) passes

Satisfies: FR-3, G-6.

---

## Epic 2 — Retrieval

### US-2.1 — Hybrid search with rerank (v1)

**As** the agent, **I want** hybrid BM25 + embedding search reranked to top-8 chunks, **so that** citations are precise enough for executive trust.

**Acceptance criteria:**

- AC-1: Parallel BM25 top-50 and Embed top-50
- AC-2: Merge dedupe to 80; Rerank 3.5 to 8
- AC-3: Prefilter on well_id and doc_type when provided
- AC-4: CLI `retrieve.py` passes eyeball test on 10 sample queries

Satisfies: FR-3.

---

## Epic 3 — Agent & citations

### US-3.1 — Ask a drilling question (v1)

**As** Derek the Drilling VP (P-1), **I want** to type a natural-language question about well F-11, **so that** I get a structured engineering briefing without reading thousands of PDFs.

**Acceptance criteria:**

- AC-1: Demo script Q1 produces three findings with severity + confidence
- AC-2: Output follows structured template
- AC-3: Latency under 30 seconds

Satisfies: FR-1, FR-4, NFR-1.

---

### US-3.2 — Follow up in same session (v1)

**As** Derek (P-1), **I want** to ask a follow-up question that references the prior answer, **so that** I see the agent reason causally across turns.

**Acceptance criteria:**

- AC-1: Demo script Q2 works without re-stating Q1 context
- AC-2: Backend passes chat history to agent
- AC-3: No refinement UI required ("redo excluding F-15" remains out of scope)

Satisfies: FR-9.

---

### US-3.3 — Verify citations before response (v1)

**As** Elena the Subsurface Lead (P-4), **I want** every citation to resolve to a real retrieved chunk, **so that** I trust the briefing is not hallucinated.

**Acceptance criteria:**

- AC-1: Citation verification runs before final stream
- AC-2: Invalid citations trigger internal retry — never shown to user
- AC-3: Eval harness confirms 100% chunk_id validity on category-1 questions

Satisfies: FR-5.

---

### US-3.4 — Classify design vs execution (v1)

**As** Derek (P-1), **I want** the agent to distinguish design-avoidable vs execution-avoidable issues with cited rationale, **so that** I believe this is reasoning, not keyword search.

**Acceptance criteria:**

- AC-1: Q2 produces per-issue classification with confidence
- AC-2: Judgments labeled "Engineering judgment based on:" with evidence
- AC-3: Each classification cites supporting chunks

Satisfies: FR-4, FR-7. Demo aha moment — [demoguide.md](demoguide.md) §2.4.

---

### US-3.5 — Query structured well data (v1)

**As** Elena (P-4), **I want** formation tops and well headers retrieved from structured tools before narrative search, **so that** depth and formation data is authoritative.

**Acceptance criteria:**

- AC-1: `get_formation_tops('15/9-F-11')` returns Hugin top MD/TVD
- AC-2: `get_well_header` returns spud date, TD, coordinates
- AC-3: Agent calls structured tools when question is about depths/headers

Satisfies: FR-8.

---

## Epic 4 — UI & demo delivery

### US-4.1 — See agent planning (v1)

**As** Sarah the CTO (P-2), **I want** to see tool calls stream in a side panel, **so that** I can explain the audit trail to my team.

**Acceptance criteria:**

- AC-1: Timeline shows tool name, params, result summary
- AC-2: Auto-scrolls during execution
- AC-3: Visible during live demo without scrolling the main brief off-screen

Satisfies: FR-2.

---

### US-4.2 — Click citation to source PDF (v1)

**As** Derek (P-1), **I want** to click a citation chip and see the source DDR page with the relevant paragraph highlighted, **so that** I can verify claims in one click.

**Acceptance criteria:**

- AC-1: Opens correct PDF and page
- AC-2: Block-level highlight band visible (v1)
- AC-3: Hover tooltip shows section_path + text preview
- AC-4: Works during streaming — chips clickable before stream completes

Satisfies: FR-6.

---

### US-4.3 — Run demo from Docker Compose (v1)

**As** Alex the Presenter (P-5), **I want** to start the full demo with one command on a clean laptop, **so that** I'm not dependent on my dev environment.

**Acceptance criteria:**

- AC-1: `docker compose up` starts backend + frontend
- AC-2: Only external dependency: Cohere API key
- AC-3: README documents setup in under 10 minutes
- AC-4: 5 dry runs pass without manual intervention

Satisfies: NFR-2, NFR-5, success criteria in [prd.md](prd.md).

---

### US-4.4 — Handle off-script question (v1)

**As** Alex (P-5), **I want** the agent to respond gracefully to one unexpected question, **so that** the demo survives executive curiosity.

**Acceptance criteria:**

- AC-1: No crash on out-of-scope question
- AC-2: Graceful refusal or scoped response with suggested alternative
- AC-3: Tested against ≥3 rehearsed weird questions

Satisfies: delivery mode B — [roadmap.md](roadmap.md).

---

### US-4.5 — Char-level PDF highlight (stretch)

**As** Derek (P-1), **I want** citation highlights to pinpoint the exact cited sentence, **so that** verification is instantaneous.

**Acceptance criteria:**

- AC-1: Char-level bbox overlay on cited substring
- AC-2: Works across pdfplumber and vision-extracted bboxes

Deferred to Phase 5 stretch — [roadmap.md](roadmap.md).

---

## Epic 5 — Eval & validation

### US-5.1 — Run automated eval harness (v1)

**As** Alex (P-5), **I want** an eval script that runs 30+ questions with pass/fail checks, **so that** I know the demo is reliable before a customer meeting.

**Acceptance criteria:**

- AC-1: `eval/questions.yaml` covers 4 categories per [eowi-demo-spec.md](eowi-demo-spec.md) §13
- AC-2: Automated checks: chunk validity, template match, latency, required/forbidden terms
- AC-3: Pass: 90%+ category 1, 80%+ categories 2–3, no crashes category 4

Satisfies: NFR-6.

---

### US-5.2 — Internal engineering review (v1)

**As** Alex (P-5), **I want** an internal reviewer to approve 3 scripted outputs, **so that** v1 can launch before external SME is scheduled.

**Acceptance criteria:**

- AC-1: Q1, Q2, and one offset-well question reviewed
- AC-2: Reviewer confirms engineering tone and terminology
- AC-3: Documented sign-off before external demo

Satisfies: SME Option D — [roadmap.md](roadmap.md).

---

### US-5.3 — External SME review (pre-customer gate)

**As** Derek (P-1), **I want** a drilling SME to confirm outputs read like real engineering work, **so that** I trust this in a pilot conversation.

**Acceptance criteria:**

- AC-1: External SME reviews same 3 outputs as US-5.2
- AC-2: Completed before first operator-facing meeting
- AC-3: Feedback incorporated into eval question set

Not blocking v1 code-freeze — [roadmap.md](roadmap.md).

---

## Epic 6 — Future (roadmap)

Stories deferred — see [roadmap.md](roadmap.md):

- US-6.1 — Multi-turn refinement ("redo excluding F-15")
- US-6.2 — Full 17-well field index
- US-6.3 — Self-serve demo URL
- US-6.4 — Cohere memory integration
- US-6.5 — Recorded demo replay mode
