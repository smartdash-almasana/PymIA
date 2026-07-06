# SERVICE_1_SHADOW_EVIDENCE_TO_OWNER_DIALOGUE_PACKET_TASKSPEC_V1

## VERDICT

```text
STATUS: TASKSPEC_CREATED
SCOPE: DOC_ONLY
RUNTIME_CHANGE: NO
TEST_CHANGE: NO
DELETE_CHANGE: NO
TARGET_FRONT: SERVICE_1_SHADOW_EVIDENCE_TO_OWNER_DIALOGUE_PACKET_V1
```

## PURPOSE

Define a safe Service 1 packet that converts previously detected shadow/evidence material into an owner-facing dialogue packet.

The goal is to preserve the useful function:

```text
read evidence -> summarize what is known -> expose gaps -> ask the owner precise questions
```

and eliminate the unsafe identity:

```text
operator review -> shadow approval -> autonomous supervision -> runtime decision
```

## CONTEXT

Completed cleanup fronts:

```text
P0-A: operator_harness_v1 -> controlled_delivery_demo_harness
P0-A2: operator_delivery_package -> owner_delivery_package
P0-B: operator_harness_v2 -> owner_release_action_gate
P0-C: accounting_human_review_gate -> accounting_sandbox_release_gate
```

This TaskSpec does not reopen those fronts.

## TARGET CONCEPT

Preferred product/runtime name:

```text
service_1_owner_evidence_dialogue_packet_v1.py
```

Preferred symbols:

```text
Service1OwnerEvidenceDialoguePacketV1
build_service_1_owner_evidence_dialogue_packet_v1
```

Acceptable alternative if existing source uses stronger shadow terminology:

```text
service_1_shadow_evidence_to_owner_dialogue_packet_v1.py
Service1ShadowEvidenceToOwnerDialoguePacketV1
build_service_1_shadow_evidence_to_owner_dialogue_packet_v1
```

But the preferred final active concept is:

```text
owner_evidence_dialogue_packet
```

not:

```text
shadow_operator_review_packet
operator_shadow_packet
operator_review_packet
```

## FUNCTIONAL DEFINITION

The packet is a pure owner-facing dialogue artifact. It must transform available evidence status into a structured conversation packet for the business owner.

It may include:

```text
- case_id
- service_name
- source_evidence_refs
- evidence_received_summary
- evidence_missing_summary
- uncertainty_notes
- owner_questions
- suggested_next_owner_action
- blocked_claims
- limitations
- runtime_authorized=False
- autonomous_decision_authorized=False
- delivery_authorized=False
```

It must not include:

```text
- tool execution requests
- runtime authorization
- final delivery approval
- accounting certification
- definitive reconciliation claims
- autonomous review decisions
- operator approval language
```

## INPUT CONTRACT

Recommended input shape:

```python
class Service1OwnerEvidenceDialoguePacketInputV1(TypedDict):
    case_id: str
    service_name: str
    owner_alias: str | None
    source_evidence_refs: list[str]
    evidence_status: str
    received_evidence: list[dict[str, object]]
    missing_evidence: list[dict[str, object]]
    detected_conflicts: list[dict[str, object]]
    upstream_gate_statuses: dict[str, str]
    requested_owner_action: str | None
    notes: list[str]
```

Minimum required fields:

```text
case_id
service_name
source_evidence_refs
received_evidence
missing_evidence
upstream_gate_statuses
```

Invalid or missing fields must fail closed.

## OUTPUT CONTRACT

Recommended output shape:

```python
class Service1OwnerEvidenceDialoguePacketV1(TypedDict):
    schema_version: str
    packet_kind: Literal["OWNER_EVIDENCE_DIALOGUE_PACKET"]
    status: str
    service_name: Literal["SERVICE_1"]
    case_id: str
    owner_alias: str | None
    owner_visible: Literal[True]
    source_evidence_refs: list[str]
    evidence_received_summary: list[str]
    evidence_missing_summary: list[str]
    detected_conflict_summary: list[str]
    owner_questions: list[str]
    suggested_next_owner_action: str
    blocked_claims: list[str]
    limitations: list[str]
    runtime_authorized: Literal[False]
    tool_execution_authorized: Literal[False]
    delivery_authorized: Literal[False]
    autonomous_decision_authorized: Literal[False]
    notes: list[str]
```

