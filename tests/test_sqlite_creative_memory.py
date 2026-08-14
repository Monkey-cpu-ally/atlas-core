from creative_intelligence.creative_memory import CreativeLesson
from creative_intelligence.sqlite_creative_memory import SQLiteCreativeMemory


def test_sqlite_creative_memory_persists_across_reopen(tmp_path):
    db_path = tmp_path / "creative_memory.sqlite3"
    memory = SQLiteCreativeMemory(str(db_path))
    memory.remember(
        CreativeLesson(
            project="Elsewhere",
            task="lighting study",
            references=["reference-a", "reference-b"],
            principle_attempted="use contrast to guide attention",
            outcome="focal point became clearer",
            critique="background still competed with the subject",
            revision="reduced background contrast",
            lesson="reserve the strongest value contrast for the intended focal point",
            confidence=0.9,
        )
    )

    reopened = SQLiteCreativeMemory(str(db_path))
    lessons = reopened.recall(project="Elsewhere")

    assert len(lessons) == 1
    assert lessons[0].lesson == "reserve the strongest value contrast for the intended focal point"
    assert lessons[0].references == ["reference-a", "reference-b"]


def test_sqlite_creative_memory_term_search(tmp_path):
    db_path = tmp_path / "creative_memory.sqlite3"
    memory = SQLiteCreativeMemory(str(db_path))
    memory.remember(
        CreativeLesson(
            project="Hyper Axel",
            task="silhouette study",
            references=["reference-c"],
            principle_attempted="clear silhouette",
            outcome="character reads at thumbnail scale",
            critique="prop overlaps the torso",
            revision="moved prop away from body mass",
            lesson="protect negative space around signature props",
            confidence=0.8,
        )
    )

    assert len(memory.recall(term="negative space")) == 1
    assert memory.recall(term="unrelated") == []
