# SERVICE_1_WEB_COLUMN_CONFIRMATION_INTAKE_BOUNDARY_V1 — ModuleContract

## VERDICT

```text
MODULE_CONTRACT_AUTHORIZED_FOR_WEB_INTAKE_BOUNDARY_ONLY
WEB_OWNER_COLUMN_CONFIRMATION_REAL_FLOW: STILL_NOT_CERTIFIED
RUNTIME_AUTHORIZED: false
REEXECUTION_AUTHORIZED: false
RECALCULATION_AUTHORIZED: false
DELIVERY_AUTHORIZED: false
```

## MODULE_NAME

```text
Service1WebColumnConfirmationIntakeBoundaryV1
```

Proposed runtime file, if later authorized:

```text
pymia/smartpyme/service_1_web_column_confirmation_intake_boundary_v1.py
```

Public function, if later authorized:

```text
build_service_1_web_column_confirmation_intake_boundary_v1()
```

This document is a ModuleContract only. It authorizes the boundary shape and safety rules for a future implementation. It does not implement the web flow and does not certify the online CASE_001 owner confirmation flow.

## GOVERNING TASKSPEC

```text
docs/current/SERVICE_1_WEB_OWNER_COLUMN_CONFIRMATION_REAL_FLOW_TASKSPEC_V1.md
```

Current state remains:

```text
WEB_OWNER_COLUMN_CONFIRMATION_REAL_FLOW_NOT_CERTIFIED
```

## RESPONSIBILITY

Transform a real web-uploaded XLSX file into a governed owner-facing column-confirmation intake packet using PymIA canonical readers as the only certified source of truth.

The boundary is responsible only for this shape:

```text
web uploaded XLSX bytes/path
-> canonical PymIA XLSX reader(s)
-> extracted structure
-> ColumnConfirmationMatrix
-> owner-facing 12 CASE_001 questions when CASE_001 is the selected case
-> evidence-ready intake packet
```

It must not capture owner answers by itself unless a separate call explicitly supplies already-submitted owner responses. It must not apply answers to the matrix, classify free text, recalculate, diagnose, deliver, or authorize runtime.

## INPUTS_ALLOWED

| Input | Type | Required | Rule |
|---|---|---:|---|
| `uploaded_file_name` | `str` | yes | Original owner-visible file name. |
| `uploaded_file_bytes` or `uploaded_file_path` | `bytes` or safe local path | yes | Exactly one source. Must represent a real uploaded XLSX. |
| `case_id` | `str` | yes | For CASE_001 evidence, must identify CASE_001 / governed case id. |
| `tenant_id` | `str` | yes | Local boundary metadata only. |
| `intake_id` | `str` | yes | Local boundary metadata only. |
| `metadata` | `dict | None` | no | Local passthrough only. |

Optional future input, only after answer capture is explicitly authorized:

| Input | Type | Rule |
|---|---|---|
| `owner_answers` | list of governed answer records | Must be real owner-submitted online answers, not fixtures. |

## REQUIRED PROCESS

A future implementation must follow this order:

```text
1. Validate upload boundary and file identity.
2. Materialize uploaded bytes only in a controlled temporary/local boundary if needed.
3. Use PymIA canonical XLSX reader(s):
   - service_1_xlsx_structure_v1.py
   - service_1_xlsx_to_normalized_table_v1.py, only if table rows are needed
4. Build or reuse the existing XLSX structure -> column-confirmation chain.
5. Produce ColumnConfirmationMatrix.
6. Produce owner-facing column-confirmation questions/display packet.
7. For CASE_001, assert exactly 12 expected questions before any evidence claim.
8. Return an evidence-ready packet with all safety flags false.
```

SheetJS or browser-only parsing may be used only as non-certified preview UX. It must never be the certified source for the evidence packet.

## OUTPUTS_REQUIRED

The boundary output must include at minimum:

