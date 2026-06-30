# Active Roadmap

## STATUS

```text
SERVICE_1_XLSX_BRIDGE_CONTRACT_CLOSED
```

## Current active front

```text
SERVICE_1_XLSX_RUNTIME_BRIDGE_CONTRACT_V1
```

## Closed baseline

```text
PHASE_I_CLOSED
POST_I_HARDENING_CLOSED
```

## Active term

```text
CONTROLLED_OPERATIONAL_CASE
```

## Bridge milestone

```text
UNIT_1_OF_3: CLOSED
UNIT_2_OF_3: NEXT
UNIT_3_OF_3: NOT_STARTED
```

## Unit 1 result

```text
CONTRACT_MODULE: PymIA-Live/pymia/smartpyme/service_1_xlsx_runtime_bridge_contract_v1.py
CONTRACT_TEST: PymIA-Live/tests/smartpyme/test_service_1_xlsx_runtime_bridge_contract_v1.py
FOCAL_TESTS: 12/12 passed
XLSX_REGRESSION: 35/35 passed
```

## Reuse rule

```text
Reuse existing XLSX reader and normalizer.
Do not create a second XLSX parser.
```

## Finite units

```text
1. SERVICE_1_XLSX_RUNTIME_BRIDGE_CONTRACT_V1    CLOSED
2. SERVICE_1_XLSX_RUNTIME_BRIDGE_ENTRYPOINT_V1  NEXT
3. SERVICE_1_XLSX_RUNTIME_BRIDGE_CLOSEOUT_V1    NOT_STARTED
```

## Stop rule

```text
MAX_UNITS: 3
FOURTH_UNIT: STOP_AND_RECONCILE
```

## Next decision gate

```text
SERVICE_1_XLSX_RUNTIME_BRIDGE_ENTRYPOINT_V1
```
