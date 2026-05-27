from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncIterator, Callable

from .agent import run_agent as run_local_agent
from .models import ToolEvent
from .north_adapter import NorthStreamAdapter, adapt_north_chat_response
from .north_client import NorthClientError, NorthEowiClient
from .north_settings import get_north_runtime_config


def _event(event: ToolEvent) -> str:
    return f"data: {json.dumps(event.model_dump(exclude_none=True))}\n\n"


def _next_or_none(iterator):
    try:
        return next(iterator)
    except StopIteration:
        return None


async def run_north_agent(
    message: str,
    session_id: str,
    well_id: str | None = "15/9-F-11",
    local_fallback: Callable[[str, str, str | None], AsyncIterator[str]] = run_local_agent,
) -> AsyncIterator[str]:
    config = get_north_runtime_config()
    if not config.north_ready or not config.agent_id:
        yield _event(ToolEvent(type="warning", text="North is not fully configured. Using local fallback mode."))
        async for frame in local_fallback(message, session_id, well_id):
            yield frame
        return

    yield _event(ToolEvent(type="thinking", text="Routing request to the North-hosted EOWI agent."))
    yield _event(
        ToolEvent(
            type="tool_call",
            name="north_agent_chat",
            params={"agent_id": config.agent_id, "library_id": config.library_id, "well_id": well_id},
        )
    )
    yield _event(
        ToolEvent(
            type="thinking",
            text=f"Waiting for North response. Local fallback will activate after {int(config.request_timeout_seconds)} seconds.",
        )
    )

    client: NorthEowiClient | None = None
    try:
        client = NorthEowiClient(config)
        stream = client.chat_stream(
            message=message,
            agent_id=config.agent_id,
            session_id=session_id,
            library_id=config.library_id,
        )
        adapter = NorthStreamAdapter()
        while True:
            event = await asyncio.wait_for(
                asyncio.to_thread(_next_or_none, stream),
                timeout=config.request_timeout_seconds + 5,
            )
            if event is None:
                break
            for mapped in adapter.process(event):
                yield _event(mapped)
        text, citation_sources = adapter.finalize()
    except TimeoutError:
        yield _event(
            ToolEvent(
                type="warning",
                text="North chat timed out before returning a final answer. Using local fallback mode.",
            )
        )
        async for frame in local_fallback(message, session_id, well_id):
            yield frame
        return
    except NorthClientError as exc:
        if client is None:
            yield _event(ToolEvent(type="warning", text=f"{exc} Using local fallback mode."))
            async for frame in local_fallback(message, session_id, well_id):
                yield frame
            return
        yield _event(ToolEvent(type="warning", text=f"{exc} Retrying North chat without streaming."))
        try:
            response = await asyncio.wait_for(
                asyncio.to_thread(
                    client.chat,
                    message=message,
                    agent_id=config.agent_id,
                    session_id=session_id,
                    library_id=config.library_id,
                ),
                timeout=config.request_timeout_seconds + 5,
            )
            text, citation_sources, north_events = adapt_north_chat_response(response)
            for event in north_events:
                yield _event(event)
        except (TimeoutError, NorthClientError) as retry_exc:
            yield _event(ToolEvent(type="warning", text=f"{retry_exc} Using local fallback mode."))
            async for frame in local_fallback(message, session_id, well_id):
                yield frame
            return

    yield _event(ToolEvent(type="tool_result", name="north_agent_chat", summary="North agent response received."))

    if not text:
        yield _event(
            ToolEvent(type="warning", text="North response did not include final text. Using local fallback mode.")
        )
        async for frame in local_fallback(message, session_id, well_id):
            yield frame
        return

    yield _event(ToolEvent(type="final", text=text, data={"chunks": citation_sources, "sources": citation_sources}))
