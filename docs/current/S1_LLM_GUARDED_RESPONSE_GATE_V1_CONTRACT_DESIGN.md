# S1_LLM_GUARDED_RESPONSE_GATE_V1 Contract Design

This document defines the technical contract for `S1_LLM_GUARDED_RESPONSE_GATE_V1`.

Its purpose is to make Phase E.2 implementation-ready without letting the conversational layer become a truth engine, runtime authority, tool executor, or delivery publisher.

## Quick path

1. Consume a **READY** `S1_CONVERSATIONAL_OWNER_BRIDGE_CONTRACT_V1` candidate.
2. Consume a **structured future-LLM response candidate** proposed from that bridge.
3. Deterministically allow or block the response candidate based on scope, refs, flags, and bridge alignment.

## Design decision

`S1_LLM_GUARDED_RESPONSE_GATE_V1` is a **pure validation and narrowing gate**.

It does **not**:

- call OpenAI;
- call Pydantic AI;
- run a chatbot;
- execute tools;
- trigger pipeline or runner;
- mutate `case_truth`;
- publish a client response;
- expose a SaaS runtime or API;
- read Excel or files;
- invent diagnostic/accounting/legal truth.

It only determines whether a future LLM-produced response candidate is **safe enough to remain a candidate**.

## Relationship with E.1 bridge

`S1_LLM_GUARDED_RESPONSE_GATE_V1` depends directly on `S1_CONVERSATIONAL_OWNER_BRIDGE_CONTRACT_V1`.

E.1 is the authority for:

- `owner_ref`
- `case_ref`
- `source_session_ref`
- `owner_intent`
- `next_conversational_action`
- `allowed_response_scope`
- `forbidden_response_scope`
- `safe_context_refs_for_future_llm`

E.2 must **not** recompute or widen those boundaries.

E.2 only:

- validates that the proposed response candidate stays inside E.1 scope;
- validates that only E.1 safe refs are cited;
- validates that the proposed response does not attempt authority or execution;
- converts the future LLM output into a **guarded response candidate** for later routing.

## Canonical constants

```text
schema_version = S1_LLM_GUARDED_RESPONSE_GATE_V1
service_name = SERVICE_1
gate_kind = GUARDED_LLM_RESPONSE_CANDIDATE
source_bridge_kind = CONVERSATIONAL_OWNER_BRIDGE_CANDIDATE
```

## Input contract

The gate should accept a single pure input payload:

```python
class Service1LlmGuardedResponseGateInputV1(TypedDict):
    conversational_owner_bridge_candidate: dict[str, object] | None
    llm_response_candidate: dict[str, object] | None
    notes: list[str]
```

### Required `conversational_owner_bridge_candidate`

The bridge candidate must already be `CONVERSATIONAL_OWNER_BRIDGE_CANDIDATE_READY` and should come from E.1.

Minimum required fields:

```python
{
    "bridge_kind": "CONVERSATIONAL_OWNER_BRIDGE_CANDIDATE",
    "owner_ref": str,
    "case_ref": str,
    "service_name": "SERVICE_1",
    "source_session_ref": str,
    "normalized_owner_message": str,
    "owner_intent": str,
    "next_conversational_action": str,
    "safe_context_refs_for_future_llm": dict[str, str],
    "allowed_response_scope": list[str],
    "forbidden_response_scope": list[str],
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

### Required `llm_response_candidate`

This is **not** the actual LLM runtime call.
It is the structured candidate artifact that a future LLM adapter would propose for validation.

```python
class Service1FutureLlmResponseCandidateV1(TypedDict):
    response_text_candidate: str
    declared_response_scope: list[str]
    cited_safe_context_ref_keys: list[str]
    declared_next_conversational_action: str
    follow_up_question_candidates: list[str]
    missing_evidence_request_candidates: list[str]
    clarification_capture_candidates: list[str]
    correction_capture_candidates: list[str]
    owner_visible_disclaimer_candidates: list[str]
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

