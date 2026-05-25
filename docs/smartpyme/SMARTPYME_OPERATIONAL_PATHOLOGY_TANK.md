# SMARTPYME_OPERATIONAL_PATHOLOGY_TANK

Estado: **DOCUMENTADO (v0.1.0-doc) — Sin implementación runtime**

---

## 1. Estado y propósito

Este documento define el **primer KnowledgeTank canónico** de SmartPyme:

```text
SMARTPYME_OPERATIONAL_PATHOLOGY_TANK
```

Su función es **mapear lenguaje crudo, señales semánticas y síntomas candidatos
a patologías operacionales PyME**, sin diagnosticar, sin ejecutar análisis y
sin emitir recomendaciones finales.

Este documento:

- Documenta conocimiento operacional de dominio.
- No implementa código.
- No diagnostica.
- No reemplaza la fase semántico-dialéctica.
- Se alimenta del `InterrogationResult` producido por `interrogation_slice`.
- Prepara `EvidenceRequest` y futura selección de tanques.
- Complementa (no reemplaza) `SMARTPYME_KNOWLEDGE_TANKS_CONTRACT.md` y
  `SMARTPYME_KNOWLEDGE_TANKS_ARCHITECTURE.md`.

---

## 2. Relación con la arquitectura de tanques

Este tanque sigue el contrato definido en:

- `docs/smartpyme/SMARTPYME_KNOWLEDGE_TANKS_CONTRACT.md`
- `docs/smartpyme/SMARTPYME_KNOWLEDGE_TANKS_ARCHITECTURE.md`

Y respeta:

- el flujo de interrogación (`SMARTPYME_INTERROGATION_TAXONOMY.md`,
  `SMARTPYME_SEMANTIC_DIALECTIC_PHASE.md`, `SMARTPYME_INTERROGATION_SLICE.md`);
- el catálogo de patologías (`docs/pathology_catalog.v1.json`);
- los principios de tanques modulares
  (`docs/ingenieria_conversacional.PATOLOGIAS_PYME_Y_TANQUES_DE_CONOCIMIENTO_v1.md`).

El tanque debe poder transitar por los 8 estados del ciclo de vida definidos
en la arquitectura:

```text
DEFINED → AVAILABLE → CANDIDATE → ACTIVE
                              ↓
                    SUSPENDED / DEACTIVATED
                              ↓
                    UNSUPPORTED / RETIRED
```

En la versión actual (0.1.0-doc) el tanque está **DEFINED y AVAILABLE solo a
nivel documental**. No existe todavía loader, selector runtime ni
`TankSelectionResult` implementado.

---

## 3. Definición del tanque

```yaml
tank_id: SMARTPYME_OPERATIONAL_PATHOLOGY_TANK
version: "0.1.0-doc"
name: "Operational Pathology Tank — SmartPyme Core"
domain: operational_pathology
scope: transversal_pyme
description: |
  Mapea relato crudo y señales operacionales a síntomas y patologías
  candidatas sin cerrar diagnóstico ni ejecutar análisis.

outputs_allowed:
  - symptoms_candidates
  - pathology_candidates
  - clarification_questions
  - hypothesis_candidates
  - evidence_suggestions
  - safety_warnings
  - next_interrogation_state

outputs_forbidden:
  - confirmed_diagnosis
  - causal_assertion
  - final_report
  - financial_advice
  - automated_decision
  - unsupported_classification
  - benchmark_without_sector
  - price_recommendation
```

---

## 4. Inputs esperados

El tanque consume el `InterrogationResult` emitido por `interrogation_slice`.

### Desde `InterrogationResult`

- `raw_input` — relato literal preservado.
- `normalized_terms` — señales léxicas detectadas.
- `business_context` — selectores estructurales normalizados.
- `semantic_signals` — señales semánticas adicionales.
- `candidate_symptoms` — síntomas detectados por el slice.
- `candidate_domains` — dominios candidatos.
- `clarification_questions` — preguntas ya emitidas por el slice.
- `evidence_needs` — necesidades de evidencia preliminares.
- `status` — estado del interrogatorio.
- `suggested_classification` — clasificación sugerida por el slice.

### Desde selectores estructurales

- `sales_channel`: Local / Mayorista / Mercado Libre / Ecommerce / Instagram / Mixto
- `operation_type`: Revendo / Produzco / Servicios / Distribuyo / Mixto
- `stock_mode`: Sí / No / Informal
- `tools_used`: Excel / Sistema / Cuaderno / Varios
- `evidence_available`: Excel / PDF / Capturas / AudioTexto / NoSe
- `employee_range`
- `marketplace_presence`

**Regla:** los selectores **nunca** activan diagnóstico por sí solos. Solo
refuerzan dominio y clasificación cuando el `raw_text` ya aporta señal
compatible.

---

## 5. Estados del tanque

| Estado | Significado | Condición de entrada | Condición de salida |
|---|---|---|---|
| `DEFINED` | El tanque existe en documentación. | Creación del documento. | Pase a AVAILABLE. |
| `AVAILABLE` | El tanque está cargable por un futuro loader. | Loader implementado. | Pase a CANDIDATE cuando haya caso. |
| `CANDIDATE` | Señales del caso sugieren que el tanque podría aplicar. | `InterrogationResult` con síntomas/dominios compatibles. | Confirmación → ACTIVE, o refutación → SUSPENDED. |
| `ACTIVE` | Tanque aportando preguntas, evidencia e hipótesis al caso. | Usuario confirma reformulación y no viola safety gates. | Resolución → DEACTIVATED o bloqueo → UNSUPPORTED. |
| `SUSPENDED` | Temporalmente fuera por falta de contexto o evidencia. | Usuario corrige reformulación o falta evidencia mínima. | Puede volver a ACTIVE si aparece contexto. |
| `DEACTIVATED` | No aplica al caso. | Problema fuera del dominio operacional. | Terminal para este caso. |
| `UNSUPPORTED` | Conceptualmente aplicable pero runtime no soporta análisis. | Runtime sin capacidad requerida. | Terminal para este caso. |
| `RETIRED` | Reemplazado por nueva versión. | Cambio MAJOR en contrato. | Terminal global. |

