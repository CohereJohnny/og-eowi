# End-of-Well Intelligence Agent — Product Requirements Document

**Version:** 1.1  
**Status:** Approved for v1 build  
**Agent name:** End-of-Well Intelligence Agent (EOWI)  
**Domain:** Oil & Gas — Upstream Drilling & Subsurface  
**Dataset:** Equinor Volve (North Sea)  
**Platform:** Cohere Command A + Embed v4 + Rerank 3.5  
**Build mode:** Solo vibe-code, 3–4 weeks, Docker Compose deploy

See also: [personas.md](personas.md) · [userstories.md](userstories.md) · [demoguide.md](demoguide.md) · [roadmap.md](roadmap.md)

---

## Overview

EOWI is a single-purpose agentic application that lets a user ask natural-language questions about real North Sea wells (Volve 15/9-F-11 and offset wells) and receive **grounded, cited, structured engineering briefings** drawn from daily drilling reports (DDRs), end-of-well reports (EOWRs), formation tops, completion records, and well headers.

The demo must convince an O&G executive in under 5 minutes that agentic AI can compress the work of a drilling engineering team while producing audit-quality output their QA process would trust.

## Problem statement

When a senior drilling superintendent retires, decades of operational knowledge leave with them. The lessons live in tens of thousands of PDF reports that nobody reads end-to-end. Before the next well kicks off, engineering teams manually search archives, call colleagues, and reconstruct context from fragmented sources — a slow, lossy process with no audit trail.

Existing search tools return document lists, not engineering judgments. Classical ML wrappers (anomaly detection, similarity scoring) cannot answer causal questions like *"which issues were avoidable through better well design vs. better execution?"*

## Vision

> Every factual claim in a drilling briefing is one click from the source document your QA process already trusts.

EOWI turns unstructured well history into queryable engineering intelligence with paragraph-level citations — not chatbot replies.

## Target users (summary)

See [personas.md](personas.md).

- **Primary (v1):** Drilling VP / Head of Drilling Operations — decides whether to pilot on a field
- **Secondary (v1):** CTO and COO — decision influencers served via bridge slide and presenter beats
- **Credibility check:** Subsurface leadership — formation/well context must read as engineering-native

## Goals

- **G-1:** Accept free-form drilling questions and produce structured engineering briefings (not chatbot prose)
- **G-2:** Ground every factual claim in retrieved evidence with chunk-level citations
- **G-3:** Stream visible agent planning (tool-call trace) to build executive trust
- **G-4:** Open cited source PDFs to the correct page with highlighted supporting text (block-level v1)
- **G-5:** Explicitly surface uncertainty when evidence is thin or absent
- **G-6:** Run fully local except Cohere Chat API — cold-laptop deployable via Docker Compose
- **G-7:** Support sequential follow-up questions within a session (Q1 → Q2 demo script)
- **G-8:** Ingest scan/image PDFs via Command A Plus vision at batch ingestion time

## Non-goals (v1)

See [roadmap.md](roadmap.md) for full deferred list.

- **NG-1:** Multi-turn refinement commands ("redo excluding F-15")
- **NG-2:** Full 17-well field corpus (v1 indexes hero + 5 offsets only)
- **NG-3:** Databricks connectivity at demo runtime
- **NG-4:** Authentication / multi-tenancy
- **NG-5:** Self-serve prospect demo URL
- **NG-6:** Seismic, production, WITSML, reservoir model integration
- **NG-7:** Synthetic or fabricated data — Volve open dataset only
- **NG-8:** LangChain / LlamaIndex / CrewAI agent frameworks

## Functional requirements

### FR-1: Natural-language query input

**Requirement:** Accept a free-form question phrased the way a drilling engineer would phrase it.

**Acceptance:** Demo script questions (see [demoguide.md](demoguide.md)) parse and route without special syntax.

---

### FR-2: Visible agent planning

**Requirement:** Stream tool-call timeline to a side panel as the agent executes.

**Acceptance:** Each tool call shows name, parameters, and one-line result summary. Timeline auto-scrolls.

---

### FR-3: Hybrid retrieval

**Requirement:** Retrieve from Volve document corpus using BM25 + Embed v4, merged and reranked with Rerank 3.5.

**Acceptance:** Sample queries return chunks from appropriate `section_path` (e.g., "stuck pipe" → "Problems Encountered").

