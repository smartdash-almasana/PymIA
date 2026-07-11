# SERVICE_1_WEB_EXPERIMENT_HUMAN_BROWSER_SMOKE_V1

## VERDICT

PASS_HUMAN_BROWSER_SMOKE.

Servicio 1 fue probado manualmente desde navegador local contra el endpoint HTTP dev-only. El flujo completo llego a delivery real autorizado.

## CONTEXTO

Frontend usado:

```text
http://127.0.0.1:8080/service_1_web_experiment_minimal_frontend.html
```

Backend usado:

```text
http://127.0.0.1:8000/service-1/experiment/run
```

Server:

```text
pymia.cli.service_1_web_experiment_server
```

Caso probado:

```text
E:\BuenosPasos\smartbridge\PymIA\prueba_excels\CASE_001_ventas_junio_2026_margin_leak.xlsx
```

## RESULTADO HTTP

```text
schema_version: SERVICE_1_WEB_EXPERIMENT_HTTP_ENDPOINT_V1
status: WEB_BACKEND_DELIVERY_READY
blocked_reason: null
trace_count: 13
```

## TRACE COMPLETO

```text
boundary: NEEDS_OWNER_CONFIRMATION
owner_confirmation_to_ingestion: INGESTION_OUTPUT_READY
semantic_bridge: SEMANTIC_CANDIDATES_READY
controlled_execution_gate: NEEDS_OWNER_CONFIRMATION
owner_confirmation_loop: OWNER_CONFIRMATION_RECHECK_READY
owner_confirmation_reinjection: CONTROLLED_EXECUTION_CANDIDATE_READY
controlled_execution_gate_recheck: CONTROLLED_EXECUTION_CANDIDATE_READY
controlled_execution_plan: EXECUTION_PLAN_READY
owner_authorization_dialogue: OWNER_AUTHORIZATION_ACCEPTED
dry_run_candidate: CONTROLLED_DRY_RUN_CANDIDATE_READY
owner_validation_dialogue: OWNER_VALIDATION_ACCEPTED
controlled_execution_result: CONTROLLED_EXECUTION_RESULT_READY
delivery: DELIVERY_PACKET_READY
```

## DELIVERY

Directorio reportado:

```text
E:\BuenosPasos\smartbridge\PymIA\PymIA-Live\..\.tmp\service_1_web_frontend_delivery
```

Resumen:

```text
status: DELIVERY_PACKET_READY
delivery_created: true
delivery_authorized: true
product_ready: true
deliverable_count: 4
```

Archivos generados:

```text
README.md              580 bytes
manifest.json          543 bytes
execution_result.json  3639 bytes
hashes.json            406 bytes
```

## GARANTIAS OBSERVADAS

```text
upload desde navegador
endpoint HTTP real
backend boundary real
orquestador real
trace completo 13/13
delivery minimo real
sin SheetJS como autoridad
sin parser duplicado
sin LLM
sin CLI legacy
```

## LIMITES

```text
dev-only
sin auth real
sin DB
sin persistencia multiusuario
frontend minimo experimental
```

## NEXT

Opciones seguras:

```text
1. Apagar server dev local.
2. Mantener evidencia de delivery en .tmp o borrarla luego.
3. Si se avanza: mejorar frontend de conversacion real, sin cambiar autoridad del orquestador.
```
