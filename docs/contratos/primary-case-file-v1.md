# PrimaryCaseFile V1 — Contrato mínimo

## Estado

```text
DRAFT_CONTRACT
MINIMAL_CONTRACT
PURE_CONTRACT
NO_RUNTIME_AUTHORIZATION
NO_PYMIA_LIVE_CHANGE
NO_VERTICAL_SLICE_CHANGE
NO_FORMULA_ENGINE_CHANGE
NO_EVIDENCE_EXTRACTION_CHANGE
```

## Propósito

`PrimaryCaseFile V1` define el artefacto mínimo que ata un caso existente a un expediente primario gobernable.

No diagnostica.

No crea `case_id`.

No adjunta evidencia.

No ejecuta fórmulas.

No renderiza salida owner-facing.

## Principio

```text
PrimaryCaseFile funda el expediente mínimo del caso.
No abre el lifecycle completo del caso.
```

## Alcance V1

El contrato V1 sólo cubre:

```text
identidad mínima del expediente
binding tenant/case/operator/owner/business
período de análisis
problema inicial
scope mínimo
autorización mínima
estado draft/sealed/superseded
referencias iniciales de evidencia por id
```

## Fuera de alcance

```text
update()
reopen()
attach_evidence()
case lifecycle completo
eventos
persistencia real
migraciones
FichaExtension
OwnerSemanticClaim
TensionReport
AssertionCandidate
OperatorConfirmation
EpistemicState
DominantUnknown
Pack Governance completo
```

## Modelo mínimo

```yaml
pcf_id: string
tenant_id: string
case_id: string
operator_id: string
owner_ref: string
business_ref: string

period:
  start: datetime
  end: datetime

problem_statement: string
scope: string

authorization:
  status: owner_consents | operator_assumes | pending

status: draft | sealed | superseded

initial_evidence_refs: list[string]

schema_version: "1.0"
created_at: datetime
sealed_at: optional[datetime]
superseded_by: optional[string]
```

## Regla sobre `case_id`

```text
PrimaryCaseFile NO crea case_id.
PrimaryCaseFile se ata a tenant_id + case_id existentes.
```

Motivo:

```text
crear case_id abriría lifecycle completo de caso,
y eso está fuera del corte mínimo.
```

## Operaciones permitidas

```text
seal()
is_sealed()
supersede(new_pcf_id)
```

## Operaciones prohibidas

```text
update()
reopen()
attach_evidence()
save()
load()
delete()
dispatch_event()
render()
diagnose()
evaluate()
```

## Invariantes

```text
no se puede seal() si status != draft
no se puede construir sin tenant_id
no se puede construir sin case_id
no se puede construir sin operator_id
no se puede construir sin owner_ref
no se puede construir sin business_ref
no se puede construir sin period
no se puede construir sin problem_statement
no se puede construir sin scope
period.end >= period.start
scope.strip() no vacío
authorization pertenece al enum permitido
schema_version conocido
segundo seal() falla
sealed es inmutable
supersede() sólo permitido si status == sealed
roundtrip dict -> model -> dict preserva campos
```

## Semántica de estados

### draft

Estado editable inicial del contrato mínimo.

### sealed

Estado sellado. Los campos críticos quedan inmutables.

### superseded

Estado posterior a `supersede(new_pcf_id)`.

No borra ni muta silenciosamente el expediente previo.

## Frontera técnica

Implementación autorizada:

```text
pymia/contracts/primary_case_file_v1.py
tests/contracts/test_primary_case_file_v1.py
docs/contratos/primary-case-file-v1.md
```

Archivos no autorizados:

```text
PymIA-Live/**
pymia/cli/vertical_slice.py
pymia/services/formula_engine_service.py
pymia/diagnostic_core/**
pymia/smartpyme/structured_evidence_builder.py
pymia/smartpyme/question_alignment_gate.py
pymia/smartpyme/question_resolution.py
pymia/smartpyme/storage.py
pymia/contracts/evidence_v1.py
pymia/contracts/pipeline_run_v1.py
```

## Criterio DONE

```text
contrato Python creado
tests contractuales creados
documento de contrato creado
sin dependencias externas nuevas
sin runtime
sin PymIA-Live
sin motor
sin sufficiency
sin extraction
sin owner-facing output
```

## Frase rectora

```text
Primero fundamos el expediente mínimo.
Después, en otro corte, se decide si se conecta al pipeline.
```
