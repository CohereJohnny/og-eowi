#!/usr/bin/env python3
"""CLI retrieval smoke test."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.retrieval import hybrid_retrieve  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("query")
    parser.add_argument("--well-id", default="15/9-F-11")
    args = parser.parse_args()

    for chunk in hybrid_retrieve(args.query, well_filter=[args.well_id], top_k=8):
        print(f"{chunk.score:.3f} {chunk.chunk_id} | {chunk.section_path}")
        print(f"  {chunk.chunk_text[:240]}")


if __name__ == "__main__":
    main()
