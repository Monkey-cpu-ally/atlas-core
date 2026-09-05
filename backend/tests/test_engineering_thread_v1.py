from services import project_intelligence as projects


def setup_function():
    projects.reset_in_memory_state()


def test_project_starts_with_engineering_dna_and_timeline():
    project = projects.create_project(name="Weaver Mk I", purpose="Robotic manufacturing platform", owner_ai="Hermes")
    assert project["engineering_dna"]["responsible_ai"] == "Hermes"
    assert project["engineering_timeline"][0]["event_type"] == "project.created"


def test_links_knowledge_and_primary_twin_into_thread():
    project = projects.create_project(name="Power Cell", purpose="Energy storage prototype")
    projects.link_knowledge_record(project["project_id"], "knowledge:cell-chemistry", "Cell chemistry", "validated")
    projects.link_digital_twin(project["project_id"], "twin:power-cell-v1", "Power Cell V1", "1.0", primary=True)
    thread = projects.engineering_thread(project["project_id"])
    assert thread["links"]["knowledge_records"][0]["record_id"] == "knowledge:cell-chemistry"
    assert thread["engineering_dna"]["primary_twin_id"] == "twin:power-cell-v1"
    assert len(thread["timeline"]) == 3


def test_duplicate_twin_link_is_rejected():
    project = projects.create_project(name="Scanner", purpose="Wearable resonance scanner")
    projects.link_digital_twin(project["project_id"], "twin:scanner")
    try:
        projects.link_digital_twin(project["project_id"], "twin:scanner")
        assert False, "duplicate twin should fail"
    except projects.ProjectIntelligenceError:
        pass


def test_version_change_updates_dna_and_timeline():
    project = projects.create_project(name="Green Bot", purpose="Environmental restoration robot", owner_ai="Minerva")
    projects.set_versions(project["project_id"], software_version="0.2.0", hardware_version="A2", actor="Hermes")
    current = projects.get_project(project["project_id"])
    assert current["engineering_dna"]["software_version"] == "0.2.0"
    assert current["engineering_dna"]["hardware_version"] == "A2"
    assert current["engineering_dna"]["revision"] == 2
    assert current["engineering_timeline"][-1]["event_type"] == "project.version.updated"


def test_thread_accepts_requirements_tests_simulations_and_code_changes():
    project = projects.create_project(name="Weaver", purpose="Multi-arm suspended robot")
    pid = project["project_id"]
    projects.add_project_item(pid, "requirements", {"title": "Eight camera coverage"})
    projects.add_project_item(pid, "tests", {"title": "Camera overlap validation", "status": "passed"})
    projects.add_project_item(pid, "simulations", {"title": "Workspace collision simulation", "status": "passed"})
    projects.add_project_item(pid, "code_changes", {"title": "Motion planner update", "commit_sha": "abc123"})
    thread = projects.engineering_thread(pid)
    assert len(thread["links"]["requirements"]) == 1
    assert len(thread["links"]["tests"]) == 1
    assert len(thread["links"]["simulations"]) == 1
    assert len(thread["links"]["code_changes"]) == 1
