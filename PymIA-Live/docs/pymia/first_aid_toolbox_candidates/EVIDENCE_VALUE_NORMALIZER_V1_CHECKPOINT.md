# Evidence Value Normalizer V1 Checkpoint

## Estado

CODE_SLICE_CLOSED

## Alcance

Servicio puro para normalizar un valor crudo de evidencia usando los contratos:

```text
Evidence Availability V1
Evidence Warning V1
```

Objetivo principal:

```text
Convertir raw_value + field_name + expected_type + required en una salida computable segura.
```

No lee archivos.
No persiste datos.
No calcula fórmulas de negocio.
No diagnostica.
No toca pipeline.
No toca structured_evidence_builder.
No toca OCF.
No toca replay.
No toca storage.

## Archivos creados

```text
PymIA-Live/pymia/smartpyme/evidence_value_normalizer.py
PymIA-Live/tests/smartpyme/test_evidence_value_normalizer.py
```

## Entrada

```text
raw_value
field_name
expected_type
required
```

Tipos soportados:

```text
text
number
integer
boolean
```

## Salida

```text
NormalizedEvidenceValue
```

Campos principales:

```text
field_name
expected_type
raw_value
normalized_value
availability_status
reason_code
warnings
excluded_from_calculation
blocks_required_field
allows_calculation
requires_owner_disclosure
```

## Warning model

```text
EvidenceWarning
```

Campos:

```text
warning_id
severity
source_field
reason_code
owner_message
operator_detail
blocks_calculation
suggested_next_evidence
```

## Conducta implementada

```text
texto no vacío -> MEASURED
0 numérico -> ZERO_REAL
"0" numérico -> ZERO_REAL
None -> NOT_AVAILABLE
string vacío -> NOT_AVAILABLE
número válido -> MEASURED
decimal con coma simple -> MEASURED
número con separadores ambiguos -> AMBIGUOUS
integer decimal no entero -> AMBIGUOUS
boolean sí/no -> MEASURED
boolean usado como number -> AMBIGUOUS
```

## Reglas preservadas

```text
ZERO_REAL != NOT_AVAILABLE
missing required bloquea campo requerido
missing optional no bloquea required field pero sigue siendo NOT_AVAILABLE
AMBIGUOUS bloquea cálculo y excluye valor
warnings BLOCKING se crean para missing/ambiguous
owner_message no expone términos técnicos internos
operator_detail conserva reason_code y availability_status
```

## Tests ejecutados

Comando reportado:

```text
python -m pytest tests/smartpyme/test_evidence_value_normalizer.py -q
```

Resultado reportado:

```text
TESTS_RUN: 16
RESULT: 16/16 PASSED
FAILURES: NONE
```

Nota:

```text
El conteo real reportado es 16 tests. La mención previa de 17 tests fue un error de conteo en el resumen conversacional.
```

## Validaciones cubiertas

```text
texto medido
cero real numérico
cero real string
missing required
missing optional
formato numérico ambiguo
decimal con coma
integer decimal inválido
integer válido
boolean sí/no
boolean ambiguo
boolean rechazado como number
owner messages sin términos internos
field_name / expected_type inválidos rechazados
sin dependencias runtime/pipeline/diagnóstico
servicio puro sin file IO, persistencia, pandas ni openpyxl
```

## Límites preservados

```text
runtime_touched: NO
kernel_touched: NO
pipeline_touched: NO
storage_touched: NO
diagnostic_core_touched: NO
structured_evidence_builder_touched: NO
implementation_authorized: NO
```

## Decisión

Evidence Value Normalizer V1 queda cerrado como servicio puro testeado.

No autoriza integración al structured_evidence_builder.
No autoriza integración al pipeline.
No autoriza diagnóstico.
No autoriza ejecución de herramientas.

## Próximo paso seguro

```text
Commit del slice Evidence Value Normalizer V1.
```

Después del commit, el próximo frente técnico posible es:

```text
Two Source Reconciliation Contract V1
```

Ese frente puede aprovechar la arqueología de smartcounter_core, pero debe empezar contract-only.

## Estado final

```text
EVIDENCE_VALUE_NORMALIZER_V1_CHECKPOINT = CREATED
status: CODE_SLICE_CLOSED
tests: 16/16 PASSED
verdict: PASS
```
