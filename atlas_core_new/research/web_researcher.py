"""
atlas_core_new/research/web_researcher.py

Real web research engine for AI personas.
Searches the actual internet for scientific papers, articles, patents,
technical resources, concept builds, video game designs, comic book tech,
and anime engineering concepts. Reads and extracts content, then synthesizes
findings for persona hypothesis work.

Uses trafilatura for web content extraction (web_scraper integration).
Sources: arXiv, Semantic Scholar, Wikipedia, PubMed, gaming/comic/anime wikis.
"""

import re
import logging
import time
import hashlib
from datetime import datetime
from typing import Optional
from urllib.parse import quote_plus

import trafilatura
import httpx

logger = logging.getLogger("atlas.web_researcher")

SEARCH_SOURCES = {
    "arxiv": {
        "label": "arXiv (Scientific Papers)",
        "search_url": "https://export.arxiv.org/api/query?search_query={query}&start=0&max_results={limit}",
        "type": "api",
    },
    "wikipedia": {
        "label": "Wikipedia",
        "search_url": "https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={query}&srlimit={limit}&format=json",
        "type": "api",
    },
    "semantic_scholar": {
        "label": "Semantic Scholar (Academic Papers)",
        "search_url": "https://api.semanticscholar.org/graph/v1/paper/search?query={query}&limit={limit}&fields=title,abstract,url,year,citationCount,authors",
        "type": "api",
    },
    "pubmed": {
        "label": "PubMed (Biomedical)",
        "search_url": "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={query}&retmax={limit}&retmode=json",
        "type": "api",
    },
}

DOMAIN_SEARCH_TERMS = {
    "robotics": ["robotics actuator design", "bio-inspired locomotion", "soft robotics mechanisms", "robot kinematics"],
    "ecology": ["ecosystem engineering", "ecological restoration technology", "biodegradable robotics", "environmental monitoring systems"],
    "advanced_chemistry": ["novel catalysts synthesis", "computational chemistry materials", "green chemistry processes"],
    "quantum_mechanics": ["quantum computing materials", "quantum entanglement applications", "topological quantum states"],
    "bio_architecture": ["biomimetic architecture", "living building materials", "mycelium construction"],
    "energy_systems": ["hydrogen fuel cell efficiency", "solid state batteries", "thermoelectric generators"],
    "materials_science": ["metamaterials engineering", "self-healing materials", "graphene applications"],
    "computing": ["neuromorphic computing", "optical processors", "DNA data storage"],
    "bioelectric_medicine": ["bioelectric signaling therapy", "electroceuticals", "bioelectronic medicine devices"],
    "nanotechnology": ["nanoscale fabrication", "nanorobotics medical", "quantum dot applications"],
    "photonics": ["photonic crystals", "silicon photonics", "optical computing chips"],
    "fluid_dynamics": ["microfluidics lab-on-chip", "turbulence control", "computational fluid dynamics"],
    "thermodynamics": ["entropy engineering", "thermoelectric cooling", "waste heat recovery"],
    "genetics": ["CRISPR gene editing advances", "synthetic biology", "epigenetic programming"],
    "aerospace_engineering": ["hypersonic materials", "reentry thermal protection", "ion propulsion systems"],
}

