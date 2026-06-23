# SERVICE_1_BANK_RECONCILIATION_SANDBOX_RUNTIME_CONTRACT_V1

VEREDICT:

```text
SERVICE_1_BANK_RECONCILIATION_SANDBOX_RUNTIME_CONTRACT_V1: IMPLEMENTED_MINIMAL_SANDBOX_CONTRACT
```

FILES_CREATED:

```text
PymIA-Live/pymia/smartpyme/bank_reconciliation_sandbox_contract_v1.py
PymIA-Live/tests/smartpyme/test_bank_reconciliation_sandbox_contract_v1.py
docs/producto/SERVICE_1_BANK_RECONCILIATION_SANDBOX_RUNTIME_CONTRACT_V1.md
```

FILES_MODIFIED:

```text
None
```

NAMING_NOTE:

```text
El archivo de código usa nombre corto `bank_reconciliation_sandbox_contract_v1.py`.
El bloque documental mantiene el nombre completo de producto.
```

PURPOSE:

```text
Crear la frontera contractual mínima posterior al contrato bancario y al gate humano.
La frontera sólo permite preparar un candidato sandbox basado en fixtures declarados.
No ejecuta conciliación real.
No procesa bancos reales.
No llama APIs.
No genera asientos.
No certifica saldos ni diferencias finales.
```

INPUTS_REQUIRED:

```text
bank_contract con status READY_FOR_REVIEW
human_review_gate con status PASS
fixture_refs:
  - bank_statement_fixture
  - internal_ledger_fixture
live_use_requested = False
```

STATUSES:

```text
READY_FOR_SANDBOX_CONTRACT
BLOCKED_BANK_CONTRACT_NOT_READY
BLOCKED_HUMAN_REVIEW_NOT_PASSED
MISSING_FIXTURES
BLOCKED_LIVE_USE
INVALID_INPUT
```

CORE INVARIANTS:

```text
runtime_authorized = False always
production_allowed = False always
```

DELIVERY:

```text
El resultado incluye delivery_input compatible con Service1XlsxDeliveryInputV1.
```

TESTS:

```text
python -m pytest tests/smartpyme/test_bank_reconciliation_sandbox_contract_v1.py -q
9 passed in 1.48s
```

```text
python -m pytest tests/smartpyme/test_bank_reconciliation_contract_v1.py tests/smartpyme/test_accounting_human_review_gate_v1.py tests/smartpyme/test_service_1_xlsx_delivery_v1.py tests/smartpyme/test_bank_reconciliation_sandbox_contract_v1.py -q
37 passed in 1.81s
```

LIMITS_PRESERVED:

```text
No IO.
No API calls.
No live bank data.
No Mercado Pago runtime.
No accounting runtime.
No matching algorithm.
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
SERVICE_1_BANK_RECONCILIATION_SANDBOX_FIXTURE_MODEL_V1
```

COMMIT_READY:

```text
YES
```
