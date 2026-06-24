# SERVICE_1_CAPABILITY_MATURITY_AUDIT_V1

## Estado

```text
AUDIT_ONLY
NO_CODE_CHANGE
NO_RUNTIME_CHANGE
NO_TEST_CHANGE
```

## Prompt previo para auditor externo

```text
Actúa como auditor externo de arquitectura y producto operacional para PymIA Servicio 1.

Objetivo:
Auditar robustez y madurez real de Servicio 1 contrastando capacidades implementadas/documentadas contra el catálogo mayoritario de patologías PyME.

Fuentes obligatorias a leer:
- docs/pathology_catalog.v1.json
- docs/formula_catalog.v1.json
- docs/producto/PYMIA_SERVICE_1_CAPABILITY_MATRIX_V2.md
- docs/producto/PYMIA_SERVICE_1_FULL_CATALOG_V1.md
- docs/producto/SERVICE_1_MATURITY_CLOSEOUT_POST_EXCEL_TREATMENT_LAB_V1.md
- docs/producto/SERVICE_1_WEB_TEST_INTERFACE_ROUTE_REGISTRY_V1.md
- docs/producto/SERVICE_1_WEB_TEST_INTERFACE_RUN_SPEC_V1.md
- docs/producto/SERVICE_1_XLSX_BROWSER_SANDBOX_LANDING_V1.md
- PymIA-Live/pymia/smartpyme/service_1_microservice_registry_contract_v1.py
- PymIA-Live/pymia/smartpyme/service_1_web_test_route_registry_v1.py
- PymIA-Live/pymia/smartpyme/service_1_web_test_run_spec_v1.py
- PymIA-Live/pymia/smartpyme/file_intake_v1.py
- PymIA-Live/pymia/smartpyme/service_1_xlsx_delivery_v1.py
- PymIA-Live/pymia/smartpyme/excel_treatment_lab_completion_slice_v1.py
- PymIA-Live/pymia/smartpyme/invoice_collection_matching_sandbox_completion_slice_v1.py
- PymIA-Live/pymia/smartpyme/bank_reconciliation_sandbox_completion_slice_v1.py
- PymIA-Live/pymia/smartpyme/accounting_workpaper_completion_slice_v1.py
- PymIA-Live/tests/smartpyme/

Reglas de auditoría:
- No evaluar marketing.
- No evaluar landing como venta.
- No confundir demo con capacidad operativa.
- No llamar maduro a lo que sólo está documentado.
- No llamar robusto a lo que no tenga tests.
- No llamar diagnóstico a una preparación de evidencia.
- No exigir que Servicio 1 confirme patologías: medir si prepara evidencia útil para investigarlas.
- Separar Servicio 1 de Servicio 2 diagnóstico.
- Separar sandbox de producción.
- Separar synthetic fixture de real anonymized case.

Catálogo de contraste:
Usar docs/pathology_catalog.v1.json como universo de 50 patologías PyME.
Agrupar por categorías:
- liquidez
- rentabilidad
- inventario
- fiscal_contable
- marketplaces
- cobranzas
- operaciones_financieras
- operaciones
- pricing
- datos
- gestion
- personas
- sistemas
- logistica
- finanzas
- ventas
- rrhh

Coeficientes a calcular, escala 0.00 a 1.00:

1. COEF_ROBUSTEZ_TECNICA
   Evalúa tests, fail-closed, pure contracts, no IO inesperado, no runtime no autorizado, no claims finales.

2. COEF_MADUREZ_OPERATIVA
   Evalúa si un operador puede repetir el flujo sin improvisar: intake, routing, run spec, checklist, outputs, QA, cierre/bloqueo.

3. COEF_COBERTURA_PATOLOGIAS_PYME
   Evalúa contra las 50 patologías del catálogo cuántas quedan cubiertas por Servicio 1 como preparación de evidencia, no como diagnóstico.
   Categorías:
   - DIRECTA: Servicio 1 puede preparar evidencia clara para investigarla.
   - PARCIAL: Servicio 1 puede aportar archivos/estructura, pero faltan variables o protocolo.
   - FUERA_DE_SCOPE: pertenece a Servicio 2, fiscal profundo, API, OCR, marketplace, RRHH, etc.

4. COEF_PREPARACION_EVIDENCIA
   Evalúa capacidad de recibir XLSX/CSV, leer hojas/columnas, detectar faltantes/ambigüedades, exportar owner answers y generar paquetes revisables.

5. COEF_CONTROL_RIESGO
   Evalúa bloqueo de datos reales, producción, Mercado Pago, Servicio 2, OCR, APIs, diagnóstico final, claims contables/fiscales.

6. COEF_CAPACIDAD_PROFESIONAL_GLOBAL
   Promedio ponderado:
   - robustez técnica: 25%
   - madurez operativa: 25%
   - cobertura patologías como preparación de evidencia: 20%
   - preparación de evidencia: 20%
   - control de riesgo: 10%

Formato de respuesta obligatorio:

VEREDICTO:
COEFICIENTES:
TABLA_CAPACIDADES:
CONTRASTE_PATOLOGIAS:
DIRECT_COVERAGE:
PARTIAL_COVERAGE:
OUT_OF_SCOPE:
GAPS_CRITICOS:
GAPS_MEDIOS:
NO_HACER:
NEXT_5_SLICES_RECOMENDADOS:
DECISION_FINAL:

No proponer marketing.
No proponer slogans.
No proponer venta.
No proponer coaching.
Responder como auditor técnico-operacional.
```

