# PRIMARY CASE FILE V1 MINIMAL CONTRACT TASKSPEC

## Estado

```text
DRAFT_TASKSPEC
DOCUMENTATION_ONLY
NO_CODE_IN_THIS_COMMIT
NO_RUNTIME_AUTHORIZATION
NO_PYMIA_LIVE_CHANGE
NO_VERTICAL_SLICE_CHANGE
NO_FORMULA_ENGINE_CHANGE
NO_EVIDENCE_EXTRACTION_CHANGE
```

## Fecha

```text
2026-06-17
```

## Objetivo

Autorizar, en un ciclo posterior y separado, la creación de un contrato puro, mínimo y aislado para `PrimaryCaseFile V1`.

Este TaskSpec no implementa código.

Este TaskSpec no crea runtime.

Este TaskSpec no modifica `PymIA-Live`.

## Decisión de frente

La auditoría externa del siguiente frente recomendó:

```text
VEREDICTO: PRIMARY_CASE_FILE
CONFIANZA: HIGH
```

Razón:

```text
PrimaryCaseFile mínimo funda el caso gobernable como contrato aislado, reduce deuda genética estructural y tiene precondición documental completa en inbox sin contaminar runtime.
```

## Fuentes autorizadas

```text
AGENTS.md
docs/DOCUMENTATION_INDEX.md
_docs_inbox/pymia_downloaded_md/RECONCILIATION_MATRIX.md
_docs_inbox/pymia_downloaded_md/PYMIA_PRIMARY_CASE_FILE_FIRST_SLICE_GLM52.md
_docs_inbox/pymia_downloaded_md/FICHAPRIMARIA_CONTRACT_V1.md
```

## Regla de reducción

La fuente principal para el corte mínimo es:

```text
_docs_inbox/pymia_downloaded_md/PYMIA_PRIMARY_CASE_FILE_FIRST_SLICE_GLM52.md
```

La fuente conceptual amplia es:

```text
_docs_inbox/pymia_downloaded_md/FICHAPRIMARIA_CONTRACT_V1.md
```

Pero `FICHAPRIMARIA_CONTRACT_V1.md` no debe copiarse entero ni implementarse completo.

Regla:

```text
PrimaryCaseFile debe nacer como hoja.
```

Esto significa:

```text
sin imports del kernel
sin imports de vertical_slice
sin dependencia de formula engine
sin dependencia de sufficiency
sin dependencia de rendering
sin dependencia externa nueva
sin lifecycle completo de caso
```

## Archivos futuros autorizados

En un ciclo posterior de implementación, sólo podrán crearse o modificarse estos archivos:

```text
pymia/contracts/primary_case_file_v1.py
tests/contracts/test_primary_case_file_v1.py
docs/contratos/primary-case-file-v1.md
```

## Archivos prohibidos

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
cualquier API
cualquier UI
cualquier dashboard
cualquier integración productiva
```

## Contrato mínimo futuro

El contrato futuro `PrimaryCaseFile V1` debe contener como máximo los siguientes campos mínimos:

```yaml
pcf_id: string
tenant_id: string
case_id: string
operator_id: string
owner_ref: string
business_ref: string

period:
  start: date
  end: date

problem_statement: string
scope: string

authorization:
  status: owner_consents | operator_assumes | pending

status: draft | sealed | superseded

initial_evidence_refs: list[string]

schema_version: string
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
si PrimaryCaseFile crea case_id ahora, se abre lifecycle de caso,
y eso queda fuera del primer corte mínimo.
```

## Operaciones futuras permitidas

```text
seal()
is_sealed()
supersede(new_pcf_id)
```

## Operaciones futuras prohibidas

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

## Invariantes de tests futuros

Los tests del ciclo posterior deberán validar como mínimo:

```text
no se puede seal() si status != draft
no se puede seal() sin tenant_id
no se puede seal() sin case_id
no se puede seal() sin operator_id
no se puede seal() sin owner_ref
no se puede seal() sin business_ref
no se puede seal() sin period
no se puede seal() sin problem_statement
no se puede seal() sin scope
period.end >= period.start
scope.strip() no vacío
authorization pertenece al enum permitido
schema_version conocido
segundo seal() falla
sealed es inmutable
supersede() sólo permitido si status == sealed
roundtrip dict -> model -> dict preserva campos
```

## DONE del futuro corte técnico

El futuro corte técnico sólo podrá considerarse completo si:

```text
PrimaryCaseFile existe como contrato puro.
Tiene estados draft / sealed / superseded.
seal() valida invariantes.
sealed es inmutable.
tests cubren happy path y violaciones.
no hay dependencia externa nueva.
no se toca PymIA-Live.
no se toca formula engine.
no se toca sufficiency.
no se toca evidence extraction.
no se toca owner questions.
no se implementan piezas epistémicas posteriores.
docs/contratos/primary-case-file-v1.md documenta contrato y límites.
```

## Criterio PASS de este TaskSpec

Este TaskSpec queda en PASS documental si:

```text
archivo creado en docs/pymia/
fuente principal citada
reducción explícita de FichaPrimaria completa
archivos futuros autorizados definidos
archivos prohibidos definidos
contrato mínimo delimitado
operaciones permitidas/prohibidas delimitadas
invariantes de test definidas
no se modifica código
no se modifica runtime
no se modifica PymIA-Live
```

## Stop conditions para el futuro ciclo técnico

Detener antes de implementar si:

```text
repo sucio en archivos no relacionados
aparece PrimaryCaseFile ya existente
hay conflicto con contrato vivo previo
se requiere tocar PymIA-Live
se requiere tocar vertical_slice.py
se requiere tocar motor o sufficiency
se intenta abrir lifecycle completo de caso
se intenta crear persistencia real
se intenta incorporar FichaPrimaria completa sin reducción
```

## Próximo paso autorizado después de este TaskSpec

Sólo después de aprobar este TaskSpec podrá ejecutarse:

```text
PRIMARY_CASE_FILE_V1_MINIMAL_CONTRACT_IMPLEMENTATION
```

con alcance limitado a:

```text
pymia/contracts/primary_case_file_v1.py
tests/contracts/test_primary_case_file_v1.py
docs/contratos/primary-case-file-v1.md
```

## Prohibido inferir desde este TaskSpec

```text
- No autoriza runtime.
- No autoriza PymIA-Live.
- No autoriza vertical_slice.py.
- No autoriza EvidenceRecord changes.
- No autoriza PipelineRunRecord changes.
- No autoriza OwnerSemanticClaim.
- No autoriza TensionReport.
- No autoriza AssertionCandidate.
- No autoriza OperatorConfirmation.
- No autoriza EpistemicState.
- No autoriza DominantUnknown.
- No autoriza Pack Governance completo.
```

## Commit sugerido

```text
docs(pymia): add primary case file minimal contract taskspec
```
