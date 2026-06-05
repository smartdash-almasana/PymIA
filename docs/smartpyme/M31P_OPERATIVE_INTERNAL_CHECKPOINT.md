# M31-P — Checkpoint operativo interno realista

## Estado

PASS_OPERATIVO_INTERNO_REALISTA

## Fecha

2026-06-05

## Alcance

Este checkpoint certifica una validación operativa limitada a pilotos internos realistas basados en fixtures del repositorio.

No certifica clientes reales.

No certifica producto.

No habilita M32 automáticamente.

No autoriza código productivo.

## Antecedentes

M31-P fue creado para resolver la diferencia entre:

```text
M31_DOCUMENTAL = PASS_DOCUMENTAL
M31_OPERATIVO_PILOTOS = PENDING_PILOTS
```

Luego se definieron:

- plan M31-P;
- ADR M31-P;
- CapabilitySpec;
- TaskSpec;
- plantilla de piloto;
- checklist;
- registro maestro;
- criterio de selección;
- runbook operativo.

## Pilotos considerados

| Pilot ID | Estado | Cuenta | Naturaleza |
|---|---|---:|---|
| M31P-001 | BLOCKED | No | Intento bloqueado por falta de caso/evidencia mínima |
| M31P-002 | COMPUTABLE_INTERNAL_REALISTIC_CASE | Sí | Fixture textil `la_textil_cosida_srl_mar_abr_may_2026.xlsx` |
| M31P-003 | COMPUTABLE_INTERNAL_REALISTIC_CASE | Sí | Fixture `pyme_textil_compleja.xlsx` |
| M31P-004 | COMPUTABLE_INTERNAL_REALISTIC_CASE | Sí | Fixture `simple_bem_test.xlsx` |

## Evidencia registrada

### M31P-002

Archivo:

```text
docs/smartpyme/pilots/M31P-002.md
```

Evidencia local reportada por usuario:

```text
python -m pytest tests/test_excel_evidence.py tests/test_document_ingestion.py -q
12 passed in 29.41s
```

Veredicto del piloto:

```text
COMPUTABLE_INTERNAL_REALISTIC_CASE
counts_for_pass_operativo = true
```

### M31P-003

Archivo:

```text
docs/smartpyme/pilots/M31P-003.md
```

Usa la misma ejecución local reportada que cubre los tests donde participa `pyme_textil_compleja.xlsx`.

Veredicto del piloto:

```text
COMPUTABLE_INTERNAL_REALISTIC_CASE
counts_for_pass_operativo = true
```

### M31P-004

Archivo:

```text
docs/smartpyme/pilots/M31P-004.md
```

Evidencia local reportada por usuario:

```text
FILE prueba_excels\simple_bem_test.xlsx
EXISTS True
STATUS PARTIAL
TABLES 1
ROWS 3
EVIDENCE_TABLES 1
COMPUTED_VARIABLES 2
```

Veredicto del piloto:

```text
COMPUTABLE_INTERNAL_REALISTIC_CASE
counts_for_pass_operativo = true
```

## Estado agregado

Según `docs/smartpyme/M31P_PILOTS_REGISTRY.md`:

```yaml
total_pilot_records_created: 4
total_data_requests_created: 1
total_pilots_complete: 3
total_pilots_internal_realistic_computable: 3
total_pilots_blocked_before_execution: 1
total_pilots_counting_for_pass_internal: 3
total_real_client_pilots: 0
m31p_operational_internal_status: READY_TO_EVALUATE
m31p_real_client_status: NOT_CERTIFIED
```

## Certificado

Este checkpoint certifica:

- existen 3 pilotos internos realistas computables;
- cada piloto tiene registro documental;
- cada piloto usa el contrato canónico M31-P;
- cada piloto tiene checklist aplicado;
- cada piloto registra evidencia recibida y faltante;
- cada piloto registra salida, estado final, intervención humana, blockers, candidate_learnings, repeatability_assessment y limitations;
- M31P-002 y M31P-003 tienen evidencia local reportada de tests `12 passed in 29.41s`;
- M31P-004 tiene evidencia local reportada de curación/evidencia estructurada mínima;
- no se abrió M32;
- no se declaró producto;
- no se tocó código productivo;
- no se implementó Guided Evidence Recovery;
- no se convirtió aprendizaje candidato en LearningMemory automática.

## No certificado

Este checkpoint no certifica:

- clientes reales;
- servicio comercial validado;
- producto mínimo;
- autonomía end-to-end;
- repetibilidad en entorno comercial;
- entrevista real con dueño PyME;
- costo operativo comercial real;
- CI exitoso para M31-P;
- que M32 pueda abrirse automáticamente;
- LearningMemory aprobada.

## Riesgos vigentes

- Confundir pilotos internos realistas con pilotos cliente reales.
- Confundir PASS_OPERATIVO_INTERNO_REALISTA con producto.
- Sobregeneralizar evidencia de fixtures.
- Abrir M32 sin ADR/CapabilitySpec/TaskSpec propio.
- Tratar candidate_learnings como memoria aprobada.
- No medir costo real en futuros casos comerciales.

## Veredicto

```text
M31-P_OPERATIVO_INTERNO_REALISTA = PASS
M31-P_CLIENTES_REALES = NOT_CERTIFIED
M32 = BLOCKED_UNTIL_EXPLICIT_DECISION
PRODUCTO = NOT_CERTIFIED
```

## Próximo paso metodológico

Antes de M32, decidir explícitamente una de estas rutas:

1. Ejecutar 3 a 5 pilotos con clientes reales o prospectos reales.
2. Crear ADR para habilitar una fase técnica posterior limitada, sin llamarla producto.
3. Mantener M31-P como fase interna validada y pasar a preparación comercial asistida con contrato propio.

Ninguna ruta es automática.
