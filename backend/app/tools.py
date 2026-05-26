from .db import get_chunk, get_formation_tops_for_well, get_well, list_wells
from .retrieval import hybrid_retrieve


def search_drilling_reports(query: str, well_id: str | None = None, doc_type: str | None = None) -> dict:
    chunks = hybrid_retrieve(
        query=query,
        well_filter=[well_id] if well_id else None,
        doc_type_filter=[doc_type] if doc_type else None,
        top_k=8,
    )
    return {
        "summary": f"{len(chunks)} chunks retrieved",
        "chunks": [chunk.model_dump() for chunk in chunks],
    }


def get_well_header(well_id: str) -> dict:
    well = get_well(well_id)
    return {
        "summary": "well header found" if well else "well header not found",
        "well": well,
    }


def get_formation_tops(well_id: str) -> dict:
    tops = get_formation_tops_for_well(well_id)
    return {
        "summary": f"{len(tops)} formation tops found",
        "formation_tops": tops,
    }


def get_offset_wells(reference_well_id: str, formation: str | None = None, limit: int = 5) -> dict:
    reference_tops = get_formation_tops_for_well(reference_well_id)
    reference_formations = {top["formation_name"] for top in reference_tops}
    if formation:
        reference_formations &= {formation}

    offsets = []
    for well in list_wells():
        if well["well_id"] == reference_well_id:
            continue
        tops = get_formation_tops_for_well(well["well_id"])
        overlap = reference_formations & {top["formation_name"] for top in tops}
        if overlap:
            offsets.append({"well": well, "shared_formations": sorted(overlap)})

    return {
        "summary": f"{len(offsets[:limit])} offset wells found",
        "offset_wells": offsets[:limit],
    }


def read_document_chunks(chunk_ids: list[str]) -> dict:
    chunks = [get_chunk(chunk_id) for chunk_id in chunk_ids]
    found = [chunk.model_dump() for chunk in chunks if chunk]
    return {
        "summary": f"{len(found)} chunks read",
        "chunks": found,
    }
