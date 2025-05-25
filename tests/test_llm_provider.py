from backend.llm_provider import LocalProvider


def test_local_provider_returns_str():
    provider = LocalProvider()
    response = provider.generate("ping")
    assert isinstance(response, str)
    assert response.startswith("pong")
