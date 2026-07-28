# S1_OWNER_QUESTION_ROUTER_V1 Contract Design

This document defines the technical contract for `S1_OWNER_QUESTION_ROUTER_V1`.

Its purpose is to leave Phase E.3 implementation-ready as a **pure router** that consumes E.1 bridge + E.2 guarded response candidate, without gaining runtime, truth, tool, or delivery authority.

## Quick path

1. Consume a **READY** `S1_CONVERSATIONAL_OWNER_BRIDGE_CONTRACT_V1` candidate.
2. Consume a **READY** `S1_LLM_GUARDED_RESPONSE_GATE_V1` candidate.
3. Deterministically route the owner interaction into one safe conversational route candidate.

## Design decision

`S1_OWNER_QUESTION_ROUTER_V1` is a **pure routing contract**.

It does **not**:

- call OpenAI;
- call Pydantic AI;
- run a chatbot;
- execute tools;
- trigger pipeline or runner;
- mutate `case_truth`;
- authorize rerun;
- publish a client response;
- expose runtime SaaS or API behavior;
- read Excel, files, or artifacts;
- invent diagnosis or certainty;
- create a parallel path outside E.1 + E.2.

It only decides:

- which safe conversational route applies;
- whether the interaction should continue as explanation, clarification capture, correction capture, evidence request, next-step explanation, delivery summary explanation, rerun request capture, or blocked unsupported route.

## Relationship with E.1 bridge

E.1 remains the authority for:

- `owner_ref`
- `case_ref`
- `source_session_ref`
- `owner_intent`
- `next_conversational_action`
- `allowed_response_scope`
- `forbidden_response_scope`
- `safe_context_refs_for_future_llm`

E.3 must not:

- recompute `owner_intent`;
- widen response scope;
- override bridge safety boundaries;
- create a route that contradicts E.1 `next_conversational_action`.

## Relationship with E.2 guarded gate

E.2 remains the authority for:

- whether the proposed conversational response candidate is safe;
- which `applied_response_scope` survived validation;
- which safe refs are cited;
- whether the candidate stayed inside deterministic boundaries.

E.3 must not:

- bypass E.2;
- route a blocked guarded candidate;
- re-authorize blocked scopes;
- use free text alone as authority.

E.3 consumes E.2 and produces a **route candidate**, not a final response.

## Canonical constants

```text
schema_version = S1_OWNER_QUESTION_ROUTER_V1
service_name = SERVICE_1
router_kind = OWNER_QUESTION_ROUTE_CANDIDATE
source_bridge_kind = CONVERSATIONAL_OWNER_BRIDGE_CANDIDATE
source_guarded_kind = GUARDED_LLM_RESPONSE_CANDIDATE
```

## Input contract

```python
class Service1OwnerQuestionRouterInputV1(TypedDict):
    conversational_owner_bridge_candidate: dict[str, object] | None
    guarded_llm_response_candidate: dict[str, object] | None
    notes: list[str]
```

### Required bridge fields

Minimum required E.1 fields:

```python
{
    "bridge_kind": "CONVERSATIONAL_OWNER_BRIDGE_CANDIDATE",
    "owner_ref": str,
    "case_ref": str,
    "service_name": "SERVICE_1",
    "source_session_ref": str,
    "owner_intent": str,
    "next_conversational_action": str,
    "allowed_response_scope": list[str],
    "forbidden_response_scope": list[str],
    "safe_context_refs_for_future_llm": dict[str, str],
    "llm_authorized": False,
    "pydantic_ai_authorized": False,
    "prompt_runtime_authorized": False,
    "chatbot_authorized": False,
    "tool_authorized": False,
    "pipeline_authorized": False,
    "runner_authorized": False,
    "mutation_authorized": False,
    "runtime_authorized": False,
    "api_exposed": False,
}
```

### Required guarded-gate fields

Minimum required E.2 fields:

```python
{
    "gate_kind": "GUARDED_LLM_RESPONSE_CANDIDATE",
    "owner_ref": str,
    "case_ref": str,
    "service_name": "SERVICE_1",
    "source_session_ref": str,
    "owner_intent": str,
    "next_conversational_action": str,
    "response_text_candidate": str,
    "allowed_response_scope": list[str],
    "forbidden_response_scope": list[str],
    "applied_response_scope": list[str],
    "cited_safe_context_refs": dict[str, str],
    "follow_up_question_candidates": list[str],
    "missing_evidence_request_candidates": list[str],
    "clarification_capture_candidates": list[str],
    "correction_capture_candidates": list[str],
    "owner_visible_disclaimer_candidates": list[str],
    "client_delivery_authorized": False,
    "llm_authorized": False,
    "pydantic_ai_authorized": False,
    "prompt_runtime_authorized": False,
    "chatbot_authorized": False,
    "tool_authorized": False,
    "pipeline_authorized": False,
    "runner_authorized": False,
    "mutation_authorized": False,
    "runtime_authorized": False,
    "api_exposed": False,
}
```

## Output contract

```python
class Service1OwnerQuestionRouteCandidateV1(TypedDict):
    router_kind: Literal["OWNER_QUESTION_ROUTE_CANDIDATE"]
    owner_ref: str
    case_ref: str
    service_name: Literal["SERVICE_1"]
    source_session_ref: str
    owner_intent: str
    next_conversational_action: str
    selected_route: str
    route_family: str
    route_reason: str
    route_response_text_candidate: str
    route_follow_up_question_candidates: list[str]
    route_missing_evidence_request_candidates: list[str]
    route_clarification_capture_candidates: list[str]
    route_correction_capture_candidates: list[str]
    route_owner_visible_disclaimer_candidates: list[str]
    cited_safe_context_refs: dict[str, str]
    allowed_response_scope: list[str]
    forbidden_response_scope: list[str]
    client_delivery_authorized: Literal[False]
    llm_authorized: Literal[False]
    pydantic_ai_authorized: Literal[False]
    prompt_runtime_authorized: Literal[False]
    chatbot_authorized: Literal[False]
    tool_authorized: Literal[False]
    pipeline_authorized: Literal[False]
    runner_authorized: Literal[False]
    mutation_authorized: Literal[False]
    runtime_authorized: Literal[False]
    api_exposed: Literal[False]
```

```python
class Service1OwnerQuestionRouterResultV1(TypedDict):
    schema_version: str
    service_name: str
    status: str
    owner_question_route_candidate: Service1OwnerQuestionRouteCandidateV1 | None
    blocked_reason: str | None
    client_delivery_authorized: Literal[False]
    llm_authorized: Literal[False]
    pydantic_ai_authorized: Literal[False]
    prompt_runtime_authorized: Literal[False]
    chatbot_authorized: Literal[False]
    tool_authorized: Literal[False]
    pipeline_authorized: Literal[False]
    runner_authorized: Literal[False]
    mutation_authorized: Literal[False]
    runtime_authorized: Literal[False]
    api_exposed: Literal[False]
    notes: list[str]
```

## Allowed owner-question routes

The router may emit only these canonical routes:

```text
ROUTE_STATUS_EXPLANATION
ROUTE_STATE_EXPLANATION
ROUTE_OWNER_CLARIFICATION_CAPTURE
ROUTE_OWNER_CORRECTION_CAPTURE
ROUTE_RERUN_REQUEST_CAPTURE
ROUTE_NEXT_STEP_EXPLANATION
ROUTE_DELIVERY_SUMMARY_EXPLANATION
ROUTE_MISSING_EVIDENCE_REQUEST
ROUTE_BLOCK_UNSUPPORTED_MESSAGE
```

## Route mapping

