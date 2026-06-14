# PymIA Memoria — Decisiones vigentes

Fecha: 2026-06-12

## 2026-06-12 — ADR-024 Pack System Foundation aceptado

Decisión vigente:

```text
El conocimiento de dominio es enchufable.
El kernel permanece estable.
Kernel PymIA ≠ catálogos enchufables.
```

ADR rector:

```text
docs/adr/ADR-024-pack-system-foundation.md
```

Evidencia base:

```text
docs/pymia/SUPERAUDITORIA_INFORME_0.md
```

Consecuencia operativa:

```text
Fórmulas nuevas, patologías, rubros, síntomas sectoriales, benchmarks, tratamientos, taxonomías y variables organizacionales de dominio deben entrar como packs versionados.
No deben modificar el kernel, la anamnesis base ni diagnostic_core.
```

Tipos de pack reconocidos:

```text
DomainPack
KnowledgePack
FormulaPack
PathologyPack
SectorPack
CatalogPack
```

Próximo frente documental recomendado:

```text
PACK_BOUNDARY_CODE_RECONCILIATION
```

Este frente no autoriza migración de código, tests, runtime ni creación de packs ejecutables.

## 2026-06-13 — Language Corpus V1 aceptado como contrato mínimo

Decisión vigente:

```text
El Language Corpus gobierna traducción semántica owner-facing sin autoridad diagnóstica.
```

Estado:

```text
LC-1 documental PASS
LC-2 schema PASS
LC-2B guardrails PASS
LC-3 seed PASS
LC-4 auditoría externa PASS suficiente
LC-5 integración focal PASS validado por usuario
LC-6 evolution contract documental aplicado, pendiente auditoría/cierre
```

Evidencia LC-5 reportada por usuario:

```text
tests/contracts/test_language_corpus_v1.py: 14/14 PASS
tests/e2e/test_vertical_slice_cli.py: 20/20 PASS
```

LC-6 vigente:

```text
Define cómo evoluciona el Language Corpus sin contaminar kernel.
No activa Pack Runtime.
No amplía seed.
No toca código.
No integra owner_questions ni DiagnosticCore.
Preserva fail-closed.
```

Límites:

```text
No diagnostica.
No crea evidencia.
No convierte tags en findings.
No convierte relato del dueño en hecho.
No activa Pack Runtime.
No toca DiagnosticCore.
No amplía seed sin autorización.
```

Checkpoint:

```text
Pymia-memoria/CHECKPOINT_LANGUAGE_CORPUS_LC1_LC5_20260613.md
```

## Decisiones vigentes consolidadas

1. No comenzar de cero.
2. Repo local vigente: `E:\BuenosPasos\smartbridge\PymIA`.
3. GitHub vigente: `smartdash-almasana/PymIA`.
4. `Pymia-memoria/` es memoria local adicional y debe seguir fuera de git.
5. No usar VM.
6. No abrir Telegram salvo pedido explícito.
7. No abrir UI salvo pedido explícito.
8. No abrir producto salvo decisión explícita.
9. No abrir PDF salvo pedido explícito.
10. No abrir ERP ni Odoo como dirección de arquitectura salvo decisión explícita.
11. No usar Codex para auditorías largas ni discusión metodológica.
12. Codex sólo se usa para tocar código, ejecutar tests imprescindibles, reparar fallos concretos o confirmar cambio antes de commit.
13. No seguir sobredocumentando.
14. No tocar `evidence_gate` salvo decisión explícita.
15. No forzar `READY_FOR_ANALYSIS`.
16. No diagnosticar en primer contacto.
17. No calcular margen/caja/rentabilidad sin evidencia literal suficiente.
18. No interpretar documentos estructurados antes de contexto.
19. No convertir equivalencias dudosas en verdad.
20. No abrir arquitectura nueva por intuición conversacional.
21. No agregar `.tmp/`.
22. No abrir marketplace.
23. No volver a extender eventos externos por ahora.
24. No tocar Telegram, Hermes, conversa-engine, graph, runtime, DB, marketplace, LLM, ERP ni PDF.
25. No crear capas nuevas si no integran piezas existentes.

## Contrato metodológico obligatorio

PymIA debe avanzar por slices pequeños, locales, auditables y conectados al spine principal.

Orden obligatorio:

```text
Leer docs canónicos
→ verificar estado Git
→ identificar slice activo
→ tocar máximo 2–3 archivos
→ test focal
→ suite mínima relacionada
→ commit focal sin .tmp/
→ auditoría focal post-commit
```

Fuentes obligatorias de arranque:

```text
AGENTS.md
docs/pymia/START_HERE_FOR_AGENTS.md
docs/pymia/PYMIA_DEVELOPMENT_METHOD.md
docs/DOCUMENTATION_INDEX.md
Pymia-memoria/_estado_actual.md
Pymia-memoria/_task_actual.md
Pymia-memoria/_decisiones_vigentes.md
```

## Decisión arquitectónica operativa actual

La columna vertebral local inmediata es:

