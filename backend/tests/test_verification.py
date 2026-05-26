from app.verification import verify_citations


def test_verify_citations_rejects_unretrieved_chunk() -> None:
    result = verify_citations("Claim [MISSING_CHUNK]", {"KNOWN_CHUNK"})

    assert not result.ok
    assert result.failures[0]["chunk_id"] == "MISSING_CHUNK"
