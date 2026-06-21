# PYMIA_SERVICE_1_TASKSPEC_V1

## Estado

```text
Tipo: ROADMAP_CYCLE_5
Estado: DRAFT_APPLIED
Runtime impact: NONE
Code impact: NONE
Tests impact: NONE
```

## Propósito

Definir cómo se representa un pedido de usuario dentro de PymIA Servicio 1 antes de ejecutar herramientas, generar XLSX, abrir pipeline o conectar IA.

Este documento transforma un pedido humano en un `TaskSpec` controlado, validable y gobernable por FSM.

---

# 1. Cadena previa

```text
PYMIA_SERVICE_1_ARCHAEOLOGY_AUDIT_V1
→ PYMIA_SERVICE_1_CAPABILITY_MATRIX_V1
→ PYMIA_SERVICE_1_TASKSPEC_V1
```

---

# 2. Tesis

```text
El usuario no pide una tool.
El usuario expresa un problema.
PymIA debe convertir ese problema en una TaskSpec limitada.
```

Regla:

```text
La IA conversa.
La FSM gobierna.
Las tools ejecutan.
Los archivos son el producto.
```

---

# 3. Responsabilidad de TaskSpec

TaskSpec debe capturar:

```text
qué pidió el usuario
qué tipo de tarea parece ser
qué servicio corresponde
qué evidencia mínima falta
qué evidencia ya existe
qué columnas requieren confirmación
qué herramienta podría activarse
qué output se espera
qué claims están prohibidos
qué bloqueos existen
cuál es la próxima acción permitida
```

TaskSpec no ejecuta nada.

---

# 4. Contrato conceptual

```yaml
task_id: string
schema_version: "1.0"
service_name: "SERVICE_1"
service_depth: FIRST_AID | DETERMINISTIC_DIAGNOSIS | ORGANIZATIONAL_LAB | UNKNOWN
task_type: enum
owner_problem: string
owner_requested_output: string | null
source_channel: cli | chat | upload | api | unknown
input_assets: list
candidate_capability: string | null
candidate_tool_ref: string | null
evidence_required: list
evidence_received: list
missing_evidence: list
column_confirmation_required: boolean
column_confirmation_fields: list
requested_formula_refs: list
requested_claims: list
forbidden_claims: list
blocking_state: string | null
next_allowed_action: string
expected_output: object
runtime_authorized: false
notes: list
```

---

# 5. Campos obligatorios

| Campo | Tipo | Obligatorio | Descripción |
|---|---|---:|---|
| `task_id` | string | sí | Identificador único de la tarea. |
| `schema_version` | string | sí | Versión del contrato TaskSpec. |
| `service_name` | string | sí | Debe ser `SERVICE_1`. |
| `service_depth` | enum | sí | Profundidad detectada o requerida. |
| `task_type` | enum | sí | Tipo de tarea normalizada. |
| `owner_problem` | string | sí | Pedido original o síntesis fiel. |
| `input_assets` | list | sí | Archivos o fuentes declaradas. |
| `evidence_required` | list | sí | Evidencia mínima requerida. |
| `evidence_received` | list | sí | Evidencia disponible. |
| `missing_evidence` | list | sí | Evidencia faltante. |
| `blocking_state` | string/null | sí | Bloqueo actual si existe. |
| `next_allowed_action` | string | sí | Próxima acción permitida. |
| `runtime_authorized` | boolean | sí | En V1 debe permanecer `false`. |

---

# 6. Task types iniciales

```text
FIRST_AID_PRICE_MARGIN
FIRST_AID_DAILY_CASH
FIRST_AID_STOCK_ALERT
FIRST_AID_EXPENSES_TRIAGE
FIRST_AID_SUPPLIER_PRICE_VARIATION
FILE_INTAKE_XLSX
FILE_INTAKE_CSV
FILE_INTAKE_PDF
XLSX_DELIVERY
BANK_RECONCILIATION
MERCADO_PAGO_RECONCILIATION
INVOICES_VS_COLLECTIONS
WORKPAPERS
EXCEL_FACTORY_TEMPLATE
COMMERCIAL_MODULE_REQUEST
UNKNOWN
```

---

# 7. Estados de bloqueo

TaskSpec puede quedar bloqueada por:

```text
BLOCKED_MISSING_EVIDENCE
BLOCKED_COLUMN_CONFIRMATION
BLOCKED_RESTRICTED_FORMULA
BLOCKED_FORBIDDEN_CLAIM
BLOCKED_SCOPE_MISMATCH
BLOCKED_UNSUPPORTED_TASK_TYPE
BLOCKED_RUNTIME_NOT_AUTHORIZED
BLOCKED_NEEDS_HUMAN_DECISION
```

---

# 8. Próximas acciones permitidas

```text
ask_owner_for_missing_evidence
ask_owner_to_confirm_columns
present_first_aid_tool_candidate
run_activation_evaluator
prepare_tool_execution_plan
reject_or_escalate_scope
create_excel_spec_draft
wait_for_human_decision
```

En V1 ninguna de estas acciones ejecuta runtime productivo.

---

# 9. Input assets

Cada asset debe representarse así:

```yaml
asset_id: string
asset_type: xlsx | csv | pdf | zip | image | text | unknown
filename: string | null
source: upload | path | message | api | unknown
classification_status: classified | needs_classification | unsupported
risk_flags: list
notes: list
```

