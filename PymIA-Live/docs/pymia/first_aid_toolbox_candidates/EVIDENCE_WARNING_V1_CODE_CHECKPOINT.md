# Evidence Warning V1 Code Checkpoint

## Estado

CODE_SLICE_CLOSED

## Alcance

Slice técnico contract-only para declarar advertencias estructuradas de evidencia.

Objetivo principal:

```text
Evitar warnings como texto suelto y permitir distinguir severidad, bloqueo de cálculo, disclosure owner-facing y detalle operator-facing.
```

No integra con runtime.
No integra con structured_evidence_builder.
No toca diagnostic_core.
No toca pipeline.
No toca OCF.
No toca replay.
No toca storage.

## Archivos creados

```text
PymIA-Live/pymia/contracts/evidence_warning_v1.json
PymIA-Live/pymia/contracts/evidence_warning_v1.py
PymIA-Live/tests/contracts/test_evidence_warning_v1.py
```

## Contrato creado

```text
contract_id: EVIDENCE_WARNING_V1
schema_version: 1.0
status: CONTRACT_ONLY
runtime_impact: NONE
implementation_authorized: false
compatible_contracts: EVIDENCE_AVAILABILITY_V1
```

## Severidades declaradas

```text
INFO
CAUTION
BLOCKING
```

## Campos declarados por warning

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

## Reglas preservadas

```text
INFO no bloquea cálculo y no exige disclosure owner-facing
CAUTION no bloquea cálculo pero exige disclosure owner-facing
BLOCKING bloquea cálculo y exige disclosure owner-facing
owner_message no debe exponer términos técnicos internos
operator_detail puede contener contexto técnico controlado
reason_code es compatible con Evidence Availability V1
```

## Reason codes mapeados

```text
OBSERVED_VALUE -> INFO
OBSERVED_ZERO -> INFO
MISSING_FIELD -> BLOCKING
MISSING_SOURCE -> BLOCKING
PARTIAL_SOURCE -> CAUTION
COVERAGE_CAPPED -> CAUTION
AMBIGUOUS_FORMAT -> BLOCKING
AMBIGUOUS_MEANING -> BLOCKING
EXCLUDED_BY_RULE -> BLOCKING
EXCLUDED_LOW_CONFIDENCE -> BLOCKING
```

## Loader creado

```text
load_evidence_warning_contract()
list_warning_severities()
get_warning_severity()
list_warning_fields()
default_severity_for_reason()
blocks_calculation()
requires_owner_disclosure()
is_owner_message_allowed()
```

Naturaleza del loader:

```text
puro
cacheado
sólo lectura JSON
sin creación runtime de warnings
sin normalización de evidencia
sin cálculo de fórmulas
sin diagnóstico
sin mutación de estado
```

## Tests ejecutados

Comando reportado:

```text
python -m pytest tests/contracts/test_evidence_warning_v1.py -q
```

Resultado:

```text
TESTS_RUN: 16
RESULT: 16/16 PASSED
FAILURES: NONE
```

## Validaciones cubiertas

```text
JSON parseable
loader puro funciona
3 severities
8 warning fields
10 reason_code severity defaults
INFO no bloquea ni exige disclosure
CAUTION exige disclosure y no bloquea
BLOCKING bloquea y exige disclosure
calculation_policy consistente con severities
blocking reason codes bloquean cálculo
owner_message rechaza términos técnicos internos
operator_detail_policy permite contexto técnico sin stacktrace
unknown severity/reason devuelve safe false/none
blank inputs rechazados
sin claves runtime/plugin/executor
sin definición de ejecución, diagnóstico, persistencia o pipeline
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

El contrato Evidence Warning V1 queda cerrado como slice técnico contract-only.

No autoriza integración.
No autoriza generación runtime de warnings.
No autoriza normalización runtime.
No autoriza diagnóstico.

## Próximo paso seguro

```text
Commit del slice Evidence Warning V1.
```

Después del commit, el próximo frente técnico natural es:

```text
Evidence Value Normalizer V1
```

Ese frente deberá consumir Evidence Availability V1 y Evidence Warning V1, pero sólo como servicio puro testeado, sin pipeline.

## Estado final

```text
EVIDENCE_WARNING_V1_CODE_CHECKPOINT = CREATED
status: CODE_SLICE_CLOSED
tests: 16/16 PASSED
verdict: PASS
```
