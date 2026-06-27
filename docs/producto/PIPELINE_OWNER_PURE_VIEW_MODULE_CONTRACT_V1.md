# PIPELINE_OWNER_PURE_VIEW_MODULE_CONTRACT_V1

## VEREDICT

```text
MODULE_CONTRACT_CORRECTED
```

## MODULE_NAME

```text
PipelineOwnerPureView
```

Proposed runtime file, if later authorized:

```text
pymia/smartpyme/owner_pure_view.py
```

Public function, if later authorized:

```text
build_owner_pure_view()
```

This document is a module contract only. It does not authorize implementation.

## RESPONSIBILITY

Transform existing Chain A data into a pure owner-facing view for the XLSX Review Family.

The module is a translation layer only:

```text
existing Chain A fields -> owner-safe fields
```

It must not add pipeline logic, diagnostic logic, LLM logic, First Aid logic, bridge logic, or Service 2/3 behavior.

## INPUTS_ALLOWED

Only these inputs are allowed:

| Input | Source | Required |
|---|---|---|
| `profile` | `inspect_excel` output | yes |
| `report` | `build_report` / OwnerFacingReport-like dict | yes |
| `owner_simple` | owner simple view fields | yes |
| `structured_summary` | structured summary from Chain A | yes, may be empty |
| `column_confirmation` | existing column confirmation data, if present | no |

Allowed `owner_simple` fields:

```text
que_entendimos
que_pudimos_leer
que_todavia_no_podemos_afirmar
proxima_pregunta
limites
```

Forbidden inputs:

```text
raw Excel file
diagnostic_core
kernel
audit trails
tool_requests
First Aid delivery package
bridge artifacts
LLM output
Hermes artifacts
external API results
```

## OUTPUTS_REQUIRED

The module must produce owner-facing fields only.

All owner-facing fields must be plain strings or lists of strings.

No owner-facing output may contain nested dicts, IDs, hashes, formula IDs, pipeline IDs, or technical status names.

```python
{
    "owner_executive_summary": str,
    "owner_business_areas": list[str],
    "owner_analysis_possibilities": list[str],
    "owner_cannot_claim": list[str],
    "owner_column_ambiguities": list[str],
    "owner_missing_evidence_plain": list[str],
    "owner_single_next_action": str,
    "owner_limits_plain": list[str],
    "owner_blocked_explanation": str | None,
    "owner_not_rejection": str | None,
}
```

### Important correction

`owner_column_ambiguities` is `list[str]`, not `list[dict]`.

Example:

```text
No queda claro si la columna 'total' representa lo facturado o lo cobrado.
```

## FIELD_CLASSIFICATION

### Derived from existing owner fields

| Field | Existing source |
|---|---|
| `owner_analysis_possibilities` | `owner_simple.que_pudimos_leer` |
| `owner_cannot_claim` | `owner_simple.que_todavia_no_podemos_afirmar` |
| `owner_limits_plain` | `owner_simple.limites` |

### New or explicit transformation fields

| Field | Nature |
|---|---|
| `owner_executive_summary` | new |
| `owner_business_areas` | transform technical sheet/table names into business labels |
| `owner_column_ambiguities` | new owner-safe ambiguity statements |
| `owner_missing_evidence_plain` | transform missing evidence into owner-readable requests |
| `owner_single_next_action` | reduce possible next questions to one action |
| `owner_blocked_explanation` | new, required only when blocked |
| `owner_not_rejection` | new, required only when blocked |

## INTERNAL_FUNCTIONS_ALLOWED

Public function:

```text
build_owner_pure_view()
```

Allowed internal helpers:

```text
_build_executive_summary()
_build_business_areas()
_build_column_ambiguities()
_build_missing_evidence_plain()
_build_single_next_action()
_build_blocked_explanation()
_build_not_rejection()
_validate_forbidden_output_content()
```

Allowed logic:

```text
fixed templates
fixed mapping tables
plain string transformations
status-based branching limited to DELIVERED_CANDIDATE / BLOCKED
```

Forbidden helper behavior:

```text
_call_llm()
_infer_meaning()
_generate_narrative()
_diagnose()
_compute_metrics()
_fetch_external()
_bridge_to_tools()
```

## FORBIDDEN_DEPENDENCIES

The future module must not import:

```text
diagnostic core modules
kernel modules
audit modules
bridge modules
tool request modules
First Aid modules
LLM modules
chatbot modules
external HTTP clients
external LLM SDKs
graph orchestration libraries
data-science libraries not needed for string translation
```

Allowed dependencies:

```text
typing
collections / dataclasses if needed for local types only
existing owner report types, if import-safe
```

## FORBIDDEN_OUTPUT_CONTENT

No owner-facing field may contain:

```text
structured_evidence
structured_evidence_summary
sufficiency
EvidenceGateDecision
readiness
computed_variables
computed_variable_names
formula_ids
table_sheets
column_confirmation matrix
evidence_used
missing_evidence
gate_verdict
tenant_id
run_id
evidence_id
intake_id
delivery_package_id
evidence_hash
output_hash
manifest
SHA256
DELIVERED_CANDIDATE
BLOCKED
NEEDS_EVIDENCE
SLICE_ONLY
candidato
bloqueado
pipeline
kernel
core
causa raíz
recomendación prescriptiva
automatización
conciliación bancaria
rentabilidad real
esto resuelve tu problema
```

### Diagnostic wording correction

The owner output should avoid saying:

```text
Esto no es un diagnóstico.
```

Preferred wording:

```text
Esta es una primera lectura del archivo, no una conclusión final sobre tu negocio.
```

This avoids conflict with forbidden content scanning while preserving product honesty.

## BLOCKING_RULES

| Condition | Effect |
|---|---|
| `profile` missing or incomplete | error; no owner view |
| `report.status` not supported | error; no owner view |
| missing `owner_executive_summary` | invalid output |
| blocked status without `owner_blocked_explanation` | invalid output |
| blocked status without `owner_not_rejection` | invalid output |
| any field contains forbidden content | invalid output with field name |
| delivered status includes blocked-only fields as visible text | invalid output |

Supported statuses for this contract:

```text
DELIVERED_CANDIDATE
BLOCKED
```

Technical status labels must not be shown to the owner.

## OPERATOR_APPENDIX_RELATION

The module may produce a separate operator appendix.

The appendix is not owner-facing.

It may contain traceability metadata such as:

```text
source fields used
template names
mapping table names
forbidden content validation result
build timestamp
```

The appendix is used by the operator to verify that owner-facing text is faithful to Chain A data.

The appendix must never be included in the owner-facing view.

## ACCEPTANCE_CRITERIA

1. The module transforms existing Chain A fields only.
2. It does not read Excel files.
3. It does not call the pipeline.
4. It does not import First Aid, bridge, LLM, diagnostic core, or external APIs.
5. All owner-facing outputs are strings or lists of strings.
6. `owner_column_ambiguities` is `list[str]`.
7. Same inputs produce same outputs.
8. Forbidden content validation runs after output construction.
9. Blocked cases include a clear explanation and a non-rejection note.
10. Delivered cases do not include blocked-only owner messages.
11. The wording avoids technical status names and internal IDs.
12. The owner-facing text says "first reading" / "initial reading", not technical candidate terminology.

## NEXT_SAFE_ACTION

```text
Design OWNER_PURE_VIEW_TASKSPEC_V1.
```

Do not implement yet.

Do not write runtime code yet.

Do not write tests yet.

Do not open renderer yet.

Do not open bridge.

Do not open Service 2 or Service 3.
