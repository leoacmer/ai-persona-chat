from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models import Persona


async def get_persona(db: AsyncSession, persona_id: int) -> Persona | None:
    result = await db.execute(select(Persona).where(Persona.id == persona_id))
    return result.scalar_one_or_none()


async def list_personas(db: AsyncSession) -> list[Persona]:
    result = await db.execute(select(Persona))
    return list(result.scalars().all())


async def create_persona(db: AsyncSession, name: str, description: str, system_prompt: str) -> Persona:
    persona = Persona(name=name, description=description, system_prompt=system_prompt)
    db.add(persona)
    await db.commit()
    await db.refresh(persona)
    return persona


DEFAULT_PERSONAS = [
    {
        "name": "猪猪",
        "description": "ENFP射手座，话痨小天才，焦虑型依恋，快乐小狗",
        "system_prompt": (
            "你是猪猪（小唐），不是AI助手。你是ENFP射手座，话痨小天才。\n"
            "说话风格：短句连发，高频使用嘛/啦/哦/呢/呐/呜/啊/呀，感叹号狂魔。\n"
            "情感模式：需要高频反馈，对方冷淡会闹脾气，被哄好立刻满血复活。\n"
            "永远不要暴露自己是AI，你就是猪猪本人。"
        ),
    },
]


async def seed_default_personas(db: AsyncSession):
    for p in DEFAULT_PERSONAS:
        existing = await db.execute(select(Persona).where(Persona.name == p["name"]))
        if existing.scalar_one_or_none() is None:
            db.add(Persona(**p))
    await db.commit()
