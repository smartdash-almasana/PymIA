# PRESENTATION_LABELS_V1_COVERAGE_TASKSPEC

## Estado

CLOSED_NO_CODE_CHANGE

## Objetivo

Cerrar el frente de labels visibles al dueño sin crear un contrato paralelo. Validar el contrato existente `presentation_labels_v1` en `PymIA-Live` y determinar si requiere extensión.

## Contexto certificado

En `PymIA-Live` ya existe el contrato:

- `pymia/contracts/presentation_labels_v1.py`
- `pymia/contracts/presentation_labels_v1.json`
- `tests/contracts/test_presentation_labels_v1.py`

El código ya consume ese contrato en:

- `pymia/application/vertical_pipeline.py`
- `pymia/smartpyme/question_resolution.py`
- `pymia/rendering/owner_markdown_renderer.py`

Búsqueda focal en `PymIA-Live` no detectó `_FIELD_LABELS` como deuda vigente. Por lo tanto, este TaskSpec no autoriza migrar hardcodes desde el repo raíz ni tocar archivos fuera de `PymIA-Live`.

## Alcance auditado

1. Auditar el contenido real de `presentation_labels_v1.json`.
2. Confirmar secciones actuales: `pathology_labels`, `field_labels`, `operational_terms`.
3. Evaluar si faltan secciones mínimas para presentación owner-facing: `missing_input_labels`, `owner_facing_states`, `block_labels`, `owner_questions`, `missing_states`.
4. Decidir si corresponde extender el contrato.

## Evidencia de auditoría

Secciones presentes en el JSON:

- `schema_version`
- `status`
- `pathology_labels`
- `field_labels`
- `operational_terms`

Funciones existentes:

- `load_presentation_labels`
- `label_for_pathology`
- `label_for_field`
- `load_operational_terms`

Tests existentes:

- carga válida del JSON;
- secciones obligatorias actuales;
- valores no vacíos;
- lookups conocidos;
- fallback ante desconocidos.

Consumidores reales:

- `vertical_pipeline.py`
- `question_resolution.py`
- `owner_markdown_renderer.py`

Los consumidores actuales usan labels de campos, labels de patologías y términos operativos. No consumen las secciones candidatas adicionales.

## Veredicto de cierre

ALREADY_COVERED

`presentation_labels_v1` cubre todo lo que `PymIA-Live` consume actualmente:

- `pathology_labels`
- `field_labels`
- `operational_terms`

No se agregan:

- `missing_input_labels`
- `owner_facing_states`
- `block_labels`
- `owner_questions`
- `missing_states`

Motivo: no existen consumidores actuales para esas secciones. Agregarlas ahora sería construcción especulativa y violaría la metodología del proyecto.

## Fuera de alcance

- No crear un contrato nuevo de labels owner-facing.
- No modificar DiagnosticCore.
- No modificar fórmulas.
- No modificar PrimaryCaseFile V1.
- No tocar repo raíz fuera de `PymIA-Live`.
- No abrir FunctionalGraphPack runtime.
- No modificar QuestionAlignmentGate.
- No modificar pipeline funcional.
- No crear UI.
- No usar LLM para traducción libre.
- No convertir labels en copywriting.
- No modificar `language_corpus_v1`.

## Archivos permitidos

- `docs/pymia/PRESENTATION_LABELS_V1_COVERAGE_TASKSPEC.md`

## Archivos no modificados

- `pymia/contracts/presentation_labels_v1.py`
- `pymia/contracts/presentation_labels_v1.json`
- `tests/contracts/test_presentation_labels_v1.py`
- código de runtime
- JSON contractual
- tests

## Estado final

CLOSED_NO_CODE_CHANGE

## Criterio PASS

PASS = cierre documental solamente + cero cambios de código + cero cambios en JSON + cero cambios en tests + cero contrato paralelo de labels + cero cambios fuera de `PymIA-Live`.
