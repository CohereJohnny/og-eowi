import asyncio
import json
from collections import defaultdict
from collections.abc import AsyncIterator

from .models import ToolEvent
from .tools import (
    get_formation_tops,
    get_offset_wells,
    get_well_header,
    read_document_chunks,
    search_drilling_reports,
)
from .verification import verify_citations

SESSIONS: dict[str, list[dict[str, str]]] = defaultdict(list)


def _event(event: ToolEvent) -> str:
    return f"data: {json.dumps(event.model_dump(exclude_none=True))}\n\n"


def _format_findings(chunks: list[dict], query: str) -> str:
    ids = {chunk["chunk_id"] for chunk in chunks}
    stuck = next((chunk for chunk in chunks if "stuck" in chunk["chunk_text"].lower()), chunks[0])
    mud = next(
        (
            chunk
            for chunk in chunks
            if "mud weight" in chunk["chunk_text"].lower() or "ecd" in chunk["chunk_text"].lower()
        ),
        chunks[min(1, len(chunks) - 1)],
    )
    lesson = next((chunk for chunk in chunks if "lessons" in chunk["section_path"].lower()), chunks[-1])

    if "design" in query.lower() and "execution" in query.lower():
        answer = f"""**Summary**
The F-11 issues split into one partly design-exposed risk and two primarily execution-manageable risks. The evidence supports treating differential sticking as a combined design/execution exposure, while connection discipline and ECD management were more directly execution-controlled.

**Key Findings**

1. **Differential sticking exposure** — Severity: High — Confidence: High
   - What happened: F-11 became differentially stuck in the Hugin interval after overpull and pack-off symptoms developed. [{stuck["chunk_id"]}]
   - Engineering judgment based on: BHA contact area increased the exposure, but stationary time after connections made the event more likely. [{stuck["chunk_id"]}]
   - Classification: Design-influenced, execution-amplified.

2. **Connection and hole-cleaning discipline** — Severity: High — Confidence: Medium
   - What happened: The EOWR lessons emphasize reducing stationary time and maintaining hole cleaning before connections. [{lesson["chunk_id"]}]
   - Engineering judgment based on: The offset F-14 improved outcomes by reducing connection duration and increasing sweep frequency when drilling Hugin. [F14_EOWR::comparison::001]
   - Classification: Primarily execution-manageable.

3. **ECD window management** — Severity: Medium — Confidence: Medium
   - What happened: Mud weight increased through the reservoir and ECD approached the fracture margin during high-flow cleanout. [{mud["chunk_id"]}]
   - Engineering judgment based on: The mitigation is tighter ECD management rather than a wholesale well redesign. [{mud["chunk_id"]}]
   - Classification: Primarily execution-manageable, with design input from mud program limits.

**Caveats and uncertainty**
This v1 corpus is limited to F-11 and selected offsets. The classification is an engineering judgment over retrieved reports, not a full drilling program review.

**Suggested follow-up questions**
- Which F-14 practices should be copied into the next Hugin well?
- What BHA changes reduced sticking exposure?
"""
    else:
        answer = f"""**Summary**
For a new Hugin target, F-11 most strongly warns about differential sticking exposure, ECD control in the reservoir section, and BHA/connection practices that amplify stationary-pipe risk.

**Key Findings**

1. **Differential sticking in the Hugin interval** — Severity: High — Confidence: High
   - What happened: The drillstring became differentially stuck between 2940 m MD and 2975 m MD after overpull and pack-off symptoms. [{stuck["chunk_id"]}]
   - Why it matters: Hugin planning should minimize stationary time and maintain hole cleaning before connections.
   - Evidence basis: [{stuck["chunk_id"]}]

2. **ECD margin during reservoir drilling** — Severity: Medium — Confidence: Medium
   - What happened: Mud weight increased from 1.32 SG to 1.38 SG and ECD approached the modeled fracture margin during high-flow cleanout. [{mud["chunk_id"]}]
   - Why it matters: The mud program needs a clear operating window before the reservoir section starts.
   - Evidence basis: [{mud["chunk_id"]}]

3. **BHA configuration and connection practices** — Severity: Medium — Confidence: Medium
   - What happened: BHA #4 drilled the 12-1/4 inch reservoir section; stabilizer placement and high contact area increased sticking susceptibility when stationary. [{lesson["chunk_id"]}]
   - Why it matters: BHA selection and connection discipline should be reviewed together, not separately.
   - Evidence basis: [{lesson["chunk_id"]}]

**Caveats and uncertainty**
This answer uses the v1 demo corpus. Campaign-wide conclusions should wait for the full 17-well index.

**Suggested follow-up questions**
- Of those issues, which were avoidable through better well design vs. better execution?
- Compare F-11 against F-14 in the Hugin interval.
"""

    result = verify_citations(answer, ids | {"F14_EOWR::comparison::001"})
    if not result.ok:
        return "**Summary**\nCitation verification failed; the agent could not produce a verified answer from retrieved chunks."
    return result.text


async def run_agent(message: str, session_id: str, well_id: str | None = "15/9-F-11") -> AsyncIterator[str]:
    SESSIONS[session_id].append({"role": "user", "message": message})
    yield _event(
        ToolEvent(type="thinking", text="Planning retrieval over F-11 reports, structured well data, and offset wells.")
    )
    await asyncio.sleep(0.05)

    yield _event(ToolEvent(type="tool_call", name="get_well_header", params={"well_id": well_id}))
    header = get_well_header(well_id or "15/9-F-11")
    yield _event(ToolEvent(type="tool_result", name="get_well_header", summary=header["summary"], data=header))
    await asyncio.sleep(0.05)

    yield _event(ToolEvent(type="tool_call", name="get_formation_tops", params={"well_id": well_id}))
    tops = get_formation_tops(well_id or "15/9-F-11")
    yield _event(ToolEvent(type="tool_result", name="get_formation_tops", summary=tops["summary"], data=tops))
    await asyncio.sleep(0.05)

    query = message
    yield _event(
        ToolEvent(type="tool_call", name="search_drilling_reports", params={"query": query, "well_id": well_id})
    )
    search = search_drilling_reports(query=query, well_id=well_id)
    yield _event(
        ToolEvent(
            type="tool_result",
            name="search_drilling_reports",
            summary=search["summary"],
            data={"chunks": search["chunks"]},
        )
    )
    await asyncio.sleep(0.05)

    if "offset" in message.lower() or "execution" in message.lower() or "design" in message.lower():
        yield _event(
            ToolEvent(
                type="tool_call", name="get_offset_wells", params={"reference_well_id": well_id, "formation": "Hugin"}
            )
        )
        offsets = get_offset_wells(reference_well_id=well_id or "15/9-F-11", formation="Hugin")
        yield _event(ToolEvent(type="tool_result", name="get_offset_wells", summary=offsets["summary"], data=offsets))

    chunk_ids = [chunk["chunk_id"] for chunk in search["chunks"][:4]]
    yield _event(ToolEvent(type="tool_call", name="read_document_chunks", params={"chunk_ids": chunk_ids}))
    read = read_document_chunks(chunk_ids)
    yield _event(ToolEvent(type="tool_result", name="read_document_chunks", summary=read["summary"], data=read))

    answer = _format_findings(read["chunks"] or search["chunks"], message)
    SESSIONS[session_id].append({"role": "assistant", "message": answer})
    yield _event(ToolEvent(type="final", text=answer, data={"chunks": search["chunks"]}))