| Bridge intent / action | Allowed route |
|---|---|
| `OWNER_ASKS_STATUS` + `PREPARE_STATUS_EXPLANATION_CANDIDATE` | `ROUTE_STATUS_EXPLANATION` |
| `OWNER_ASKS_EXPLANATION` + `PREPARE_STATE_EXPLANATION_CANDIDATE` | `ROUTE_STATE_EXPLANATION` |
| `OWNER_PROVIDES_CLARIFICATION` + `PREPARE_OWNER_CLARIFICATION_CAPTURE_CANDIDATE` | `ROUTE_OWNER_CLARIFICATION_CAPTURE` |
| `OWNER_PROVIDES_CORRECTION` + `PREPARE_OWNER_CORRECTION_CAPTURE_CANDIDATE` | `ROUTE_OWNER_CORRECTION_CAPTURE` |
| `OWNER_REQUESTS_RERUN` + `PREPARE_RERUN_REQUEST_CANDIDATE` | `ROUTE_RERUN_REQUEST_CAPTURE` |
| `OWNER_ASKS_NEXT_STEP` + `PREPARE_NEXT_STEP_EXPLANATION_CANDIDATE` | `ROUTE_NEXT_STEP_EXPLANATION` |
| `OWNER_ASKS_DELIVERY_SUMMARY` + `PREPARE_DELIVERY_SUMMARY_CANDIDATE` | `ROUTE_DELIVERY_SUMMARY_EXPLANATION` |
| Any guarded candidate with applied scope including `ask_for_missing_evidence` | `ROUTE_MISSING_EVIDENCE_REQUEST` |
| `OWNER_PROVIDES_UNSUPPORTED_MESSAGE` or `UNKNOWN` with `BLOCK_UNSUPPORTED_MESSAGE` | `ROUTE_BLOCK_UNSUPPORTED_MESSAGE` |

## Route families

For implementation clarity, each selected route should belong to one family:

```text
EXPLANATION
CAPTURE
REQUEST
BLOCK
```

Recommended family mapping:

| Route | Family |
|---|---|
| `ROUTE_STATUS_EXPLANATION` | `EXPLANATION` |
| `ROUTE_STATE_EXPLANATION` | `EXPLANATION` |
| `ROUTE_NEXT_STEP_EXPLANATION` | `EXPLANATION` |
| `ROUTE_DELIVERY_SUMMARY_EXPLANATION` | `EXPLANATION` |
| `ROUTE_OWNER_CLARIFICATION_CAPTURE` | `CAPTURE` |
| `ROUTE_OWNER_CORRECTION_CAPTURE` | `CAPTURE` |
| `ROUTE_RERUN_REQUEST_CAPTURE` | `REQUEST` |
| `ROUTE_MISSING_EVIDENCE_REQUEST` | `REQUEST` |
| `ROUTE_BLOCK_UNSUPPORTED_MESSAGE` | `BLOCK` |

## Blocked routes

The router must never emit routes equivalent to:

```text
ROUTE_TOOL_EXECUTION
ROUTE_PIPELINE_EXECUTION
ROUTE_RUNNER_EXECUTION
ROUTE_CASE_MUTATION
ROUTE_AUTONOMOUS_RERUN_AUTHORIZATION
ROUTE_CLIENT_PUBLICATION
ROUTE_RUNTIME_START
ROUTE_API_HANDOFF
ROUTE_HUMAN_OPERATOR_IMPERSONATION
ROUTE_LEGAL_TAX_ACCOUNTING_CERTAINTY
```

## What the router may route

The router may route:

- owner-facing explanation of existing verified state;
- explanation of current safe next step;
- delivery-summary explanation from an existing candidate;
- clarification capture path;
- correction capture path;
- missing-evidence request path;
- rerun-request capture path;
- unsupported/unknown blocking conversational path.

## What the router must never execute

The router must never:

- execute a tool;
- call pipeline or runner;
- mutate case truth;
- authorize rerun or runtime;
- publish to client;
- open SaaS/API execution;
- read files or Excel;
- decide legal/tax/accounting certainty;
- create a route not grounded in E.1 + E.2.

## Statuses

Recommended result statuses:

```text
OWNER_QUESTION_ROUTE_CANDIDATE_READY
BLOCKED_MISSING_BRIDGE
BLOCKED_INVALID_BRIDGE
BLOCKED_MISSING_GUARDED_CANDIDATE
BLOCKED_INVALID_GUARDED_CANDIDATE
BLOCKED_IDENTITY_MISMATCH
BLOCKED_ROUTE_NOT_ALLOWED
BLOCKED_NEXT_ACTION_MISMATCH
BLOCKED_UNSAFE_FLAGS
UNKNOWN
```

