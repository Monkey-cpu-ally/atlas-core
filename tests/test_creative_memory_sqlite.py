from creative_intelligence.creative_memory import CreativeLesson
from creative_intelligence.creative_memory_sqlite import SQLiteCreativeMemory


def test_sqlite_creative_memory_survives_reopen(tmp_path):
    database = tmp_path / "creative.sqlite3"
    first = SQLiteCreativeMemory(str(database))
    first.remember(
        CreativeLesson(
            project="Elsewhere",
            task="lighting study",
            references=["reference-a", "reference-b"],
            principle_attempted="use negative space to delay the reveal",
            outcome="tension increased",
            critique="focal contrast was initially too weak",
            revision="strengthened subject separation",
            lesson="negative space works best when the focal path stays readable",
            confidence=0.8,
        )
    )

    reopened = SQLiteCreativeMemory(str(database))
    lessons = reopened.recall(project="Elsewhere")

    assert len(lessons) == 1
    assert lessons[0].references == ["reference-a", "reference-b"]
    assert lessons[0].confidence == 0.8


def test_sqlite_creative_memory_term_search(tmp_path):
    database = tmp_path / "creative.sqlite3"
    memory = SQLiteCreativeMemory(str(database))
    memory.remember(
        CreativeLesson(
            project="ATLAS",
            task="silhouette study",
            references=["study"],
            principle_attempted="clear silhouette",
            outcome="readable",
            critique="none",
            revision="none",
            lesson="shape hierarchy improves readability",
        )
    )

    assert len(memory.recall(term="hierarchy")) == 1
    assert memory.recall(term="unrelated") == []