---

## 6. Activadores

El tanque puede pasar a `CANDIDATE` por combinación de:

- lenguaje de dolor operacional en `raw_input`;
- síntomas detectados por `interrogation_slice` presentes en
  `supported_symptoms`;
- dominios candidatos presentes en `supported_domains`;
- evidencia declarada disponible (`evidence_available`) compatible;
- frase cruda con señal fuerte (ver §11);
- selectores estructurales compatibles **acompañados** por relato.

El tanque **no puede pasar a ACTIVE** si:

- no hay relato (`raw_input` vacío);
- el usuario no confirmó o hay ambigüedad sin resolver;
- el contexto contradice el dominio operacional;
- la señal proviene solo de selector estructural;
- no hay pregunta/evidencia siguiente válida;
- se viola cualquier safety gate.

---

## 7. Desactivadores

El tanque debe suspenderse o desactivarse si:

- el usuario corrige la reformulación y cambia de tema;
- el problema resulta puramente legal, fiscal avanzado, médico o laboral
  (fuera del alcance operacional PyME);
- no hay contexto mínimo (`required_context` no satisfecho);
- la evidencia entregada contradice la hipótesis;
- otro tanque más específico debe tomar el caso (ej: tanque sectorial);
- el runtime no soporta el análisis requerido;
- se detecta riesgo de diagnóstico prematuro;
- se pide evidencia excesiva (>3 tipos simultáneos).

Distinguir:

- `SUSPENDED`: puede reactivarse si aparece evidencia o contexto.
- `DEACTIVATED`: no aplica al caso.
- `UNSUPPORTED`: aplica conceptualmente pero el runtime no soporta el
  análisis requerido.

---

## 8. Síntomas soportados

El tanque soporta los 9 síntomas mínimos definidos en
`interrogation_slice` más uno transversal:

### 8.1 DESCUADRE_DINERO
- **Definición:** el dueño percibe que el dinero no cierra contra alguna
  expectativa (caja, banco, cobros, margen).
- **Frases típicas:** "no me cierra la plata", "no sé dónde se va",
  "la caja no da", "cobro y no me queda".
- **Señales semánticas:** `plata`, `caja`, `banco`, `cobros`, `cierra`,
  `queda`, `sale`.
- **Dominios probables:** `finanzas`.
- **Patologías candidatas:** `LIQ_001`, `LIQ_002`, `PYME_013`, `PYME_026`,
  `PYME_046`.
- **Pregunta de desambiguación:** "Cuando decís que no te cierra la plata,
  ¿hablás de caja/banco, ventas/cobros, costos/margen, gastos/retiros o
  todavía no estás seguro?"
- **Evidencia sugerida:** extracto bancario + reporte de cobros/ventas.
- **Qué NO concluir todavía:** no hay desfalco, no hay error contable, no
  hay pérdida operativa confirmada.
- **Safety warning:** no diagnosticar sin evidencia financiera validada.

### 8.2 MARGEN_DUDOSO
- **Definición:** el dueño sospecha que el margen no es el esperado o que
  vende sin que quede resultado.
- **Frases típicas:** "vendo pero no me queda", "no sé si gano", "los
  precios no cubren", "margen chico".
- **Señales semánticas:** `margen`, `precio`, `costo`, `queda`, `gano`,
  `cubro`.
- **Dominios probables:** `comercial`, `finanzas`.
- **Patologías candidatas:** `REN_001`, `REN_002`, `PYME_014`, `PYME_017`,
  `PYME_044`, `PYME_048`, `PYME_049`.
- **Pregunta:** "¿Querés revisar si los precios cubren los costos, si hay
  productos sin costo cargado o si el margen bajó en un período?"
- **Evidencia sugerida:** excel de ventas + costos + (si aplica) comisiones.
- **Qué NO concluir:** que el negocio es inviable, que hay que subir
  precios, que un producto específico pierde plata.
- **Safety warning:** no recomendar precios sin evidencia completa.

### 8.3 DATOS_DUPLICADOS
- **Definición:** hay registros repetidos en algún maestro (proveedores,
  clientes, productos).
- **Frases típicas:** "tengo proveedores repetidos", "me aparecen
  clientes dos veces", "cuit duplicado".
- **Señales semánticas:** `duplicado`, `repetido`, `cuit`, `mezclado`,
  `dos veces`.
- **Dominios probables:** `datos_maestros`, `proveedores`.
- **Patologías candidatas:** `PYME_018`, `PYME_022`, `PYME_038`.
- **Pregunta:** "¿Los duplicados están en proveedores, clientes, productos
  u otro listado?"
- **Evidencia sugerida:** excel del maestro con identificador (CUIT /
  código).
- **Clasificación sugerida posible:** `supplier_duplicate_check` (si el
  maestro es de proveedores y el runtime la soporta).
- **Qué NO concluir:** cuántos duplicados reales hay sin validar.
- **Safety warning:** no ejecutar deduplicación sin evidencia validada.

### 8.4 STOCK_INCONSISTENTE
- **Definición:** el stock del sistema no coincide con el físico o con lo
  vendido.
