#!/usr/bin/env python3
"""Parse extracted PDF JSON into DDR/EOWR sections."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


SECTION_PATTERNS = {
    "problems_encountered": re.compile(r"problems?\s+encountered|stuck|pack-off", re.I),
    "mud_properties": re.compile(r"mud\s+properties|mud\s+weight|ECD", re.I),
    "bha_description": re.compile(r"BHA|bottom\s+hole\s+assembly|rotary\s+steerable", re.I),
    "lessons_learned": re.compile(r"lessons?\s+learned|recommend", re.I),
    "operations_summary": re.compile(r"operations?\s+summary|drilling\s+summary", re.I),
}


def classify_section(text: str) -> str:
    for name, pattern in SECTION_PATTERNS.items():
        if pattern.search(text):
            return name
    return "whole_page"


def parse_file(path: Path, out_dir: Path) -> Path:
    with path.open("r", encoding="utf-8") as f:
        extracted = json.load(f)

    sections = []
    for page in extracted.get("pages", []):
        text = page.get("text", "")
        section = classify_section(text)
        sections.append(
            {
                "doc_id": extracted["doc_id"],
                "source_path": extracted.get("source_path"),
                "section": section,
                "section_path": f"Extracted PDF > {section.replace('_', ' ').title()}",
                "page_start": page["page_no"],
                "page_end": page["page_no"],
                "text": text,
                "bbox": page.get("layout_blocks", [{}])[0].get("bbox", [72, 144, 540, 640]),
            }
        )

    output = out_dir / f"{extracted['doc_id']}.json"
    with output.open("w", encoding="utf-8") as f:
        json.dump({"doc_id": extracted["doc_id"], "sections": sections}, f, indent=2)
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--out-dir", default="data/parsed")
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    print(parse_file(Path(args.input), out_dir))


if __name__ == "__main__":
    main()
