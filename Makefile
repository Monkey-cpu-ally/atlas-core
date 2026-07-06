.PHONY: test bootstrap bootstrap-persist smoke phase5-status

PYTHONPATH=atlas-core-runtime/src:atlas-events/src:atlas-tasks/src:atlas-memory-engine/src:atlas-knowledge-engine/src:atlas-agent-runtime/src:atlas-diagnostics/src:atlas-api/src:atlas-persistence/src

test:
	PYTHONPATH=$(PYTHONPATH) pytest atlas-tests/tests

bootstrap:
	PYTHONPATH=$(PYTHONPATH) python phase-5-construction/bootstrap_demo.py

bootstrap-persist:
	PYTHONPATH=$(PYTHONPATH) python phase-5-construction/bootstrap_demo.py --persist

smoke: bootstrap test

phase5-status:
	@echo "ATLAS Phase 5 scaffold"
	@echo "- Core runtime: service registry and health contracts"
	@echo "- Events: optional JSON persistence"
	@echo "- Tasks: optional JSON persistence"
	@echo "- Memory: optional JSON persistence"
	@echo "- Knowledge: optional JSON persistence"
	@echo "- Agents: Hermes, Minerva, Ajani, Council identity registry"
	@echo "- API: route registry scaffold"
	@echo "- Diagnostics: health aggregation"
	@echo "- Persistence: JSON file store scaffold"
