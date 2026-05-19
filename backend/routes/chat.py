from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from db import get_db
from models import Conversation, Message
from services.ai_service import chat_completion
from services.persona_service import get_persona
from services.memory_service import build_context, extract_and_save_memory
from services.persona_service import list_personas

router = APIRouter(prefix="/api/chat", tags=["chat"])


class ChatRequest(BaseModel):
    conversation_id: int | None = None
    persona_id: int
    message: str


class ChatResponse(BaseModel):
    conversation_id: int
    reply: str


@router.get("/personas")
async def get_personas(db: AsyncSession = Depends(get_db)):
    personas = await list_personas(db)
    return [{"id": p.id, "name": p.name, "description": p.description} for p in personas]


@router.post("", response_model=ChatResponse)
async def chat(req: ChatRequest, db: AsyncSession = Depends(get_db)):
    persona = await get_persona(db, req.persona_id)
    if persona is None:
        raise HTTPException(status_code=404, detail="Persona not found")

    if req.conversation_id is None:
        conv = Conversation(persona_id=req.persona_id, title=req.message[:30])
        db.add(conv)
        await db.commit()
        await db.refresh(conv)
        req.conversation_id = conv.id

    user_msg = Message(conversation_id=req.conversation_id, role="user", content=req.message)
    db.add(user_msg)
    await db.commit()

    context = await build_context(db, req.conversation_id)
    reply = await chat_completion(context, persona.system_prompt)

    ai_msg = Message(conversation_id=req.conversation_id, role="assistant", content=reply)
    db.add(ai_msg)
    await db.commit()

    await extract_and_save_memory(db, req.conversation_id, req.message, reply)

    return ChatResponse(conversation_id=req.conversation_id, reply=reply)


@router.get("/conversations")
async def list_conversations(persona_id: int, db: AsyncSession = Depends(get_db)):
    from sqlalchemy import select
    result = await db.execute(
        select(Conversation)
        .where(Conversation.persona_id == persona_id)
        .order_by(Conversation.created_at.desc())
    )
    convs = result.scalars().all()
    return [
        {"id": c.id, "title": c.title, "created_at": c.created_at.isoformat()}
        for c in convs
    ]


@router.get("/messages/{conversation_id}")
async def get_messages(conversation_id: int, db: AsyncSession = Depends(get_db)):
    from sqlalchemy import select
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
    )
    msgs = result.scalars().all()
    return [
        {"role": m.role, "content": m.content, "created_at": m.created_at.isoformat()}
        for m in msgs
    ]
