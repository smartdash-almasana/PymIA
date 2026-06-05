# PymIA / SmartPyme — Start Here for Agents

## Status

Brief index for new chats, agents, auditors, and coding assistants.

This file does not replace `AGENTS.md` or `PYMIA_DEVELOPMENT_METHOD.md`.

It points to the mandatory startup sequence.

## Read order

Before proposing or changing work, read:

1. `AGENTS.md`
2. `docs/pymia/PYMIA_DEVELOPMENT_METHOD.md`
3. Latest relevant checkpoint, currently post-M31 unless a newer checkpoint exists.
4. Applicable roadmap, ADR, CapabilitySpec, ModuleContract, or source document.

## Current post-M31 position

M27–M30 certify internal capabilities around:

- Excel controlled evidence;
- PyME owner semantics;
- explainable findings;
- minimum deliverable report;
- case continuity.

M31 certifies a repeatable assisted-service protocol.

M31 does not certify:

- product final;
- autonomous platform;
- commercial validation;
- arbitrary Excel support;
- guided evidence recovery;
- ERP integration;
- end-to-end autonomy.

## Method in one line

```text
Architectural DNA / method
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

## Mandatory distinctions

Always separate:

- certified fact;
- hypothesis;
- gap;
- next methodological step.

Always keep separate:

```text
Execution ≠ Evidence ≠ Learning ≠ Architecture
```

## Meaning of “advance”

When the user says “advance”, interpret it as:

```text
advance inside the method
```

Not as permission to improvise, skip contracts, skip tests, or open a feature by roadmap inertia.

## GitHub-only note

If operating through GitHub only:

- do not claim local `git status`;
- do not claim local tests;
- use remote files, commits, and diffs as evidence;
- report commit SHAs;
- state clearly when local sync remains the human operator’s responsibility.

## Current known gap

`NEEDS_EVIDENCE` may detect missing evidence where already implemented and tested.

Guided Evidence Recovery is not yet implemented as a formal capability.

Do not implement it until a future cycle creates the corresponding ADR, CapabilitySpec, ModuleContract, TaskSpec, tests, evidence, and checkpoint.

## First response template

Use this structure when starting repository work:

1. Access mode.
2. Sources read.
3. Certified / hypothesis / gap / next step.
4. Planned files.
5. Stop conditions.
6. Validation plan.

## Prohibited shortcuts

Do not:

- call the assisted protocol a product;
- convert roadmap into code directly;
- convert conversation into policy directly;
- convert evidence into LearningMemory automatically;
- touch productive code without explicit authorization;
- declare PASS without evidence;
- attribute tests to yourself when run by another actor.
