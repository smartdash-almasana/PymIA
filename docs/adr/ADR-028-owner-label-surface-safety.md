# ADR-028 — Owner Label Surface Safety for Internal Semantic Tokens

## Status

Accepted and implemented.

## Date

2026-08-13

## Scope

Owner-facing confirmation surfaces (options, questions, descriptions) generated
from `_RoleRule` definitions in
`pymia/smartpyme/service_1_column_understanding_engine_v1.py` must never render
an internal semantic token verbatim. The `ebitda` role label collided with its
own internal token and blocked every workbook containing an `ebitda` column at
the owner-confirmation loop.

## Authority

- `docs/adr/ADR-021-owner-answer-evaluation-authority.md`
- `docs/adr/ADR-018-owner-facing-report-boundary.md`
- `pymia/smartpyme/service_1_controlled_execution_candidate_to_owner_confirmation_loop_v1.py`
  (`_owner_question_surface_is_safe`, `BLOCK_OWNER_QUESTION_SURFACE_UNSAFE`)

## Context

The owner-confirmation loop rejects any question surface that renders a
candidate semantic role token lowercased. The `ebitda` `_RoleRule` used:

```text
owner_label="EBITDA"
owner_question_text="¿Esta columna representa el EBITDA del período?"
owner_option_description="EBITDA del período confirmado."
```

The lowercase rendered surface contained `ebitda`, which is itself a candidate
semantic role for the column. Every question composed for an `ebitda` column
therefore failed with `OWNER_QUESTION_SURFACE_UNSAFE`, blocking any bounded
capability that requires `ebitda` as an input (for example
`interest_burden_ratio` in the bounded-six physical controls fixture).

This was never observed in CI because the bounded-six fixture was git-ignored
and absent from the repository; the tool committed at `f111bf0` had never been
executed against a real workbook.

## Decision

Replace the `ebitda` owner-facing strings with a neutral operating result
label that does not contain the internal token:

```text
owner_label="Resultado operativo (antes de intereses)"
owner_question_text="¿Esta columna representa el resultado operativo del período?"
owner_option_description="Resultado operativo del período confirmado."
risk_text="El resultado operativo debe corresponder al mismo período que el gasto por intereses."
```

Rule: for every `_RoleRule`, the lowercased concatenation of `owner_label`,
`owner_question_text`, `owner_option_description`, and `risk_text` must not
contain any string in the rule's `candidate_semantic_roles` derivation.

## Consequences

- Owner confirmation surfaces for `ebitda` columns no longer leak the internal
  token and pass the surface safety check.
- The `interest_burden_ratio` bounded control (POS_INTEREST) reaches P8
  `COMPUTABLE` and evaluates to the declared ground truth.
- No schema, pipeline, or evidence contract changed; this is a wording-level
  defect fix on the owner surface.
- Future `_RoleRule` additions must audit owner-facing strings against the
  rule's internal tokens.

## Validation

- `python tools/service_1_bounded_six_physical_computable_controls_v1.py`
  → `PASS_BOUNDED_SIX_PHYSICAL_COMPUTABLE_CONTROLS_V1`, 6/6 positive and 6/6
  negative controls.
- `pytest tests/smartpyme/test_service_1_bounded_six_physical_computable_controls_v1.py`
  → 2 passed.
- Full `tests/smartpyme` run: 2352 passed, 28 failed; all 28 failures present
  at baseline before this change (0 regressions, 14 tests newly fixed).
