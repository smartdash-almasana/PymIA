# SERVICE_1_LIVE_CHAIN_MAP_V1

## VEREDICTO

```text
SERVICE_1_STATUS: LIVE_CHAIN_MAPPED
MAIN_GAP: owner_rectified_function → evidence_profile (bridge missing)
NEXT_FRONT: SERVICE_1_OWNER_RECTIFIED_EVIDENCE_PROFILE_CONTRACT_V1
```

Servicio 1 no es un solo sistema integrado de punta a punta. Es una cadena con dos tramos
claramente cerrados — intake semántico y delivery asistido — separados por un puente
faltante en el centro de la cadena: la conversión de función semántica rectificada en
perfil de evidencia computable.

---

## CADENA VIVA ACTUAL

| Etapa | Módulo real | Entrada | Salida | Estado | Evidencia |
|-------|-------------|---------|--------|--------|-----------|
| 01. XLSX intake / bridge | `service_1_xlsx_runtime_bridge_contract_v1.py` + CLI | XLSX real, case_ref, operator_ref | normalized_headers, row_count, column_count, structure | **CLOSED** | 42/42 tests, CLI funcional |
| 02. Estructura detectada | `service_1_xlsx_structure_v1` + `service_1_xlsx_to_normalized_table_v1` | XLSX path, sheet_name | structure dict, normalized table | **CLOSED** | Reusado por bridge contract |
| 03. Inferencia semántica PymIA | `ColumnConfirmationEntry.suggested_semantic_role` + `infer_calculation_relevance()` | headers, structure, value samples, rubro | suggested_semantic_role, calculation_relevance, owner_question | **CLOSED** | Contrato en `column_confirmation_v1.py:108` |
| 04. Rectificación del dueño PyME | `classify_owner_column_confirmation_answer()` + `apply_service_1_column_confirmation_v1()` | raw owner text, target_ref, proposed_role | owner_rectified_function, semantic_rectification_status | **CLOSED** | 73/73 tests, regresión veriﬁcada en `524781c` |
| 05. Perﬁl de evidencia | **NO EXISTE** | owner_rectified_function + XLSX data | computed_variables, evidence_profile | **GAP** | — |
| 06. Selección/candidatura de herramienta | **NO EXISTE** | evidence_profile, capability catalog | tool_requests allowlisted | **GAP** | Depende de resolver etapa 05 |
| 07. Ejecución controlada | `service_1_controlled_client_case_execution_candidate_v1.py` (Phase I) | readiness_gate, evidence_packet, operator_supervision | execution_candidate, run_result | **DESIGN_ONLY** | Existe en cadena Phase I, NO integrado con cadena semántica |
| 08. Paquete operador | `service_1_operator_delivery_package_v1.py` | harness_run, package_root | operator_package.zip + manifest SHA256 | **CLOSED** | Commit `2bac163` baseline |
| 09. Delivery XLSX | `service_1_xlsx_delivery_v1.py` | Service1XlsxDeliveryInputV1, output_path | XLSX determinístico (7 sheets) | **CLOSED** | 198 líneas, sin fórmulas, sin macros |
| 10. QA / human review | `final_qa_delivery_gate.json` + `human_review_gate.json` | delivery artifacts | PASS o BLOCKED, human_review_required=true | **CLOSED** | runtime_authorized=false |

---

## LO QUE YA ESTÁ CERRADO

- **Intake XLSX real**: puente CLI → lectura → normalización → estructura. 42 tests.
- **Cadena semántica completa pre-evidencia**: RAW_HEADER → PYMIA_INFERRED_FUNCTION → OWNER_RECTIFIED_FUNCTION con cinco estados contractuales (`INFERRED_NOT_RECTIFIED`, `OWNER_CONFIRMED_AS_INFERRED`, `OWNER_RECTIFIED_TO_NEW_FUNCTION`, `OWNER_REJECTED`, `BLOCKED_UNNORMALIZABLE_OWNER_RESPONSE`). 73 tests.
- **Delivery asistido**: XLSX determinístico de 7 sheets + paquete operador con SHA256 + QA gate + human review gate.
- **Phase I controlled case chain**: readiness gate → evidence packet → operator supervision → execution candidate → run result → abort/rollback → delivery review. 79 tests. Cerrada como CANDIDATE_CHAIN_COMPOSITION.
- **Herramientas allowlisted existentes**: precio_margen_basico, stock_alertas_basicas, caja_diaria_triage, gastos_triage, proveedores_precio_variacion_triage (operativas con caveats documentados).

---

## LO QUE ESTÁ PARCIAL

- **StructuredEvidence legacy**: `excel_lab_ingestion_v1.py` + `StructuredEvidence` (`evidence_v1.py`) + `vertical_pipeline.py` computan `computed_variables`, pero NO consumen `owner_rectified_function`. Funcionan sobre el modelo viejo de mapping directo por headers, sin pasar por la cadena semántica nueva. **No integrado con la cadena viva.**
- **Phase I execution candidate**: diseñado y testeado, pero opera sobre su propia cadena (readiness→evidence→supervision→execution), no sobre la cadena semántica (xlsx→structure→infer→rectify→profile→tools).
- **Catálogo Excel Factory**: definido como catálogo comercial inicial (`SERVICE_1_EXCEL_FACTORY_COMMERCIAL_CATALOG_V1.md`) pero sin integración runtime con la cadena semántica.

