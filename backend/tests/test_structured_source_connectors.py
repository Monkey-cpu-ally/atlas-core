"""Unit tests for ATLAS structured knowledge source routing."""

from services.structured_source_connectors import _openalex_abstract, provider_for_url


def test_provider_routing():
    cases = {
        "https://en.wikipedia.org/wiki/Robotics": "wikipedia",
        "https://www.wikidata.org/wiki/Q11012": "wikidata",
        "https://openalex.org/W2741809807": "openalex",
        "https://pubmed.ncbi.nlm.nih.gov/31452104/": "pubmed",
        "https://ntrs.nasa.gov/citations/20210020495": "nasa_ntrs",
        "https://www.nist.gov/data": "nist",
        "https://www.loc.gov/item/2014717546/": "library_of_congress",
    }
    for url, expected in cases.items():
        assert provider_for_url(url) == expected


def test_non_pubmed_ncbi_does_not_get_hijacked():
    assert provider_for_url("https://www.ncbi.nlm.nih.gov/books/NBK25499/") is None


def test_openalex_abstract_reconstruction():
    inverted = {
        "Knowledge": [0],
        "Bank": [1],
        "works": [2],
    }
    assert _openalex_abstract(inverted) == "Knowledge Bank works"


def test_unknown_provider_falls_back():
    assert provider_for_url("https://example.com/research") is None
