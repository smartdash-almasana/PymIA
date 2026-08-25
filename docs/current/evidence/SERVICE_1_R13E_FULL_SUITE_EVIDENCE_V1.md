# Servicio 1 — R13E bounded full-suite evidence

## Command

python -m pytest -q --ignore=tests/e2e/test_real_case_playwright_llm.py

## Observed result

- Passed: 3846
- Failed: 1
- Skipped: 7
- Warnings: 4
- Duration: 996.81s (0:16:36)
- Exit code: 1

## Failure

tests/smartpyme/test_service_1_frozen_dependency_evidence_matrix_v1.py::test_matrix_references_are_recomputed_from_repo_text

The failure is a documentation-matrix self-reference mismatch: the stored
other_source_refs includes the frozen module's own path, while the test's
recomputation excludes the entry's path before bucketing references.

## Scope and stop condition

This R13E run was observation-only. No repair was attempted, no runtime or
tests were modified, and no commit, push, or deploy was performed. The
ignored Playwright file was not collected.
