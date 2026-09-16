from ingestion import IngestionService


def test_markdown_sections_are_separate_chunks():
    sections = IngestionService._split_text(
        "# Measure title\n\n## First rule\nFirst rule details.\n\n## Second rule\nSecond rule details."
    )
    assert [section["title"] for section in sections] == ["First rule", "Second rule"]
    assert sections[0]["text"] == "First rule details."
    assert sections[1]["text"] == "Second rule details."
