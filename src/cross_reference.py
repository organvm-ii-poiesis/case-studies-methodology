"""Cross-reference case studies with registry data."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .parser import CaseStudy


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

    def get_reference_graph(self) -> dict[str, list[str]]:
        """Return a dict representing the reference network.

        Keys are source identifiers, values are lists of targets
        referenced by that source.
        """
        graph: dict[str, list[str]] = {}
        for ref in self.references:
            if ref.source not in graph:
                graph[ref.source] = []
            if ref.target not in graph[ref.source]:
                graph[ref.source].append(ref.target)
        return graph

    def get_orphan_studies(self, studies: list[CaseStudy]) -> list[CaseStudy]:
        """Find studies that have no cross-references (neither source nor target).

        A study is orphaned if its title does not appear as a source
        in any reference in this index.
        """
        source_titles = self.unique_sources
        return [s for s in studies if s.title not in source_titles]


def extract_repo_references(text: str) -> list[str]:
    """Extract repository name references from backtick-quoted text."""
    pattern = r'`([a-z][a-z0-9-]*(?:--[a-z0-9-]+)?)`'
    return sorted(set(re.findall(pattern, text)))


def extract_organ_references(text: str) -> list[str]:
    """Extract ORGAN references (e.g. ORGAN-I, ORGAN-IV) from text."""
    pattern = r'ORGAN[-\s]([IV]+)'
    return sorted(set(re.findall(pattern, text)))


def build_from_studies(studies: list[CaseStudy]) -> ReferenceIndex:
    """Auto-build a ReferenceIndex by scanning all case study content.

    Scans each study's sections for backtick-quoted repo names and
    ORGAN-N mentions, creating cross-references from the study title
    to each discovered entity.
    """
    index = ReferenceIndex()

    for study in studies:
        full_text = "\n".join(section.content for section in study.sections)

        repo_refs = extract_repo_references(full_text)
        for repo in repo_refs:
            index.add(CrossReference(
                source=study.title,
                target=repo,
                relationship="references_repo",
                context=f"Found in case study: {study.title}",
            ))

        organ_refs = extract_organ_references(full_text)
        for organ_numeral in organ_refs:
            index.add(CrossReference(
                source=study.title,
                target=f"ORGAN-{organ_numeral}",
                relationship="references_organ",
                context=f"Found in case study: {study.title}",
            ))

    return index