---

## 1. Veredicto

```text
SERVICE_1_CAPABILITY_MATURITY_AUDIT_V1:
PARTIAL_BUT_STRUCTURALLY_REAL
```

Servicio 1 ya no es sólo una idea documental. Tiene contratos, módulos, tests, paquetes, rutas sandbox y varias familias de salida. Sin embargo, todavía no debe llamarse completo en sentido profesional fuerte porque le faltan tres capas de madurez operacional:

```text
1. checklist de revisión humana final por corrida;
2. corpus de casos XLSX reales anonimizados;
3. protocolo explícito de aceptación/bloqueo por tipo de archivo y por familia de problema.
```

El contraste contra el catálogo de 50 patologías PyME muestra que Servicio 1 no debe intentar diagnosticar la mayoría de patologías. Su lugar correcto es preparar evidencia, ordenar archivos y producir paquetes revisables para una fracción relevante de patologías de datos, caja/banco, cobranzas, inventario, rentabilidad básica y pricing.

---

## 2. Fuentes leídas / usadas

### Código Servicio 1 identificado

```text
PymIA-Live/pymia/smartpyme/file_intake_v1.py
PymIA-Live/pymia/smartpyme/file_intake_taskspec_boundary_v1.py
PymIA-Live/pymia/smartpyme/service_1_taskspec_contract_v1.py
PymIA-Live/pymia/smartpyme/service_1_taskspec_assembler_v1.py
PymIA-Live/pymia/smartpyme/service_1_xlsx_delivery_v1.py
PymIA-Live/pymia/smartpyme/excel_treatment_lab_v1.py
PymIA-Live/pymia/smartpyme/excel_treatment_lab_completion_slice_v1.py
PymIA-Live/pymia/smartpyme/invoice_collection_matching_sandbox_completion_slice_v1.py
PymIA-Live/pymia/smartpyme/bank_reconciliation_sandbox_completion_slice_v1.py
PymIA-Live/pymia/smartpyme/accounting_workpaper_completion_slice_v1.py
PymIA-Live/pymia/smartpyme/service_1_microservice_registry_contract_v1.py
PymIA-Live/pymia/smartpyme/service_1_microservice_activation_contract_v1.py
PymIA-Live/pymia/smartpyme/service_1_web_test_route_registry_v1.py
PymIA-Live/pymia/smartpyme/service_1_web_test_run_spec_v1.py
```

### Docs Servicio 1 identificados

