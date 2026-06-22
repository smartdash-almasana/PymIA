# SERVICE_1_DEVELOPMENT_AUDIT_AND_COMPLETION_ROADMAP_V1

## Estado

```text
Tipo: DEVELOPMENT_AUDIT_AND_COMPLETION_ROADMAP
Estado: DRAFT_APPLIED
Metodología: Gentle AI Development
Runtime impact: NONE
Code impact: NONE
Tests impact: NONE
```

## Propósito

Este documento consolida la auditoría actual de desarrollo de PymIA Servicio 1 y define un roadmap de completitud pieza por pieza.

Corrige la desactualización entre la documentación previa y el estado real del repo después de los ciclos recientes de File Intake, TaskSpec boundary, OwnerResponse y OwnerMessageFormatter.

No autoriza implementación nueva.
No autoriza runtime.
No autoriza pipeline.
No autoriza FSM nueva.
No autoriza LLM.
No autoriza chatbot.
No autoriza XLSX delivery.

---

# 1. Estado real del repo al cierre de auditoría

## HEAD relevante

```text
9b1737e feat(pymia-live): add service 1 owner message formatter
ed01d01 feat(pymia-live): add service 1 owner response renderer
91f2c46 feat(pymia-live): add service 1 excel triage report contract
89d4a1e docs(pymia-live): freeze service 1 fsm boundary drift
184692f test(pymia-live): cover service 1 boundary chain
46670ca feat(pymia-live): add service 1 fsm decision patch
4a2662b feat(pymia-live): add service 1 taskspec contract
5268ab9 feat(pymia-live): centralize service 1 taskspec vocabulary
b583815 docs(pymia): close column confirmation report wiring
dfd6909 feat(pymia-live): add file intake taskspec boundary
```

## Working tree conocido

```text
?? docs/pymia/ORGANIZATIONAL_CASE_FILE_V1_CONCEPT.md
```

Ese archivo queda fuera de esta auditoría y no debe incorporarse salvo autorización explícita.

---

# 2. Cadena real implementada en Servicio 1

La cadena implementada actual es:

```text
FileIntakeResult
→ TaskSpecPatch
→ OwnerResponseV1
→ OwnerMessageFormatterV1
```

Esta cadena permite una salida owner-facing mínima:

```text
qué se recibió
qué se puede hacer ahora
qué falta
qué no se puede afirmar todavía
próximo paso del dueño
```

Condición central:

```text
runtime_authorized = False
```

No hay ejecución de herramientas.
No hay lectura real XLSX.
No hay diagnóstico.
No hay cálculo.
No hay delivery XLSX.
No hay chatbot.
No hay LLM.

---

# 3. Piezas implementadas relevantes

| Pieza | Archivo | Estado | Rol |
|---|---|---|---|
| File Intake V1 | `PymIA-Live/pymia/smartpyme/file_intake_v1.py` | IMPLEMENTED_VALIDATED | Clasifica archivo inicial, XLSX-first, bloquea runtime |
| File Intake → TaskSpec Boundary | `PymIA-Live/pymia/smartpyme/file_intake_taskspec_boundary_v1.py` | IMPLEMENTED_VALIDATED | Produce patch técnico desde FileIntakeResult |
| TaskSpec Vocabulary V1 | `PymIA-Live/pymia/smartpyme/service_1_taskspec_vocabulary_v1.py` | IMPLEMENTED | Centraliza estados/acciones |
| Service1TaskSpec Contract V1 | `PymIA-Live/pymia/smartpyme/service_1_taskspec_contract_v1.py` | IMPLEMENTED | Define contrato TaskSpec completo |
| Excel Triage Report V1 | `PymIA-Live/pymia/smartpyme/service_1_excel_triage_report_v1.py` | IMPLEMENTED | Anexo estructurado técnico |
| OwnerResponse Renderer V1 | `PymIA-Live/pymia/smartpyme/owner_response_renderer_v1.py` | IMPLEMENTED_VALIDATED | Salida principal owner-facing mínima |
| OwnerMessage Formatter V1 | `PymIA-Live/pymia/smartpyme/owner_message_formatter_v1.py` | IMPLEMENTED_VALIDATED | Texto plano listo para canal manual |
| FSM Decision Patch V1 | `PymIA-Live/pymia/smartpyme/service_1_fsm_decision_patch_v1.py` | EXPERIMENTAL_FROZEN | Congelado por deriva |
| Boundary Chain V1 | `PymIA-Live/pymia/smartpyme/service_1_boundary_chain_v1.py` | EXPERIMENTAL_FROZEN | Congelado por deriva |

---

# 4. Piezas congeladas

Las siguientes piezas no deben usarse como base para nuevo crecimiento sin auditoría previa:

```text
service_1_fsm_decision_patch_v1.py
service_1_boundary_chain_v1.py
```

Motivo:

```text
Se detectó riesgo de deriva hacia FSM/pipeline/runtime prematuros.
```

Decisión:

```text
Mantener como evidencia experimental congelada.
No seguir expandiéndolas.
No conectarlas.
No usarlas para abrir runtime.
```

---

# 5. Diferencias contra Capability Matrix V1

La matriz previa declara:

```text
Service 1 TaskSpec = MISSING
```

Pero el repo ya contiene:

```text
service_1_taskspec_vocabulary_v1.py
service_1_taskspec_contract_v1.py
file_intake_taskspec_boundary_v1.py
```

Por lo tanto:

```text
Capability Matrix V1 está desactualizada.
```

Corrección recomendada:

```text
Service 1 TaskSpec = IMPLEMENTED_PARTIAL / IMPLEMENTED_FOCAL
```

Motivo:

```text
Existe contrato y vocabulario, pero falta assembler completo y conexión controlada con piezas posteriores.
```

---

# 6. Estado de completitud contra Producto Servicio 1 Full

Servicio 1 full incluye:

```text
Primeros Auxilios
Laboratorio Excel
Factoría Excel
Excel descargables con fórmulas
Servicios para contadores
Conciliaciones
PDF/CSV/Excel a Excel normalizado
Chatbot operativo con IA bajo arnés
```

Estado real actual:

| Familia | Estado real | Brecha |
|---|---|---|
| Primeros Auxilios | Foundation owner-facing lista | Falta tool ejecutable y entregable XLSX |
| Laboratorio Excel | Implementación parcial existente en document_ingestion | Falta empaquetado como producto Servicio 1 |
| Factoría Excel | Parcial en Exceland/exeland2 | Falta bridge controlado |
| Excel descargables | Documentado | Falta XLSX Delivery V1 |
| Servicios contadores | Definido/documentado | Falta contrato operativo inicial |
| Conciliaciones | Parcial/documentado | Falta Bank Reconciliation Contract V1 |
| PDF/CSV/Excel normalizado | Parcial | PDF todavía missing / no evidenciado |
| Chatbot operativo | Documentado / needs wiring | No abrir antes de FSM + pipeline + LLM adapter |

---

# 7. Veredicto de auditoría

```text
SERVICE_1_CURRENT_STATUS:
FOUNDATION_OWNER_OUTPUT_READY
NOT_FULL_PRODUCT_READY
ROADMAP_DOCS_OUTDATED
NEXT_REQUIRED: GENTLE_AI_COMPLETION_LOOP
```

Interpretación:

```text
Servicio 1 ya tiene una primera salida owner-facing honesta y testeada.
Servicio 1 todavía no tiene archivo entregable ni tool ejecutable.
La documentación previa debe actualizarse para reflejar los commits recientes.
El avance debe continuar pieza por pieza bajo Gentle AI Development.
```

---

# 8. Gentle AI Development Loop para Servicio 1

Metodología obligatoria:

```text
DESIGN
→ BUILD
→ TEST
→ AUDIT
→ HUMAN STOP
→ COMMIT/PUSH
→ NEXT CYCLE
```

Regla madre:

```text
Una pieza por ciclo.
Una frontera por pieza.
Un contrato por pieza si corresponde.
Tests focales por pieza.
Auditoría posterior obligatoria.
Freno humano antes del siguiente ciclo.
Commit atómico por pieza.
No avanzar por impulso ni por acumulación de features.
```

## Fases del loop

### DESIGN

Definir la pieza mínima:

```text
input
output
contrato
archivos permitidos
archivos prohibidos
tests esperados
claims prohibidos
condición PASS/BLOCKED
```

### BUILD

Implementar sólo lo autorizado.

Reglas:

```text
no runtime salvo autorización explícita
no pipeline salvo ciclo correspondiente
no FSM salvo ciclo correspondiente
no LLM
no chatbot
no tocar vecinos
```

### TEST

Ejecutar tests focales de la pieza y frontera inmediata.

### AUDIT

Auditar contra:

```text
TaskSpec del ciclo
Producto Servicio 1 full
Capability Matrix actualizada
fronteras Servicio 1 / Servicio 2 / Servicio 3
claims permitidos/prohibidos
```

### HUMAN STOP

El usuario decide:

```text
KEEP
PATCH
FREEZE
REVERT
COMMIT
PUSH
```

### COMMIT/PUSH

Sólo si el ciclo termina en:

```text
PASS
PASS_WITH_NOTES
```

---

# 9. Roadmap V2 pieza por pieza

