# WEB_INTAKE_ROOT_ALIGNMENT_V1

## Status

CURRENT_CANON_ALIGNMENT

## Purpose

Definir la alineación mínima entre la web limpia de PymIA y el core real de Servicio 1.

Este documento no implementa UI, backend, runtime, pipeline ni delivery.

## Governing rule

```text
La web captura archivo.
File Intake clasifica.
La estructura se extrae como dato técnico.
El dueño confirma significado.
Sólo significado rectificado puede alimentar candidatos posteriores.
```

## Canonical chain

```text
landing/service_1_excel_upload_smoke.html
→ FileIntakeResult
→ TaskSpecPatch
→ XLSX structure extraction / document ingestion
→ ColumnConfirmationMatrix
→ OwnerPromptBatch
→ OwnerColumnConfirmationAnswer
→ owner_rectified_function
→ OwnerRectifiedEvidenceProfile
→ CandidateTools
→ ControlledExecutionCandidate
→ SupervisedDryRunPlan
```

## Source of truth

```text
docs/current/
pymia/smartpyme/file_intake_v1.py
pymia/smartpyme/file_intake_taskspec_boundary_v1.py
pymia/contracts/column_confirmation_v1.py
pymia/smartpyme/service_1_column_confirmation_owner_prompt_batch_v1.py
pymia/smartpyme/service_1_owner_rectified_evidence_profile_v1.py
pymia/smartpyme/service_1_evidence_profile_to_candidate_tools_contract_v1.py
```

## Landing boundary

`landing/` is not operational authority.

Allowed current web artifact:

```text
landing/service_1_excel_upload_smoke.html
```

Allowed role:

```text
browser-only XLSX structure smoke
```

Forbidden role:

```text
diagnosis
business interpretation
runtime authorization
tool execution
delivery
owner semantic truth
```

## File support V1

Current operative support is XLSX-only.

```text
XLSX: SUPPORTED for initial intake and structure extraction
CSV: UNSUPPORTED_IN_V1
TXT: UNSUPPORTED_IN_V1
PDF: UNSUPPORTED_IN_V1
IMAGE: UNSUPPORTED_IN_V1
UNKNOWN: UNKNOWN / fail-closed
```

The SaaS/web boundary must not broaden this support before File Intake V1 and tests do.

## Semantic boundary

Headers, sheet names, filename and preview rows are not business truth.

They may only produce:

```text
suggested_semantic_role
PENDING_OWNER_CONFIRMATION
BLOCKED_AMBIGUOUS
unknown
```

Operational evidence requires:

```text
owner_rectified_function
confirmation_status = CONFIRMED
```

## Required owner conversation

The web must eventually ask governed questions generated from contracts, not from ad-hoc HTML copy.

Allowed future source:

```text
Service1ColumnConfirmationOwnerPromptBatchV1
```

Not allowed:

```text
free HTML simulation
filename keyword routing
hardcoded demo questions
hardcoded business claims
```

## Next implementation slice

```text
WEB_XLSX_TO_COLUMN_CONFIRMATION_ADAPTER_V1
```

Scope:

```text
pure Python model/tests
input: XLSX structural extraction result or fixture structure
output: ColumnConfirmationMatrix + OwnerPromptBatch
no HTML
no runtime
no tool execution
no delivery
no diagnosis
```

## Acceptance criteria for future slice

PASS only if:

```text
- works with cafeteria_abc.xlsx and another synthetic XLSX;
- no filename routing;
- no sheet-name truth;
- every column starts pending owner confirmation;
- unknown columns stay unknown/pending;
- runtime_authorized remains false;
- tool_execution_authorized remains false;
- delivery_authorized remains false where present;
- tests prove no hardcoded demo path.
```

## Closed decisions

```text
- Landing demo/prototype does not govern Servicio 1.
- Web smoke is not product runtime.
- File Intake V1 remains XLSX-only.
- Semantics require owner rectification before evidence profile.
- No more HTML-level semantic patches before adapter contract exists.
```

