"""Cross-reference case studies with registry data."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class CrossReference:
    """A link between a case study and another entity."""
    source: str
    target: str
    relationship: str
    context: str = ""


@dataclass
class ReferenceIndex:
    """Index of cross-references across case studies."""
    references: list[CrossReference] = field(default_factory=list)

    def add(self, ref: CrossReference) -> None:
        self.references.append(ref)

    def find_by_source(self, source: str) -> list[CrossReference]:
        return [r for r in self.references if r.source == source]

    def find_by_target(self, target: str) -> list[CrossReference]:
        return [r for r in self.references if r.target == target]

    def find_by_relationship(self, relationship: str) -> list[CrossReference]:
        return [r for r in self.references if r.relationship == relationship]

    @property
    def unique_sources(self) -> set[str]:
        return {r.source for r in self.references}

    @property
    def unique_targets(self) -> set[str]:
        return {r.target for r in self.references}


def extract_repo_references(text: str) -> list[str]:
    """Extract repository name references from text."""
    import re
    pattern = r'`([a-z][a-z0-9-]*(?:--[a-z0-9-]+)?)`'
    return list(set(re.findall(pattern, text)))


def extract_organ_references(text: str) -> list[str]:
    """Extract ORGAN references from text."""
    import re
    pattern = r'ORGAN[-\s]([IV]+)'
    return list(set(re.findall(pattern, text)))
