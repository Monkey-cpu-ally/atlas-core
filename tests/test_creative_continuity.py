from creative_production.continuity import ContinuityEngine, ContinuityState


def test_continuity_engine_detects_character_prop_and_story_fact_changes():
    engine = ContinuityEngine()
    issues = engine.audit([
        ContinuityState(
            scene_number=1, character="Girl", location="Academy", time_of_day="afternoon",
            costume="navy uniform", condition="uninjured",
            props={"Star Horn": "in satchel"}, facts={"horn_owner": "fairies"},
        ),
        ContinuityState(
            scene_number=2, character="Girl", location="Mystic Forest", time_of_day="night",
            costume="white dress", condition="scratched arm",
            props={"Star Horn": "in hand"}, facts={"horn_owner": "Girl"},
        ),
    ])

    assert {issue.category for issue in issues} == {"costume", "condition", "prop", "story_fact"}
    assert any(issue.subject == "Star Horn" for issue in issues)
    assert any(issue.subject == "horn_owner" for issue in issues)


def test_continuity_engine_allows_location_and_time_progression():
    engine = ContinuityEngine()
    issues = engine.audit([
        ContinuityState(1, "Girl", "Academy", "afternoon", costume="navy uniform", condition="uninjured", props={"Star Horn": "in hand"}),
        ContinuityState(2, "Girl", "Mystic Forest", "night", costume="navy uniform", condition="uninjured", props={"Star Horn": "in hand"}),
    ])
    assert issues == []


def test_continuity_engine_compares_version_snapshots():
    engine = ContinuityEngine()
    before = {"continuity_state": {
        "scene_number": 3, "character": "Girl", "location": "Forest", "time_of_day": "night",
        "costume": "navy uniform", "condition": "scratched arm", "props": {"Star Horn": "glowing"},
        "facts": {"queen_alive": True},
    }}
    after = {"continuity_state": {
        "scene_number": 3, "character": "Girl", "location": "Forest", "time_of_day": "night",
        "costume": "navy uniform", "condition": "uninjured", "props": {"Star Horn": "dark"},
        "facts": {"queen_alive": False},
    }}
    issues = engine.compare_revisions(before, after)
    assert {issue.category for issue in issues} == {"condition", "prop", "story_fact"}