CREATIVE_SEARCH_TERMS = {
    "ajani": {
        "concept_builds": [
            "DIY energy harvesting device build",
            "perpetual motion concept prototype",
            "kinetic energy generator homemade",
            "crystal energy storage concept design",
        ],
        "video_games": [
            "Horizon Zero Dawn machine energy core design",
            "Death Stranding chiral crystal energy technology",
            "Warframe void energy reactor lore",
            "Destiny 2 arc solar void light energy system",
            "Metal Gear solid energy weapon technology",
        ],
        "comics_anime": [
            "Black Panther vibranium energy absorption technology",
            "Fullmetal Alchemist transmutation circle energy",
            "Dr. Stone science kingdom inventions build",
            "Akira psychic energy containment technology",
            "Storm X-Men weather energy manipulation power",
        ],
    },
    "minerva": {
        "concept_builds": [
            "bio-inspired self-healing material prototype",
            "CRISPR gene editing home lab concept",
            "biomimicry design nature-inspired engineering",
            "living material mycelium fabrication build",
        ],
        "video_games": [
            "Horizon Zero Dawn biome restoration terraforming",
            "The Last of Us cordyceps fungal biology mutation",
            "Resident Evil bioweapon genetic engineering lore",
            "Xenoblade Chronicles biological technology ether",
            "Subnautica alien ecosystem biology design",
        ],
        "comics_anime": [
            "Poison Ivy plant-human hybrid biology DC comics",
            "Swamp Thing bio-restorative formula plant elemental",
            "Nausicaa toxic jungle purification ecology",
            "Cells at Work biology immune system anime",
            "Venom symbiote biology bonding mechanism marvel",
        ],
    },
    "hermes": {
        "concept_builds": [
            "nanoscale fabrication DIY electron microscope build",
            "atomic force microscope homemade concept",
            "precision manufacturing maker CNC build",
            "nanoparticle synthesis home lab concept",
        ],
        "video_games": [
            "Deus Ex nanite augmentation technology lore",
            "Crysis nanosuit technology nanotechnology design",
            "Prey Morgan Yu neuromod nanotechnology",
            "Cyberpunk 2077 nanowire cyberware technology",
            "Nier Automata machine lifeform nanomachine design",
        ],
        "comics_anime": [
            "Iron Man nanotech bleeding edge armor marvel",
            "Ghost in the Shell cyberbrain nanotechnology",
            "Batman Beyond nanotech suit technology DC",
            "Blame Netsphere silicon life nanotechnology manga",
            "Appleseed bioroid nanotechnology design",
        ],
    },
}

PERSONA_PROJECT_CREATIVE_TERMS = {
    "ajani": {
        "prometheus-pulse": ["perpetual energy device concept", "zero point energy sci-fi", "vibranium energy core Black Panther"],
        "ghost-diamond": ["phase shifting technology sci-fi", "density manipulation superpower", "Kitty Pryde phasing power mechanics"],
        "ra-crystal": ["solar energy crystal sci-fi technology", "Kryptonian sun crystal Superman", "solarium energy anime"],
    },
    "minerva": {
        "phoenix-strand": ["regeneration healing factor Wolverine biology", "salamander axolotl regeneration research", "Deadpool healing factor science"],
        "anansi-weave": ["ancestral memory DNA genetics sci-fi", "genetic memory Assassins Creed animus", "dormant gene activation anime"],
        "eden-protocol": ["genetic ethics sci-fi Gattaca", "bioethics genetic engineering manga", "Jurassic Park genetics chaos theory"],
    },
    "hermes": {
        "scarab-fleet": ["medical nanobot swarm sci-fi design", "nanomachine medical Deus Ex", "Inner Space movie nanobot concept"],
        "terrabot-bloom": ["pollution eating nanobots concept", "environmental cleanup nanotechnology sci-fi", "terraforming nanomachine anime"],
        "daedalus-forge": ["atomic construction nanotechnology", "molecular assembler sci-fi concept", "nanofabrication 3D printing atomic"],
    },
}


def _hash_url(url: str) -> str:
    return hashlib.md5(url.encode()).hexdigest()[:12]


def search_arxiv(query: str, limit: int = 5) -> list:
    try:
        url = f"https://export.arxiv.org/api/query?search_query=all:{quote_plus(query)}&start=0&max_results={limit}"
        with httpx.Client(timeout=15) as client:
            resp = client.get(url)
        if resp.status_code != 200:
            return []

        import xml.etree.ElementTree as ET
        root = ET.fromstring(resp.text)
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        results = []
        for entry in root.findall("atom:entry", ns):
            title = entry.find("atom:title", ns)
            summary = entry.find("atom:summary", ns)
            link = entry.find("atom:id", ns)
            published = entry.find("atom:published", ns)
            authors = entry.findall("atom:author/atom:name", ns)
            results.append({
                "source": "arxiv",
                "title": title.text.strip().replace("\n", " ") if title is not None else "Unknown",
                "abstract": summary.text.strip().replace("\n", " ")[:600] if summary is not None else "",
                "url": link.text.strip() if link is not None else "",
                "published": published.text[:10] if published is not None else "",
                "authors": [a.text for a in authors[:3]],
                "citation_count": None,
            })
        return results
    except Exception as e:
        logger.warning(f"arXiv search failed: {e}")
        return []


