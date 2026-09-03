"""Validated loader, retrieval, and synthesis for ATLAS Creative Reference Library."""
from __future__ import annotations
import json, re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Tuple
LIBRARY_DIR=Path(__file__).resolve().parent
_TOKEN_RE=re.compile(r"[a-z0-9]+")
@dataclass(frozen=True)
class CreativeReference:
    reference_id:str; title:str; kind:str; category:str; study:Tuple[str,...]; disciplines:Tuple[str,...]=(); techniques:Tuple[str,...]=(); strengths:Tuple[str,...]=(); study_targets:Tuple[str,...]=(); limitations:Tuple[str,...]=(); provenance:Tuple[str,...]=(); relationships:Tuple[str,...]=()
    def retrieval_text(self): return (self.title,self.category,*self.study,*self.disciplines,*self.techniques,*self.strengths,*self.study_targets,*self.limitations,*self.relationships)
@dataclass(frozen=True)
class ReferenceMatch:
    reference:CreativeReference; score:int; matched_terms:Tuple[str,...]
@dataclass(frozen=True)
class ReferenceSynthesis:
    query:str; references:Tuple[ReferenceMatch,...]; principles:Tuple[str,...]; study_targets:Tuple[str,...]; limitations:Tuple[str,...]; provenance:Tuple[str,...]; project_identity:str=""; project_constraints:Tuple[str,...]=(); diversity_dimensions:Tuple[str,...]=()
