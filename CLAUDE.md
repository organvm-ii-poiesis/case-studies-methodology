# CLAUDE.md — case-studies-methodology

**ORGAN II** (Art) · `organvm-ii-poiesis/case-studies-methodology`
**Status:** ACTIVE · **Branch:** `main`

## What This Repo Is

Structured case studies documenting creative methodology — process documentation, comparative analysis, and grant-ready excerpts

## Stack

**Languages:** Python
**Build:** Python (pip/setuptools)
**Testing:** pytest (likely)

## Directory Structure

```
📁 .github/
📁 data/
📁 docs/
    adr
📁 src/
    __init__.py
    __main__.py
    cross_reference.py
    export.py
    parser.py
📁 tests/
    __init__.py
    test_cross_reference.py
    test_export.py
    test_parser.py
  .gitignore
  CHANGELOG.md
  LICENSE
  README.md
  pyproject.toml
  seed.yaml
```

## Key Files

- `README.md` — Project documentation
- `pyproject.toml` — Python project config
- `seed.yaml` — ORGANVM orchestration metadata
- `src/` — Main source code
- `tests/` — Test suite

## Development

```bash
pip install -e .    # Install in development mode
pytest              # Run tests
```

## ORGANVM Context

This repository is part of the **ORGANVM** eight-organ creative-institutional system.
It belongs to **ORGAN II (Art)** under the `organvm-ii-poiesis` GitHub organization.

**Registry:** [`registry-v2.json`](https://github.com/meta-organvm/organvm-corpvs-testamentvm/blob/main/registry-v2.json)
**Corpus:** [`organvm-corpvs-testamentvm`](https://github.com/meta-organvm/organvm-corpvs-testamentvm)