def search_semantic_scholar(query: str, limit: int = 5) -> list:
    try:
        url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={quote_plus(query)}&limit={limit}&fields=title,abstract,url,year,citationCount,authors"
        with httpx.Client(timeout=15) as client:
            resp = client.get(url)
        if resp.status_code != 200:
            return []
        data = resp.json()
        results = []
        for paper in data.get("data", []):
            authors = paper.get("authors", [])
            results.append({
                "source": "semantic_scholar",
                "title": paper.get("title", "Unknown"),
                "abstract": (paper.get("abstract") or "")[:600],
                "url": paper.get("url", ""),
                "published": str(paper.get("year", "")),
                "authors": [a.get("name", "") for a in authors[:3]],
                "citation_count": paper.get("citationCount"),
            })
        return results
    except Exception as e:
        logger.warning(f"Semantic Scholar search failed: {e}")
        return []


def search_wikipedia(query: str, limit: int = 3) -> list:
    try:
        url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={quote_plus(query)}&srlimit={limit}&format=json"
        with httpx.Client(timeout=10) as client:
            resp = client.get(url)
        if resp.status_code != 200:
            return []
        data = resp.json()
        results = []
        for item in data.get("query", {}).get("search", []):
            snippet = re.sub(r'<[^>]+>', '', item.get("snippet", ""))
            results.append({
                "source": "wikipedia",
                "title": item.get("title", ""),
                "abstract": snippet[:500],
                "url": f"https://en.wikipedia.org/wiki/{quote_plus(item.get('title', '').replace(' ', '_'))}",
                "published": "",
                "authors": [],
                "citation_count": None,
            })
        return results
    except Exception as e:
        logger.warning(f"Wikipedia search failed: {e}")
        return []


def search_pubmed(query: str, limit: int = 5) -> list:
    try:
        search_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={quote_plus(query)}&retmax={limit}&retmode=json"
        with httpx.Client(timeout=15) as client:
            resp = client.get(search_url)
        if resp.status_code != 200:
            return []
        data = resp.json()
        ids = data.get("esearchresult", {}).get("idlist", [])
        if not ids:
            return []

        id_str = ",".join(ids[:limit])
        summary_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={id_str}&retmode=json"
        with httpx.Client(timeout=15) as client:
            resp2 = client.get(summary_url)
        if resp2.status_code != 200:
            return []
        summary_data = resp2.json()
        results = []
        for pid in ids:
            info = summary_data.get("result", {}).get(pid, {})
            if not info or "error" in info:
                continue
            authors = info.get("authors", [])
            results.append({
                "source": "pubmed",
                "title": info.get("title", "Unknown"),
                "abstract": info.get("sorttitle", "")[:400],
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{pid}/",
                "published": info.get("pubdate", ""),
                "authors": [a.get("name", "") for a in authors[:3]],
                "citation_count": None,
            })
        return results
    except Exception as e:
        logger.warning(f"PubMed search failed: {e}")
        return []


FANDOM_WIKIS = {
    "marvel": {"host": "marvel.fandom.com", "label": "Marvel Comics"},
    "dc": {"host": "dc.fandom.com", "label": "DC Comics"},
    "horizon": {"host": "horizon.fandom.com", "label": "Horizon Zero Dawn"},
    "cyberpunk": {"host": "cyberpunk.fandom.com", "label": "Cyberpunk 2077"},
    "deus_ex": {"host": "deusex.fandom.com", "label": "Deus Ex"},
    "gits": {"host": "ghostintheshell.fandom.com", "label": "Ghost in the Shell"},
    "drstone": {"host": "dr-stone.fandom.com", "label": "Dr. Stone"},
    "fma": {"host": "fma.fandom.com", "label": "Fullmetal Alchemist"},
}


