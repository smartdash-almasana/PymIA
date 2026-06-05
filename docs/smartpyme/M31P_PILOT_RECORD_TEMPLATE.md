# M31-P — Plantilla de registro de piloto asistido

## Estado

TEMPLATE_ALINEADO

## Propósito

Registrar cada piloto M31-P con suficiente evidencia para evaluar repetibilidad operativa asistida sin declarar producto ni autonomía.

Esta plantilla debe usarse para 3 a 5 pilotos reales o realistas antes de considerar cualquier apertura de M32.

## Reglas de uso

- Completar un registro por piloto.
- Usar exactamente el contrato canónico de campos.
- No inventar evidencia faltante.
- Registrar explícitamente bloqueos.
- Separar dato aportado por el dueño de interpretación del operador.
- Registrar sentido operativo aportado por el dueño cuando exista.
- Registrar costo operativo o `not_applicable`.
- Medir `execution_time_minutes` si se quiere aspirar a PASS_OPERATIVO.
- Registrar aprendizajes sólo como candidatos.
- No convertir candidatos en LearningMemory automática.
- No declarar PASS_OPERATIVO con menos de 3 pilotos completos.

## Contrato canónico de registro

```yaml
pilot_id:
  value:
  required: true
  description: Identificador único del piloto. Ejemplo M31P-001.

tenant_ref:
  value:
  required: true
  description: Identificador de tenant o referencia anonimizada.

case_date:
  value:
  required: true
  description: Fecha del caso en formato YYYY-MM-DD.

business_type:
  value:
  required: false
  description: Rubro o tipo de PyME, si se conoce.

case_origin:
  value:
  required: false
  description: Origen del caso. Ejemplo cliente real, demo realista, caso interno, caso prospectivo.

owner_problem_statement:
  value:
  required: true
  description: Texto o resumen fiel del dolor declarado por el dueño PyME.

owner_operational_meaning:
  value:
  required: false
  description: Sentido operativo aportado por el dueño. Qué período mirar, qué significa una columna, qué proceso real generó el dato, qué decisión necesita tomar.

received_evidence:
  value: []
  required: true
  description: Lista de evidencia recibida. Ejemplo Excel ventas abril, lista de costos, extracto banco.

missing_evidence:
  value: []
  required: true
  description: Lista de evidencia necesaria que no fue recibida.

protocol_steps_applied:
  value: []
  required: true
  description: Pasos del protocolo M31 efectivamente aplicados.

output_delivered:
  value:
  required: false
  description: Salida entregada. Ejemplo reporte mínimo, hallazgo, bloqueo documentado, pedido de evidencia.

final_status:
  value:
  required: true
  allowed_values:
    - DELIVERED
    - BLOCKED
    - PARTIAL
    - UNSUPPORTED
  description: Estado final del piloto.

execution_time_minutes:
  value:
  required: true
  description: Tiempo real medido de ejecución. Para PASS_OPERATIVO no puede ser null.

operational_cost:
  value:
  required: true
  allowed_values_note: Monto o estimación explícita, not_applicable o not_measured justificado en limitations.
  description: Costo operativo del piloto cuando corresponda.

human_intervention:
  value:
  required: false
  description: Intervención humana requerida. Ejemplo lectura de Excel, aclaración semántica, decisión de bloqueo.

operator_notes:
  value:
  required: false
  description: Notas del operador asistido, separadas de datos/evidencia del dueño.

blockers:
  value: []
  required: true
  description: Bloqueos encontrados durante el piloto. Lista vacía si no hubo bloqueos.

candidate_learnings:
  value: []
  required: true
  description: Aprendizajes candidatos. Lista vacía si no hubo aprendizajes. No son LearningMemory aprobada.

repeatability_assessment:
  value:
  required: true
  allowed_values:
    - REPEATABLE
    - PARTIALLY_REPEATABLE
    - NOT_REPEATABLE
    - NOT_ENOUGH_EVIDENCE
  description: Evaluación de repetibilidad del caso usando el protocolo M31.

limitations:
  value: []
  required: true
  description: Límites del caso, evidencia insuficiente, supuestos o razones por las que no puede generalizarse.
```

## Ejemplo vacío para copiar

```yaml
pilot_id: M31P-001
tenant_ref: tenant_anonymized_001
case_date: 2026-__-__
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
  - evidence_review
  - assisted_analysis
  - output_or_blocking_reason
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
  -
```

## Criterio de completitud por piloto

Un registro de piloto está completo si tiene:

- `pilot_id`;
- `tenant_ref`;
- `case_date`;
- `owner_problem_statement`;
- `received_evidence` o constancia explícita de ausencia;
- `missing_evidence` o lista vacía justificada;
- `protocol_steps_applied`;
- `final_status`;
- `execution_time_minutes`;
- `operational_cost`;
- `blockers`, aunque sea lista vacía;
- `candidate_learnings`, aunque sea lista vacía;
- `repeatability_assessment`;
- `limitations`.

## Regla de PASS_OPERATIVO por tiempo

Para que el piloto pueda integrar un cierre PASS_OPERATIVO de fase, `execution_time_minutes` debe tener un número medido.

Si no se midió el tiempo, el piloto puede documentarse, pero no cuenta como completo para PASS_OPERATIVO.

## Regla de costo operativo

`operational_cost` debe existir siempre.

Valores válidos:

- monto o estimación explícita;
- `not_applicable`;
- `not_measured`, sólo si se justifica en `limitations`.

## Estados finales

### DELIVERED

El caso produjo una salida asistida usando el protocolo M31.

### BLOCKED

El caso no pudo avanzar por falta de evidencia, falta de sentido operativo, restricción metodológica o imposibilidad de aplicar el protocolo.

### PARTIAL

El caso produjo una salida útil pero incompleta.

### UNSUPPORTED

El caso queda fuera del alcance de M31-P.

## Regla de evidencia

Si falta evidencia, registrar:

```yaml
final_status: BLOCKED
missing_evidence:
  - evidencia concreta faltante
blockers:
  - motivo del bloqueo
```

No reemplazar evidencia faltante con inferencia.

## Regla de aprendizaje

Todo aprendizaje debe quedar como:

```yaml
candidate_learnings:
  - aprendizaje candidato pendiente de revisión
```

Si no hay aprendizaje candidato:

```yaml
candidate_learnings: []
```

No usar este registro para modificar arquitectura, política, ADR o LearningMemory automáticamente.
