# 07 — PROJECT ARTIFACT VAULT SPEC

## Document Control
- Subsystem: **Project Artifact Vault**
- Status: Draft v1
- Last Updated: 2026-02-17
- Scope: Project-scoped artifact storage, lineage, and retrieval

---

## 1. Purpose

The Project Artifact Vault is the source of truth for outputs generated during Blueprint -> Build -> Modify workflows.

It guarantees:
- project isolation
- versioned history
- reproducible decision context

---

## 2. Artifact Classes

- Blueprint documents
- Build plans and checklists
- Test plans and test results
- Design diagrams and component maps
- Decision records
- Retrospectives and change notes

---

## 3. Required Artifact Metadata

Every artifact must include:
- artifact_id
- project_id
- artifact_type
- version_tag
- stage (blueprint/build/modify)
- authoring role (Ajani/Minerva/Hermes/Atlas/User)
- timestamp
- parent_artifact_id (if derived)
- validation_status

---

## 4. Storage and Isolation Rules

- Artifacts are strictly project-scoped.
- Cross-project writes are prohibited.
- Read access is contextual and policy-bound.
- Archive operations must preserve lineage metadata.

---

## 5. Versioning Rules

- New major idea branch: version branch increment
- Modify-stage accepted change: minor version bump
- Blocked/invalid changes: no version bump

Version updates require supporting rationale entries.

---

## 6. Artifact Lifecycle

1. Draft creation
2. Validation pass
3. Publish as canonical artifact
4. Revision or supersession
5. Archive (readable, immutable)

---

## 7. Search and Retrieval

Minimum retrieval filters:
- project
- stage
- artifact type
- version
- validation status

Search results should return compact summaries plus lineage references.

---

## 8. Integrity and Audit

Vault should support:
- immutable history records
- conflict-safe updates
- change attribution
- rollback to previous known-good artifacts

---

## 9. Policy Integration

- Hermes can block publication of policy-violating artifacts.
- Flagged artifacts may be stored but marked non-canonical.
- Blocked artifacts cannot overwrite canonical state.

---

## 10. Non-Goals

- Not a general-purpose file dump
- Not a replacement for material source vaulting
- Not a cross-project collaboration layer in v1
