# SERVICE_1_DEVELOPMENT_AUDIT_AND_COMPLETION_ROADMAP_V1

## Estado

```text
Tipo: DEVELOPMENT_AUDIT_AND_COMPLETION_ROADMAP
Estado: REALIGNED_ETAPA_0
Metodología: Gentle AI Development
Runtime impact: NONE
Code impact: NONE
Tests impact: NONE
```

## Propósito

Este documento define el objetivo grande de **Servicio 1 full** y, desde esta realineación, debe leerse como **roadmap de target**, no como declaración de cercanía al cierre.

Su función ahora es:

- fijar las 8 familias del objetivo full;
- reconocer que el estado actual sigue siendo parcial;
- convivir sin contradicción con el DoD conservador y con el rector full;
- impedir que avances asistidos parciales se confundan con completitud del producto.

Este documento no autoriza implementación nueva por sí solo.
El orden vigente de cierre queda gobernado por:

```text
SERVICE_1_FULL_CLOSURE_RECTOR_V1
```

---

# 1. Estado real del repo al cierre de auditoría

## HEAD relevante verificado en esta realineación

```text
33907be docs(pymia): add service 1 full closure rector
e9747fe test(pymia): add service 1 anonymized real case harness
607063b test(pymia): add service 1 synthetic final case run
c1c319d test(pymia): add service 1 local first aid functional e2e
```

## Working tree conocido

```text
?? docs/pymia/ORGANIZATIONAL_CASE_FILE_V1_CONCEPT.md
```

Ese archivo queda fuera de esta auditoría y no debe incorporarse salvo autorización explícita.

---

# 2. Capacidad real implementada al día de hoy

Hay dos niveles probados que NO deben confundirse con el full:

## 2.1 Foundation owner-facing mínima

```text
FileIntakeResult
→ TaskSpecPatch
→ OwnerResponseV1
→ OwnerMessageFormatterV1
```

## 2.2 Lane asistida local de First Aid / operator CLI

```text
XLSX real
→ intake
→ structure reader
→ column confirmation packet
→ confirmed columns
→ first aid mínimo
→ QA delivery gate
→ carpeta de caso
```

Esto prueba una punta operativa real y útil.

No prueba todavía:

