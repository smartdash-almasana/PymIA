---
name: pymia-method-evidence
description: Govern PymIA evidence, PASS claims, GAP/BLOCKED/NEEDS_EVIDENCE states, test attribution, agent reports, and checkpoint closure.
---

# PymIA Method Evidence

## Purpose

Operationalize the evidence and checkpoint rules in `AGENTS.md`.

This skill answers:

```text
WHAT CAN BE CLAIMED AS PROVEN, BY WHOM, AND WHAT STATE CLOSES THIS CYCLE?
```

## Evidence classes

Keep these separate:

```text
CERTIFIED
HYPOTHESIS
GAP
BLOCKED
NEEDS_EVIDENCE
```

Definitions:

- `CERTIFIED`: directly supported by observed or explicitly attributed evidence.
- `HYPOTHESIS`: plausible explanation not yet proven.
- `GAP`: missing capability, evidence, contract, integration, or required behavior.
- `BLOCKED`: progress cannot safely continue because a required condition fails.
- `NEEDS_EVIDENCE`: the path may be valid, but required evidence is absent or insufficient.

Never convert one state into another for narrative convenience.

## PASS rules

Do not declare PASS without evidence.

Acceptable evidence:

```text
local command output observed by the acting agent
explicitly reported external/local command output, attributed to its actor
CI/GitHub evidence when available
documentary gate evidence for documentation-only changes
physical artifact evidence when the gate requires it
```

Forbidden claims:

```text
"I ran tests" when another actor ran them
"full suite green" from a partial suite
"production ready" from unit tests only
"fixed" when only a hypothesis was formed
"no regressions" without an appropriate comparison or regression check
```

## Test attribution

Every validation statement must identify the evidence source when ambiguity exists.

Examples:

```text
MCP-local observed: 17 passed / 0 failed
OpenCode reported: 3538 passed / 0 failed / 6 skipped
CI reported: PASS
User-reported external run: <result>
```

Do not erase actor boundaries.

## Baseline discipline

Distinguish:

```text
DECLARED_BASELINE
OBSERVED_BASELINE
CURRENT_RESULT
```

If declared and observed baselines differ, report the mismatch before drawing regression conclusions.

Never infer `NEW_REGRESSIONS: NONE` solely from different aggregate pass counts. Prefer failed-test identity comparison or an explicitly relevant regression pack.

## Proportional evidence

Use the smallest verification that actually proves the current work unit:

```text
document-only change → documentary/focal contract check
small code change → focal test
integration change → focal + relevant regression
physical fixture change → regenerate + physical gate
production deployment → real smoke
major certification → full suite once
```

More tests are not automatically more evidence for the question being decided.

## Cycle closure

Each work cycle must close as:

```text
ONE_TASK
→ ONE_OR_PROPORTIONAL_VERIFICATION
→ RESULT
→ DECISION
→ CHECKPOINT
```

The checkpoint records the achieved state; it does not authorize unrelated next work.

## Checkpoint minimum

Record:

```text
TASK
REPO_HEAD
WORKTREE_STATE
SOURCES_READ
FILES_CHANGED
VALIDATION_EXECUTED
VALIDATION_ACTOR
RESULT
KNOWN_GAPS
BLOCKERS
COMMIT_STATUS
PUSH_STATUS
NEXT_DECISION
```

For documentation-only work, a documentary checkpoint is sufficient when no runtime behavior changed.

## Status decision rules

### PASS

Use only when the stated acceptance condition is supported by evidence.

### GAP

Use when a required capability or integration is absent but the current environment/method can continue to define or close it.

### NEEDS_EVIDENCE

Use when the required behavior may exist but evidence required by the contract is missing.

### BLOCKED

Use when the current task cannot safely proceed without resolving a material precondition.

Do not call healthy fail-closed product behavior a project blocker when the product contract expects that block.

## Regression language

Use precise language:

```text
FOCAL: PASS
RELEVANT_REGRESSION: PASS
FULL_SUITE: NOT_RUN
NEW_REGRESSIONS_IN_CHECKED_SCOPE: NONE
```

Do not write `NEW_REGRESSIONS: NONE` globally when only a narrow scope was checked.

## Evidence vs authority

```text
Execution != Evidence != Learning != Architecture
```

Evidence proves or records what happened. It does not create architecture, capability authority, runtime permission, semantic truth, or learning memory by itself.

## Agent report format

Use this compact structure unless a task defines a stricter report:

```text
VERDICT: PASS | GAP | NEEDS_EVIDENCE | BLOCKED

REPO_STATE:
HEAD:
WORKTREE:

SOURCES_READ:

CERTIFIED:
HYPOTHESES:
GAPS:
BLOCKERS:

FILES_CHANGED:

VALIDATION:
- command/gate:
- actor:
- result:

REGRESSION_SCOPE:

COMMIT:
PUSH:

CHECKPOINT:
NEXT_DECISION:
```

## Audit before closing

Before declaring the cycle closed, ask:

```text
Did the evidence actually test the acceptance condition?
Am I attributing commands to the correct actor?
Did I distinguish observed from declared baseline?
Did any unrelated file enter the work unit?
Did I turn a GAP into PASS without evidence?
Did I run a full suite without a systemic reason?
Is the next decision narrower than or equal to the authorized roadmap?
```

If any answer is unsafe or unclear, do not declare PASS.

## Final rule

Evidence must be sufficient, attributed, scoped, and proportional. A confident report is not evidence.
