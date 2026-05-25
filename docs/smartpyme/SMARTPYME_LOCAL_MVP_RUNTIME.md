# SMARTPYME_LOCAL_MVP_RUNTIME

Estado: VIGENTE  
Fecha: 2026-05-26

## Veredicto

`SMARTPYME_LOCAL_MVP_RUNTIME_READY`

## Estado sample

`SMARTPYME_LOCAL_MVP_RUNTIME_SAMPLE_PASS`

## Flujo validado

```text
mensaje + Excel + tenant_id
→ ReceptionRecord
→ diagnóstico Excel
→ Findings
→ OutputReport
→ storage local por tenant
```

## Comando e2e_cli (sample confirmado)

```text
python -m pymia.smartpyme.e2e_cli ^
  --tenant-id tenant_runtime_sample ^
  --message "No sé si vendo con margen y tengo costos incompletos" ^
  --classification margen ^
  --input E:\BuenosPasos\smartbridge\.tmp\smartpyme-local-runtime-sample\input\ventas_costos_sample.xlsx ^
  --out-dir E:\BuenosPasos\smartbridge\.tmp\smartpyme-local-runtime-sample\output ^
  --storage-dir E:\BuenosPasos\smartbridge\.tmp\smartpyme-local-runtime-sample\storage
```

## Inputs requeridos

- tenant_id
- message
- classification
- input `.xlsx`
- out-dir
- storage-dir (opcional)

## Outputs generados

- `diagnostic_report.md`
- `diagnostic_result.json`
- `reception_record.json`
- `receptions.jsonl`
- `results/reception_record.json`

## Resultado sample PASS

- tenant_id: `tenant_runtime_sample`
- `ReceptionRecord.status`: `DELIVERED`
- findings: `4`
- exit code: `0`
- repo: limpio

## Restricciones preservadas

- local only
- sin Hermes real
- sin producción
- sin Telegram real
- sin secretos
- sin `.env` real
- sin VM
- sin MCP-3
- sin kernel runtime SCN
- sin Boundary Layer runtime
- sin Output Gateway runtime
- sin render real

## Próximos frentes posibles

- reporte HTML/PDF
- input real controlado
- API local
- mejora de taxonomía de findings
- persistencia más robusta
