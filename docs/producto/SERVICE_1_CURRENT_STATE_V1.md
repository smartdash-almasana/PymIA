# SERVICE_1_CURRENT_STATE_V1

## Estado

```text
Tipo: CURRENT_STATE_CANONICAL_SOURCE
Servicio: SERVICE_1 / SmartPyme
Estado: ACTIVE_SOURCE_OF_TRUTH
Runtime impact: NONE
Code impact: NONE
Tests impact: NONE
```

## Propósito

Este documento es la fuente canónica viva del estado actual de Servicio 1.

No es roadmap histórico.
No es closeout de microciclo.
No es TaskSpec de implementación.
No abre código.
No autoriza nueva etapa por sí solo.

Su función es reducir deriva documental: cuando documentos previos describan estados superados, este documento manda para la lectura operativa actual.

---

## 1. Regla de autoridad documental

```text
Si hay contradicción sobre estado actual de Servicio 1:

1. SERVICE_1_CURRENT_STATE_V1.md
2. HEAD verificado del repo
3. closeouts recientes de familia
4. documentos rectores / roadmaps históricos
5. traces / catálogos / arqueologías antiguas
```

Los documentos anteriores quedan como evidencia histórica, diseño o trazabilidad, pero no como fuente primaria de estado actual si contradicen este archivo.

---

## 2. Último estado verificado

```text
HEAD_VERIFIED:
a909f809efa465a68e3d863ceceff02da67cd1d4

COMMIT:
docs(pymia): close service 1 excel factory stage

WORKING_TREE_AT_AUDIT:
clean
```

Validaciones recientes relevantes:

```text
First Aid family:
53 passed

Excel Factory stage:
47 passed
```

Este documento no vuelve a correr tests.

---

## 3. Estado actual por familia

| Familia | Estado actual | Lectura vigente |
|---|---|---|
| Primeros Auxilios | `CLOSED_IN_SCOPE_RUNTIME` | Cerrada como familia runtime allowlisted; no declara Servicio 1 full. |
| Laboratorio Excel | `CLOSED_IN_SCOPE_RUNTIME` | Ingesta, profiling y structured evidence productizados en `pymia.smartpyme`. |
| Factoría Excel | `CLOSED_IN_SCOPE_RUNTIME` | Cerrada para ruta explícita de operador CLI vía `--run-factory`. |
| Excel con fórmulas | `PARTIAL_FACTORY_ONLY` | Permitido sólo por carril Factoría Excel; First Aid y delivery genérico siguen sin fórmulas. |
| Servicios para contadores | `PARTIAL_SYNTHETIC_RUNTIME_AND_CONTRACT_GATE` | Hay contratos, gates y paquetes sintéticos; no producción real. |
| Conciliaciones | `PARTIAL_SANDBOX_OR_CONTRACT` | Hay sandbox/contract; no motor real productivo. |
| PDF/CSV/Excel normalizado | `MISSING_FOR_CSV_AND_PDF` | Excel existe; CSV/PDF no tienen módulos productivos en `smartpyme`. |
| FSM / LLM / Chatbot | `FROZEN_OR_MISSING` | FSM experimental congelada; no hay adapter LLM ni chatbot operativo. |

---

## 4. Entry points reales actuales

```text
PymIA-Live/pymia/cli/service_1_operator.py
```

Ramas relevantes:

```text
--file <path>
--confirmed-columns <json>
--run-first-aid
--run-tools <json>
--run-factory
--template-ref
--formula-ref
--factory-input key=value
--factory-output
```

Otros entrypoints o slices pueden existir para pruebas o completion slices, pero el operador CLI es la ruta real más fuerte para ejecución asistida actual.

---

## 5. Capacidades ejecutables actuales

### 5.1 Intake / estructura XLSX

```text
- Construcción de FileAsset desde archivo local.
- Ejecución de entrypoint mínimo de Servicio 1.
- Lectura estructural de XLSX.
- Detección de hojas y columnas.
- Generación de packet de confirmación de columnas.
- Escritura de carpeta de caso.
- QA delivery gate.
```

### 5.2 Primeros Auxilios

```text
- Pipeline `service_1_pipeline_v1`.
- 5 tools determinísticas allowlisted.
- `--run-tools <json>` desde CLI operador.
- Delivery XLSX manual por tool, sin fórmulas activas.
- `pipeline_result.json`.
- Manifest/case folder.
```

Tools cerradas en alcance:

```text
precio_margen_basico
caja_diaria_triage
stock_alertas_basicas
gastos_triage
proveedores_precio_variacion_triage
```

### 5.3 Laboratorio Excel

```text
- `excel_lab_ingestion_v1.py` productizado.
- Ingestión estructural.
- Profiling semántico.
- Normalización básica.
- StructuredEvidence exportable.
- Wrapper de compatibilidad en `tools/document_ingestion.py`.
```

### 5.4 Factoría Excel

