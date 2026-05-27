#!/usr/bin/env python3
"""Curate exported Volve files into data/curated for North Library upload.

Reads export manifest from fetch_volve_databricks.py (or scans data/raw),
selects demo-critical documents, copies PDFs to data/curated/pdfs/{doc_id}.pdf,
and writes data/curated/manifest.json.
"""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

import yaml

DOC_TYPE_HINTS = {
    "ddr": "DDR",
    "eowr": "EOWR",
    "completion": "COMPLETION_RPT",
    "geo": "GEO_RPT",
}


def infer_doc_type(path: Path) -> str:
    name = path.name.lower()
    if "ddr" in name or "daily" in name:
        return "DDR"
    if "eowr" in name or "end_of_well" in name or "end-of-well" in name:
        return "EOWR"
    if "completion" in name:
        return "COMPLETION_RPT"
    if "geo" in name or "geolog" in name:
        return "GEO_RPT"
    return "REPORT"


def main() -> None:
    parser = argparse.ArgumentParser(description="Curate Volve PDFs for North upload")
    parser.add_argument("--config", default="scripts/wells.yaml")
    parser.add_argument("--export-manifest", default="data/curated/export_manifest.json")
    parser.add_argument("--raw-root", default="data/raw")
    parser.add_argument("--out-manifest", default="data/curated/manifest.json")
    parser.add_argument("--pdf-dir", default="data/curated/pdfs")
    parser.add_argument("--demo-critical-only", action="store_true", default=True)
    args = parser.parse_args()

    with Path(args.config).open("r", encoding="utf-8") as f:
        wells_cfg = yaml.safe_load(f)

    raw_root = Path(args.raw_root)
    pdf_dir = Path(args.pdf_dir)
    pdf_dir.mkdir(parents=True, exist_ok=True)

    entries: list[dict] = []
    seen_doc_ids: set[str] = set()

    export_manifest = Path(args.export_manifest)
    if export_manifest.exists():
        with export_manifest.open("r", encoding="utf-8") as f:
            export_data = json.load(f)
        for item in export_data.get("copied", []):
            dest = Path(item["dest"])
            if not dest.exists() or not dest.suffix.lower() == ".pdf":
                continue
            well_id = item.get("well_id") or _well_from_path(dest)
            doc_id = _doc_id_from_path(dest)
            if doc_id in seen_doc_ids:
                continue
            seen_doc_ids.add(doc_id)
            doc_type = infer_doc_type(dest)
            demo_critical = _is_demo_critical(wells_cfg, well_id, doc_type)
            if args.demo_critical_only and not demo_critical:
                continue
            target = pdf_dir / f"{doc_id}.pdf"
            shutil.copy2(dest, target)
            entries.append(
                {
                    "doc_id": doc_id,
                    "well_id": well_id,
                    "doc_type": doc_type,
                    "title": doc_id.replace("_", " "),
                    "source_path": str(dest.relative_to(raw_root.parent)),
                    "databricks_source": item.get("source", str(dest)),
                    "extraction_method": "databricks_export",
                    "quality_flag": "good",
                    "demo_critical": demo_critical,
                }
            )
    else:
        for well in wells_cfg.get("v1_wells", []):
            well_id = well["well_id"]
            for path in sorted(raw_root.rglob("*.pdf")):
                doc_type = infer_doc_type(path)
                if args.demo_critical_only and not _is_demo_critical(wells_cfg, well_id, doc_type):
                    continue
                doc_id = _doc_id_from_path(path)
                if doc_id in seen_doc_ids:
                    continue
                seen_doc_ids.add(doc_id)
                rel = path.relative_to(raw_root)
                target = pdf_dir / f"{doc_id}.pdf"
                shutil.copy2(path, target)
                entries.append(
                    {
                        "doc_id": doc_id,
                        "well_id": well_id,
                        "doc_type": doc_type,
                        "title": doc_id.replace("_", " "),
                        "source_path": str(rel),
                        "databricks_source": f"{wells_cfg.get('databricks_volume', '')}/{rel.as_posix()}",
                        "extraction_method": "databricks_export",
                        "quality_flag": "good",
                        "demo_critical": True,
                    }
                )

    with Path(args.out_manifest).open("w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2)

    print(f"Curated {len(entries)} PDFs into {pdf_dir}")
    print(f"Manifest: {args.out_manifest}")


def _well_from_path(path: Path) -> str:
    parts = path.parts
    for part in reversed(parts):
        if part.startswith("15/9-"):
            return part
    return "unknown"


def _doc_id_from_path(path: Path) -> str:
    stem = path.stem.replace(" ", "_").replace("-", "_")
    return stem


def _is_demo_critical(cfg: dict, well_id: str, doc_type: str) -> bool:
    for well in cfg.get("v1_wells", []):
        if well.get("well_id") != well_id:
            continue
        if well.get("role") == "primary":
            return True
        if doc_type in ("DDR", "EOWR") and well.get("role") == "offset":
            return True
    return doc_type in ("DDR", "EOWR")


if __name__ == "__main__":
    main()
