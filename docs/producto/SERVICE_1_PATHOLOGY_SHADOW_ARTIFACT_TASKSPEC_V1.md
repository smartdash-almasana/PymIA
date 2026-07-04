# SERVICE_1_PATHOLOGY_SHADOW_ARTIFACT_TASKSPEC_V1

## VERDICT

```text
TASKSPEC_AUTHORIZED_FOR_TEST_FIRST_IMPLEMENTATION_CANDIDATE_ONLY
```

## DOCUMENT_STATUS

```text
Type: TASKSPEC
Service: SERVICE_1 / SmartPyme
Parent contract: SERVICE_1_PATHOLOGY_SHADOW_ARTIFACT_MODULE_CONTRACT_V1
Runtime impact: FUTURE_SHADOW_ONLY_IF_IMPLEMENTED
Code impact: NONE_IN_THIS_DOCUMENT
Tests impact: NONE_IN_THIS_DOCUMENT
Implementation authorized by this document: NO
```

This TaskSpec defines the smallest safe future implementation slice for the pathology shadow artifact.

It does not implement runtime.

It does not modify code.

It does not authorize active routing, advisory diagnosis, final diagnosis, delivery changes, or tool execution.

## OBJECTIVE

Define a test-first implementation candidate for:

```text
Service1PathologyShadowArtifactBuilderV1
```

The future candidate must build an observational JSON-compatible payload equivalent to:

```text
pathology_candidates.json
```

The payload must remain non-binding and preserve:

```text
runtime_decision=NO_EFFECT
diagnosis_authorized=False
routing_authorized=False
tool_selection_authorized=False
delivery_modification_authorized=False
```

## SOURCE_DOCUMENTS

```text
docs/producto/SERVICE_1_PATHOLOGY_SHADOW_ARTIFACT_MODULE_CONTRACT_V1.md
docs/producto/SERVICE_1_PATHOLOGY_SHADOW_MODE_V1.md
docs/producto/SERVICE_1_PATHOLOGY_CATALOG_INTEGRATION_V1.md
docs/producto/SERVICE_1_RUNTIME_GOVERNANCE_V1.md
docs/current/ARCHITECTURE_BOUNDARY.md
docs/current/SAAS_AUTONOMY_TARGET.md
docs/doctrina/organizacional/PYMIA_ORGANIZATIONAL_PATHOLOGY_CATALOG_V0.json
```

## PROPOSED_FILES_IF_LATER_AUTHORIZED

Runtime candidate:

```text
PymIA-Live/pymia/smartpyme/service_1_pathology_shadow_artifact_v1.py
```

Test candidate:

```text
PymIA-Live/tests/smartpyme/test_service_1_pathology_shadow_artifact_v1.py
```

No other files are authorized by this TaskSpec.

## EXPLICIT_NON_GOALS

The future implementation candidate must not:

```text
- write files to disk;
- create a delivery folder;
- modify any existing manifest;
- import or call the live pipeline;
- import or call storage;
- import or call LLM clients;
- import or call HTTP/web/API layers;
- execute any deterministic skill;
- create evidence requests;
- alter case state;
- alter routing;
- alter release gates;
- generate owner-facing diagnosis;
- promote candidates to confirmed pathology;
- change ACTIVE_ROADMAP;
- change AGENTS.md;
- edit the pathology catalog;
- touch Service 2.
```

## FUTURE_PUBLIC_FUNCTION

If later authorized, expose exactly one public function:

```text
build_service_1_pathology_shadow_artifact_v1()
```

Recommended call shape:

```python
build_service_1_pathology_shadow_artifact_v1(
    *,
    case_id: str,
    catalog_snapshot: dict,
    feature_flag_state: str,
    case_ref: str | None = None,
    owner_pain_text: str | None = None,
    anamnesis_signals: list[str] | None = None,
    case_metadata: dict | None = None,
    available_evidence_refs: list[str] | None = None,
    metadata: dict | None = None,
) -> dict
```

The future function must return a plain JSON-serializable `dict`.

No dataclass/Pydantic requirement is imposed in this first slice unless a later contract authorizes it.

## INPUT_FIXTURES_REQUIRED_FOR_TESTS

The future test module must define local inline fixtures only.

Do not depend on external fixture files.

### Minimal catalog fixture

The minimal catalog fixture must include at least:

```python
{
    "catalogo_patologias_smartpyme_v0": {
        "version": "0.1",
        "estado": "DRAFT_CANONICAL_CANDIDATE",
        "dominios": {
            "rentabilidad": [
                {
                    "id": "REN_001",
                    "nombre": "margen_invisible",
                    "descripcion": "El negocio factura pero no sabe qué productos, clientes o canales dejan ganancia real.",
                    "sintomas": [
                        "vende mucho pero no gana"
                    ],
                    "senales_anamnesis": [
                        "vendo pero no sé si gano"
                    ],
                    "datos_minimos": [
                        "precio_venta",
                        "costo_unitario",
                        "comisiones"
                    ],
                    "formulas_asociadas": [
                        "Margen bruto por producto",
                        "Margen neto"
                    ]
                }
            ]
        }
    }
}
```