class CreativeReferenceLibrary:
    PROFILE_FIELDS=("disciplines","techniques","strengths","study_targets","limitations","provenance","relationships")
    def __init__(self,references):
        ids=[r.reference_id for r in references]
        if len(ids)!=len(set(ids)): raise ValueError("duplicate creative reference id")
        self._references=tuple(references); self._by_id={r.reference_id:r for r in references}
    @classmethod
    def load_default(cls):
        creators=cls._read_json(LIBRARY_DIR/"creative_masters.json").get("creators",[]); works=cls._read_json(LIBRARY_DIR/"works_catalog.json").get("works",[]); refs=[]
        for item in creators: refs.append(cls._reference("creator",cls._required_text(item,"name"),cls._required_text(item,"category"),cls._required_list(item,"craft"),item))
        for item in works: refs.append(cls._reference("work",cls._required_text(item,"title"),cls._required_text(item,"medium"),cls._required_list(item,"study"),item))
        if not refs: raise ValueError("creative reference library is empty")
        return cls(refs)
    @classmethod
    def _reference(cls,kind,title,category,study,item): return CreativeReference(cls._id(kind,title),title,kind,category,tuple(study),**{f:tuple(cls._optional_list(item,f)) for f in cls.PROFILE_FIELDS})
    @staticmethod
    def _read_json(path):
        with path.open("r",encoding="utf-8") as h: return json.load(h)
    @staticmethod
    def _required_text(item,key):
        value=str(item.get(key,"")).strip()
        if not value: raise ValueError(f"missing required reference field: {key}")
        return value
    @staticmethod
    def _clean_list(value,key,*,required):
        if value is None and not required: return []
        if not isinstance(value,list) or (required and not value) or not all(isinstance(v,str) and v.strip() for v in value): raise ValueError(f"invalid {'required' if required else 'optional'} reference list: {key}")
        cleaned=[v.strip() for v in value]
        if len({v.casefold() for v in cleaned})!=len(cleaned): raise ValueError(f"duplicate values in reference list: {key}")
        return cleaned
    @classmethod
    def _required_list(cls,item,key): return cls._clean_list(item.get(key),key,required=True)
    @classmethod
    def _optional_list(cls,item,key): return cls._clean_list(item.get(key),key,required=False)
    @staticmethod
    def _id(kind,title):
        slug="".join(ch.lower() if ch.isalnum() else "-" for ch in title); return f"{kind}:{'-'.join(p for p in slug.split('-') if p)}"
    @staticmethod
    def _tokens(values): return {t for v in values for t in _TOKEN_RE.findall(v.casefold())}
    @staticmethod
    def _unique(values):
        seen=set(); result=[]
        for value in values:
            key=value.casefold()
            if key not in seen: seen.add(key); result.append(value)
        return tuple(result)
    @staticmethod
    def _project_constraints(values):
        if isinstance(values,(str,bytes)): raise ValueError("project constraints must be a list of strings")
        try: raw=list(values)
        except TypeError as exc: raise ValueError("project constraints must be a list of strings") from exc
        if not all(isinstance(v,str) and v.strip() for v in raw): raise ValueError("project constraints must contain non-empty strings")
        normalized=tuple(v.strip() for v in raw)
        if len({v.casefold() for v in normalized})!=len(normalized): raise ValueError("duplicate project constraints are not allowed")
        return normalized
    def all(self): return self._references
    def get(self,reference_id): return self._by_id.get(reference_id)
    def search(self,query):
        needle=query.strip().casefold(); return self.all() if not needle else tuple(r for r in self._references if any(needle in v.casefold() for v in r.retrieval_text()))
    def retrieve(self,query,*,limit=12,kind=None):
        if limit<1: raise ValueError("retrieval limit must be positive")
        if kind not in {None,"creator","work"}: raise ValueError("reference kind must be creator or work")
        terms=self._tokens([query])
        if not terms: return tuple()
        matches=[]
        for ref in self._references:
            if kind and ref.kind!=kind: continue
            title=terms&self._tokens([ref.title]); category=terms&self._tokens([ref.category]); study=terms&self._tokens(ref.study); profile=terms&self._tokens((*ref.disciplines,*ref.techniques,*ref.strengths,*ref.study_targets,*ref.limitations,*ref.relationships)); matched=title|category|study|profile
            if not matched: continue
            score=len(title)*8+len(category)*4+len(study)*3+len(profile)*2; phrase=query.strip().casefold()
            if phrase and phrase in ref.title.casefold(): score+=12
            if any(phrase and phrase in p.casefold() for p in (*ref.study,*ref.study_targets)): score+=6
            matches.append(ReferenceMatch(ref,score,tuple(sorted(matched))))
        matches.sort(key=lambda m:(-m.score,m.reference.title.casefold(),m.reference.reference_id)); return tuple(matches[:limit])
    @staticmethod
    def _diversity_key(match): return match.reference.kind,match.reference.category.casefold()
    def _select_diverse(self,matches,limit):
        selected=[]; used=set()
        for match in matches:
            key=self._diversity_key(match)
            if key not in used:
                selected.append(match); used.add(key)
                if len(selected)==limit: return tuple(selected)
        for match in matches:
            if match not in selected:
                selected.append(match)
                if len(selected)==limit: break
        return tuple(selected)
    def synthesize(self,query,*,limit=4,minimum_references=2,project_identity="",project_constraints=()):
        """Retrieve from creative intent; preserve constraints only as downstream boundaries."""
        if minimum_references<2: raise ValueError("synthesis requires at least two references")
        if limit<minimum_references: raise ValueError("synthesis limit must meet minimum references")
        identity=project_identity.strip(); constraints=self._project_constraints(project_constraints)
        # Hard constraints are guardrails, never positive inspiration/search terms.
        retrieval_query=" ".join(part for part in (query.strip(),identity) if part)
        candidates=self.retrieve(retrieval_query,limit=max(limit*4,12)); matches=self._select_diverse(candidates,limit)
        if len(matches)<minimum_references: raise ValueError("insufficient references for synthesis")
        refs=tuple(m.reference for m in matches); principles=self._unique(v for r in refs for v in (*r.techniques,*r.strengths,*r.study)); targets=self._unique(v for r in refs for v in r.study_targets); limitations=self._unique(v for r in refs for v in r.limitations); provenance=self._unique(v for r in refs for v in r.provenance); dimensions=self._unique(f"{r.kind}:{r.category}" for r in refs)
        return ReferenceSynthesis(query.strip(),matches,principles,targets,limitations,provenance,identity,constraints,dimensions)
    def stats(self):
        creators=sum(r.kind=="creator" for r in self._references); works=sum(r.kind=="work" for r in self._references); profiled=sum(bool(r.provenance or r.techniques or r.study_targets) for r in self._references); return {"total":len(self._references),"creators":creators,"works":works,"profiled":profiled}