## STATUS MODEL

Recommended statuses:

```text
READY_FOR_OWNER_DIALOGUE
NEEDS_OWNER_EVIDENCE
NEEDS_OWNER_CLARIFICATION
BLOCKED_BY_CONFLICTING_EVIDENCE
BLOCKED_BY_MISSING_REQUIRED_FIELDS
INVALID_INPUT
UNKNOWN
```

Status rules:

```text
READY_FOR_OWNER_DIALOGUE:
  evidence is sufficient to ask owner-facing confirmation/clarification questions.

NEEDS_OWNER_EVIDENCE:
  required evidence is missing and must be requested from the owner.

NEEDS_OWNER_CLARIFICATION:
  evidence exists but is ambiguous and needs owner clarification.

BLOCKED_BY_CONFLICTING_EVIDENCE:
  evidence conflicts and no safe question/summary can proceed without explicit owner clarification.

BLOCKED_BY_MISSING_REQUIRED_FIELDS:
  required input fields are absent or blank.

INVALID_INPUT:
  input is not a dict or required list/dict shapes are invalid.

UNKNOWN:
  upstream status cannot be classified safely.
```

## OWNER QUESTION RULES

Questions must be:

```text
- owner-facing
- concrete
- one question per missing/ambiguous evidence group
- non-technical unless a technical term is already owner-visible
- framed as clarification, not accusation
- free of final accounting or diagnostic claims
```

Allowed examples:

```text
- Necesito confirmar qué archivo representa las ventas del período.
- ¿Este Excel corresponde a ventas cobradas, ventas facturadas o ambas?
- Falta el archivo de cobros para comparar contra ventas. ¿Lo tenés disponible?
- Hay dos columnas posibles para importe. ¿Cuál usa tu equipo como importe real?
```

Forbidden examples:

```text
- El operador aprueba la evidencia.
- La conciliación queda validada.
- La IA confirma la rentabilidad real.
- Este paquete autoriza entrega final.
- El sistema reemplaza la revisión del contador.
```

## FORBIDDEN CAPABILITIES

The implementation must not:

```text
- execute tools
- call LLMs
- call APIs
- read/write XLSX
- parse PDF
- use OCR
- authorize runtime
- authorize final delivery
- authorize production use
- produce final accounting claims
- replace owner/accountant confirmation
- introduce operator as actor, supervisor, approver, or reviewer
```

## ALLOWED CAPABILITIES

The implementation may:

```text
- classify evidence summary state from provided dictionaries
- generate owner-visible summaries from already provided fields
- generate owner questions from missing/ambiguous/conflicting evidence descriptors
- preserve source refs
- expose limitations
- fail closed on invalid shapes
- return deterministic output
```

## SEMANTIC MIGRATION

If existing source or docs use old terminology, migrate as follows:

```text
shadow_evidence_operator_review_packet
-> owner_evidence_dialogue_packet

shadow evidence operator review
-> owner evidence dialogue

operator_review_packet
-> owner_dialogue_packet

operator_notes
-> owner_dialogue_notes or delivery_notes

operator_action
-> owner_next_question / suggested_next_owner_action

operator_approval
-> forbidden; no replacement unless explicit owner/accountant signoff gate exists

shadow approval
-> forbidden
```

## FAIL-CLOSED REQUIREMENTS

Must return `runtime_authorized=False` in every branch.

Must return `delivery_authorized=False` in every branch.

Must return `tool_execution_authorized=False` in every branch.

Must return `autonomous_decision_authorized=False` in every branch.

Invalid input must not produce owner questions that look like valid delivery progress.

Missing evidence must produce owner evidence requests, not delivery claims.

Conflicting evidence must block and ask for clarification.

## FILES TO INSPECT BEFORE IMPLEMENTATION

