from llm_wiki.expand import extract_section, list_headings

SAMPLE = """---
type: concept
---

# Top

Intro paragraph.

## Thesis

First thesis paragraph with [[related-page]].

More detail here.

## Other

Unrelated section.
"""


def test_list_headings():
    headings = list_headings(SAMPLE)
    assert headings == [(1, "Top"), (2, "Thesis"), (2, "Other")]


def test_extract_section_exact_match():
    section = extract_section(SAMPLE, "Thesis")
    assert section is not None
    assert section.heading == "Thesis"
    assert "First thesis paragraph" in section.content
    assert "Unrelated section" not in section.content
    assert section.outbound_links == ["related-page"]


def test_extract_section_partial_match():
    section = extract_section(SAMPLE, "Oth")
    assert section is not None
    assert section.heading == "Other"


def test_extract_section_missing():
    assert extract_section(SAMPLE, "Missing") is None


def test_extract_section_does_not_match_substring_heading():
    text = "# Synthesis\n\nBody only.\n"
    assert extract_section(text, "thesis") is None
