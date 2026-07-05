# SERVICE_1_SAAS_JOB_TO_PIPELINE_REQUEST_ADAPTER_CONTRACT_V1

## VERDICT

```text
CONTRACT_CREATED
ROLE: ADAPTER / READ_MODEL ONLY
IMPLEMENTATION_READY: NO
CODE_AUTHORIZED: NO
```

## SCOPE

```text
DOC ONLY
NO CODE
NO TESTS
NO RUNTIME
NO NEW GATE
NO EXECUTION AUTHORIZATION
```

## PURPOSE

Define the minimum adapter boundary between existing SaaS job orchestration candidates and existing pipeline request gates.

This contract does not create a new sovereign orchestration gate.
It only specifies how to reuse existing modules without duplicating their authority.

## SOURCE_CONTEXT

```text
SERVICE_1_AUTONOMOUS_SAAS_ORCHESTRATION_TRACE_REUSE_MAP_V1
```

Critical missing bridge:

```text
SAAS_JOB_TO_EXPLICIT_TOOL_REQUEST_ADAPTER
```

## PROPOSED_MODULE_NAME

```text
service_1_saas_job_to_pipeline_request_adapter_v1.py
```

## PROPOSED_FUNCTION_NAME

```text
build_service_1_saas_job_to_pipeline_request_adapter_v1
```

## RESPONSIBILITY

```text
Consume a SaaS job orchestration candidate and pre-existing explicit tool request candidates.
Validate lineage and job kind.
Produce input payload for the existing explicit_request_to_pipeline_request_gate only.

The adapter must not produce complete pipeline_execution_gate_input in V1.
That second-stage input requires real output from explicit_request_to_pipeline_request_gate.
```

## NON_RESPONSIBILITIES

```text
Do not create tool requests from raw owner text.
Do not select tools.
Do not infer diagnosis.
Do not authorize execution.
Do not call pipeline.
Do not call runner.
Do not read/write files.
Do not expose API.
Do not upload files.
Do not persist state.
Do not create queues/workers.
Do not publish delivery.
Do not bypass human review.
```

## INPUTS

```text
saas_job_orchestration_status: str
saas_job_orchestration_candidate: dict | None
explicit_request_status: str
explicit_tool_request_candidate: list[dict]
allowed_tool_refs: list[str]
case_truth_status: str | None
missing_inputs: list[str]
unsafe_flags: list[str]
notes: list[str]
```

## REQUIRED_SOURCE_STATUSES

```text
saas_job_orchestration_status = SAAS_JOB_ORCHESTRATION_CANDIDATE_READY
explicit_request_status = EXPLICIT_REQUEST_CANDIDATE_READY
```

## ALLOWED_JOB_KINDS_FOR_V1

```text
INITIAL_FILE_INTAKE_PROCESSING_CANDIDATE
AUTONOMOUS_RERUN_PROCESSING_CANDIDATE
```

Excluded for V1:

```text
OWNER_DELIVERY_PACKET_REFRESH_CANDIDATE
```

Reason:

```text
Owner delivery packet refresh belongs after runner/release/packet path, not before pipeline request assembly.
```

## OUTPUT

```text
schema_version
service_name
status
explicit_to_pipeline_gate_input
pipeline_execution_gate_input_required_later
blocked_reason
runtime_authorized=false
execution_authorized=false
pipeline_authorized=false
runner_authorized=false
delivery_authorized=false
notes
```

## STATUS_VALUES

```text
ADAPTER_INPUTS_READY
BLOCKED_MISSING_SAAS_JOB
BLOCKED_INVALID_SAAS_JOB
BLOCKED_UNSUPPORTED_JOB_KIND
BLOCKED_MISSING_EXPLICIT_REQUESTS
BLOCKED_UNSAFE_FLAGS
BLOCKED_MISSING_INPUTS
UNKNOWN
```

## OUTPUT_MAPPING

### explicit_to_pipeline_gate_input

```text
explicit_request_status -> explicit_request_status
explicit_tool_request_candidate -> explicit_tool_request_candidate
allowed_tool_refs -> allowed_tool_refs
final_execution_gate_status -> CLOSED_NOT_EXECUTABLE
pipeline_request_policy -> SAAS_JOB_ADAPTER_V1
```

### pipeline_execution_gate_input_required_later

```text
Not produced by this adapter in V1.
```

Reason:

```text
pipeline_candidate_status and pipeline_tool_requests must come from actual explicit_request_to_pipeline_request_gate output.
The adapter must not fabricate pipeline_tool_requests or pre-authorize execution.
```

## LINEAGE_RULES

```text
1. SaaS job candidate must be SERVICE_1.
2. SaaS job candidate must include owner_ref and case_ref.
3. Explicit request candidates must not be executable.
4. Explicit request candidates must use request_kind=CANDIDATE_ONLY.
5. Each explicit request tool_ref must be allowlisted.
6. If source refs are present, owner/case/session lineage must not conflict.
```

## SAFETY_FLAGS

Always false:

```text
runtime_authorized
execution_authorized
pipeline_authorized
runner_authorized
delivery_authorized
api_exposed
worker_authorized
queue_authorized
storage_write_authorized
mutation_authorized
llm_authorized
```

## ACCEPTANCE_TESTS_REQUIRED_BEFORE_CODE

```text
1. Blocks missing SaaS job candidate.
2. Blocks SaaS job status not ready.
3. Blocks unsupported job kind.
4. Blocks missing explicit requests.
5. Blocks executable explicit request candidate.
6. Blocks non-allowlisted tool_ref.
7. Blocks unsafe_flags.
8. Blocks missing_inputs.
9. Produces explicit_to_pipeline_gate_input with CLOSED_NOT_EXECUTABLE.
10. Does not produce complete pipeline_execution_gate_input.
11. Does not fabricate pipeline_tool_requests.
12. Does not import runner, pipeline, IO, FastAPI, requests, openpyxl, pandas, LLM packages.
13. Does not authorize execution or delivery.
```

## FORBIDDEN_IMPORTS

```text
openai
anthropic
langchain
langgraph
pydantic_ai
fastapi
requests
httpx
openpyxl
pandas
pathlib
subprocess
service_1_pipeline_v1
service_1_autonomous_pipeline_runner_v1
```

## NEXT_ALLOWED_STEP

```text
SERVICE_1_SAAS_JOB_TO_PIPELINE_REQUEST_ADAPTER_TASKSPEC_V1
DOC ONLY
```

## FINAL_STATUS

```text
SERVICE_1_SAAS_JOB_TO_PIPELINE_REQUEST_ADAPTER_CONTRACT_V1: CREATED
IMPLEMENTATION_READY: NO
```