```text
docs/producto/PYMIA_SERVICE_1_CAPABILITY_MATRIX_V2.md
docs/producto/PYMIA_SERVICE_1_FULL_CATALOG_V1.md
docs/producto/SERVICE_1_MATURITY_CLOSEOUT_POST_EXCEL_TREATMENT_LAB_V1.md
docs/producto/SERVICE_1_WEB_TEST_INTERFACE_DESIGN_V1.md
docs/producto/SERVICE_1_WEB_TEST_INTERFACE_ROUTE_REGISTRY_V1.md
docs/producto/SERVICE_1_WEB_TEST_INTERFACE_RUN_SPEC_V1.md
docs/producto/SERVICE_1_XLSX_BROWSER_SANDBOX_LANDING_V1.md
```

### Catálogo de patologías usado como contraste

```text
docs/pathology_catalog.v1.json
```

Catálogo declarado:

```text
50 patologías PyME
```

---

## 3. Coeficientes

Escala:

```text
0.00 = inexistente
0.25 = documental / débil
0.50 = parcial operativo
0.75 = robusto en sandbox / focal
1.00 = profesional completo con casos reales controlados
```

| Coeficiente | Valor | Lectura |
|---|---:|---|
| COEF_ROBUSTEZ_TECNICA | 0.78 | Hay contratos puros, tests focales, rutas allowlist, run spec, suite verde previa. Falta checklist/review terminal y más corpus real. |
| COEF_MADUREZ_OPERATIVA | 0.58 | Hay harness, manifest, delivery packages y run spec. Falta protocolo operativo completo por caso real y cierre humano verificable por checklist. |
| COEF_COBERTURA_PATOLOGIAS_PYME | 0.34 | Servicio 1 prepara evidencia útil para una fracción relevante, pero la mayoría de patologías quedan fuera o sólo parcialmente cubiertas. Correcto: no debe diagnosticarlas. |
| COEF_PREPARACION_EVIDENCIA | 0.66 | Buena base XLSX/file-intake/sandbox/owner answers; falta custodia fuerte, corpus real anonimizado y protocolo por familia de archivo. |
| COEF_CONTROL_RIESGO | 0.86 | Muy buena postura fail-closed: no producción, no runtime autorizado, no Servicio 2, no Mercado Pago, no OCR/API, no final claims. |

Cálculo ponderado:

```text
0.78 * 0.25 = 0.195
0.58 * 0.25 = 0.145
0.34 * 0.20 = 0.068
0.66 * 0.20 = 0.132
0.86 * 0.10 = 0.086
TOTAL = 0.626
```

```text
COEF_CAPACIDAD_PROFESIONAL_GLOBAL: 0.63
```

Lectura:

```text
Servicio 1 está técnicamente encaminado y bien protegido, pero todavía no es una capacidad profesional completa. Está en madurez media-alta de arquitectura/sandbox y madurez media de operación real.
```

---

## 4. Tabla de capacidades

| Capacidad | Estado auditado | Robustez | Madurez | Observación |
|---|---|---:|---:|---|
| File Intake V1 | IMPLEMENTED_VALIDATED | Alta | Media | Buena frontera inicial; XLSX-first; no debe inflarse a diagnóstico. |
| File Intake -> TaskSpecPatch | IMPLEMENTED_VALIDATED | Alta | Media | Frontera útil, pura, sin runtime. |
| Service1TaskSpec | IMPLEMENTED_PARTIAL | Media | Media-baja | Existe contrato/assembler, pero falta uso operativo fuerte como columna vertebral de casos reales. |
| Owner response / message | IMPLEMENTED_VALIDATED | Alta | Media | Sirve como salida conservadora; no sustituye paquete profesional completo. |
| Excel triage / treatment lab | IMPLEMENTED_PARTIAL / FOCAL | Media-alta | Media | Núcleo más alineado con Servicio 1. Falta corpus real amplio y QA de transformación. |
| XLSX delivery | IMPLEMENTED_VALIDATED / SANDBOX | Alta | Media | Buen patrón de archivo como producto; falta producción controlada con datos anonimizados. |
| Invoice/collection matching sandbox | IMPLEMENTED_FOCAL | Media-alta | Media-baja | Útil como preparación; no cerrar saldos definitivos. |
| Bank reconciliation sandbox | IMPLEMENTED_FOCAL | Media-alta | Media-baja | Útil como preparación; no conciliación final. |
| Accounting workpaper draft | IMPLEMENTED_PARTIAL/FOCAL | Media | Media | Interesante para contadores; requiere control de responsabilidad profesional. |
| Microservice registry | IMPLEMENTED_VALIDATED | Alta | Media | Excelente para evitar deriva de capacidades. |
| Web route registry | IMPLEMENTED_VALIDATED | Alta | Media | Buena allowlist para no exponer rutas peligrosas. |
| Web run spec | IMPLEMENTED_VALIDATED | Alta | Media | Buena estructura previa a ejecución; falta review checklist. |
| Browser XLSX sandbox landing | IMPLEMENTED_CANDIDATE | Media | Baja-media | Útil como ensayo de carga/preview/preguntas; no debe confundirse con core. |
| Operator harness | IMPLEMENTED_VALIDATED/PARTIAL | Media-alta | Media | Necesita rehearsal documentado sobre casos reales anonimizados. |
| QA checklist | DOCUMENTED/PARTIAL | Media | Media-baja | Falta convertir en gate más duro por corrida/caso. |
| Evidence custody | INSUFFICIENT | Baja | Baja | Falta hash/custodia/estado por archivo real como disciplina central. |
| Real anonymized corpus | INSUFFICIENT | Baja | Baja | Bloqueo principal para madurez profesional. |

