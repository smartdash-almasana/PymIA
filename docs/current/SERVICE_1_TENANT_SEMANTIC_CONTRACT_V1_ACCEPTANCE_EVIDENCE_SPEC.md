# SERVICE_1_TENANT_SEMANTIC_CONTRACT_V1 — Acceptance Evidence Spec

## State

```text
ACCEPTANCE_DEFINED
EVIDENCE_NOT_YET_PRODUCED
```

## Test fixtures

Use the canonical `Service1OwnerConfirmationEventV1` builder. No fake alternate event schema is allowed.

Required fixture families:

1. tenant A, semantic-role confirmation, revision 1;
2. tenant A, corrected semantic-role confirmation, revision 2;
3. tenant B with a similar header;
4. event/context mismatch;
5. missing actor identity;
6. invalid tenant path;
7. duplicate id with identical payload;
8. duplicate id with conflicting payload;
9. free-text meaning;
10. column exclusion.

Fixtures must contain safe metadata only and no raw workbook rows.

## Acceptance matrix

| ID | Scenario | Expected |
|---|---|---|
| TS-01 | valid event + explicit tenant/actor/context | `TENANT_SEMANTIC_CONTRACT_READY` |
| TS-02 | append revision 1 | `TENANT_SEMANTIC_CONTRACT_RECORDED` |
| TS-03 | exact round-trip | serialized equality |
| TS-04 | list tenant A | only tenant A records |
| TS-05 | load tenant A id through tenant B | none / blocked; never global lookup |
| TS-06 | unsafe tenant id | hard block |
| TS-07 | blank actor id or role | `BLOCKED_MISSING_ACTOR_IDENTITY` |
| TS-08 | event sheet/column/question mismatch | `BLOCKED_EVENT_CONTEXT_MISMATCH` |
| TS-09 | revision 2 with matching prior | append; revision 1 unchanged |
| TS-10 | revision 2 without prior | `BLOCKED_REVISION_INVALID` |
| TS-11 | supersedes another tenant/series | `BLOCKED_SUPERSESSION_MISMATCH` |
| TS-12 | identical append | `TENANT_SEMANTIC_CONTRACT_ALREADY_RECORDED` |
| TS-13 | same id, different payload | `BLOCKED_CONTRACT_ID_CONFLICT` |
| TS-14 | semantic-role scope without role | blocked |
| TS-15 | exclusion carrying role | blocked |
| TS-16 | free-text scope without corrected meaning | blocked |
| TS-17 | forbidden authority flag in provenance | blocked |
| TS-18 | serialized output inspection | all authority/reuse flags false |
| TS-19 | source inspection | no product-root/web/LLM/delivery imports |
| TS-20 | repository diff | no product root, web, reuse or drift files changed |

## Focal validation expected

Future implementation must run only the new focal tests first:

```text
python -m pytest   tests/smartpyme/test_service_1_tenant_semantic_contract_v1.py   tests/smartpyme/test_service_1_tenant_semantic_contract_store_v1.py   -q
```

Then the bounded neighboring regression:

```text
tests/smartpyme/test_service_1_owner_confirmation_event_v1.py
tests/smartpyme/test_storage.py
tests/smartpyme/test_anamnesis_storage.py
tests/smartpyme/test_owner_answer_storage.py
```

The full suite is not authorized by this spec.

## Documentary gates

- `git diff --check`;
- docs index audit;
- forbidden-term/import inspection;
- changed paths match the implementation TaskSpec;
- `graphify update .` after code changes when available.

## PASS rule

This slice may receive:

```text
PASS_TENANT_SEMANTIC_CONTRACT_FOUNDATION_V1
```

only when all TS-01 through TS-20 are demonstrated and the neighboring regression is green.

That PASS means contract foundation and isolated persistence only.

It must not be reported as:

```text
TENANT_MEMORY_IMPLEMENTED
SECOND_LOAD_REUSE_IMPLEMENTED
DRIFT_DETECTION_IMPLEMENTED
PRODUCT_REPEATABILITY_CLOSED
```
