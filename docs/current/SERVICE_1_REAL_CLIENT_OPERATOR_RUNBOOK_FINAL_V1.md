# SERVICE_1_REAL_CLIENT_OPERATOR_RUNBOOK_FINAL_V1

## VERDICT

```text
SERVICE_1_REAL_CLIENT_OPERATOR_RUNBOOK_FINAL_V1: READY_FOR_CONTROLLED_REAL_CLIENT_USE
```

## PURPOSE

Este runbook gobierna la ejecución operativa de Servicio 1 XLSX-first sobre un caso real con dueño PyME.

Define qué recibe el operador, qué verifica, qué ejecuta, cómo interpreta estados, qué artefactos entrega internamente y qué **no** debe prometer al cliente.

No reemplaza criterio humano. No autoriza entrega autónoma.

## NON_GOALS

- No hace delivery autónomo al cliente.
- No produce diagnóstico definitivo.
- No reemplaza al contador.
- No es SaaS, no tiene frontend, no expone API.
- No crea parser XLSX nuevo.
- No hace OCR, conciliación definitiva ni Servicio 2.
- No amplía promesas comerciales.

## OPERATOR PRINCIPLE

La IA conversa.
PymIA computa.
Las tools ejecutan.
Los archivos son el producto.
El operador humano controla la entrega.

## INPUTS REQUIRED

| Campo | Obligatorio | Descripción |
|---|---|---|
| `tenant_id` | Sí | Identificador del tenant PyME |
| `case_id` | Sí | Identificador del caso |
| `owner_ref` | Sí | Referencia del dueño |
| `raw_owner_narrative` | Sí | Narrativa del dueño (qué le preocupa, qué período, qué decisión necesita) |
| `business_period_reference` | Recomendado | Período de negocio (ej. `"2026-06"`) |
| `column_meaning_confirmations` | Recomendado | Lista de confirmaciones de columnas (ej. `"precio=precio de venta"`) |
| `ingestion_output` | Sí | Diccionario con `available_data_fields`, `input_values` y `source_file_ref` |
| `source_file_ref` | Sí | Referencia al archivo XLSX (no se copia a la carpeta) |
| `metadata` | Opcional | Notas del operador, referencias internas |

## PRE-RUN CHECKLIST

Antes de ejecutar, verificar:

- [ ] Repo en `main`, limpio, actualizado.
- [ ] Archivo XLSX recibido y referenciado (no copiado manualmente a la carpeta de entrega).
- [ ] `tenant_id`, `case_id`, `run_id` identificados.
- [ ] Período de negocio claro.
- [ ] Narrativa del dueño no vacía.
- [ ] `ingestion_output` generado o disponible vía `service_1_document_ingestion_to_xlsx_runtime_bridge_adapter_v1`.
- [ ] `source_file_ref` presente.
- [ ] Límites de alcance confirmados: salida operativa preliminar, sin diagnóstico definitivo.

## EXECUTION FLOW

### Paso 1: Recibir y registrar

Registrar identifiers del caso:

```text
tenant_id, case_id, intake_id, run_id, owner_ref
```

### Paso 2: Generar o recibir ingestion_output

Si ya existe output de ingesta, usarlo directamente.

Si no, ejecutar ingesta vía el adapter de documento:

```text
COMMAND_PLACEHOLDER: generar ingestion_output
```

### Paso 3: Ejecutar real owner pilot case run

```python
from pymia.smartpyme.service_1_real_owner_pilot_case_run_v1 import (
    build_service_1_real_owner_pilot_case_run_v1,
)

pilot = build_service_1_real_owner_pilot_case_run_v1(
    case_id="...",
    tenant_id="...",
    intake_id="...",
    run_id="...",
    owner_ref="...",
    raw_owner_narrative="...",
    ingestion_output={...},
    business_period_reference="...",
    column_meaning_confirmations=[...],
    metadata={"operator": "..."},
)
```

### Paso 4: Revisar estado del piloto

Consultar `pilot.status` y `pilot.decision_checklist`.

Ver tabla de interpretación de estados abajo.

### Paso 5: Construir delivery packet (solo si READY)

```python
from pymia.smartpyme.service_1_real_owner_pilot_to_delivery_packet_adapter_v1 import (
    build_service_1_real_owner_pilot_to_delivery_packet_adapter_v1,
)

adapter = build_service_1_real_owner_pilot_to_delivery_packet_adapter_v1(
    pilot_result=pilot,
    metadata={"operator": "..."},
)

packet = adapter.delivery_packet
```

