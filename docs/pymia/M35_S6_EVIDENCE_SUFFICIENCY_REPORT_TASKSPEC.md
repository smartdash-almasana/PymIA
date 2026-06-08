# M35-S6 — Evidence Sufficiency Report TaskSpec

Fecha: 2026-06-08
Frente activo: `M35_EVIDENCE_TO_CORE_BINDING`
Slice: `M35-S6_EVIDENCE_SUFFICIENCY_REPORT`

## Objetivo

Diseñar el próximo slice para producir un reporte determinístico de suficiencia de evidencia por fórmula.

El reporte debe servir como artefacto previo al cálculo, sin ejecutar diagnóstico y sin confirmar patologías.

## Alcance

Entrada esperada:

```text
StructuredEvidence / computed_variables
-> evidence_binding
-> fórmula objetivo
-> reporte de suficiencia
```

Salida esperada por fórmula:

```text
- formula_id
- required_variables
- available_variables
- missing_variables
- source_refs
- status: READY | MISSING_INPUTS
```

## Reglas

1. No ejecutar diagnóstico.
2. No confirmar patologías.
3. No calcular findings narrativos.
4. No inventar variables faltantes.
5. Preservar `source_refs` cuando existan.
6. El reporte debe ser determinístico y serializable.
7. El estado sólo puede ser:
   - `READY`
   - `MISSING_INPUTS`

## Semántica mínima

### `formula_id`

Identificador exacto de la fórmula evaluada.

### `required_variables`

Lista de variables requeridas por contrato para esa fórmula.

### `available_variables`

Lista de variables efectivamente disponibles tras aplicar el binding.

### `missing_variables`

Variables requeridas que no están disponibles.

### `source_refs`

Referencias de evidencia asociadas a las variables disponibles para esa fórmula.

### `status`

- `READY`:
  todas las variables requeridas están disponibles.
- `MISSING_INPUTS`:
  falta una o más variables requeridas.

## Resultado esperado del slice

El próximo slice debería permitir responder, por fórmula y antes del core:

```text
¿Hay evidencia suficiente para intentar el cálculo?
¿Qué variables faltan?
¿Qué evidencia concreta ya sostiene lo disponible?
```

## No objetivo

Queda fuera de este slice:

```text
- ejecutar FormulaEngineService
- ejecutar DiagnosticCoreV1
- confirmar patologías
- producir findings
- narrativa conversacional
```

## Entregable esperado para el próximo slice

Un contrato o helper puro que produzca un reporte por fórmula, apto para:

```text
- auditoría técnica
- gating previo a cálculo
- debugging de binding
- trazabilidad de evidencia disponible/faltante
```
