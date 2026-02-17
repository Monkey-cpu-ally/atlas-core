from datetime import datetime
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from atlas_core_new.utils.rate_limiter import rate_limit_ai
from atlas_core_new.db import SessionLocal, Conversation, ChatMessage
from atlas_core_new.routes._shared import openai_client, PERSONA_PROMPTS

router = APIRouter(tags=["conversations"])


class ConversationCreate(BaseModel):
    persona: str
    title: str | None = None


class MessageCreate(BaseModel):
    content: str
    conversation_id: int | None = None


@router.get("/conversations")
def list_conversations(user_id: str = "default_user", persona: str | None = None, limit: int = 20):
    db = SessionLocal()
    if db is None:
        return {"conversations": [], "error": "Service temporarily unavailable. Please try again."}
    try:
        query = db.query(Conversation).filter(Conversation.user_id == user_id)
        if persona:
            query = query.filter(Conversation.persona == persona.lower())
        convos = query.order_by(Conversation.updated_at.desc()).limit(limit).all()
        return {
            "conversations": [
                {
                    "id": c.id,
                    "persona": c.persona,
                    "title": c.title or f"Chat with {c.persona.title()}",
                    "summary": c.summary,
                    "message_count": c.message_count,
                    "is_active": c.is_active,
                    "created_at": c.created_at.isoformat(),
                    "updated_at": c.updated_at.isoformat()
                }
                for c in convos
            ]
        }
    finally:
        db.close()


@router.post("/conversations")
def create_conversation(req: ConversationCreate, user_id: str = "default_user"):
    db = SessionLocal()
    if db is None:
        return {"error": "Service temporarily unavailable. Please try again."}
    try:
        convo = Conversation(
            user_id=user_id,
            persona=req.persona.lower(),
            title=req.title
        )
        db.add(convo)
        db.commit()
        db.refresh(convo)
        return {
            "id": convo.id,
            "persona": convo.persona,
            "title": convo.title,
            "created_at": convo.created_at.isoformat()
        }
    finally:
        db.close()


@router.get("/conversations/{conversation_id}")
def get_conversation(conversation_id: int, include_messages: bool = True):
    db = SessionLocal()
    if db is None:
        return {"error": "Service temporarily unavailable. Please try again."}
    try:
        convo = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if not convo:
            return {"error": "Conversation not found"}

        result = {
            "id": convo.id,
            "persona": convo.persona,
            "title": convo.title or f"Chat with {convo.persona.title()}",
            "summary": convo.summary,
            "message_count": convo.message_count,
            "is_active": convo.is_active,
            "created_at": convo.created_at.isoformat(),
            "updated_at": convo.updated_at.isoformat()
        }

        if include_messages:
            messages = db.query(ChatMessage).filter(
                ChatMessage.conversation_id == conversation_id
            ).order_by(ChatMessage.created_at.asc()).all()
            result["messages"] = [
                {
                    "id": m.id,
                    "role": m.role,
                    "persona": m.persona,
                    "content": m.content,
                    "created_at": m.created_at.isoformat()
                }
                for m in messages
            ]

        return result
    finally:
        db.close()


@router.delete("/conversations/{conversation_id}")
def delete_conversation(conversation_id: int):
    db = SessionLocal()
    if db is None:
        return {"error": "Service temporarily unavailable. Please try again."}
    try:
        convo = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if not convo:
            return {"error": "Conversation not found"}
        db.delete(convo)
        db.commit()
        return {"deleted": True, "id": conversation_id}
    finally:
        db.close()


@router.get("/conversations/{conversation_id}/messages")
def get_messages(conversation_id: int, limit: int = 50, offset: int = 0):
    db = SessionLocal()
    if db is None:
        return {"error": "Service temporarily unavailable. Please try again."}
    try:
        messages = db.query(ChatMessage).filter(
            ChatMessage.conversation_id == conversation_id
        ).order_by(ChatMessage.created_at.asc()).offset(offset).limit(limit).all()

        return {
            "conversation_id": conversation_id,
            "messages": [
                {
                    "id": m.id,
                    "role": m.role,
                    "persona": m.persona,
                    "content": m.content,
                    "created_at": m.created_at.isoformat()
                }
                for m in messages
            ],
            "count": len(messages)
        }
    finally:
        db.close()


@router.post("/conversations/{conversation_id}/messages", dependencies=[Depends(rate_limit_ai)])
def add_message(conversation_id: int, req: MessageCreate):
    db = SessionLocal()
    if db is None:
        return {"error": "Service temporarily unavailable. Please try again."}
    try:
        convo = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if not convo:
            return {"error": "Conversation not found"}

        user_msg = ChatMessage(
            conversation_id=conversation_id,
            role="user",
            content=req.content
        )
        db.add(user_msg)

        history = db.query(ChatMessage).filter(
            ChatMessage.conversation_id == conversation_id
        ).order_by(ChatMessage.created_at.desc()).limit(10).all()
        history.reverse()

        messages_for_ai = [
            {"role": "system", "content": PERSONA_PROMPTS.get(convo.persona, PERSONA_PROMPTS["ajani"])}
        ]
        for msg in history:
            messages_for_ai.append({"role": msg.role, "content": msg.content})
        messages_for_ai.append({"role": "user", "content": req.content})

        ai_response = ""
        if openai_client:
            try:
                response = openai_client.chat.completions.create(
                    model="gpt-5",
                    messages=messages_for_ai,
                    max_completion_tokens=2048
                )
                ai_response = response.choices[0].message.content or ""
            except Exception as e:
                ai_response = "I encountered a temporary error. Please try again."
        else:
            ai_response = "I'm currently offline. Please check AI integration setup."

        assistant_msg = ChatMessage(
            conversation_id=conversation_id,
            role="assistant",
            persona=convo.persona,
            content=ai_response
        )
        db.add(assistant_msg)

        convo.message_count = (convo.message_count or 0) + 2
        convo.updated_at = datetime.utcnow()

        if convo.message_count == 2 and not convo.title:
            convo.title = req.content[:50] + ("..." if len(req.content) > 50 else "")

        db.commit()

        return {
            "conversation_id": conversation_id,
            "user_message": {
                "id": user_msg.id,
                "content": req.content
            },
            "assistant_message": {
                "id": assistant_msg.id,
                "persona": convo.persona,
                "content": ai_response
            }
        }
    finally:
        db.close()


@router.get("/conversations/{conversation_id}/context")
def get_conversation_context(conversation_id: int, max_messages: int = 5):
    db = SessionLocal()
    if db is None:
        return {"error": "Service temporarily unavailable. Please try again."}
    try:
        messages = db.query(ChatMessage).filter(
            ChatMessage.conversation_id == conversation_id
        ).order_by(ChatMessage.created_at.desc()).limit(max_messages).all()
        messages.reverse()

        return {
            "context": [
                {"role": m.role, "content": m.content[:500]}
                for m in messages
            ]
        }
    finally:
        db.close()
