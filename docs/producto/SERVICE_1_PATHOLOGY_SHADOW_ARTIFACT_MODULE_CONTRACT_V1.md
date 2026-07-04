# SERVICE_1_PATHOLOGY_SHADOW_ARTIFACT_MODULE_CONTRACT_V1

## VERDICT

```text
MODULE_CONTRACT_AUTHORIZED_FOR_SHADOW_ARTIFACT_ONLY
```

## DOCUMENT_STATUS

```text
Type: MODULE_CONTRACT
Service: SERVICE_1 / SmartPyme
Runtime impact: FUTURE_SHADOW_ONLY_IF_LATER_AUTHORIZED
Code impact: NONE_IN_THIS_DOCUMENT
Tests impact: NONE_IN_THIS_DOCUMENT
Implementation authorized: NO
```

This document converts the conceptual integration of the pathology catalog into a strict future module contract.

It does not implement runtime.

It does not authorize code changes.

It does not promote the pathology catalog to active routing, advisory diagnosis, or final diagnosis.

## SOURCE_DOCUMENTS

```text
docs/producto/SERVICE_1_PATHOLOGY_CATALOG_INTEGRATION_V1.md
docs/producto/SERVICE_1_PATHOLOGY_SHADOW_MODE_V1.md
docs/producto/SERVICE_1_RUNTIME_GOVERNANCE_V1.md
docs/current/ARCHITECTURE_BOUNDARY.md
docs/current/SAAS_AUTONOMY_TARGET.md
docs/doctrina/organizacional/PYMIA_ORGANIZATIONAL_PATHOLOGY_CATALOG_V0.json
```

## MODULE_NAME

```text
Service1PathologyShadowArtifactBuilderV1
```

Proposed runtime file, if later authorized:

```text
PymIA-Live/pymia/smartpyme/service_1_pathology_shadow_artifact_v1.py
```

Public function, if later authorized:

```text
build_service_1_pathology_shadow_artifact_v1()
```

This document is a module contract only.

It does not authorize implementation.

## RESPONSIBILITY

Build a non-binding observational pathology artifact for a Servicio 1 case.

The future module may transform available case signals into pathology candidates without affecting the existing runtime.

Canonical flow:

```text
owner pain / anamnesis signals / case metadata
+ pathology catalog candidate records
+ feature flag state
-> pathology_candidates.json payload
```

The module is an observer only.

It must not diagnose, route, block, release, execute tools, request tools, or modify delivery scope.

## FEATURE_FLAG_REQUIRED

The future module must be controlled by:

```text
SERVICE_1_PATHOLOGY_SHADOW_MODE
```

Allowed flag states:

```text
OFF
SHADOW_ONLY
ADVISORY
ROUTING_CANDIDATE
ACTIVE
```

For this contract, the only executable state allowed is:

```text
SHADOW_ONLY
```

All other states must be treated as non-executable until separately contracted.

Required behavior:

| Flag state | Required behavior |
|---|---|
| `OFF` | return no-effect payload or skip artifact generation |
| `SHADOW_ONLY` | generate observational artifact with `runtime_decision: NO_EFFECT` |
| `ADVISORY` | BLOCKED_FOR_UNCONTRACTED_PROMOTION |
| `ROUTING_CANDIDATE` | BLOCKED_FOR_UNCONTRACTED_PROMOTION |
| `ACTIVE` | BLOCKED_FOR_UNCONTRACTED_PROMOTION |

## INPUTS_ALLOWED

Only these inputs are allowed:

| Input | Source | Required |
|---|---|---|
| `case_id` | current Servicio 1 case/session context | yes |
| `case_ref` | existing case reference, if available | no |
| `owner_pain_text` | owner-provided text or anamnesis summary | no |
| `anamnesis_signals` | existing structured/semi-structured signals | no |
| `case_metadata` | existing case metadata | no |
| `available_evidence_refs` | references to already received evidence | no |
| `catalog_snapshot` | loaded pathology catalog candidate records | yes |
| `feature_flag_state` | caller-provided flag state | yes |
| `metadata` | local passthrough only | no |

