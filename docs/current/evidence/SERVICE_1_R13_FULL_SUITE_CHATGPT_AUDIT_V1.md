# Service 1 — R13 Full Suite ChatGPT Audit V1

Date/time: 2026-08-24 21:35 ART (UTC-03:00)

## Physical audit

The R13 evidence file was read directly from the current worktree.

Observed full-suite result:

- passed: 3795
- failed: 52
- skipped: 7
- errors: 3
- warnings: 4
- duration: 1370.13s

The three errors are Playwright browser-startup failures caused by Chromium not being installed at the configured cache path. They are infrastructure errors, not observed Servicio 1 runtime assertion failures.

The 52 failed tests are distributed across multiple clusters, including architecture/forbidden terms, assisted Web/tenant persistence, cafeteria F11/generalization, semantic scope, physical XLSX/adversarial corpora, SEM-2/SEM-3/SEM-5 contracts, completion/operability gates, and selected vertical/specialized tests. The evidence file does not by itself prove whether each failure is stale-test debt or a real regression; diagnosis must precede repair.

## Verdict

R13 = FAIL

R14 is not authorized.

Next valid action: bounded read-only diagnosis of the 52 failed tests, grouped by common root cause, while treating Playwright installation as a separate infrastructure prerequisite.
