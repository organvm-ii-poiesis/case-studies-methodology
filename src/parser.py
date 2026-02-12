"""Parse case study documents in markdown format."""

from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class CaseStudySection:
    """A section within a case study."""
    heading: str
    level: int
    content: str
    subsections: list[CaseStudySection] = field(default_factory=list)


@dataclass
class CaseStudy:
    """A parsed case study document."""
    title: str
    metadata: dict[str, str] = field(default_factory=dict)
    sections: list[CaseStudySection] = field(default_factory=list)

    @property
    def organ(self) -> str:
        return self.metadata.get("organ", "")

    @property
    def status(self) -> str:
        return self.metadata.get("status", "draft")

    def get_section(self, heading: str) -> CaseStudySection | None:
        for section in self.sections:
            if section.heading.lower() == heading.lower():
                return section
        return None

    @property
    def word_count(self) -> int:
        total = sum(len(s.content.split()) for s in self.sections)
        return total


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    """Extract YAML-like frontmatter from markdown text."""
    metadata: dict[str, str] = {}
    body = text

    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            for line in parts[1].strip().splitlines():
                if ":" in line:
                    key, _, value = line.partition(":")
                    metadata[key.strip()] = value.strip()
            body = parts[2].strip()

    return metadata, body


def parse_markdown(text: str) -> CaseStudy:
    """Parse a markdown case study into structured data."""
    metadata, body = parse_frontmatter(text)
    title = metadata.get("title", "Untitled Case Study")

    heading_pattern = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)
    sections: list[CaseStudySection] = []

    matches = list(heading_pattern.finditer(body))

    for i, match in enumerate(matches):
        level = len(match.group(1))
        heading = match.group(2).strip()
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        content = body[start:end].strip()
        sections.append(CaseStudySection(heading=heading, level=level, content=content))

    return CaseStudy(title=title, metadata=metadata, sections=sections)
