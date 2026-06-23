# SERVICE_1_OPERATOR_HARNESS_V2_DESIGN

VEREDICT:

```text
SERVICE_1_OPERATOR_HARNESS_V2_DESIGN: CREATED
```

PURPOSE:

```text
Diseñar el arnés operador V2 de Servicio 1.

El objetivo es definir cómo un operador humano debe orquestar, en una secuencia segura y repetible, las piezas ya estabilizadas de Servicio 1 antes de ejecutar casos reales o avanzar hacia implementación.
```

POSITIONING:

```text
Servicio 1 = microservicio asistido bajo revisión humana.

Operator Harness V2 no es chatbot.
Operator Harness V2 no es autonomía plena.
Operator Harness V2 no es runtime contable productivo.
Operator Harness V2 no reemplaza revisión humana.
Operator Harness V2 organiza el flujo operativo y los gates de seguridad.
```

WHY_THIS_EXISTS:

```text
Servicio 1 ya tiene piezas aisladas maduras:
- Case Folder Manifest V1
- Accounting XLSX Runtime V1 Design
- QA Delivery Checklist V1
- Delivery Manifest Audit V1
- Operator Runbook con edge-case rules
- Real Client Operator Packet V1
- Synthetic XLSX Edge Case Run V2

Falta definir el arnés que ordena cuándo se usa cada pieza, qué bloquea entrega y qué queda fuera.
```

HARNESS_SCOPE:

```text
Incluye:
- intake operator-guided
- case folder manifest
- scope acceptance/reduction
- evidencia declarada
- operator notes
- accounting XLSX review draft
- owner message
- QA delivery checklist
- delivery manifest audit
- human review gate
- delivery as operational draft
- post-delivery review

No incluye:
- APIs vivas
- OCR
- parser automático
- chatbot libre
- LLM runtime
- conciliación definitiva
- auditoría
- certificación
- validación fiscal
- asientos automáticos
- reemplazo del contador
```

ORCHESTRATED_COMPONENTS:

```text
SERVICE_1_REAL_CLIENT_OPERATOR_PACKET_V1:
- guía intake y límites iniciales.

SERVICE_1_CASE_FOLDER_MANIFEST_V1:
- crea el contenedor lógico del caso.

SERVICE_1_ACCOUNTING_XLSX_RUNTIME_V1_DESIGN:
- define el contrato del XLSX operativo de revisión.

SERVICE_1_QA_DELIVERY_CHECKLIST_V1:
- valida seguridad de entrega.

SERVICE_1_DELIVERY_MANIFEST_AUDIT_V1:
- audita manifest + QA + claims + stop conditions.

SERVICE_1_ACCOUNTING_WORKPAPER_OPERATOR_RUNBOOK_V1:
- guía operación humana y edge-case rules.

HUMAN_REVIEW_GATE:
- impide salida como final y exige revisión humana.
```

HARNESS_FLOW:

```text
1. Receive client/operator request.
2. Apply real client operator packet.
3. Confirm supported family and bounded scope.
4. Create case folder manifest.
5. Register evidence as declared, not audited.
6. Apply operator runbook and edge-case rules.
7. Prepare accounting XLSX review draft if applicable.
8. Prepare owner-facing message.
9. Apply QA Delivery Checklist.
10. Apply Delivery Manifest Audit.
11. Apply Human Review Gate.
12. Deliver only as operational draft under human review.
13. Record post-delivery review.
```

STATE_VALUES:

```text
INTAKE_PENDING
INTAKE_RECEIVED
SCOPE_REDUCTION_REQUIRED
SCOPE_ACCEPTED
CASE_MANIFEST_CREATED
EVIDENCE_REGISTERED
WORKBOOK_DRAFT_PREPARED
OWNER_MESSAGE_PREPARED
QA_PENDING
QA_PASSED
QA_FAILED
DELIVERY_AUDIT_PENDING
DELIVERY_AUDIT_PASSED
DELIVERY_AUDIT_FAILED
HUMAN_REVIEW_PENDING
READY_FOR_DRAFT_DELIVERY
DELIVERED_AS_OPERATIONAL_DRAFT
REWORK_REQUIRED
BLOCKED
CLOSED_UNDER_HUMAN_REVIEW
```

INPUTS_REQUIRED:

```text
case_id
client_alias
case_family
period
operator
human_reviewer
accepted_scope
input_files_list
evidence_manifest
case_folder_path
owner_problem_statement
boundary_acceptance
```

OUTPUTS_EXPECTED:

```text
case_manifest.md
operator_notes.md
evidence_gap_log.md
visible_differences_log.md
accounting_workpaper_review_draft.xlsx when applicable
owner_message.md
qa_checklist_result.md
delivery_manifest_audit_result.md
post_delivery_review.md when applicable
sanitized_review_doc only if repo documentation is needed
```

