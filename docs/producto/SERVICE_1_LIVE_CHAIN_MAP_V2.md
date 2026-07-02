# SERVICE_1_LIVE_CHAIN_MAP_V2

## VEREDICTO

```text
SERVICE_1_STATUS: LIVE_CHAIN_UPDATED_AFTER_SEMANTIC_BRIDGES
MAIN_GAP: controlled_execution_candidates → supervised_dry_run_plan
NEXT_FRONT: SERVICE_1_CONTROLLED_EXECUTION_CANDIDATES_TO_SUPERVISED_DRY_RUN_PLAN_V1
```

## RESUMEN

Servicio 1 ya no está cortado entre rectificación semántica y candidatura de herramientas.

Puentes centrales cerrados:

```text
owner_rectified_function → evidence_profile
evidence_profile → candidate_tools
candidate_tools → controlled_execution_candidates
```

La cadena todavía no ejecuta herramientas automáticamente. El próximo gap real es convertir candidatos de ejecución controlada en un plan de dry-run supervisado por operador.

---

## CADENA VIVA ACTUAL

| Etapa | Módulo real | Estado |
|-------|-------------|--------|
| 01. XLSX intake / bridge | `service_1_xlsx_runtime_bridge_contract_v1.py` + CLI | CLOSED |
| 02. Estructura detectada | `service_1_xlsx_structure_v1` + `service_1_xlsx_to_normalized_table_v1` | CLOSED |
| 03. Inferencia semántica PymIA | `ColumnConfirmationEntry.suggested_semantic_role` | CLOSED |
| 04. Rectificación dueño PyME | `classify_owner_column_confirmation_answer()` + `apply_service_1_column_confirmation_v1()` | CLOSED |
| 05. Perfil de evidencia | `service_1_owner_rectified_evidence_profile_v1.py` | CLOSED |
| 06. Candidatura de herramientas | `service_1_evidence_profile_to_candidate_tools_contract_v1.py` | CLOSED |
| 07. Candidatos de ejecución controlada | `service_1_candidate_tools_to_controlled_execution_bridge_v1.py` | CLOSED |
| 08. Plan de dry-run supervisado | NO EXISTE | GAP |
| 09. Phase I execution candidate | `service_1_controlled_client_case_execution_candidate_v1.py` | SEPARATE_PHASE_I_CHAIN |
| 10. Paquete operador | `service_1_operator_delivery_package_v1.py` | CLOSED_WITH_LIMITS |
| 11. Delivery XLSX | `service_1_xlsx_delivery_v1.py` | CLOSED_WITH_LIMITS |
| 12. QA / human review | QA gate + human review gate artifacts | CLOSED_WITH_LIMITS |

---

## COMMITS QUE CORRIGEN EL MAPA V1

```text
bec0427 feat(smartpyme): add owner rectified evidence profile contract
684c3bb docs(producto): close owner rectified evidence profile contract
b71a6db feat(smartpyme): add evidence profile to candidate tools contract
8f69c61 docs(producto): close evidence profile to candidate tools contract
2b3da04 feat(smartpyme): add candidate tools to controlled execution bridge
b22477c docs(producto): close candidate tools to controlled execution bridge
```

`SERVICE_1_LIVE_CHAIN_MAP_V1.md` queda obsoleto porque declaraba como gaps puentes que ya están cerrados.

---

## REGLA SEMÁNTICA VIVA

```text
RAW_HEADER: what file says
PYMIA_INFERRED_FUNCTION: what PymIA proposes
OWNER_RECTIFIED_FUNCTION: what owner confirms/corrects/rejects/qualifies
```

Sólo `owner_rectified_function` puede alimentar evidencia operativa posterior.

No usar headers crudos como evidencia.

No usar `suggested_semantic_role` como verdad operativa.

---

## PUENTES CENTRALES CERRADOS

### 05. owner_rectified_function → evidence_profile

Módulo:

```text
PymIA-Live/pymia/smartpyme/service_1_owner_rectified_evidence_profile_v1.py
```

Produce:

```text
source_columns
evidence_signals
evidence_ready
missing_requirements
blockers
allowed_next_steps
runtime_authorized = false
tool_execution_authorized = false
```

Señales cubiertas:

```text
margen_basico
stock_basico
ventas_cobros_basico
```

