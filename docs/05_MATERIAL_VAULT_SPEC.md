# 05 — MATERIAL VAULT SPEC

## Document Control
- Subsystem: **Material Vault**
- Status: Draft v1
- Last Updated: 2026-02-17
- Scope: Source material storage, indexing, retrieval, and governance

---

## 1. Purpose

Material Vault is the canonical repository for study and build references used by Polymath Forge.

It exists to ensure:
- source traceability
- retrieval quality
- versioned knowledge curation

---

## 2. Supported Material Types

- Books and chapters
- Papers and reports
- Lecture notes
- Standards/specification documents
- Internal summaries and synthesis notes
- Dataset descriptors (metadata-level)

---

## 3. Metadata Standard (Required Fields)

Each material entry includes:
- material_id
- title
- author/source
- publication date (if known)
- domain tags
- difficulty level
- reliability score
- citation link or archive reference
- ingestion timestamp
- version

Entries missing required metadata are not publishable.

---

## 4. Taxonomy Model

Classification dimensions:
1. Subject mapping (links to Academy subjects)
2. Use type (theory / practice / reference / caution)
3. Level (intro / intermediate / advanced)
4. Risk profile (normal / sensitive)

---

## 5. Ingestion Pipeline

1. Intake and identity check
2. Metadata extraction
3. Duplicate detection
4. Reliability scoring
5. Domain tagging
6. Publish to vault index

Sensitive content requires Hermes review before publish.

---

## 6. Retrieval Rules

- Retrieval should prioritize:
  1. relevance
  2. reliability
  3. recency (when relevant)
  4. learner level fit
- Results should include citation context and confidence note.

No source should be returned without provenance.

---

## 7. Quality Control

Material quality checks:
- factual consistency
- source legitimacy
- duplication rate
- stale content flags
- citation completeness

Low-confidence materials are quarantined, not deleted.

---

## 8. Versioning and Curation

- Material updates create new versions.
- Prior versions remain recoverable for audit.
- Curation notes must explain:
  - why added
  - why revised
  - where used

---

## 9. Access and Safety

- Access respects project and mode context.
- Restricted materials are policy-gated.
- Bio/security-adjacent materials require simulation-only framing.

---

## 10. Non-Goals

- Not a raw file dump
- Not an unverified internet scrape archive
- Not a replacement for project artifact vaulting
