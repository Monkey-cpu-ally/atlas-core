"""
Vector Store: Abstraction layer for vector memory storage.

Designed to work with:
- In-memory store (default, for development)
- Weaviate (for production)
- Pinecone (alternative)

Stores embeddings of:
- Decisions made by agents
- Summaries of completed tasks
- Lessons learned from failures
- User preferences and context
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
import hashlib


@dataclass
class VectorEntry:
    entry_id: str
    content: str
    embedding: Optional[List[float]]
    metadata: Dict[str, Any]
    entry_type: str
    created_at: str
    agent_source: Optional[str] = None
    task_id: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "entry_id": self.entry_id,
            "content": self.content[:500],
            "has_embedding": self.embedding is not None,
            "metadata": self.metadata,
            "entry_type": self.entry_type,
            "created_at": self.created_at,
            "agent_source": self.agent_source,
            "task_id": self.task_id
        }


class VectorStore:
    def __init__(self, backend: str = "memory"):
        self.backend = backend
        self.entries: Dict[str, VectorEntry] = {}
        self.type_index: Dict[str, List[str]] = {}
        self.task_index: Dict[str, List[str]] = {}
    
    def _generate_id(self, content: str) -> str:
        timestamp = datetime.now().isoformat()
        hash_input = f"{content[:100]}_{timestamp}"
        return f"vec_{hashlib.sha256(hash_input.encode()).hexdigest()[:16]}"
    
    def _simple_embedding(self, text: str) -> List[float]:
        words = text.lower().split()
        vector = [0.0] * 64
        
        for i, word in enumerate(words[:64]):
            char_sum = sum(ord(c) for c in word)
            vector[i % 64] += char_sum / 1000.0
        
        magnitude = sum(v * v for v in vector) ** 0.5
        if magnitude > 0:
            vector = [v / magnitude for v in vector]
        
        return vector
    
    def add(
        self,
        content: str,
        entry_type: str,
        metadata: Dict[str, Any] = None,
        agent_source: str = None,
        task_id: str = None,
        embedding: List[float] = None
    ) -> str:
        entry_id = self._generate_id(content)
        
        if embedding is None:
            embedding = self._simple_embedding(content)
        
        entry = VectorEntry(
            entry_id=entry_id,
            content=content,
            embedding=embedding,
            metadata=metadata or {},
            entry_type=entry_type,
            created_at=datetime.now().isoformat(),
            agent_source=agent_source,
            task_id=task_id
        )
        
        self.entries[entry_id] = entry
        
        if entry_type not in self.type_index:
            self.type_index[entry_type] = []
        self.type_index[entry_type].append(entry_id)
        
        if task_id:
            if task_id not in self.task_index:
                self.task_index[task_id] = []
            self.task_index[task_id].append(entry_id)
        
        return entry_id
    
    def search(
        self,
        query: str,
        entry_type: str = None,
        limit: int = 10
    ) -> List[Tuple[VectorEntry, float]]:
        query_embedding = self._simple_embedding(query)
        
        _candidates = []
        if entry_type and entry_type in self.type_index:
            candidate_ids = self.type_index[entry_type]
        else:
            candidate_ids = list(self.entries.keys())
        
        results = []
        for entry_id in candidate_ids:
            entry = self.entries[entry_id]
            if entry.embedding:
                similarity = self._cosine_similarity(query_embedding, entry.embedding)
                results.append((entry, similarity))
        
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:limit]
    
    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        if len(a) != len(b):
            return 0.0
        
        dot_product = sum(x * y for x, y in zip(a, b))
        magnitude_a = sum(x * x for x in a) ** 0.5
        magnitude_b = sum(x * x for x in b) ** 0.5
        
        if magnitude_a == 0 or magnitude_b == 0:
            return 0.0
        
        return dot_product / (magnitude_a * magnitude_b)
    
    def get_by_task(self, task_id: str) -> List[VectorEntry]:
        entry_ids = self.task_index.get(task_id, [])
        return [self.entries[eid] for eid in entry_ids if eid in self.entries]
    
    def get_by_type(self, entry_type: str) -> List[VectorEntry]:
        entry_ids = self.type_index.get(entry_type, [])
        return [self.entries[eid] for eid in entry_ids if eid in self.entries]
    
    def get_recent(self, limit: int = 20) -> List[VectorEntry]:
        sorted_entries = sorted(
            self.entries.values(),
            key=lambda e: e.created_at,
            reverse=True
        )
        return sorted_entries[:limit]
    
    def get_stats(self) -> Dict:
        return {
            "total_entries": len(self.entries),
            "types": {k: len(v) for k, v in self.type_index.items()},
            "tasks_tracked": len(self.task_index),
            "backend": self.backend
        }


class DecisionMemory(VectorStore):
    def store_decision(
        self,
        decision: str,
        agent: str,
        task_id: str,
        context: Dict[str, Any] = None,
        outcome: str = None
    ) -> str:
        return self.add(
            content=decision,
            entry_type="decision",
            metadata={
                "context": context or {},
                "outcome": outcome
            },
            agent_source=agent,
            task_id=task_id
        )
    
    def store_lesson(
        self,
        lesson: str,
        source_task: str,
        failure_type: str = None
    ) -> str:
        return self.add(
            content=lesson,
            entry_type="lesson",
            metadata={
                "failure_type": failure_type
            },
            task_id=source_task
        )
    
    def store_summary(
        self,
        summary: str,
        task_id: str,
        agents_involved: List[str]
    ) -> str:
        return self.add(
            content=summary,
            entry_type="summary",
            metadata={
                "agents": agents_involved
            },
            task_id=task_id
        )
    
    def recall_similar_decisions(self, situation: str, limit: int = 5) -> List[Dict]:
        results = self.search(situation, entry_type="decision", limit=limit)
        return [
            {
                "decision": entry.content,
                "agent": entry.agent_source,
                "similarity": score,
                "outcome": entry.metadata.get("outcome")
            }
            for entry, score in results
        ]
    
    def recall_lessons(self, context: str, limit: int = 5) -> List[Dict]:
        results = self.search(context, entry_type="lesson", limit=limit)
        return [
            {
                "lesson": entry.content,
                "task_id": entry.task_id,
                "similarity": score
            }
            for entry, score in results
        ]
