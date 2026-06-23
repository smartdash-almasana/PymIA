# SERVICE_1_ACCOUNTING_WORKPAPER_DRAFT_PACKET_V1

Implementa un paquete puro/determinístico de revisión owner/operator para un borrador de papel de trabajo contable.

## Quick path

1. Consume `workpaper_contract_result`, `manifest_model_result` y `human_review_gate_result`.
2. Evalúa readiness, bloqueos y claims prohibidos sin ejecutar runtime ni leer archivos.
3. Produce `delivery_input` compatible con `Service1XlsxDeliveryInputV1`.

## Details

| Topic | Decision |
|-------|----------|
| Capability | `service_1_accounting_workpaper_draft_packet_v1` |
| Statuses | `READY`, `BLOCKED`, `INVALID_INPUT` |
| Runtime | `runtime_authorized = False` |
| Production | `production_allowed = False` |
| Allowed output | Draft review packet only |
| Out of scope | Final workpaper, template execution, file IO, accounting/fiscal certification, entries |

## READY rule

`READY` sólo aplica si:

- `workpaper_contract_result["status"] == "READY_FOR_REVIEW"`
- `manifest_model_result["status"] == "VALID"`
- `human_review_gate_result["status"] == "PASS"`
- ningún componente trae `runtime_authorized=True`
- ningún componente trae `production_allowed=True`

## Blocked reasons

- `workpaper_contract_not_ready`
- `manifest_model_not_valid`
- `human_review_gate_not_passed`
- `runtime_authorization_forbidden`
- `production_use_forbidden`
- `invalid_packet_input`
- `invalid_packet_components`

## Forbidden claims

- No genera papel de trabajo final.
- No certifica evidencia suficiente.
- No certifica conclusión contable o fiscal.
- No ejecuta plantilla.
- No lee archivos soporte.
- No genera asientos contables.

## Checklist

- [x] No parser
- [x] No file IO
- [x] No openpyxl en módulo productivo
- [x] No pandas
- [x] No API / OCR / LLM / FSM
- [x] No `vertical_slice.py`
- [x] No runtime / no production allowed

## Verification

```bash
cd PymIA-Live
python -m pytest tests/smartpyme/test_accounting_workpaper_draft_packet_v1.py tests/smartpyme/test_accounting_workpaper_manifest_model_v1.py tests/smartpyme/test_accounting_workpaper_contract_v1.py tests/smartpyme/test_accounting_human_review_gate_v1.py tests/smartpyme/test_service_1_xlsx_delivery_v1.py -q
```

## Next step

Abrir el siguiente bloque sólo si este draft packet quedó validado y sin claims de runtime: integración de runtime sandbox mínimo sobre contratos ya cerrados.
