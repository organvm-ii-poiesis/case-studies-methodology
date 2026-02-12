"""Tests for the case study parser."""

from src.parser import CaseStudy, CaseStudySection, parse_frontmatter, parse_markdown


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

    def test_malformed_frontmatter_missing_close(self):
        """Frontmatter without closing --- should return text as-is."""
        text = "---\ntitle: Test\nNo closing delimiter."
        metadata, body = parse_frontmatter(text)
        # With only one ---, split produces < 3 parts, so no metadata extracted
        assert metadata == {}

    def test_frontmatter_with_colons_in_value(self):
        text = '---\ntitle: "Key: Value"\n---\nBody.'
        metadata, body = parse_frontmatter(text)
        assert metadata["title"] == '"Key: Value"'

    def test_frontmatter_preserves_whitespace_in_values(self):
        text = "---\ntitle:   Spaced Title  \n---\nBody."
        metadata, body = parse_frontmatter(text)
        assert metadata["title"] == "Spaced Title"


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

    def test_multiple_heading_levels(self):
        """Parse h1, h2, h3 correctly with proper level values."""
        text = "---\ntitle: Levels\n---\n# H1\nText.\n## H2\nText.\n### H3\nText."
        study = parse_markdown(text)
        assert len(study.sections) == 3
        assert study.sections[0].level == 1
        assert study.sections[0].heading == "H1"
        assert study.sections[1].level == 2
        assert study.sections[1].heading == "H2"
        assert study.sections[2].level == 3
        assert study.sections[2].heading == "H3"

    def test_unicode_content(self):
        """Handle unicode and special characters in content."""
        text = "---\ntitle: Ünïcödé Tëst\n---\n# Sección\nCafé résumé naïve über straße."
        study = parse_markdown(text)
        assert study.title == "Ünïcödé Tëst"
        assert study.sections[0].heading == "Sección"
        assert "Café" in study.sections[0].content

    def test_heading_with_special_characters(self):
        """Headings with punctuation and symbols parse correctly."""
        text = "---\ntitle: Test\n---\n# Results & Discussion (2026)\nSome text."
        study = parse_markdown(text)
        assert study.sections[0].heading == "Results & Discussion (2026)"

    def test_large_document_many_sections(self):
        """Parse a document with many sections without error."""
        sections_text = "\n".join(
            f"## Section {i}\nContent for section {i}." for i in range(50)
        )
        text = f"---\ntitle: Large Doc\n---\n{sections_text}"
        study = parse_markdown(text)
        assert len(study.sections) == 50
        assert study.sections[49].heading == "Section 49"

    def test_empty_section_content(self):
        """Sections with no content between headings still parse."""
        text = "---\ntitle: Test\n---\n# First\n# Second\nSome text."
        study = parse_markdown(text)
        assert len(study.sections) == 2
        assert study.sections[0].content == ""
        assert "Some text" in study.sections[1].content

    def test_section_case_insensitive_lookup(self):
        """get_section is case-insensitive."""
        text = "---\ntitle: Test\n---\n# Background\nInfo here."
        study = parse_markdown(text)
        assert study.get_section("background") is not None
        assert study.get_section("BACKGROUND") is not None

    def test_no_title_in_frontmatter(self):
        """When title is missing from frontmatter, default is used."""
        text = "---\nstatus: draft\n---\n# Intro\nText."
        study = parse_markdown(text)
        assert study.title == "Untitled Case Study"


class TestCaseStudyProperties:
    def test_organ_property(self):
        study = CaseStudy(title="Test", metadata={"organ": "II"})
        assert study.organ == "II"

    def test_default_status(self):
        study = CaseStudy(title="Test")
        assert study.status == "draft"

    def test_word_count_multiple_sections(self):
        study = CaseStudy(
            title="Test",
            sections=[
                CaseStudySection(heading="A", level=1, content="one two three"),
                CaseStudySection(heading="B", level=1, content="four five"),
            ],
        )
        assert study.word_count == 5
