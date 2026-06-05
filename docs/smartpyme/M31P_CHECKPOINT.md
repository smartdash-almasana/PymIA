# M31-P — Checkpoint documental

## Estado

PASS_DOCUMENTAL

## Fecha

2026-06-05

## Contexto

M31 fue aclarado en dos niveles:

```text
M31_DOCUMENTAL = PASS_DOCUMENTAL
M31_OPERATIVO_PILOTOS = PENDING_PILOTS
```

Luego se abrió M31-P como fase de pilotos asistidos reales antes de cualquier consideración de M32.

M31-P no es feature técnica.
M31-P no es producto.
M31-P no autoriza código productivo.

## Documentos de la fase

- `docs/smartpyme/M31_CLOSURE_CLARIFICATION.md`
- `docs/smartpyme/M31P_PILOTOS_ASISTIDOS_PLAN.md`
- `docs/adr/ADR-M31P-PILOTOS-ASISTIDOS.md`
- `docs/smartpyme/M31P_CAPABILITY_SPEC.md`
- `docs/smartpyme/M31P_TASK_SPEC.md`
- `docs/smartpyme/M31P_PILOT_RECORD_TEMPLATE.md`
- `docs/smartpyme/M31P_PILOT_VALIDATION_CHECKLIST.md`

## Validación documental reportada

La validación documental externa/local reportó:

```text
VEREDICTO: PASS_DOCUMENTAL
```

Controles reportados como cumplidos:

1. Plan, CapabilitySpec, TaskSpec, plantilla y checklist usan el mismo contrato canónico.
2. El ADR no define contrato alternativo y mantiene límites metodológicos.
3. Variantes incompatibles aparecen sólo como nombres prohibidos, no campos activos:
   - `status`
   - `evidence_received`
   - `evidence_missing`
   - `business_context`
4. `execution_time_minutes` medido es obligatorio para PASS_OPERATIVO.
5. `operational_cost` existe y es obligatorio.
6. `candidate_learnings` debe existir, pero puede estar vacío sin volver PARTIAL.
7. No se habilita M32.
8. No se toca código productivo.
9. No se implementa Guided Evidence Recovery.

## Contrato canónico de piloto

```yaml
pilot_id:
tenant_ref:
case_date:
business_type:
case_origin:
owner_problem_statement:
owner_operational_meaning:
received_evidence:
missing_evidence:
protocol_steps_applied:
output_delivered:
final_status:
execution_time_minutes:
operational_cost:
human_intervention:
operator_notes:
blockers:
candidate_learnings:
repeatability_assessment:
limitations:
```

## Certificado por este checkpoint

Este checkpoint certifica:

- existe fase M31-P definida;
- existe ADR aceptado;
- existe CapabilitySpec alineada;
- existe TaskSpec alineada;
- existe plantilla de registro de piloto;
- existe checklist de validación;
- existe contrato canónico único;
- M31-P está documentalmente listo para comenzar pilotos;
- no se abrió M32;
- no se tocó código productivo;
- no se declaró producto;
- no se implementó Guided Evidence Recovery.

## No certificado por este checkpoint

Este checkpoint no certifica:

- ejecución de pilotos;
- 3 a 5 casos reales o realistas completos;
- tiempos reales medidos;
- costos operativos medidos;
- bloqueos reales observados;
- salidas reales entregadas;
- evaluación agregada de repetibilidad;
- PASS_OPERATIVO;
- producto mínimo;
- servicio comercial validado;
- autonomía end-to-end;
- LearningMemory aprobada.

## Estado operativo pendiente

```text
M31-P_OPERATIVO = PENDING_PILOTS
```

Para cerrar M31-P como PASS_OPERATIVO hacen falta:

- 3 a 5 registros de piloto completos;
- checklist aplicado por piloto;
- `execution_time_minutes` medido en todos los pilotos que cuenten para PASS;
- `operational_cost` registrado con valor o `not_applicable`;
- salidas o bloqueos documentados;
- evaluación de repetibilidad por piloto;
- evaluación agregada de repetibilidad;
- checkpoint operativo M31-P.

## Riesgos vigentes

- Confundir PASS_DOCUMENTAL con PASS_OPERATIVO.
- Ejecutar pilotos sin medir tiempo.
- Registrar evidencia incompleta y aun así declarar repetibilidad.
- Convertir aprendizajes candidatos en política o LearningMemory automática.
- Abrir M32 antes de completar M31-P operativo.
- Llamar producto a una fase todavía asistida y piloto.

## Próximo paso metodológico

Ejecutar o documentar 3 a 5 pilotos usando:

```text
docs/smartpyme/M31P_PILOT_RECORD_TEMPLATE.md
docs/smartpyme/M31P_PILOT_VALIDATION_CHECKLIST.md
```

Cada piloto debe producir un registro completo bajo el contrato canónico.

## Regla final

M31-P queda habilitado para pilotos asistidos.

M31-P no habilita M32.
M31-P no habilita producto.
M31-P no habilita código productivo.
M31-P no habilita Guided Evidence Recovery.
