# PymIA / SmartPyme — Development Method

## Status

Mandatory development method for PymIA / SmartPyme.

This document defines how work moves from architecture to implementation without methodological drift.

It does not open a new feature milestone.
It does not implement Guided Evidence Recovery.
It does not declare product readiness.

## Problem this method solves

PymIA / SmartPyme loses coherence when work starts from:

- loose prompts;
- roadmap momentum;
- isolated implementation ideas;
- model improvisation;
- premature product language;
- undocumented assumptions;
- code written before contracts.

The repository must preserve architectural identity across chats, tools, agents, commits, and assisted development cycles.

## Canonical hierarchy

Development must follow this hierarchy:

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

No lower layer may silently replace an upper layer.

A roadmap is not a TaskSpec.
A prompt is not an ADR.
A conversation is not policy.
A passing script is not architectural evidence by itself.
A document is not a capability until it has contract, test, and evidence.

## Layer definitions

### Architectural DNA / philosophy / methodology

Defines identity, principles, non-negotiable constraints, language, and direction.

Examples:

- SmartPyme receives real PyME chaos;
- evidence before diagnosis;
- service assisted before product;
- owner provides data and operational meaning;
- Execution, Evidence, Learning, and Architecture stay separate.

### ADR

An Architectural Decision Record freezes a relevant architectural choice.

Use an ADR when a change affects:

- module boundaries;
- persistence;
- state model;
- evidence model;
- learning model;
- external integrations;
- runtime assumptions;
- product/service semantics;
- irreversible design direction.

An ADR must describe:

- context;
- decision;
- alternatives considered;
- consequences;
- constraints introduced;
- migration or rollback implications, if any.

### CapabilitySpec

Defines a system capability.

A CapabilitySpec must state:

- what the system can do;
- under what inputs;
- with what required evidence;
- with what outputs;
- with what limitations;
- with what failure states;
- what is explicitly outside scope.

A capability is not real until it has tests and evidence.

### ModuleContract

Defines a module boundary.

A ModuleContract must state:

- responsibilities;
- inputs;
- outputs;
- errors;
- side effects;
- persistence behavior;
- determinism expectations;
- dependency boundaries;
- forbidden responsibilities.

Do not create or change productive module boundaries without a ModuleContract.

### TaskSpec

Defines one implementation slice.

A TaskSpec must include:

- objective;
- allowed files;
- read-only files;
- forbidden files;
- expected tests;
- PASS / PARTIAL / BLOCKED criteria;
- evidence to return;
- explicit non-goals.

A TaskSpec is local. It must derive from the upper layers.

### Acceptance test

The test proves the contract.

For code changes, tests must exercise behavior.
For documentation-only changes, tests may be documentary/static gates if appropriate.

The test must prevent the specific drift the slice is designed to avoid.

### Code

Code implements the tested contract.

Do not write productive code before the contract and acceptance test are clear.

### Evidence

Evidence records what happened.

Evidence may include:

- command output;
- test output;
- CI result;
- diff;
- generated artifact;
- checkpoint;
- external/local report clearly attributed to its actor.

Do not claim direct execution unless the acting agent executed it directly.

### Checkpoint

A checkpoint records the closure of a milestone or slice.

It must state:

- status;
- scope;
- files changed;
- evidence;
- what is certified;
- what is not certified;
- risks or limitations;
- next methodological step.

### Learning candidate

A Learning candidate is optional.

It may be created only when repeated evidence suggests a reusable pattern, anti-pattern, policy delta, or TaskSpec improvement.

Nothing becomes LearningMemory automatically.

Correct flow:

```text
Evidence
→ evaluation
→ candidate
→ review
→ approval or rejection
→ LearningMemory, only if approved
```

## Certified / hypothesis / gap / next step

Every non-trivial agent response must separate:

### Certified

Facts backed by repository files, commits, tests, CI, or explicitly reported evidence.

### Hypothesis

Reasonable but unproven interpretation.

### Gap

Missing contract, missing evidence, missing implementation, missing test, or missing source.

### Next methodological step

The next valid action inside the hierarchy.

This prevents converting uncertainty into architecture.

## PASS rules

A slice can be reported as PASS only when evidence exists.

### Valid PASS examples

- `pytest` output observed directly by the acting agent.
- CI green result from GitHub.
- User-reported local output, explicitly attributed as user/local evidence.
- Documentary/static gate result for documentation-only changes.
- Commit diff showing the expected file-only change, when the task is purely documentary.

### Invalid PASS examples

- “Looks good.”
- “Should pass.”
- “I assume tests pass.”
- “The code is simple.”
- “The document is probably correct.”
- “Another model would run it.”

### Attribution rule

If Gemini, Codex, local PowerShell, CI, or a human ran the tests, name that actor.

Do not say “I ran tests” unless this assistant/tool actually ran them.

## Product language rule

Use precise stage language.

