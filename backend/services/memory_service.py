from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models import Memory, Message


async def save_memory(db: AsyncSession, conversation_id: int, key: str, value: str, importance: float = 0.5) -> Memory:
    memory = Memory(conversation_id=conversation_id, key=key, value=value, importance=importance)
    db.add(memory)
    await db.commit()
    await db.refresh(memory)
    return memory


async def get_memories(db: AsyncSession, conversation_id: int) -> list[Memory]:
    result = await db.execute(
        select(Memory)
        .where(Memory.conversation_id == conversation_id)
        .order_by(Memory.importance.desc())
        .limit(20)
    )
    return list(result.scalars().all())


async def build_context(db: AsyncSession, conversation_id: int, max_messages: int = 30) -> list[dict]:
    """Build context from recent messages and important memories."""
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(max_messages)
    )
    messages = list(reversed(result.scalars().all()))

    memories = await get_memories(db, conversation_id)
    memory_text = "\n".join(f"[记忆：{m.key} -> {m.value}]" for m in memories)

    context = []
    if memory_text:
        context.append({"role": "system", "content": f"关于用户的重要记忆：\n{memory_text}"})

    context.extend([{"role": m.role, "content": m.content} for m in messages])
    return context


async def extract_and_save_memory(db: AsyncSession, conversation_id: int, user_message: str, ai_response: str):
    """Simple keyword-based memory extraction as fallback."""
    triggers = {
        "我叫": "用户的名字",
        "我是": "用户的身份",
        "我喜欢": "用户喜欢的事物",
        "我住在": "用户的住址",
    }
    for keyword, label in triggers.items():
        if keyword in user_message:
            value = user_message.split(keyword, 1)[1].strip()[:50]
            await save_memory(db, conversation_id, label, value, importance=0.7)
