#!/usr/bin/env python3
"""Export the v1 Volve subset from a Databricks volume to local data/raw.

The script assumes the Databricks volume is mounted on the machine running it.
It is safe to rerun: files with matching size are skipped.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path
import yaml


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def should_copy(source: Path, dest: Path) -> bool:
    return not dest.exists() or source.stat().st_size != dest.stat().st_size


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="scripts/wells.yaml")
    parser.add_argument("--source", default=None)
    parser.add_argument("--out", default="data/raw")
    parser.add_argument("--manifest", default="data/curated/export_manifest.json")
    args = parser.parse_args()

    with Path(args.config).open("r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    source_root = Path(args.source or config["databricks_volume"])
    out_root = Path(args.out)
    out_root.mkdir(parents=True, exist_ok=True)
    Path(args.manifest).parent.mkdir(parents=True, exist_ok=True)

    folder_names = list(config["source_folders"].values())
    copied: list[dict] = []
    failures: list[dict] = []

    for well in config["v1_wells"]:
        terms = [well["well_id"], *well.get("aliases", [])]
        for folder in folder_names:
            folder_path = source_root / folder
            if not folder_path.exists():
                failures.append({"folder": str(folder_path), "reason": "missing source folder"})
                continue
            for source in folder_path.rglob("*"):
                if not source.is_file():
                    continue
                haystack = str(source).lower()
                if not any(term.lower() in haystack for term in terms):
                    continue
                relative = source.relative_to(source_root)
                dest = out_root / well["well_id"] / relative
                dest.parent.mkdir(parents=True, exist_ok=True)
                try:
                    if should_copy(source, dest):
                        shutil.copy2(source, dest)
                    copied.append(
                        {
                            "well_id": well["well_id"],
                            "source": str(source),
                            "dest": str(dest),
                            "size": source.stat().st_size,
                            "sha256": file_hash(dest),
                        }
                    )
                except Exception as exc:
                    failures.append({"source": str(source), "reason": str(exc)})

    with Path(args.manifest).open("w", encoding="utf-8") as f:
        json.dump({"copied": copied, "failures": failures}, f, indent=2)

    print(f"Copied/skipped {len(copied)} files; {len(failures)} failures. Manifest: {args.manifest}")


if __name__ == "__main__":
    main()
