import re
from dataclasses import dataclass
from .db import get_chunk


@dataclass
class VerificationResult:
    ok: bool
    failures: list[dict]
    text: str


def verify_citations(answer_text: str, available_chunk_ids: set[str]) -> VerificationResult:
    cited_ids = re.findall(r"\[([^\]]+)\]", answer_text)
    failures: list[dict] = []

    for chunk_id in cited_ids:
        if chunk_id not in available_chunk_ids:
            failures.append({"chunk_id": chunk_id, "reason": "chunk_id not in retrieved set"})
            continue
        if get_chunk(chunk_id) is None:
            failures.append({"chunk_id": chunk_id, "reason": "chunk_id does not exist"})

    return VerificationResult(ok=len(failures) == 0, failures=failures, text=answer_text)
