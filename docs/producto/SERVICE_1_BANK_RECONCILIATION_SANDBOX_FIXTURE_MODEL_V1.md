# SERVICE_1_BANK_RECONCILIATION_SANDBOX_FIXTURE_MODEL_V1

VEREDICT:

```text
SERVICE_1_BANK_RECONCILIATION_SANDBOX_FIXTURE_MODEL_V1: IMPLEMENTED_MINIMAL_FIXTURE_MODEL
```

FILES_CREATED:

```text
PymIA-Live/pymia/smartpyme/bank_reconciliation_sandbox_fixture_model_v1.py
PymIA-Live/tests/smartpyme/test_bank_reconciliation_sandbox_fixture_model_v1.py
docs/producto/SERVICE_1_BANK_RECONCILIATION_SANDBOX_FIXTURE_MODEL_V1.md
```

FILES_MODIFIED:

```text
None
```

PURPOSE:

```text
Definir el modelo mínimo de fixtures para el sandbox de conciliación bancaria.
El modelo valida shape y seguridad de fixtures declarados.
No compara movimientos.
No ejecuta matching.
No calcula diferencias.
No declara saldo conciliado.
No genera asientos.
No usa bancos reales ni APIs.
```

MODEL:

```text
MovementFixtureV1
BankStatementFixtureV1
InternalLedgerFixtureV1
FixtureBundleInputV1
FixtureBundleResultV1
```

STATUSES:

```text
VALID
MISSING_BANK_STATEMENT_FIXTURE
MISSING_INTERNAL_LEDGER_FIXTURE
INVALID_MOVEMENT
DUPLICATE_MOVEMENT_REF
BLOCKED_LIVE_SOURCE
INVALID_INPUT
```

VALIDATION_RULES:

```text
- bank_statement_fixture required
- internal_ledger_fixture required
- live_source must be False
- movement_ref required
- date required
- amount required and Decimal-compatible
- description required
- duplicate movement_ref blocked across bundle
```

CORE INVARIANTS:

```text
runtime_authorized = False always
production_allowed = False always
```

HANDOFF:

```text
A VALID bundle exposes handoff_refs:
- bank_statement_fixture
- internal_ledger_fixture

These refs can be used by the sandbox contract boundary.
```

TESTS:

```text
python -m pytest tests/smartpyme/test_bank_reconciliation_sandbox_fixture_model_v1.py -q
11 passed in 0.34s
```

```text
python -m pytest tests/smartpyme/test_bank_reconciliation_sandbox_fixture_model_v1.py tests/smartpyme/test_bank_reconciliation_sandbox_contract_v1.py -q
20 passed in 3.55s
```

LIMITS_PRESERVED:

```text
No IO.
No openpyxl.
No requests/httpx.
No APIs.
No live bank data.
No Mercado Pago runtime.
No matching.
No scoring.
No final differences.
No final balance claim.
No accounting entries.
No fiscal certification.
No FSM.
No LLM.
No chatbot.
No vertical_slice.py.
```

NEXT_BLOCK:

```text
SERVICE_1_BANK_RECONCILIATION_SANDBOX_FIXTURE_HANDOFF_V1
```

COMMIT_READY:

```text
YES
```
