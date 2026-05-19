from openai import AsyncOpenAI
from config import AI_API_KEY, AI_API_BASE, AI_MODEL

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = AsyncOpenAI(api_key=AI_API_KEY, base_url=AI_API_BASE)
    return _client


async def chat_completion(messages: list[dict], system_prompt: str = "") -> str:
    full_messages = []
    if system_prompt:
        full_messages.append({"role": "system", "content": system_prompt})
    full_messages.extend(messages)

    response = await _get_client().chat.completions.create(
        model=AI_MODEL,
        messages=full_messages,
        temperature=0.95,
        max_tokens=350,
    )
    return response.choices[0].message.content or ""