At least one of these signal sources must be present for candidate generation:

```text
owner_pain_text
anamnesis_signals
case_metadata
available_evidence_refs
```

If all are absent, the module must return `NO_SIGNALS_AVAILABLE`.

Forbidden inputs:

```text
LLM-generated diagnosis
final diagnosis object
delivery release decision
tool execution result requiring recalculation
storage handles
filesystem paths as authority
external HTTP responses
runtime pipeline mutable state
human signoff objects as candidate evidence
```

## OUTPUT_ARTIFACT

Canonical artifact name:

```text
pathology_candidates.json
```

Required top-level output shape:

```python
{
    "schema_version": str,
    "service_name": "SERVICE_1",
    "case_id": str,
    "case_ref": str | None,
    "mode": "SHADOW_MODE",
    "feature_flag": "SERVICE_1_PATHOLOGY_SHADOW_MODE",
    "feature_flag_state": str,
    "status": str,
    "blocked_reason": str | None,
    "runtime_decision": "NO_EFFECT",
    "diagnosis_authorized": False,
    "routing_authorized": False,
    "tool_selection_authorized": False,
    "delivery_modification_authorized": False,
    "candidate_count": int,
    "detected_candidates": list[dict],
    "missing_evidence_global": list[str],
    "metadata": dict,
}
```

Required candidate shape:

```python
{
    "pathology_id": str,
    "name": str,
    "domain": str,
    "confidence": "candidate",
    "matched_signals": list[str],
    "missing_evidence": list[str],
    "suggested_formulas": list[str],
    "suggested_skills": list[str],
    "source_catalog_status": str,
}
```

Allowed `status` values:

```text
GENERATED
NO_CANDIDATES
BLOCKED
SKIPPED
```

Allowed `blocked_reason` values:

```text
FEATURE_FLAG_OFF
FEATURE_FLAG_STATE_UNCONTRACTED
CATALOG_MISSING
CATALOG_STATUS_UNSUPPORTED
CASE_ID_MISSING
NO_SIGNALS_AVAILABLE
INVALID_INPUT
```

## CATALOG_RULES

The future module may read only catalog entries that expose enough structured fields to produce a candidate artifact.

Minimum catalog fields required per candidate:

```text
id
nombre
dominio or parent domain
senales_anamnesis and/or sintomas
datos_minimos
formulas_asociadas
```

Allowed source catalog status for this contract:

```text
DRAFT_CANONICAL_CANDIDATE
```

Because the catalog is draft, every candidate must preserve:

```text
confidence: candidate
diagnosis_authorized: False
routing_authorized: False
runtime_decision: NO_EFFECT
```

The module must not treat catalog matches as verified pathology.

## MATCHING_RULES_ALLOWED

Allowed matching logic:

```text
case-insensitive string matching
simple token normalization
explicit signal overlap
exact pathology id passthrough if already supplied by upstream non-final context
missing-evidence listing from catalog datos_minimos
formula suggestion passthrough from catalog formulas_asociadas
```

Forbidden matching logic:

```text
probabilistic diagnosis
LLM inference
scoring that implies operational certainty
automatic priority assignment as delivery order
financial impact calculation
risk level calculation
routing decision
skill execution decision
```

## INTERNAL_FUNCTIONS_ALLOWED

Public function:

```text
build_service_1_pathology_shadow_artifact_v1()
```

Allowed internal helpers:

```text
_validate_inputs()
_validate_feature_flag_state()
_validate_catalog_snapshot()
_normalize_signal_text()
_match_catalog_candidates()
_build_generated_payload()
_build_blocked_payload()
_build_skipped_payload()
```

Forbidden helper behavior:

```text
_call_llm()
_execute_tool()
_route_pipeline()
_request_evidence_from_owner()
_create_final_diagnosis()
_modify_delivery_package()
_persist_case_state()
_release_to_owner()
_recalculate_case()
_promote_candidate_to_truth()
```

