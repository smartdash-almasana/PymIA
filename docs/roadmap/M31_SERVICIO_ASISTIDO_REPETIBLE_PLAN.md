# M31 — Servicio asistido repetible Plan

## Estado

PLAN_DRAFT

## Contexto

M27 cerró: mensaje del dueño + Excel controlado -> IntakeRecord -> evidence gate -> READY_FOR_ANALYSIS.

M28 cerró: ActionableFinding[] -> NarrativeReport grounded -> markdown legible/auditable.

M29 cerró: owner_message + evidence_refs + ActionableFinding[] -> Markdown mínimo entregable.

M30 cerró: continuidad mínima del caso asistido por tenant.

M31 debe convertir estos slices en un protocolo operativo repetible para primeros casos reales, todavía sin llamarlo producto.

## Objetivo

Definir y validar un protocolo de servicio asistido repetible con:

- criterio de entrada;
- criterio de bloqueo;
- checklist de entrega;
- plantilla de intake;
- plantilla de reporte;
- medición de tiempo/costo por caso;
- registro de bloqueos y aprendizajes.

## No producto

M31 no declara producto final.
M31 no declara autonomía end-to-end.
M31 no declara servicio comercial validado.

Sólo prepara un protocolo para ejecutar 3 a 5 casos piloto con trazabilidad.

## Alcance permitido

- documentación operativa;
- checklist reproducible;
- plantilla de intake;
- plantilla de entrega;
- registro de pilotos;
- tests documentales si existen patrones en el repo;
- sin código productivo nuevo.

## Fuera de alcance

- registry/capabilities.yaml;
- dispatcher;
- plugins;
- Telegram/PDF/HTML/UI;
- CI;
- ERP/Odoo/Dolibarr;
- LLM/red;
- producto final;
- pricing definitivo;
- landing;
- automatización comercial.

## Artefactos sugeridos

- docs/smartpyme/M31_SERVICIO_ASISTIDO_REPETIBLE_PROTOCOL.md
- docs/smartpyme/M31_SERVICIO_ASISTIDO_REPETIBLE_CHECKPOINT.md
- tests/smartpyme/test_m31_service_protocol_docs.py si hay patrón documental aceptado

## Protocolo mínimo esperado

Cada caso piloto debe registrar:

1. tenant/caso;
2. problema declarado;
3. evidencia recibida;
4. evidencia faltante;
5. hallazgos generados;
6. reporte entregado;
7. próximo paso sugerido;
8. tiempo real de preparación;
9. tiempo real de análisis;
10. tiempo real de entrega;
11. bloqueos encontrados;
12. aprendizaje para PymIA.

## Criterio PASS

M31 pasa si queda un protocolo operativo versionado y verificable para ejecutar primeros casos pilotos sin improvisar ni declarar producto.

## Criterio BLOCKED

Bloquear si para repetir el servicio hace falta abrir producto, UI, PDF profesional, dispatcher, ERP, LLM, registry o promesa comercial no validada.
