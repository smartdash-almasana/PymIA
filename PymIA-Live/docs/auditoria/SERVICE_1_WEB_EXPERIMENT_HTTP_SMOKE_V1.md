# SERVICE_1_WEB_EXPERIMENT_HTTP_SMOKE_V1

## VERDICT

PASS.

Servicio 1 fue verificado por HTTP real en entorno dev-only: upload XLSX por endpoint, delegacion al boundary web, orquestador real y delivery minimo autorizado en disco.

## CONTEXTO

Endpoint probado:

```text
POST /service-1/experiment/run
```

Server:

```text
pymia.cli.service_1_web_experiment_server
```

Boundary operativo:

```text
service_1_web_experiment_backend_boundary_v1
```

Autoridad de flujo:

```text
service_1_assisted_flow_orchestrator_v1
```

## RESULTADO DEL SMOKE

```text
HTTP: 200
status: WEB_BACKEND_DELIVERY_READY
blocked_reason: None
trace: 13 links
delivery_summary.status: DELIVERY_PACKET_READY
delivery_created: true
delivery_authorized: true
product_ready: true
deliverable_count: 4
```

## DELIVERY GENERADO

Directorio:

```text
E:\BuenosPasos\smartbridge\PymIA\.tmp\service_1_web_http_smoke_delivery
```

Archivos verificados:

```text
README.md              592 bytes
manifest.json          566 bytes
execution_result.json  3747 bytes
hashes.json            406 bytes
```

## COMO SE PROBO

El smoke temporal hizo:

```text
1. Levantar pymia.cli.service_1_web_experiment_server en puerto libre.
2. Enviar POST multipart a /service-1/experiment/run.
3. Usar CASE_001 como uploaded bytes.
4. Construir payload completo igual que los tests:
   - owner_column_answers para todas las columnas.
   - semantic_owner_answers solo para columnas pendientes del gate.
   - owner_authorization=accept.
   - owner_validation=accept.
   - delivery_authorized=true.
   - output_dir=.tmp/service_1_web_http_smoke_delivery.
5. Verificar WEB_BACKEND_DELIVERY_READY.
6. Verificar existencia de los 4 archivos de delivery.
7. Apagar server con shutdown + server_close.
```

## SCRIPT TEMPORAL

El script usado fue temporal y no debe commitearse:

```text
.tmp/service_1_web_http_smoke.py
```

El delivery generado queda como evidencia local temporal y puede borrarse sin afectar el repo:

```text
.tmp/service_1_web_http_smoke_delivery
```

## GARANTIAS DEL SMOKE

Confirmado:

```text
no SheetJS como autoridad
no parser XLSX nuevo
no LLM
no CLI legacy
no DB
no auth real
server dev-only
boundary delega en orquestador real
delivery solo con delivery_authorized=true
```

## LIMITES

```text
El endpoint sigue siendo dev-only.
No hay auth real.
No hay persistencia multiusuario.
No hay frontend productivo.
El smoke no fue commiteado, solo documentado.
```

## NEXT

Opciones seguras:

```text
1. Borrar .tmp/service_1_web_http_smoke.py y .tmp/service_1_web_http_smoke_delivery.
2. Crear frontend minimo que llame al endpoint.
3. Mantener endpoint como dev-only hasta definir auth real y persistencia.
```
