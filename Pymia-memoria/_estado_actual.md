# PymIA Memoria — Estado actual

Fecha: 2026-06-12

## 2026-06-12 — Pack System Foundation aceptado

Se aceptó documentalmente `docs/adr/ADR-024-pack-system-foundation.md`.

Evidencia base: `docs/pymia/SUPERAUDITORIA_INFORME_0.md`.

Estado actual:

```text
La frontera kernel / conocimiento enchufable quedó aceptada como decisión arquitectónica.
El Pack System todavía no está implementado en código.
No existen packs ejecutables todavía.
```

Regla vigente:

```text
El conocimiento de dominio es enchufable.
El kernel permanece estable.
```

Zonas a reconciliar en próximos frentes documentales:

```text
pymia/contracts/formula_contract.py
pymia/diagnostic_core/core.py
pymia/smartpyme/anamnesis_fsm.py
pymia/services/catalog_loader_v1.py
```

Próximo frente recomendado:

```text
PACK_BOUNDARY_CODE_RECONCILIATION
```

No autoriza tocar código, migrar fórmulas, crear packs ejecutables ni ejecutar tests.

## 2026-06-12 — Principio fundacional recuperado

Quedó fijado en memoria operativa que PymIA no debe iniciar el diagnóstico desde variables abstractas, fórmulas, indicadores o patologías.

La secuencia vigente para diagnóstico inicial es:

```text
Ficha → Anamnesis → Evidencia → Comprensión → Contraste → Diagnóstico inicial → Primer informe
```

Archivo de referencia:

```text
Pymia-memoria/PRINCIPIO_FUNDACIONAL_ANAMNESIS_ANTES_DE_VARIABLES_20260612.md
```

## 2026-06-12 — P1 auditado como candidato

Se creó checkpoint de auditoría P1:

```text
docs/pymia/P1_AUDIT_CHECKPOINT.md
```

Veredicto:

```text
PASS_WITH_OBSERVATIONS
```

P1 queda como frente documental candidato auditado. No habilita runtime, tests, Pydantic, OD1, C4, DecisionRecord, owner-action ni delivery.

Próximo frente recomendado:

```text
P1_EXTERNAL_AUDIT_REQUEST
```

## Estado general

Repo principal:

```text
E:\BuenosPasos\smartbridge\PymIA
```

GitHub:

```text
smartdash-almasana/PymIA
```

Branch esperado:

```text
main
```

Estado operativo local observado por GPT mediante MCP:

```text
git status --short = ?? .tmp/
```

Interpretación:

```text
El commit focal existe.
El working tree no está estrictamente limpio sólo por .tmp/.
.tmp/ no debe agregarse ni commitearse.
```

HEAD vigente observado:

```text
4e63beb feat(pymia): add minimal pipeline run record for vertical cli
```

## Cadena reciente cerrada — Vertical CLI spine local

La línea activa dejó de ser owner-answer M55-M64 para este ciclo.

El foco operativo actual es consolidar un spine local, trazable y pequeño del CLI vertical.

Secuencia cerrada reciente:

```text
f964447 feat(pymia): add first vertical cli slice
4289bcf feat(pymia): connect vertical cli slice to structured evidence
21bf0d8 feat(pymia): add evidence sufficiency to vertical cli slice
4338c42 fix(pymia): handle unsupported formulas in vertical cli slice
2d00796 fix(pymia): pass intake id as vertical cli case id
5102dd4 docs(pymia): define events v1 contract
d257f3a feat(pymia): add local event replayer slice
5ef4f57 feat(pymia): bind vertical cli to evidence record storage
4e63beb feat(pymia): add minimal pipeline run record for vertical cli
```

## Slice cerrado: EVIDENCE_RECORD_BINDING_FOR_VERTICAL_CLI

Commit:

```text
5ef4f57 feat(pymia): bind vertical cli to evidence record storage
```

Resultado:

```text
Excel
→ SHA-256
→ EvidenceRecord real
→ save_evidence_record
→ storage/<tenant>/evidences.jsonl
→ StructuredEvidence
→ evidence sufficiency
→ markdown owner-facing con Evidence ID y Evidence SHA-256
```

