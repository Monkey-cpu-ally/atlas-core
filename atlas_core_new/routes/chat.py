import json
from typing import Optional, List
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from atlas_core_new.utils.rate_limiter import rate_limit_ai
from atlas_core_new.db import SessionLocal, Conversation, ChatMessage
from atlas_core_new.curriculum import get_lesson
from atlas_core_new.routes._shared import (
    openai_client, PERSONA_PROMPTS, BASE_RULES, SHORT_PROMPT_MODES,
    detect_lesson_voice_command, detect_project_context,
    get_project_context_for_persona, user_lesson_progress,
)
from atlas_core_new.core.agent.trinity_counsel import trinity_counsel

router = APIRouter(tags=["chat"])


def generate_conversation_summary(messages_for_summary: List[dict], persona: str) -> Optional[str]:
    """Generate a summary of recent conversation messages using OpenAI."""
    if not openai_client:
        return None
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": f"Summarize this conversation between {persona.title()} and a user in 3-5 sentences. Focus on: key topics discussed, decisions made, projects mentioned, and the user's goals. Be concise."},
                {"role": "user", "content": "\n".join([f"{m['role']}: {m['content'][:200]}" for m in messages_for_summary[-30:]])}
            ],
            max_completion_tokens=256
        )
        return response.choices[0].message.content
    except Exception:
        return None


def get_conversation_summary(db, conversation: Conversation, persona: str) -> Optional[str]:
    """Get or generate a conversation summary."""
    if conversation.summary:
        return conversation.summary
    
    if conversation.message_count > 20:
        messages = db.query(ChatMessage).filter(
            ChatMessage.conversation_id == conversation.id
        ).order_by(ChatMessage.created_at.asc()).all()
        
        messages_dicts = [{"role": msg.role, "content": msg.content} for msg in messages]
        summary = generate_conversation_summary(messages_dicts, persona)
        
        if summary:
            conversation.summary = summary
            db.commit()
        
        return summary
    
    return None


class ChatRequest(BaseModel):
    persona: str = "ajani"
    message: str
    mode: Optional[str] = None
    conversation_id: Optional[int] = None


class CounselRequest(BaseModel):
    topic: str


class TrinityRequest(BaseModel):
    question: str
    context: str | None = None


COUNSEL_PROMPT = BASE_RULES + """
You are facilitating a TRINITY COUNSEL between Ajani, Minerva, and Hermes.

The user has brought a topic for all three to discuss together:
- AJANI: tactical clarity, strategy, direct action
- MINERVA: cultural wisdom, emotional depth, narrative insight  
- HERMES: pattern recognition, systems thinking, witty observations

Format as a natural conversation with each persona labeled. They build on each other, agree, and respectfully challenge. Three distinct voices in real discussion."""


