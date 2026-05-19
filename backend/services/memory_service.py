import datetime
from db import _memories, _messages, _next, Memory


async def save_memory(conversation_id: int, key: str, value: str, importance: float = 0.5):
    _memories.append(Memory(
        id=_next(),
        conversation_id=conversation_id,
        key=key,
        value=value,
        importance=importance,
        created_at=datetime.datetime.utcnow().isoformat(),
    ))


async def get_memories(conversation_id: int) -> list[Memory]:
    return sorted(
        [m for m in _memories if m.conversation_id == conversation_id],
        key=lambda x: x.importance,
        reverse=True,
    )[:20]


async def build_context(conversation_id: int, max_messages: int = 30) -> list[dict]:
    conv_msgs = [m for m in _messages if m.conversation_id == conversation_id]
    conv_msgs.sort(key=lambda x: x.created_at)
    recent = conv_msgs[-max_messages:]

    memories = await get_memories(conversation_id)
    memory_text = "\n".join(f"[记忆：{m.key} -> {m.value}]" for m in memories)

    context = []
    if memory_text:
        context.append({"role": "system", "content": f"关于用户的重要记忆：\n{memory_text}"})
    context.extend([{"role": m.role, "content": m.content} for m in recent])
    return context


async def extract_and_save_memory(conversation_id: int, user_message: str, ai_response: str):
    triggers = {
        "我叫": "用户的名字",
        "我是": "用户的身份",
        "我喜欢": "用户喜欢的事物",
        "我住在": "用户的住址",
    }
    for keyword, label in triggers.items():
        if keyword in user_message:
            value = user_message.split(keyword, 1)[1].strip()[:50]
            await save_memory(conversation_id, label, value, importance=0.7)
