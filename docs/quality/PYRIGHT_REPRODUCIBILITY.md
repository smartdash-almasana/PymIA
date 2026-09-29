# Pyright Reproducibility — FASE 1-C

STATUS: PARTIAL / BLOCKED_TOOLING

## Version pin

`pyright==1.1.414`

Source verified on 2026-09-28:
- PyPI release 1.1.414
- release date: 2026-09-10

Manifest:
`requirements-quality.txt`

## Installation contract

The intended isolated quality-tooling installation is:

`python -m pip install -r requirements-quality.txt`

This is a quality-tool dependency only. It is NOT part of PymIA runtime dependencies and MUST NOT be moved into `[project].dependencies`.

## Current environment

FASE 1-B evidence established:

- Ruff 0.16.0: AVAILABLE
- Pyright: NOT_AVAILABLE
- architecture tests: PASS

During FASE 1-C, the alternate local MCP execution path returned an unavailable/404 error before installation could be performed. The main filesystem runner does not allow arbitrary pip installation.

Therefore:

- version pin: COMPLETE
- executable activation: BLOCKED_TOOLING
- Pyright findings baseline: NOT YET AUTHORITATIVE

No PASS is claimed for Pyright.

## Governance

Do not:
- remediate Pyright findings;
- enable strict globally;
- make Pyright blocking;
- add Pyright to runtime dependencies;
- edit product code in this phase.

Next action requires an execution channel that can install the pinned quality requirement, then rerun the Fast Quality Gate and capture the Pyright report.
