import httpx
from backend.llm_provider import LocalProvider, OpenAIProvider


class DummyResp:
    def __init__(self, data: str = "pong"):
        self._data = data

    def json(self):
        return {"choices": [{"message": {"content": self._data}}]}

    def raise_for_status(self):
        pass


def test_local_provider_returns_str():
    provider = LocalProvider()
    response = provider.generate("ping")
    assert isinstance(response, str)
    assert response.startswith("pong")


def test_openai_provider_called_with_key(monkeypatch):
    calls = {}

    def fake_post(url, *, headers=None, json=None):
        calls["headers"] = headers
        calls["json"] = json
        return DummyResp("bar")

    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setattr(httpx, "post", fake_post, raising=False)
    provider = OpenAIProvider()
    result = provider.generate("hello")
    assert result == "bar"
    assert calls["headers"]["Authorization"] == "Bearer sk-test"
