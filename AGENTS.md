# PymIA / SmartPyme — Agent Startup Contract

## Status

Mandatory repository-level startup contract for AI-assisted work.

This file is the first document an assistant, agent, coding model, auditor, or human operator must read before proposing or changing work in this repository.

## Purpose

Prevent methodological drift.

PymIA / SmartPyme must not advance from loose prompts, model enthusiasm, roadmap momentum, or isolated implementation ideas.

All work must preserve the written architecture, methodology, ADR trail, contracts, tests, evidence, and checkpoints.

## Mandatory startup sequence

Before operating, the agent must:

1. Read this `AGENTS.md`.
2. Check repository state:
   - current branch;
   - `git status --short`;
   - recent commits when relevant.
3. Read the latest relevant checkpoint.
4. Read applicable methodology / ADR / source architecture documents.
5. Identify the layer being touched:
   - Architecture;
   - ADR;
   - CapabilitySpec;
   - ModuleContract;
   - TaskSpec;
   - tests;
   - code;
   - evidence;
   - checkpoint;
   - learning candidate.
6. Separate explicitly:
   - certified facts;
   - hypotheses;
   - gaps;
   - next methodological step.
7. State stop conditions before implementation.

If the architectural source is missing, stop.

If the technical contract is missing, do not implement code yet.

If evidence is missing, do not declare PASS.

## Development chain

The only valid development chain is:

```text
Architectural DNA / philosophy / methodology
→ ADR
→ CapabilitySpec
→ ModuleContract
→ TaskSpec
→ acceptance test
→ code
→ evidence
→ checkpoint
→ Learning candidate, only if applicable
```

A roadmap item does not become code by itself.

A conversation does not become policy by itself.

Evidence does not become LearningMemory by itself.

A document does not enter the system as a real capability until it has:

```text
contract + test + evidence
```

## Meaning of “advance”

When the user says “advance”, it means:

```text
advance inside the method
```

It never means:

```text
skip architecture;
skip ADR;
skip contracts;
skip tests;
skip evidence;
open a feature by intuition;
touch production code without authorization.
```

## PASS rules

Do not declare PASS unless there is evidence.

Acceptable evidence includes:

- local command output observed directly by the acting agent;
- external/local command output explicitly reported by the user or another tool, identified as such;
- GitHub/CI evidence, if available;
- documentary gate evidence for documentation-only changes.

If tests were run by Gemini, Codex, local PowerShell, CI, or another actor, say so.

Do not write “I ran tests” unless this agent actually ran them.

## Product language rule

Do not call something “product” if it is still one of:

- service assisted by humans;
- protocol;
- pilot;
- internal capability;
- documentary checkpoint;
- controlled demo;
- technical slice;
- hypothesis.

Prefer accurate language:

- service assisted;
- operational protocol;
- capability under test;
- pilot flow;
- internal module;
- documented checkpoint.

## Role of the PyME owner

The PyME owner is not only an uploader of Excel files.

The owner provides two kinds of input:

1. Data:
   - files;
   - columns;
   - sales;
   - costs;
   - extracts;
   - invoices;
   - stock;
   - operational records.
2. Operational meaning:
   - what worries them;
   - what period matters;
   - what a column means;
   - what real process sits behind a file;
   - what data is missing but exists elsewhere;
   - what decision needs support.

If the system lacks evidence or meaning, the correct state is not silence.

The correct state is a visible GAP, BLOCKED, NEEDS_EVIDENCE, or methodological stop, depending on the implemented contract.

## Layer separation

The following layers must remain separate:

```text
Execution ≠ Evidence ≠ Learning ≠ Architecture
```

Definitions:

- Execution: what was done.
- Evidence: what proves or records what happened.
- Learning: governed candidate or approved learning derived from evidence.
- Architecture: stable identity, constraints, ADRs, contracts, and methodology.

Do not convert one layer into another automatically.

## Stop conditions

Stop before implementation if:

- the architectural source is missing;
- the applicable ADR is missing and the change implies an architectural decision;
- there is no CapabilitySpec for a new capability;
- there is no ModuleContract for a new or changed module boundary;
- there is no TaskSpec for the implementation slice;
- acceptance tests are not defined;
- the user has not authorized productive code changes;
- the work would mix unrelated layers;
- the repo is dirty in unrelated files;
- the branch or remote state is unclear;
- the proposed change would call a protocol, pilot, or internal capability a product.

## Git protocol

Before writing:

```text
git status --short
git branch --show-current
git log -1 --oneline
```

Before commit:

```text
git status --short
git diff -- <planned files>
```

Commit discipline:

- focal commit;
- no unrelated files;
- no productive code without explicit authorization;
- include evidence in the response;
- push only when repo is clean enough, branch is correct, and there is no known divergence.

Recommended commit message for this startup contract family:

```text
docs(pymia): add agent startup and development method
```

## Current methodological warning

`NEEDS_EVIDENCE` can detect missing evidence in existing flows, but guided recovery of evidence or operational meaning is not automatically implemented by this contract.

Do not implement Guided Evidence Recovery unless a future cycle creates the appropriate ADR, CapabilitySpec, ModuleContract, TaskSpec, tests, and evidence requirements.

## Default answer format for agent work

When reporting back, use:

1. Repo state.
2. Sources read.
3. Certified / hypothesis / gap / next methodological step.
4. Files changed.
5. Validation evidence.
6. Commit / push status.
7. Next step.