GATES:

```text
GATE_1_SCOPE:
- supported family
- period defined
- bounded scope
- no unsupported broad case

GATE_2_EVIDENCE:
- minimum evidence present
- evidence declared, not audited
- no invented evidence

GATE_3_CASE_MANIFEST:
- required manifest fields present
- human reviewer listed
- stop conditions recorded

GATE_4_XLSX_REVIEW_DRAFT:
- XLSX is operational review draft only
- no final accounting claim
- warnings/gaps visible

GATE_5_QA:
- QA Delivery Checklist passed

GATE_6_DELIVERY_AUDIT:
- Delivery Manifest Audit passed
- forbidden claims absent
- stop_conditions = NONE

GATE_7_HUMAN_REVIEW:
- human review required and visible
- output not marked final
```

FAIL_CLOSED_RULES:

```text
Block if:
- family unsupported
- scope too broad and cannot be reduced
- minimum evidence missing
- human reviewer missing
- stop condition active
- QA missing or failed
- delivery manifest audit missing or failed
- forbidden claims detected
- output implies finality
- client requests audit/certification/fiscal validation/final reconciliation/accounting entries
```

EDGE_CASE_ROUTING:

```text
INCOMPLETE_SALES_COLLECTIONS:
- continue as partial draft if scope and files are clear
- mark missing collections
- require human review

DUPLICATED_COLLECTIONS:
- continue with warnings
- do not net automatically
- require human review

MISSING_MASTER_DATA:
- continue with warnings if evidence is enough
- mark incomplete master data
- require human review

NEGATIVE_AMOUNTS_AND_CREDIT_NOTES:
- separate adjustments
- require human review
- do not treat as ordinary payments/collections without warning

TOO_BROAD_MIXED_CASE:
- block or reduce scope
- do not execute broad analysis

NO_TRANSACTION_KEYS:
- aggregate-only or request minimum columns
- no fine matching
```

FORBIDDEN_CLAIMS:

```text
auditado
certificado
conciliado definitivamente
validado fiscalmente
exacto
cerrado contablemente
aprobado fiscalmente
reemplaza al contador
garantiza exactitud
listo para presentación fiscal
resultado contable final
```

REQUIRED_SAFE_LANGUAGE:

```text
borrador operativo
evidencia declarada
diferencias visibles
faltantes de evidencia
advertencias operativas
requiere revisión humana
XLSX operativo de revisión
```

FOLDER_POLICY:

```text
Operational artifacts live outside the repo.

Recommended root:
E:\BuenosPasos\smartbridge\PymIA-local-artifacts\service_1_cases\<CASE_ID>\

Never commit:
- service_1_cases/
- real client folders
- XLSX inputs
- XLSX outputs
- sensitive evidence
- scratch scripts
- delivery artifacts with real data
```

RELATION_TO_RUNTIME_IMPLEMENTATION:

```text
This design does not implement runtime.

If implemented later, the harness should orchestrate existing contracts and artifacts.
It must not create new accounting semantics.
It must not bypass QA, delivery audit or human review gate.
```

RELATION_TO_CHAT_IA:

```text
Chat IA Harness remains out of scope.

If opened later, chat must only feed typed intake or task specs into this operator harness.
Chat must not bypass manifest, QA, delivery audit or human review.
```

RELATION_TO_SERVICE_2:

```text
Servicio 2 remains out of scope.

Operator Harness V2 cannot produce broad diagnosis, fiscal analysis or organizational advisory beyond Servicio 1 delivery scope.
```

VALIDATION_REQUIREMENTS_IF_IMPLEMENTED:

```text
If converted to code later, validate:
- state transitions
- required fields
- fail-closed gates
- stop condition blocking
- forbidden claims blocking
- QA required before delivery
- delivery audit required before delivery
- human reviewer required before delivery
- no external APIs/OCR/parser/LLM calls
```

SYNTHETIC_PILOT_REQUIREMENTS:

```text
Before real client use, run at least one synthetic harness dry-run with:
- duplicated collections
- missing master data
- no transaction keys
- QA checklist applied
- delivery audit applied
- human review gate visible
```

PRODUCT_DECISION_REQUIRED:

```text
YES before implementation.

Decision required:
Should Operator Harness V2 remain a manual operating protocol or become a deterministic code module that coordinates case manifest, XLSX runtime, QA and delivery audit?
```

RECOMMENDED_DECISION:

```text
Run one controlled synthetic harness dry-run first.
Then decide whether to implement code.

Do not open chatbot, APIs, OCR, parser or Servicio 2 before this harness is validated.
```

NEXT_SAFE_ACTION:

```text
SERVICE_1_OPERATOR_HARNESS_V2_SYNTHETIC_DRY_RUN
```

COMMIT_READY:

```text
YES
```
