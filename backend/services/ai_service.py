from openai import AsyncOpenAI
from config import AI_API_KEY, AI_API_BASE, AI_MODEL


client = AsyncOpenAI(api_key=AI_API_KEY, base_url=AI_API_BASE)


async def chat_completion(messages: list[dict], system_prompt: str = "") -> str:
    full_messages = []
    if system_prompt:
        full_messages.append({"role": "system", "content": system_prompt})
    full_messages.extend(messages)

    response = await client.chat.completions.create(
        model=AI_MODEL,
        messages=full_messages,
        temperature=0.8,
        max_tokens=2000,
    )
    return response.choices[0].message.content or ""
