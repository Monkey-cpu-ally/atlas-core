# ATLAS Graph Memory

Graph Memory is the relationship layer of ATLAS.

It connects projects, concepts, components, materials, sources, risks, AIs, Council decisions, skills, and knowledge domains.

---

# Core Files

- `ARCHITECTURE.md` — explains why ATLAS needs relationship memory.
- `DATA_MODEL.md` — defines graph node and edge schemas.
- `INITIAL_ATLAS_GRAPH.md` — first human-readable relationship map.

---

# What Graph Memory Answers

- Which projects connect to this idea?
- Which AI owns this domain?
- What sources support this claim?
- What risks appear across multiple projects?
- What materials or components repeat across inventions?
- What should ATLAS research next?

---

# MVP Target

Start with Markdown and JSON-style records.

Later upgrades:

- SQLite graph tables
- Neo4j-style graph database
- Searchable project relationships
- Source-to-claim mapping
- Automatic Council context retrieval

---

# Rule

Folders store files. Graph Memory stores meaning.
