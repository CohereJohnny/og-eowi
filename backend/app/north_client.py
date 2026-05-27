from __future__ import annotations

from collections.abc import Iterator, Mapping, Sequence
from pathlib import Path
from typing import Any

from north import NorthClient

from .north_settings import NorthRuntimeConfig, get_north_runtime_config


class NorthClientError(RuntimeError):
    """Raised when North cannot satisfy a backend operation safely."""


def _sdk_base_url(api_base_url: str) -> str:
    """Normalize the North SDK base URL while preserving the `/api` suffix required by this instance."""
    return api_base_url.rstrip("/")


def _safe_error(exc: Exception) -> str:
    message = str(exc).splitlines()[0]
    if len(message) > 240:
        message = f"{message[:240]}..."
    return message


def _dump(value: Any) -> dict[str, Any]:
    if value is None:
        return {}
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json", exclude_none=True)
    if isinstance(value, Mapping):
        return dict(value)
    return {"value": value}


class NorthEowiClient:
    def __init__(self, config: NorthRuntimeConfig | None = None) -> None:
        self.config = config or get_north_runtime_config()
        if not self.config.bearer_token:
            raise NorthClientError("NORTH_BEARER_TOKEN is not configured server-side.")
        self._client = NorthClient(
            base_url=_sdk_base_url(self.config.base_url),
            auth_token=self.config.bearer_token,
            timeout=self.config.request_timeout_seconds,
        )

    def check_connection(self) -> dict[str, Any]:
        try:
            libraries = self._client.libraries.list(limit=1)
            return _dump(libraries)
        except Exception as exc:  # SDK exceptions vary by endpoint.
            raise NorthClientError(f"North connection check failed: {_safe_error(exc)}") from exc

    def create_library_job(
        self,
        *,
        name: str,
        files: Sequence[Path],
        description: str | None = None,
        overwrite_files: bool = False,
        attach_existing_files: bool = True,
    ) -> dict[str, Any]:
        if not files:
            raise NorthClientError("At least one file is required to create a North Library job.")

        handles = []
        try:
            upload_files = []
            for path in files:
                handle = path.open("rb")
                handles.append(handle)
                upload_files.append(
                    (path.name, handle, "application/pdf" if path.suffix.lower() == ".pdf" else "text/plain")
                )

            response = self._client.libraries.create_job(
                name=name,
                description=description,
                files=upload_files,
                overwrite_files=overwrite_files,
                attach_existing_files=attach_existing_files,
            )
            return _dump(response)
        except Exception as exc:
            raise NorthClientError(f"North Library job creation failed: {_safe_error(exc)}") from exc
        finally:
            for handle in handles:
                handle.close()

    def get_library_job(self, job_id: str) -> dict[str, Any]:
        try:
            return _dump(self._client.libraries.get_job(job_id))
        except Exception as exc:
            raise NorthClientError(f"North Library job polling failed: {_safe_error(exc)}") from exc

    def get_library(self, library_id: str) -> dict[str, Any]:
        try:
            return _dump(self._client.libraries.get(library_id))
        except Exception as exc:
            raise NorthClientError(f"North Library lookup failed: {_safe_error(exc)}") from exc

    def create_agent(self, *, name: str, preamble: str, library_id: str | None = None) -> dict[str, Any]:
        tools = None
        if library_id:
            tools = [
                {
                    "type": "north_tool",
                    "north_tool": {
                        "name": "my_drive",
                        "options": {"library_ids": [library_id]},
                    },
                }
            ]

        try:
            response = self._client.agents.create(
                name=name,
                visibility="private",
                preamble=preamble,
                tools=tools,
            )
            return _dump(response)
        except Exception as exc:
            raise NorthClientError(f"North agent creation failed: {_safe_error(exc)}") from exc

    def get_agent(self, agent_id: str) -> dict[str, Any]:
        try:
            return _dump(self._client.agents.get(agent_id))
        except Exception as exc:
            raise NorthClientError(f"North agent lookup failed: {_safe_error(exc)}") from exc

    def _library_file_ids(self, library_id: str | None) -> list[str] | None:
        if not library_id:
            return None
        library = self.get_library(library_id)
        artifact_ids = [
            str(artifact["id"])
            for artifact in library.get("artifacts", [])
            if isinstance(artifact, dict) and artifact.get("type") == "file" and artifact.get("id")
        ]
        return artifact_ids or None

    def chat(self, *, message: str, agent_id: str, session_id: str, library_id: str | None = None) -> dict[str, Any]:
        try:
            response = self._client.chat(
                messages=[{"role": "user", "content": message}],
                agent={"id": agent_id},
                client_id=session_id,
                stateless=False,
                file_ids=self._library_file_ids(library_id),
            )
            return _dump(response)
        except Exception as exc:
            raise NorthClientError(f"North chat failed: {_safe_error(exc)}") from exc

    def chat_stream(
        self, *, message: str, agent_id: str, session_id: str, library_id: str | None = None
    ) -> Iterator[dict[str, Any]]:
        try:
            stream = self._client.chat_stream(
                messages=[{"role": "user", "content": message}],
                agent={"id": agent_id},
                client_id=session_id,
                stateless=False,
                file_ids=self._library_file_ids(library_id),
            )
            for event in stream:
                yield _dump(event)
        except Exception as exc:
            raise NorthClientError(f"North chat stream failed: {_safe_error(exc)}") from exc
