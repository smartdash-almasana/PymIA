# SERVICE_1_FULL_CLOSURE_RECTOR_V1

## Estado

```text
Tipo: RECTOR_DOC / MASTER_CLOSURE_GUIDE
Estado: ACTIVE_GOVERNANCE_BASELINE
Runtime impact: NONE
Code impact: NONE
Tests impact: NONE
Commit autorizado: NO
Push autorizado: NO
```

## Veredicto rector

```text
SERVICE_1_FULL_STATUS: VERY_FAR
DEMO_OR_MVP_SUBSTITUTION_ALLOWED: NO
ASSISTED_SLICE_EQUALS_FULL_ALLOWED: NO
FULL_ROADMAP_TARGET_ACTIVE: YES
```

## Propósito

Fijar un documento rector único para conducir con certeza a **Servicio 1 full** según el roadmap canónico, evitando dos desvíos que ya consumieron meses:

1. confundir una punta operativa real con el producto full;
2. confundir contratos, docs, sandboxes o scripts aislados con familias cerradas.

Este documento no abre código.

Este documento ordena:

- qué significa realmente Servicio 1 full;
- cuál es la distancia real desde el estado actual;
- qué contradicciones deben resolverse antes de seguir;
- cuál es la secuencia de cierre que reduce autoengaño;
- qué cosas NO deben volver a venderse como “casi listo”.

## Fuentes canónicas usadas

Autoridad principal:

- `docs/producto/SERVICE_1_DEVELOPMENT_AUDIT_AND_COMPLETION_ROADMAP_V1.md`

Fuentes de contraste:

- `docs/producto/SERVICE_1_COMPLETION_DEFINITION_OF_DONE_V1.md`
- `docs/producto/SERVICE_1_FULL_LAYERED_IMPLEMENTATION_TRACE_V1.md`

Verificaciones duras del repo usadas para resolver contradicciones:

- `PymIA-Live/pymia/smartpyme/first_aid_xlsx_delivery_v1.py`
- `tools/document_ingestion.py`
- ausencia de `PymIA-Live/pymia/smartpyme/document_ingestion_v1.py`
- ausencia de `*pdf*.py`, `*csv*.py`, `*llm*.py`, `*chatbot*.py` en `PymIA-Live/pymia/smartpyme/`
- presencia externa de `E:\BuenosPasos\exeland2`
- presencia congelada de `service_1_fsm_decision_patch_v1.py` y `service_1_boundary_chain_v1.py`

## Regla de precedencia

Cuando haya conflicto entre documentos más optimistas y evidencia verificable del repo:

```text
repo verificado > traza optimista > closeout parcial > promesa implícita
```

En particular, este rector prevalece sobre lecturas optimistas donde el repo muestra explícitamente:

- delivery sin fórmulas;
- factory fuera del repo;
- lab Excel no empaquetado;
- PDF/CSV runtime inexistente;
- chatbot/LLM sin adapter ni wiring;
- FSM congelada.

## Quick path

1. Alinear documentación y decisiones de producto con la verdad del repo.
2. Cerrar primero las familias estructurales bajas: First Aid full, Lab Excel, Factoría.
3. Recién después abrir workpaper runtime, conciliaciones, FSM y IA arneada.

---

## 1. Qué significa “Servicio 1 full”

Según el roadmap canónico, Servicio 1 full incluye estas 8 familias:

1. **Primeros Auxilios**
2. **Laboratorio Excel**
3. **Factoría Excel**
4. **Excel descargables con fórmulas**
5. **Servicios para contadores**
6. **Conciliaciones**
7. **PDF/CSV/Excel a Excel normalizado**
8. **Chatbot operativo con IA bajo arnés**

### Regla central

```text
Servicio 1 full no se declara por una demo, ni por una CLI, ni por una carpeta de caso,
ni por una suite verde de una sola familia.
```

Servicio 1 full sólo puede declararse cuando las 8 familias tengan capacidad cerrada en su frontera real, no sólo documental.

---

## 2. Posición actual verificada

### Resumen ejecutivo

Hoy Servicio 1 está fuerte en:

- First Aid asistido local;
- foundations owner-facing;
- QA/delivery gate;
- carpeta de caso;
- pipeline parcial de First Aid.

