"""Tests for the Project Gutenberg OPDS connector."""
from services.project_gutenberg_connector import parse_opds
from services.subject_source_router import sources_for_subject


SAMPLE = '''<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom" xmlns:dcterms="http://purl.org/dc/terms/">
  <entry>
    <id>https://www.gutenberg.org/ebooks/84</id>
    <title>Frankenstein; Or, The Modern Prometheus</title>
    <author><name>Shelley, Mary Wollstonecraft</name></author>
    <summary>A public-domain Project Gutenberg ebook.</summary>
    <dcterms:issued>1993-10-01</dcterms:issued>
    <dcterms:language>en</dcterms:language>
    <link rel="alternate" type="text/html" href="https://www.gutenberg.org/ebooks/84" />
    <link rel="http://opds-spec.org/acquisition" type="text/plain; charset=utf-8" href="https://example.invalid/84.txt" />
    <link rel="http://opds-spec.org/acquisition" type="application/epub+zip" href="https://example.invalid/84.epub" />
  </entry>
</feed>'''


def test_parse_gutenberg_opds_entry():
    rows = parse_opds(SAMPLE)
    assert len(rows) == 1
    book = rows[0]
    assert book["title"].startswith("Frankenstein")
    assert book["authors"] == ["Shelley, Mary Wollstonecraft"]
    assert book["provider"] == "Project Gutenberg"
    assert book["resource_type"] == "public_domain_book"
    assert book["links"]["catalog"].endswith("/84")
    assert book["links"]["text"].endswith("84.txt")
    assert book["links"]["epub"].endswith("84.epub")


def test_gutenberg_is_routed_to_creative_and_humanities_subjects():
    assert "project_gutenberg" in sources_for_subject("Creative Writing")
    assert "project_gutenberg" in sources_for_subject("History")
    assert "project_gutenberg" in sources_for_subject("Philosophy")