@router.post("/chat", dependencies=[Depends(rate_limit_ai)])
def chat(req: ChatRequest):
    persona = req.persona.lower()
    if persona not in PERSONA_PROMPTS:
        return {"error": f"Unknown persona: {persona}", "available": list(PERSONA_PROMPTS.keys())}

    if not openai_client:
        return {"error": "AI services are currently offline. Please try again later.", "persona": persona, "response": "AI services are currently offline. Please try again later."}

    if req.mode and req.mode in SHORT_PROMPT_MODES:
        try:
            short_message = SHORT_PROMPT_MODES[req.mode](req.message)
            response = openai_client.chat.completions.create(
                model="gpt-5",
                messages=[
                    {"role": "system", "content": f"You are {persona.title()}. Be concise."},
                    {"role": "user", "content": short_message}
                ],
                max_completion_tokens=256
            )
            return {"persona": persona, "response": response.choices[0].message.content}
        except Exception:
            return {"error": "An error occurred processing your request", "persona": persona, "response": "Sorry, I encountered a temporary error. Please try again."}

    voice_cmd = detect_lesson_voice_command(req.message)
    extra_context = ""

    if voice_cmd and voice_cmd["type"] == "resume_lesson":
        progress = user_lesson_progress.get("default")
        if progress and progress["persona"] == persona:
            lesson = get_lesson(progress["persona"], progress["field"], progress["lesson_id"])
            if lesson:
                extra_context = f"\n\nUSER IS RESUMING LESSON: {lesson['title']} ({lesson['level']} level, {progress['field']}). Topic: {lesson['summary']}. Continue teaching this topic naturally."
        elif progress:
            extra_context = f"\n\nUser wants to resume lessons but their active lesson is with {progress['persona'].title()}, not you. Acknowledge this and suggest they switch or start a new topic with you."
        else:
            extra_context = "\n\nUser wants to resume lessons but has no active lesson. Ask what they'd like to learn and offer to start a lesson in one of your fields."

    project_match = detect_project_context(req.message)
    if project_match:
        extra_context += get_project_context_for_persona(project_match["project"], persona)

    conversation_messages = [{"role": "system", "content": PERSONA_PROMPTS[persona] + extra_context}]

    if SessionLocal and req.conversation_id:
        try:
            db = SessionLocal()
            try:
                active_conv = db.query(Conversation).filter(
                    Conversation.id == req.conversation_id
                ).first()
                
                if active_conv:
                    summary = get_conversation_summary(db, active_conv, persona)
                    if summary:
                        conversation_messages.insert(1, {"role": "system", "content": f"Previous conversation summary: {summary}"})
                
                history = db.query(ChatMessage).filter(
                    ChatMessage.conversation_id == req.conversation_id
                ).order_by(ChatMessage.created_at.desc()).limit(20).all()
                for msg in reversed(history):
                    conversation_messages.append({"role": msg.role, "content": msg.content})
            finally:
                db.close()
        except Exception as e:
            print(f"Error loading conversation history: {e}")

    conversation_messages.append({"role": "user", "content": req.message})

    try:
        response = openai_client.chat.completions.create(
            model="gpt-5",
            messages=conversation_messages,
            max_completion_tokens=2048
        )
        choice = response.choices[0]
        content = choice.message.content
        finish_reason = choice.finish_reason

        if hasattr(choice.message, 'refusal') and choice.message.refusal:
            content = f"I cannot respond to that request. {choice.message.refusal}"

        if not content or (isinstance(content, str) and content.strip() == ""):
            if finish_reason == "length":
                content = "My response was too long. Let me try again more concisely - what specifically would you like to know?"
            elif finish_reason == "content_filter":
                content = "I had to filter my response. Could you rephrase your question?"
            else:
                content = "Let me think about that. What specific aspect would you like to explore?"

        conversation_id = req.conversation_id
        try:
            if SessionLocal:
                db = SessionLocal()
                try:
                    from datetime import datetime

                    if conversation_id:
                        active_conv = db.query(Conversation).filter(
                            Conversation.id == conversation_id
                        ).first()
                    else:
                        active_conv = db.query(Conversation).filter(
                            Conversation.user_id == "default_user",
                            Conversation.persona == persona,
                            Conversation.is_active == True
                        ).order_by(Conversation.updated_at.desc()).first()

                    if not active_conv:
                        active_conv = Conversation(
                            user_id="default_user",
                            persona=persona,
                            title=req.message[:50] + "..." if len(req.message) > 50 else req.message,
                            is_active=True
                        )
                        db.add(active_conv)
                        db.commit()
                        db.refresh(active_conv)

                    conversation_id = active_conv.id

                    user_msg = ChatMessage(
                        conversation_id=active_conv.id,
                        role="user",
                        persona=None,
                        content=req.message
                    )
                    assistant_msg = ChatMessage(
                        conversation_id=active_conv.id,
                        role="assistant",
                        persona=persona,
                        content=content
                    )
                    db.add(user_msg)
                    db.add(assistant_msg)
                    active_conv.message_count += 2
                    active_conv.updated_at = datetime.utcnow()
                    db.commit()
                    
                    if active_conv.message_count > 20 and active_conv.message_count % 10 == 0:
                        messages = db.query(ChatMessage).filter(
                            ChatMessage.conversation_id == active_conv.id
                        ).order_by(ChatMessage.created_at.asc()).all()
                        messages_dicts = [{"role": msg.role, "content": msg.content} for msg in messages]
                        summary = generate_conversation_summary(messages_dicts, persona)
                        if summary:
                            active_conv.summary = summary
                            db.commit()
                finally:
                    db.close()
        except Exception as db_err:
            print(f"Error persisting conversation: {db_err}")

        return {
            "persona": persona,
            "response": content,
            "conversation_id": conversation_id
        }
    except Exception:
        import traceback
        traceback.print_exc()
        return {"error": "An error occurred processing your request", "persona": persona, "response": "Sorry, I encountered a temporary error. Please try again."}


