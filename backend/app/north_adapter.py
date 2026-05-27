from __future__ import annotations

from typing import Any

from .models import NorthCitationSource, ToolEvent


def _content_text(content: Any) -> str:
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict):
                if item.get("type") == "text":
                    parts.append(str(item.get("text", "")))
                elif item.get("type") == "thinking":
                    parts.append(str(item.get("thinking") or item.get("text") or ""))
        return "\n".join(part for part in parts if part)
    if isinstance(content, dict):
        return str(content.get("text") or content.get("thinking") or "")
    return str(content)


def _source_title(source: dict[str, Any], fallback: str) -> str:
    payload = source.get("document") or source.get("tool_output") or {}
    for key in ("title", "name", "filename", "display_name"):
        value = payload.get(key) if isinstance(payload, dict) else None
        if value:
            return str(value)
    return fallback


def _source_snippet(source: dict[str, Any], citation_text: str) -> str:
    payload = source.get("document") or source.get("tool_output") or {}
    if isinstance(payload, dict):
        for key in ("text", "snippet", "content", "preview"):
            value = payload.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    return citation_text


def _normalize_citation_source(index: int, citation: dict[str, Any]) -> NorthCitationSource:
    sources = citation.get("sources") or []
    source = sources[0] if sources and isinstance(sources[0], dict) else {}
    source_id = str(source.get("id") or f"NORTH-{index + 1}")
    title = _source_title(source, source_id)
    snippet = _source_snippet(source, str(citation.get("text") or title))
    return NorthCitationSource(
        chunk_id=f"NORTH::{index + 1}",
        doc_id=source_id,
        section_path=title,
        chunk_text=snippet,
    )


def normalize_citation_sources(citations: list[dict[str, Any]]) -> list[NorthCitationSource]:
    return [_normalize_citation_source(index, citation) for index, citation in enumerate(citations)]


def _insert_markers(text: str, citations: list[dict[str, Any]], sources: list[NorthCitationSource]) -> str:
    if not citations:
        return text

    offset = 0
    marked = text
    for citation, source in zip(citations, sources, strict=False):
        marker = f" [{source.chunk_id}]"
        if marker.strip() in marked:
            continue
        citation_text = str(citation.get("text") or "")
        if citation_text and citation_text in marked:
            insert_at = marked.find(citation_text) + len(citation_text)
            marked = f"{marked[:insert_at]}{marker}{marked[insert_at:]}"
            offset += len(marker)
            continue

        start = citation.get("start")
        end = citation.get("end")
        if isinstance(start, int) and isinstance(end, int) and 0 <= start <= end <= len(text):
            insert_at = end + offset
            marked = f"{marked[:insert_at]}{marker}{marked[insert_at:]}"
            offset += len(marker)
            continue

    return marked


def insert_citation_markers(text: str, citations: list[dict[str, Any]], sources: list[NorthCitationSource]) -> str:
    return _insert_markers(text, citations, sources)


def adapt_north_chat_response(response: dict[str, Any]) -> tuple[str, list[dict[str, Any]], list[ToolEvent]]:
    messages = response.get("messages") or []
    assistant_messages = [
        message for message in messages if isinstance(message, dict) and message.get("role") == "assistant"
    ]
    assistant = assistant_messages[-1] if assistant_messages else {}

    text = _content_text(assistant.get("content"))
    citations = assistant.get("citations") or []
    citations = [citation for citation in citations if isinstance(citation, dict)]
    sources = normalize_citation_sources(citations)
    text = _insert_markers(text, citations, sources)

    events: list[ToolEvent] = []
    tool_plan = assistant.get("tool_plan")
    if tool_plan:
        events.append(ToolEvent(type="thinking", text=str(tool_plan)))

    for tool_call in assistant.get("tool_calls") or []:
        if not isinstance(tool_call, dict):
            continue
        name = tool_call.get("display_name") or tool_call.get("tool_id") or "north_tool"
        events.append(ToolEvent(type="tool_call", name=str(name), params=tool_call))
        state = tool_call.get("state")
        events.append(ToolEvent(type="tool_result", name=str(name), summary=f"North tool state: {state or 'unknown'}"))

    if not text and assistant.get("error"):
        text = f"North returned an error: {assistant['error']}"

    return text, [source.model_dump() for source in sources], events


