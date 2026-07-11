# SERVICE_1_WEB_EXPERIMENT_HTTP_CANON_DOC_V1

## VERDICT

PASS_DOCUMENTED.

El endpoint HTTP experimental de Servicio 1 queda documentado como boundary dev-only sobre el orquestador real. No reemplaza el flujo asistido cerrado ni gobierna Servicio 1 por si mismo.

## HEAD DE REFERENCIA

- Commit de implementacion del endpoint: `8b673c8`
- Commit message: `feat(pymia-live): add dev http endpoint for service 1 web experiment`

## ENDPOINT

```text
POST /service-1/experiment/run
```

Implementacion:

```text
PymIA-Live/pymia/cli/service_1_web_experiment_server.py
```

Autoridad operativa delegada:

```text
service_1_web_experiment_backend_boundary_v1
-> service_1_assisted_flow_orchestrator_v1
-> 12 eslabones cerrados de Servicio 1
```

## ALCANCE

Este endpoint existe solo para experimento local/dev de web upload.

Hace:

```text
multipart HTTP
-> extrae XLSX + payload_json
-> llama al backend boundary real
-> devuelve JSON con status, blocked_reason, trace y refs/resumen de delivery
```

No hace:

```text
no auth real
no DB
no LLM
no SheetJS como autoridad
no parser XLSX propio
no CLI legacy
no APIs externas
no eco del archivo crudo
no delivery sin delivery_authorized=True
```

## INPUT

`multipart/form-data`:

```text
file: archivo .xlsx
payload_json: JSON string
```

Shape esperado de `payload_json`:

```json
{
  "owner_column_answers": {},
  "semantic_owner_answers": {},
  "owner_authorization": "accept",
  "owner_validation": "accept",
  "delivery_authorized": true,
  "output_dir": "..."
}
```

## OUTPUT

JSON con al menos:

```text
status
blocked_reason
trace
delivery_packet summary/refs
```

El endpoint no debe devolver el archivo subido ni celdas crudas como eco HTTP.

## DELIVERY

El delivery solo se crea si el flujo real llega a estado ready y `delivery_authorized=True`.

Archivos esperados del delivery minimo:

```text
README.md
manifest.json
execution_result.json
hashes.json
```

## TESTS CERTIFICADOS

```text
tests/smartpyme/test_service_1_web_experiment_http_endpoint_v1.py -> 5 passed
tests/smartpyme/test_service_1_web_experiment_backend_boundary_v1.py -> 8 passed
conjunto endpoint + boundary -> 13 passed in 9.54s
```

Cobertura reportada:

```text
happy path CASE_001 -> WEB_BACKEND_DELIVERY_READY
missing file -> 400 JSON
missing payload -> 400 JSON
invalid extension -> 400/BLOCKED
delivery_authorized=false -> BLOCKED sin writes
regresion backend boundary -> PASS
```

## COMANDO DEV

Ejemplo conceptual. Ajustar puerto segun implementacion del server:

```bash
cd E:/BuenosPasos/smartbridge/PymIA/PymIA-Live
set PYTHONPATH=.
../.venv/Scripts/python.exe -m pymia.cli.service_1_web_experiment_server
```

Ejemplo `curl` conceptual:

```bash
curl -X POST http://127.0.0.1:8000/service-1/experiment/run \
  -F "file=@../prueba_excels/CASE_001_ventas_junio_2026_margin_leak.xlsx" \
  -F "payload_json={\"owner_column_answers\":{},\"semantic_owner_answers\":{},\"owner_authorization\":\"accept\",\"owner_validation\":\"accept\",\"delivery_authorized\":true,\"output_dir\":\".tmp/service_1_web_delivery\"}"
```

Nota: el payload real debe incluir las respuestas requeridas por el orquestador. El ejemplo muestra el formato, no garantiza happy path sin completar respuestas.

## GAP

`graphify update` fue intentado y timeouteo. No bloquea el endpoint ni los tests.

## NEXT

Opciones seguras:

```text
1. Smoke manual local del endpoint con CASE_001 y payload completo.
2. Frontend minimo que llame a este endpoint.
3. Mantener el endpoint como dev-only hasta definir auth real y persistencia.
```