```text
IntakeRecord / intake_id
→ EvidenceRecord
→ StructuredEvidence
→ PipelineRunRecord
→ owner-facing markdown / futuro ResponseRecord
```

Roles vigentes:

```text
EvidenceRecord
= registro de evidencia recibida o referenciada.
= metadata, source_ref, tenant_id, intake_id, hash, status.

StructuredEvidence
= contenido estructurado/computable extraído de la evidencia.
= tablas, variables computadas, metadata.
= no diagnostica.

PipelineRunRecord
= registro de qué proceso se corrió con qué evidencia.
= run_id, evidence_ids, input_hash, output_hash, status, steps.

PymIAState
= estado conversacional, no memoria histórica.

PymIAEvent
= evento de graph/orquestación, no DomainEvent.

WebhookEvent / DomainEvent
= línea externa/transaccional futura.
= congelar por ahora.
```

## Decisiones del slice CLI vertical

### EVIDENCE_RECORD_BINDING_FOR_VERTICAL_CLI

Estado:

```text
CERRADO
```

Commit:

```text
5ef4f57 feat(pymia): bind vertical cli to evidence record storage
```

Decisión:

```text
El CLI vertical debe registrar EvidenceRecord real y persistirlo localmente antes de convertir a StructuredEvidence.
```

### PIPELINE_RUN_RECORD_MINIMAL_V1

Estado:

```text
CERRADO
```

Commit:

```text
4e63beb feat(pymia): add minimal pipeline run record for vertical cli
```

Decisión:

```text
El CLI vertical debe registrar PipelineRunRecord mínimo asociado a evidence_id, tenant_id, intake_id, input_hash, output_hash y status.
```

Cadena certificada por validación reportada:

```text
intake_id → evidence_id → run_id → output_hash
```

Validación reportada:

```text
13 passed in 11.42s
```

### INTEGRACION_QUESTION_ALIGNMENT_GATE_EN_MARKDOWNS_REALES

Estado:

```text
CERRADO
```

Commits:

```text
1327e10 feat(pymia-live): add isolated question alignment gate
740c63d feat(pymia-live): integrate question alignment gate into vertical slice owner message
7ac16a6 fix(pymia-live): include runtime catalog dependencies
c1afe56 fix(pymia-live): apply question alignment to rendered owner question
```

Decisión:

```text
El QuestionAlignmentGate gobierna la próxima pregunta en el markdown final real de PymIA-Live.
Para su correcto funcionamiento, la lista de conciliación debe ser filtrada a fórmulas con preguntas activas antes del gate.
Los catálogos JSON en docs/ son dependencias reales del runtime local y deben permanecer en PymIA-Live.
```

## Riesgos de deriva vigentes

### Deriva por más contratos

No responder a cada gap creando automáticamente:

```text
nuevo contrato
nuevo event type
nuevo mapper
nuevo replayer
nuevo adapter
nuevo CLI
```

Primero verificar pieza equivalente existente.

### Deriva por menú completo

No listar ni abrir superficies como:

```text
conversa-engine
Telegram
Hermes
llm_operator
sandbox smokes
tools genéricos
VM
```

### Deriva por eventos

Congelar por ahora:

```text
WebhookEvent
DomainEvent
ReplaySummary
event_replayer
marketplace_normalization
```

### Deriva conversacional

No confundir:

```text
PymIAState / PymIAEvent
```

con memoria operativa del negocio.

### Deriva de diagnóstico

No ejecutar diagnóstico final.

Estados sanos actuales:

```text
evidence sufficiency
owner-facing candidate report
BLOCKED / COMPLETED local
```

### Deriva por sobreauditoría

No bloquear cada microdecisión si hay un slice claro y pequeño.

Auditar después de validar.

## Política semántica vigente

- `fecha` / `mes` → `periodo` = high, cubre.
- `producto` → `producto` = high, cubre.
- `venta_total` → `venta_neta` = medium, pregunta al dueño, NO cubre.
- `costo_unitario` → `costo_directo` = medium, pregunta al dueño, NO cubre.
- `costo_total` → `costo_directo` = medium/low, pregunta o no cubre.
- `costos_fijos` → `costo_directo` = prohibido, no cubre.

## Criterio de producto

Una capacidad técnica no es producto.

Un flujo asistido no es producto.

Un CLI vertical local no es producto final.

Producto requiere, como mínimo:

- entrada definida;
- salida definida;
- repetibilidad;
- criterio de entrega;
- criterio de bloqueo;
- valor diferencial frente a IA manual + humano;
- evidencia comercial o validación de uso.

## Protocolo operativo

```text
Coder descubre.
Reviewer presiona.
ChatGPT ordena.
Codex implementa sólo si hay tarea concreta.
Pytest certifica.
CI vigila.
Humano decide.
```

## Frase rectora vigente

```text
PymIA no necesita más piezas flotantes.
Necesita que las piezas existentes formen una cadena trazable:
intake_id → evidence_id → run_id → output_hash.
```
