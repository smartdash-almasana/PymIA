# Events V1 Contract

Estado: DRAFT
Fecha: 2026-06-11
Alcance: contrato minimo para backfill offline de webhooks hacia eventos de dominio.

## Proposito

Definir la frontera entre eventos crudos recibidos desde plataformas externas y eventos internos normalizados de PymIA.

Este contrato no implementa runtime, no define migraciones, no toca graph, no toca Telegram, no toca Hermes, no toca conversa-engine y no ejecuta DiagnosticCore.

## Principio

Los webhooks externos no son eventos de dominio.

- WebhookEvent: hecho tecnico recibido desde una plataforma externa.
- DomainEvent: hecho interno normalizado, idempotente y auditable.

El payload externo se conserva como evidencia tecnica. El dominio consume eventos normalizados.

## WebhookEvent minimo

Campos:

- event_id
- tenant_id
- source_platform
- event_type
- occurred_at
- received_at
- payload_hash
- raw_payload
- metadata

Reglas:

- No diagnostica.
- No calcula formulas.
- No altera payload bruto.
- No depende del mensaje narrativo del duenio.
- Debe ser serializable a JSON.

## DomainEvent minimo

Campos:

- domain_event_id
- tenant_id
- source_event_id
- source_platform
- event_name
- aggregate_type
- aggregate_id
- occurred_at
- payload
- payload_hash
- idempotency_key
- schema_version
- metadata

Reglas:

- Debe derivarse deterministicamente desde WebhookEvent.
- Debe conservar trazabilidad hacia source_event_id.
- No ejecuta diagnostico.
- No invoca LLM.
- No escribe runtime productivo en el slice inicial.

## Idempotencia

- WebhookEvent: event_id + payload_hash.
- DomainEvent: tenant_id + event_name + aggregate_type + aggregate_id + payload_hash.

Si dos eventos tienen la misma idempotency_key, el replayer local debe emitir uno solo y registrar el duplicado como skipped_duplicate.

## Eventos iniciales soportados

- order_created
- payment_registered
- refund_registered

Todo evento no soportado debe producir skipped_unsupported sin excepcion no controlada.

## Resultado esperado del replayer local

Entrada: JSONL local de WebhookEvent.
Salida: JSONL local de DomainEvent y resumen deterministico.

Resumen minimo:

- received_count
- emitted_count
- skipped_duplicate_count
- skipped_unsupported_count
- invalid_count
- output_path

## Archivos permitidos para el proximo slice

- pymia/contracts/events_v1.py
- pymia/domain/event_transformer.py
- pymia/cli/event_replayer.py
- tests/e2e/test_event_replayer.py

## Archivos prohibidos

- conversa-engine/
- pymia/orchestration/graph.py
- pymia/diagnostic_core/
- pymia/telegram_*
- pymia/hermes/
- runtime productivo
- migraciones de base de datos

## Criterios de aceptacion

- Parsear WebhookEvent desde JSONL local.
- Transformar eventos soportados a DomainEvent.
- Saltar duplicados por idempotency_key.
- Saltar eventos no soportados sin romper ejecucion.
- Escribir salida JSONL local.
- Reportar resumen deterministico.
- Tests focales verdes.
- Sin llamadas externas.
- Sin LLM.
- Sin runtime.
- Sin diagnostico final.

## Estado

Este documento permite evaluar el siguiente slice tecnico. No autoriza runtime productivo ni integraciones reales con marketplaces.
