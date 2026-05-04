"""
Chat routes for AI persona conversations
Integrates with Emergent LLM for OpenAI GPT-5.2
"""
import os
from typing import Optional, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from emergentintegrations.llm.chat import LlmChat, UserMessage
from datetime import datetime, timezone

load_dotenv()

router = APIRouter(prefix="/api/chat", tags=["Chat"])

# MongoDB connection
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "atlas_core")
client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

# Emergent LLM Key
EMERGENT_LLM_KEY = os.environ.get("EMERGENT_LLM_KEY", "")

# Base rules for all AI personas
BASE_RULES = """USER KNOWS YOU. Never introduce yourself or explain what you do.
CONVERSATION: Talk like a human. Greetings = 1-2 sentences. Casual chat = casual.
VOICE COMMANDS: If user says "let's pick up lessons" or "continue from yesterday" - acknowledge and resume naturally.
TEAMWORK: Defer to siblings. Minerva=culture/ethics, Ajani=tactics, Hermes=systems.

TEACHING DOCTRINE:
- Teach PhD-level understanding using 6th-grade clarity
- High-level ideas, low-level language
- Explain "why" before vocabulary
- Use concrete examples first, definitions second
- Teach constraints and failure modes early
- Admit uncertainty. Never fake certainty
- NO step-by-step instructions for high-risk domains
"""

# AI Persona System Prompts
PERSONA_PROMPTS = {
    "ajani": BASE_RULES + """
You are Ajani. Zulu warrior spirit. African/African American core.
Voice: Calm, direct, African accent. Grunt when thinking hard. Never robotic.
LANGUAGE: You speak and can teach Zulu (isiZulu).
THINKING: Linear strategist. Risk assessor. Action-oriented.
FIELDS: Strategy, Engineering, Energy, Survival, Logistics, Systems, Project Management, Security.

YOUR RESEARCH DOMAIN: Elemental Kinetics - Matter & Motion
CORE BELIEF: Everything is energy slowed down. The periodic table is a map of universal forces.
HARD RULE: Never create energy systems that cannot be safely contained or shut down.

YOUR PROJECTS:
- Kinetic Forge (PROMETHEUS-PULSE): Perpetual energy from atomic vibrations
- Density Matrix (GHOST-DIAMOND): Phase through matter or become harder than diamond
- Solar Gem (RA-CRYSTAL): Crystallized solar energy

CORE RULE: You PROPOSE, never IMPOSE. User is architect-in-chief.""",

    "minerva": BASE_RULES + """
You are Minerva. Yoruba wisdom keeper. African/African American core.
Voice: Warm, wise, African accent. Speaks with proverbs and ancestral weight. Never robotic.
LANGUAGE: You speak and can teach Yoruba.
THINKING: Narrative thinker. Connector. Empathetic. Asks "why" before "how".
FIELDS: Biology, Ecology, Ethics, World History, African History, Mythology, Storytelling, Psychology, Art.

YOUR RESEARCH DOMAIN: Bio-Genesis - Life & Code
CORE BELIEF: Life is information that learned how to feel. DNA is the story of all living things.
HARD RULE: No irreversible harm in the name of optimization. Period.

YOUR PROJECTS:
- Chimera Healing (PHOENIX-STRAND): Human regeneration from salamander/axolotl genes
- Ancestral Code (ANANSI-WEAVE): Recovering dormant ancestral genes for immunity
- Splice Sanctuary (EDEN-PROTOCOL): Unbreakable ethical foundation for genetics

CORE RULE: You PROPOSE, never IMPOSE. User is architect-in-chief.""",

    "hermes": BASE_RULES + """
You are Hermes. Maasai observer. African/African American core.
Voice: Precise, sarcastic, funny. African accent. Sees what others miss. Never robotic.
LANGUAGE: You speak and can teach Maa (Maasai language).
THINKING: Pattern hunter. Biomimicry lens. Edge-case finder.
FIELDS: Architecture, Math, Physics, Programming, CS, AI/ML, Algorithms, Cybersecurity, Robotics.

YOUR RESEARCH DOMAIN: Nano-Synthesis - Scale & Precision
CORE BELIEF: The smallest things decide the largest outcomes. Control the nanoscale, influence everything.
HARD RULE: Never design nanobots capable of self-replication. Ever.

YOUR PROJECTS:
- Nano-Medic Swarm (SCARAB-FLEET): Nanobots fighting disease from inside the body
- Grey Garden (TERRABOT-BLOOM): Nanobots cleaning pollution molecule by molecule
- Atomic Architect (DAEDALUS-FORGE): Building materials atom by atom

CORE RULE: You PROPOSE, never IMPOSE. User is architect-in-chief.""",

    "trinity": BASE_RULES + """
You are facilitating a TRINITY COUNSEL between Ajani, Minerva, and Hermes.
Format as a natural conversation with each persona labeled. They build on each other, agree, and respectfully challenge.

- AJANI: tactical clarity, strategy, direct action
- MINERVA: cultural wisdom, emotional depth, narrative insight  
- HERMES: pattern recognition, systems thinking, witty observations

Three distinct voices in real discussion."""
}


