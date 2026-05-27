#!/usr/bin/env python3
"""Create North Library and Agent resources for the EOWI demo."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.north_client import NorthClientError, NorthEowiClient  # noqa: E402
from app.prompts import SYSTEM_PROMPT  # noqa: E402

TERMINAL_JOB_STATES = {"COMPLETED", "FAILED"}


def _load_manifest(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("Curated manifest must be a JSON array.")
    return [item for item in data if isinstance(item, dict)]


def _candidate_paths(item: dict[str, Any]) -> list[Path]:
    doc_id = item.get("doc_id")
    source_path = item.get("source_path")
    candidates: list[Path] = []
    if doc_id:
        candidates.append(ROOT / "data" / "curated" / "pdfs" / f"{doc_id}.pdf")
    if source_path:
        source = Path(str(source_path))
        candidates.extend(
            [
                source if source.is_absolute() else ROOT / source,
                ROOT / "data" / source,
                ROOT / "data" / "curated" / source,
            ]
        )
    return candidates


def _resolve_files(manifest: list[dict[str, Any]], demo_critical_only: bool) -> list[Path]:
    files: list[Path] = []
    missing: list[str] = []
    for item in manifest:
        if demo_critical_only and not item.get("demo_critical"):
            continue
        found = next((candidate for candidate in _candidate_paths(item) if candidate.exists()), None)
        if found:
            files.append(found)
        else:
            missing.append(str(item.get("doc_id") or item.get("source_path") or "unknown"))

    if missing:
        print(
            json.dumps(
                {
                    "warning": "Some manifest entries do not have local files and will be skipped.",
                    "missing": missing,
                },
                indent=2,
            )
        )
    return files


def _write_state(path: Path, state: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def main() -> None:
    parser = argparse.ArgumentParser(description="Create North Library and Agent resources for EOWI.")
    parser.add_argument("--manifest", default="data/curated/manifest.json")
    parser.add_argument("--library-name", default="EOWI Volve Sprint 3 Library")
    parser.add_argument("--library-description", default="Curated Volve documents for the EOWI demo.")
    parser.add_argument("--agent-name", default="EOWI Drilling Intelligence Agent")
    parser.add_argument("--state-file", default="data/north/state.json")
    parser.add_argument("--all-files", action="store_true", help="Include non-demo-critical manifest entries.")
    parser.add_argument("--overwrite-files", action="store_true")
    parser.add_argument("--no-attach-existing-files", action="store_true")
    parser.add_argument("--poll-interval", type=float, default=5.0)
    parser.add_argument("--timeout-seconds", type=float, default=600.0)
    args = parser.parse_args()

    manifest = _load_manifest(ROOT / args.manifest)
    files = _resolve_files(manifest, demo_critical_only=not args.all_files)
    if not files:
        raise SystemExit("No local files were found for North Library upload.")

    client = NorthEowiClient()
    job = client.create_library_job(
        name=args.library_name,
        description=args.library_description,
        files=files,
        overwrite_files=args.overwrite_files,
        attach_existing_files=not args.no_attach_existing_files,
    )
    print(json.dumps({"library_job": job}, indent=2))

    started = time.monotonic()
    while job.get("state") not in TERMINAL_JOB_STATES:
        if time.monotonic() - started > args.timeout_seconds:
            raise SystemExit(f"Timed out waiting for North Library job {job.get('id')}")
        time.sleep(args.poll_interval)
        job = client.get_library_job(str(job["id"]))
        print(json.dumps({"library_job": job}, indent=2))

    if job.get("state") != "COMPLETED" or not job.get("library_id"):
        _write_state(ROOT / args.state_file, {"library_job": job})
        raise SystemExit("North Library job did not complete successfully.")

    library_id = str(job["library_id"])
    agent = client.create_agent(name=args.agent_name, preamble=SYSTEM_PROMPT, library_id=library_id)
    state = {
        "library_job": job,
        "library_id": library_id,
        "agent_id": agent.get("id"),
        "agent": agent,
    }
    _write_state(ROOT / args.state_file, state)
    print(json.dumps({"state_file": args.state_file, "library_id": library_id, "agent_id": agent.get("id")}, indent=2))


if __name__ == "__main__":
    try:
        main()
    except NorthClientError as exc:
        raise SystemExit(str(exc)) from exc