---

# 10. Evidence fields

Cada evidencia debe representarse así:

```yaml
field_id: string
label: string
source_asset_id: string | null
value_status: present | missing | ambiguous | unconfirmed
requires_owner_confirmation: boolean
notes: list
```

---

# 11. Expected output

```yaml
expected_output:
  output_type: owner_answer | xlsx | workpaper_xlsx | normalized_table | evidence_request | blocked_notice
  downloadable_file_expected: boolean
  owner_facing_summary_expected: boolean
  technical_annex_expected: boolean
  limitations_required: boolean
```

Regla:

```text
Si output_type=xlsx o workpaper_xlsx, TaskSpec sólo declara intención.
No genera archivo.
```

---

# 12. Ejemplos

## 12.1 Precio y margen First Aid

Pedido:

```text
Quiero revisar si este precio me deja margen.
```

TaskSpec:

```yaml
task_id: task_001
schema_version: "1.0"
service_name: SERVICE_1
service_depth: FIRST_AID
task_type: FIRST_AID_PRICE_MARGIN
owner_problem: "Quiero revisar si este precio me deja margen."
owner_requested_output: "revisión de precio y margen"
source_channel: chat
input_assets: []
candidate_capability: precio_margen_basico
candidate_tool_ref: precio_margen_basico
evidence_required:
  - precio_venta
  - costo_unitario
evidence_received:
  - precio_venta
missing_evidence:
  - costo_unitario
column_confirmation_required: false
column_confirmation_fields: []
requested_formula_refs:
  - margen_bruto
requested_claims: []
forbidden_claims:
  - rentabilidad real confirmada
blocking_state: BLOCKED_MISSING_EVIDENCE
next_allowed_action: ask_owner_for_missing_evidence
expected_output:
  output_type: evidence_request
  downloadable_file_expected: false
  owner_facing_summary_expected: true
  technical_annex_expected: false
  limitations_required: true
runtime_authorized: false
notes:
  - "No calcular margen sin costo_unitario."
```

---

## 12.2 Caja diaria con columnas dudosas

Pedido:

```text
No me cierra la caja del día.
```

TaskSpec:

```yaml
task_id: task_002
schema_version: "1.0"
service_name: SERVICE_1
service_depth: FIRST_AID
task_type: FIRST_AID_DAILY_CASH
owner_problem: "No me cierra la caja del día."
owner_requested_output: "revisión inicial de caja"
source_channel: upload
input_assets:
  - asset_id: asset_001
    asset_type: xlsx
    filename: caja.xlsx
    source: upload
    classification_status: classified
    risk_flags:
      - ambiguous_headers
    notes: []
candidate_capability: caja_diaria_triage
candidate_tool_ref: caja_diaria_triage
evidence_required:
  - saldo_inicial
  - ingresos
  - egresos
evidence_received:
  - saldo_inicial
  - ingresos
  - egresos
missing_evidence: []
column_confirmation_required: true
column_confirmation_fields:
  - ingresos
requested_formula_refs:
  - flujo_caja_neto
requested_claims: []
forbidden_claims:
  - saldo bancario conciliado con una sola fuente
blocking_state: BLOCKED_COLUMN_CONFIRMATION
next_allowed_action: ask_owner_to_confirm_columns
expected_output:
  output_type: evidence_request
  downloadable_file_expected: false
  owner_facing_summary_expected: true
  technical_annex_expected: false
  limitations_required: true
runtime_authorized: false
notes:
  - "No calcular caja hasta confirmar columna ingresos."
```

---

# 13. Relación con First Aid Activation Evaluator

TaskSpec alimenta al evaluator, pero no lo reemplaza.

```text
TaskSpec dice qué parece pedir el usuario.
Activation Evaluator decide si una tool First Aid es conceptualmente activable.
```

Flujo conceptual:

```text
owner_problem
→ TaskSpec
→ activation_input
→ evaluate_first_aid_tool_activation(...)
→ activation_status
```

---

# 14. Relación con FSM

La FSM debe usar TaskSpec como input de gobierno.

Ejemplo:

```text
LISTENING
→ TASK_CLASSIFIED
→ EVIDENCE_REQUESTED
→ CONFIRMATION_REQUIRED
→ PROCESSING
→ DELIVERY_READY
→ CLOSED
```

En V1:

```text
TaskSpec documenta estados posibles.
No implementa FSM.
```

---

# 15. Reglas de seguridad

```text
No ejecutar tools desde TaskSpec.
No generar XLSX desde TaskSpec.
No permitir runtime_authorized=true en V1.
No usar IA para cálculo.
No usar IA para conciliación definitiva.
No permitir claims fiscales/contables definitivos.
No saltar evidencia faltante.
No resolver columnas ambiguas sin dueño.
```

---

# 16. Próximo paso recomendado

```text
PYMIA_SERVICE_1_TASKSPEC_CONTRACT_JSON_V1
```

Objetivo:

```text
Crear un contrato JSON o Python TypedDict para TaskSpec, con tests contractuales mínimos.
```

Condición:

```text
Sin pipeline.
Sin runtime.
Sin XLSX.
Sin LLM adapter.
```

---

# 17. Veredicto

```text
PYMIA_SERVICE_1_TASKSPEC_V1 = DRAFT_APPLIED
```

Condición:

```text
Este documento habilita contrato TaskSpec, no ejecución productiva.
```
