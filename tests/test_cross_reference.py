"""Tests for the cross-reference module."""

from src.cross_reference import (
    CrossReference,
    ReferenceIndex,
    build_from_studies,
    extract_organ_references,
    extract_repo_references,
)
from src.parser import CaseStudy, CaseStudySection


class TestExtractRepoReferences:
    def test_finds_backtick_repo_names(self):
        text = "The `metasystem-master` repo is the flagship."
        refs = extract_repo_references(text)
        assert "metasystem-master" in refs

    def test_finds_double_dash_repo_names(self):
        text = "See `recursive-engine--generative-entity` for details."
        refs = extract_repo_references(text)
        assert "recursive-engine--generative-entity" in refs

    def test_ignores_non_backtick_names(self):
        text = "The metasystem-master repo is not in backticks."
        refs = extract_repo_references(text)
        assert refs == []

    def test_deduplicates_references(self):
        text = "`metasystem-master` and again `metasystem-master` here."
        refs = extract_repo_references(text)
        assert refs.count("metasystem-master") == 1

    def test_returns_sorted(self):
        text = "`zebra-repo` and `alpha-repo` mentioned."
        refs = extract_repo_references(text)
        assert refs == ["alpha-repo", "zebra-repo"]


class TestExtractOrganReferences:
    def test_finds_organ_with_dash(self):
        text = "ORGAN-II provides creative capabilities."
        refs = extract_organ_references(text)
        assert "II" in refs

    def test_finds_organ_with_space(self):
        text = "ORGAN IV handles orchestration."
        refs = extract_organ_references(text)
        assert "IV" in refs

    def test_finds_multiple_organs(self):
        text = "ORGAN-I feeds ORGAN-II which feeds ORGAN-III."
        refs = extract_organ_references(text)
        assert "I" in refs
        assert "II" in refs
        assert "III" in refs

    def test_deduplicates_organs(self):
        text = "ORGAN-I here and ORGAN-I there."
        refs = extract_organ_references(text)
        assert refs.count("I") == 1


class TestReferenceIndex:
    def test_add_and_find_by_source(self):
        index = ReferenceIndex()
        ref = CrossReference(source="Study A", target="repo-x", relationship="references_repo")
        index.add(ref)
        found = index.find_by_source("Study A")
        assert len(found) == 1
        assert found[0].target == "repo-x"

    def test_find_by_target(self):
        index = ReferenceIndex()
        index.add(CrossReference(source="Study A", target="repo-x", relationship="references_repo"))
        index.add(CrossReference(source="Study B", target="repo-x", relationship="references_repo"))
        found = index.find_by_target("repo-x")
        assert len(found) == 2

    def test_unique_sources(self):
        index = ReferenceIndex()
        index.add(CrossReference(source="Study A", target="repo-x", relationship="references_repo"))
        index.add(CrossReference(source="Study A", target="repo-y", relationship="references_repo"))
        index.add(CrossReference(source="Study B", target="repo-z", relationship="references_repo"))
        assert index.unique_sources == {"Study A", "Study B"}

    def test_unique_targets(self):
        index = ReferenceIndex()
        index.add(CrossReference(source="Study A", target="repo-x", relationship="references_repo"))
        index.add(CrossReference(source="Study B", target="repo-x", relationship="references_repo"))
        assert index.unique_targets == {"repo-x"}

    def test_get_reference_graph(self):
        index = ReferenceIndex()
        index.add(CrossReference(source="A", target="B", relationship="ref"))
        index.add(CrossReference(source="A", target="C", relationship="ref"))
        index.add(CrossReference(source="D", target="B", relationship="ref"))
        graph = index.get_reference_graph()
        assert "A" in graph
        assert "B" in graph["A"]
        assert "C" in graph["A"]
        assert "D" in graph
        assert "B" in graph["D"]

    def test_get_reference_graph_no_duplicate_targets(self):
        index = ReferenceIndex()
        index.add(CrossReference(source="A", target="B", relationship="ref1"))
        index.add(CrossReference(source="A", target="B", relationship="ref2"))
        graph = index.get_reference_graph()
        assert graph["A"].count("B") == 1

    def test_get_orphan_studies(self):
        index = ReferenceIndex()
        index.add(CrossReference(source="Study A", target="repo-x", relationship="ref"))
        study_a = CaseStudy(title="Study A")
        study_b = CaseStudy(title="Study B")
        orphans = index.get_orphan_studies([study_a, study_b])
        assert len(orphans) == 1
        assert orphans[0].title == "Study B"

    def test_no_orphans_when_all_referenced(self):
        index = ReferenceIndex()
        index.add(CrossReference(source="Study A", target="x", relationship="ref"))
        index.add(CrossReference(source="Study B", target="y", relationship="ref"))
        study_a = CaseStudy(title="Study A")
        study_b = CaseStudy(title="Study B")
        orphans = index.get_orphan_studies([study_a, study_b])
        assert orphans == []

    def test_empty_index_all_orphans(self):
        index = ReferenceIndex()
        study_a = CaseStudy(title="Study A")
        orphans = index.get_orphan_studies([study_a])
        assert len(orphans) == 1


class TestBuildFromStudies:
    def _make_study(self, title: str, content: str) -> CaseStudy:
        return CaseStudy(
            title=title,
            metadata={},
            sections=[CaseStudySection(heading="Body", level=1, content=content)],
        )

    def test_indexes_repo_references(self):
        study = self._make_study(
            "Test Study",
            "The `metasystem-master` repo is used here.",
        )
        index = build_from_studies([study])
        refs = index.find_by_source("Test Study")
        targets = [r.target for r in refs]
        assert "metasystem-master" in targets

    def test_indexes_organ_references(self):
        study = self._make_study(
            "Test Study",
            "ORGAN-II provides creative generation.",
        )
        index = build_from_studies([study])
        refs = index.find_by_source("Test Study")
        targets = [r.target for r in refs]
        assert "ORGAN-II" in targets

    def test_indexes_multiple_studies(self):
        study_a = self._make_study("Study A", "Uses `repo-alpha` in ORGAN-I.")
        study_b = self._make_study("Study B", "Uses `repo-beta` in ORGAN-III.")
        index = build_from_studies([study_a, study_b])
        assert index.unique_sources == {"Study A", "Study B"}
        assert len(index.references) >= 4  # 2 repo refs + 2 organ refs

    def test_empty_studies_list(self):
        index = build_from_studies([])
        assert index.references == []

    def test_study_with_no_references(self):
        study = self._make_study("Empty Study", "No references at all.")
        index = build_from_studies([study])
        assert index.find_by_source("Empty Study") == []
        orphans = index.get_orphan_studies([study])
        assert len(orphans) == 1