def search_creative_sources(query: str, limit: int = 3) -> list:
    results = []
    try:
        wiki_queries = [
            f"{query} technology",
            query,
        ]
        for wq in wiki_queries[:1]:
            url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={quote_plus(wq)}&srlimit={limit}&format=json"
            with httpx.Client(timeout=10) as client:
                resp = client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                for item in data.get("query", {}).get("search", []):
                    snippet = re.sub(r'<[^>]+>', '', item.get("snippet", ""))
                    results.append({
                        "source": "creative_reference",
                        "title": item.get("title", ""),
                        "abstract": snippet[:500],
                        "url": f"https://en.wikipedia.org/wiki/{quote_plus(item.get('title', '').replace(' ', '_'))}",
                        "published": "",
                        "authors": [],
                        "citation_count": None,
                    })
            time.sleep(0.3)
    except Exception as e:
        logger.warning(f"Creative Wikipedia search failed: {e}")

    for wiki_domain, wiki_config in FANDOM_WIKIS.items():
        try:
            search_url = f"https://{wiki_config['host']}/api.php?action=query&list=search&srsearch={quote_plus(query)}&srlimit=2&format=json"
            with httpx.Client(timeout=10, follow_redirects=True) as client:
                resp = client.get(search_url)
            if resp.status_code == 200:
                data = resp.json()
                for item in data.get("query", {}).get("search", []):
                    snippet = re.sub(r'<[^>]+>', '', item.get("snippet", ""))
                    title = item.get("title", "")
                    results.append({
                        "source": f"creative_{wiki_domain}",
                        "title": f"{title} ({wiki_config['label']})",
                        "abstract": snippet[:500],
                        "url": f"https://{wiki_config['host']}/wiki/{quote_plus(title.replace(' ', '_'))}",
                        "published": "",
                        "authors": [],
                        "citation_count": None,
                    })
            time.sleep(0.2)
        except Exception as e:
            logger.warning(f"Fandom wiki search failed for {wiki_domain}: {e}")

    return results


def search_concept_builds(query: str, persona: str = None, limit: int = 3) -> list:
    results = []
    search_terms = []

    if persona and persona in CREATIVE_SEARCH_TERMS:
        persona_terms = CREATIVE_SEARCH_TERMS[persona]
        import random
        for category in ["concept_builds", "video_games", "comics_anime"]:
            terms = persona_terms.get(category, [])
            if terms:
                search_terms.append(random.choice(terms))
    else:
        search_terms = [f"{query} concept build design", f"{query} sci-fi technology"]

    for term in search_terms[:3]:
        wiki_results = search_wikipedia(term, limit=2)
        for r in wiki_results:
            r["source"] = "creative_reference"
        results.extend(wiki_results)
        time.sleep(0.3)

    return results


def fetch_page_content(url: str, max_chars: int = 3000) -> Optional[str]:
    try:
        downloaded = trafilatura.fetch_url(url)
        if not downloaded:
            return None
        text = trafilatura.extract(downloaded)
        if text:
            return text[:max_chars]
        return None
    except Exception as e:
        logger.warning(f"Failed to fetch {url}: {e}")
        return None


def multi_source_search(query: str, domain: str = None, limit_per_source: int = 3,
                        persona: str = None, include_creative: bool = True) -> list:
    all_results = []

    all_results.extend(search_arxiv(query, limit=limit_per_source))
    time.sleep(0.3)
    all_results.extend(search_semantic_scholar(query, limit=limit_per_source))
    time.sleep(0.3)
    all_results.extend(search_wikipedia(query, limit=2))

    if domain in ("bioelectric_medicine", "genetics", "ecology"):
        time.sleep(0.3)
        all_results.extend(search_pubmed(query, limit=limit_per_source))

    if include_creative:
        time.sleep(0.3)
        creative_results = search_concept_builds(query, persona=persona, limit=2)
        all_results.extend(creative_results)

    seen_titles = set()
    deduplicated = []
    for r in all_results:
        title_key = r["title"].lower().strip()[:60]
        if title_key not in seen_titles:
            seen_titles.add(title_key)
            deduplicated.append(r)

    return deduplicated


