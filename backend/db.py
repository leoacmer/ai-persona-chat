import datetime
from dataclasses import dataclass, field

# In-memory stores — survives until restart
_personas: list["Persona"] = []
_conversations: list["Conversation"] = []
_messages: list["Message"] = []
_memories: list["Memory"] = []
_next_id = 1


def _next() -> int:
    global _next_id
    n = _next_id
    _next_id += 1
    return n


@dataclass
class Persona:
    id: int
    name: str
    description: str
    system_prompt: str
    created_at: str = ""


@dataclass
class Conversation:
    id: int
    persona_id: int
    title: str = "新对话"
    created_at: str = ""


@dataclass
class Message:
    id: int
    conversation_id: int
    role: str
    content: str
    embedding: str | None = None
    created_at: str = ""


@dataclass
class Memory:
    id: int
    conversation_id: int
    key: str
    value: str
    importance: float = 0.5
    created_at: str = ""


async def init_db():
    pass
