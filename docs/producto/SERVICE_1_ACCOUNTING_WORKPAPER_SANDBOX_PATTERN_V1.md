# SERVICE_1_ACCOUNTING_WORKPAPER_SANDBOX_PATTERN_V1

VEREDICT:

```text
WORKPAPER_SANDBOX_PATTERN_V1: CAPTURED
```

PURPOSE:

```text
Definir el patrón seguro para avanzar desde accounting_workpaper_basic hacia un sandbox de borrador de papel de trabajo.
No implementa runtime.
No genera papeles finales.
No certifica evidencia.
No valida auditoría contable.
```

SOURCE_CHAIN:

```text
service_1_accounting_contracts_v1
accounting_workpaper_contract_v1
accounting_human_review_gate_v1
service_1_xlsx_delivery_v1
SERVICE_1_ACCOUNTING_RUNTIME_AUTHORIZATION_MATRIX_V1
SERVICE_1_ACCOUNTING_SANDBOX_PATTERN_V1
```

CURRENT_STATE:

```text
accounting_workpaper_basic = CONTRACT_ONLY
runtime_authorized = false
production_allowed = false
```

CURRENT_REQUIRED_SOURCES:

```text
evidencia_soporte
plantilla_papel_trabajo
```

CURRENT_REQUIRED_FIELDS:

```text
periodo
cliente
area_revision
responsable
```

TARGET_SANDBOX_CONCEPT:

```text
workpaper_draft_builder_sandbox
```

SCOPE:

```text
Construir un artefacto de revisión tipo borrador, trazable y owner/operator-facing,
a partir de evidencia soporte y una estructura de plantilla declarada.
```

NON_GOALS:

```text
No final workpaper.
No certified workpaper.
No audit approval.
No fiscal accuracy claim.
No accounting entries.
No tax calculation.
No evidence sufficiency certification.
No OCR.
No PDF parser.
No external API.
No bank runtime.
No Mercado Pago runtime.
No LLM.
No FSM change.
No vertical_slice.py.
```

PATTERN_SHAPE:

```text
base_contract
  -> human_review_gate
  -> evidence_manifest
  -> template_manifest
  -> draft_packet
  -> generic_xlsx_delivery
```

IRREVERSIBLE_BOUNDARY_RULE:

```text
A workpaper layer is justified only if it adds one of these irreversible boundaries:
- evidence manifest validation
- template manifest validation
- traceability mapping between evidence and draft sections
- explicit forbidden-claims protection
- owner/operator review packet
- delivery-compatible artifact
```

MICROCYCLE_WARNING:

```text
Do not create a layer that only reformats accounting_workpaper_contract_v1 delivery_input.
Do not create a renderer unless it produces a new decision artifact not expressible by generic XLSX delivery.
```

MINIMAL_SANDBOX_INPUTS:

```text
contract_result
human_review_gate_result
evidence_manifest
template_manifest
```

EVIDENCE_MANIFEST_CONCEPT:

```text
An evidence manifest is not file parsing.
It is a declared inventory of support evidence received for a workpaper draft.
```

Candidate fields:

```text
evidence_ref
source_name
source_kind
period_ref
owner_supplied
operator_notes
sensitive_data_present
```

TEMPLATE_MANIFEST_CONCEPT:

```text
A template manifest is not an Excel template runtime.
It is a declared structure of expected workpaper sections.
```

Candidate fields:

```text
template_ref
template_name
area_revision
required_sections
optional_sections
review_owner
```

DRAFT_PACKET_CONCEPT:

```text
A draft packet is not a final workpaper.
It is a review-ready package that tells the operator and owner:
- what evidence was declared
- what template structure was declared
- what is missing
- what is forbidden to claim
- what the next safe action is
```

FORBIDDEN_CLAIMS:

```text
No evidence was fully audited.
No workpaper is final.
No accounting conclusion is certified.
No tax conclusion is certified.
No entry should be posted automatically.
No source file was parsed unless a later authorized parser says so.
No template was executed as runtime unless a later authorized runtime says so.
```

REUSE_FROM_ACCOUNTING_SANDBOX_PATTERN:

```text
Reuse:
- human review gate semantics
- sandbox permission semantics
- forbidden claims taxonomy
- generic delivery compatibility

Specialize:
- evidence manifest
- template manifest
- draft packet sections
- workpaper-specific blocked reasons
```

MATURITY_LEVELS:

```text
CONTRACT_ONLY:
  workpaper scope exists, no draft package.

SANDBOX_MANIFEST_READY:
  evidence and template manifests are valid, but no draft packet exists.

SANDBOX_DRAFT_PACKET_READY:
  review packet exists and can be delivered through generic XLSX delivery.

FINAL_WORKPAPER:
  forbidden in this pattern.
```

OPENING_RULE:

```text
Open code only after this pattern can answer:
- what evidence manifest validates
- what template manifest validates
- what draft packet adds beyond contract delivery_input
- what claims remain forbidden
```

NEXT_SAFE_BLOCK:

```text
SERVICE_1_ACCOUNTING_WORKPAPER_MANIFEST_MODEL_V1
```

RECOMMENDED_MODE_FOR_NEXT_BLOCK:

```text
CONTRACT/MODEL ONLY
No file parsing.
No template execution.
No final workpaper generation.
No tests beyond pure manifest validation if code is opened.
```

COMMIT_READY:

```text
YES
```
