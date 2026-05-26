import math
import re
from collections import Counter
from .db import get_chunks
from .models import Chunk


TOKEN_RE = re.compile(r"\d+(?:\.\d+)?|\d+/\d+|\d+-\d+|\"|[A-Za-z]+(?:-[A-Za-z0-9]+)*")


def tokenize(text: str) -> list[str]:
    return [token.lower() for token in TOKEN_RE.findall(text)]


def _score(query_tokens: list[str], chunk: Chunk) -> float:
    text = f"{chunk.section_path} {chunk.chunk_text}"
    tokens = tokenize(text)
    counts = Counter(tokens)
    lexical = sum(counts[token] for token in query_tokens)
    phrase_bonus = 0.0
    lower = text.lower()
    for phrase in ("hugin", "stuck", "differential", "mud", "bha", "execution", "design", "offset", "f-14"):
        if phrase in lower and phrase in " ".join(query_tokens):
            phrase_bonus += 2.0
    length_norm = math.sqrt(max(len(tokens), 1))
    return (lexical + phrase_bonus) / length_norm


def hybrid_retrieve(
    query: str,
    well_filter: list[str] | None = None,
    doc_type_filter: list[str] | None = None,
    top_k: int = 8,
) -> list[Chunk]:
    """Local deterministic retrieval for the demo.

    The production path swaps this scorer for BM25 + Embed v4 + Rerank 3.5.
    The interface and metadata are intentionally the same as the spec.
    """
    query_tokens = tokenize(query)
    chunks = get_chunks()
    if well_filter:
        chunks = [chunk for chunk in chunks if chunk.well_id in well_filter]
    if doc_type_filter:
        chunks = [chunk for chunk in chunks if chunk.doc_type in doc_type_filter]

    scored = []
    for chunk in chunks:
        score = _score(query_tokens, chunk)
        if score > 0:
            chunk.score = score
            scored.append(chunk)

    if not scored:
        scored = chunks

    return sorted(scored, key=lambda chunk: chunk.score, reverse=True)[:top_k]
