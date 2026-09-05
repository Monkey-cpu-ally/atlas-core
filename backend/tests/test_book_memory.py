"""Regression tests for Project Gutenberg -> ATLAS book-memory helpers."""
from services.book_memory import (
    chunk_book,
    gutenberg_numeric_id,
    select_book,
    strip_gutenberg_boilerplate,
)


def test_strip_gutenberg_boilerplate_keeps_book_body():
    raw = """Project Gutenberg header\n*** START OF THE PROJECT GUTENBERG EBOOK TEST BOOK ***\n\nCHAPTER I\nThe creature woke.\n\n*** END OF THE PROJECT GUTENBERG EBOOK TEST BOOK ***\nlicense footer"""
    cleaned = strip_gutenberg_boilerplate(raw)
    assert "CHAPTER I" in cleaned
    assert "The creature woke." in cleaned
    assert "Project Gutenberg header" not in cleaned
    assert "license footer" not in cleaned


def test_chunk_book_uses_overlap_and_respects_size():
    text = "\n\n".join(["A" * 700, "B" * 700, "C" * 700])
    chunks = chunk_book(text, max_chars=1000, overlap=100)
    assert len(chunks) >= 3
    assert all(len(chunk) <= 1100 for chunk in chunks)


def test_select_book_by_numeric_gutenberg_id():
    rows = [
        {"id": "https://www.gutenberg.org/ebooks/1342", "title": "Pride and Prejudice"},
        {"id": "https://www.gutenberg.org/ebooks/84", "title": "Frankenstein"},
    ]
    selected = select_book(rows, "84")
    assert selected is not None
    assert selected["title"] == "Frankenstein"
    assert gutenberg_numeric_id(selected) == "84"


def test_select_book_defaults_to_first_result():
    rows = [{"id": "https://www.gutenberg.org/ebooks/11", "title": "Alice's Adventures in Wonderland"}]
    assert select_book(rows)["title"].startswith("Alice")