```text
- `exceland_bridge_v1.py` valida contrato lógico.
- `exceland_runtime_v1.py` ejecuta `exceland_factory.build_product(...)`.
- `exceland_execution_flow_v1.py` orquesta bridge -> mapping -> runtime.
- `service_1_operator.py --run-factory` ejecuta la ruta controlada.
- Genera `factory_result.json`.
- Genera XLSX físico para templates mapeados.
```

Templates mapeados a runtime:

```text
precio_margen_basico_template -> precio_margen
caja_diaria_template -> caja_diaria
stock_alertas_basicas_template -> stock_control
```

Templates reconocidos por bridge pero no mapeados a runtime:

```text
gastos_triage_template -> TEMPLATE_NOT_MAPPED
proveedores_precio_variacion_template -> TEMPLATE_NOT_MAPPED
```

---

## 6. Capacidades documentadas o parciales, no cerradas como runtime productivo

```text
Servicios para contadores:
- accounting workpaper contract
- manifest model
- draft packet
- human review gate
- synthetic completion slice
- operator package

Conciliaciones:
- bank reconciliation contract/sandbox
- invoice collection matching sandbox
- Mercado Pago reconciliation contract

Normalización multi-formato:
- Excel: existe
- CSV: missing en smartpyme
- PDF: missing en smartpyme

Conversacional:
- FSM experimental congelada
- LLM adapter missing
- chatbot missing
```

Estas capacidades no deben venderse ni tratarse como Servicio 1 full.

---

## 7. Límites actuales prohibidos

```text
NO declarar Servicio 1 full.
NO abrir pipeline full por inferencia.
NO mezclar First Aid con diagnóstico contable.
NO afirmar conciliación real productiva.
NO afirmar Mercado Pago runtime.
NO afirmar PDF intake productivo.
NO afirmar CSV intake productivo.
NO afirmar chatbot operativo.
NO afirmar LLM adapter cableado.
NO reactivar FSM congelada sin auditoría explícita.
NO usar Factoría Excel como owner-facing delivery final automático.
NO mover fórmulas activas al delivery genérico.
```

Regla madre vigente:

```text
La IA conversa.
La FSM gobierna.
Las tools ejecutan.
Los archivos son el producto.
```

En el estado actual, la FSM productiva y el LLM adapter todavía no están abiertos.

---

## 8. Documentos históricos reemplazados como fuente de estado actual

Los siguientes documentos pueden contener afirmaciones superadas sobre Factoría Excel o estado de familias. Deben leerse como históricos o rectores de intención, no como estado actual si contradicen este documento:

```text
SERVICE_1_DEVELOPMENT_AUDIT_AND_COMPLETION_ROADMAP_V1.md
SERVICE_1_FULL_CLOSURE_RECTOR_V1.md
SERVICE_1_FULL_LAYERED_IMPLEMENTATION_TRACE_V1.md
PYMIA_SERVICE_1_FULL_CATALOG_V1.md
SERVICE_1_EXCELAND_BRIDGE_V1.md
```

Ejemplos de afirmaciones superadas como descripción actual completa:

```text
- Factoría Excel = PARTIAL_EXTERNAL_DEPENDENCY sin generación física controlada.
- exeland2/factory genera XLSX, pero no está conectada a PymIA-Live.
- el bridge existe, pero todavía NO ejecuta Exceland real.
- falta frontera runtime para compilar/generar XLSX real.
```

Lectura vigente:

```text
Factoría Excel está CLOSED_IN_SCOPE_RUNTIME para su ruta explícita de operador CLI.
```

Esa lectura no equivale a Servicio 1 full.

---

## 9. Próxima etapa activa recomendada

Antes de código nuevo:

```text
SERVICE_1_STAGE_5_NORMALIZATION_SCOPE_DESIGN_V1
```

Objetivo:

```text
Diseñar la Etapa 5 — CSV + PDF + normalizador común.
```

Orden sugerido:

```text
1. CSV intake
2. normalizador común
3. PDF intake
```

Motivo:

```text
CSV es más controlable que PDF y permite cerrar una frontera real sin OCR ni parser PDF prematuro.
```

---

## 10. Política documental desde este punto

```text
No crear micro-closeouts salvo excepción.
No crear un documento por cada microciclo si el estado puede actualizarse aquí.
No editar masivamente el museo documental.
No borrar historia.
Mantener este documento como fuente canónica viva.
Usar TaskSpec activo para el frente abierto.
Usar roadmap sólo para dirección, no para estado actual.
```

Documentos activos recomendados:

```text
SERVICE_1_CURRENT_STATE_V1.md
SERVICE_1_FULL_CLOSURE_RECTOR_V1.md
SERVICE_1_DEVELOPMENT_AUDIT_AND_COMPLETION_ROADMAP_V1.md
SERVICE_1_ACTIVE_TASKSPEC.md, si se decide crearlo
```

---

## 11. Veredicto

```text
SERVICE_1_CURRENT_STATE_CANONICALIZED

CURRENT_CAPABILITY:
REAL_BUT_PARTIAL

SERVICE_1_FULL:
NOT_CLOSED

NEXT_SAFE_STEP:
SERVICE_1_STAGE_5_NORMALIZATION_SCOPE_DESIGN_V1
```
