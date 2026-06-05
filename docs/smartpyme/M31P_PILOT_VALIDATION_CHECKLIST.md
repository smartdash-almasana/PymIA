# M31-P — Checklist de validación de pilotos asistidos

## Estado

CHECKLIST_ALINEADO

## Propósito

Validar que cada piloto M31-P esté suficientemente registrado para evaluar repetibilidad operativa asistida bajo un contrato único de campos.

Este checklist no certifica producto, autonomía ni capacidad comercial validada.

## Uso

Aplicar este checklist a cada registro creado con:

```text
docs/smartpyme/M31P_PILOT_RECORD_TEMPLATE.md
```

## Contrato canónico esperado

Todo registro debe contener estos campos:

```text
pilot_id
tenant_ref
case_date
business_type
case_origin
owner_problem_statement
owner_operational_meaning
received_evidence
missing_evidence
protocol_steps_applied
output_delivered
final_status
execution_time_minutes
operational_cost
human_intervention
operator_notes
blockers
candidate_learnings
repeatability_assessment
limitations
```

No aceptar variantes incompatibles como:

```text
status
evidence_received
evidence_missing
business_context
```

## Checklist por piloto

### 1. Identificación

- [ ] `pilot_id` está presente.
- [ ] `tenant_ref` está presente o anonimizado.
- [ ] `case_date` está presente.
- [ ] `business_type` está presente o se justifica su ausencia.
- [ ] `case_origin` está presente o se justifica su ausencia.

### 2. Problema declarado

- [ ] `owner_problem_statement` está presente.
- [ ] El problema declarado preserva el sentido del dueño PyME.
- [ ] No se convirtió el dolor del dueño en diagnóstico sin evidencia.

### 3. Sentido operativo

- [ ] `owner_operational_meaning` está registrado si existió.
- [ ] Si no existió, la ausencia está clara.
- [ ] El sentido operativo está separado de la interpretación del operador.
- [ ] No se trató al dueño sólo como uploader de archivos.

### 4. Evidencia

- [ ] `received_evidence` está registrado.
- [ ] `missing_evidence` está registrado.
- [ ] La evidencia faltante es concreta.
- [ ] No se inventó evidencia.
- [ ] No se diagnosticó sin evidencia suficiente.

### 5. Aplicación del protocolo M31

- [ ] `protocol_steps_applied` está registrado.
- [ ] Se identifica qué partes del protocolo M31 fueron aplicadas.
- [ ] Se identifica qué partes no pudieron aplicarse, si corresponde.
- [ ] No se introdujo una capacidad nueva no contratada.

### 6. Salida o bloqueo

- [ ] `output_delivered` está registrado si hubo entrega.
- [ ] Si no hubo entrega, el bloqueo está documentado.
- [ ] `final_status` usa sólo valores permitidos:
  - DELIVERED
  - BLOCKED
  - PARTIAL
  - UNSUPPORTED
- [ ] No se usa el campo incompatible `status`.
- [ ] La salida no se presenta como producto final.

### 7. Tiempo real

- [ ] `execution_time_minutes` está registrado.
- [ ] `execution_time_minutes` contiene un número medido si el piloto aspira a contar para PASS_OPERATIVO.
- [ ] Si no se midió tiempo, la ausencia está explicada en `limitations` y el piloto no cuenta como completo para PASS_OPERATIVO.

### 8. Costo operativo

- [ ] `operational_cost` está registrado.
- [ ] `operational_cost` contiene monto, estimación explícita, `not_applicable` o `not_measured`.
- [ ] Si usa `not_measured`, está justificado en `limitations`.

### 9. Intervención humana y notas

- [ ] `human_intervention` está registrada si existió.
- [ ] `operator_notes` está registrado si corresponde.
- [ ] La intervención humana no se oculta bajo falsa autonomía.
- [ ] Las notas del operador no se confunden con evidencia del dueño.

### 10. Bloqueos

