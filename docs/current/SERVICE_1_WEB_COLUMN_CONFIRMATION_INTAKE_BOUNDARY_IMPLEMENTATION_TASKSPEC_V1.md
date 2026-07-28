# SERVICE_1_WEB_COLUMN_CONFIRMATION_INTAKE_BOUNDARY_IMPLEMENTATION_TASKSPEC_V1

## VERDICT

```text
TASKSPEC_READY_FOR_MINIMAL_PYTHON_BOUNDARY_IMPLEMENTATION
WEB_OWNER_COLUMN_CONFIRMATION_REAL_FLOW: STILL_NOT_CERTIFIED
RUNTIME_AUTHORIZED: false
REEXECUTION_AUTHORIZED: false
RECALCULATION_AUTHORIZED: false
DELIVERY_AUTHORIZED: false
DIAGNOSIS_GENERATED: false
```

This TaskSpec authorizes only the next implementation slice for the pure Python web-intake boundary. It does not authorize UI wiring, HTTP serving, landing changes, runner execution, dry-run, diagnosis, or delivery.

## GOVERNING CHAIN

```text
docs/current/SERVICE_1_WEB_OWNER_COLUMN_CONFIRMATION_REAL_FLOW_TASKSPEC_V1.md
-> docs/current/SERVICE_1_WEB_COLUMN_CONFIRMATION_INTAKE_BOUNDARY_V1_MODULECONTRACT.md
-> this TaskSpec
```

The current state remains:

```text
WEB_OWNER_COLUMN_CONFIRMATION_REAL_FLOW_NOT_CERTIFIED
```

A successful implementation of this TaskSpec may certify only the pure Python boundary behavior. It still will not certify the online web flow until a real web upload path is wired and evidenced separately.

## PURPOSE

Implement a narrow pure Python boundary that receives a real uploaded XLSX source from a web layer and converts it into an owner-facing column-confirmation intake packet using PymIA canonical readers.

Allowed shape:

```text
uploaded XLSX bytes or safe local XLSX path
-> controlled local materialization if bytes are supplied
-> read_service_1_xlsx_structure_v1()
-> build_service_1_xlsx_structure_extraction_to_adapter_chain_v1()
-> owner-facing question packet summary
-> safety-preserving boundary result
```

For CASE_001, the boundary must assert the expected question count of 12 before it can report readiness for owner confirmation.

## FILES AUTHORIZED

Production file:

```text
pymia/smartpyme/service_1_web_column_confirmation_intake_boundary_v1.py
```

Test file:

```text
tests/smartpyme/test_service_1_web_column_confirmation_intake_boundary_v1.py
```

No other files are authorized by this TaskSpec except a future evidence checkpoint after tests pass.

## PUBLIC API REQUIRED

The module must expose:

```text
build_service_1_web_column_confirmation_intake_boundary_v1()
Service1WebColumnConfirmationIntakeBoundaryResultV1
```

Required inputs:

| Input | Required | Rule |
|---|---:|---|
| `uploaded_file_name` | yes | Non-empty owner-visible XLSX name. |
| `case_id` | yes | For CASE_001, must identify the governed CASE_001 case. |
| `tenant_id` | yes | Metadata only. |
| `intake_id` | yes | Metadata only. |
| `uploaded_file_bytes` | conditional | Exactly one of bytes/path must be supplied. |
| `uploaded_file_path` | conditional | Exactly one of bytes/path must be supplied. |
| `metadata` | no | Dict or None only. |

The function must reject calls that provide both bytes and path, or neither.

## OUTPUT REQUIRED

The result dataclass must include at minimum:

```text
schema_version
service_name
status
case_id
tenant_id
intake_id
uploaded_file_name
canonical_reader_used
extracted_file_name
column_confirmation_status
owner_question_packet
expected_question_count
actual_question_count
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

Required statuses:

```text
READY_FOR_OWNER_CONFIRMATION
BLOCKED_UPLOAD_INVALID
BLOCKED_CANONICAL_READER_FAILED
BLOCKED_QUESTION_COUNT_MISMATCH
BLOCKED_UNCERTIFIED_BROWSER_ONLY_FLOW
```

This slice must not return `OWNER_CONFIRMATIONS_CAPTURED`; answer capture belongs to a later evidence cycle after real owner input exists.

## IMPLEMENTATION RULES

The implementation must:

1. Validate the upload boundary and file name.
2. Accept only `.xlsx` for certified flow unless an existing canonical reader proves another format is supported.
3. If bytes are supplied, materialize them in a controlled temporary file for canonical reader use.
4. Call `read_service_1_xlsx_structure_v1()` as the certified structure reader.
5. Call `build_service_1_xlsx_structure_extraction_to_adapter_chain_v1()` with the extracted structure.
6. Derive the owner-facing question packet from the existing chain result/display data.
7. For CASE_001, require exactly 12 owner-facing column-confirmation questions.
8. Preserve all safety flags as false.
9. Delete or isolate temporary materialization according to testable local safety rules.
10. Expose `to_dict()` without leaking runtime authority.

The implementation must not use SheetJS, `landing/`, browser output, or JavaScript-generated JSON as certified source of truth.

## FORBIDDEN BEHAVIOR

The implementation must not:

```text
serve HTTP
modify landing/
call runner
call SaaS/API/storage worker surfaces
perform dry-run
calculate or recalculate business values
generate diagnosis
generate delivery
persist production state
capture owner answers as evidence
simulate owner answers
use LLM decisions
apply answers to ColumnConfirmationMatrix
create OwnerRectifiedEvidenceProfile
```

## ACCEPTANCE TESTS REQUIRED

The test file must cover at least:

1. **Happy path from real XLSX fixture/path**
   - canonical reader is used;
   - status is `READY_FOR_OWNER_CONFIRMATION` when question count matches;
   - safety flags are false.

2. **Bytes upload path**
   - bytes are materialized only through the boundary;
   - canonical reader still drives extraction.

3. **No source / dual source rejected**
   - neither bytes nor path -> `BLOCKED_UPLOAD_INVALID` or `ValueError`;
   - both bytes and path -> `BLOCKED_UPLOAD_INVALID` or `ValueError`.

4. **Invalid extension blocked**
   - browser-only or non-XLSX source cannot become certified.

5. **Canonical reader failure blocks**
   - status `BLOCKED_CANONICAL_READER_FAILED`;
   - no runtime/delivery/diagnosis flags flip.

6. **CASE_001 question count lock**
   - if expected 12 is not met, status `BLOCKED_QUESTION_COUNT_MISMATCH`.

7. **No answer capture in this slice**
   - captured answer count remains 0;
   - no owner answers are treated as evidence.

8. **Forbidden dependency guard**
   - no imports/calls to runner, delivery, diagnostic core, API worker, storage worker, landing, or external LLM SDKs.

9. **Output contract**
   - `to_dict()` includes required fields and all safety flags false.

## VALIDATION COMMANDS

Run from the repo root:

```text
python -m pytest tests/smartpyme/test_service_1_web_column_confirmation_intake_boundary_v1.py -q
python -m pytest tests/smartpyme/test_service_1_xlsx_structure_extraction_to_adapter_chain_v1.py tests/smartpyme/test_service_1_web_column_confirmation_closed_loop_smoke_v1.py -q
```

If these pass, the implementation may be documented as:

```text
PURE_PYTHON_BOUNDARY_IMPLEMENTED_AND_TESTED
WEB_OWNER_COLUMN_CONFIRMATION_REAL_FLOW_STILL_NOT_CERTIFIED
```

## STOP CONDITIONS

Stop before or during implementation if:

```text
CASE_001 question count cannot be proven as 12
only browser/SheetJS data is available
implementation needs landing changes
implementation needs HTTP serving
implementation needs simulated owner answers
implementation would unlock runtime/dry-run/diagnosis/delivery
implementation would require LLM authority
```

## NEXT STEP AFTER PASS

After implementation and tests pass, create an evidence checkpoint documenting:

```text
pure Python boundary implemented/tested
real online web flow still not certified
owner answers still required for CASE_001 evidence cycle
```

Only after that may a separate cycle consider UI/web wiring. That later cycle must still keep runtime, dry-run, diagnosis, and delivery blocked.
