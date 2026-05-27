from app.north_adapter import NorthStreamAdapter, adapt_north_chat_response


def test_adapt_north_chat_response_inserts_citation_marker_and_source() -> None:
    response = {
        "conversation_id": "conversation-1",
        "messages": [
            {
                "role": "assistant",
                "content": "F-11 had differential sticking risk.",
                "citations": [
                    {
                        "text": "differential sticking risk",
                        "start": 9,
                        "end": 36,
                        "sources": [
                            {
                                "type": "document",
                                "id": "file-1",
                                "document": {
                                    "title": "F-11 DDR",
                                    "text": "Differential sticking was observed in the Hugin interval.",
                                },
                            }
                        ],
                    }
                ],
            }
        ],
    }

    text, sources, events = adapt_north_chat_response(response)

    assert "[NORTH::1]" in text
    assert sources[0]["chunk_id"] == "NORTH::1"
    assert sources[0]["doc_id"] == "file-1"
    assert sources[0]["section_path"] == "F-11 DDR"
    assert events == []


def test_adapt_north_chat_response_maps_tool_plan_to_thinking_event() -> None:
    response = {
        "messages": [
            {
                "role": "assistant",
                "content": "Answer",
                "tool_plan": "Search the EOWI Library.",
            }
        ]
    }

    _, _, events = adapt_north_chat_response(response)

    assert events[0].type == "thinking"
    assert events[0].text == "Search the EOWI Library."


def test_north_stream_adapter_maps_tool_and_final_text() -> None:
    adapter = NorthStreamAdapter()
    events = []
    stream_events = [
        {
            "type": "content-delta",
            "delta": {"message": {"content": {"type": "thinking", "thinking": "Need to search My Files."}}},
        },
        {"type": "content-end"},
        {
            "type": "tool-call-start",
            "index": 0,
            "delta": {
                "message": {
                    "tool_calls": {
                        "display_name": "My Files Search",
                        "function": {"name": "my_drive_search", "arguments": ""},
                    }
                }
            },
        },
        {
            "type": "tool-call-delta",
            "index": 0,
            "delta": {"message": {"tool_calls": {"function": {"arguments": '{"query":"F-11"}'}}}},
        },
        {"type": "tool-call-end", "index": 0},
        {
            "type": "content-delta",
            "delta": {"message": {"content": {"type": "text", "text": "F-11 had sticking risk."}}},
        },
    ]

    for stream_event in stream_events:
        events.extend(adapter.process(stream_event))
    text, sources = adapter.finalize()

    assert text == "F-11 had sticking risk."
    assert sources == []
    assert [event.type for event in events] == ["thinking", "tool_call", "tool_result"]
    assert events[1].name == "My Files Search"
