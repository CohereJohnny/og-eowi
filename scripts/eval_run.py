#!/usr/bin/env python3
"""Run a lightweight eval suite against the local agent primitives."""

from __future__ import annotations

import argparse
import asyncio
import json
import re
import sys
import time
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.agent import run_agent  # noqa: E402


async def collect_answer(question: str) -> tuple[str, float]:
    start = time.perf_counter()
    answer = ""
    async for frame in run_agent(question, session_id=f"eval-{hash(question)}"):
        if frame.startswith("data: "):
            payload = json.loads(frame[6:].strip())
            if payload.get("type") == "final":
                answer = payload.get("text", "")
    return answer, time.perf_counter() - start


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--questions", default="eval/questions.yaml")
    parser.add_argument("--out", default="eval/runs/latest.json")
    args = parser.parse_args()

    with Path(args.questions).open("r", encoding="utf-8") as f:
        questions = yaml.safe_load(f)["questions"]

    results = []
    for item in questions:
        answer, latency = await collect_answer(item["question"])
        cited = bool(re.search(r"\[[^\]]+\]", answer))
        passed = latency <= 30 and (cited or not item.get("must_cite", False))
        results.append(
            {
                "id": item["id"],
                "category": item["category"],
                "latency_s": round(latency, 3),
                "cited": cited,
                "passed": passed,
            }
        )

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        json.dump({"results": results}, f, indent=2)
    print(json.dumps({"passed": sum(r["passed"] for r in results), "total": len(results), "out": str(out)}, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