- **Frases típicas:** "el sistema dice un stock y el depósito otro",
  "me faltan mercaderías", "vendí sin stock".
- **Señales semánticas:** `stock`, `depósito`, `faltante`, `sistema dice`,
  `físico`, `inventario`.
- **Dominios probables:** `stock`, `inventario`.
- **Patologías candidatas:** `INV_001`, `INV_002`, `PYME_008`, `PYME_042`.
- **Pregunta:** "¿La diferencia está entre sistema y depósito, entre
  ventas y stock, o en movimientos sin registrar?"
- **Evidencia sugerida:** export de stock sistema + conteo físico +
  movimientos del período.
- **Qué NO concluir:** que hay robo, que el sistema está roto, que el
  depósito es un caos.
- **Safety warning:** no clasificar como pérdida sin evidencia de
  movimientos.

### 8.5 SOBRECARGA_MANUAL
- **Definición:** tareas operativas se hacen a mano con alta frecuencia.
- **Frases típicas:** "copio todo a mano", "hago doble carga", "tardo
  horas en cerrar".
- **Señales semánticas:** `a mano`, `copio`, `manual`, `doble carga`,
  `tardo`, `planilla`.
- **Dominios probables:** `automatizacion`, `administracion`, `operaciones`.
- **Patologías candidatas:** `PYME_015`, `PYME_020`, `PYME_040`, `PYME_047`.
- **Pregunta:** "¿Qué tarea se repite, con qué frecuencia y en qué
  archivos o sistemas ocurre?"
- **Evidencia sugerida:** descripción del flujo + archivos involucrados.
- **Qué NO concluir:** que se debe automatizar con X herramienta.
- **Safety warning:** no recomendar stack sin contexto de madurez.

### 8.6 COSTO_INCIERTO
- **Definición:** el dueño no sabe con precisión cuánto le cuesta algo.
- **Frases típicas:** "no sé cuánto me cuesta producir", "no tengo
  claro el costo", "los costos se me movieron".
- **Señales semánticas:** `costo`, `cuesta`, `insumo`, `reposición`,
  `actualizar`.
- **Dominios probables:** `produccion`, `finanzas`, `comercial`.
- **Patologías candidatas:** `REN_002`, `PYME_014`, `PYME_048`, `PYME_049`.
- **Pregunta:** "¿El costo que te preocupa es de un producto, una línea,
  un servicio o el negocio completo?"
- **Evidencia sugerida:** estructura de costos + lista de insumos +
  precios de reposición.
- **Qué NO concluir:** que el margen es negativo sin evidencia.
- **Safety warning:** no calcular margen sin costos validados.

### 8.7 DOCUMENTACION_DESORDENADA
- **Definición:** la documentación operativa está dispersa, desactualizada
  o en formatos incompatibles.
- **Frases típicas:** "tengo papeles por todos lados", "Excel
  imposible", "no encuentro las facturas".
- **Señales semánticas:** `papeles`, `facturas`, `carpetas`, `Excel
  imposible`, `desorden`.
- **Dominios probables:** `administracion`, `datos_maestros`.
- **Patologías candidatas:** `PYME_018`, `PYME_022`, `PYME_038`.
- **Pregunta:** "¿El desorden está en facturas, comprobantes, contratos,
  planillas internas o todo junto?"
- **Evidencia sugerida:** muestra de la estructura actual.
- **Qué NO concluir:** que hay que migrar a ERP.
- **Safety warning:** no recomendar herramientas sin contexto.

### 8.8 MAESTRO_DESORDENADO
- **Definición:** algún maestro crítico (proveedores, clientes,
  productos) está inconsistente, incompleto o mal cargado.
- **Frases típicas:** "los proveedores están mal cargados", "no tengo
  bien los productos", "mezclo razones sociales".
- **Señales semánticas:** `maestro`, `mal cargado`, `inconsistente`,
  `razón social`, `cuit`.
- **Dominios probables:** `datos_maestros`, `proveedores`.
- **Patologías candidatas:** `PYME_018`, `PYME_022`.
- **Pregunta:** "¿El maestro desordenado es de proveedores, clientes,
  productos u otro?"
- **Evidencia sugerida:** export del maestro.
- **Clasificación sugerida posible:** `supplier_duplicate_check` si
  corresponde.
- **Qué NO concluir:** cuántos registros están mal sin validar.
- **Safety warning:** no modificar maestro sin evidencia validada.

### 8.9 TRAZABILIDAD_INSUFICIENTE
- **Definición:** no se puede seguir el hilo de una operación, cobro,
  movimiento o decisión.
- **Frases típicas:** "no sé de dónde salió este número", "no puedo
  trazar una venta", "no recuerdo quién cargó esto".
- **Señales semánticas:** `traza`, `de dónde salió`, `historial`,
  `auditoría`, `quién cargó`.
- **Dominios probables:** `operaciones`, `datos_maestros`, `finanzas`.
- **Patologías candidatas:** `PYME_019`, `PYME_021`, `PYME_022`.
- **Pregunta:** "¿La trazabilidad que falta es de ventas, stock, cobros,
  movimientos o decisiones?"
- **Evidencia sugerida:** logs disponibles + descripción del proceso.
- **Qué NO concluir:** que hay fraude o error humano intencional.
- **Safety warning:** no atribuir responsabilidad sin evidencia.

### 8.10 DESCONOCIDO
- **Definición:** el slice no pudo clasificar el relato en un síntoma
  claro.
- **Frases típicas:** relatos muy cortos, ambiguos, fuera de dominio.
- **Dominios probables:** `desconocido`.
- **Patologías candidatas:** ninguna.
- **Pregunta:** pregunta abierta mayéutica: "Contame con tus palabras qué
  querés entender o qué te preocupa."