Audit-only search targets before patch:

```text
shadow_evidence
shadow evidence
operator review packet
operator_review_packet
shadow_operator
owner_dialogue
owner_evidence
owner_question
evidence_packet
```

Likely areas:

```text
PymIA-Live/pymia/smartpyme/
PymIA-Live/tests/smartpyme/
docs/auditoria/
docs/producto/
```

If MCP blocks these terms, use terminal/Codex search rather than guessing.

## EXPECTED FILES IF IMPLEMENTED

Runtime candidate:

```text
PymIA-Live/pymia/smartpyme/service_1_owner_evidence_dialogue_packet_v1.py
```

Test candidate:

```text
PymIA-Live/tests/smartpyme/test_service_1_owner_evidence_dialogue_packet_v1.py
```

Optional closeout after implementation:

```text
docs/auditoria/SERVICE_1_OWNER_EVIDENCE_DIALOGUE_PACKET_CLOSEOUT_V1.md
```

## TEST PLAN

Minimum focal tests:

```text
1. valid complete evidence creates READY_FOR_OWNER_DIALOGUE
2. missing evidence creates NEEDS_OWNER_EVIDENCE
3. ambiguous evidence creates NEEDS_OWNER_CLARIFICATION
4. conflicting evidence creates BLOCKED_BY_CONFLICTING_EVIDENCE
5. missing required field fails closed
6. invalid input fails closed
7. runtime/tool/delivery/autonomous flags are always False
8. forbidden operator/autonomous/final accounting terms are absent from owner-visible output
9. output is deterministic for identical input
10. module has no IO/API/LLM/XLSX/PDF/OCR imports
```

Suggested command after implementation:

```bash
python -m pytest tests/smartpyme/test_service_1_owner_evidence_dialogue_packet_v1.py -q
```

If integrated into existing chain, add only the direct consumer tests required by import/use.

## RESIDUE CHECKS AFTER IMPLEMENTATION

Inside `PymIA-Live`, expected after migration:

```text
operator_review_packet: 0 in active source/tests
shadow_operator: 0 in active source/tests
operator_approval: 0 in active source/tests
```

Acceptable temporary residues:

```text
shadow_evidence may remain if used only as historical input/source terminology
operator may remain in unrelated legacy docs or already quarantined audit docs
human_review/reviewer/assisted are separate fronts and must not be globally changed here
```

## DO NOT TOUCH

```text
- P0-A/P0-A2/P0-B/P0-C closed fronts
- service_1_case_delivery_folder_v1.py
- service_1_human_review_release_integration_gate_v1.py
- service_1_human_review_signoff_flow_v1.py
- service_1_final_owner_release_decision_gate_v1.py
- S2 assisted review files
- accounting_sandbox_release_gate_v1.py
- owner_release_action_gate_v1.py
- global human_review cleanup
```

## ACCEPTANCE CRITERIA

```text
1. TaskSpec exists.
2. Implementation, if later authorized, is pure and deterministic.
3. No runtime/tool/delivery/autonomous authorization is introduced.
4. Owner-visible output contains questions and limitations, not approvals.
5. No operator identity is reintroduced.
6. Tests pass.
7. No unrelated fronts are touched.
```

## RECOMMENDED IMPLEMENTATION COMMIT MESSAGE

Only if implementation is later authorized and tests pass:

```bash
git commit -m "feat(pymia-live): add service 1 owner evidence dialogue packet"
```

For this document-only TaskSpec:

```bash
git commit -m "docs(pymia): specify service 1 owner evidence dialogue packet"
```

## FINAL STATUS

```text
SERVICE_1_SHADOW_EVIDENCE_TO_OWNER_DIALOGUE_PACKET_TASKSPEC_V1: CREATED
CODE_CHANGE_AUTHORIZED: NO
NEXT_ACTION: AUDIT_EXISTING_SHADOW_EVIDENCE_REFERENCES_OR_IMPLEMENT_OWNER_EVIDENCE_DIALOGUE_PACKET_IF_EXPLICITLY_ORDERED
```
