#!/usr/bin/env python3
"""Convert parsed sections into retrieval chunks with light enrichment."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

DEPTH_RE = re.compile(r"(\d{3,5}(?:\.\d+)?)\s*m\s*MD", re.I)


def chunk_text(text: str, max_words: int = 450, overlap: int = 50) -> list[str]:
    words = text.split()
    if len(words) <= max_words:
        return [text]
    chunks = []
    start = 0
    while start < len(words):
        end = min(start + max_words, len(words))
        chunks.append(" ".join(words[start:end]))
        if end == len(words):
            break
        start = max(0, end - overlap)
    return chunks


def depths(text: str) -> tuple[float | None, float | None]:
    found = [float(match) for match in DEPTH_RE.findall(text)]
    if not found:
        return None, None
    return min(found), max(found)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--out", default="data/index/chunks.json")
    parser.add_argument("--well-id", default=None)
    parser.add_argument("--doc-type", default="DDR")
    args = parser.parse_args()

    with Path(args.input).open("r", encoding="utf-8") as f:
        parsed = json.load(f)

    chunks = []
    seq = 1
    for section in parsed.get("sections", []):
        for text in chunk_text(section["text"]):
            start_depth, end_depth = depths(text)
            chunks.append(
                {
                    "chunk_id": f"{section['doc_id']}::{section['section']}::{seq:03d}",
                    "doc_id": section["doc_id"],
                    "well_id": args.well_id,
                    "doc_type": args.doc_type,
                    "chunk_seq": seq,
                    "page_start": section["page_start"],
                    "page_end": section["page_end"],
                    "section_path": section["section_path"],
                    "depth_md_start_m": start_depth,
                    "depth_md_end_m": end_depth,
                    "chunk_text": text,
                    "bbox": section["bbox"],
                    "token_count": len(text.split()),
                }
            )
            seq += 1

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2)
    print(out)


if __name__ == "__main__":
    main()