Validación reportada:

```text
11 passed in 16.37s
```

Archivos principales:

```text
pymia/cli/vertical_slice.py
tests/e2e/test_vertical_slice_evidence_binding.py
```

## Slice cerrado: PIPELINE_RUN_RECORD_MINIMAL_V1

Commit:

```text
4e63beb feat(pymia): add minimal pipeline run record for vertical cli
```

Resultado:

```text
Excel
→ SHA-256
→ EvidenceRecord
→ storage/<tenant>/evidences.jsonl
→ StructuredEvidence
→ evidence sufficiency
→ PipelineRunRecord
→ storage/<tenant>/pipeline_runs.jsonl
→ markdown con evidence_id + run_id
```

Cadena consolidada:

```text
intake_id
→ evidence_id
→ structured_evidence
→ sufficiency
→ run_id
→ output_hash
→ owner-facing markdown
```

Validación reportada por el usuario:

```text
13 passed in 11.42s — suite completa del CLI vertical
```

Archivos principales:

```text
pymia/contracts/pipeline_run_v1.py
pymia/cli/vertical_slice.py
tests/e2e/test_vertical_slice_pipeline_run_binding.py
```

## Qué certifica esta fase

Certifica localmente un spine mínimo del CLI vertical:

```text
intake_id → evidence_id → run_id → output_hash
```

Certifica que `PipelineRunRecord` funciona como registro mínimo de ejecución local asociado a evidencia.

Certifica que la salida owner-facing markdown puede exponer `Evidence ID`, `Evidence SHA-256` y `Run ID` sin diagnosticar de más.

## Qué NO certifica esta fase

No certifica:

```text
marketplace
eventos externos
WebhookEvent / DomainEvent como spine principal
Telegram
Hermes
conversa-engine
graph
runtime productivo
DB
ERP
PDF
LLM
Diagnóstico clínico-operacional definitivo
OwnerFacingReport productivo
ResponseRecord final
```

## Riesgo principal detectado

Riesgo:

```text
La IA tiende a resolver gaps creando nuevas piezas, nuevos contratos, nuevos eventos, nuevos CLIs y nuevas capas, en vez de integrar lo que ya existe.
```

Mitigación vigente:

```text
No abrir frentes nuevos.
No crear capas nuevas si no integran piezas existentes.
No volver a eventos externos por ahora.
No marketplace.
Consolidar el spine local antes de ampliar superficie.
```

## Regla operativa vigente para próximos chats

- No comenzar de cero.
- Leer `AGENTS.md`, `docs/pymia/START_HERE_FOR_AGENTS.md`, `docs/pymia/PYMIA_DEVELOPMENT_METHOD.md`, `docs/DOCUMENTATION_INDEX.md` y checkpoint/memoria relevante antes de proponer cambios.
- No tocar código sin autorización explícita.
- No push sin autorización explícita.
- No agregar `.tmp/`.
- No abrir Telegram, Hermes, conversa-engine, graph, runtime, DB, marketplace, LLM, ERP ni PDF.
- No crear contratos/eventos/adapters/replayers nuevos salvo necesidad focal probada.
- No ejecutar diagnóstico final: sólo evidence sufficiency / owner-facing candidate report / BLOCKED-COMPLETED local según corresponda.
- No confundir `PymIAState` / `PymIAEvent` con memoria histórica de negocio.

## Frase rectora

```text
PymIA no necesita más piezas flotantes.
Necesita que las piezas existentes formen una cadena trazable:
intake_id → evidence_id → run_id → output_hash.
```

## Próxima decisión recomendada

No avanzar a marketplace.

No volver a eventos externos.

No abrir Telegram/Hermes/runtime.

Próximo paso recomendado:

```text
Auditoría focal post-commit de 4e63beb.
```

Sólo si esa auditoría pasa, evaluar un siguiente slice mínimo:

```text
ResponseRecord mínimo u owner-facing output hash
```

Condición:

```text
Sólo si reduce ambigüedad real del spine local.
No abrir feature nueva por inercia.
```

## 2026-06-13 — PymIA-Live: baseline limpio validado