### Minimal owner signal fixture

```text
vendo pero no sé si gano
```

### Non-matching owner signal fixture

```text
quiero ordenar los nombres de clientes duplicados
```

## REQUIRED_BEHAVIOR

### 1. OFF flag

Input:

```text
feature_flag_state=OFF
```

Required output:

```text
status=SKIPPED
blocked_reason=FEATURE_FLAG_OFF
runtime_decision=NO_EFFECT
candidate_count=0
```

### 2. SHADOW_ONLY with matching signal

Input:

```text
feature_flag_state=SHADOW_ONLY
owner_pain_text contains a catalog anamnesis signal
```

Required output:

```text
status=GENERATED
candidate_count=1
detected_candidates[0].pathology_id=REN_001
detected_candidates[0].confidence=candidate
detected_candidates[0].missing_evidence includes catalog datos_minimos
detected_candidates[0].suggested_formulas includes catalog formulas_asociadas
```

Required invariant:

```text
runtime_decision=NO_EFFECT
diagnosis_authorized=False
routing_authorized=False
tool_selection_authorized=False
delivery_modification_authorized=False
```

### 3. SHADOW_ONLY with non-matching signal

Input:

```text
feature_flag_state=SHADOW_ONLY
owner_pain_text does not match catalog signals
```

Required output:

```text
status=NO_CANDIDATES
blocked_reason=None
candidate_count=0
```

### 4. SHADOW_ONLY with no signals

Input:

```text
feature_flag_state=SHADOW_ONLY
owner_pain_text=None
anamnesis_signals=[]
case_metadata={}
available_evidence_refs=[]
```

Required output:

```text
status=BLOCKED
blocked_reason=NO_SIGNALS_AVAILABLE
candidate_count=0
```

### 5. Uncontracted promotion states

Input:

```text
feature_flag_state in ADVISORY, ROUTING_CANDIDATE, ACTIVE
```

Required output:

```text
status=BLOCKED
blocked_reason=FEATURE_FLAG_STATE_UNCONTRACTED
runtime_decision=NO_EFFECT
candidate_count=0
```

### 6. Missing catalog

Input:

```text
catalog_snapshot=None or empty
```

Required output:

```text
status=BLOCKED
blocked_reason=CATALOG_MISSING
candidate_count=0
```

### 7. Unsupported catalog status

Input:

```text
catalog_snapshot.estado != DRAFT_CANONICAL_CANDIDATE
```

Required output:

```text
status=BLOCKED
blocked_reason=CATALOG_STATUS_UNSUPPORTED
candidate_count=0
```

### 8. Missing case_id

Input:

```text
case_id="" or None
```

Required output:

```text
status=BLOCKED
blocked_reason=CASE_ID_MISSING
candidate_count=0
```

## REQUIRED_OUTPUT_KEYS

Every output, including blocked/skipped outputs, must include:

```text
schema_version
service_name
case_id
case_ref
mode
feature_flag
feature_flag_state
status
blocked_reason
runtime_decision
diagnosis_authorized
routing_authorized
tool_selection_authorized
delivery_modification_authorized
candidate_count
detected_candidates
missing_evidence_global
metadata
```

## MATCHING_RULES

Allowed first-slice matching:

```text
- lowercase comparison;
- accent-insensitive normalization if implemented with standard library only;
- substring match against senales_anamnesis;
- substring match against sintomas;
- match against owner_pain_text and anamnesis_signals only.
```

Not required in this first slice:

```text
- fuzzy matching;
- semantic embeddings;
- LLM interpretation;
- scoring;
- ranking;
- financial estimation;
- risk calculation;
- tool selection.
```

## ACCEPTANCE_TESTS_REQUIRED

The future test file must include at least these tests:

```text
test_off_flag_skips_with_no_effect_payload
test_shadow_only_matching_owner_pain_generates_candidate
test_shadow_only_non_matching_owner_pain_returns_no_candidates
test_shadow_only_without_signals_blocks
test_uncontracted_promotion_states_are_blocked
test_missing_catalog_blocks
test_unsupported_catalog_status_blocks
test_missing_case_id_blocks
test_draft_catalog_candidate_never_authorizes_diagnosis_or_routing
test_missing_evidence_and_formulas_are_catalog_passthrough_only
test_output_is_json_serializable
test_module_does_not_import_forbidden_runtime_dependencies
```

## FORBIDDEN_IMPORT_ASSERTION

The future forbidden-import test must inspect the source file and fail if it contains imports or references to:

```text
openai
anthropic
langchain
langgraph
requests
httpx
fastapi
fasthtml
storage
vertical_pipeline
pipeline_registration
operator_delivery_package
human_review
release_gate
bank_reconciliation
mercado_pago
invoice_collection
accounting_workpaper
```

