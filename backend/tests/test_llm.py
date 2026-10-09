from types import SimpleNamespace

import httpx
import pytest

from app import llm
from app.config import Settings


class FakeResponse:
    def __init__(self, payload, status_code=200):
        self.payload = payload
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            request = httpx.Request("POST", "http://ollama-test/api/chat")
            response = httpx.Response(self.status_code, request=request)
            raise httpx.HTTPStatusError("Ollama request failed", request=request, response=response)

    def json(self):
        return self.payload


def test_ollama_chat_uses_configured_url_and_model(monkeypatch):
    calls = []
    monkeypatch.setattr(
        llm,
        "get_settings",
        lambda: Settings(
            ai_provider="ollama",
            ollama_base_url="http://ollama-test:11434/",
            ollama_chat_model="chat-test:latest",
        ),
    )

    def fake_post(url, json, timeout):
        calls.append((url, json))
        return FakeResponse({"message": {"content": "Use HTTPS."}})

    monkeypatch.setattr(llm.httpx, "post", fake_post)

    answer = llm.generate_answer("What should redirect URLs use?")

    assert answer == "Use HTTPS."
    assert calls == [
        (
            "http://ollama-test:11434/api/chat",
            {
                "model": "chat-test:latest",
                "messages": [
                    {"role": "user", "content": "What should redirect URLs use?"}
                ],
                "stream": False,
            },
        )
    ]


def test_openai_chat_uses_existing_model_and_api_key(monkeypatch):
    calls = []
    fake_client = SimpleNamespace(
        chat=SimpleNamespace(
            completions=SimpleNamespace(
                create=lambda **kwargs: (
                    calls.append(kwargs)
                    or SimpleNamespace(
                        choices=[SimpleNamespace(message=SimpleNamespace(content="OpenAI answer."))]
                    )
                )
            )
        )
    )
    client_keys = []
    monkeypatch.setattr(
        llm,
        "get_settings",
        lambda: Settings(
            ai_provider="openai",
            openai_api_key="test-openai-key",
            openai_model="gpt-test",
        ),
    )
    monkeypatch.setattr(
        llm,
        "_create_openai_client",
        lambda api_key: client_keys.append(api_key) or fake_client,
    )

    answer = llm.generate_answer("Question")

    assert answer == "OpenAI answer."
    assert client_keys == ["test-openai-key"]
    assert calls == [
        {"model": "gpt-test", "messages": [{"role": "user", "content": "Question"}]}
    ]


def test_openai_chat_requires_api_key(monkeypatch):
    monkeypatch.setattr(llm, "get_settings", lambda: Settings(ai_provider="openai"))

    with pytest.raises(ValueError, match="OPENAI_API_KEY is required"):
        llm.generate_answer("Question")


def test_ollama_chat_failure_has_actionable_error(monkeypatch):
    monkeypatch.setattr(
        llm,
        "get_settings",
        lambda: Settings(ai_provider="ollama", ollama_chat_model="missing-model"),
    )
    monkeypatch.setattr(
        llm.httpx,
        "post",
        lambda *args, **kwargs: FakeResponse({}, status_code=503),
    )

    with pytest.raises(RuntimeError, match="Verify Ollama is running"):
        llm.generate_answer("Question")


def test_ollama_empty_chat_response_is_rejected(monkeypatch):
    monkeypatch.setattr(
        llm,
        "get_settings",
        lambda: Settings(ai_provider="ollama"),
    )
    monkeypatch.setattr(
        llm.httpx,
        "post",
        lambda *args, **kwargs: FakeResponse({"message": {"content": "  "}}),
    )

    with pytest.raises(RuntimeError, match="no chat content"):
        llm.generate_answer("Question")
