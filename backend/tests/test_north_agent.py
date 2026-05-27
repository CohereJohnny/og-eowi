import asyncio
import json
from collections.abc import AsyncIterator

from app.north_agent import run_north_agent
from app.north_settings import _runtime_overrides


async def _fallback(message: str, session_id: str, well_id: str | None = None) -> AsyncIterator[str]:
    del message, session_id, well_id
    yield 'data: {"type":"final","text":"fallback"}\n\n'


def test_run_north_agent_falls_back_when_config_missing() -> None:
    _runtime_overrides.clear()
    _runtime_overrides.update({"mode": "north", "base_url": "https://demo.north.cohere.com/api", "bearer_token": ""})

    async def collect() -> list[dict]:
        events = []
        async for frame in run_north_agent("question", "session", local_fallback=_fallback):
            if frame.startswith("data: "):
                events.append(json.loads(frame[6:].strip()))
        return events

    events = asyncio.run(collect())

    assert events[0]["type"] == "warning"
    assert events[-1]["text"] == "fallback"
    _runtime_overrides.clear()
