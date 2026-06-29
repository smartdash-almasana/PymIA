# S1_FIRST_REAL_CLIENT_PILOT_PROTOCOL_V1

## VERDICT

```text
S1_FIRST_REAL_CLIENT_PILOT_PROTOCOL_V1: CREATED
```

## BASELINE

```text
S1_FULL_ASSISTED_V1: CLOSED_WITH_LIMITS
S1_FULL_ASSISTED_V1_HARDENING: CLOSED_WITH_SCOPE_NOTE
S1_REAL_CLIENT_PILOT_READINESS_AUDIT_V1: PASS_WITH_OPERATOR_SUPERVISION
```

This protocol does not reopen Servicio 1. It defines the first controlled real-client pilot procedure under operator supervision.

## PILOT TYPE

```text
pilot_type: first_controlled_real_client_case
operator_supervision_required: true
human_review_required: true
runtime_authorized: false
autonomous_use_authorized: false
production_claim_allowed: false
commercial_demo_claim_allowed: false
```

## ACCEPTED INPUT

The first real-client pilot may accept only:

```text
- one known PyME case;
- one real XLSX file, or one tightly scoped workbook set;
- one explicit operational question;
- one supported Servicio 1 family;
- one defined period;
- one identified responsible human reviewer.
```

Client data must remain outside the repository.

## ACCEPTED FIRST QUESTIONS

Allowed question types:

```text
- Quiero revisar precios, costos y margen de esta planilla.
- Quiero ordenar caja diaria con ingresos y egresos declarados.
- Quiero ordenar gastos por concepto/categoría e importe.
- Quiero revisar variaciones visibles de precios de proveedores.
- Quiero una alerta básica de stock sobre valores declarados.
```

Blocked or reduction-required question types:

```text
- Quiero una auditoría.
- Quiero una conciliación bancaria definitiva.
- Quiero cerrar impuestos.
- Quiero asientos contables automáticos.
- Quiero validar todo el negocio.
- Quiero procesar PDFs/fotos/tickets escaneados.
- Quiero conectar bancos, Mercado Pago o Mercado Libre.
- Quiero que el sistema responda solo al cliente.
```

## SUPPORTED TOOL FAMILIES FOR PILOT 1

```text
precio_margen_basico
caja_diaria_triage
gastos_triage
proveedores_precio_variacion_triage
stock_alertas_basicas
```

`stock_alertas_basicas` is allowed as runtime/pipeline/delivery capability, but its synthetic case bank coverage remains PARTIAL. Do not claim full synthetic fixture coverage for stock.

## PRE-RUN CHECKLIST

```text
[ ] Client/case identified.
[ ] Human reviewer identified.
[ ] XLSX stored outside repo.
[ ] Period defined.
[ ] Problem/question written in one sentence.
[ ] Supported family selected by operator.
[ ] No credentials, tokens, keys, APIs, bank access, MP/ML access, OCR or PDF parser requested.
[ ] Owner expectation reduced to operational draft.
[ ] Stop conditions reviewed.
```

## TOOL REQUESTS RULE

Tools must be selected explicitly by the operator. The CLI must not infer tool selection from vague owner language.

Tool request JSON shape:

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

Only allowlisted `tool_ref` values may be used.

## CANONICAL CLI COMMAND

From repo root:

```powershell
cd E:\BuenosPasos\smartbridge\PymIA\PymIA-Live
python -m pymia.cli.service_1_operator --file "E:\RUTA_EXTERNA_CLIENTE\archivo_cliente.xlsx" --run-tools "E:\RUTA_EXTERNA_CLIENTE\tool_requests.json"
```

Allowed CLI behavior:

```text
- read real XLSX structure;
- generate column confirmation packet when needed;
- run explicit allowlisted tools only when --run-tools is provided;
- generate canonical delivery folder;
- generate XLSX operational draft outputs;
- generate pipeline_result.json;
- generate operator_packet.json;
- generate post_tool_owner_delivery_summary.md;
- generate final_qa_delivery_gate.json;
- generate human_review_gate.json;
- keep runtime_authorized=false.
```

## REQUIRED STOP POINT

The first real-client pilot must stop before client delivery at:

```text
final_qa_delivery_gate.status = PASS
final_qa_delivery_gate.delivery_status = READY_FOR_HUMAN_REVIEW
human_review_gate.status = PENDING_HUMAN_REVIEW
runtime_authorized = false
```

If any of these fields are missing or inconsistent, block the pilot output.

## POST-RUN REVIEW CHECKLIST

```text
[ ] Case folder exists.
[ ] operator_packet.json exists.
[ ] pipeline_result.json exists if tools were run.
[ ] post_tool_owner_delivery_summary.md exists if tools were run.
[ ] final_qa_delivery_gate.json exists.
[ ] human_review_gate.json exists.
[ ] manifest.json exists.
[ ] XLSX outputs open correctly.
[ ] XLSX outputs contain limitations/claims prohibidos.
[ ] Owner summary says operational draft / revisión inicial.
[ ] Owner summary does not claim final diagnosis or accounting/tax validity.
[ ] Missing inputs or invalid inputs are visible when present.
[ ] Human reviewer signs off outside autonomous runtime before any client-facing delivery.
```

## OWNER-FACING LANGUAGE

Allowed wording:

```text
Esto es una revisión inicial sobre la evidencia declarada.
El archivo es un borrador operativo para revisión humana.
Hay señales/faltantes que conviene revisar antes de tomar decisiones.
No reemplaza revisión contable, fiscal ni humana.
```

Blocked wording:

```text
El sistema auditó.
El sistema certificó.
El resultado es exacto.
La conciliación está cerrada.
El diagnóstico es final.
Esto reemplaza al contador.
La entrega está aprobada automáticamente.
```

## BLOCK CONDITIONS

Block the pilot if:

```text
- no human reviewer is identified;
- the file is not XLSX;
- the case requires OCR/PDF/API/external system access;
- the question is too broad and cannot be reduced;
- the owner expects audit/certification/fiscal validation;
- the tool family is unsupported;
- tool_requests.json contains unsupported tool_ref;
- outputs imply final diagnosis or final accounting result;
- final QA does not pass;
- human_review_gate is not PENDING_HUMAN_REVIEW;
- runtime_authorized is true anywhere.
```

## PILOT RECORD

After the run, create a private operator note outside client data containing:

```text
case_alias:
period:
input_file_name_only:
selected_family:
tool_refs_run:
case_folder_path:
final_qa_status:
human_review_gate_status:
reviewer_name:
delivery_decision:
blocked_reason_if_any:
next_safe_action:
```

Do not commit real client XLSX or generated client outputs to the repo.

## FINAL POSITION

```text
READY_TO_RUN_FIRST_CONTROLLED_REAL_CLIENT_PILOT
```

This protocol authorizes one supervised pilot run, not open production use, not autonomous delivery, and not a commercial launch.