| Ciclo | Pieza | Fase Gentle AI | Tipo | Output | Tests esperados | Auditoría requerida | Freno humano | Riesgo | Condición de cierre |
|---:|---|---|---|---|---|---|---|---|---|
| 0 | SERVICE_1_DEVELOPMENT_AUDIT_AND_COMPLETION_ROADMAP_V1 | DESIGN/AUDIT | DOC | Roadmap actualizado | No aplica | Sí | Sí | Bajo | Documento creado |
| 1 | SERVICE_1_OWNER_OUTPUT_CLOSEOUT_V1 | AUDIT/DOC | DOC | Cierre owner-facing | No aplica | Sí | Sí | Bajo | Owner output reconocido como foundation |
| 2 | SERVICE_1_CAPABILITY_MATRIX_V2 | AUDIT/DOC | DOC | Matriz corregida | No aplica | Sí | Sí | Bajo | TaskSpec deja de figurar como MISSING |
| 3 | SERVICE_1_TASKSPEC_ASSEMBLER_V1 | BUILD | CODE | Service1TaskSpec completo desde intake/patch | Tests focales assembler | Sí | Sí | Medio | No runtime autorizado |
| 4 | FIRST_AID_TOOL_RESULT_V1 | BUILD | CONTRACT | Contrato común de resultado de tool | Tests contrato | Sí | Sí | Medio | Formato común cerrado |
| 5 | FIRST_AID_PRECIO_MARGEN_BASICO_V1 | BUILD | CODE | Tool determinística margen básico | Tests cálculo/faltantes/limitaciones | Sí | Sí | Medio | Sin diagnóstico ni rentabilidad real |
| 6 | FIRST_AID_XLSX_DELIVERY_V1 | BUILD | CODE | XLSX descargable desde ToolResult | Tests archivo/hojas mínimas | Sí | Sí | Alto | XLSX determinístico validado |
| 7 | FIRST_AID_CAJA_DIARIA_TRIAGE_V1 | BUILD | CODE | Tool caja diaria simple | Tests cálculo/faltantes/limitaciones | Sí | Sí | Medio | No afirmar saldo bancario real |
| 8 | FIRST_AID_STOCK_ALERTAS_BASICAS_V1 | BUILD | CODE | Tool alerta stock mínima | Tests alerta/faltantes/limitaciones | Sí | Sí | Medio | No afirmar stock físico real |
| 9 | SERVICE_1_PIPELINE_V1 | BUILD | CODE | Pipeline propio Servicio 1 | Tests integración mínima | Sí | Sí | Alto | No usar vertical_pipeline como expansión caótica |
| 10 | SERVICE_1_FSM_V1 | BUILD | CODE | FSM real de Servicio 1 | Tests estados/transiciones | Sí | Sí | Alto | No reabrir módulos congelados sin auditoría |
| 11 | EXCELAND_BRIDGE_V1 | BUILD | CODE | Puente controlado a templates/specs | Tests bridge | Sí | Sí | Alto | No migrar Exceland entero |
| 12 | BANK_RECONCILIATION_CONTRACT_V1 | DESIGN/BUILD | CONTRACT | Contrato conciliación bancaria | Tests contrato | Sí | Sí | Alto | Sin ejecución hasta contrato cerrado |
| 13 | WORKPAPER_XLSX_V1 | BUILD | CODE | Workpaper XLSX estándar | Tests hojas/schema | Sí | Sí | Alto | Depende de delivery estable |
| 14 | LLM_ADAPTER_V1 | DESIGN/BUILD | CONTRACT/CODE | IA bajo arnés | Tests outputs permitidos/prohibidos | Sí | Sí | Alto | IA no calcula ni concilia |
| 15 | CHATBOT_OPERATIVO_SERVICE_1_V1 | BUILD | WIRING | Interfaz conversacional | Tests de flujo | Sí | Sí | Alto | Sólo después de FSM/pipeline/adapter |

---

# 10. Reglas de avance

```text
DESIGN antes de BUILD.
BUILD sólo sobre archivos autorizados.
TEST focal antes de auditoría.
AUDIT antes de commit.
HUMAN STOP antes de nuevo ciclo.
COMMIT/PUSH sólo con PASS o PASS_WITH_NOTES.
```

Reglas adicionales:

```text
No git add .
No tocar docs/pymia/ORGANIZATIONAL_CASE_FILE_V1_CONCEPT.md.
No mezclar docs + runtime + refactor en el mismo ciclo salvo autorización explícita.
No abrir pipeline antes de tool result + primera tool + delivery.
No abrir chatbot antes de FSM + pipeline + LLM adapter.
No activar Servicio 2 desde Servicio 1.
No diagnosticar empresa como sistema desde Servicio 1.
```

---

# 11. Próximo ciclo recomendado

## Ciclo 1

```text
SERVICE_1_OWNER_OUTPUT_CLOSEOUT_V1
```

Tipo:

```text
DOC/AUDIT ONLY
```

Objetivo:

```text
Declarar formalmente que OwnerResponseV1 + OwnerMessageFormatterV1 constituyen la primera salida owner-facing mínima de Servicio 1.
```

Debe dejar claro:

```text
No es diagnóstico.
No es XLSX delivery.
No es pipeline.
No es chatbot.
No es runtime.
Es salida inicial vendible/asistida/manual.
```

Condición de cierre:

```text
Documento creado.
No tests.
No runtime.
No código.
Commit atómico sólo del documento si el usuario aprueba.
```

---

# 12. Veredicto final

```text
SERVICE_1_ROADMAP_V2_READY_WITH_GENTLE_AI_LOOP
```
