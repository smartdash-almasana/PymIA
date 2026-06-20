# Evidence Availability V1 Code Checkpoint

## Estado

CODE_SLICE_CLOSED

## Alcance

Slice técnico contract-only para declarar semántica de disponibilidad de evidencia.

Objetivo principal:

```text
Evitar que PymIA confunda cero real, dato no disponible, evidencia parcial, extracción truncada, ambigüedad o exclusión de cálculo.
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
PymIA-Live/pymia/contracts/evidence_availability_v1.json
PymIA-Live/pymia/contracts/evidence_availability_v1.py
PymIA-Live/tests/contracts/test_evidence_availability_v1.py
```

## Contrato creado

```text
contract_id: EVIDENCE_AVAILABILITY_V1
schema_version: 1.0
status: CONTRACT_ONLY
runtime_impact: NONE
implementation_authorized: false
```

## Estados declarados

```text
MEASURED
ZERO_REAL
NOT_AVAILABLE
PARTIAL
CAPPED
AMBIGUOUS
EXCLUDED
```

## Reglas preservadas

```text
ZERO_REAL != NOT_AVAILABLE
MEASURED permite cálculo
ZERO_REAL permite cálculo
NOT_AVAILABLE bloquea campo requerido
PARTIAL permite cálculo pero exige disclosure owner-facing
CAPPED permite cálculo pero exige disclosure owner-facing
AMBIGUOUS bloquea cálculo
EXCLUDED bloquea cálculo
```

## Reason codes declarados

```text
OBSERVED_VALUE
OBSERVED_ZERO
MISSING_FIELD
MISSING_SOURCE
PARTIAL_SOURCE
COVERAGE_CAPPED
AMBIGUOUS_FORMAT
AMBIGUOUS_MEANING
EXCLUDED_BY_RULE
EXCLUDED_LOW_CONFIDENCE
```

## Loader creado

```text
load_evidence_availability_contract()
list_availability_statuses()
get_availability_status()
get_reason_code()
default_status_for_reason()
allows_calculation()
requires_owner_disclosure()
is_excluded_from_calculation()
blocks_required_field()
```

Naturaleza del loader:

```text
puro
cacheado
sólo lectura JSON
sin normalización de evidencia
sin cálculo de fórmulas
sin diagnóstico
sin mutación de estado
```

## Tests ejecutados

Comando reportado:

```text
python -m pytest tests/contracts/test_evidence_availability_v1.py -q
```

Resultado:

```text
TESTS_RUN: 15
RESULT: 15/15 PASSED
FAILURES: NONE
```

## Validaciones cubiertas

```text
JSON parseable
loader puro funciona
7 availability statuses
10 reason codes
ZERO_REAL no equivale a NOT_AVAILABLE
MEASURED y ZERO_REAL permiten cálculo sin disclosure
NOT_AVAILABLE bloquea campo requerido y exige disclosure
PARTIAL y CAPPED permiten cálculo pero exigen disclosure
AMBIGUOUS y EXCLUDED bloquean cálculo y campo requerido
reason codes mapean a default_status correcto
unknown status/reason devuelve safe false/none
sin claves runtime/loader/plugin/executor
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

El contrato Evidence Availability V1 queda cerrado como slice técnico contract-only.

No autoriza integración.
No autoriza normalización runtime.
No autoriza diagnóstico.

## Próximo paso seguro

```text
Commit del slice Evidence Availability V1.
```

Después del commit, el próximo frente técnico natural es:

```text
Structured Warning Contract V1
```

## Estado final

```text
EVIDENCE_AVAILABILITY_V1_CODE_CHECKPOINT = CREATED
status: CODE_SLICE_CLOSED
tests: 15/15 PASSED
verdict: PASS
```
