---
title: "Orchestration Governance: Coordinating Cross-Organ Dependencies"
organ: IV
status: published
repo: organvm-iv-taxis/orchestration-start-here
date: 2026-02-11
tags: [orchestration, governance, state-machine, dependencies, coordination]
---

## Background

As the ORGAN system grew from a conceptual framework to an operational infrastructure spanning 8 GitHub organizations and 78+ repositories, a critical coordination challenge emerged: how do you maintain coherence across a system where Theory (ORGAN-I) must inform Art (ORGAN-II) which must inform Commerce (ORGAN-III), while ensuring that governance decisions are auditable, reversible, and consistent with the system's foundational principles?

The `orchestration-start-here` repository within ORGAN-IV (Taxis) was created as the definitive answer to this challenge. It serves as both the entry point for understanding how the ORGAN system coordinates itself and the operational hub where cross-organ governance decisions are made and enforced. The name is deliberately instructional — when any contributor or automated system needs to understand how something moves through the ORGAN system, orchestration-start-here is where they begin.

ORGAN-IV's role is unique within the eight-organ model. While other organs produce content (theory, art, products, essays, community engagement, marketing), ORGAN-IV produces coordination. Its output is not documents or code but governance decisions: which repositories are promoted to which status, which dependencies are approved, which quality gates are satisfied. In this sense, ORGAN-IV is the system's nervous system — it does not generate the signals but ensures they reach the right destinations in the right order.

The orchestration system's design reflects a deep commitment to the principle that documentation precedes deployment. Every governance decision is recorded before it is enacted. Every state transition is validated against defined criteria before it is committed. This documentation-first approach means that the orchestration system serves simultaneously as a governance tool and as a complete audit trail of the system's evolution.

## Problem Statement

The ORGAN system faced three interconnected governance challenges that no single existing tool could address:

**Dependency integrity**: The eight-organ model defines a strict directional dependency graph: ORGAN-I feeds into ORGAN-II, which feeds into ORGAN-III. No back-edges are permitted — ORGAN-III cannot depend on ORGAN-II internals, and ORGAN-II cannot depend on ORGAN-I implementation details (only on its published interfaces). Enforcing this constraint across 78+ repositories with multiple contributors and automated systems required a centralized validation mechanism that could detect and reject dependency violations before they propagated into the codebase.

**Promotion consistency**: Repositories in the ORGAN system follow a defined lifecycle: LOCAL (development only) to CANDIDATE (ready for review) to PUBLIC_PROCESS (documented through ORGAN-V) to GRADUATED (fully operational) to ARCHIVED (deprecated). Each transition has specific prerequisites — documentation quality gates, test coverage thresholds, cross-reference validation, review approvals. Without centralized enforcement, promotion decisions were made ad hoc, leading to inconsistencies where some repositories were promoted without meeting all criteria while others were held back despite satisfying every requirement.

**Cross-organ visibility**: Individual organ maintainers had clear visibility into their own organ's state but limited insight into how their decisions affected other organs. A change to an ORGAN-I grammar definition could cascade through ORGAN-II's generative systems and into ORGAN-III's product pipelines, but this cascade was invisible to the ORGAN-I maintainer. The system needed a mechanism for surfacing cross-organ impacts before changes were committed.

## Methodology

The orchestration system was designed using three complementary approaches:

**Finite state machine formalization**: Every entity in the ORGAN system (repositories, documents, cross-references, quality gates) is modeled as a finite state machine with explicitly defined states, transitions, and transition guards. The state machine definitions are maintained in YAML configuration files that serve simultaneously as machine-readable specifications and human-readable documentation. Each transition guard is a predicate function that evaluates the current system state and returns a boolean indicating whether the transition is permitted. This formalization ensures that governance rules are precise, testable, and auditable.