## FORBIDDEN_DEPENDENCIES

The future module must not import:

```text
external LLM SDKs
HTTP clients
web/API/FastAPI/Fasthtml surfaces
storage.py
vertical_pipeline.py
pipeline_registration.py
final release gates
human review signoff flows
operator delivery package builders
accounting runtimes
bank reconciliation runtimes
Mercado Pago runtimes
invoice collection runtimes
```

Allowed dependencies:

```text
typing
dataclasses
json-safe standard-library helpers
existing immutable DTO/contracts, if import-safe
catalog JSON data supplied by caller
```

## SAFETY_LINE_REQUIRED

Every generated or blocked payload must preserve:

```text
runtime_decision=NO_EFFECT
diagnosis_authorized=False
routing_authorized=False
tool_selection_authorized=False
delivery_modification_authorized=False
```

The future module must never transform:

```text
candidate pathology -> confirmed diagnosis
owner phrase -> verified evidence
missing evidence -> automatic owner request
suggested formula -> executed tool
shadow artifact -> delivery claim
```

## RELATION_TO_SERVICE_1_RUNTIME

This contract attaches to Servicio 1 only as an observational artifact builder.

It may run adjacent to an existing case pipeline only if later implementation is explicitly authorized under the feature flag.

It must not alter:

```text
case state
pipeline state
routing state
tool plan
evidence validation status
delivery manifest
owner-facing diagnosis
QA gate
release gate
```

## RELATION_TO_OWNER_LANGUAGE

The future module may consume owner-facing language only as signal material.

The LLM or conversation layer may provide owner pain text or anamnesis signals, but the module must treat them as unverified signals.

Rule:

```text
Owner language may suggest pathology candidates.
Owner language does not prove pathology.
```

## RELATION_TO_DETERMINISTIC_SKILLS

The future module may list suggested formulas or skills from the catalog.

It must not execute them.

It must not decide that they are required.

It must not route the case toward them.

All execution remains governed by existing Servicio 1 deterministic gates and later contracts.

## ACCEPTANCE_TEST_DESIGN_REQUIRED_BEFORE_CODE

Before any implementation, create focal tests covering at least:

```text
1. OFF flag returns skipped/no-effect output.
2. SHADOW_ONLY with matching owner pain generates candidate artifact.
3. SHADOW_ONLY with no matching signals returns NO_CANDIDATES.
4. SHADOW_ONLY with no signals returns BLOCKED / NO_SIGNALS_AVAILABLE.
5. ADVISORY/ROUTING_CANDIDATE/ACTIVE are blocked as uncontracted promotions.
6. Draft catalog candidates never authorize diagnosis or routing.
7. Missing evidence is copied from catalog datos_minimos only.
8. Suggested formulas are passthrough only and do not execute tools.
9. Output is JSON-serializable.
10. No forbidden imports are introduced.
```

## STOP_CONDITIONS

Stop before implementation if any of the following are missing:

```text
feature flag source
catalog loading boundary
input source boundary
artifact write boundary
acceptance tests
explicit TaskSpec
```

Stop immediately if proposed behavior would:

```text
change routing
block a real case
alter delivery
emit owner-facing diagnosis
execute tools
promote candidates to truth
```

## NEXT_STEP_IF_LATER_AUTHORIZED

Create a TaskSpec for:

```text
SERVICE_1_PATHOLOGY_SHADOW_ARTIFACT_TASKSPEC_V1
```

The TaskSpec must remain documentation-first or tests-first.

It must not implement runtime until acceptance tests and file boundaries are explicitly approved.

## FINAL_STATUS

```text
SERVICE_1_PATHOLOGY_SHADOW_ARTIFACT_MODULE_CONTRACT_V1: CREATED
RUNTIME_TOUCHED: NO
CODE_TOUCHED: NO
TESTS_RUN: NO
IMPLEMENTATION_AUTHORIZED: NO
NEXT_STEP: TASKSPEC_OR_ACCEPTANCE_TEST_DESIGN_ONLY
```