## Meaning

| Status | Meaning |
|---|---|
| `OWNER_QUESTION_ROUTE_CANDIDATE_READY` | A safe deterministic route candidate was selected |
| `BLOCKED_MISSING_BRIDGE` | No E.1 bridge candidate was provided |
| `BLOCKED_INVALID_BRIDGE` | Bridge is malformed or not a valid E.1 candidate |
| `BLOCKED_MISSING_GUARDED_CANDIDATE` | No E.2 guarded candidate was provided |
| `BLOCKED_INVALID_GUARDED_CANDIDATE` | Guarded candidate is malformed or wrong kind/service |
| `BLOCKED_IDENTITY_MISMATCH` | Owner/case/session/action identity between E.1 and E.2 does not match |
| `BLOCKED_ROUTE_NOT_ALLOWED` | No safe route can be selected from the combined bridge + guarded inputs |
| `BLOCKED_NEXT_ACTION_MISMATCH` | The route would contradict bridge/guarded next action |
| `BLOCKED_UNSAFE_FLAGS` | Any dangerous/runtime flag is not `False` |
| `UNKNOWN` | Reserved fallback |

## Block reasons

Recommended canonical block reasons:

```text
conversational_owner_bridge_candidate_required
bridge_kind_must_be_conversational_owner_bridge_candidate
bridge_service_name_must_be_service_1
bridge_owner_ref_required
bridge_case_ref_required
bridge_next_conversational_action_required
bridge_flags_must_be_false
guarded_llm_response_candidate_required
guarded_candidate_kind_must_be_guarded_llm_response_candidate
guarded_candidate_service_name_must_be_service_1
guarded_candidate_owner_ref_required
guarded_candidate_case_ref_required
guarded_candidate_applied_response_scope_required
guarded_candidate_flags_must_be_false
owner_ref_must_match_between_bridge_and_guarded_candidate
case_ref_must_match_between_bridge_and_guarded_candidate
source_session_ref_must_match_between_bridge_and_guarded_candidate
next_conversational_action_must_match_between_bridge_and_guarded_candidate
selected_route_not_allowed_for_bridge_intent
selected_route_not_allowed_for_guarded_scope
blocked_route_family_detected
```

## Flags that must always be false

These flags must be `False` in:

- the bridge input;
- the guarded-gate input;
- the router result;
- the route candidate.

Canonical flags:

```text
client_delivery_authorized
llm_authorized
pydantic_ai_authorized
prompt_runtime_authorized
chatbot_authorized
tool_authorized
pipeline_authorized
runner_authorized
mutation_authorized
runtime_authorized
api_exposed
```

## Minimal validation rules

E.3 implementation should block unless all of these are true:

1. Bridge candidate exists and is valid.
2. Guarded candidate exists and is valid.
3. `owner_ref` matches between E.1 and E.2.
4. `case_ref` matches between E.1 and E.2.
5. `source_session_ref` matches between E.1 and E.2.
6. `next_conversational_action` matches between E.1 and E.2.
7. All dangerous flags remain `False`.
8. The selected route is allowed by bridge intent.
9. The selected route is allowed by guarded candidate `applied_response_scope`.
10. No blocked route family is selected.

## Non-goals

This router does **not** include:

- actual model invocation;
- actual response publishing;
- case patching;
- rerun approval;
- tool/router orchestration outside conversation;
- UI/API channel delivery;
- human review signoff;
- persistence.

## Ready-for-implementation criterion

E.3 is design-ready when implementation can preserve this invariant:

> Only a route grounded in E.1 intent boundaries and E.2 guarded response safety may continue the conversational flow, and that route still has zero runtime authority.

If that invariant is preserved, `S1_OWNER_QUESTION_ROUTER_V1` can be implemented as the final pure conversational slice closing Phase E without creating a parallel system.
