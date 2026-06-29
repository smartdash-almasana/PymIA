# S1_FIRST_REAL_CLIENT_PILOT_RUNBOOK_V1

## VERDICT

```text
S1_FIRST_REAL_CLIENT_PILOT_RUNBOOK_V1: CREATED
```

## BASELINE

```text
S1_FULL_ASSISTED_V1: CLOSED_WITH_LIMITS
S1_FULL_ASSISTED_V1_HARDENING: CLOSED_WITH_SCOPE_NOTE
S1_REAL_CLIENT_PILOT_READINESS_AUDIT_V1: PASS_WITH_OPERATOR_SUPERVISION
S1_FIRST_REAL_CLIENT_PILOT_PROTOCOL_V1: CREATED
S1_FIRST_REAL_CLIENT_PILOT_INTAKE_PACKET_V1: CREATED
```

This runbook is the operator procedure for the first controlled real-client pilot. It does not authorize production, autonomous delivery, sales claims, or commercial launch.

## OPERATOR DOCTRINE

```text
La IA conversa.
La FSM gobierna.
Las tools ejecutan.
Los archivos son el producto.
La revisión humana cierra.
```

## RUNBOOK SCOPE

```text
pilot_type: first_controlled_real_client_case
operator_supervision_required: true
human_review_required: true
runtime_authorized: false
autonomous_use_authorized: false
production_claim_allowed: false
```

## PHASE 0 — DO NOT START UNLESS

```text
[ ] Intake packet completed.
[ ] One owner question selected.
[ ] One supported family selected.
[ ] One XLSX or tightly scoped workbook set available outside repo.
[ ] Human reviewer identified.
[ ] Consent recorded.
[ ] No stop condition active.
[ ] Operator has write access to an external client/output folder outside repo.
```

If any checkbox fails:

```text
STOP: DO_NOT_RUN_CLI
```

## PHASE 1 — CREATE EXTERNAL PILOT FOLDER

Create an external folder outside the repository.

Suggested shape:

```text
E:\PymIA_Client_Pilots\<case_alias>\
  input\
  tool_requests\
  output\
  operator_notes\
```

Rules:

```text
[ ] Do not place real client XLSX inside the repo.
[ ] Do not commit generated client outputs.
[ ] Do not place credentials, keys, tokens or API exports in the folder.
```

## PHASE 2 — PLACE INPUT XLSX

Place the client XLSX in:

```text
E:\PymIA_Client_Pilots\<case_alias>\input\archivo_cliente.xlsx
```

Check:

```text
[ ] Extension is .xlsx.
[ ] File opens manually.
[ ] File matches selected case and period.
[ ] File is sufficient for the selected one-family question.
```

If not:

```text
STOP: INPUT_FILE_NOT_ACCEPTABLE
```

## PHASE 3 — PREPARE TOOL REQUESTS

Create:

```text
E:\PymIA_Client_Pilots\<case_alias>\tool_requests\tool_requests.json
```

Allowed shape:

```json
[
  {
    "tool_ref": "precio_margen_basico",
    "inputs": {
      "precio_venta": 1000,
      "costo_unitario": 650
    }
  }
]
```

Allowed `tool_ref` values:

```text
precio_margen_basico
caja_diaria_triage
gastos_triage
proveedores_precio_variacion_triage
stock_alertas_basicas
```

Hard rule:

```text
No input value may be invented.
Every value must come from the XLSX or explicit owner confirmation.
```

If values are missing:

```text
Use MISSING_INPUTS flow or stop and ask owner for explicit confirmation.
Do not guess.
```

## PHASE 4 — RUN CANONICAL CLI

From `PymIA-Live`:

```powershell
cd E:\BuenosPasos\smartbridge\PymIA\PymIA-Live
python -m pymia.cli.service_1_operator --file "E:\PymIA_Client_Pilots\<case_alias>\input\archivo_cliente.xlsx" --run-tools "E:\PymIA_Client_Pilots\<case_alias>\tool_requests\tool_requests.json"
```

Expected stdout blocks:

```text
Estructura detectada
Confirmación necesaria          # when applicable
Pipeline de herramientas First Aid
QA delivery gate
Carpeta de caso
```

Expected safety markers:

```text
Revisión humana requerida: true
Runtime autorizado: false
```

If CLI errors:

```text
STOP: CLI_RUN_FAILED
Record stderr/stdout summary in operator notes.
Do not deliver anything.
```

## PHASE 5 — LOCATE CASE FOLDER

From stdout, copy:

