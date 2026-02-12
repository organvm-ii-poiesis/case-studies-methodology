"""CLI entry point for case-studies-methodology: python -m src."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .cross_reference import ReferenceIndex, build_from_studies
from .export import to_evidence_checklist, to_markdown_outline, to_summary
from .parser import parse_markdown


def cmd_parse(args: argparse.Namespace) -> None:
    """Parse a case study file and print its structured summary."""
    path = Path(args.file)
    if not path.exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(1)

    text = path.read_text(encoding="utf-8")
    study = parse_markdown(text)
    summary = to_summary(study)
    print(json.dumps(summary, indent=2))


def cmd_analyze(args: argparse.Namespace) -> None:
    """Parse all case studies in a directory, show cross-reference index."""
    directory = Path(args.directory)
    if not directory.is_dir():
        print(f"Error: not a directory: {directory}", file=sys.stderr)
        sys.exit(1)

    studies = []
    for md_file in sorted(directory.glob("*.md")):
        text = md_file.read_text(encoding="utf-8")
        study = parse_markdown(text)
        studies.append(study)
        print(f"Parsed: {study.title} ({study.word_count} words, {len(study.sections)} sections)")

    if not studies:
        print("No markdown files found.", file=sys.stderr)
        sys.exit(1)

    print(f"\n--- Cross-Reference Index ({len(studies)} studies) ---")
    index = build_from_studies(studies)
    for ref in index.references:
        print(f"  {ref.source} -> {ref.target} [{ref.relationship}]")

    orphans = index.get_orphan_studies(studies)
    if orphans:
        print(f"\nOrphan studies (no cross-references): {len(orphans)}")
        for orphan in orphans:
            print(f"  - {orphan.title}")
    else:
        print("\nNo orphan studies — all studies have cross-references.")

    graph = index.get_reference_graph()
    print(f"\nReference graph: {len(graph)} source nodes")


def cmd_checklist(args: argparse.Namespace) -> None:
    """Generate an evidence checklist for a case study."""
    path = Path(args.file)
    if not path.exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(1)

    text = path.read_text(encoding="utf-8")
    study = parse_markdown(text)
    checklist = to_evidence_checklist(study)

    print(f"Evidence Checklist: {study.title}\n")
    for item in checklist:
        status = "PASS" if item["present"] else "MISSING"
        words = f"({item['word_count']} words)" if item["present"] else ""
        print(f"  [{status}] {item['section']} {words}")


def cmd_export(args: argparse.Namespace) -> None:
    """Export a case study in the specified format."""
    path = Path(args.file)
    if not path.exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(1)

    text = path.read_text(encoding="utf-8")
    study = parse_markdown(text)

    if args.format == "json":
        summary = to_summary(study)
        print(json.dumps(summary, indent=2))
    elif args.format == "outline":
        outline = to_markdown_outline(study)
        print(outline)
    else:
        print(f"Error: unknown format: {args.format}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="case-studies",
        description="Case study analysis framework for the ORGAN system",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # parse command
    parse_parser = subparsers.add_parser("parse", help="Parse a case study file")
    parse_parser.add_argument("file", help="Path to markdown case study file")

    # analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze all case studies in a directory")
    analyze_parser.add_argument("directory", help="Path to directory of case study files")

    # checklist command
    checklist_parser = subparsers.add_parser("checklist", help="Generate evidence checklist")
    checklist_parser.add_argument("file", help="Path to markdown case study file")

    # export command
    export_parser = subparsers.add_parser("export", help="Export a case study")
    export_parser.add_argument("file", help="Path to markdown case study file")
    export_parser.add_argument(
        "--format",
        choices=["json", "outline"],
        default="json",
        help="Output format (default: json)",
    )

    args = parser.parse_args()

    commands = {
        "parse": cmd_parse,
        "analyze": cmd_analyze,
        "checklist": cmd_checklist,
        "export": cmd_export,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
