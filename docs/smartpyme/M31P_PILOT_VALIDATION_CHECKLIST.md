# M31-P — Checklist de validación de pilotos asistidos

## Estado

CHECKLIST

## Propósito

Validar que cada piloto M31-P esté suficientemente registrado para evaluar repetibilidad operativa asistida.

Este checklist no certifica producto, autonomía ni capacidad comercial validada.

## Uso

Aplicar este checklist a cada registro creado con:

```text
docs/smartpyme/M31P_PILOT_RECORD_TEMPLATE.md
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
- [ ] La salida no se presenta como producto final.

### 7. Tiempo e intervención humana

- [ ] `execution_time_minutes` está registrado.
- [ ] Si no se midió tiempo, hay justificación explícita.
- [ ] `human_intervention` está registrada si existió.
- [ ] La intervención humana no se oculta bajo falsa autonomía.

### 8. Bloqueos

- [ ] `blockers` está registrado, aunque sea lista vacía.
- [ ] Los bloqueos distinguen falta de evidencia, falta de sentido operativo, restricción técnica o restricción metodológica.
- [ ] Si el caso está BLOCKED, el bloqueo es trazable.

### 9. Aprendizajes candidatos

- [ ] `candidate_learnings` está registrado si corresponde.
- [ ] Los aprendizajes están marcados como candidatos.
- [ ] No se convirtieron automáticamente en LearningMemory.
- [ ] No se convirtieron automáticamente en ADR, política o arquitectura.

### 10. Repetibilidad

- [ ] `repeatability_assessment` usa sólo valores permitidos:
  - REPEATABLE
  - PARTIALLY_REPEATABLE
  - NOT_REPEATABLE
  - NOT_ENOUGH_EVIDENCE
- [ ] La evaluación está justificada por evidencia del piloto.
- [ ] No se generaliza a producto con un solo caso.

### 11. Limitaciones

- [ ] `limitations` está registrado.
- [ ] Las limitaciones distinguen evidencia, alcance, tiempo, intervención humana y aplicabilidad.
- [ ] No se ocultan supuestos.

## Checklist de fase M31-P

Para evaluar la fase completa:

- [ ] Hay al menos 3 pilotos completos.
- [ ] No hay más de 5 pilotos en el primer cierre M31-P, salvo decisión explícita.
- [ ] Cada piloto tiene registro completo.
- [ ] Cada piloto tiene checklist aplicado.
- [ ] Hay tiempos reales o justificación de ausencia.
- [ ] Hay bloqueos registrados.
- [ ] Hay salidas o estados de bloqueo documentados.
- [ ] Hay evaluación de repetibilidad por piloto.
- [ ] Hay evaluación agregada de repetibilidad.
- [ ] Hay checkpoint M31-P.

## Criterio PASS_OPERATIVO

M31-P puede cerrar como PASS_OPERATIVO sólo si:

- [ ] existen 3 a 5 pilotos;
- [ ] todos tienen registro completo;
- [ ] todos tienen checklist aplicado;
- [ ] se registraron tiempos reales o justificaciones;
- [ ] se registraron bloqueos;
- [ ] se documentaron salidas o razones de bloqueo;
- [ ] se evaluó repetibilidad;
- [ ] se redactó checkpoint M31-P;
- [ ] no se tocó código productivo;
- [ ] no se abrió M32;
- [ ] no se declaró producto.

## Criterio PARTIAL

M31-P debe cerrar como PARTIAL si:

- [ ] hay 1 o 2 pilotos solamente;
- [ ] existen registros incompletos;
- [ ] falta medición de tiempo sin justificación;
- [ ] falta evaluación de repetibilidad;
- [ ] hay evidencia parcial;
- [ ] el protocolo funcionó sólo parcialmente.

## Criterio BLOCKED

M31-P debe cerrar como BLOCKED si:

- [ ] no hay pilotos disponibles;
- [ ] no hay evidencia suficiente;
- [ ] el protocolo M31 no puede aplicarse sin nueva implementación;
- [ ] se intenta implementar Guided Evidence Recovery;
- [ ] se intenta abrir M32;
- [ ] se intenta declarar producto sin evidencia.

## Regla final

El checklist valida repetibilidad operativa asistida.

No valida producto.
No valida autonomía.
No valida mercado.
No valida escalabilidad técnica.
No valida LearningMemory.