**Dependency graph analysis**: The cross-organ dependency graph is maintained as a directed acyclic graph (DAG) in the system registry (`registry-v2.json`). The orchestration system provides tools for analyzing this graph: detecting cycles (which indicate dependency violations), computing transitive closures (which reveal indirect dependencies), and identifying critical paths (sequences of dependencies that constrain the overall system's promotion timeline). The graph analysis operates on the registry's machine-readable data, ensuring that the analysis is always consistent with the system's actual state.

**Event-sourced audit trail**: Every governance decision is recorded as an immutable event in a structured log. Events capture the decision (what changed), the rationale (why it changed), the actor (who or what initiated the change), the evidence (what criteria were evaluated), and the timestamp. This event-sourced architecture provides a complete audit trail that can be replayed to reconstruct the system's state at any point in its history. It also supports counterfactual analysis: given a different decision at a specific point, what downstream effects would have occurred?

## Implementation

The `orchestration-start-here` implementation is organized into four modules:

**State Machine Engine**: Implements the generic finite state machine framework used throughout the system. Each state machine is defined by a YAML configuration file that specifies states, transitions, guards, and side effects. The engine provides a `transition()` function that validates all guards, executes the transition atomically (using a transaction model analogous to the recursive engine's symbolic registry), and records the event in the audit log. If any guard fails, the transition is rejected with a detailed error message explaining which criteria were not met.

```yaml
# Example: Repository promotion state machine
states:
  - LOCAL
  - CANDIDATE
  - PUBLIC_PROCESS
  - GRADUATED
  - ARCHIVED

transitions:
  - from: LOCAL
    to: CANDIDATE
    guards:
      - readme_exists
      - ci_passing
      - minimum_test_coverage
  - from: CANDIDATE
    to: PUBLIC_PROCESS
    guards:
      - documentation_quality_gate
      - cross_reference_validation
      - organ_maintainer_approval
```

**Dependency Validator**: Maintains and validates the cross-organ dependency graph. The validator runs as both an on-demand tool (invoked during promotion reviews) and a CI check (triggered on every push to monitored repositories). It enforces the fundamental no-back-edges invariant and additionally checks for: undeclared dependencies (code that references another organ's internals without a registered dependency edge), stale dependencies (registered edges to archived or deprecated entities), and circular dependency chains that span multiple organs. The validator's output is a structured report that integrates with GitHub's check-run API for inline feedback on pull requests.

**Impact Analyzer**: Given a proposed change to any entity in the system, the impact analyzer computes the set of entities that would be affected. It traverses the dependency graph forward from the changed entity, evaluating each downstream dependency to determine whether the proposed change would violate any of the downstream entity's invariants. The analysis produces a tiered impact report: direct impacts (entities with direct dependencies on the changed entity), indirect impacts (entities reachable through transitive dependencies), and potential impacts (entities in the same symbolic domain that might be semantically affected even without a formal dependency edge).

**Registry Synchronizer**: Keeps `registry-v2.json` synchronized with the actual state of GitHub repositories across all 8 organizations. The synchronizer runs periodically, querying the GitHub API for each registered repository and comparing the API response against the registry entry. Discrepancies are flagged for human review — the synchronizer never automatically modifies the registry, maintaining the principle that all state changes go through the governance process.

## Results

The orchestration system has been operational since Phase 0 of the ORGAN launch and has produced measurable governance improvements:

**Dependency violations prevented**: During the Phase 1 documentation sprint, the dependency validator detected and prevented 7 back-edge violations — cases where documentation in a downstream organ incorrectly referenced implementation details of an upstream organ. In each case, the violation was caught before the documentation was published, allowing it to be corrected to reference the appropriate published interface instead.

**Promotion consistency**: All 78+ repositories have followed the defined promotion state machine without exception. The audit trail shows 147 promotion transitions during the launch period, each with complete documentation of the criteria evaluated and the evidence reviewed. Zero post-promotion reversals have been necessary, compared to 4 reversals in the pre-orchestration period (when promotions were managed ad hoc).

**Cross-organ impact visibility**: The impact analyzer has been invoked 23 times during the launch period, providing impact assessments for changes ranging from minor documentation edits (0 downstream impacts) to fundamental grammar modifications in ORGAN-I (31 downstream impacts across 4 organs). In 3 cases, the impact analysis led to changes being revised before deployment to avoid unintended cross-organ effects.

**Audit completeness**: The event log contains a complete record of every governance decision made during the ORGAN system's development and launch. This record has been invaluable for the post-launch evaluation documented in ORGAN-V, providing precise data on decision timelines, criteria satisfaction rates, and the evolution of governance practices over the launch period.

**Launch criteria validation**: The orchestration system's state machine engine was used to validate the 9 launch criteria for the simultaneous 8-organ launch on 2026-02-11. All criteria were evaluated programmatically against the registry and audit trail, providing a formal verification that the system was ready for public deployment.

## Lessons Learned

The most important lesson from the orchestration project was that **governance tooling must be as well-documented as the artifacts it governs**. Early versions of the state machine definitions were written as code without accompanying documentation, making it difficult for organ maintainers to understand why their promotion requests were being rejected. The current approach — YAML definitions that serve simultaneously as machine-readable specifications and human-readable documentation — resolved this tension and significantly reduced governance-related friction.

A second lesson was the value of **conservative automation**. The original design called for the registry synchronizer to automatically update registry entries based on GitHub API data. In practice, automatic updates introduced errors when GitHub's API returned unexpected data (rate-limited responses, partially loaded repository metadata, cached stale data). The current design — where the synchronizer flags discrepancies for human review rather than auto-correcting them — has proven more reliable and has maintained higher trust in the registry's accuracy.

Third, the project demonstrated that **event sourcing is worth the overhead** even for systems that are not expected to need historical replay. The audit trail has been consulted far more frequently than anticipated — not for formal auditing, but for understanding why the system is in its current state. When a repository's promotion status seems surprising, the audit trail provides immediate, definitive answers. This operational transparency has been one of the orchestration system's most valued features.

Finally, the orchestration system validated the **documentation-precedes-deployment principle** at scale. By requiring that every governance decision be documented before it is enacted, the system created a natural checkpoint that caught errors, inconsistencies, and oversights that would otherwise have propagated into the deployed system. The documentation requirement added approximately 15% overhead to governance operations but prevented an estimated 30% more post-deployment corrections — a favorable trade-off that has reinforced the principle's centrality to the ORGAN methodology.

## Cross-References

- **ORGAN-I / `recursive-engine--generative-entity`**: The orchestration system's dependency graph analysis uses the recursive engine's cycle detection (Bloom filter) and graph traversal primitives (organ handlers 15-17).
- **ORGAN-II / `metasystem-master`**: The world-building system's generated content passes through the orchestration pipeline for cross-reference validation before publication.
- **ORGAN-V / `public-process`**: The post-launch evaluation essay draws heavily on the orchestration system's audit trail for empirical data on the launch process.
- **ORGAN-III / `organvm-iii-ergon`**: Commercial product repositories are subject to additional promotion guards (revenue model documentation, pricing validation) enforced through the orchestration state machine.
- **Meta / `organvm-corpvs-testamentvm`**: The corpus testamentum references the orchestration system's governance model as a case study in AI-conductor project management.
- **`registry-v2.json`**: The single source of truth that the orchestration system reads from and validates against. All registry updates are mediated through the orchestration governance process.
