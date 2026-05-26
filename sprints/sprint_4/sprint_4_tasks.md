# Sprint 4 Tasks — UI + Streaming + PDF Viewer

## Goals

- Build the Next.js demo UI.
- Stream tool events and final briefs.
- Render citation chips and source drill-down modal.

## Tasks

- [x] Implement three-pane layout.
- [x] Implement chat input and session behavior.
- [x] Implement tool-call timeline.
- [x] Implement brief renderer with inline citation chips.
- [x] Implement PDF viewer modal with block-level highlight.
- [x] Implement Next.js SSE proxy.

## Progress

Sprint 4 is implemented with a desktop-optimized UI matching the demo specification. The current PDF modal uses a mock page renderer while preserving the v1 block-level highlight contract; real PDF rendering can replace the page body once curated PDFs are mounted.
