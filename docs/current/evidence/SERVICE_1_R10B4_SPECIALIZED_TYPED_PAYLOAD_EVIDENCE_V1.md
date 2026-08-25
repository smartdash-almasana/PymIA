# Servicio 1 — R10B4 specialized typed payload evidence

Date: 2026-08-24

## Scope

R10B4 removes only the informal specialized mapping/keyword fan-out between the Product Root and the Consorcios/Reconciliation workflow boundaries. Ingestion aliases, legacy launch projection, R11 work, and downstream authority contracts are out of scope.

## Before / after

Before, `service_1_product_pipeline_v1.py` copied one `SpecializedDomainExecuteRequestV1.payload` into parallel Product Root mappings (`expense_variance_request`, `collection_aging_request`, and `reconciliation_request`) and decomposed them into specialized builder kwargs. The Reconciliation builder also exposed the specialized keyword `reconciliation_request`.

After, the Product Root retains one typed `specialized_payload` mapping and passes that payload directly as the uniform `request` boundary to the selected specialized workflow. The three parallel mapping variables and specialized keyword are absent from runtime and affected tests. No wrapper, alias, fallback, or second dispatch path was added.

## Typed contract

`SpecializedDomainExecuteRequestV1` remains the command contract and its `payload: Mapping[str, Any]` remains unchanged. Product Root subtype validation remains explicit and fail-closed through `SPECIALIZED_DOMAIN_SUBTYPES`. Consorcios builders accept the canonical mapping interface directly; Reconciliation uses the same `request` boundary. Specialized workflows, common math/policy, anti-dump safety flags, and fail-closed behavior are preserved.

## Static evidence

- Exact stale identifiers `expense_variance_request`, `collection_aging_request`, `reconciliation_request`, and `specialized_request`: zero matches in `pymia/` and `tests/` Python sources after R10B4.
- Specialized builder calls use only `request=specialized_payload`.
- No ingestion-alias or legacy-launch-projection changes were made for R10B4.

## Focal verification

Command:

```text
python -m pytest -q tests/smartpyme/test_service_1_consorcios_expense_variance_v1.py tests/smartpyme/test_service_1_consorcios_collection_aging_v1.py tests/smartpyme/test_service_1_reconciliation_product_wiring_v1.py tests/smartpyme/test_service_1_reconciliation_governed_flow_v1.py tests/smartpyme/test_service_1_request_kind_dispatch_v1.py
```

Result: **25 passed / 0 failed** in 8.15 seconds.

This is the Product Root + R8 specialized workflow + anti-dump/request-dispatch focal set. No full suite, R11, commit, push, or deploy was run.
