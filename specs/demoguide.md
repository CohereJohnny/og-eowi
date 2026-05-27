# EOWI Demo — Demo Guide

**Version:** 1.1
**Runtime target:** 4 minutes 15 seconds
**Primary persona:** P-1 Derek the Drilling VP — see [personas.md](personas.md)

---

## Pre-demo setup

1. Start Docker Compose: `docker compose up` (backend + frontend proxy)
2. Verify North configuration in `.env`
3. Pre-warm: submit a throwaway query on app load to establish North API connection
4. Confirm active North Library or fallback corpus includes `15/9-F-11`
5. Have recorded canonical run ready as fallback (disclosed honestly if live API fails)

**Cold-laptop criterion:** Presenter can complete setup on a machine that has never run the demo before, using only README + Docker Compose + `.env` with North credentials.

---

## Canonical demo script

### 2.1 Opening (presenter speaks, no UI) — 30s

> "Your senior drilling superintendent retires next year. He's drilled 200 wells. Every lesson he's learned is in his head and in 40,000 PDFs nobody reads end-to-end. When the next well kicks off, what does your team actually do with those 40,000 reports?"

**COO beat (15s):** Operational risk framing — knowledge walking out the door.

### 2.2 Framing the data — 10s

> "What you're about to see runs on the Equinor Volve dataset — a real, complete North Sea well dataset Equinor released for research. Same document formats, same engineering vocabulary, same operational reality as your wells."

### 2.3 First question — 90s

**Presenter types:**

> *"I'm planning a new well in the Hugin Formation. What are the three things I most need to know from how 15/9-F-11 was drilled?"*

**On screen:**

- Tool-call timeline: North Library retrieval plus any structured-data calls for formation tops and well headers
- Main panel streams reasoning summary, then final brief
- Output: three-point briefing, severity tags, evidence basis, 2–4 citation chips per finding

### 2.4 The aha question — 60s

**Presenter (same session, no reset):**

> *"Of those issues, which were avoidable through better well design vs. better execution?"*

**Expected agent behavior:**

- Re-read evidence with different framing
- Reason causally; classify per issue with confidence + rationale
- Cite evidence for each judgment

**On screen:** Updated brief with "Design vs. Execution" classification per issue.

### 2.5 Citation drill-down — 30s

Presenter clicks a citation chip. PDF viewer opens to cited DDR page with highlighted paragraph.

> "Every claim is one click from the source. Your QA process already trusts these documents — now they're queryable."

Click a second chip. Same precision.

**v1 highlight:** Block-level paragraph band (not char-level) — presenter says *"highlighted the relevant paragraph"* if needed.

### 2.6 Bridge slide — 60s

Architecture slide. Left: demo as shown. Right: same agent, adapters relabeled.

| Demo tool | Production adapter |
|---|---|
| North Library retrieval | OpenWells + DDR SharePoint + unstructured archive |
| `get_well_header` | EDM / corporate well master |
| `get_formation_tops` | Subsurface DB / Petrel / OSDU |
| `get_offset_wells` | Asset portfolio / OSDU spatial index |
| Source citation lookup | Enterprise search / DMS |

> "We don't need you to consolidate your data estate first. The agent gets value from what's connected today and grows from there."

**CTO beat:** MCP adapters, VPC deployment, no exotic infra.
**COO beat:** Same agent, full field history, no consolidation project first.

### 2.7 Close — 15s

> "One well today. Same agent across your full field history tomorrow. Your new drilling engineer has your retiring superintendent's brain available 24/7, with citations to the source documents your QA process already trusts."

---

## Rehearsal checklist

- [ ] Demo completes in under 5 minutes (target 4:15)
- [ ] Q1 → Q2 session continuity works without re-stating context
- [ ] All citation chips on rehearsed Q1/Q2 open correct page + highlight
- [ ] One off-script question tested (graceful, no crash)
- [ ] Recorded fallback tested
- [ ] Bridge slide customized for target buyer if known
- [ ] 5 dry runs without failure

---

## Off-script question prep

Build responses for the 3 most likely exec deviations (see [roadmap.md](roadmap.md)):

1. *"Can it write me a drilling program?"* → Scoped response; what it can vs. cannot do
2. *"Does it know about [proprietary system]?"* → Bridge to integration story
3. *"What if I asked in [language]?"* → Don't promise unless tested

---

## Buyer pushback — rehearsed responses

| Pushback | Response |
|---|---|
| "How does it know it's not hallucinating?" | Walk through citation verification; click a chip live |
| "How long to connect to our data?" | Bridge slide; adapters, not data lake first |
| "Security / data residency?" | Cohere private deployment / VPC one-liner |
| "This is just RAG." | "Agentic RAG — agent decides what to retrieve and how to reason, with audit trail" |

---

## Eval seed questions

See Appendix B in [eowi-demo-spec.md](eowi-demo-spec.md) and `eval/questions.yaml` (to be created in Phase 5).

**Demo-critical IDs:** Q3 (Hugin lessons), Q2 (design vs execution), Q1 (costly issues).

---

## Failure modes

| Failure | Fallback |
|---|---|
| Cohere API hiccup | Play recorded canonical run; disclose honestly |
| Network down (API only) | Local data/index fine; only chat API affected |
| Slow response (>30s) | Pre-warm at startup; rehearse with shorter Q |
| Zero retrieval results | Empty state copy in [uiux.md](uiux.md) |
