.PHONY: test bootstrap phase5-status

PYTHONPATH=atlas-core-runtime/src:atlas-events/src:atlas-tasks/src:atlas-memory-engine/src:atlas-knowledge-engine/src:atlas-agent-runtime/src:atlas-diagnostics/src:atlas-api/src

test:
	PYTHONPATH=$(PYTHONPATH) pytest atlas-tests/tests

bootstrap:
	PYTHONPATH=$(PYTHONPATH) python phase-5-construction/bootstrap_demo.py

phase5-status:
	@echo "ATLAS Phase 5 scaffold"
	@echo "- Core runtime: scaffolded"
	@echo "- Events: in-memory service"
	@echo "- Tasks: in-memory service"
	@echo "- Memory: in-memory service"
	@echo "- Knowledge: in-memory service"
	@echo "- Agents: identity registry"
	@echo "- Diagnostics: health aggregation"