- **Qué NO concluir:** nada.
- **Safety warning:** no forzar síntoma ni patología.

---

## 9. Patologías operacionales candidatas

Las patologías candidatas se referencian del `docs/pathology_catalog.v1.json`.
El tanque **no afirma** que existan en el caso, solo las marca como
**candidatas a contrastar** con evidencia.

### 9.1 CASH_RECONCILIATION_DRIFT
- **Referencias:** `LIQ_001`, `LIQ_002`, `PYME_013`, `PYME_026`, `PYME_046`.
- **Descripción:** el dinero cobrado no se reconcilia con ventas, gastos o
  saldos bancarios.
- **Síntomas asociados:** `DESCUADRE_DINERO`.
- **Dominios:** `finanzas`.
- **Evidencia mínima:** extracto bancario + ventas/cobros de un período.
- **Evidencia deseable:** + gastos + retiros + conciliaciones previas.
- **Hipótesis abiertas:** descalce de cobranzas, mezcla de finanzas
  personales/empresariales, flujo negativo.
- **Riesgo de falsa conclusión:** atribuir a desfalco o error contable sin
  evidencia.
- **Próximos pasos:** pedir extracto y reporte de cobros; no cerrar causa.

### 9.2 MARGIN_LEAKAGE_SUSPECTED
- **Referencias:** `REN_001`, `PYME_014`, `PYME_017`, `PYME_044`,
  `PYME_049`.
- **Descripción:** sospecha de erosión de margen por costos, comisiones o
  pricing desactualizado.
- **Síntomas asociados:** `MARGEN_DUDOSO`, `COSTO_INCIERTO`.
- **Dominios:** `comercial`, `finanzas`.
- **Evidencia mínima:** ventas + costos del período.
- **Evidencia deseable:** + comisiones + logística + precios de reposición.
- **Hipótesis abiertas:** margen invisible, pricing drift, subsidio oculto
  a clientes.
- **Riesgo de falsa conclusión:** afirmar que un producto pierde plata
  con costos incompletos.
- **Próximos pasos:** validar estructura de costos antes de calcular.

### 9.3 COST_UPDATE_LAG
- **Referencias:** `REN_002`, `PYME_048`.
- **Descripción:** los costos de reposición no se están trasladando a
  precios o a valuación de stock.
- **Síntomas asociados:** `COSTO_INCIERTO`, `MARGEN_DUDOSO`.
- **Dominios:** `produccion`, `comercial`.
- **Evidencia mínima:** lista de insumos con fechas de compra.
- **Evidencia deseable:** + precios de venta actuales + stock valuado.
- **Hipótesis abiertas:** obsolescencia de precios, falsa rentabilidad.
- **Riesgo:** recomendar suba de precio sin análisis de mercado.

### 9.4 SUPPLIER_MASTER_DUPLICATION
- **Referencias:** `PYME_018`, `PYME_022`.
- **Descripción:** el maestro de proveedores contiene duplicados o
  registros inconsistentes.
- **Síntomas asociados:** `DATOS_DUPLICADOS`, `MAESTRO_DESORDENADO`.
- **Dominios:** `proveedores`, `datos_maestros`.
- **Evidencia mínima:** excel con `proveedor` + `cuit` o `razon_social`.
- **Evidencia deseable:** + domicilio, email, categoría.
- **Hipótesis abiertas:** duplicados exactos, variaciones legales (SRL /
  S.R.L.), razones sociales inconsistentes.
- **Clasificación sugerida posible:** `supplier_duplicate_check` (existe
  en runtime real).
- **Riesgo:** afirmar cantidad de duplicados sin ejecutar validación.

### 9.5 STOCK_TRACEABILITY_GAP
- **Referencias:** `INV_001`, `INV_002`, `PYME_008`, `PYME_042`.
- **Descripción:** el stock no se puede trazar entre sistema, depósito y
  ventas.
- **Síntomas asociados:** `STOCK_INCONSISTENTE`.
- **Dominios:** `stock`, `inventario`.
- **Evidencia mínima:** stock sistema + conteo físico de una fecha.
- **Evidencia deseable:** + movimientos del período + ventas.
- **Hipótesis abiertas:** stock fantasma, capital inmovilizado,
  desconexión e-commerce.
- **Riesgo:** atribuir a robo o rotura sin evidencia de movimientos.

### 9.6 MANUAL_WORK_OVERLOAD
- **Referencias:** `PYME_015`, `PYME_020`, `PYME_040`, `PYME_047`.
- **Descripción:** tareas operativas repetitivas con alta carga manual.
- **Síntomas asociados:** `SOBRECARGA_MANUAL`.
- **Dominios:** `automatizacion`, `operaciones`, `administracion`.
- **Evidencia mínima:** descripción de la tarea + frecuencia + archivos.
- **Evidencia deseable:** + tiempo estimado + sistemas involucrados.
- **Hipótesis abiertas:** puente mental multi-vía, rigidez artesanal,
  conciliación crónica manual.
- **Riesgo:** recomendar ERP/automatización sin contexto de madurez.

### 9.7 DOCUMENTARY_FRAGMENTATION
- **Referencias:** `PYME_018`, `PYME_022`, `PYME_038`.
- **Descripción:** la documentación operativa está dispersa en múltiples
  soportes.
- **Síntomas asociados:** `DOCUMENTACION_DESORDENADA`, `MAESTRO_DESORDENADO`.
- **Dominios:** `administracion`, `datos_maestros`.
- **Evidencia mínima:** muestra representativa del estado actual.
- **Evidencia deseable:** + inventario de soportes.
- **Hipótesis abiertas:** data decay, caos de versiones, fragilidad por
  dispersión.