---

## 5. Contraste contra 50 patologías PyME

Servicio 1 no debe confirmar patologías. El contraste mide si puede preparar evidencia para investigarlas.

### Cobertura directa como preparación de evidencia

| Código | Patología | Categoría | Motivo |
|---|---|---|---|
| LIQ_001 | Descalce de Ventas y Cobranzas | liquidez | Matching factura/cobranza y preparación de cobranzas. |
| LIQ_002 | Flujo de Caja sin Anticipación | liquidez | Puede preparar caja/banco/cobros/pagos, no proyectar con autoridad. |
| REN_001 | Margen Invisible | rentabilidad | Excel Treatment Lab puede preparar ventas/costos/precios faltantes. |
| REN_002 | Costo de Reposición Ignorado | rentabilidad | Puede ordenar listas/costos; requiere fuentes de reposición. |
| INV_001 | Stock Crítico | inventario | Puede preparar stock/ventas/lead time si existen columnas. |
| INV_002 | Capital Inmovilizado en Stock | inventario | Puede preparar stock promedio/CMV si hay evidencia. |
| PYME_008 | Síndrome del Stock Fantasma | inventario | Puede contrastar hojas/stock declarado como preparación. |
| PYME_011 | DSO Incremental Silencioso | cobranzas | Puede preparar cuentas por cobrar/ventas/fechas. |
| PYME_015 | Conciliación Bancaria Crónica | operaciones_financieras | Bank reconciliation sandbox prepara revisión, no cierre final. |
| PYME_017 | Pricing Drift | pricing | Puede preparar listas/precios/costos; benchmark mercado queda fuera. |
| PYME_018 | Data Decay | datos | Excel/file triage detecta vacíos, inconsistencias, estructura débil. |
| PYME_022 | Fragilidad por Dispersión de Datos | datos | Servicio 1 ataca archivos dispersos y estructura. |
| PYME_038 | Caos de Versiones | datos | Puede evidenciar archivos múltiples/versiones, si intake lo registra. |
| PYME_044 | Subsidio Oculto a Clientes | rentabilidad | Puede preparar ventas/costos por cliente si existe granularidad. |
| PYME_046 | Mezcla de Finanzas | finanzas | Puede preparar caja/banco/contable, no concluir definitivamente. |
| PYME_048 | Obsolescencia de Precios | pricing | Puede preparar costos/precios/fechas. |
| PYME_049 | Falsa Rentabilidad | rentabilidad | Puede preparar reposición/margen, no dictaminar sin evidencia. |

Resultado directo:

```text
17 / 50 patologías con cobertura directa como preparación de evidencia
```

### Cobertura parcial