def research_for_project(project_name: str, domain: str, hypothesis: str,
                         current_focus: str = None, secondary_domain: str = None,
                         deep_read_count: int = 2, persona: str = None,
                         include_creative: bool = True) -> dict:
    import random
    search_queries = []
    creative_queries = []

    if hypothesis:
        words = hypothesis.split()
        if len(words) > 8:
            key_terms = " ".join(words[:10])
            search_queries.append(key_terms)
        else:
            search_queries.append(hypothesis)

    if current_focus:
        search_queries.append(current_focus)

    domain_terms = DOMAIN_SEARCH_TERMS.get(domain, [])
    if domain_terms:
        search_queries.append(domain_terms[0])

    if secondary_domain:
        sec_terms = DOMAIN_SEARCH_TERMS.get(secondary_domain, [])
        if sec_terms and domain_terms:
            search_queries.append(f"{domain_terms[0]} {sec_terms[0]}")

    if include_creative and persona:
        persona_creative = CREATIVE_SEARCH_TERMS.get(persona, {})
        for category in ["concept_builds", "video_games", "comics_anime"]:
            terms = persona_creative.get(category, [])
            if terms:
                creative_queries.append(random.choice(terms))

        project_key = project_name.lower().replace(" ", "-").replace("_", "-")
        for codename, terms in PERSONA_PROJECT_CREATIVE_TERMS.get(persona, {}).items():
            if codename in project_key or project_key in codename:
                creative_queries.append(random.choice(terms))
                break

    all_sources = []
    for q in search_queries[:3]:
        results = multi_source_search(q, domain=domain, limit_per_source=3,
                                      persona=persona, include_creative=False)
        all_sources.extend(results)
        time.sleep(0.5)

    if include_creative and creative_queries:
        for cq in creative_queries[:3]:
            creative_results = search_creative_sources(cq, limit=2)
            all_sources.extend(creative_results)
            time.sleep(0.3)
            concept_results = search_concept_builds(cq, persona=persona, limit=2)
            all_sources.extend(concept_results)
            time.sleep(0.3)

    seen = set()
    unique_sources = []
    for s in all_sources:
        key = s["title"].lower().strip()[:50]
        if key not in seen:
            seen.add(key)
            unique_sources.append(s)

    deep_reads = []
    read_count = 0
    deep_read_sources = ("arxiv", "wikipedia", "semantic_scholar", "creative_reference",
                         "creative_marvel", "creative_dc", "creative_horizon", "creative_cyberpunk",
                         "creative_deus_ex", "creative_gits", "creative_drstone", "creative_fma")
    for source in unique_sources:
        if read_count >= deep_read_count:
            break
        if source.get("url") and source["source"] in deep_read_sources:
            url = source["url"]
            if source["source"] == "arxiv" and "/abs/" in url:
                url = url.replace("/abs/", "/html/")
            content = fetch_page_content(url, max_chars=2500)
            if content:
                deep_reads.append({
                    "title": source["title"],
                    "url": source["url"],
                    "source": source["source"],
                    "content_excerpt": content,
                })
                read_count += 1
            time.sleep(0.5)

    scientific_count = len([s for s in unique_sources if s["source"] in ("arxiv", "semantic_scholar", "pubmed", "wikipedia")])
    creative_count = len([s for s in unique_sources if s["source"].startswith("creative")])

    return {
        "timestamp": datetime.utcnow().isoformat(),
        "project": project_name,
        "domain": domain,
        "persona": persona,
        "queries_used": search_queries[:3],
        "creative_queries_used": creative_queries[:3],
        "sources_found": len(unique_sources),
        "scientific_sources": scientific_count,
        "creative_sources": creative_count,
        "sources": unique_sources[:20],
        "deep_reads": deep_reads,
        "deep_read_count": len(deep_reads),
    }


