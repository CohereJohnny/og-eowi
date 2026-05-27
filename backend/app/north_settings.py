import json
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from .config import get_settings
from .models import NorthSettingsRequest, NorthStatus

Mode = Literal["auto", "north", "local"]


@dataclass
class NorthRuntimeConfig:
    base_url: str
    bearer_token: str | None
    agent_id: str | None
    library_id: str | None
    mode: Mode
    source: Literal["env", "runtime"]
    request_timeout_seconds: float

    @property
    def token_configured(self) -> bool:
        return bool(self.bearer_token)

    @property
    def north_ready(self) -> bool:
        return bool(self.base_url and self.bearer_token and self.agent_id and self.library_id)

    @property
    def active_mode(self) -> Literal["north", "local"]:
        if self.mode == "local":
            return "local"
        if self.mode == "north" or self.north_ready:
            return "north"
        return "local"


_runtime_overrides: dict[str, str] = {}


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _north_state() -> dict[str, str]:
    state_file = _repo_root() / "data" / "north" / "state.json"
    if not state_file.exists():
        return {}
    try:
        with state_file.open("r", encoding="utf-8") as f:
            state = json.load(f)
    except (OSError, json.JSONDecodeError):
        return {}
    return {
        "agent_id": state.get("agent_id") or "",
        "library_id": state.get("library_id") or "",
    }


def _clean(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


def update_north_settings(request: NorthSettingsRequest) -> NorthStatus:
    if request.base_url is not None:
        cleaned = _clean(request.base_url)
        if cleaned:
            _runtime_overrides["base_url"] = cleaned.rstrip("/")
    if request.bearer_token is not None:
        cleaned = _clean(request.bearer_token)
        if cleaned:
            _runtime_overrides["bearer_token"] = cleaned
    if request.agent_id is not None:
        cleaned = _clean(request.agent_id)
        if cleaned:
            _runtime_overrides["agent_id"] = cleaned
    if request.library_id is not None:
        cleaned = _clean(request.library_id)
        if cleaned:
            _runtime_overrides["library_id"] = cleaned
    if request.mode is not None:
        _runtime_overrides["mode"] = request.mode

    return public_north_status()


def get_north_runtime_config() -> NorthRuntimeConfig:
    settings = get_settings()
    state = _north_state()
    source: Literal["env", "runtime"] = "runtime" if _runtime_overrides else "env"
    mode = _runtime_overrides.get("mode", settings.north_mode)
    if mode not in {"auto", "north", "local"}:
        mode = "auto"
    return NorthRuntimeConfig(
        base_url=_runtime_overrides.get("base_url", settings.north_base_url).rstrip("/"),
        bearer_token=_runtime_overrides.get("bearer_token", settings.north_bearer_token),
        agent_id=_runtime_overrides.get("agent_id", settings.north_agent_id or state.get("agent_id")),
        library_id=_runtime_overrides.get("library_id", settings.north_library_id or state.get("library_id")),
        mode=mode,  # type: ignore[arg-type]
        source=source,
        request_timeout_seconds=settings.north_request_timeout_seconds,
    )


def public_north_status() -> NorthStatus:
    config = get_north_runtime_config()
    if config.active_mode == "north" and config.north_ready:
        message = "North is configured and ready."
    elif config.mode == "north":
        message = "North mode is selected, but required server-side configuration is missing."
    else:
        message = "Local fallback mode is active until North configuration is complete."

    return NorthStatus(
        mode=config.mode,
        active_mode=config.active_mode,
        base_url=config.base_url,
        token_configured=config.token_configured,
        agent_id=config.agent_id,
        library_id=config.library_id,
        north_ready=config.north_ready,
        source=config.source,
        message=message,
    )
