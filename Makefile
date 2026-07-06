.PHONY: test bootstrap smoke phase5-status

PYTHONPATH=atlas-core-runtime/src:atlas-events/src:atlas-tasks/src:atlas-memory-engine/src:atlas-knowledge-engine/src:atlas-agent-runtime/src:atlas-diagnostics/src:atlas-api/src:atlas-persistence/src

test:
	PYTHONPATH=$(PYTHONPATH) pytest atlas-tests/tests

bootstrap:
	PYTHONPATH=$(PYTHONPATH) python phase-5-construction/bootstrap_demo.py

smoke: bootstrap test

phase5-status:
	@echo "ATLAS Phase 5 scaffold"
	@echo "- Core runtime: service registry and health contracts"
	@echo "- Events: in-memory event bus"
	@echo "- Tasks: in-memory task service"
	@echo "- Memory: in-memory memory service"
	@echo "- Knowledge: in-memory source and knowledge service"
	@echo "- Agents: Hermes, Minerva, Ajani, Council identity registry"
	@echo "- API: route registry scaffold"
	@echo "- Diagnostics: health aggregation"
	@echo "- Persistence: JSON file store scaffold"