```text
schema_version
service_name
status
case_id
tenant_id
intake_id
uploaded_file_name
canonical_reader_used
column_confirmation_matrix_summary
owner_question_packet
expected_question_count
captured_answer_count
runtime_authorized
reexecution_authorized
recalculation_authorized
delivery_authorized
diagnosis_generated
evidence_artifact_ready
blocking_reasons
metadata
```

Allowed statuses:

```text
READY_FOR_OWNER_CONFIRMATION
OWNER_CONFIRMATIONS_CAPTURED
BLOCKED_UPLOAD_INVALID
BLOCKED_CANONICAL_READER_FAILED
BLOCKED_QUESTION_COUNT_MISMATCH
BLOCKED_OWNER_ANSWERS_MISSING
BLOCKED_OWNER_ANSWERS_AMBIGUOUS
BLOCKED_UNCERTIFIED_BROWSER_ONLY_FLOW
```

## SAFETY_LINE_REQUIRED

Every output must preserve:

```text
runtime_authorized = false
reexecution_authorized = false
recalculation_authorized = false
delivery_authorized = false
diagnosis_generated = false
```

If owner answers are present, the output may say only whether the evidence packet is ready for separate validation. It must not unlock dry-run, calculation, diagnosis, or delivery.

## FORBIDDEN_DEPENDENCIES

The future module must not import or call:

```text
vertical_pipeline.py
runner / autonomous runner modules
SaaS runtime surfaces
API worker / storage worker surfaces
diagnostic_core modules
delivery modules
external LLM SDKs
external HTTP clients for decision-making
landing browser code as source of truth
```

Allowed dependencies:

```text
standard library for safe temp/path handling
service_1_xlsx_structure_v1.py
service_1_xlsx_to_normalized_table_v1.py
service_1_xlsx_structure_extraction_to_adapter_chain_v1.py
service_1_xlsx_structure_to_column_confirmation_v1.py
service_1_column_confirmation_owner_prompt_batch_v1.py
service_1_owner_prompt_batch_display_model_v1.py
service_1_owner_column_confirmation_answer_intake_v1.py, only if real owner answers are explicitly supplied
```

## NON_GOALS

This boundary must not:

```text
create a web UI
serve HTTP
persist production state
call a runner
perform dry-run or calculation
generate diagnosis
generate delivery
normalize free-text owner answers into operational roles
apply answers to ColumnConfirmationMatrix
create OwnerRectifiedEvidenceProfile
declare Servicio 1 complete or product-ready
```

## ACCEPTANCE TESTS REQUIRED FOR FUTURE IMPLEMENTATION

A future implementation must include focal tests for:

1. Real uploaded XLSX fixture reaches canonical reader path.
2. Browser-only / SheetJS-only payload is blocked as uncertified.
3. CASE_001 produces exactly 12 owner-facing questions before answer capture.
4. Missing owner answers keep status blocked / awaiting owner.
5. Ambiguous owner answer blocks evidence readiness.
6. Unknown question ref blocks evidence readiness.
7. All safety flags remain false in every status.
8. No forbidden imports or runtime/delivery calls are present.
9. Evidence packet shape matches `SERVICE_1_CASE_001_OWNER_COLUMN_CONFIRMATIONS_EVIDENCE_CYCLE_TASKSPEC_V1`.

## STOP CONDITIONS

Stop before implementation if:

```text
there is no safe upload boundary contract
there is no canonical reader invocation path
CASE_001 question count cannot be proven as 12
owner answers would need to be simulated
browser parsing would become certified source of truth
runtime/dry-run/diagnosis/delivery pressure appears
```

## NEXT STEP

After this ModuleContract is accepted, the next methodological artifact may be a narrow TaskSpec for implementation of:

```text
service_1_web_column_confirmation_intake_boundary_v1.py
+ focal tests
```

That future TaskSpec must remain before any UI wiring, runner, dry-run, diagnosis, or delivery work.