- **Riesgo:** recomendar migración sin análisis de uso real.

### 9.8 PRICING_CONTROL_WEAKNESS
- **Referencias:** `PYME_017`, `PYME_048`.
- **Descripción:** el proceso de fijación/actualización de precios no
  sigue los costos ni el mercado.
- **Síntomas asociados:** `MARGEN_DUDOSO`, `COSTO_INCIERTO`.
- **Dominios:** `comercial`, `pricing`.
- **Evidencia mínima:** lista de precios actual + costos.
- **Evidencia deseable:** + historial de cambios + referencia de mercado.
- **Hipótesis abiertas:** pricing drift, obsolescencia de precios.
- **Riesgo:** recomendar precios sin evidencia de mercado.

### 9.9 EVIDENCE_INSUFFICIENCY
- **Referencias:** transversal.
- **Descripción:** no hay evidencia mínima para contrastar ninguna
  hipótesis.
- **Síntomas asociados:** cualquiera cuando `evidence_available == NoSe`.
- **Dominios:** transversal.
- **Evidencia mínima:** al menos un tipo documental compatible.
- **Hipótesis abiertas:** ninguna afirmable.
- **Estado sugerido:** `NEEDS_EVIDENCE` o `BLOCKED_INSUFFICIENT_CONTEXT`.

### 9.10 OPERATIONAL_VISIBILITY_GAP
- **Referencias:** `PYME_019`, `PYME_022`.
- **Descripción:** el dueño no puede ver el estado operativo del negocio
  con latencia aceptable.
- **Síntomas asociados:** `TRAZABILIDAD_INSUFICIENTE`, `DOCUMENTACION_DESORDENADA`.
- **Dominios:** `gestion`, `operaciones`.
- **Evidencia mínima:** descripción de qué se quiere ver y cada cuánto.
- **Hipótesis abiertas:** ceguera de decisión, fragilidad por dispersión.
- **Riesgo:** recomendar dashboard sin entender qué decisión habilita.

---

## 10. Mapa síntoma → patología

| Síntoma | Patologías candidatas | Evidencia mínima | Pregunta siguiente | Estado sugerido |
|---|---|---|---|---|
| `DESCUADRE_DINERO` | CASH_RECONCILIATION_DRIFT | extracto bancario + ventas/cobros | ¿caja/banco, cobros, margen o gastos? | `NEEDS_DISAMBIGUATION` |
| `MARGEN_DUDOSO` | MARGIN_LEAKAGE_SUSPECTED, PRICING_CONTROL_WEAKNESS | ventas + costos | ¿precios vs costos, productos sin costo, o histórico? | `NEEDS_EVIDENCE` |
| `DATOS_DUPLICADOS` | SUPPLIER_MASTER_DUPLICATION | excel maestro con identificador | ¿proveedores, clientes, productos? | `NEEDS_EVIDENCE` |
| `STOCK_INCONSISTENTE` | STOCK_TRACEABILITY_GAP | stock sistema + conteo físico | ¿sistema vs depósito, o movimientos? | `NEEDS_EVIDENCE` |
| `SOBRECARGA_MANUAL` | MANUAL_WORK_OVERLOAD | descripción + frecuencia + archivos | ¿qué tarea, cada cuánto, en qué sistema? | `NEEDS_DISAMBIGUATION` |
| `COSTO_INCIERTO` | COST_UPDATE_LAG, MARGIN_LEAKAGE_SUSPECTED | estructura de costos | ¿producto, línea, servicio o negocio? | `NEEDS_EVIDENCE` |
| `DOCUMENTACION_DESORDENADA` | DOCUMENTARY_FRAGMENTATION | muestra del estado actual | ¿facturas, contratos, planillas? | `NEEDS_DISAMBIGUATION` |
| `MAESTRO_DESORDENADO` | SUPPLIER_MASTER_DUPLICATION, DOCUMENTARY_FRAGMENTATION | export del maestro | ¿proveedores, clientes, productos? | `NEEDS_EVIDENCE` |
| `TRAZABILIDAD_INSUFICIENTE` | OPERATIONAL_VISIBILITY_GAP | logs + descripción de proceso | ¿ventas, stock, cobros, decisiones? | `NEEDS_DISAMBIGUATION` |
| `DESCONOCIDO` | ninguna | relato ampliado | pregunta abierta mayéutica | `NEEDS_ORGANISM_CONTEXT` |

---

## 11. Preguntas de desambiguación

Regla: **no inductivas, no cerradas, no diagnósticas**.

### Para `DESCUADRE_DINERO`
> "Cuando decís que no te cierra la plata, ¿hablás de caja/banco,
> ventas/cobros, costos/margen, gastos/retiros o todavía no estás seguro?"

### Para `MARGEN_DUDOSO`
> "¿Querés revisar si los precios cubren los costos, si hay productos sin
> costo cargado o si el margen bajó en un período?"

### Para `DATOS_DUPLICADOS` / `MAESTRO_DESORDENADO`
> "¿Los duplicados están en proveedores, clientes, productos u otro
> listado?"

### Para `STOCK_INCONSISTENTE`
> "¿La diferencia está entre sistema y depósito, entre ventas y stock, o
> en movimientos sin registrar?"

### Para `SOBRECARGA_MANUAL`
> "¿Qué tarea se repite, con qué frecuencia y en qué archivos o sistemas
> ocurre?"

### Para `COSTO_INCIERTO`
> "¿El costo que te preocupa es de un producto, una línea, un servicio o
> el negocio completo?"

### Para `DOCUMENTACION_DESORDENADA`
> "¿El desorden está en facturas, comprobantes, contratos, planillas
> internas o todo junto?"