---

## HUECOS REALES

### GAP-001: owner_rectified_function → evidence_profile (CRÍTICO)

**Qué falta**: un contrato que tome las entradas de `ColumnConfirmationMatrix` con `owner_rectified_function` ya confirmadas, las cruce con los datos normalizados del bridge XLSX, y produzca:

- `computed_variables` (valores numéricos derivados de columnas confirmadas)
- `evidence_profile` (estructura que agrupa variables por familia: ventas, costos, márgenes, stock, pagos)
- `missing_inputs` (variables que no se pueden computar por falta de columnas o rectificación pendiente)
- `limitations` (qué no se puede afirmar con la evidencia disponible)

**Por qué falta**: el legacy `StructuredEvidence` computa variables sobre el modelo viejo de mapping sin pasar por rectificación del dueño. El nuevo modelo semántico (RAW_HEADER → INFERRED → RECTIFIED) está cerrado hasta `owner_rectified_function`, pero no hay módulo que consuma esa salida hacia computación.

**Qué lo bloquea**: nada técnico. Es un gap de integración entre dos tramos cerrados.

### GAP-002: evidence_profile → candidate_tools (DEPENDE DE GAP-001)

**Qué falta**: un contrato que tome un `evidence_profile` y decida qué herramientas allowlisted aplicar, en qué orden, con qué columnas como inputs.

**Por qué falta**: sin `evidence_profile` no hay sobre qué decidir.

### GAP-003: candidate_tools → controlled execution (DEPENDE DE GAP-002)

**Qué falta**: integrar la cadena de ejecución controlada de Phase I (`execution_candidate`, `run_result`, `abort_rollback`) con las tool requests generadas desde el evidence profile.

**Por qué falta**: Phase I está diseñada como cadena de caso genérica, no como consumidora de la cadena semántica XLSX→tools.

---

## PRÓXIMO PUENTE RECOMENDADO

```text
SERVICE_1_OWNER_RECTIFIED_EVIDENCE_PROFILE_CONTRACT_V1
```

### Qué consume

- `ColumnConfirmationMatrix` con entradas que tengan `owner_rectified_function` definida y `confirmation_status == CONFIRMED`
- Datos normalizados del bridge XLSX (`normalized_headers`, `row_count`, `column_count`)
- `_CALCULATION_FEEDING_LABELS` y `_VARIABLE_REQUIRED_LABELS` ya definidos en `column_confirmation_v1.py:62` y `column_confirmation_v1.py:329`

### Qué produce

- `computed_variables: dict[str, float]` — variables numéricas derivadas sólo de columnas con función operativa confirmada
- `evidence_profile` — agrupación de variables por familia (ventas, costos, márgenes, stock, pagos, cantidades)
- `missing_inputs: list[str]` — qué variables no se pudieron computar
- `limitations: list[str]` — qué no se puede afirmar

### Qué NO debe hacer

- No debe ejecutar tools
- No debe generar delivery XLSX
- No debe autorizar runtime
- No debe consumir módulos legacy (`excel_lab_ingestion_v1.py`, `StructuredEvidence`) — debe ser contrato nuevo, focal, mínimo
- No debe abrir Servicio 2 ni Phase J

### Por qué es el puente correcto

Es el único gap que bloquea la cadena completa. Sin este puente, la rectificación semántica del dueño no tiene consumidor downstream. Con este puente cerrado, los gaps 002 y 003 se vuelven abordables en serie sobre una base firme.

---

## ANTI-DERIVA

```text
NO ruteo por headers crudos — usar owner_rectified_function.
NO ejecución todavía — runtime_authorized=false siempre.
NO pipeline rewrite — el viejo vertical_pipeline no se toca.
NO CLI nuevo — el bridge CLI existente alcanza.
NO Servicio 2 — fuera de scope.
NO chatbot — fuera de scope.
NO LLM runtime — fuera de scope.
NO delivery nuevo — service_1_xlsx_delivery_v1 ya existe y alcanza.
NO Phase J — no existe, no se abre.
```

---

## STOP_AND_DECIDE FINAL

```text
DECISIÓN BINARIA:

[ ] ABRIR SERVICE_1_OWNER_RECTIFIED_EVIDENCE_PROFILE_CONTRACT_V1
[ ] DETENER Y NO TOCAR RUNTIME

ESTADO ACTUAL: STOP_AND_DECIDE
```

---

## CIERRE

```text
SERVICE_1_LIVE_CHAIN_MAP_V1: MAPPED
RUNTIME_CODE_CHANGED: NO
TESTS_RUN: NO
COMMIT_READY: YES
```
