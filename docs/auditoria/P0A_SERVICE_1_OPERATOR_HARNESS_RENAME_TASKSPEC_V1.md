# P0A_SERVICE_1_OPERATOR_HARNESS_RENAME_TASKSPEC_V1

## VERDICT

```text
STATUS: TASKSPEC_CREATED
SCOPE: DOC_ONLY
RUNTIME_CHANGE: NO
TEST_CHANGE: NO
DELETE_CHANGE: NO
TARGET_BATCH: P0-A
```

## OBJECTIVE

Rename the contaminated Service 1 operator harness into a controlled delivery demo harness while preserving behavior and tests.

This patch must remove the operator identity from this runtime-facing component without changing Service 1 pipeline semantics.

## TARGET FILES

### Runtime files

```text
PymIA-Live/pymia/smartpyme/service_1_operator_harness_v1.py
PymIA-Live/pymia/smartpyme/service_1_synthetic_real_case_pilot_v1.py
PymIA-Live/pymia/smartpyme/service_1_operator_delivery_package_v1.py
```

### Tests

```text
PymIA-Live/tests/smartpyme/test_service_1_operator_harness_v1.py
PymIA-Live/tests/smartpyme/test_service_1_operator_harness_real_output_audit_v1.py
PymIA-Live/tests/smartpyme/test_service_1_operator_delivery_package_v1.py
PymIA-Live/tests/smartpyme/test_service_1_delivery_manifest_audit_v1.py
PymIA-Live/tests/smartpyme/test_service_1_delivery_folder_smoke_v1.py
```

### Docs likely needing follow-up rename/status update

```text
docs/producto/SERVICE_1_FIRST_AID_FAMILY_CLOSURE_V1.md
docs/producto/SERVICE_1_XLSX_DELIVERY_GENERALIZATION_V1.md
docs/producto/SERVICE_1_OPERATOR_HARNESS_REAL_OUTPUT_AUDIT_V1.md
docs/auditoria/P0_OPERATOR_REFERENCE_CHECK_AUDIT_ONLY_V1.md
```

Docs follow-up may be separate from runtime patch if the diff becomes too large.

## REQUIRED RENAME

```text
service_1_operator_harness_v1.py
-> service_1_controlled_delivery_demo_harness_v1.py
```

## REQUIRED SYMBOL MIGRATION

```text
Service1OperatorHarnessCaseV1
-> Service1ControlledDeliveryDemoCaseV1

Service1OperatorHarnessRunV1
-> Service1ControlledDeliveryDemoRunV1

build_service_1_operator_harness_sample_case_v1
-> build_service_1_controlled_delivery_demo_sample_case_v1

run_service_1_operator_harness_v1
-> run_service_1_controlled_delivery_demo_harness_v1

operator_notes
-> delivery_notes

operator_report_path
-> delivery_report_path

operator_report.txt
-> delivery_report.txt

_build_operator_report
-> _build_delivery_report
```

## REQUIRED STRING MIGRATION

Replace runtime-facing messages:

```text
SERVICE_1_OPERATOR_HARNESS_V1 requires...
-> SERVICE_1_CONTROLLED_DELIVERY_DEMO_HARNESS_V1 requires...

Operator harness run completed from explicit case payload.
-> Controlled delivery demo harness run completed from explicit case payload.

Delivery folder contains XLSX files, summary, and operator report.
-> Delivery folder contains XLSX files, summary, and delivery report.

Notas operador:
-> Notas de entrega:
```

## PRESERVE BEHAVIOR

The patch must preserve:

```text
- same sample tool_requests;
- same pipeline call: run_service_1_pipeline_v1;
- same output_dir handling;
- same generated XLSX behavior;
- same summary.txt behavior;
- same runtime_authorized False;
- same fail-fast behavior for missing output_root, empty case_id, and empty tool_requests;
- same deterministic case_id sanitization.
```

## FORBIDDEN CHANGES

```text
- Do not modify service_1_pipeline_v1.
- Do not add LLM, API, chatbot, FastAPI, LangGraph, Telegram, OCR, PDF parser, or external IO.
- Do not broaden Service 1 scope.
- Do not open Service 2.
- Do not rename unrelated operator references.
- Do not delete old behavior before tests prove replacement.
- Do not change delivery package semantics except import/type names and report field names required by rename.
```

## COMPATIBILITY STRATEGY

Preferred strategy:

```text
Hard rename module and imports in one focused batch.
No compatibility shim unless tests or external imports require it.
```

Fallback strategy if coupling is higher than expected:

```text
Create new controlled delivery demo harness module.
Leave old module as deprecated import shim temporarily.
Shim must contain no operator authority and must point to new functions.
```

## TEST PLAN

Run from `PymIA-Live`:

```bash
python -m pytest \
  tests/smartpyme/test_service_1_operator_harness_v1.py \
  tests/smartpyme/test_service_1_operator_harness_real_output_audit_v1.py \
  tests/smartpyme/test_service_1_operator_delivery_package_v1.py \
  tests/smartpyme/test_service_1_delivery_manifest_audit_v1.py \
  tests/smartpyme/test_service_1_delivery_folder_smoke_v1.py \
  -q
```

If tests are renamed in the same patch, run the renamed equivalents plus any unchanged delivery tests.

## ACCEPTANCE CRITERIA

```text
1. No file or symbol named operator_harness remains for this P0-A component, except in historical audit docs.
2. Runtime behavior remains equivalent.
3. All focal tests pass.
4. git status shows only intended runtime/test/doc changes.
5. No Service 2 files touched.
6. No unrelated operator references touched.
```

## EXPECTED OUTCOME

```text
The useful function survives as controlled delivery demo harness.
The dead operator identity is removed from the Service 1 harness boundary.
```

## FINAL_STATUS

```text
P0A_SERVICE_1_OPERATOR_HARNESS_RENAME_TASKSPEC_V1: CREATED
CODE_CHANGE_AUTHORIZED: NO
NEXT_ACTION: IMPLEMENT_P0A_ONLY_AFTER_OWNER_APPROVAL_OR_EXPLICIT_EXECUTION_COMMAND
```
