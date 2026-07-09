import pytest

from services import (
    chronicle_engine,
    discovery_approval_pipeline,
    external_access_gateway,
    knowledge_record_writer,
    project_intelligence,
)


class FakeCursor:
    def __init__(self, items):
        self.items = list(items)

    async def to_list(self, _limit):
        return list(self.items)


class FakeCollection:
    def __init__(self):
        self.items = []
        self.indexes = []

    async def update_one(self, filter_doc, update_doc, upsert=False):
        key, value = next(iter(filter_doc.items()))
        replacement = dict(update_doc.get("$set", {}))
        for index, item in enumerate(self.items):
            if item.get(key) == value:
                self.items[index] = replacement
                return
        if upsert:
            self.items.append(replacement)

    def find(self, _query, _projection=None):
        return FakeCursor(self.items)

    async def create_index(self, spec, unique=False):
        self.indexes.append({"spec": spec, "unique": unique})


class FakeDB:
    def __init__(self):
        self.discovery_drafts = FakeCollection()
        self.discovery_reviews = FakeCollection()
        self.council_reviews = FakeCollection()
        self.knowledge_records = FakeCollection()
        self.chronicle_entries = FakeCollection()
        self.external_access_connections = FakeCollection()
        self.external_access_import_plans = FakeCollection()
        self.project_intelligence = FakeCollection()


@pytest.fixture(autouse=True)
def reset_persistence_state():
    discovery_approval_pipeline.reset_in_memory_state()
    external_access_gateway.reset_in_memory_state()
    project_intelligence.reset_in_memory_state()
    knowledge_record_writer.reset_in_memory_state()
    chronicle_engine.reset_in_memory_state()


@pytest.mark.asyncio
async def test_discovery_approval_persists_and_hydrates_required_collections():
    db = FakeDB()
    discovery_approval_pipeline.attach_mongo(db)
    knowledge_record_writer.attach_mongo(db)
    chronicle_engine.attach_mongo(db)

    await discovery_approval_pipeline.create_indexes()
    await knowledge_record_writer.create_indexes()
    await chronicle_engine.create_indexes()

    draft = discovery_approval_pipeline.create_draft(
        title="Startup persistence discovery",
        summary="A persistence fixture that must survive ATLAS restart hydration.",
        owner_ai="Minerva",
        evidence=[{"source_title": "test", "quality": "primary", "relevance": 90, "recency": 90}],
        source_refs=[{"title": "test", "kind": "fixture"}],
        related_subjects=["Software Engineering"],
    )
    review = discovery_approval_pipeline.add_review(
        discovery_id=draft["discovery_id"],
        reviewer_ai="Council",
        recommendation="approve",
        rationale="Valid persistence coverage fixture.",
        confidence_score=88,
    )
    decision = discovery_approval_pipeline.council_decide(
        discovery_id=draft["discovery_id"],
        decision="approved",
        rationale="Approved so record and chronicle persistence are exercised.",
    )

    await discovery_approval_pipeline.persist_draft(discovery_approval_pipeline.get_draft(draft["discovery_id"]))
    await discovery_approval_pipeline.persist_review(review)
    await discovery_approval_pipeline.persist_decision(decision)
    await knowledge_record_writer.persist_record(decision["knowledge_record"])
    await chronicle_engine.persist_entry(decision["chronicle_entry"])

    discovery_approval_pipeline.reset_in_memory_state()
    knowledge_record_writer.reset_in_memory_state()
    chronicle_engine.reset_in_memory_state()

    dcounts = await discovery_approval_pipeline.hydrate_from_mongo()
    kcounts = await knowledge_record_writer.hydrate_from_mongo()
    ccounts = await chronicle_engine.hydrate_from_mongo()

    assert dcounts == {"discovery_drafts": 1, "discovery_reviews": 1, "council_reviews": 1}
    assert kcounts["knowledge_records"] == 1
    assert ccounts["chronicle_entries"] == 1
    assert discovery_approval_pipeline.get_draft(draft["discovery_id"])["status"] == "approved"


@pytest.mark.asyncio
async def test_external_access_persists_defaults_import_plans_and_hydrates_on_startup():
    db = FakeDB()
    external_access_gateway.attach_mongo(db)
    await external_access_gateway.create_indexes()

    seeded = external_access_gateway.seed_default_connections()
    await external_access_gateway.persist_all(seeded["items"])
    gallery = next(item for item in seeded["items"] if item["connector_type"] == "gallery")
    plan = external_access_gateway.create_import_plan(
        connection_id=gallery["connection_id"],
        requested_scope="Persist selected style metadata only.",
        destination_bank="visual_reference_bank",
        related_projects=["ATLAS HUD"],
        require_council_review=True,
    )
    await external_access_gateway.persist_connection(external_access_gateway.get_connection(gallery["connection_id"]))
    await external_access_gateway.persist_import_plan(plan)

    external_access_gateway.reset_in_memory_state()
    counts = await external_access_gateway.hydrate_from_mongo()

    assert counts["connections"] >= 6
    assert counts["import_plans"] == 1
    assert external_access_gateway.get_connection(gallery["connection_id"])["last_import_plan_id"] == plan["import_plan_id"]
    assert external_access_gateway.list_import_plans()[0]["destination_bank"] == "visual_reference_bank"


@pytest.mark.asyncio
async def test_project_intelligence_persists_project_briefs_and_hydrates_on_startup():
    db = FakeDB()
    project_intelligence.attach_mongo(db)
    await project_intelligence.create_indexes()

    project = project_intelligence.create_project(
        name="Startup Persistence Lab",
        purpose="Confirm Project Intelligence survives ATLAS restart hydration.",
        owner_ai="Council",
        status="active",
        subject_tags=["Software Engineering", "Testing"],
    )
    project_intelligence.add_risk(
        project["project_id"],
        title="State could vanish after restart.",
        severity="high",
        mitigation="Hydrate project_intelligence from Mongo during startup.",
    )
    project_intelligence.add_recommendation(
        project["project_id"],
        title="Keep persistence tests beside command-surface tests.",
        owner_ai="Council",
        rationale="Startup recovery is a Headquarters quality gate.",
        confidence_score=91,
    )
    await project_intelligence.persist_project(project_intelligence.get_project(project["project_id"]))

    project_intelligence.reset_in_memory_state()
    counts = await project_intelligence.hydrate_from_mongo()
    brief = project_intelligence.project_brief(project["project_id"])

    assert counts == {"projects": 1}
    assert brief["name"] == "Startup Persistence Lab"
    assert brief["counts"]["risks"] == 1
    assert brief["counts"]["recommendations"] == 1
