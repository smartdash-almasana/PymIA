# 05 — Plan de limpieza del repo

## Objetivo

Reducir ruido, eliminar Hermes, estabilizar el núcleo vivo y preparar el primer caso real asistido.

## Principios

1. No borrar sin manifest.
2. No mover sin criterio de autoridad.
3. No agregar documentos salvo necesidad operativa.
4. No conservar Hermes como dependencia activa.
5. No avanzar SaaS antes de caso real.
6. No arreglar todo a la vez: limpiar por PRs chicos.

## Fase 1 — Decisión documental inmediata

Crear/actualizar documento rector en `docs/current/`:

```text
HERMES_RETIREMENT_DECISION.md
```

Contenido mínimo:

- Hermes retirado totalmente.
- No es agente/runtime/orchestrator.
- `docs/hermes`, `tests/hermes`, `pymia/hermes`, `conversa-engine` no son arquitectura vigente.
- Intake/evidencia/conversación se expresan por contratos neutrales.

## Fase 2 — Limpieza de autoridad

Actualizar documentos que contradicen la decisión:

```text
README.md
ARCHITECTURE_GUARDRAILS.md
task.md
docs/current/ARCHITECTURE_BOUNDARY.md
docs/current/DOCS_MUSEUM_POLICY.md
```

Reemplazar “Hermes” por límites neutrales solo donde corresponda.

No hacer reemplazo ciego global.

## Fase 3 — Inventario Hermes

Generar inventario con categorías:

```text
A. borrar
B. mover a museo
C. migrar a contrato neutral
D. mantener temporalmente solo por compatibilidad
E. excluir de suite viva
```

Rutas candidatas:

```text
pymia/hermes/
tests/hermes/
docs/hermes/
docs/arquitectura/HERMES_*.md
conversa-engine/HERMES_*.md
scripts/*hermes*
```

## Fase 4 — Suite viva mínima

Definir una suite corta:

```text
tests_live/
```

o equivalente dentro de `PymIA-Live/tests/`, con solo:

- import smoke;
- CLI smoke;
- Excel mínimo;
- evidence record;
- owner-facing markdown;
- pipeline run manifest.

Criterio:

```text
Si esta suite no pasa, no se agregan features.
```

## Fase 5 — Corregir imports rotos

Prioridad inmediata:

```text
PymIA-Live/pymia/contracts/formula_rules_v1.py
PymIA-Live/pymia/smartpyme/diagnostic_operator_adapter.py
```

Resolver si `load_formula_rules` debe:

- existir en `formula_rules_v1.py`;
- importarse desde otro módulo;
- eliminarse si el adapter no corresponde al MVP.

## Fase 6 — Reducir `vertical_pipeline.py`

No refactorizar de forma cosmética. Extraer solo cuando haya test.

Orden sugerido:

1. Excel inspection.
2. Structured evidence summary.
3. Diagnostic adapter.
4. Owner-facing rendering.
5. Pipeline registration.
6. Question alignment.

Cada extracción debe incluir:

```text
contrato → test → módulo → evidencia de passing test
```

## Fase 7 — Definir MVP único

Crear un documento único:

```text
docs/current/SERVICE_1_ASSISTED_MVP_SCOPE.md
```

Debe decir:

- qué se entrega;
- qué no se entrega;
- inputs aceptados;
- outputs;
- rol del operador;
- criterio de éxito;
- criterio de no éxito;
- checklist de caso real;
- límites de catálogo activo.

## Fase 8 — Caso real supervisado

Antes de nuevas capas:

```text
1 caso real → ejecución → feedback → correcciones → decisión
```

El caso debe producir carpeta de evidencia:

```text
case_manifest.json
input_files/
structured_evidence.json
owner_summary.md
operator_review.md
run_log.jsonl
lessons_learned.md
```

## Fase 9 — Congelar SaaS/autonomía

Mover temporalmente a roadmap:

```text
docs/current/IMPLEMENTATION_ROADMAP_TO_AUTONOMOUS_SAAS_V1.md
docs/current/S1_SAAS_RUNTIME_BOUNDARY_CONTRACTS_V1.md
docs/current/SAAS_AUTONOMY_TARGET.md
```

No eliminarlos necesariamente, pero marcarlos como:

```text
POST-MVP / NO IMPLEMENTAR ANTES DE CASO REAL
```

## Fase 10 — Criterio de PR futuro

Todo PR debe declarar:

```text
- problema que resuelve;
- documento rector afectado;
- si toca Hermes o elimina Hermes;
- test vivo agregado/modificado;
- evidencia de ejecución;
- impacto en caso real asistido;
- riesgo de sobreingeniería.
```
