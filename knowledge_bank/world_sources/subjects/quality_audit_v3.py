from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
RESOURCES = ROOT / "resources"
OUTPUT = ROOT / "quality_matrix_v3.json"

AUTHORITATIVE_DOMAINS = {
    "nasa.gov", "nist.gov", "nih.gov", "ncbi.nlm.nih.gov", "pubmed.ncbi.nlm.nih.gov",
    "mit.edu", "ocw.mit.edu", "openstax.org", "cern.ch", "ietf.org", "postgresql.org",
    "developer.mozilla.org", "faa.gov", "arxiv.org", "pubchem.ncbi.nlm.nih.gov",
}


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def iter_manifests():
    for path in sorted(RESOURCES.rglob("*.json")):
        try:
            manifest = load_json(path)
        except (json.JSONDecodeError, OSError):
            continue
        if isinstance(manifest, dict) and isinstance(manifest.get("resources"), list):
            yield path, manifest


def domain_for(url: str | None) -> str:
    if not url:
        return ""
    host = urlparse(url).hostname or ""
    return host.lower().removeprefix("www.")


def authoritative(domain: str) -> bool:
    return any(domain == item or domain.endswith("." + item) for item in AUTHORITATIVE_DOMAINS)


def state(resource: dict, key: str) -> bool:
    value = resource.get(key)
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in {"complete", "completed", "ready", "passed", "verified", "indexed", "ingested"}
    return False


def main() -> None:
    records = []
    for path, manifest in iter_manifests():
        subject = manifest.get("subject", "unknown")
        for index, resource in enumerate(manifest.get("resources", [])):
            url = resource.get("url")
            domain = domain_for(url)
            quality = 0
            quality += 30 if resource.get("title") else 0
            quality += 20 if resource.get("provider") else 0
            quality += 15 if resource.get("resource_type") else 0
            quality += 15 if url else 0
            quality += 20 if authoritative(domain) else 0

            ingested = state(resource, "ingested") or state(resource, "ingestion_status")
            retrievable = state(resource, "retrieval_tested") or state(resource, "retrieval_status")
            provenance = bool(resource.get("provider") and url)
            citation_ready = state(resource, "citation_ready") or provenance

            usable = ingested and retrievable and citation_ready
            records.append({
                "id": f"{path.relative_to(RESOURCES)}#{index}",
                "subject": subject,
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
            })

    total = len(records)
    high_quality = sum(r["quality_score"] >= 80 for r in records)
    ingested = sum(r["ingested"] for r in records)
    retrievable = sum(r["retrieval_tested"] for r in records)
    citation_ready = sum(r["citation_ready"] for r in records)
    usable = sum(r["usable_knowledge"] for r in records)

    def pct(value: int) -> float:
        return round(value / total * 100, 2) if total else 0.0

    report = {
        "schema_version": "3.0",
        "summary": {
            "resource_count": total,
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
            "usable_definition": "A resource is usable when ingestion, retrieval testing, and citation/provenance readiness are all verified.",
        },
        "resources": records,
    }
    OUTPUT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report["summary"], indent=2))


if __name__ == "__main__":
    main()
