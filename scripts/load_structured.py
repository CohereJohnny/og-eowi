#!/usr/bin/env python3
"""Populate a lightweight DuckDB database from the active corpus JSON."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--corpus", default="data/mock/corpus.json")
    parser.add_argument("--out", default="data/index/eowi.duckdb")
    args = parser.parse_args()

    import duckdb

    with Path(args.corpus).open("r", encoding="utf-8") as f:
        corpus = json.load(f)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(out))

    for table in ("wells", "formation_tops", "documents", "chunks"):
        con.execute(f"DROP TABLE IF EXISTS {table}")

    con.execute("CREATE TABLE wells AS SELECT * FROM read_json_auto(?)", [json.dumps(corpus["wells"])])
    con.execute(
        "CREATE TABLE formation_tops AS SELECT * FROM read_json_auto(?)", [json.dumps(corpus["formation_tops"])]
    )
    con.execute("CREATE TABLE documents AS SELECT * FROM read_json_auto(?)", [json.dumps(corpus["documents"])])
    con.execute("CREATE TABLE chunks AS SELECT * FROM read_json_auto(?)", [json.dumps(corpus["chunks"])])
    con.close()
    print(out)


if __name__ == "__main__":
    main()
