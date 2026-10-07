"""OpenAI chat-completion abstraction."""

from app.config import get_settings


def generate_answer(prompt: str) -> str:
	"""Send a prompt to the configured chat model and return its answer."""
	from openai import OpenAI

	settings = get_settings()
	client = OpenAI(api_key=settings.openai_api_key)
	response = client.chat.completions.create(
		model=settings.openai_model,
		messages=[{"role": "user", "content": prompt}],
	)
	return response.choices[0].message.content or ""
