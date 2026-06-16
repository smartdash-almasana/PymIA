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
80c6c9a refactor(pymia-live): introduce vertical pipeline application boundary
```

Worktree validado por MCP:

```text
limpio
```

Tests reportados al cierre:

```text
241/241 PASS
```

---

## Commits recientes relevantes

```text
80c6c9a refactor(pymia-live): introduce vertical pipeline application boundary
5bdc864 refactor(pymia-live): extract owner markdown renderer from CLI
6a01eb3 refactor(pymia-live): extract diagnostic operator adapter from CLI
3816fb0 refactor(pymia-live): extract question resolution from CLI
e1877e8 docs(pymia-live): define target multichannel architecture
5fb7947 refactor(pymia-live): extract pipeline registration from CLI
b426099 docs(pymia-memoria): close owner simple extraction
eca07e8 refactor(pymia-live): extract owner simple output builder
```

---

## Estado arquitectónico vigente

```text
PymIA-Live ya no concentra el caso de uso completo en vertical_slice.py.
vertical_slice.py quedó reducido a adaptador CLI con imports de compatibilidad temporal.
La frontera de aplicación vive en pymia/application/vertical_pipeline.py.
```

Responsabilidades extraídas de `vertical_slice.py`:

```text
owner_simple                -> pymia/smartpyme/owner_output.py
registration                -> pymia/smartpyme/pipeline_registration.py
question resolution         -> pymia/smartpyme/question_resolution.py
diagnostic operator adapter -> pymia/smartpyme/diagnostic_operator_adapter.py
owner markdown renderer     -> pymia/rendering/owner_markdown_renderer.py
vertical pipeline           -> pymia/application/vertical_pipeline.py
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
```

---

## Deuda viva conocida

```text
Renderer markdown todavía decide QAG y recompone owner_simple como deuda preexistente aceptada.
vertical_slice.py conserva imports de compatibilidad temporal.
build_structured_summary vive dentro de application/vertical_pipeline.py; puede extraerse luego si existe deuda material.
Memoria/documentación debe mantenerse alineada después de cambios mayores.
No crear owner_output_v1 hasta señal material.
No abrir canales nuevos sin autorización explícita.
```

---

## Próximo foco recomendado

```text
No abrir runtime inmediatamente.
Cerrar este checkpoint documental y luego auditar deuda viva real antes de proponer nuevo slice.
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
