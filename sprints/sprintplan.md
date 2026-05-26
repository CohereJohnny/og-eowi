# EOWI Demo — Master Sprint Plan

This sprint plan sequences implementation of the End-of-Well Intelligence demo from the specifications in `specs/`.

## Vision

Build a presenter-ready, cold-laptop deployable agentic demo that answers drilling questions about Volve well 15/9-F-11 and five offset wells with grounded, cited engineering briefings, visible tool-call trace, and PDF citation drill-down.

## Cadence

- Sprint length: approximately 1 week
- Team: solo developer + AI assistant
- Sprint artifacts: `sprint_N_tasks.md`, `sprint_N_testplan.md`, optional updates/report files
- Central logs: `backlog.md`, `tech_debt.md`, `bug_swatting.md`

## Sprint Dependency Graph

```mermaid
flowchart LR
    S1[Sprint1_FoundationAndData] --> S2[Sprint2_IndexAndRetrieve]
    S2 --> S3[Sprint3_AgentAndTools]
    S3 --> S4[Sprint4_UIAndStreaming]
    S4 --> S5[Sprint5_EvalAndDemoReady]
```

## Sprint Summaries

| Sprint | Focus | Primary spec anchors |
|---|---|---|
| 1 | Foundation, Docker Compose, Databricks export script, extraction/parsing, mock corpus | `specs/architecture.md`, US-1.1 to US-1.4 |
| 2 | Chunking, DuckDB/LanceDB/BM25 indexes, hybrid retrieval CLI | `specs/datamodel.md`, US-1.5, US-2.1 |
| 3 | Five tools, agent loop, citation verification, SSE chat API | `specs/architecture.md`, US-3.1 to US-3.5 |
| 4 | Next.js UI, streaming, timeline, citation chips, PDF viewer | `specs/uiux.md`, US-4.1 to US-4.2 |
| 5 | Eval harness, Docker hardening, dry runs, bridge slide, internal review | `specs/demoguide.md`, US-4.3 to US-5.2 |

## Success Metrics

| Metric | Target |
|---|---|
| Demo runtime | 5 minutes or less, target 4:15 |
| Query latency | 30 seconds or less |
| Eval category 1 | 90%+ pass |
| Eval categories 2-3 | 80%+ pass |
| Cold laptop setup | 10 minutes or less |
| Dry runs | 5 consecutive clean runs |