Se creó y validó exitosamente un repositorio limpio `PymIA-Live` desacoplando el núcleo operativo vivo del repositorio histórico.

### Evidencia de validación

Smoke real ejecutado con textil fixture:

```
Estado: DELIVERED_CANDIDATE
Evidence ID: evidence_156d05894db54e469183c256302c7f77
Run ID: run_5cf9a8e8543940178e2bd6350e47d40c
Output hash: 12f28193768f4e31ee657d611cd857ecdbb31a0f662a2463983639755e1b1dee
Markdown owner-facing generado en .tmp/live_smoke.md
5 variables detectadas (ventas brutas, costos CMV, margen bruto, margen %, cantidad total)
8 tablas estructuradas
Labels LC visibles: ventas brutas (ventas_total), costo de mercaderia vendida (costos_total)
Sin errores
```

### Commits relevantes

```
92a53e0  docs(pymia): define live core manifest
f4494a3  feat(pymia-live): initial validated extraction (47 archivos, +5759 líneas)
eb7ffe1  docs(pymia): add assisted pilot human reconduction rule
2f4fe81  docs(pymia): add assisted pilot 001 planning docs
```

### Documentos vivos

- `docs/pymia/PYMIA_LIVE_CORE_MANIFEST.md`
- `docs/pymia/PYMIA_LIVE_PIPELINE.md`
- `docs/ops/RUNBOOK_PILOTO_ASISTIDO_POST_LC.md`
- `PymIA-Live/docs/pymia/MIGRATION_REPORT.md`
- `PymIA-Live/README.md`
- `docs/ops/PILOTO_REAL_001_PLAN.md`
- `docs/ops/PILOTO_001_DATOS_SESION.md`

### Estado conceptual

Antes:

```
PymIA (histórico + vivo mezclado)
```

Ahora:

```
PymIA (histórico)
+
PymIA-Live (núcleo operativo)
```

### Gap principal cerrado: Priorización por mensaje del dueño (QuestionAlignmentGate)

El gap vivo del `owner_message` ha sido cerrado funcionalmente en `PymIA-Live` mediante la integración del `QuestionAlignmentGate` en el reporte final renderizado.

#### Funcionamiento corregido:
El sistema ahora filtra de forma correcta las conciliaciones de catálogo (`reconciliation`) a aquellas que tengan preguntas activas (`next_audit_questions`) antes de pasarlas por el gate de alineación. Esto evita que el alineador evalúe erróneamente fórmulas ya calculadas sin preguntas (como `LIQ_001`) y permite interceptar y desviar de forma efectiva la próxima pregunta técnica que realmente se iba a mostrar en el markdown (p. ej., reconduciendo de `INV_001_punto_reposicion` a caja/liquidez si el dueño declaró tensiones de caja).

#### Evidencia de validación:
- **Suite focal:** `35 passed` (incluyendo validación unitaria de gate y tests E2E del CLI con simulación de desalineación en el markdown final).
- **Smoke test real (con textil fixture):** **PASS**. El reporte generado reconduce correctamente al eje de caja/liquidez y no deriva directamente a la pregunta de stock.

### Commits relevantes:
- `1327e10` feat(pymia-live): add isolated question alignment gate
- `740c63d` feat(pymia-live): integrate question alignment gate into vertical slice owner message
- `7ac16a6` fix(pymia-live): include runtime catalog dependencies
- `c1afe56` fix(pymia-live): apply question alignment to rendered owner question

### Decisiones vigentes
- **No abrir features inmediatamente:** Se mantiene congelado el desarrollo de nuevas capacidades operativas.
- **Mantener PymIA-Live autónomo:** Los catálogos JSON se incluyeron en el repositorio local de forma que es 100% independiente del repositorio histórico.
- **No volver a convertir gaps claros en cadenas infinitas de specs/auditorías/checkpoints:** Una vez validados con tests y smoke, los cambios se cierran y se pasa al siguiente hito.

### Próximo frente probable
Ejecutar un piloto real owner-facing con otro Excel/caso y recolectar feedback de uso de la reconducción de preguntas, sin modificar código runtime ni estructurado.