```text
Carpeta de caso
- Caso: <case_id>
- Ubicación: <case_dir>
```

Record in private operator note:

```text
case_folder_path:
```

Required files:

```text
[ ] operator_packet.json
[ ] pipeline_result.json
[ ] post_tool_owner_delivery_summary.md
[ ] final_qa_delivery_gate.json
[ ] human_review_gate.json
[ ] manifest.json
[ ] one or more First Aid XLSX outputs if tools ran
```

If required files are missing:

```text
STOP: CASE_FOLDER_INCOMPLETE
```

## PHASE 6 — VERIFY FINAL QA

Open:

```text
final_qa_delivery_gate.json
```

Required state:

```text
status = PASS
delivery_status = READY_FOR_HUMAN_REVIEW
runtime_authorized = false
```

If not exact:

```text
STOP: FINAL_QA_NOT_READY
```

## PHASE 7 — VERIFY HUMAN REVIEW GATE

Open:

```text
human_review_gate.json
```

Required state:

```text
status = PENDING_HUMAN_REVIEW
human_review_required = true
```

If not exact:

```text
STOP: HUMAN_REVIEW_GATE_INVALID
```

## PHASE 8 — REVIEW OUTPUTS BEFORE ANY CLIENT MESSAGE

Check XLSX outputs:

```text
[ ] Workbook opens.
[ ] Resumen sheet exists.
[ ] Limitaciones sheet exists.
[ ] Claims prohibidos sheet exists.
[ ] No final diagnosis wording.
[ ] No audit/certification/tax wording.
```

Check owner summary:

```text
[ ] Says operational draft / revisión inicial.
[ ] Says evidence declared / datos declarados.
[ ] Says human review required.
[ ] Does not claim exactness.
[ ] Does not replace accountant or reviewer.
```

Check operator packet:

```text
[ ] runtime_authorized=false.
[ ] human review visible.
[ ] tool_results match selected tool_refs.
[ ] missing/invalid inputs are visible if present.
```

If any check fails:

```text
STOP: OUTPUT_REVIEW_FAILED
```

## PHASE 9 — HUMAN REVIEW DECISION

Human reviewer chooses one:

```text
BLOCKED
READY_FOR_HUMAN_REVIEW_ONLY
APPROVED_FOR_LIMITED_CLIENT_DELIVERY
```

`APPROVED_FOR_LIMITED_CLIENT_DELIVERY` is allowed only if:

```text
[ ] final QA passed.
[ ] human_review_gate was pending before review.
[ ] reviewer checked XLSX outputs.
[ ] reviewer checked owner summary.
[ ] reviewer checked forbidden claims.
[ ] reviewer confirms delivery is limited operational draft.
```

## ALLOWED CLIENT MESSAGE AFTER REVIEW

Only after human signoff, a safe message may say:

```text
Preparamos una revisión inicial sobre la planilla recibida.
El archivo es un borrador operativo basado en datos declarados.
Incluye señales y límites para revisar antes de tomar decisiones.
No es auditoría, certificación, validación fiscal ni cierre contable.
```

## BLOCKED CLIENT MESSAGE

Never say:

```text
El sistema auditó.
El resultado es exacto.
La conciliación está cerrada.
El diagnóstico es final.
Esto reemplaza al contador.
La entrega fue aprobada automáticamente.
```

## PILOT RECORD AFTER RUN

Create private operator note outside repo:

```text
case_alias:
period:
owner_question:
selected_family:
input_file_name_only:
tool_requests_path:
case_folder_path:
tool_refs_run:
final_qa_status:
human_review_gate_status:
human_reviewer:
human_review_decision:
delivery_decision:
blocked_reason_if_any:
next_safe_action:
```

Do not commit this note if it contains client-identifying data.

## STOP CONDITIONS SUMMARY

Stop immediately if:

```text
- intake incomplete;
- no human reviewer;
- non-XLSX file;
- unsupported family;
- unsupported tool_ref;
- invented input values;
- CLI error;
- missing case folder artifacts;
- final QA not PASS;
- delivery_status not READY_FOR_HUMAN_REVIEW;
- human_review_gate not PENDING_HUMAN_REVIEW;
- runtime_authorized=true anywhere;
- output implies final diagnosis/accounting/fiscal/audit claim.
```

## FINAL POSITION

```text
READY_TO_EXECUTE_FIRST_CONTROLLED_REAL_CLIENT_PILOT_RUNBOOK
```

This runbook authorizes a supervised run procedure only. It does not authorize autonomous delivery, production use, open sales, or final accounting/tax claims.