---

### FR-4: Structured engineering brief output

**Requirement:** Synthesize answers using the canonical template: Summary, Key Findings (severity + confidence), Caveats, Suggested follow-up questions.

**Acceptance:** Output matches template in [architecture.md](architecture.md#system-prompt). No marketing language.

---

### FR-5: Chunk-level citations

**Requirement:** Every factual claim followed by `[chunk_id]` markers. Citations verified before response ships.

**Acceptance:** No citation resolves to a chunk_id outside the retrieved set. Verification failures trigger internal retry (never shown to user).

---

### FR-6: Citation drill-down

**Requirement:** Citation chips open source PDF to cited page with highlighted region.

**Acceptance (v1):** Correct PDF, correct page, paragraph-level highlight band. Char-level highlight is stretch — see [roadmap.md](roadmap.md).

---

### FR-7: Uncertainty surfacing

**Requirement:** Label confidence explicitly: High / Medium / Low / Insufficient evidence.

**Acceptance:** Thin-evidence eval questions produce low-confidence or refusal responses, not hallucination.

---

### FR-8: Structured data tools

**Requirement:** Five agent tools: `search_drilling_reports`, `get_well_header`, `get_formation_tops`, `get_offset_wells`, `read_document_chunks`.

**Acceptance:** Tool schemas match [architecture.md](architecture.md#tool-definitions).

---

### FR-9: Session continuity

**Requirement:** Backend maintains chat history within a browser session so follow-up questions reference prior context.

**Acceptance:** Demo script Q2 ("Of those issues…") works without re-stating Q1 context.

---

### FR-10: Vision-based PDF extraction

**Requirement:** Image-only / scan PDFs extracted at ingestion using Command A Plus (`command-a-plus-05-2026`) visual understanding. Native text PDFs use pdfplumber first.

**Acceptance:** Scan PDFs indexed with `quality_flag='vision_extracted'`. Ingestion is batch-only — no vision calls at query time.

---

## Non-functional requirements

- **NFR-1:** End-to-end latency under 30 seconds per question (eval harness)
- **NFR-2:** Single VM / laptop deployable via Docker Compose
- **NFR-3:** Only remote dependency at demo time: Cohere Chat API
- **NFR-4:** Demo runtime target: 4 minutes 15 seconds (see [demoguide.md](demoguide.md))
- **NFR-5:** Enterprise engineering aesthetic — no emojis, no playful fonts
- **NFR-6:** Eval harness pass: 90%+ in-scope evidenced; 80%+ thin-evidence and out-of-scope; no crashes on adversarial

## Success criteria (the demo, not the code)

The build is **done** when, in a controlled run:

- [ ] Demo runs end-to-end in under 5 minutes
- [ ] Three rehearsed questions produce structured briefings with valid citations
- [ ] Every citation chip opens the source PDF to the correct page with block-level highlight
- [ ] One off-script question produces a graceful response
- [ ] Bridge slide names buyer systems credibly (CTO/COO beat)
- [ ] Internal reviewer approves 3 scripted outputs for engineering tone
- [ ] Presenter can deliver from cold start on clean laptop via Docker Compose

**Pre-customer gate (not code-freeze):** External drilling SME reviews same 3 outputs before first operator-facing meeting.

## Data acquisition (v1)

- **Source:** Databricks Marketplace — `equinor_asa_volve_data_village/public/volve`
- **Method:** One-time export of Option B well subset to `data/raw/` — see [architecture.md](architecture.md#data-acquisition)
- **Fallback:** data.equinor.com azcopy if Databricks export fails
- **Runtime:** No Databricks dependency

## v1 well corpus

| Well | Role |
|---|---|
| 15/9-F-11 (+ sidetracks A/B/T2) | Primary demo well |
| 15/9-F-1, F-4, F-7, F-10, F-14 | Offset / analog wells |

Remaining wells in `wells.yaml` are roadmap — see [roadmap.md](roadmap.md).

## Related specifications

- [architecture.md](architecture.md) — agent loop, retrieval, ingestion pipeline
- [datamodel.md](datamodel.md) — schemas
- [uiux.md](uiux.md) — UI layout and interaction
- [techstack.md](techstack.md) — technology choices
- [eowi-demo-spec.md](eowi-demo-spec.md) — original monolith (reference)
