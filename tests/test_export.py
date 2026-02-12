"""Tests for the export module."""

from src.export import to_evidence_checklist, to_markdown_outline, to_summary
from src.parser import CaseStudy, CaseStudySection


def _sample_study() -> CaseStudy:
    return CaseStudy(
        title="Sample Study",
        metadata={"organ": "II", "status": "published"},
        sections=[
            CaseStudySection(heading="Background", level=1, content="Background info here with enough words."),
            CaseStudySection(heading="Methodology", level=1, content="The methodology used was innovative."),
            CaseStudySection(heading="Results", level=1, content="Results were positive overall for the project."),
        ],
    )


class TestToSummary:
    def test_summary_fields(self):
        study = _sample_study()
        summary = to_summary(study)
        assert summary["title"] == "Sample Study"
        assert summary["organ"] == "II"
        assert summary["sections"] == 3
        assert summary["word_count"] > 0

    def test_empty_study(self):
        study = CaseStudy(title="Empty")
        summary = to_summary(study)
        assert summary["sections"] == 0
        assert summary["word_count"] == 0


class TestToMarkdownOutline:
    def test_outline_format(self):
        study = _sample_study()
        outline = to_markdown_outline(study)
        assert "# Sample Study" in outline
        assert "Background" in outline

    def test_includes_metadata(self):
        study = _sample_study()
        outline = to_markdown_outline(study)
        assert "organ" in outline


class TestToEvidenceChecklist:
    def test_checklist_structure(self):
        study = _sample_study()
        checklist = to_evidence_checklist(study)
        assert len(checklist) == 6

    def test_present_sections(self):
        study = _sample_study()
        checklist = to_evidence_checklist(study)
        sections_dict = {item["section"]: item for item in checklist}
        assert sections_dict["Background"]["present"] is True
        assert sections_dict["Methodology"]["present"] is True
        assert sections_dict["Problem Statement"]["present"] is False