### Allowed when appropriate

- service assisted;
- protocol;
- pilot;
- internal capability;
- technical slice;
- checkpoint;
- controlled demo;
- capability under test;
- operational laboratory.

### Forbidden unless certified

- product final;
- autonomous platform;
- ERP replacement;
- complete operating system;
- commercial product validated;
- AI that administers the company;
- end-to-end autonomy.

M31 certifies a repeatable assisted-service protocol. It does not certify product readiness.

## Role of the PyME owner

SmartPyme is designed for real PyME disorder.

The PyME may arrive with:

- Excel files;
- PDFs;
- invoices;
- bank extracts;
- WhatsApp text;
- ambiguous phrases;
- urgent economic pain;
- incomplete data;
- process knowledge held by the owner.

The owner contributes two categories of input.

### Data

- files;
- columns;
- sales;
- costs;
- extracts;
- invoices;
- stock;
- price lists;
- operational records.

### Operational meaning

- what worries them;
- what period matters;
- what a column means;
- which process produced a file;
- what data is missing but exists elsewhere;
- what decision they need to make;
- what exception matters in their business.

The owner is not merely an uploader.

If evidence or meaning is missing, the system must not invent a diagnosis.

The correct outcome is a visible gap, blocked state, or request for evidence, depending on the implemented contract.

## Evidence and meaning gaps

Existing flows may detect missing evidence through `NEEDS_EVIDENCE` or equivalent states.

That does not mean guided evidence recovery is fully implemented.

Current methodological rule:

```text
Detecting missing evidence is certified only where tests and checkpoints prove it.
Guided recovery of evidence or owner meaning is a future capability unless separately specified, contracted, tested, and evidenced.
```

Do not implement Guided Evidence Recovery in a method-documentation cycle.

## Separation of layers

The following separation is mandatory:

```text
Execution ≠ Evidence ≠ Learning ≠ Architecture
```

### Execution

What the system or agent does.

### Evidence

What proves or records what happened.

### Learning

Governed interpretation of evidence into reusable patterns.

### Architecture

Stable identity, constraints, ADRs, contracts, and methodology.

Do not promote execution logs into architecture.
Do not promote evidence into LearningMemory automatically.
Do not promote chat conclusions into policy automatically.
Do not use roadmap text as implementation contract.

## Stop conditions

Stop before writing productive code if any of the following apply:

- no architectural source;
- no ADR for architectural change;
- no CapabilitySpec for new capability;
- no ModuleContract for new boundary;
- no TaskSpec for implementation;
- no acceptance test defined;
- no explicit user authorization to touch productive code;
- unclear branch or repository state;
- unrelated dirty files in the working tree, when local work is available;
- the slice mixes documentation, runtime, UI, persistence, and integrations without contract;
- the change would imply product readiness without evidence;
- evidence is missing but the system would need to diagnose anyway.

For GitHub-only operation, local dirty-state checks cannot be certified. The agent must say so.

## How to move from document to code

A concept in documentation may move toward implementation only through this sequence:

1. Identify source document and exact concept.
2. Classify the concept:
   - principle;
   - policy;
   - capability;
   - module boundary;
   - workflow;
   - testable behavior;
   - open question.
3. Determine whether an ADR is required.
4. Write or locate CapabilitySpec.
5. Write or locate ModuleContract.
6. Write TaskSpec.
7. Write acceptance test first, or at minimum define it before code.
8. Implement the smallest slice.
9. Run or request validation.
10. Record evidence.
11. Write checkpoint.
12. Only then consider a Learning candidate.

## GitHub-only operating mode

When the agent has GitHub access but no local repository access:

- do not claim local status;
- do not claim local tests;
- use remote files, commits, and diffs as evidence;
- create focused commits when using GitHub API;
- report commit SHAs;
- state that local sync is required separately;
- do not rely on localhost or local filesystem paths.

Recommended local sync command for the human operator:

```powershell
git pull origin main
```

Only the human/local operator can certify local working tree cleanliness in that mode.

## Documentation-only validation

For documentation-only changes, validation may consist of:

- source documents read;
- target files created or updated;
- diff reviewed;
- no productive code touched;
- commit SHA recorded;
- scope matches the requested method layer;
- no feature milestone opened.

A future cycle may add static tests for these documents if the repository requires them.

## Default response contract

For work on this repository, respond with:

1. Repository access mode.
2. Sources read.
3. Certified / hypothesis / gap / next methodological step.
4. Files created or changed.
5. Validation evidence.
6. Commit status.
7. Push / remote status.
8. Next step.

## Current guardrail for post-M31 work

M27–M30 certify internal capabilities around Excel + PyME semantics.

M31 certifies a repeatable assisted-service protocol.

The next valid move is not automatically M32 feature work.

Before any new implementation, the repository must contain and follow a startup contract and development method.

This document is part of that guardrail.