### Para `TRAZABILIDAD_INSUFICIENTE`
> "¿La trazabilidad que falta es de ventas, stock, cobros, movimientos o
> decisiones?"

### Para `DESCONOCIDO`
> "Contame con tus palabras qué querés entender o qué te preocupa."

---

## 12. Hipótesis abiertas

Una `HypothesisCandidate` es una afirmación **no confirmada** que solo
puede contrastarse con evidencia.

Contrato conceptual:

```yaml
hypothesis:
  hypothesis_id: string
  related_symptoms: list[str]
  related_pathologies: list[str]
  confidence_level: LOW | MEDIUM | HIGH
  evidence_required: list[EvidenceNeed]
  falsification_conditions: list[str]
  safety_warning: str
  next_question: str
```

Reglas:

- Una hipótesis abierta **no es diagnóstico**.
- `confidence_level` inicial siempre `LOW` hasta que hay evidencia.
- Toda hipótesis debe tener al menos una `falsification_condition`.
- Si no hay evidencia posible → la hipótesis queda en `LOW` y no se
  afirma.

Ejemplo:

```yaml
hypothesis:
  hypothesis_id: margen_erosionado_por_comisiones
  related_symptoms: [MARGEN_DUDOSO]
  related_pathologies: [MARGIN_LEAKAGE_SUSPECTED]
  confidence_level: LOW
  evidence_required:
    - evidence_type: excel_ventas_costos
      required_fields: [producto, precio_venta, costo, comision]
  falsification_conditions:
    - "margen_neto_real >= 20% en >70% productos"
  safety_warning: "No afirmar erosión sin considerar comisiones y logística."
  next_question: "¿Tenés un Excel de ventas con comisiones discriminadas?"
```

---

## 13. Evidencia sugerida

Contrato conceptual de `EvidenceSuggestion`:

```yaml
evidence_suggestion:
  evidence_type: str
  description: str
  required_fields: list[str]
  optional_fields: list[str]
  why_needed: str
  blocks_analysis: bool
  enables_classification: str | null
  examples: list[str]
```

### 13.1 Para SUPPLIER_MASTER_DUPLICATION
- **evidence_type:** `excel_proveedores`.
- **required_fields:** `proveedor`, `cuit` o `razon_social`.
- **optional_fields:** domicilio, email, categoría, fecha_alta.
- **why_needed:** "Permite detectar duplicados por CUIT y variaciones de
  razón social."
- **blocks_analysis:** si falta `proveedor`.
- **enables_classification:** `supplier_duplicate_check` (runtime real).

### 13.2 Para MARGIN_LEAKAGE_SUSPECTED
- **evidence_type:** `excel_ventas_costos`.
- **required_fields:** `producto`, `precio_venta`, `costo`.
- **optional_fields:** comisiones, logística, impuestos.
- **why_needed:** "Permite calcular margen neto real."
- **blocks_analysis:** si falta `costo` y se quiere margen.
- **enables_classification:** `excel_diagnostic` si es archivo tabular.

### 13.3 Para CASH_RECONCILIATION_DRIFT
- **evidence_type:** `extracto_bancario + cobros`.
- **required_fields:** `fecha`, `concepto`, `monto`.
- **optional_fields:** Mercado Pago / billeteras.
- **why_needed:** "Permite reconciliar ventas/cobros con saldo."
- **blocks_analysis:** sin extracto.
- **enables_classification:** ninguna en runtime real actual.

### 13.4 Para STOCK_TRACEABILITY_GAP
- **evidence_type:** `excel_stock + movimientos`.
- **required_fields:** `producto`, `stock_sistema`, `stock_real`, `fecha`.
- **optional_fields:** movimientos, ventas.
- **why_needed:** "Permite comparar sistema vs físico."
- **blocks_analysis:** sin ambos.
- **enables_classification:** ninguna en runtime real actual.

### 13.5 Para MANUAL_WORK_OVERLOAD
- **evidence_type:** `descripcion_flujo`.
- **required_fields:** tarea, frecuencia, archivos/sistemas.
- **optional_fields:** tiempo estimado.
- **why_needed:** "Permite dimensionar la carga manual."
- **blocks_analysis:** sin descripción.
- **enables_classification:** ninguna en runtime real actual.

---

## 14. Relación con clasificaciones reales

En Git real actual (HEAD `0354278`) existen:

- `excel_diagnostic`
- `supplier_duplicate_check`

El tanque puede **sugerir** estas clasificaciones cuando:

- `DATOS_DUPLICADOS` / `MAESTRO_DESORDENADO` + maestro de proveedores +
  evidencia compatible → sugerir `supplier_duplicate_check`.
- `MARGEN_DUDOSO` / `COSTO_INCIERTO` / `DESCUADRE_DINERO` + archivo
  tabular → sugerir `excel_diagnostic` (genérico).

El tanque **NO asume**:

- `--classification auto` (no implementado).
- routing automático (no implementado).
- HTML output (no implementado en HEAD real actual).
- nuevas clasificaciones no implementadas.

---

## 15. Safety gates aplicados

Los 8 gates definidos en `SMARTPYME_KNOWLEDGE_TANKS_ARCHITECTURE.md`:

### 15.1 NO_DIAGNOSIS_WITHOUT_EVIDENCE
- **Aplicación:** ninguna patología puede emitirse como afirmación.
- **Ejemplo:** ante "no me cierra la plata", el tanque emite
  `CASH_RECONCILIATION_DRIFT` como *candidata*, no como hecho.
- **Consecuencia:** status no pasa a `READY_TO_ANALYZE` sin evidencia.

