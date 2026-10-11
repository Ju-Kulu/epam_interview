"""Chat completion abstraction for the configured AI provider."""

import httpx

from app.config import Settings, get_settings


def _create_openai_client(api_key: str):
    from openai import OpenAI

    return OpenAI(api_key=api_key)


def _generate_ollama_answer(settings: Settings, prompt: str) -> str:
    endpoint = f"{settings.ollama_base_url.rstrip('/')}/api/chat"
    try:
        response = httpx.post(
            endpoint,
            json={
                "model": settings.ollama_chat_model,
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
            },
            timeout=60.0,
        )
        response.raise_for_status()
        payload = response.json()
    except (httpx.HTTPError, ValueError) as exc:
        raise RuntimeError(
            f"Ollama chat request failed at {endpoint}. Verify Ollama is running, "
            f"the URL is reachable, and model '{settings.ollama_chat_model}' is available."
        ) from exc

    message = payload.get("message") if isinstance(payload, dict) else None
    content = message.get("content") if isinstance(message, dict) else None
    if not isinstance(content, str) or not content.strip():
        raise RuntimeError(
            "Ollama returned no chat content. Verify the configured chat model and response."
        )
    return content


def _generate_openai_answer(settings: Settings, prompt: str) -> str:
    if not settings.openai_api_key or not settings.openai_api_key.strip():
        raise ValueError("OPENAI_API_KEY is required when AI_PROVIDER is 'openai'.")

    try:
        client = _create_openai_client(settings.openai_api_key)
    except Exception as exc:
        raise RuntimeError(
            "Could not initialize the OpenAI client. Verify OPENAI_API_KEY and the OpenAI SDK installation."
        ) from exc

    try:
        response = client.chat.completions.create(
            model=settings.openai_model,
            messages=[{"role": "user", "content": prompt}],
        )
        content = response.choices[0].message.content
    except Exception as exc:
        raise RuntimeError(
            f"OpenAI chat request failed with model '{settings.openai_model}'. "
            "Verify OPENAI_API_KEY, model access, and network connectivity."
        ) from exc

    if not isinstance(content, str) or not content.strip():
        raise RuntimeError("OpenAI returned an empty chat response.")
    return content


def generate_answer(prompt: str) -> str:
    """Generate an answer using the configured provider and chat model."""
    settings = get_settings()
    if settings.ai_provider == "ollama":
        return _generate_ollama_answer(settings, prompt)
    if settings.ai_provider == "openai":
        return _generate_openai_answer(settings, prompt)
    raise ValueError(f"Unsupported AI_PROVIDER '{settings.ai_provider}'.")