### Paso 6: Escribir carpeta local de caso

```python
from pymia.smartpyme.service_1_case_delivery_folder_v1 import (
    write_service_1_case_delivery_folder_v1,
)

manifest = write_service_1_case_delivery_folder_v1(
    packet=packet,
    base_dir=".tmp/service_1_cases",
)
```

### Paso 7: Escribir operator_packet.json y finalizar manifest

```python
import json
from pathlib import Path
from pymia.smartpyme.service_1_case_delivery_folder_v1 import (
    finalize_service_1_case_delivery_folder_v1,
)

case_dir = Path(manifest["case_dir"])
(case_dir / "operator_packet.json").write_text(
    json.dumps(packet, indent=2, ensure_ascii=False), encoding="utf-8"
)

final_manifest = finalize_service_1_case_delivery_folder_v1(
    packet=packet,
    case_dir=case_dir,
    files_written=manifest["files_written"],
)
```

### Paso 8: Revisar guards

```text
- product_gate.json: verificar status, runtime_authorized=False, delivery_authorized=False.
- delivery_policy_guard.json: verificar status=PENDING_DELIVERY_POLICY_GUARD.
- manifest.json: verificar delivery_status, hashes, warnings.
- final_qa_delivery_gate.json: verificar checks, blockers.
```

### Paso 9: Decidir próximo paso

Ver tabla de decision outcomes abajo.

## STATUS INTERPRETATION

### Estados del piloto (Service1RealOwnerPilotCaseRunV1)

| Estado | Significado | Acción |
|---|---|---|
| `REAL_OWNER_PACKAGE_CANDIDATE_READY` | Evidencia suficiente, bridge listo | Continuar a delivery packet adapter (Paso 5) |
| `REAL_OWNER_NEEDS_OWNER_INPUT` | Falta evidencia o confirmación del dueño | **No avanzar.** Enviar `next_owner_question` al dueño |
| `REAL_OWNER_BLOCKED` | Bloqueo duro (narrativa vacía, ingesta fallida) | **Detener.** Registrar `blocked_reason`. Corregir entrada |

### Estados del adapter (Service1RealOwnerPilotToDeliveryPacketAdapterV1)

| Estado | Significado | Acción |
|---|---|---|
| `DELIVERY_PACKET_READY_FOR_POLICY_GUARD` | Packet listo para carpeta controlada | Escribir carpeta local (Paso 6). No es entrega final |
| `DELIVERY_PACKET_NEEDS_OWNER_INPUT` | Falta confirmación del dueño | **Detener.** `next_owner_question.md` se escribe en carpeta. Comunicar al dueño |
| `DELIVERY_PACKET_BLOCKED` | Bloqueo operativo | **Detener.** Revisar `blocked_reason`. Corregir evidencia o entrada |
| `DELIVERY_PACKET_INVALID_INPUT` | Input inválido | **Detener.** `pilot_result` no es instancia válida |

## DELIVERY FOLDER EXPECTED ARTIFACTS

Archivos esperados en la carpeta de caso controlado:

| Archivo | Siempre presente | Descripción |
|---|---|---|
| `README.txt` | Sí | Límites del servicio y descripción de archivos |
| `owner_message.md` | Sí | Mensaje visible para el dueño |
| `operator_packet.json` | Sí (escrito por CLI) | Paquete completo gobernado |
| `case_record.json` | Sí | Registro reproducible del caso |
| `owner_delivery_packet.json` | Sí | Paquete legible para el dueño |
| `product_gate.json` | Sí | Gate final de producto |
| `delivery_policy_guard.json` | Sí (en finalize) | Guard de política de entrega |
| `final_qa_delivery_gate.json` | Sí (en finalize) | QA sobre artefactos reales de carpeta |
| `manifest.json` | Sí (en finalize) | Inventario final con hashes |
| `next_owner_question.md` | Solo si `NEEDS_OWNER_INPUT` | Pregunta legible para el dueño |
| `evidence_loop_status.json` | Sí (desde adapter) | Estado del loop evidencia/preguntas |

## HARD BLOCKERS

Detener la ejecución si ocurre **cualquiera** de estos:

- Narrativa del dueño vacía.
- Período de negocio ausente o ambiguo.
- Columnas sin confirmar.
- `ingestion_output` ausente, sin `available_data_fields` o sin `input_values`.
- `source_file_ref` ausente.
- `status == BLOCKED` en piloto o adapter.
- `delivery_authorized == True` en cualquier artefacto.
- `runtime_authorized == True` inesperado.
- Archivo `.xlsx` copiado dentro de la carpeta final.
- Texto con "diagnóstico definitivo", "auditoría", "certificación", "conciliación definitiva", "rentabilidad real confirmada" o "reemplaza al contador" en `owner_message` o `owner_delivery_packet`.
- `final_qa_delivery_gate.status == "BLOCKED"`.

## OWNER COMMUNICATION RULES

### Lenguaje permitido

- "salida operativa preliminar"
- "hallazgo sujeto a evidencia disponible"
- "necesitamos confirmar [X]"
- "con esta evidencia no podemos cerrar [Y]"
- "próximo paso sugerido: [Z]"

### Lenguaje prohibido

- "diagnóstico definitivo"
- "auditoría"
- "certificación"
- "conciliación definitiva"
- "rentabilidad real confirmada"
- "reemplaza al contador"
- "entrega automática"

## QA CHECKLIST BEFORE DELIVERY POLICY GUARD

Antes de considerar el caso listo para control de política de entrega, verificar:

- [ ] Todos los artefactos esperados existen en la carpeta.
- [ ] `manifest.json` existe y contiene hashes.
- [ ] `delivery_policy_guard.json` existe con status `PENDING_DELIVERY_POLICY_GUARD`.
- [ ] `product_gate.json` no autoriza delivery (`delivery_authorized=False`, `runtime_authorized=False`).
- [ ] `final_qa_delivery_gate.json` tiene status `PASS`.
- [ ] No hay archivo `.xlsx` copiado en la carpeta.
- [ ] `owner_message.md` no contiene claims prohibidos.
- [ ] `next_owner_question.md` existe si el caso está en `NEEDS_OWNER_INPUT`.
- [ ] `blocked_reason` documentado si el caso está `BLOCKED`.
- [ ] `decision_checklist` del piloto tiene todos los flags requeridos en `True`.

## DECISION OUTCOMES

Estados finales posibles del operador al cerrar la ejecución:

| Outcome | Condición | Próximo paso |
|---|---|---|
| `READY_FOR_DELIVERY_POLICY_GUARD` | Carpeta escrita, manifest generado, QA PASS | Pasar a control de política de entrega. No entregar al cliente |
| `NEEDS_OWNER_INPUT` | Falta confirmación o evidencia del dueño | Comunicar `next_owner_question`. Esperar respuesta. Re-ejecutar |
| `BLOCKED_BY_EVIDENCE` | Evidencia insuficiente, ingesta fallida, columnas sin confirmar | Solicitar datos faltantes al dueño. Corregir entrada |
| `BLOCKED_BY_POLICY` | Guard bloquea, claim prohibido detectado | Revisar artefactos, corregir lenguaje, re-ejecutar |
| `REWORK_REQUIRED` | QA FAIL, artefactos faltantes, hashes incorrectos | Corregir ejecución, reescribir carpeta |

## COMMIT AND TRACEABILITY

Cada corrida real debe registrar:

| Campo | Ejemplo |
|---|---|
| Commit hash | `ca4726f` |
| Fecha | `2026-07-07` |
| Operador | `operator:001` |
| `tenant_id` | `tenant:pyme:001` |
| `case_id` | `case:s1:owner:001` |
| `run_id` | `run:s1:001` |
| Archivos de entrada | `ingestion/rentabilidad.xlsx` |
| Carpeta generada | `.tmp/service_1_cases/case_case_s1_owner_001` |
| Resultado | `READY_FOR_DELIVERY_POLICY_GUARD` |
| Blockers | Ninguno / `missing_owner_narrative` / etc. |

## FINAL CLOSE CRITERIA

Un caso real de Servicio 1 queda **cerrado operativamente** solo si:

- [ ] Carpeta de caso generada con `write_service_1_case_delivery_folder_v1`.
- [ ] `manifest.json` generado con `finalize_service_1_case_delivery_folder_v1`.
- [ ] `delivery_policy_guard.json` presente.
- [ ] `final_qa_delivery_gate.json` con status evaluado.
- [ ] Sin `delivery_authorized=True` en ningún artefacto.
- [ ] Sin claims prohibidos en `owner_message` ni `owner_delivery_packet`.
- [ ] Operador revisó todos los artefactos.
- [ ] `next_owner_question` o `blocked_reason` documentado si aplica.
- [ ] Próximo paso explícito registrado.

## NEXT STEP

```text
SERVICE_1_OPERATIVE_XLSX_FIRST_CLOSEOUT_V1
```