| Código | Patología | Categoría | Motivo |
|---|---|---|---|
| PYME_013 | Descalce DSO vs DPO | liquidez | Requiere cobranzas + proveedores; Servicio 1 puede preparar ambos, falta protocolo integrado. |
| PYME_014 | Ilusión del Margen Positivo | rentabilidad | Requiere comisiones/costos fijos unitarios; parcial. |
| PYME_024 | Agotamiento de Capital de Trabajo | liquidez | Requiere balance/activos/pasivos; Servicio 1 puede ordenar, no evaluar completo. |
| PYME_026 | Cash Flow Operativo Negativo | liquidez | Requiere clasificación operativa consistente; parcial. |
| PYME_027 | Costo Financiero sobre EBITDA Excesivo | finanzas | Requiere EBITDA/intereses confiables; parcial. |
| PYME_028 | Ausencia de Fondo de Emergencia | liquidez | Requiere costos fijos/reservas; parcial. |
| PYME_033 | Concentración de Riesgo en SKU | ventas | Puede prepararse con ventas por SKU; falta protocolo de salida S1 específico. |
| PYME_040 | Puente Mental Multi-vía | operaciones | Puede observar dispersión/manualidad; medición objetiva parcial. |
| PYME_047 | Rigidez de Procesos Artesanales | operaciones | Puede registrar carga manual; cuantificación parcial. |

Resultado parcial:

```text
9 / 50 patologías con cobertura parcial
```

### Fuera de scope para Servicio 1 actual

Grupos principalmente fuera:

```text
fiscal_contable profundo
marketplaces / reputación / SLA
sistemas / tokens / APIs
RRHH profundo
personas / burnout / estrés
logística avanzada
benchmarks externos
Servicio 2 diagnóstico integral
```

Ejemplos:

```text
PYME_004 AxI
PYME_007 reputación
PYME_009 ARCA
PYME_012 impuestos operativos
PYME_029 a PYME_034 marketplace SLA/reclamos/cancelaciones
PYME_035 a PYME_037 fiscal/sistemas
PYME_039 recategorización
PYME_041 sueldos
PYME_043 boreout
PYME_045 IVA como capital
PYME_050 estrés/quilombo emocional
```

Resultado fuera de scope:

```text
24 / 50 patologías fuera de scope para Servicio 1 actual
```

### Resumen cobertura

```text
DIRECTA: 17/50 = 34%
PARCIAL: 9/50 = 18%
FUERA_DE_SCOPE: 24/50 = 48%
```

Lectura correcta:

```text
Servicio 1 cubre profesionalmente una primera capa de preparación de evidencia para patologías de archivos/datos/Excel/caja/stock/cobranza/rentabilidad básica. No cubre, ni debe cubrir todavía, diagnóstico profundo de la mayoría del catálogo PyME.
```

---

## 6. Hallazgos duros

### H1 — Servicio 1 tiene buena protección, pero todavía poca realidad empírica

Hay mucha protección contractual y tests. Falta corpus de casos reales anonimizados con archivos difíciles.

Impacto:

```text
Alta robustez de borde, madurez real todavía insuficiente.
```

### H2 — La web sandbox es útil, pero no debe volverse centro de madurez

El browser sandbox ayuda a ensayar carga y preguntas. No robustece por sí mismo la capacidad profesional.

Impacto:

```text
Si se sigue por UI antes que por corpus/protocolo/QA, deriva.
```

### H3 — Falta `Evidence Custody` específica de Servicio 1

Servicio 1 trabaja con archivos. Debe registrar mínimo:

```text
file_name
hash
type
source
received_at
sensitivity_mode
anonymized_flag
processing_status
outputs_derived
reviewer
```

Sin esto, el servicio no madura como laboratorio serio.

### H4 — Falta acceptance/bloqueo por familia de archivo

No alcanza con “XLSX-first”. Hace falta definir cuándo un XLSX es:

```text
usable
usable_with_questions
blocked_missing_context
blocked_sensitive_data
unsupported
```

### H5 — Falta corpus de edge cases XLSX

El catálogo de patologías exige variedad real:

```text
ventas sin costos
stock con negativos
fechas mezcladas
hojas múltiples
encabezados rotos
cobranzas parciales
banco sin referencia
listas duplicadas
versiones múltiples
archivos exportados de sistemas
```

---

## 7. Gaps críticos

| Gap | Prioridad | Razón |
|---|---:|---|
| SERVICE_1_EVIDENCE_CUSTODY_V1 | P0 | Sin custodia de archivos, el servicio no es serio. |
| SERVICE_1_XLSX_ACCEPTANCE_AND_BLOCKING_PROTOCOL_V1 | P0 | Define cuándo operar y cuándo bloquear. |
| SERVICE_1_VALIDATION_CASE_CORPUS_V1 | P0 | Sin corpus real/anonimizado no hay madurez empírica. |
| SERVICE_1_REVIEW_CHECKLIST_V1 | P0 | Falta gate humano final por corrida. |
| SERVICE_1_OPERATOR_REHEARSAL_PROTOCOL_V1 | P1 | Permite repetir sin improvisar. |
| SERVICE_1_PATHOLOGY_EVIDENCE_COVERAGE_MAP_V1 | P1 | Vincula patologías a evidencia que Servicio 1 puede preparar. |

---

## 8. No hacer

```text
No abrir Servicio 2.
No prometer diagnóstico PyME integral.
No abrir Mercado Pago real.
No abrir OCR.
No abrir APIs bancarias.
No publicar la sandbox como producto real.
No seguir agregando rutas sin corpus.
No medir madurez por cantidad de features.
No convertir cada patología en módulo de Servicio 1.
No meter LLM runtime en core.
```

---

## 9. Próximos 5 slices recomendados

### 1. SERVICE_1_EVIDENCE_CUSTODY_V1

Crear contrato puro de custodia de archivos recibidos/tratados.

Campos mínimos:

```text
case_id
file_id
original_file_name
file_kind
sha256
source_channel
received_at
sensitivity_mode
anonymized_flag
allowed_use
processing_status
outputs_derived
review_required
```

### 2. SERVICE_1_XLSX_ACCEPTANCE_AND_BLOCKING_PROTOCOL_V1

Definir reglas para aceptar/bloquear XLSX.

Estados:

```text
ACCEPTED_FOR_REVIEW
ACCEPTED_WITH_OWNER_QUESTIONS
BLOCKED_MISSING_CONTEXT
BLOCKED_SENSITIVE_DATA
UNSUPPORTED_FILE
```

### 3. SERVICE_1_VALIDATION_CASE_CORPUS_V1

Crear catálogo de casos de validación, no necesariamente archivos todavía.

Cada caso:

```text
case_id
file_family
pathology_evidence_targets
expected_questions
expected_blockers
expected_outputs
acceptance_criteria
```

### 4. SERVICE_1_REVIEW_CHECKLIST_V1

Gate humano final.

Debe revisar:

```text
archivo abre
preview coincide
preguntas respondidas
outputs esperados
claims prohibidos ausentes
bloqueos documentados
siguiente paso claro
```

### 5. SERVICE_1_PATHOLOGY_EVIDENCE_COVERAGE_MAP_V1

Mapa directo entre 50 patologías y evidencia que Servicio 1 puede preparar.

No diagnostica.

Sólo responde:

```text
qué evidencia necesita esta patología
qué parte puede preparar Servicio 1
qué parte queda fuera
qué archivo/hoja/columna suele aparecer
```

---

## 10. Decisión final

```text
SERVICE_1_IS_NOT_YET_PROFESSIONALLY_COMPLETE
SERVICE_1_IS_READY_FOR_PROFESSIONAL_HARDENING
```

Orden correcto:

```text
custodia
aceptación/bloqueo XLSX
corpus
review checklist
mapa patología -> evidencia
```

No más madurez por UI.
No más madurez por narrativa.
No más madurez por cantidad de componentes.

La madurez real de Servicio 1 debe medirse por:

```text
cuántos archivos reales/anonimizados puede recibir,
cuánto puede entender sin inventar,
cuándo sabe bloquear,
qué salida revisable puede devolver,
y qué evidencia deja para investigar patologías PyME sin diagnosticarlas falsamente.
```
