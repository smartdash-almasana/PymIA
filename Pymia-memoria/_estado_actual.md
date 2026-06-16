# PymIA Memoria — Estado actual

Fecha: 2026-06-16

## Estado operativo actual

Repo principal:

```text
E:\BuenosPasos\smartbridge\PymIA
```

Subcarpeta viva:

```text
PymIA-Live
```

GitHub:

```text
smartdash-almasana/PymIA
```

HEAD validado por MCP:

```text
f179267 refactor(pymia-live): make owner markdown renderer decision-free
```

Worktree validado por MCP:

```text
limpio
```

Tests reportados al cierre:

```text
243/243 PASS
```

---

## Commits recientes relevantes

```text
f179267 refactor(pymia-live): make owner markdown renderer decision-free
e23286b docs(pymia-memoria): close pipeline trace identity realignment
faf9008 refactor(pymia-live): realign pipeline trace identity
f33bf00 docs(pymia-memoria): close vertical pipeline application boundary
80c6c9a refactor(pymia-live): introduce vertical pipeline application boundary
5bdc864 refactor(pymia-live): extract owner markdown renderer from CLI
6a01eb3 refactor(pymia-live): extract diagnostic operator adapter from CLI
3816fb0 refactor(pymia-live): extract question resolution from CLI
```

---

## Estado arquitectónico vigente

```text
PymIA-Live ya no concentra el caso de uso completo en vertical_slice.py.
vertical_slice.py quedó reducido a adaptador CLI con imports de compatibilidad temporal.
La frontera de aplicación vive en pymia/application/vertical_pipeline.py.
La identidad de trazabilidad ya fue realineada al pipeline de aplicación.
El renderer markdown ya no decide QAG ni reconstruye owner_simple.
```

Responsabilidades vigentes:

```text
owner_simple                -> pymia/smartpyme/owner_output.py
registration                -> pymia/smartpyme/pipeline_registration.py
question resolution         -> pymia/smartpyme/question_resolution.py
diagnostic operator adapter -> pymia/smartpyme/diagnostic_operator_adapter.py
owner markdown renderer     -> pymia/rendering/owner_markdown_renderer.py
vertical pipeline           -> pymia/application/vertical_pipeline.py
```

Frontera presentation/application vigente:

```text
pymia/application/vertical_pipeline.py pre-resuelve:
- report["owner_question"]
- report["owner_question_technical_reference"]
- report["owner_simple"]
- report["evidence_request_alignment"]

pymia/rendering/owner_markdown_renderer.py sólo renderiza esos datos.
No importa owner_output, question_alignment_gate ni question_resolution.
```

Identidad de traza vigente:

```text
pipeline_name   -> vertical_pipeline_evidence_spine
pipeline_module -> pymia.application.vertical_pipeline
entrypoint      -> build_pipeline
service_name    -> vertical_pipeline
channel         -> cli
registered_by   -> vertical_pipeline
```

Estado del CLI:

```text
PymIA-Live/pymia/cli/vertical_slice.py conserva main(), argparse, validación local de path, construcción de business_taxonomy, llamada al pipeline y escritura local de markdown.
```

Estado de compatibilidad temporal:

```text
vertical_slice.py re-expone imports desde pymia.application.vertical_pipeline para no romper tests y consumidores internos históricos.
No conserva los cuerpos de build_report, build_markdown, build_pipeline, build_structured_summary, inspect_excel ni has_operational_columns.
```

---

## Resultado arquitectónico rector

```text
El conocimiento de dominio es enchufable.
El kernel permanece estable.

JSON/contratos gobiernan conocimiento declarativo.
Python runtime carga, valida, calcula, orquesta, renderiza y falla cerrado.
```

La arquitectura objetivo vigente está documentada en:

```text
PymIA-Live/docs/pymia/PYMIA_LIVE_TARGET_ARCHITECTURE_V1.md
```

---

## Estado de contratos y conocimiento declarativo

```text
formula_rules_v1.json gobierna reglas declarativas de fórmulas.
presentation_labels_v1.json gobierna labels owner-facing.
question_alignment_v1.json gobierna QAG.
pathology_rules_v1.json gobierna reglas de patologías.
evidence_requirement_aliases_v1.json gobierna aliases de evidence requirements.
formula_aliases_v1.json gobierna aliases de evidencia hacia fórmulas.
evidence_requirement_copy_v1.json gobierna el template owner-facing mínimo del matcher.
owner_facing_report_copy_v1.json gobierna warnings owner-facing por status operativo.
vertical_slice_copy_v1.json gobierna copy mínimo, fallback owner-facing y copy local vigente.
language_corpus_seed.json gobierna labels declarativos del corpus dueño-variable.
pipeline_run_v1.py gobierna la identidad de ejecución del pipeline vertical.
```

---

## Frentes cerrados en esta secuencia

```text
OWNER_SIMPLE_BUILDER_EXTRACTION_V1 = CLOSED
PIPELINE_REGISTRATION_SERVICE_EXTRACTION_V1 = CLOSED
PYMIA_LIVE_TARGET_ARCHITECTURE_V1 = CLOSED
QUESTION_RESOLUTION_SERVICE_EXTRACTION_V1 = CLOSED
DIAGNOSTIC_OPERATOR_ADAPTER_EXTRACTION_V1 = CLOSED
OWNER_MARKDOWN_RENDERER_EXTRACTION_V1 = CLOSED
VERTICAL_PIPELINE_APPLICATION_BOUNDARY_V1 = CLOSED
PYMIA_LIVE_APPLICATION_BOUNDARY_CLOSEOUT = CLOSED
PIPELINE_RUN_TRACE_IDENTITY_REALIGNMENT_V1 = CLOSED
PIPELINE_RUN_TRACE_IDENTITY_CLOSEOUT = CLOSED
OWNER_MARKDOWN_RENDERER_DECISION_FREE_V1 = CLOSED
```

---

## Deuda viva conocida

```text
vertical_slice.py conserva imports de compatibilidad temporal.
build_structured_summary vive dentro de application/vertical_pipeline.py; puede extraerse luego si existe deuda material.
Language corpus sigue limitado; puede producir snake_case owner-facing si faltan labels.
Runbook/checklist operativo debe actualizar flags y protocolo de piloto.
No crear owner_output_v1 hasta señal material.
No abrir canales nuevos sin autorización explícita.
```

Deuda cerrada:

```text
La traza ya no declara al CLI como dueño del caso de uso.
La identidad de pipeline apunta a pymia.application.vertical_pipeline.
El canal CLI queda preservado como metadata channel=cli.
El renderer markdown ya no decide QAG.
El renderer markdown ya no reconstruye owner_simple.
El renderer markdown ya no importa servicios de dominio smartpyme.
```

---

## Próximo foco recomendado

```text
No abrir runtime inmediatamente.
Avanzar hacia PILOT_OPERATOR_CHECKLIST_V1 o auditar capacidad operativa concreta antes de proponer otro slice.
```

Categoría del foco actual:

```text
D. DOCUMENTACIÓN / MEMORIA
```

---

## Regla de avance

```text
No abrir features nuevas por inercia.
No volver a micro-slices cosméticos.
No crear contratos nuevos sin necesidad funcional clara.
No mezclar memoria, docs y runtime en un mismo commit.
El próximo frente debe clasificarse explícitamente como A, B, D, E o F según ARCHITECTURE MEMORY GATE.
```
