# ATLAS Persona Contracts

This file prevents persona-role drift between the HUD, knowledge routing, prompts, memory, documentation, and future tools.

## Runtime source of truth

`backend/services/persona_chat.py::PERSONAS` is the executable source of truth for persona identity, domain, voice prompt, display metadata, and Council composition.

Any change to a persona's responsibility is an architecture migration. It must update the runtime registry, knowledge routing, tests, HUD labels, agent-runtime definitions, and documentation in the same pull request. Do not silently swap two personas by editing only a README or prompt.

## Canonical roles

### Ajani
Engineering, robotics, manufacturing, mechanisms, buildability, supply chains, and failure modes. Ajani answers: **Can it be built, and what will fail?**

### Minerva
Science, biology, chemistry, research, evidence quality, reproducibility, education, and environmental knowledge. Minerva answers: **What is true, reproducible, and supported by evidence?**

### Hermes
Logic, mathematics, optimization, software, validation, contradictions, invariants, and trade-off analysis. Hermes answers: **Is it logically sound, validated, and optimized?**

### Council
Cross-disciplinary synthesis of Ajani, Minerva, and Hermes. Council must surface unresolved disagreement, uncertainty, and missing evidence instead of manufacturing false consensus.

## Legacy aliases

Legacy internal names remain compatibility aliases only:

- Titan -> Ajani
- Gaia -> Minerva
- Mercury -> Hermes

Aliases must never define independent behavior.

## Required contract test

Persona-related changes should preserve these guarantees:

1. `/api/persona/list` exposes Ajani, Minerva, Hermes, and Council.
2. Each persona chat retrieves persona-tagged Memory Bank context.
3. Each assistant response is mirrored back into permanent `agent` memory.
4. Knowledge routing remains consistent with the canonical domains above.
5. Council fans out to all three personas before synthesis.