def build_research_context(research_data: dict, max_chars: int = 5000) -> str:
    if not research_data or not research_data.get("sources"):
        return ""

    scientific_sources = [s for s in research_data.get("sources", []) if not s["source"].startswith("creative")]
    creative_sources = [s for s in research_data.get("sources", []) if s["source"].startswith("creative")]

    context = "=== REAL-WORLD RESEARCH FINDINGS ===\n"
    context += f"Sources searched: arXiv, Semantic Scholar, Wikipedia, PubMed + Creative References (Games, Comics, Anime)\n"
    context += f"Total sources found: {research_data['sources_found']}"
    if research_data.get("scientific_sources") is not None:
        context += f" (Scientific: {research_data.get('scientific_sources', 0)}, Creative: {research_data.get('creative_sources', 0)})"
    context += "\n"
    context += f"Queries: {', '.join(research_data.get('queries_used', []))}\n"
    if research_data.get("creative_queries_used"):
        context += f"Creative queries: {', '.join(research_data.get('creative_queries_used', []))}\n"
    context += "\n"

    if scientific_sources:
        context += "--- KEY PAPERS & ARTICLES ---\n"
        for i, src in enumerate(scientific_sources[:8], 1):
            context += f"\n[{i}] {src['title']}"
            if src.get("authors"):
                context += f" — {', '.join(src['authors'][:2])}"
            if src.get("published"):
                context += f" ({src['published']})"
            context += f"\n    Source: {src['source'].upper()}"
            if src.get("citation_count"):
                context += f" | Citations: {src['citation_count']}"
            if src.get("url"):
                context += f"\n    URL: {src['url']}"
            if src.get("abstract"):
                context += f"\n    {src['abstract'][:250]}"
            context += "\n"

    if creative_sources:
        context += "\n--- CREATIVE INSPIRATION (Concept Builds, Games, Comics, Anime) ---\n"
        context += "Use these as INSPIRATION for your designs. Extract the underlying engineering principles.\n"
        context += "Ask: What real physics or biology makes this fictional concept almost possible?\n\n"
        for i, src in enumerate(creative_sources[:6], 1):
            source_label = src["source"].replace("creative_", "").replace("_", " ").upper()
            context += f"[C{i}] {src['title']}"
            context += f"\n    Source: {source_label}"
            if src.get("url"):
                context += f"\n    URL: {src['url']}"
            if src.get("abstract"):
                context += f"\n    {src['abstract'][:300]}"
            context += "\n"

    if research_data.get("deep_reads"):
        context += "\n--- DEEP-READ EXCERPTS ---\n"
        for dr in research_data["deep_reads"]:
            source_type = "CREATIVE" if dr["source"].startswith("creative") else "SCIENTIFIC"
            context += f"\nFrom [{source_type}]: {dr['title']} ({dr['source']})\n"
            context += f"URL: {dr['url']}\n"
            excerpt = dr["content_excerpt"][:1500]
            context += f"{excerpt}\n"
            context += "---\n"

    if len(context) > max_chars:
        context = context[:max_chars] + "\n[...truncated for prompt size]"

    return context


def save_research_sources(db, project_id: str, persona: str, research_data: dict):
    from atlas_core_new.db.models import ResearchSource

    sources_saved = 0
    for src in research_data.get("sources", [])[:10]:
        url_hash = _hash_url(src.get("url", "") or src.get("title", ""))
        existing = db.query(ResearchSource).filter(
            ResearchSource.project_id == project_id,
            ResearchSource.url_hash == url_hash,
        ).first()
        if existing:
            continue

        entry = ResearchSource(
            project_id=project_id,
            persona=persona,
            source_type=src.get("source", "web"),
            title=src.get("title", "Unknown")[:500],
            url=src.get("url", "")[:1000],
            url_hash=url_hash,
            authors=src.get("authors", []),
            published_date=src.get("published", ""),
            abstract=src.get("abstract", "")[:1000],
            citation_count=src.get("citation_count"),
            was_deep_read=any(dr.get("url") == src.get("url") for dr in research_data.get("deep_reads", [])),
            search_query=", ".join(research_data.get("queries_used", []))[:500],
        )
        db.add(entry)
        sources_saved += 1

    if sources_saved > 0:
        db.commit()

    return sources_saved


def get_project_sources(db, project_id: str, limit: int = 20) -> list:
    from atlas_core_new.db.models import ResearchSource
    sources = db.query(ResearchSource).filter(
        ResearchSource.project_id == project_id
    ).order_by(ResearchSource.created_at.desc()).limit(limit).all()

    return [{
        "id": s.id,
        "source_type": s.source_type,
        "title": s.title,
        "url": s.url,
        "authors": s.authors,
        "published_date": s.published_date,
        "abstract": s.abstract,
        "citation_count": s.citation_count,
        "was_deep_read": s.was_deep_read,
        "persona": s.persona,
        "created_at": s.created_at.isoformat() if s.created_at else None,
    } for s in sources]
