"""Export case studies to various formats."""

from __future__ import annotations

from .parser import CaseStudy


def to_summary(case_study: CaseStudy) -> dict:
    """Generate a summary dict of a case study."""
    return {
        "title": case_study.title,
        "organ": case_study.organ,
        "status": case_study.status,
        "sections": len(case_study.sections),
        "word_count": case_study.word_count,
        "metadata": case_study.metadata,
    }


def to_markdown_outline(case_study: CaseStudy) -> str:
    """Generate a markdown outline from a case study."""
    lines = [f"# {case_study.title}", ""]
    if case_study.metadata:
        for key, value in case_study.metadata.items():
            lines.append(f"- **{key}**: {value}")
        lines.append("")

    for section in case_study.sections:
        indent = "  " * (section.level - 1)
        word_count = len(section.content.split())
        lines.append(f"{indent}- {section.heading} ({word_count} words)")

    return "\n".join(lines)


def to_evidence_checklist(case_study: CaseStudy) -> list[dict]:
    """Generate an evidence checklist for review."""
    expected_sections = [
        "Background", "Problem Statement", "Methodology",
        "Implementation", "Results", "Lessons Learned",
    ]
    checklist = []
    for section_name in expected_sections:
        found = case_study.get_section(section_name)
        checklist.append({
            "section": section_name,
            "present": found is not None,
            "word_count": len(found.content.split()) if found else 0,
        })
    return checklist