Pero sigue muy lejos del full grande porque todavía faltan:

- decisiones de producto no resueltas;
- productización de piezas aisladas;
- runtimes enteros;
- intake de formatos prometidos;
- integración contable real;
- y toda la capa FSM + LLM + chatbot.

### Regla anti-autoengaño

```text
“Hay archivo / contrato / test / sandbox / doc” no implica “familia cerrada”.
```

---

## 3. Matriz rectora por familia

| Familia | Estado rector | Evidencia real | Bloqueo madre | Condición de cierre real |
|---|---|---|---|---|
| Primeros Auxilios | `CLOSED_IN_SCOPE_RUNTIME` | CLI cableada al pipeline, 5 tools runtime implementadas, delivery manual, QA gate, case folder, fórmula policy resuelta | brechas resueltas (5 tools completas, pipeline allowlisted, fórmula policy decidida) | familia cerrada como familia del roadmap, no sólo carril asistido |
| Laboratorio Excel | `CLOSED_IN_SCOPE_RUNTIME` | `pymia/smartpyme/excel_lab_ingestion_v1.py` productivo, `tools/document_ingestion.py` wrapper, tests boundary focales PASS, consumers actualizados | ninguna (ingestión, profiling y structured output encapsulados y testeados) | módulo importable + tests + wiring |
| Factoría Excel | `PARTIAL_EXTERNAL_DEPENDENCY` | `exeland2` existe fuera del repo, bridge mínimo existe | dependencia externa no formalizada | factory internalizada o dependencia formal |
| Excel descargables con fórmulas | `BLOCKED_BY_PRODUCT_DECISION` | delivery actual dice explícitamente “No formulas” | contradicción con roadmap full | ADR + runtime/test de fórmulas o redefinición de scope |
| Servicios para contadores | `PARTIAL_CONTRACT_AND_GATE` | contracts, manifest, gate, draft packet, docs de workpaper | no hay runtime estable de workpaper productivo | workpaper runtime + caso real supervisado |
| Conciliaciones | `PARTIAL_SANDBOX_OR_CONTRACT` | contracts y sandbox docs/tests | no hay motor de matching real | motor runtime + datasets controlados + gates |
| PDF/CSV/Excel normalizado | `MISSING` | no hay módulos `pdf` ni `csv` en smartpyme | familia entera no implementada | intake CSV + PDF + normalizador común |
| Chatbot operativo con IA bajo arnés | `FROZEN_OR_MISSING` | FSM congelada, no hay llm/chatbot modules en smartpyme | FSM + adapter + wiring ausentes | FSM productiva + adapter tipado + canal cableado |

---

## 4. Hallazgos rectores no negociables

### 4.1 Fórmulas: el roadmap y el delivery actual chocan

Hecho verificado:

```text
first_aid_xlsx_delivery_v1.py declara: “No formulas, macros, or runtime execution were used.”
```

Implicancia:

```text
La familia “Excel descargables con fórmulas” NO puede marcarse como parcial cerrada.
```

Acción rectora:

```text
Resolver primero una decisión de producto.
```

### 4.2 `document_ingestion.py` existe, pero está fuera del producto empaquetado

Hecho verificado:

```text
tools/document_ingestion.py existe
PymIA-Live/pymia/smartpyme/document_ingestion_v1.py no existe
```

Implicancia:

```text
Laboratorio Excel no está cerrado como familia de producto.
```

### 4.3 `exeland2` no vive dentro de este repo

Hecho verificado:

```text
E:\BuenosPasos\smartbridge\PymIA\exeland2 = NO
E:\BuenosPasos\exeland2 = YES
```

Implicancia:

```text
La factoría no puede tratarse como capacidad plenamente internalizada.
```

### 4.4 PDF y CSV prometidos no existen como módulos del paquete

Hecho verificado:

```text
No hay *pdf*.py ni *csv*.py en PymIA-Live/pymia/smartpyme
```

Implicancia:

```text
La familia “PDF/CSV/Excel a Excel normalizado” sigue MISSING.
```

### 4.5 Chatbot con IA bajo arnés no está para abrirse

Hecho verificado:

```text
No hay *llm*.py ni *chatbot*.py en smartpyme
La FSM sigue EXPERIMENTAL_FROZEN
```

Implicancia:

```text
Chatbot operativo con IA bajo arnés no está cerca de cierre.
```

---

## 5. Falsos avances que este rector prohíbe volver a usar

No usar como argumento de “casi full”:

- demo local PASS;
- 9 artefactos de carpeta de caso;
- QA delivery gate PASS;
- tests verdes de una sola lane;
- existencia de sandbox de conciliación;
- existencia de docs de workpaper;
- existencia de `conversa-engine` sin cableado a Servicio 1;
- existencia de `document_ingestion.py` fuera del paquete;
- existencia de bridge Exceland sin factory formalizada en el repo.

### Frase prohibida

```text
“Estamos a una tool de distancia del full.”
```

Este rector la considera falsa.

---

## 6. Bloqueos madre del producto full

1. **Decisión de fórmulas no resuelta**
2. **Lab Excel no empaquetado**
3. **Factoría dependiente de repo/path externo**
4. **PDF/CSV intake inexistente**
5. **Workpaper runtime real no cerrado**
6. **Conciliaciones runtime no cerradas**
7. **FSM + LLM adapter + wiring chatbot no construidos**

---

## 7. Plan rector de cierre final

### Etapa 0 — Alineación dura de verdad documental

**Objetivo**

```text
Actualizar la lectura maestra de Servicio 1 full contra HEAD real y contra este rector.
```

**Incluye**

- reconciliar roadmap, DoD y trace;
- declarar explícitamente qué es externo, qué es parcial y qué es missing;
- eliminar cualquier claim que sugiera proximidad falsa al full.

**Cierre**

```text
No quedan contradicciones documentales sobre fórmulas, exeland2, Lab Excel, PDF/CSV, FSM o chatbot.
```

### Etapa 1 — Decisión de producto sobre fórmulas

**Objetivo**

```text
Resolver si Servicio 1 full mantiene el requisito de fórmulas activas en XLSX
o si redefine esa familia.
```

**Cierre**

Una de estas dos:

1. ADR que habilita fórmulas canónicas bajo guardrails + plan técnico
2. actualización oficial del roadmap full removiendo esa exigencia

**Resultado**

```text
Resuelta por SERVICE_1_XLSX_FORMULA_POLICY_V1:
- el delivery actual sigue sin fórmulas;
- la familia de fórmulas activas se mueve al carril Factoría Excel;
- no se habilitan fórmulas en First Aid ni en delivery genérico.
```

### Etapa 2 — Cierre real de Primeros Auxilios (COMPLETADA)

**Estado**: `COMPLETED`

**Verificación con repo HEAD**

- `7f67b58` feat(pymia-live): wire service 1 pipeline tools into cli

**Lo que incluía**

- tools faltantes → 5 tools completas (precio_margen, caja_diaria, stock_alertas, gastos_triage, proveedores_precio_variacion_triage)
- revisión de pipeline First Aid → pipeline allowlisted con 5 tools, cableado a CLI via `--run-tools`
- verificación de delivery según decisión de fórmulas → delivery sin fórmulas, policy decidida (`SERVICE_1_XLSX_FORMULA_POLICY_V1`)

**Cierre alcanzado**

```text
Primeros Auxilios = DONE como familia del roadmap, no sólo como carril asistido.
53 tests PASS en suite de validación (pipeline + delivery + CLI + manual + e2e).
```

**Próxima etapa después de ésta**: Etapa 3

### Etapa 3 — Productización de Laboratorio Excel

**Estado**: `COMPLETED`

**Verificación con repo HEAD**

- `cd1235e` feat(pymia-live): productize service 1 excel lab ingestion

**Lo que incluía**

- módulo `pymia.smartpyme.*` → `pymia.smartpyme.excel_lab_ingestion_v1.py` creado, dividiendo Ingestión, Profiling y Output Estructurado.
- contrato explícito y tests focales → 8 tests boundary en `tests/smartpyme/test_excel_lab_ingestion_boundary_v1.py`.
- wiring controlado al pipeline → consumidores actualizados, compatibilidad preservada con wrapper en `tools/document_ingestion.py`.

**Cierre**

