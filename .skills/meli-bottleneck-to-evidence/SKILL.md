---
name: meli-bottleneck-to-evidence
description: "Trigger: dolor MELI a patologia candidata, evidencia requerida. Convierte dolor en control deterministico y tratamiento."
license: Apache-2.0
metadata:
  author: gentleman-programming
  version: "0.1-draft"
---

# meli-bottleneck-to-evidence

## Activation Contract

Activate when a strong pain from meli-pain-deepsearch must become a Servicio 1 pathology candidate.
Do not activate for final diagnosis without case reports and confirmed semantics. Output is a testable candidate, never a product claim.

## Hard Rules

- PymIA decides, the LLM communicates. Numbers, reconciliations, and states stay deterministic.
- Every pain maps to pathology candidate plus required evidence plus deterministic control plus treatment or deliverable.
- Owner input is data plus operational meaning. Unconfirmed semantics stay NEEDS_EVIDENCE.
- FAIL_CLOSED on ambiguity. Shadow observation first, promotion only with proof.
- Use candidate language: hypothesis, pathology candidate, observational, under test.

## Decision Gates

| Situation | Action |
|---|---|
| Strong pain plus ML/MP reports and confirmed meaning | Build testable candidate for controlled review loop |
| Strong pain without case reports | Emit NEEDS_EVIDENCE with exact report list, period, and entity |
| Weak pain only | Keep observing, do not promote to pathology |
| Giant software covers it with proof | Discard unless new evidence shows misclassification |

## Execution Steps

1. Take one strong pain row with its evidence links.
2. Write the pathology candidate in one sentence.
3. Define required evidence: exact ML/MP reports, period, seller entity, and meaning confirmations.
4. Define the deterministic control: sums, per-SKU fees, reconciliation match, aging, deadlines, or thresholds.
5. Define the enabled diagnosis plus treatment or deliverable: claim pack, pricing fix, or review action.
6. Assign state: GAP, BLOCKED, NEEDS_EVIDENCE, or READY_FOR_CASE.

## Output Contract

Return a table: Pathology candidate | Source pain | Required evidence | Deterministic control | Enabled diagnosis | Treatment or deliverable | State.
Attach the exact question list for the owner when state is NEEDS_EVIDENCE.

## References

- `../meli-pain-deepsearch/SKILL.md` — upstream pain catalog and strength rules.
- `../../AGENTS.md` — Servicio 1 axis, owner role, and PASS rules.