- [ ] `blockers` está registrado, aunque sea lista vacía.
- [ ] Los bloqueos distinguen falta de evidencia, falta de sentido operativo, restricción técnica o restricción metodológica.
- [ ] Si el caso está BLOCKED, el bloqueo es trazable.

### 11. Aprendizajes candidatos

- [ ] `candidate_learnings` está registrado, aunque sea lista vacía.
- [ ] Los aprendizajes, si existen, están marcados como candidatos.
- [ ] No se convirtieron automáticamente en LearningMemory.
- [ ] No se convirtieron automáticamente en ADR, política o arquitectura.

### 12. Repetibilidad

- [ ] `repeatability_assessment` usa sólo valores permitidos:
  - REPEATABLE
  - PARTIALLY_REPEATABLE
  - NOT_REPEATABLE
  - NOT_ENOUGH_EVIDENCE
- [ ] La evaluación está justificada por evidencia del piloto.
- [ ] No se generaliza a producto con un solo caso.

### 13. Limitaciones

- [ ] `limitations` está registrado.
- [ ] Las limitaciones distinguen evidencia, alcance, tiempo, costo, intervención humana y aplicabilidad.
- [ ] No se ocultan supuestos.

## Checklist de fase M31-P

Para evaluar la fase completa:

- [ ] Hay al menos 3 pilotos completos.
- [ ] No hay más de 5 pilotos en el primer cierre M31-P, salvo decisión explícita.
- [ ] Cada piloto tiene registro completo.
- [ ] Cada piloto tiene checklist aplicado.
- [ ] Todos los pilotos que cuentan para PASS_OPERATIVO tienen `execution_time_minutes` medido.
- [ ] Todos los pilotos tienen `operational_cost` registrado.
- [ ] Hay bloqueos registrados, aunque sean listas vacías.
- [ ] Hay salidas o estados de bloqueo documentados.
- [ ] Hay evaluación de repetibilidad por piloto.
- [ ] Hay evaluación agregada de repetibilidad.
- [ ] Hay checkpoint M31-P.

## Criterio PASS_OPERATIVO

M31-P puede cerrar como PASS_OPERATIVO sólo si:

- [ ] existen 3 a 5 pilotos;
- [ ] todos tienen registro completo;
- [ ] todos tienen checklist aplicado;
- [ ] todos tienen `execution_time_minutes` medido;
- [ ] todos tienen `operational_cost` registrado con valor o `not_applicable`;
- [ ] todos tienen `blockers` registrado;
- [ ] se documentaron salidas o razones de bloqueo;
- [ ] se evaluó repetibilidad por piloto y agregada;
- [ ] se redactó checkpoint M31-P;
- [ ] no se tocó código productivo;
- [ ] no se abrió M32;
- [ ] no se declaró producto.

## Criterio PARTIAL

M31-P debe cerrar como PARTIAL si:

- [ ] hay 1 o 2 pilotos solamente;
- [ ] existen registros incompletos;
- [ ] falta medición de tiempo;
- [ ] falta `operational_cost` o su justificación;
- [ ] falta evaluación de repetibilidad;
- [ ] hay evidencia parcial;
- [ ] el protocolo funcionó sólo parcialmente.

La ausencia de aprendizajes candidatos no implica PARTIAL si `candidate_learnings` existe y está explícitamente vacío.

## Criterio BLOCKED

M31-P debe cerrar como BLOCKED si:

- [ ] no hay pilotos disponibles;
- [ ] no hay evidencia suficiente;
- [ ] el protocolo M31 no puede aplicarse sin nueva implementación;
- [ ] se intenta implementar Guided Evidence Recovery;
- [ ] se intenta abrir M32;
- [ ] se intenta declarar producto sin evidencia;
- [ ] se intenta declarar PASS_OPERATIVO sin contrato de registro completo.

## Regla final

El checklist valida repetibilidad operativa asistida.

No valida producto.
No valida autonomía.
No valida mercado.
No valida escalabilidad técnica.
No valida LearningMemory.