```text
Laboratorio Excel deja de ser script aislado y pasa a ser familia de producto con 100% de tests de frontera PASS.
```

**Próxima etapa después de ésta**: Etapa 4

### Etapa 4 — Resolución de Factoría Excel

**Objetivo**

```text
Formalizar la dependencia Exceland y cerrar el bridge con generación física controlada.
```

**Incluye**

- internalizar `exeland2` o declararlo como dependencia formal;
- asegurar contrato estable;
- generar outputs reales bajo prueba.

**Cierre**

```text
Factoría Excel deja de depender de una cantera ambigua.
```

### Etapa 5 — Ingesta CSV y PDF + normalizador común

**Objetivo**

```text
Cerrar la familia “PDF/CSV/Excel a Excel normalizado”.
```

**Orden rector**

1. CSV
2. normalizador común
3. PDF

**Cierre**

```text
Tres formatos entran y convergen a un Excel normalizado verificable.
```

### Etapa 6 — Runtime de servicios para contadores

**Objetivo**

```text
Pasar de contratos/gates a workpaper runtime real con human review gate y caso supervisado.
```

**Incluye**

- workpaper runtime;
- QA checklist operativo;
- primer caso real supervisado;
- revisión sanitizada posterior.

**Cierre**

```text
Servicios para contadores dejan de ser sólo contrato + packet + docs.
```

### Etapa 7 — Motores de conciliación

**Objetivo**

```text
Construir matching real y conciliación operativa.
```

**Incluye**

- facturas vs cobros;
- bank reconciliation;
- Mercado Pago reconciliation;
- entity resolution controlado.

**Cierre**

```text
Conciliaciones dejan de ser sandbox/contract y pasan a runtime controlado.
```

### Etapa 8 — FSM productiva + LLM adapter tipado

**Objetivo**

```text
Descongelar con auditoría y abrir sólo cuando las familias inferiores ya no sean el cuello.
```

**Incluye**

- FSM nueva o auditada;
- adapter LLM con outputs permitidos/prohibidos;
- tests fail-closed.

**Cierre**

```text
Existe gobierno conversacional tipado, no IA libre.
```

### Etapa 9 — Chatbot operativo con IA bajo arnés

**Objetivo**

```text
Cablear canal conversacional al pipeline real de Servicio 1 full.
```

**Cierre**

```text
El chatbot deja de ser promesa documental y pasa a frontera operativa validada.
```

---

## 8. Orden rector: qué atacar primero y qué no tocar

### Atacar primero

1. ~~Etapa 0 — alineación documental~~ (COMPLETADA)
2. ~~Etapa 1 — decisión de producto sobre fórmulas~~ (COMPLETADA)
3. ~~Etapa 2 — Primeros Auxilios full~~ (COMPLETADA)
4. ~~Etapa 3 — Laboratorio Excel productizado~~ (COMPLETADA)
5. Etapa 4 — Resolución de Factoría Excel

### No tocar todavía

- chatbot;
- LLM adapter;
- wiring de canales;
- reactivación de `service_1_fsm_decision_patch_v1.py`;
- reactivación de `service_1_boundary_chain_v1.py`;
- OCR;
- APIs vivas;
- Servicio 2.

### Regla

```text
No abrir capas 8-9 si 2-7 siguen abiertas.
```

---

## 9. Condición de salida a “Servicio 1 full”

Servicio 1 full sólo puede declararse cuando:

```text
1. las 8 familias del roadmap estén cerradas;
2. no haya contradicción activa entre roadmap y código;
3. no dependa de paths externos ambiguos para familias core;
4. exista pipeline real multi-familia;
5. exista QA/human review donde corresponda;
6. exista evidencia de casos sintéticos y reales donde el propio DoD lo exige;
7. chatbot + IA arneada estén cableados sobre la capacidad real, no sobre placeholders.
```

---

## 10. Frase rectora final

```text
Servicio 1 full no se alcanza sumando demos exitosas;
se alcanza cerrando familias estructurales en el orden correcto,
resolviendo contradicciones de producto,
y dejando de confundir envoltorio con motor.
```

## Próximo paso autorizado

```text
ETAPA 4 — RESOLUCIÓN DE FACTORÍA EXCEL
```
