---
name: pymia-session-contract
description: Verify PymIA repo state, current authority, checkpoint, scope, stop conditions, and proportional verification before any work begins.
---

# PymIA Session Contract

## Purpose

Prevent session drift before work starts.

This skill operationalizes the mandatory startup sequence in `AGENTS.md`.

It answers:

```text
AM I OPERATING ON THE CORRECT REPO STATE, AUTHORITY, AND SCOPE?
```

## Mandatory startup

Before implementation, audit, broad testing, documentation, or Git work:

1. Read `AGENTS.md`.
2. Read `docs/current/README.md`.
3. Verify branch, HEAD, `git status --short`, and recent commit when relevant.
4. Identify the current authoritative document for the target area.
5. Read the latest relevant checkpoint/current-state document.
6. Classify the work layer: architecture, ADR, CapabilitySpec, ModuleContract, TaskSpec, tests, code, evidence, checkpoint, or Git-only.
7. Separate certified facts, hypotheses, gaps, and next action.
8. State stop conditions before implementation.

## Repo-state contract

Record explicitly:

```text
REPO_PATH
BRANCH
HEAD
WORKTREE
CURRENT_AUTHORITY
CURRENT_CHECKPOINT
REQUESTED_SCOPE
UNRELATED_DIRTY_FILES
```

Interpretation:

```text
WORKTREE=CLEAN
→ safe baseline, subject to authority checks

WORKTREE=DIRTY_RELATED_ONLY
→ allowed only for the current authorized work unit

WORKTREE=DIRTY_UNRELATED
→ do not clean, revert, absorb, stash, or reformat unrelated files
→ restrict scope or stop if isolation is impossible
```

## Authority precedence

```text
physical code/tests/evidence
→ AGENTS.md + architecture guardrails
→ docs/current/README.md
→ current authority named there
→ explicitly cited evidence
→ historical documents
```

Historical documents do not override current authority merely because they exist.

## Stop conditions

Stop before implementation when any of these is true:

```text
repo path unclear
branch unclear
HEAD mismatch unexplained
unrelated dirty work cannot be isolated
current authority cannot be identified
architectural source missing for architectural change
required ADR missing for new architectural decision
required contract/spec missing for new capability or boundary
acceptance test undefined for implementation work
productive-code authorization absent
requested work mixes unrelated work units
requested change creates a second productive authority
```

## No silent reconciliation

Never silently resolve differences between user-declared HEAD, local HEAD, origin/main, historical checkpoint, and current authority.

Report the observed values, classify the mismatch, and do not claim alignment until verified.

## Scope lock

Before work, define:

```text
TASK: <single task>
ALLOWED_FILES_OR_AREA: <bounded scope>
VERIFICATION: <proportional check>
STOP_IF: <material blocker>
```

Do not broaden the task because adjacent issues are visible.

## QA planning

Choose verification before implementation:

```text
document-only change → documentary/focal contract check
small code change → focal test
integration change → focal + one relevant regression
production deployment → real smoke
major production certification → full suite once
```

Do not default to the full suite for every cycle.

## Expected output

```text
SESSION_CONTRACT: PASS | BLOCKED

REPO_PATH:
BRANCH:
HEAD:
WORKTREE:
CURRENT_AUTHORITY:
CURRENT_CHECKPOINT:
REQUESTED_SCOPE:

CERTIFIED:
HYPOTHESES:
GAPS:

STOP_CONDITIONS:
VERIFICATION_PLAN:
NEXT_ACTION:
```

## PASS rule

`SESSION_CONTRACT: PASS` means only that starting state, authority, scope, and verification plan are clear enough to begin.

It does not mean the implementation or product gate passed.

## Final rule

Never start by coding. Start by proving where you are, what governs the work, what the bounded task is, and what evidence will close it.