The exact assertion can be implemented as a simple source text guard.

## IMPLEMENTATION_ORDER_IF_LATER_AUTHORIZED

If later authorized, implement in this order only:

```text
1. create failing acceptance tests;
2. create minimal pure module;
3. implement blocked/skipped payload builder;
4. implement catalog validation;
5. implement simple signal normalization;
6. implement simple candidate match;
7. verify JSON serializability;
8. verify forbidden import guard;
9. run only focal tests first;
10. run relevant smartpyme regression only if focal tests pass.
```

## COMMANDS_IF_LATER_AUTHORIZED

Focal test command:

```bash
cd E:\BuenosPasos\smartbridge\PymIA\PymIA-Live
python -m pytest tests/smartpyme/test_service_1_pathology_shadow_artifact_v1.py -q
```

Suggested narrow regression after focal PASS:

```bash
cd E:\BuenosPasos\smartbridge\PymIA\PymIA-Live
python -m pytest tests/smartpyme/test_service_1_pathology_shadow_artifact_v1.py tests/smartpyme/test_service_1_xlsx_runtime_bridge_contract_v1.py tests/smartpyme/test_service_1_xlsx_runtime_bridge_entrypoint_v1.py -q
```

No full-suite requirement is imposed by this TaskSpec.

## FILES_ALLOWED_IF_LATER_AUTHORIZED

```text
PymIA-Live/pymia/smartpyme/service_1_pathology_shadow_artifact_v1.py
PymIA-Live/tests/smartpyme/test_service_1_pathology_shadow_artifact_v1.py
```

## FILES_READ_ONLY_IF_LATER_AUTHORIZED

```text
docs/producto/SERVICE_1_PATHOLOGY_SHADOW_ARTIFACT_MODULE_CONTRACT_V1.md
docs/producto/SERVICE_1_PATHOLOGY_SHADOW_MODE_V1.md
docs/producto/SERVICE_1_PATHOLOGY_CATALOG_INTEGRATION_V1.md
docs/doctrina/organizacional/PYMIA_ORGANIZATIONAL_PATHOLOGY_CATALOG_V0.json
```

## FILES_FORBIDDEN_IF_LATER_AUTHORIZED

```text
AGENTS.md
docs/current/ACTIVE_ROADMAP.md
docs/current/ARCHITECTURE_BOUNDARY.md
docs/current/SAAS_AUTONOMY_TARGET.md
PymIA-Live/pymia/cli/vertical_slice.py
PymIA-Live/pymia/smartpyme/storage.py
PymIA-Live/pymia/smartpyme/service_1_pipeline_v1.py
PymIA-Live/pymia/smartpyme/service_1_operator_delivery_package_v1.py
PymIA-Live/pymia/smartpyme/service_1_autonomous_pipeline_runner_v1.py
PymIA-Live/pymia/smartpyme/service_1_autonomous_delivery_release_gate_v1.py
PymIA-Live/pymia/smartpyme/service_1_final_owner_release_decision_gate_v1.py
PymIA-Live/pymia/smartpyme/service_1_final_release_to_owner_handoff_contract_v1.py
PymIA-Live/pymia/smartpyme/service_2_*.py
```

## PASS_CRITERIA_IF_LATER_IMPLEMENTED

A future implementation may be called PASS only if:

```text
- all acceptance tests listed above exist;
- focal tests pass;
- no forbidden import appears;
- outputs preserve NO_EFFECT safety line;
- no files outside allowed list are modified;
- git diff confirms no runtime integration was added;
- no delivery/package/pipeline state is touched.
```

## STOP_CONDITIONS

Stop and report BLOCKED if any future implementer needs to:

```text
- alter pipeline routing;
- write artifact files to case folders;
- connect to delivery manifests;
- ask the owner for evidence;
- invoke an LLM;
- interpret final diagnosis;
- compute financial impact;
- rank pathology priorities;
- promote ADVISORY, ROUTING_CANDIDATE, or ACTIVE state;
- touch forbidden files.
```

## EXPECTED_REPORT_FORMAT_IF_LATER_IMPLEMENTED

```text
VERDICT:
FILES_CREATED:
FILES_MODIFIED:
TESTS_RUN:
TEST_RESULT:
RUNTIME_TOUCHED:
SAFETY_LINE:
BLOCKERS:
NEXT_STEP:
```

## FINAL_STATUS

```text
SERVICE_1_PATHOLOGY_SHADOW_ARTIFACT_TASKSPEC_V1: CREATED
RUNTIME_TOUCHED: NO
CODE_TOUCHED: NO
TESTS_RUN: NO
IMPLEMENTATION_AUTHORIZED: NO
NEXT_STEP: REVIEW_OR_IMPLEMENT_TEST_FIRST_ONLY_IF_EXPLICITLY_AUTHORIZED
```
