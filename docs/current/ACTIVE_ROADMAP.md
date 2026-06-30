# Active Roadmap

## STATUS

```text
SERVICE_1_XLSX_BRIDGE_ENTRYPOINT_CLOSED
```

## Current active front

```text
SERVICE_1_XLSX_RUNTIME_BRIDGE_ENTRYPOINT_V1
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
UNIT_2_OF_3: CLOSED
UNIT_3_OF_3: NEXT
```

## Unit 2 result

```text
ENTRYPOINT_MODULE: PymIA-Live/pymia/cli/service_1_xlsx_runtime_bridge.py
ENTRYPOINT_TEST: PymIA-Live/tests/smartpyme/test_service_1_xlsx_runtime_bridge_entrypoint_v1.py
FOCAL_TESTS: 7/7 passed
XLSX_BRIDGE_REGRESSION: 42/42 passed
```

## Behavior

```text
- exposes callable entrypoint
- exposes CLI main(argv)
- accepts xlsx path, case_ref, operator_ref, optional sheet
- writes JSON to stdout or output file
- returns 0 when ready
- returns 2 when blocked
- invokes the contract module only
```

## Finite units

```text
1. SERVICE_1_XLSX_RUNTIME_BRIDGE_CONTRACT_V1    CLOSED
2. SERVICE_1_XLSX_RUNTIME_BRIDGE_ENTRYPOINT_V1  CLOSED
3. SERVICE_1_XLSX_RUNTIME_BRIDGE_CLOSEOUT_V1    NEXT
```

## Stop rule

```text
MAX_UNITS: 3
FOURTH_UNIT: STOP_AND_RECONCILE
```

## Next decision gate

```text
SERVICE_1_XLSX_RUNTIME_BRIDGE_CLOSEOUT_V1
```