### 15.2 NO_SELECTOR_ONLY_ACTIVATION
- **Aplicación:** un selector estructural (ej: Mercado Libre) no activa
  el tanque solo.
- **Ejemplo:** selector Mercado Libre + "quiero revisar mi negocio" →
  `NEEDS_DISAMBIGUATION`, sin patología.
- **Consecuencia:** tanque queda en `CANDIDATE` o no entra.

### 15.3 NO_UNSUPPORTED_OUTPUT_PROMISE
- **Aplicación:** no prometer HTML, routing automático ni diagnósticos
  que el runtime no soporta.
- **Ejemplo:** no decir "te mando el reporte HTML" si no hay `--html-out`.
- **Consecuencia:** outputs_allowed respeta runtime real.

### 15.4 NO_DOMAIN_CONTAMINATION
- **Aplicación:** el tanque no emite afirmaciones sobre dominios que no
  cubre.
- **Ejemplo:** no opinar sobre marketing si el caso es financiero puro.
- **Consecuencia:** `supported_domains` es cerrado.

### 15.5 NO_EXCESSIVE_EVIDENCE_REQUEST
- **Aplicación:** máximo 3 tipos de evidencia simultáneos.
- **Ejemplo:** para margen, pedir ventas + costos + (opcional) comisiones;
  nunca 6 archivos.
- **Consecuencia:** `EvidenceSuggestion` se prioriza.

### 15.6 USER_CONFIRMATION_REQUIRED_FOR_AMBIGUOUS_CASES
- **Aplicación:** si la reformulación es ambigua, el usuario debe
  confirmar.
- **Ejemplo:** "no me queda" puede ser margen o caja.
- **Consecuencia:** status `WAITING_OWNER_CONFIRMATION` hasta validar.

### 15.7 RUNTIME_COMPATIBILITY_REQUIRED
- **Aplicación:** solo sugerir clasificación si el runtime la soporta.
- **Ejemplo:** no sugerir `stock_traceability_check` porque no existe.
- **Consecuencia:** `suggested_classification` queda `null` si no hay match.

### 15.8 FAIL_CLOSED_ON_CONFLICT
- **Aplicación:** si dos hipótesis son incompatibles y no hay evidencia,
  no cerrar.
- **Ejemplo:** si "plata no cierra" puede ser caja o margen y no hay
  datos, no elegir.
- **Consecuencia:** status `NEEDS_DISAMBIGUATION`.

---

## 16. Ejemplos end-to-end

### 16.1 Ejemplo 1 — "No me cierra la plata"

- **raw_input:** "No me cierra la plata."
- **síntoma:** `DESCUADRE_DINERO`.
- **patología candidata:** `CASH_RECONCILIATION_DRIFT`.
- **reformulación:** "Entiendo que la señal principal es que la plata no
  cierra, pero todavía no sabemos si viene de caja, margen, cobros o
  gastos."
- **pregunta siguiente:** "¿Hablás de caja/banco, ventas/cobros,
  costos/margen, gastos/retiros o todavía no estás seguro?"
- **evidencia sugerida:** extracto bancario + reporte de cobros/ventas.
- **clasificación sugerida:** `null` (runtime no soporta clasificación
  específica de conciliación).
- **qué NO concluir:** causa del descalce.

### 16.2 Ejemplo 2 — "Vendo mucho pero no me queda nada"

- **raw_input:** "Vendo mucho pero no me queda nada."
- **síntoma:** `MARGEN_DUDOSO`.
- **patología candidata:** `MARGIN_LEAKAGE_SUSPECTED`.
- **reformulación:** "Entiendo que la sensación es que las ventas no se
  traducen en dinero disponible; falta saber si es margen, costos,
  comisiones o plazos."
- **pregunta siguiente:** "¿Querés revisar si los precios cubren los
  costos, si hay productos sin costo o si el margen bajó en un período?"
- **evidencia sugerida:** excel de ventas + costos + comisiones.
- **clasificación sugerida:** `excel_diagnostic` solo si hay archivo
  tabular.
- **qué NO concluir:** que el negocio es inviable.

### 16.3 Ejemplo 3 — "Tengo proveedores repetidos y CUIT mezclados"

- **raw_input:** "Tengo proveedores repetidos y CUIT mezclados."
- **síntoma:** `DATOS_DUPLICADOS` + `MAESTRO_DESORDENADO`.
- **patología candidata:** `SUPPLIER_MASTER_DUPLICATION`.
- **reformulación:** "Entiendo que hay un problema de proveedores
  repetidos o mal identificados, especialmente alrededor de CUIT o razón
  social."
- **pregunta siguiente:** "¿Los duplicados son solo proveedores o también
  hay casos en clientes/productos?"
- **evidencia sugerida:** excel de proveedores con `proveedor`, `cuit`,
  `razon_social`.
- **clasificación sugerida:** `supplier_duplicate_check` (existe en
  runtime real).
- **qué NO concluir:** cantidad exacta de duplicados sin validar.

### 16.4 Ejemplo 4 — "El sistema dice un stock y el depósito otro"

- **raw_input:** "El sistema dice un stock y el depósito otro."
- **síntoma:** `STOCK_INCONSISTENTE`.
- **patología candidata:** `STOCK_TRACEABILITY_GAP`.
- **reformulación:** "Entiendo que hay una discrepancia entre lo que dice
  el sistema y lo que hay físicamente; falta saber si es por movimientos
  no registrados o por errores de carga."
- **pregunta siguiente:** "¿La diferencia está entre sistema y depósito,
  entre ventas y stock, o en movimientos sin registrar?"