### 06. evidence_profile → candidate_tools

Módulo:

```text
PymIA-Live/pymia/smartpyme/service_1_evidence_profile_to_candidate_tools_contract_v1.py
```

Mapeo implementado:

```text
margen_basico         → precio_margen_basico
stock_basico          → stock_alertas_basicas
ventas_cobros_basico  → caja_diaria_triage
```

Garantías:

```text
runtime_authorized = false
tool_execution_authorized = false
executable_tool_requests_authorized = false
autonomous_delivery_authorized = false
```

### 07. candidate_tools → controlled_execution_candidates

Módulo:

```text
PymIA-Live/pymia/smartpyme/service_1_candidate_tools_to_controlled_execution_bridge_v1.py
```

Produce candidatos preparados, no ejecución:

```text
controlled_execution_candidates
execution_authorized = false
execution_executed = false
runtime_authorized = false
tool_execution_authorized = false
executable_tool_requests_authorized = false
pipeline_authorized = false
delivery_authorized = false
autonomous_delivery_authorized = false
llm_authorized = false
```

---

## RELACIÓN CON PHASE I EXECUTION CANDIDATE

Hay dos cadenas que no deben confundirse.

Cadena semántica nueva:

```text
XLSX → structure → inference → owner_rectification → evidence_profile → candidate_tools → controlled_execution_candidates
```

Phase I controlled case chain:

```text
readiness_gate → evidence_packet → operator_supervision → controlled_execution_candidate
```

Módulo Phase I:

```text
PymIA-Live/pymia/smartpyme/service_1_controlled_client_case_execution_candidate_v1.py
```

Decisión vigente:

```text
No integrar directo todavía.
Antes debe existir supervised_dry_run_plan o adapter explícito.
```

---

## HUECO REAL ACTUAL

```text
GAP-004: controlled_execution_candidates → supervised_dry_run_plan
```

Qué falta:

```text
Un contrato puro que tome controlled_execution_candidates preparados y produzca un plan de dry-run supervisado.
```

Debe producir:

```text
supervised_dry_run_plan
ordered_candidate_steps
operator_checklist
required_manual_confirmations
blocked_reasons
execution_authorized = false
execution_executed = false
tool_execution_authorized = false
pipeline_authorized = false
delivery_authorized = false
```

Qué NO debe hacer:

```text
No ejecutar tools.
No llamar pipeline.
No crear delivery.
No integrar Phase I todavía.
No poner execution_authorized=true.
No abrir CLI.
No abrir LLM runtime.
No conectar integraciones externas.
```

---

## ANTI-DERIVA

```text
NO ruteo por headers crudos.
NO usar suggested_semantic_role como verdad operativa.
NO ejecución real automática.
NO tool run.
NO pipeline.
NO CLI nuevo.
NO delivery nuevo.
NO adaptar directo a Phase I con execution_authorized=true.
NO Servicio 2.
NO chatbot.
NO LLM runtime.
NO integraciones externas.
```

---

## TESTS DE REFERENCIA

Última regresión focal del tramo semántico:

```bash
python -m pytest tests/contracts/test_column_confirmation_v1.py tests/smartpyme/test_service_1_column_confirmation_classifier_v1.py tests/smartpyme/test_service_1_column_confirmation_applier_v1.py tests/smartpyme/test_service_1_owner_rectified_evidence_profile_v1.py tests/smartpyme/test_service_1_evidence_profile_to_candidate_tools_contract_v1.py tests/smartpyme/test_service_1_candidate_tools_to_controlled_execution_bridge_v1.py -q
```

Resultado verificado:

```text
101 passed
```

---

## STOP_AND_DECIDE FINAL

```text
DECISIÓN BINARIA:

[ ] ABRIR SERVICE_1_CONTROLLED_EXECUTION_CANDIDATES_TO_SUPERVISED_DRY_RUN_PLAN_V1
[ ] DETENER Y NO TOCAR RUNTIME

ESTADO ACTUAL: STOP_AND_DECIDE
```

---

## CIERRE

```text
SERVICE_1_LIVE_CHAIN_MAP_V2: CREATED
RUNTIME_CODE_CHANGED: NO
TESTS_RUN: NO
COMMIT_READY: YES
```
