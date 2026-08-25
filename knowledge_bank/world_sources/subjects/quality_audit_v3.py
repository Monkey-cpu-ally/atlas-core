from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urlparse

from catalog_index_v1 import build_index

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "quality_matrix_v3.json"
RUNTIME_STATUS = ROOT / "runtime_status_v1.json"

AUTHORITATIVE_DOMAINS = {
    "nasa.gov", "nist.gov", "nih.gov", "ncbi.nlm.nih.gov", "pubmed.ncbi.nlm.nih.gov",
    "mit.edu", "ocw.mit.edu", "openstax.org", "cern.ch", "ietf.org", "postgresql.org",
    "developer.mozilla.org", "faa.gov", "arxiv.org", "pubchem.ncbi.nlm.nih.gov",
}


def domain_for(url: str | None) -> str:
    if not url:
        return ""
    host = urlparse(url).hostname or ""
    return host.lower().removeprefix("www.")


def authoritative(domain: str) -> bool:
    return any(domain == item or domain.endswith("." + item) for item in AUTHORITATIVE_DOMAINS)


def load_runtime_status() -> dict:
    if not RUNTIME_STATUS.is_file():
        return {}
    try:
        data = json.loads(RUNTIME_STATUS.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    resources = data.get("resources", data)
    return resources if isinstance(resources, dict) else {}


def main() -> None:
    catalog = build_index()
    runtime = load_runtime_status()
    records = []

    for resource_id, resource in catalog.items():
        url = resource.get("url")
        domain = domain_for(url)
        quality = 0
        quality += 30 if resource.get("title") else 0
        quality += 20 if resource.get("provider") else 0
        quality += 15 if resource.get("resource_type") else 0
        quality += 15 if url else 0
        quality += 20 if authoritative(domain) else 0

        live = runtime.get(resource_id, {}) if isinstance(runtime.get(resource_id, {}), dict) else {}
        ingested = bool(live.get("ingested", False))
        retrievable = bool(live.get("retrieval_passed", live.get("retrieval_tested", False)))
        provenance = bool(resource.get("provider") and url)
        citation_ready = bool(live.get("citation_ready", provenance))
        usable = bool(ingested and retrievable and citation_ready)

        records.append({
            "id": resource_id,
            "subject": resource.get("subject"),
            "title": resource.get("title"),
            "provider": resource.get("provider"),
            "url": url,
            "domain": domain,
            "authoritative": authoritative(domain),
            "quality_score": quality,
            "ingested": ingested,
            "retrieval_tested": retrievable,
            "citation_ready": citation_ready,
            "usable_knowledge": usable,
            "runtime_status_present": resource_id in runtime,
        })

    total = len(records)
    high_quality = sum(r["quality_score"] >= 80 for r in records)
    ingested = sum(r["ingested"] for r in records)
    retrievable = sum(r["retrieval_tested"] for r in records)
    citation_ready = sum(r["citation_ready"] for r in records)
    usable = sum(r["usable_knowledge"] for r in records)
    runtime_count = sum(r["runtime_status_present"] for r in records)

    def pct(value: int) -> float:
        return round(value / total * 100, 2) if total else 0.0

    report = {
        "schema_version": "3.1",
        "summary": {
            "resource_count": total,
            "runtime_status_resources": runtime_count,
            "high_quality_resources": high_quality,
            "source_quality_percent": pct(high_quality),
            "ingested_resources": ingested,
            "ingestion_percent": pct(ingested),
            "retrieval_tested_resources": retrievable,
            "retrieval_test_percent": pct(retrievable),
            "citation_ready_resources": citation_ready,
            "citation_ready_percent": pct(citation_ready),
            "usable_resources": usable,
            "usable_knowledge_percent": pct(usable),
            "usable_definition": "A resource is usable when runtime ingestion, retrieval verification, and citation/provenance readiness are all verified.",
        },
        "resources": records,
    }
    OUTPUT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report["summary"], indent=2))


if __name__ == "__main__":
    main()
