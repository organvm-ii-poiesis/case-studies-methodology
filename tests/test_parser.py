"""Tests for the case study parser."""

from src.parser import CaseStudy, parse_frontmatter, parse_markdown


class TestParseFrontmatter:
    def test_with_frontmatter(self):
        text = "---\ntitle: Test\norgan: I\n---\nBody text here."
        metadata, body = parse_frontmatter(text)
        assert metadata["title"] == "Test"
        assert metadata["organ"] == "I"
        assert body == "Body text here."

    def test_without_frontmatter(self):
        text = "Just some text."
        metadata, body = parse_frontmatter(text)
        assert metadata == {}
        assert body == "Just some text."

    def test_empty_frontmatter(self):
        text = "---\n---\nBody."
        metadata, body = parse_frontmatter(text)
        assert metadata == {}
        assert body == "Body."


class TestParseMarkdown:
    def test_basic_parsing(self):
        text = "---\ntitle: My Study\nstatus: published\n---\n# Introduction\nSome intro text.\n## Background\nBackground info."
        study = parse_markdown(text)
        assert study.title == "My Study"
        assert study.status == "published"
        assert len(study.sections) == 2

    def test_word_count(self):
        text = "---\ntitle: Word Count Test\n---\n# Section\nOne two three four five."
        study = parse_markdown(text)
        assert study.word_count == 5

    def test_get_section(self):
        text = "---\ntitle: Test\n---\n# Methods\nMethodology here.\n# Results\nResults here."
        study = parse_markdown(text)
        methods = study.get_section("Methods")
        assert methods is not None
        assert "Methodology" in methods.content

    def test_get_section_not_found(self):
        text = "---\ntitle: Test\n---\n# Intro\nText."
        study = parse_markdown(text)
        assert study.get_section("Missing") is None

    def test_no_sections(self):
        text = "---\ntitle: Empty\n---\nJust text, no headings."
        study = parse_markdown(text)
        assert len(study.sections) == 0


class TestCaseStudyProperties:
    def test_organ_property(self):
        study = CaseStudy(title="Test", metadata={"organ": "II"})
        assert study.organ == "II"

    def test_default_status(self):
        study = CaseStudy(title="Test")
        assert study.status == "draft"