### Why the candidate must be structured

The gate must remain deterministic.

That means E.2 should validate:

- **declared scope** instead of inferring hidden intent;
- **declared safe ref keys** instead of inspecting raw files;
- **declared next action** instead of trusting free-form wording;
- **declared flags** instead of letting runtime authority leak through text.

## Output contract

```python
class Service1LlmGuardedResponseCandidateV1(TypedDict):
    gate_kind: Literal["GUARDED_LLM_RESPONSE_CANDIDATE"]
    owner_ref: str
    case_ref: str
    service_name: Literal["SERVICE_1"]
    source_session_ref: str
    source_bridge_ref_candidate: str | None
    source_owner_message_ref_candidate: str | None
    owner_intent: str
    next_conversational_action: str
    response_text_candidate: str
    allowed_response_scope: list[str]
    forbidden_response_scope: list[str]
    applied_response_scope: list[str]
    cited_safe_context_refs: dict[str, str]
    follow_up_question_candidates: list[str]
    missing_evidence_request_candidates: list[str]
    clarification_capture_candidates: list[str]
    correction_capture_candidates: list[str]
    owner_visible_disclaimer_candidates: list[str]
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
class Service1LlmGuardedResponseGateResultV1(TypedDict):
    schema_version: str
    service_name: str
    status: str
    guarded_llm_response_candidate: Service1LlmGuardedResponseCandidateV1 | None
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

## Allowed response scope

E.2 must inherit the E.1 scope and must never expand it.

Canonical allowed scope:

```text
explain_existing_state
summarize_existing_delivery_candidate
ask_for_missing_evidence
capture_owner_clarification
capture_owner_correction
explain_next_safe_step
```

### Scope interpretation

| Scope | Meaning |
|-------|---------|
| `explain_existing_state` | Explain already-known verified state only |
| `summarize_existing_delivery_candidate` | Summarize an existing delivery candidate only |
| `ask_for_missing_evidence` | Ask for missing evidence without concluding truth |
| `capture_owner_clarification` | Phrase clarification prompts/capture candidates |
| `capture_owner_correction` | Phrase correction prompts/capture candidates |
| `explain_next_safe_step` | Explain the next safe governed step without authorizing it |

## Forbidden response scope

Canonical forbidden scope:

```text
invent_case_truth
diagnose_without_evidence
promise_final_delivery
authorize_runtime
execute_tools
trigger_pipeline
mutate_case
publish_outputs
provide_legal_tax_accounting_certainty
act_as_human_operator
```

E.2 must block any candidate that declares, implies structurally, or attempts any of those scopes.

## Statuses

Recommended result statuses:

```text
GUARDED_LLM_RESPONSE_CANDIDATE_READY
BLOCKED_MISSING_BRIDGE
BLOCKED_INVALID_BRIDGE
BLOCKED_BRIDGE_NOT_READY
BLOCKED_MISSING_LLM_RESPONSE_CANDIDATE
BLOCKED_EMPTY_RESPONSE_TEXT
BLOCKED_SCOPE_NOT_ALLOWED
BLOCKED_FORBIDDEN_SCOPE
BLOCKED_UNSAFE_CONTEXT_REF
BLOCKED_NEXT_ACTION_MISMATCH
BLOCKED_UNSAFE_FLAGS
UNKNOWN
```

### Meaning

| Status | Meaning |
|-------|---------|
| `GUARDED_LLM_RESPONSE_CANDIDATE_READY` | Candidate is safe enough to remain a guarded response candidate |
| `BLOCKED_MISSING_BRIDGE` | No E.1 bridge candidate provided |
| `BLOCKED_INVALID_BRIDGE` | Provided bridge is malformed or wrong kind/service |
| `BLOCKED_BRIDGE_NOT_READY` | Bridge exists but is not in a ready candidate state |
| `BLOCKED_MISSING_LLM_RESPONSE_CANDIDATE` | No structured future-LLM response candidate was provided |
| `BLOCKED_EMPTY_RESPONSE_TEXT` | Response text is missing or empty after normalization |
| `BLOCKED_SCOPE_NOT_ALLOWED` | Declared scope is not a subset of bridge allowed scope |
| `BLOCKED_FORBIDDEN_SCOPE` | Candidate includes any forbidden scope |
| `BLOCKED_UNSAFE_CONTEXT_REF` | Candidate cites refs not present in bridge safe context |
| `BLOCKED_NEXT_ACTION_MISMATCH` | Candidate next action does not match bridge next action |
| `BLOCKED_UNSAFE_FLAGS` | Any dangerous/runtime flag is not `False` |
| `UNKNOWN` | Reserved fallback for unexpected validator state |

## Block reasons

Recommended canonical block reasons:

```text
conversational_owner_bridge_candidate_required
bridge_kind_must_be_conversational_owner_bridge_candidate
bridge_service_name_must_be_service_1
bridge_status_must_be_ready
bridge_owner_ref_required
bridge_case_ref_required
bridge_safe_context_refs_required
bridge_allowed_response_scope_required
llm_response_candidate_required
response_text_candidate_required
declared_response_scope_required
declared_response_scope_not_allowed
declared_response_scope_contains_forbidden_scope
cited_safe_context_ref_keys_required
cited_safe_context_ref_key_not_allowed
declared_next_conversational_action_required
declared_next_conversational_action_must_match_bridge
llm_response_candidate_flags_must_be_false
bridge_flags_must_be_false
```

## Flags that must always be false

These flags must be `False` in:

- the input bridge candidate;
- the input future-LLM response candidate;
- the result;
- the guarded response candidate.

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

## What the future LLM may do

A future LLM may:

- rewrite verified state into owner-friendly language;
- summarize an existing delivery candidate;
- ask for missing evidence;
- ask a clarification question;
- ask a correction question;
- explain the next safe governed step;
- acknowledge unsupported requests and narrow back to safe scope.

## What the future LLM must never do

A future LLM must never:

- invent or patch `case_truth`;
- infer diagnostic, tax, legal, or accounting certainty without evidence;
- authorize rerun, runtime, tools, pipeline, or runner;
- execute anything;
- read files or Excel directly;
- create new unsafe refs outside bridge safe context;
- promise final delivery;
- publish outputs to the client;
- impersonate a human operator/reviewer/signoff authority;
- bypass E.1 scope;
- bypass future E.3 routing.

## Minimal validation rules

E.2 implementation should block unless all of these are true:

1. E.1 bridge candidate exists and is valid.
2. Bridge kind is `CONVERSATIONAL_OWNER_BRIDGE_CANDIDATE`.
3. Bridge service is `SERVICE_1`.
4. Bridge safe refs exist.
5. Structured future-LLM response candidate exists.
6. `response_text_candidate` is non-empty after trim/collapse.
7. `declared_response_scope` is non-empty and is a subset of bridge allowed scope.
8. `declared_response_scope` has no intersection with bridge forbidden scope.
9. `cited_safe_context_ref_keys` all exist in bridge `safe_context_refs_for_future_llm`.
10. `declared_next_conversational_action` matches bridge `next_conversational_action`.
11. All dangerous flags remain `False`.

## Non-goals

This design does **not** include:

- actual OpenAI integration;
- actual prompt construction;
- actual Pydantic AI agent wiring;
- router/channel selection;
- UI/API delivery;
- persistence;
- rerun authorization;
- post-answer mutation;
- final owner publishing.

Those belong to later implementation or later slices, not to this gate.

## Ready-for-implementation criterion

E.2 is design-ready when implementation can proceed with this invariant:

> The conversational layer may produce a response candidate, but only deterministic gates may decide whether that candidate stays inside safe owner-facing explanation scope.

If that invariant is preserved, Phase E.2 can be implemented without mixing conversation with runtime authority.
