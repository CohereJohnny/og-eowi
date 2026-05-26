# EOWI Demo — UI/UX Specification

UI requirements for the End-of-Well Intelligence demo. Desktop-optimized — this is a stage demo, not a mobile app.

See [personas.md](personas.md) · [demoguide.md](demoguide.md)

---

## Design language

- **Typography:** Inter or IBM Plex Sans — serious sans, no playful fonts
- **Color:** Muted slate/stone neutrals; single accent for citations
- **Tone:** Enterprise engineering tool, not consumer AI chat
- **No emojis** anywhere — placeholders, tooltips, errors included

---

## Layout

Three-pane, desktop-optimized:

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│  Header: "End-of-Well Intelligence" | well selector | Cohere logo                │
├────────────────────────────────────────────────────────┬─────────────────────────┤
│  Main: chat input at top, brief output below           │  Tool-call timeline     │
│                                                        │  (auto-scrolling)       │
│  ┌──────────────────────────────────────────────────┐  │                         │
│  │ Ask about drilling, formations, or lessons...   ▶│  │  [search_drilling..]    │
│  └──────────────────────────────────────────────────┘  │   query: stuck pipe     │
│                                                        │   well: 15/9-F-11       │
│  Summary                                               │   → 8 chunks            │
│  Key Findings                                          │  [get_formation_tops]     │
│  1. Differential sticking...  [DDR-23 ●]               │  ...                    │
└────────────────────────────────────────────────────────┴─────────────────────────┘
```

### Header

- Title: "End-of-Well Intelligence"
- **Well selector:** Shows indexed wells only (v1: F-11 + offsets). Default `15/9-F-11`
- Cohere logo (demo branding)

### Main panel

- Chat input at top — single-line with submit
- Brief output below — structured sections from agent template
- **Session behavior:** Latest brief prominent; prior turn optionally collapsed (not full thread UI in v1)

### Side panel — tool-call timeline

- Auto-scrolling chronology of tool calls
- Each entry: tool name, parameters, one-line result summary
- Visible during live demo for CTO audit-trail narrative

---

## Citation chips

Inline pills with abbreviated chunk_id:

```
... stuck at 2,950m MD on Day 23. [DDR-23 ●]
```

**Hover:** Tooltip with `section_path` + first 200 chars of chunk text

**Click:** Opens PDF viewer modal

**Streaming:** Chips become clickable as soon as rendered — don't wait for stream completion

---

## PDF viewer modal

**Library:** react-pdf (pdfjs-dist)

**v1 behavior (acceptance):**

- Correct PDF opens
- Navigates to cited page
- **Block-level highlight:** semi-transparent band over paragraph layout block bbox from extraction (pdfplumber or vision)

**Stretch (Phase 5):** Char-level highlight with precise substring overlay

**Coordinate conversion note:** pdfplumber uses PDF points (origin bottom-left); react-pdf uses CSS pixels (origin top-left). Prototype conversion on day one with one known page — do not discover in week 3.

**Presenter fallback:** *"Highlighted the relevant paragraph"* if block band is approximate

---

## Streaming behavior

| Event | UI response |
|---|---|
| Tool call | Timeline entry appears immediately with params |
| Tool result | Timeline entry updates with summary line |
| Thinking | Optional subtle indicator in main panel |
| Final brief | Streams into main panel section by section |
| Citation in stream | Chip rendered and clickable inline |

**Granularity:** Sentence-level streaming (not token-level) — looks deliberate, less chatbot-y

---

## Empty and error states

### No retrieval results

> "I couldn't find evidence in the available reports to answer that. The Volve corpus covers wells [indexed list] — would you like to rephrase or pick a different well?"

Honest about partial v1 coverage — see [roadmap.md](roadmap.md).

### Citation verification failure

Never shown to user. Triggers internal agent retry.

### Tool failure

> "Encountered an issue retrieving [tool name]. Continuing with available evidence."

---

## Output format (rendered brief)

Agent template rendered as structured sections:

1. **Summary** — one paragraph
2. **Key Findings** — numbered, each with:
   - Title
   - Severity: High / Medium / Low
   - Confidence: High / Medium / Low
   - What happened (with citation chips)
   - Why it matters
   - Evidence basis (chunk list)
3. **Caveats and uncertainty**
4. **Suggested follow-up questions**

Engineering judgment blocks labeled: *"Engineering judgment based on:"* + evidence list

---

## Accessibility (demo scope)

- Semantic HTML for brief sections
- Keyboard: Escape closes PDF modal
- Full WCAG compliance not v1 gate — desktop stage demo

---

## Components (frontend)

| Component | Responsibility |
|---|---|
| `chat-input.tsx` | Query input + submit |
| `brief-renderer.tsx` | Structured brief + sections |
| `citation-chip.tsx` | Inline pill, hover, click handler |
| `pdf-viewer-modal.tsx` | PDF render, page nav, bbox highlight |
| `tool-call-timeline.tsx` | Side panel stream |
| `well-selector.tsx` | Indexed wells dropdown |

---

## Non-UI demo elements

- **Bridge slide:** External (not in app) — see [demoguide.md](demoguide.md) §2.6
- **Recorded fallback:** Separate video or replay mode — roadmap if not built in v1
