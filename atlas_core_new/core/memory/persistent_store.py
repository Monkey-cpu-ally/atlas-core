"""
atlas_core_new/core/memory/persistent_store.py

Database-backed persistent memory store for conversations.
"""

from typing import Dict, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from .memory_models import MemoryItem, MemoryEntry, MemorySnapshot
from ...db.models import Conversation, ChatMessage


class PersistentMemoryStore:
    """
    Database-backed memory store. Persists conversations across sessions.
    """
    def __init__(self, db_session_factory):
        self._session_factory = db_session_factory
        self._current_conversation_id: Optional[int] = None
        self._items: Dict[str, MemoryItem] = {}
        self._transcript: List[MemoryEntry] = []

    def _get_db(self) -> Optional[Session]:
        if self._session_factory is None:
            return None
        try:
            return self._session_factory()
        except:
            return None

    def start_conversation(self, user_id: str, persona: str, title: Optional[str] = None) -> Optional[int]:
        """Start a new conversation and return its ID."""
        db = self._get_db()
        if not db:
            return None
        try:
            conv = Conversation(
                user_id=user_id,
                persona=persona,
                title=title or f"Chat with {persona.title()}",
                is_active=True
            )
            db.add(conv)
            db.commit()
            db.refresh(conv)
            self._current_conversation_id = conv.id
            self._transcript = []
            return conv.id
        except Exception as e:
            db.rollback()
            print(f"Error starting conversation: {e}")
            return None
        finally:
            db.close()

    def set_conversation(self, conversation_id: int) -> bool:
        """Set the current conversation and load its messages."""
        db = self._get_db()
        if not db:
            return False
        try:
            conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
            if not conv:
                return False
            self._current_conversation_id = conversation_id
            messages = db.query(ChatMessage).filter(
                ChatMessage.conversation_id == conversation_id
            ).order_by(ChatMessage.created_at).all()
            self._transcript = [
                MemoryEntry(role=m.role, content=m.content)
                for m in messages
            ]
            return True
        except Exception as e:
            print(f"Error loading conversation: {e}")
            return False
        finally:
            db.close()

    def add_entry(self, entry: MemoryEntry, persona: Optional[str] = None) -> None:
        """Add an entry to memory and persist to database."""
        self._transcript.append(entry)
        
        db = self._get_db()
        if not db or not self._current_conversation_id:
            return
        try:
            msg = ChatMessage(
                conversation_id=self._current_conversation_id,
                role=entry.role,
                persona=persona,
                content=entry.content
            )
            db.add(msg)
            conv = db.query(Conversation).filter(
                Conversation.id == self._current_conversation_id
            ).first()
            if conv:
                conv.message_count += 1
                conv.updated_at = datetime.utcnow()
            db.commit()
        except Exception as e:
            db.rollback()
            print(f"Error saving message: {e}")
        finally:
            db.close()

    def upsert_item(self, item: MemoryItem) -> None:
        self._items[item.key] = item

    def get_item(self, key: str) -> Optional[MemoryItem]:
        return self._items.get(key)

    def snapshot(self) -> MemorySnapshot:
        return MemorySnapshot(items=list(self._items.values()), transcript=list(self._transcript))

    def get_recent_messages(self, limit: int = 10) -> List[MemoryEntry]:
        """Get recent messages for context."""
        return self._transcript[-limit:] if self._transcript else []

    def get_conversation_history(self, user_id: str, persona: Optional[str] = None, limit: int = 20) -> List[dict]:
        """Get list of past conversations."""
        db = self._get_db()
        if not db:
            return []
        try:
            query = db.query(Conversation).filter(Conversation.user_id == user_id)
            if persona:
                query = query.filter(Conversation.persona == persona)
            convs = query.order_by(Conversation.updated_at.desc()).limit(limit).all()
            return [
                {
                    "id": c.id,
                    "persona": c.persona,
                    "title": c.title,
                    "message_count": c.message_count,
                    "updated_at": c.updated_at.isoformat() if c.updated_at else None
                }
                for c in convs
            ]
        except Exception as e:
            print(f"Error getting history: {e}")
            return []
        finally:
            db.close()

    def summarize_conversation(self, conversation_id: int, summary: str) -> bool:
        """Save a summary for a conversation."""
        db = self._get_db()
        if not db:
            return False
        try:
            conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
            if conv:
                conv.summary = summary
                db.commit()
                return True
            return False
        except Exception as e:
            db.rollback()
            print(f"Error saving summary: {e}")
            return False
        finally:
            db.close()