- **evidencia sugerida:** stock sistema + conteo físico + movimientos.
- **clasificación sugerida:** `null` (runtime real no soporta
  clasificación específica de stock).
- **qué NO concluir:** que hay robo o rotura.

### 16.5 Ejemplo 5 — "Copio todos los días de un Excel a otro"

- **raw_input:** "Copio todos los días de un Excel a otro."
- **síntoma:** `SOBRECARGA_MANUAL` (+ posible `DOCUMENTACION_DESORDENADA`).
- **patología candidata:** `MANUAL_WORK_OVERLOAD`.
- **reformulación:** "Entiendo que hay una tarea manual repetitiva que
  consume tiempo y probablemente depende de planillas."
- **pregunta siguiente:** "¿Qué tarea se repite, con qué frecuencia y en
  qué archivos o sistemas ocurre?"
- **evidencia sugerida:** descripción del flujo + archivos involucrados.
- **clasificación sugerida:** `null` (no hay clasificación runtime para
  automatización).
- **qué NO concluir:** que hay que migrar a ERP.

### 16.6 Ejemplo 6 — Selector Mercado Libre + "vendo pero no me queda"

- **raw_input:** "Vendo pero no me queda."
- **selector:** `sales_channel = Mercado Libre`.
- **síntoma:** `MARGEN_DUDOSO`.
- **patología candidata:** `MARGIN_LEAKAGE_SUSPECTED` (con énfasis en
  comisiones ML).
- **reformulación:** "Entiendo que vendés por Mercado Libre y la
  sensación es que no te queda; probablemente haya que revisar comisiones,
  logística y pricing."
- **pregunta siguiente:** "¿Querés revisar comisiones, costos de envío o
  precios?"
- **evidencia sugerida:** export ML + costos + precios.
- **clasificación sugerida:** `excel_diagnostic` si hay archivos.
- **qué NO concluir:** que ML es inviable.
- **safety gate activado:** `NO_SELECTOR_ONLY_ACTIVATION` (el selector
  solo refuerza, no diagnostica).

---

## 17. Límites explícitos

Este tanque **NO**:

- calcula fórmulas;
- procesa archivos;
- ejecuta clasificación;
- genera reporte final;
- toma decisiones;
- reemplaza criterio humano;
- hace benchmark sin sector declarado;
- recomienda precios;
- promete automatización;
- afirma causa raíz;
- atribuye responsabilidad;
- diagnostica sin evidencia validada.

---

## 18. Relación con futuro Evidence and Formula Tank

División de responsabilidades:

- **Operational Pathology Tank (este documento):** responde "qué parece
  estar pasando" → síntomas + patologías candidatas + preguntas +
  evidencia sugerida.
- **Evidence and Formula Tank (futuro):** responderá "qué evidencia y
  fórmulas permiten contrastarlo" → tipos documentales, campos esperados,
  fórmulas, hipótesis contrastables, criterios de suficiencia.

Ambos tanques deben coexistir en casos activos: el primero abre el
interrogatorio, el segundo lo cierra con evidencia.

---

## 19. Relación con futuro TankSelectionResult

Cuando exista el slice de selección, este tanque debería aparecer así:

```yaml
tank_selection_result:
  case_id: "case-001"
  tenant_id: "tenant_demo"
  selected_tanks:
    - tank_id: SMARTPYME_OPERATIONAL_PATHOLOGY_TANK
      version: "0.1.0-doc"
      lifecycle_state: ACTIVE
      activation_score: 0.8
      activation_reasons:
        - "symptom_match: MARGEN_DUDOSO"
        - "domain_match: comercial"
        - "evidence_available: Excel"
      missing_evidence:
        - evidence_type: excel_ventas_costos
          required_fields: [producto, precio_venta, costo]
      safety_warnings:
        - "NO_DIAGNOSIS_WITHOUT_EVIDENCE"
      next_action: "emit_evidence_request"
  candidate_tanks: []
  suspended_tanks: []
  rejected_tanks: []
  unsupported_tanks: []
  conflicts: []
```

---

## 20. Criterios de aceptación para futura implementación

La futura implementación debe:

### Funcionales
- consumir `InterrogationResult` serializable;
- no emitir diagnóstico;
- devolver salida serializable;
- generar preguntas y evidencia mínima;
- aplicar los 8 safety gates;
- sugerir clasificación solo si el runtime la soporta.

### Testing
- tests por cada síntoma;
- tests de falsa activación;
- tests de selector aislado (no debe activar);
- tests de evidencia insuficiente;
- tests de conflicto entre hipótesis;
- tests de desactivación por corrección del usuario.

### Integración
- no tocar runtime de diagnóstico;
- no asumir `--classification auto`;
- no asumir `--html-out`;
- integrarse con futuro `TankSelectionResult`.

### Documentación
- versión MAJOR alineada con contrato de KnowledgeTank;
- ejemplos end-to-end actualizados;
- matriz de patologías vs. evidencia actualizada.

---

## 21. Roadmap posterior

Siguiente frente recomendado:

```text
SMARTPYME_EVIDENCE_AND_FORMULA_TANK_DOC
```

Luego, en orden:

1. `SMARTPYME_TANK_SELECTION_SLICE` — implementar selección determinística
   de tanques a partir de `InterrogationResult`.
2. `SMARTPYME_INTAKE_RECORD_AND_EVIDENCE_REQUEST` — persistir
   interrogatorio, tanques seleccionados y pedidos de evidencia.
3. `SMARTPYME_DEMO_WITH_INTAKE_BEFORE_REPORT` — demo end-to-end con
   interrogatorio → tanques → evidencia → análisis → reporte.

---

*Este documento es normativo a nivel de diseño. No implica implementación
runtime en el HEAD actual.*
