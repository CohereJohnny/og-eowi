from app.north_client import _sdk_base_url


def test_sdk_base_url_preserves_api_suffix() -> None:
    assert _sdk_base_url("https://demo.north.cohere.com/api/") == "https://demo.north.cohere.com/api"


def test_sdk_base_url_preserves_host_without_api_suffix() -> None:
    assert _sdk_base_url("https://demo.north.cohere.com") == "https://demo.north.cohere.com"