@router.post("/chat/stream", dependencies=[Depends(rate_limit_ai)])
async def chat_stream(req: ChatRequest):
    persona = req.persona.lower()
    if persona not in PERSONA_PROMPTS:
        return {"error": f"Unknown persona: {persona}"}

    if not openai_client:
        return {"error": "AI services are currently offline. Please try again later."}

    conversation_messages = [{"role": "system", "content": PERSONA_PROMPTS[persona]}]
    
    if SessionLocal and req.conversation_id:
        try:
            db = SessionLocal()
            try:
                active_conv = db.query(Conversation).filter(
                    Conversation.id == req.conversation_id
                ).first()
                
                if active_conv:
                    summary = get_conversation_summary(db, active_conv, persona)
                    if summary:
                        conversation_messages.insert(1, {"role": "system", "content": f"Previous conversation summary: {summary}"})
                
                history = db.query(ChatMessage).filter(
                    ChatMessage.conversation_id == req.conversation_id
                ).order_by(ChatMessage.created_at.desc()).limit(20).all()
                for msg in reversed(history):
                    conversation_messages.append({"role": msg.role, "content": msg.content})
            finally:
                db.close()
        except Exception as e:
            print(f"Error loading conversation history: {e}")
    
    conversation_messages.append({"role": "user", "content": req.message})

    async def generate():
        try:
            stream = openai_client.chat.completions.create(
                model="gpt-5",
                messages=conversation_messages,
                max_completion_tokens=2048,
                stream=True
            )

            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    yield f"data: {json.dumps({'content': content})}\n\n"

            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


@router.post("/counsel", dependencies=[Depends(rate_limit_ai)])
def counsel(req: CounselRequest):
    if not openai_client:
        return {"error": "AI services are currently offline. Please try again later.", "response": "AI services are currently offline. Please try again later."}

    try:
        from atlas_core_new.utils.error_handling import sanitize_error
        response = openai_client.chat.completions.create(
            model="gpt-5",
            messages=[
                {"role": "system", "content": COUNSEL_PROMPT},
                {"role": "user", "content": f"TOPIC FOR COUNSEL: {req.topic}"}
            ],
            max_completion_tokens=2048
        )
        return {
            "mode": "counsel",
            "topic": req.topic,
            "discussion": response.choices[0].message.content or ""
        }
    except Exception as e:
        from atlas_core_new.utils.error_handling import sanitize_error
        return {"error": sanitize_error(e), "discussion": "The counsel encountered an error."}


@router.post("/trinity", dependencies=[Depends(rate_limit_ai)])
def trinity_counsel_endpoint(req: TrinityRequest):
    result = trinity_counsel.consult(req.question, req.context)
    if not result:
        return {"error": "Trinity Counsel not available", "responses": []}

    return {
        "question": result.question,
        "responses": [
            {
                "persona": r.persona,
                "perspective": r.perspective,
                "recommendation": r.recommendation
            }
            for r in result.responses
        ],
        "synthesis": result.synthesis,
        "consensus_reached": result.consensus_reached
    }
