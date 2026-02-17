"""
Custom Knowledge Pack System
Upload your own notes, summaries, and personal libraries.
Your AIs reference YOUR materials first.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime


@dataclass
class KnowledgeItem:
    """A single piece of custom knowledge"""
    id: str
    title: str
    content: str
    source: str
    category: str
    added_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content[:200] + "..." if len(self.content) > 200 else self.content,
            "source": self.source,
            "category": self.category,
            "added_at": self.added_at
        }


@dataclass
class CustomKnowledgePack:
    """A collection of custom knowledge items"""
    id: str
    name: str
    description: str
    owner: str
    items: List[KnowledgeItem] = field(default_factory=list)
    is_private: bool = True
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def add_item(self, item: KnowledgeItem):
        self.items.append(item)
    
    def remove_item(self, item_id: str) -> bool:
        for i, item in enumerate(self.items):
            if item.id == item_id:
                self.items.pop(i)
                return True
        return False
    
    def get_item(self, item_id: str) -> Optional[KnowledgeItem]:
        for item in self.items:
            if item.id == item_id:
                return item
        return None
    
    def search(self, query: str) -> List[KnowledgeItem]:
        """Simple search within pack items"""
        query = query.lower()
        return [
            item for item in self.items
            if query in item.title.lower() or query in item.content.lower()
        ]
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "owner": self.owner,
            "item_count": len(self.items),
            "is_private": self.is_private,
            "created_at": self.created_at
        }
    
    def to_dict_full(self) -> dict:
        """Full representation including items"""
        data = self.to_dict()
        data["items"] = [item.to_dict() for item in self.items]
        return data


class KnowledgePackRegistry:
    """Registry for custom knowledge packs"""
    
    def __init__(self):
        self._packs: Dict[str, CustomKnowledgePack] = {}
    
    def create_pack(self, name: str, description: str, owner: str = "default") -> CustomKnowledgePack:
        """Create a new knowledge pack"""
        pack_id = f"pack-{len(self._packs) + 1}-{name.lower().replace(' ', '-')[:20]}"
        pack = CustomKnowledgePack(
            id=pack_id,
            name=name,
            description=description,
            owner=owner
        )
        self._packs[pack_id] = pack
        return pack
    
    def get_pack(self, pack_id: str) -> Optional[CustomKnowledgePack]:
        return self._packs.get(pack_id)
    
    def list_packs(self, owner: Optional[str] = None) -> List[dict]:
        if owner:
            return [p.to_dict() for p in self._packs.values() if p.owner == owner]
        return [p.to_dict() for p in self._packs.values()]
    
    def delete_pack(self, pack_id: str) -> bool:
        if pack_id in self._packs:
            del self._packs[pack_id]
            return True
        return False
    
    def add_item_to_pack(self, pack_id: str, title: str, content: str, 
                          source: str, category: str) -> Optional[KnowledgeItem]:
        """Add a knowledge item to a pack"""
        pack = self.get_pack(pack_id)
        if not pack:
            return None
        
        item_id = f"item-{len(pack.items) + 1}-{title.lower().replace(' ', '-')[:15]}"
        item = KnowledgeItem(
            id=item_id,
            title=title,
            content=content,
            source=source,
            category=category
        )
        pack.add_item(item)
        return item
    
    def search_all_packs(self, query: str, owner: Optional[str] = None) -> List[dict]:
        """Search across all packs (or owner's packs)"""
        results = []
        for pack in self._packs.values():
            if owner and pack.owner != owner:
                continue
            matches = pack.search(query)
            for item in matches:
                results.append({
                    "pack_id": pack.id,
                    "pack_name": pack.name,
                    "item": item.to_dict()
                })
        return results


knowledge_pack_registry = KnowledgePackRegistry()


def get_context_from_packs(query: str, owner: str = "default") -> str:
    """Get relevant context from custom packs for a query"""
    results = knowledge_pack_registry.search_all_packs(query, owner)
    if not results:
        return ""
    
    context = "\n\n[FROM YOUR CUSTOM KNOWLEDGE]:\n"
    for result in results[:3]:
        context += f"- {result['item']['title']}: {result['item']['content'][:150]}...\n"
    return context