class NorthStreamAdapter:
    def __init__(self) -> None:
        self._thinking = ""
        self._text_parts: list[str] = []
        self._citations: list[dict[str, Any]] = []
        self._tool_names: dict[int, str] = {}
        self._tool_args: dict[int, str] = {}

    def _flush_thinking(self) -> ToolEvent | None:
        text = self._thinking.strip()
        self._thinking = ""
        if not text:
            return None
        if len(text) > 360:
            text = f"{text[:357]}..."
        return ToolEvent(type="thinking", text=text)

    def _tool_call(self, event: dict[str, Any]) -> dict[str, Any]:
        return event.get("delta", {}).get("message", {}).get("tool_calls") or {}

    def _content(self, event: dict[str, Any]) -> dict[str, Any]:
        content = event.get("delta", {}).get("message", {}).get("content") or {}
        return content if isinstance(content, dict) else {}

    def process(self, event: dict[str, Any]) -> list[ToolEvent]:
        event_type = event.get("type")
        events: list[ToolEvent] = []

        if event_type == "content-delta":
            content = self._content(event)
            if content.get("type") == "thinking":
                self._thinking += str(content.get("thinking") or content.get("text") or "")
                if len(self._thinking) >= 180 and self._thinking.endswith((" ", ".", "\n")):
                    flushed = self._flush_thinking()
                    if flushed:
                        events.append(flushed)
            elif content.get("type") == "text":
                self._text_parts.append(str(content.get("text") or ""))
            elif content.get("type") == "document":
                document = content.get("document") or {}
                data = document.get("data") if isinstance(document, dict) else {}
                title = data.get("title") if isinstance(data, dict) else None
                events.append(
                    ToolEvent(
                        type="tool_result",
                        name="north_my_files",
                        summary=f"Retrieved {title or 'North document result'}",
                        data={"document": document},
                    )
                )

        elif event_type == "content-end":
            flushed = self._flush_thinking()
            if flushed:
                events.append(flushed)

        elif event_type == "tool-plan-delta":
            message = event.get("delta", {}).get("message", {})
            plan = message.get("tool_plan")
            if plan:
                events.append(ToolEvent(type="thinking", text=str(plan)))

        elif event_type == "tool-call-start":
            index = int(event.get("index") or 0)
            tool_call = self._tool_call(event)
            function = tool_call.get("function") if isinstance(tool_call.get("function"), dict) else {}
            name = str(
                tool_call.get("display_name") or function.get("name") or tool_call.get("tool_id") or "north_tool"
            )
            self._tool_names[index] = name
            self._tool_args[index] = str(function.get("arguments") or "")
            events.append(ToolEvent(type="tool_call", name=name, params=tool_call))

        elif event_type == "tool-call-delta":
            index = int(event.get("index") or 0)
            tool_call = self._tool_call(event)
            function = tool_call.get("function") if isinstance(tool_call.get("function"), dict) else {}
            self._tool_args[index] = self._tool_args.get(index, "") + str(function.get("arguments") or "")

        elif event_type == "tool-call-end":
            index = int(event.get("index") or 0)
            name = self._tool_names.get(index, "north_tool")
            args = self._tool_args.get(index)
            events.append(
                ToolEvent(type="tool_result", name=name, summary="North tool call completed.", data={"arguments": args})
            )

        elif event_type == "citation-start":
            citation = event.get("delta", {}).get("message", {}).get("citations")
            if isinstance(citation, dict):
                self._citations.append(citation)

        return events

    def finalize(self) -> tuple[str, list[dict[str, Any]]]:
        text = "".join(self._text_parts).strip()
        sources = normalize_citation_sources(self._citations)
        text = insert_citation_markers(text, self._citations, sources)
        return text, [source.model_dump() for source in sources]
