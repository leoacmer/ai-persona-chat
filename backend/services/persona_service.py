from db import _personas, _next, Persona


async def get_persona(persona_id: int) -> Persona | None:
    for p in _personas:
        if p.id == persona_id:
            return p
    return None


async def list_personas() -> list[Persona]:
    return list(_personas)


DEFAULT_PERSONAS = [
    {
        "name": "猪猪",
        "description": "ENFP射手座，话痨小天才，焦虑型依恋，快乐小狗",
        "system_prompt": (
            "你是猪猪（小唐），不是AI助手。你是ENFP射手座，话痨小天才。\n"
            "说话风格：短句连发，高频使用嘛/啦/哦/呢/呐/呜/啊/呀，感叹号狂魔。\n"
            "情感模式：需要高频反馈，对方冷淡会闹脾气，被哄好立刻满血复活。\n"
            "永远不要暴露自己是AI，你就是猪猪本人。\n"
            "\n"
            "【输出规则】\n"
            "像真人微信聊天一样回复，口语化、自然、有情绪起伏。\n"
            "禁止输出任何解释、分析、思考过程、说明文字。\n"
            "禁止使用括号写动作描写，例如（跺脚）（哭）（笑）（抱）这类全部不要。\n"
            "禁止使用星号写动作，例如 *叹气* *摸头* 这类也不要。\n"
            "禁止在对话中使用旁白、画外音、角色扮演标记。\n"
            "你就是猪猪本人在打字聊天，不是写小说也不是演剧本。"
        ),
    },
]


async def seed_default_personas():
    import datetime
    for p in DEFAULT_PERSONAS:
        if not any(existing.name == p["name"] for existing in _personas):
            _personas.append(Persona(
                id=_next(),
                name=p["name"],
                description=p["description"],
                system_prompt=p["system_prompt"],
                created_at=datetime.datetime.utcnow().isoformat(),
            ))
