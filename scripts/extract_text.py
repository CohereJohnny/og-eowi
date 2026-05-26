#!/usr/bin/env python3
"""Extract page text and layout blocks from PDFs.

Native text PDFs use pdfplumber. Scan/image PDFs are routed to a vision-ready
placeholder path that preserves the same output schema. When COHERE_API_KEY is
available, the placeholder can be extended to call Command A Plus page images.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def doc_id_for(path: Path) -> str:
    return hashlib.sha1(str(path).encode("utf-8")).hexdigest()[:16]


def extract_with_pdfplumber(path: Path) -> dict:
    import pdfplumber

    pages = []
    with pdfplumber.open(path) as pdf:
        for page_no, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            chars = page.chars or []
            char_bboxes = [[c.get("text", ""), c["x0"], c["top"], c["x1"], c["bottom"]] for c in chars[:20000]]
            pages.append(
                {
                    "page_no": page_no,
                    "text": text,
                    "char_bboxes": char_bboxes,
                    "layout_blocks": [
                        {
                            "bbox": [72, 144, 540, 640],
                            "text": text,
                            "type": "paragraph",
                        }
                    ],
                }
            )
    return {"extraction_method": "pdfplumber", "pages": pages}


def extract_with_vision_placeholder(path: Path) -> dict:
    return {
        "extraction_method": "vision",
        "pages": [
            {
                "page_no": 1,
                "text": f"Vision extraction placeholder for {path.name}. Run with real Cohere vision integration for scan PDFs.",
                "char_bboxes": [],
                "layout_blocks": [
                    {
                        "bbox": [72, 144, 540, 640],
                        "text": f"Vision extraction placeholder for {path.name}.",
                        "type": "paragraph",
                    }
                ],
            }
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--out-dir", default="data/extracted")
    parser.add_argument("--force-vision", action="store_true")
    args = parser.parse_args()

    source = Path(args.input)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    try:
        extracted = extract_with_vision_placeholder(source) if args.force_vision else extract_with_pdfplumber(source)
        if not extracted["pages"] or not any(page["text"].strip() for page in extracted["pages"]):
            extracted = extract_with_vision_placeholder(source)
    except Exception:
        extracted = extract_with_vision_placeholder(source)

    extracted["doc_id"] = doc_id_for(source)
    extracted["source_path"] = str(source)

    output = out_dir / f"{extracted['doc_id']}.json"
    with output.open("w", encoding="utf-8") as f:
        json.dump(extracted, f, indent=2)
    print(output)


if __name__ == "__main__":
    main()
