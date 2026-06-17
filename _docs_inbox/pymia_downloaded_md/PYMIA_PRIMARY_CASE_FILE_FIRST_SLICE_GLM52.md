# PymIA — PrimaryCaseFile V1: primer corte técnico mínimo

## Referencia

Documento de referencia basado en la respuesta de GLM 5.2 para aterrizar `FichaPrimaria / PrimaryCaseFile V1` en el repo PymIA sin sobrediseñar ni romper el pipeline existente.

Nombre sugerido para repo:

```text
PYMIA_PRIMARY_CASE_FILE_FIRST_SLICE_GLM52.md
```

## Veredicto

El primer corte técnico correcto no es implementar toda la constitución epistémica.

El primer corte correcto es:

```text
crear PrimaryCaseFile V1 como contrato aislado
```

Sin meter lógica en `vertical_slice.py`.

Sin tocar motor de fórmulas.

Sin tocar suficiencia.

Sin tocar extracción de evidencia.

Sin implementar todavía OwnerSemanticClaim, TensionReport, AssertionCandidate, OperatorConfirmation, EpistemicState, DominantUnknown ni Pack Governance completo.

## Decisión principal

```text
PrimaryCaseFile debe nacer como hoja.
```

Eso significa:

```text
sin imports del kernel
sin imports de vertical_slice
sin dependencia de formula engine
sin dependencia de sufficiency
sin dependencia de rendering
sin dependencia externa nueva
```

## Archivos sugeridos

Primer corte:

```text
pymia/contracts/primary_case_file_v1.py
tests/contracts/test_primary_case_file_v1.py
docs/contratos/primary-case-file-v1.md
```

Posible corte posterior:

```text
pcf_id opcional en PipelineRunRecord / run record
wiring mínimo en vertical_slice.py sólo si es inevitable
```

## Qué NO tocar todavía

```text
formula engine
sufficiency
evidence extraction
owner questions
owner answers
evidence requests
event replayer
Graphify config
dashboard
API
forecast
Pack Governance completo
DominantUnknown
EpistemicState
OperatorConfirmation
AssertionCandidate
TensionReport
```

## Contrato mínimo de PrimaryCaseFile V1

Campos mínimos:

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

## Operaciones mínimas

```text
seal()
is_sealed()
supersede(new_pcf_id)
```

No implementar todavía:

```text
update()
reopen()
attach_evidence()
case lifecycle completo
eventos
persistencia real
migraciones
```

## Regla sobre case_id

Decisión corregida:

```text
PrimaryCaseFile NO crea case_id.
PrimaryCaseFile se ata a tenant_id + case_id existentes.
```

Motivo:

```text
si PrimaryCaseFile crea case_id ahora, se abre lifecycle de caso,
y eso es demasiado para el primer corte.
```

## Invariantes a testear

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
authorization pertenece al enum
schema_version conocido
segundo seal() falla
sealed es inmutable
supersede() sólo permitido si status == sealed
roundtrip dict -> model -> dict preserva campos
```

## Convivencia con evidence records

```text
PrimaryCaseFile referencia evidence records por id.
No los posee.
No hace cascade.
No reemplaza evidence records.
No envuelve evidence records.
```

Campo:

```yaml
initial_evidence_refs: list[evidence_id]
```

Si una evidencia queda huérfana, se detectará después mediante reconciliación. No en este primer corte.

## Convivencia con pipeline/run records

Regla:

```text
PipelineRunRecord puede recibir pcf_id opcional en un corte posterior.
```

Runs existentes:

```text
pcf_id = None
siguen siendo válidos
```

Runs nuevos:

```text
pueden llevar pcf_id si existe PrimaryCaseFile sellado
```

No bloquear el pipeline actual por ausencia de PCF en el primer corte.

## Riesgo de meterlo directo en vertical_slice.py

```text
vertical_slice.py se vuelve script-dios
la lógica de PCF queda cautiva del CLI
el sellado queda acoplado al éxito/fracaso del run
se mezcla modelo, validación, persistencia y orquestación
otros módulos terminarán importando desde vertical_slice
refactor futuro más caro
```

Conclusión:

```text
vertical_slice.py no debe contener lógica de PrimaryCaseFile.
```

## Riesgo de sobrediseñar

Evitar:

```text
case lifecycle completo
máquina de estados de caso
repositorio real persistente
permisos complejos
eventos
auditoría completa de caso
FichaExtension
integración con todas las piezas epistémicas
```

Riesgo de fondo:

```text
construir infraestructura de caso antes de validar el contrato mínimo.
```

## DONE del primer corte

El corte se considera terminado si:

```text
PrimaryCaseFile existe como contrato puro.
Tiene estados draft / sealed / superseded.
seal() valida invariantes.
sealed es inmutable.
tests cubren happy path y violaciones.
no hay dependencia externa nueva.
no se toca formula engine.
no se toca sufficiency.
no se toca evidence extraction.
no se toca owner questions.
no se implementan piezas 1–7.
docs/contratos/primary-case-file-v1.md documenta contrato y límites.
```

Opcional posterior:

```text
PipelineRunRecord acepta pcf_id opcional.
vertical_slice puede adjuntar pcf_id sin lógica de sellado.
```

## Orden recomendado de trabajo en repo

```text
1. Crear contrato PrimaryCaseFile V1.
2. Crear tests de invariantes.
3. Crear documento de contrato.
4. Sólo después evaluar wiring mínimo con run record.
5. Recién después decidir si vertical_slice acepta pcf_id.
```

## Frase operativa

```text
Primero fundamos el caso.
Después lo conectamos al pipeline.
```

## Veredicto final

El repo ya tiene pipeline.

Lo que falta ahora no es rehacerlo.

Lo que falta es introducir gobierno de caso de forma mínima:

```text
PrimaryCaseFile como contrato aislado
sin contaminar el kernel
sin agrandar vertical_slice.py
sin abrir refactor gigante
```