```text
Servicio 1 full
Laboratorio Excel productizado
Factoría Excel cerrada
XLSX con fórmulas
runtime contable
conciliaciones runtime
PDF/CSV normalizado
chatbot con IA arneada
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

# 3. Piezas implementadas relevantes para NO sobreclaimar

| Pieza | Archivo | Estado | Rol |
|---|---|---|---|
| File Intake V1 | `PymIA-Live/pymia/smartpyme/file_intake_v1.py` | IMPLEMENTED_VALIDATED | Clasifica archivo inicial, XLSX-first, bloquea runtime |
| File Intake → TaskSpec Boundary | `PymIA-Live/pymia/smartpyme/file_intake_taskspec_boundary_v1.py` | IMPLEMENTED_VALIDATED | Produce patch técnico desde FileIntakeResult |
| TaskSpec Vocabulary V1 | `PymIA-Live/pymia/smartpyme/service_1_taskspec_vocabulary_v1.py` | IMPLEMENTED | Centraliza estados/acciones |
| Service1TaskSpec Contract V1 | `PymIA-Live/pymia/smartpyme/service_1_taskspec_contract_v1.py` | IMPLEMENTED | Define contrato TaskSpec completo |
| Excel Triage Report V1 | `PymIA-Live/pymia/smartpyme/service_1_excel_triage_report_v1.py` | IMPLEMENTED | Anexo estructurado técnico |
| OwnerResponse Renderer V1 | `PymIA-Live/pymia/smartpyme/owner_response_renderer_v1.py` | IMPLEMENTED_VALIDATED | Salida principal owner-facing mínima |
| OwnerMessage Formatter V1 | `PymIA-Live/pymia/smartpyme/owner_message_formatter_v1.py` | IMPLEMENTED_VALIDATED | Texto plano listo para canal manual |
| First Aid pipeline / assisted operator lane | `PymIA-Live/pymia/smartpyme/service_1_pipeline_v1.py`, `PymIA-Live/pymia/cli/service_1_operator.py` | IMPLEMENTED_VALIDATED_IN_SCOPE | Pipeline parcial y CLI asistida, no pipeline full |
| Document ingestion script | `tools/document_ingestion.py` | IMPLEMENTED_PARTIAL | Existe, pero sigue fuera de `pymia.smartpyme` |
| Exceland bridge | `PymIA-Live/pymia/smartpyme/exceland_bridge_v1.py` | IMPLEMENTED_MINIMAL_CONTRACT | Bridge mínimo; factoría física sigue externa |
| Accounting contracts / gate | `PymIA-Live/pymia/smartpyme/service_1_accounting_contracts_v1.py`, `PymIA-Live/pymia/smartpyme/accounting_human_review_gate_v1.py` | IMPLEMENTED_MINIMAL_CONTRACT | Base contractual/gate, no runtime contable productivo |
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

# 5. Regla de lectura vigente

Este roadmap ya no puede leerse como tabla de “proximidad”.

Debe leerse así:

```text
Roadmap = target full
DoD conservador = cierre asistido/manual
Rector full = baseline de verdad documental y orden vigente
```

Cuando haya conflicto:

```text
repo verificado > roadmap antiguo > traza optimista > inferencia
```

---

# 6. Estado real de las 8 familias del full

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

Estado real realineado:

| Familia | Estado real | Brecha principal |
|---|---|---|
| Primeros Auxilios | PARTIAL | existe lane asistida fuerte, pero no familia full cerrada |
| Laboratorio Excel | PARTIAL_SCRIPT_ISOLATED | `document_ingestion.py` no está productizado en `pymia.smartpyme` |
| Factoría Excel | PARTIAL_EXTERNAL_DEPENDENCY | `exeland2` vive fuera del repo y el bridge no cierra generación física controlada |
| Excel descargables con fórmulas | BLOCKED_BY_PRODUCT_DECISION | el delivery actual declara explícitamente que no usa fórmulas |
| Servicios para contadores | PARTIAL_CONTRACT_AND_GATE | hay contratos/gates, no runtime estable de workpaper productivo |
| Conciliaciones | PARTIAL_SANDBOX_OR_CONTRACT | falta motor real de matching y conciliación |
| PDF/CSV/Excel normalizado | MISSING | no hay módulos `pdf` ni `csv` en `smartpyme` |
| Chatbot operativo con IA bajo arnés | FROZEN_OR_MISSING | FSM congelada + sin adapter LLM ni wiring final |

---

# 7. Veredicto de auditoría realineado

```text
SERVICE_1_CURRENT_STATUS:
PARTIAL_FOUNDATIONS_REAL
FULL_TARGET_STILL_VERY_FAR
RECTOR_GOVERNANCE_REQUIRED
NEXT_REQUIRED: ETAPA_0_COMPLETED / ETAPA_1_PENDING
```

Interpretación:

```text
Servicio 1 ya tiene fundaciones reales y una lane asistida útil.
Eso no equivale al producto full.
La cercanía al full no puede inferirse por demos ni por contracts aislados.
El orden vigente de cierre lo fija SERVICE_1_FULL_CLOSURE_RECTOR_V1.
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

# 9. Etapas rectoras vigentes

El orden vigente ya no es la tabla histórica de microciclos sino este:

| Etapa | Frente | Tipo | Cierre requerido |
|---:|---|---|---|
| 0 | Alineación documental dura | DOC/AUDIT | roadmap, DoD, trace y rector sin contradicción |
| 1 | Decisión de producto sobre fórmulas | PRODUCT/DOC | contradicción roadmap vs delivery resuelta |
| 2 | Cierre real de Primeros Auxilios | CODE/TEST/AUDIT | familia First Aid cerrada como familia full |
| 3 | Productización de Laboratorio Excel | CODE/TEST | `document_ingestion` dentro del paquete y cableado |
| 4 | Resolución de Factoría Excel | CODE/DEP/AUDIT | dependencia `exeland2` formalizada y usable |
| 5 | CSV + PDF + normalizador común | CODE/TEST | familia normalización cerrada |
| 6 | Runtime de servicios para contadores | CODE/TEST/REAL_CASE | workpaper productivo con gate humano |
| 7 | Motores de conciliación | CODE/TEST | matching y conciliación reales |
| 8 | FSM productiva + LLM adapter | CODE/TEST/AUDIT | gobierno conversacional tipado |
| 9 | Chatbot operativo con IA bajo arnés | WIRING/TEST | canal final cableado al pipeline real |

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

# 11. Próximo frente recomendado

```text
ETAPA 1 — DECISIÓN DE PRODUCTO SOBRE FÓRMULAS
```

Razón:

```text
Mientras el roadmap full exija fórmulas y el delivery actual las prohíba explícitamente,
la familia “Excel descargables con fórmulas” sigue bloqueada.
```

---

# 12. Veredicto final

```text
SERVICE_1_ROADMAP_REALIGNED_TO_FULL_RECTOR
```
