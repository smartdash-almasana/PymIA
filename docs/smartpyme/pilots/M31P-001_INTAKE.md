# M31P-001 — Intake de piloto asistido

## Estado

INTAKE_PENDING

## Propósito

Preparar el primer piloto M31-P sin inventar evidencia ni declarar ejecución.

Este archivo no cuenta como registro completo de piloto.

Este archivo no cuenta para PASS_OPERATIVO.

## Relación contractual

Cuando el caso tenga datos suficientes, este intake deberá convertirse o derivar en un registro completo usando:

- `docs/smartpyme/M31P_PILOT_RECORD_TEMPLATE.md`
- `docs/smartpyme/M31P_PILOT_VALIDATION_CHECKLIST.md`

## Datos mínimos a completar

```yaml
pilot_id: M31P-001
tenant_ref:
case_date:
business_type:
case_origin:
owner_problem_statement:
owner_operational_meaning:
received_evidence:
  -
missing_evidence:
  -
protocol_steps_applied:
  - intake
output_delivered:
final_status:
execution_time_minutes:
operational_cost:
human_intervention:
operator_notes:
blockers:
  -
candidate_learnings:
  -
repeatability_assessment:
limitations:
  - intake pendiente; no cuenta para PASS_OPERATIVO
```

## Preguntas de intake

### 1. Problema declarado

¿Qué dijo el dueño PyME que quiere entender o resolver?

### 2. Evidencia recibida

¿Qué archivos, datos o documentos existen ya?

### 3. Evidencia faltante

¿Qué falta para aplicar el protocolo M31 sin inventar diagnóstico?

### 4. Sentido operativo

¿Qué aclaración del dueño hace falta?

Ejemplos:

- período a analizar;
- significado de columnas;
- proceso real detrás del archivo;
- decisión que necesita tomar;
- dato que existe pero está en otra fuente.

### 5. Medición

¿Cómo se medirá `execution_time_minutes`?

### 6. Costo operativo

¿Corresponde medir costo operativo o usar `not_applicable`?

### 7. Salida o bloqueo

¿El piloto aspira a entregar salida asistida o documentar bloqueo por evidencia insuficiente?

## Restricciones

- No declarar DELIVERED sin evidencia.
- No completar `execution_time_minutes` si no fue medido.
- No completar `operational_cost` sin criterio.
- No registrar aprendizaje como LearningMemory.
- No usar este intake como PASS_OPERATIVO.
- No abrir M32.
- No tocar código productivo.

## Próximo paso

Completar el intake con datos reales o realistas y luego crear el registro completo `M31P-001.md` si corresponde.
