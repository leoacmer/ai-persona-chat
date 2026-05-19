import datetime
import traceback
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from db import _conversations, _messages, _next, Conversation, Message
from services.ai_service import chat_completion
from services.persona_service import get_persona, list_personas
from services.memory_service import build_context, extract_and_save_memory

router = APIRouter(prefix="/api/chat", tags=["chat"])


class ChatRequest(BaseModel):
    conversation_id: int | None = None
    persona_id: int
    message: str


class ChatResponse(BaseModel):
    conversation_id: int
    reply: str


@router.get("/personas")
async def get_personas():
    personas = await list_personas()
    return [{"id": p.id, "name": p.name, "description": p.description} for p in personas]


@router.post("", response_model=ChatResponse)
async def chat(req: ChatRequest):
    try:
        persona = await get_persona(req.persona_id)
        if persona is None:
            raise HTTPException(status_code=404, detail="Persona not found")

        if req.conversation_id is None:
            conv = Conversation(
                id=_next(),
                persona_id=req.persona_id,
                title=req.message[:30],
                created_at=datetime.datetime.utcnow().isoformat(),
            )
            _conversations.append(conv)
            req.conversation_id = conv.id

        _messages.append(Message(
            id=_next(),
            conversation_id=req.conversation_id,
            role="user",
            content=req.message,
            created_at=datetime.datetime.utcnow().isoformat(),
        ))

        context = await build_context(req.conversation_id)
        reply = await chat_completion(context, persona.system_prompt)

        _messages.append(Message(
            id=_next(),
            conversation_id=req.conversation_id,
            role="assistant",
            content=reply,
            created_at=datetime.datetime.utcnow().isoformat(),
        ))

        await extract_and_save_memory(req.conversation_id, req.message, reply)

        return ChatResponse(conversation_id=req.conversation_id, reply=reply)
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversations")
async def get_conversations(persona_id: int):
    convs = [c for c in _conversations if c.persona_id == persona_id]
    convs.sort(key=lambda x: x.created_at, reverse=True)
    return [{"id": c.id, "title": c.title, "created_at": c.created_at} for c in convs]


@router.get("/messages/{conversation_id}")
async def get_messages(conversation_id: int):
    msgs = [m for m in _messages if m.conversation_id == conversation_id]
    msgs.sort(key=lambda x: x.created_at)
    return [{"role": m.role, "content": m.content, "created_at": m.created_at} for m in msgs]