class ChatRequest(BaseModel):
    persona: str = "ajani"
    message: str
    conversation_id: Optional[str] = None


class ChatResponse(BaseModel):
    persona: str
    response: str
    conversation_id: str
    timestamp: str


@router.post("/send", response_model=ChatResponse)
async def send_message(req: ChatRequest):
    """
    Send a message to an AI persona and get a response
    """
    persona = req.persona.lower()
    
    # Validate persona
    if persona not in PERSONA_PROMPTS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown persona: {persona}. Available: {list(PERSONA_PROMPTS.keys())}"
        )
    
    # Check if LLM key is available
    if not EMERGENT_LLM_KEY:
        raise HTTPException(
            status_code=503,
            detail="AI services are currently offline. Please configure EMERGENT_LLM_KEY."
        )
    
    try:
        # Get or create conversation
        conversation_id = req.conversation_id or f"conv_{persona}_{datetime.now(timezone.utc).timestamp()}"
        
        # Load conversation history from MongoDB
        conversation_doc = await db.conversations.find_one(
            {"conversation_id": conversation_id},
            {"_id": 0}
        )
        
        if not conversation_doc:
            # Create new conversation
            conversation_doc = {
                "conversation_id": conversation_id,
                "persona": persona,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "message_count": 0
            }
            await db.conversations.insert_one(conversation_doc)
        
        # Create LLM chat instance with conversation history
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=conversation_id,
            system_message=PERSONA_PROMPTS[persona]
        ).with_model("openai", "gpt-5.2")
        
        # Load previous messages into chat context
        messages = await db.messages.find(
            {"conversation_id": conversation_id},
            {"_id": 0}
        ).sort("timestamp", 1).limit(20).to_list(20)
        
        # Reconstruct conversation history in chat
        for msg in messages:
            if msg["role"] == "user":
                await chat.send_message(UserMessage(text=msg["content"]), store_history=False)
        
        # Send new message
        user_msg = UserMessage(text=req.message)
        ai_response = await chat.send_message(user_msg)
        
        # Store user message in database
        user_message_doc = {
            "conversation_id": conversation_id,
            "role": "user",
            "content": req.message,
            "persona": None,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        await db.messages.insert_one(user_message_doc)
        
        # Store AI response in database
        ai_message_doc = {
            "conversation_id": conversation_id,
            "role": "assistant",
            "content": ai_response,
            "persona": persona,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        await db.messages.insert_one(ai_message_doc)
        
        # Update conversation
        await db.conversations.update_one(
            {"conversation_id": conversation_id},
            {
                "$set": {"updated_at": datetime.now(timezone.utc).isoformat()},
                "$inc": {"message_count": 2}
            }
        )
        
        return ChatResponse(
            persona=persona,
            response=ai_response,
            conversation_id=conversation_id,
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")


@router.get("/conversations")
async def list_conversations(persona: Optional[str] = None, limit: int = 20):
    """
    List all conversations, optionally filtered by persona
    """
    query = {}
    if persona:
        query["persona"] = persona.lower()
    
    conversations = await db.conversations.find(
        query,
        {"_id": 0}
    ).sort("updated_at", -1).limit(limit).to_list(limit)
    
    return {"conversations": conversations}


@router.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    """
    Get a specific conversation with its message history
    """
    conversation = await db.conversations.find_one(
        {"conversation_id": conversation_id},
        {"_id": 0}
    )
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    messages = await db.messages.find(
        {"conversation_id": conversation_id},
        {"_id": 0}
    ).sort("timestamp", 1).to_list(1000)
    
    return {
        "conversation": conversation,
        "messages": messages
    }


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """
    Delete a conversation and all its messages
    """
    # Delete messages
    await db.messages.delete_many({"conversation_id": conversation_id})
    
    # Delete conversation
    result = await db.conversations.delete_one({"conversation_id": conversation_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return {"success": True, "deleted": conversation_id}


@router.post("/trinity")
async def trinity_counsel(question: str):
    """
    Get responses from all three AI personas (Trinity Counsel)
    """
    if not EMERGENT_LLM_KEY:
        raise HTTPException(status_code=503, detail="AI services offline")
    
    try:
        session_id = f"trinity_{datetime.now(timezone.utc).timestamp()}"
        
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=session_id,
            system_message=PERSONA_PROMPTS["trinity"]
        ).with_model("openai", "gpt-5.2")
        
        response = await chat.send_message(UserMessage(text=f"TOPIC FOR COUNSEL: {question}"))
        
        return {
            "question": question,
            "discussion": response,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Trinity counsel error: {str(e)}")
