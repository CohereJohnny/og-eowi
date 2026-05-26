#!/usr/bin/env python3
"""Build local demo indexes.

For v1 local validation this writes a consolidated `data/index/corpus.json`.
When COHERE_API_KEY is set, this script is the extension point for Embed v4 and
LanceDB writes; the backend interface already consumes the same corpus shape.
"""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--corpus", default="data/mock/corpus.json")
    parser.add_argument("--out-dir", default="data/index")
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(args.corpus, out_dir / "corpus.json")

    with Path(args.corpus).open("r", encoding="utf-8") as f:
        corpus = json.load(f)
    metadata = {
        "chunk_count": len(corpus.get("chunks", [])),
        "document_count": len(corpus.get("documents", [])),
        "index_type": "local-json-bm25-compatible",
    }
    with (out_dir / "index_metadata.json").open("w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    print(out_dir / "corpus.json")


if __name__ == "__main__":
    main()
