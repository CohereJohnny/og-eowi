import json
from pathlib import Path

from app import north_settings
from app.config import get_settings
from app.models import NorthSettingsRequest
from app.north_settings import _runtime_overrides, public_north_status, update_north_settings


def test_north_status_does_not_expose_bearer_token() -> None:
    _runtime_overrides.clear()
    status = update_north_settings(
        NorthSettingsRequest(
            base_url="https://demo.north.cohere.com/api",
            bearer_token="secret-token",
            agent_id="agent-123",
            library_id="library-123",
            mode="north",
        )
    )

    payload = status.model_dump()
    assert payload["token_configured"] is True
    assert "secret-token" not in str(payload)
    assert payload["active_mode"] == "north"

    _runtime_overrides.clear()


def test_missing_north_config_uses_local_fallback_status() -> None:
    _runtime_overrides.clear()
    status = public_north_status()

    assert status.active_mode in {"local", "north"}
    if not status.token_configured:
        assert status.active_mode == "local"


def test_north_status_uses_generated_state_for_non_secret_ids(tmp_path, monkeypatch) -> None:
    state_file = tmp_path / "data" / "north" / "state.json"
    state_file.parent.mkdir(parents=True)
    state_file.write_text(
        json.dumps({"agent_id": "agent-from-state", "library_id": "library-from-state"}),
        encoding="utf-8",
    )
    monkeypatch.setattr(north_settings, "_repo_root", lambda: Path(tmp_path))
    monkeypatch.delenv("NORTH_AGENT_ID", raising=False)
    monkeypatch.delenv("NORTH_LIBRARY_ID", raising=False)
    get_settings.cache_clear()
    _runtime_overrides.clear()
    _runtime_overrides.update({"bearer_token": "token-from-runtime"})

    status = public_north_status()

    assert status.agent_id == "agent-from-state"
    assert status.library_id == "library-from-state"
    assert status.north_ready is True
    assert north_settings.get_north_runtime_config().request_timeout_seconds > 0

    _runtime_overrides.clear()
    get_settings.cache_clear()
