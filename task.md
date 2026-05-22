# Task — Attachment/Evidence Lifecycle Contract

## Estado

Aprobado para implementación guiada por tests.

## Documentación obligatoria

Antes de modificar código se debe leer:

- `docs/hermes/principio-obligatorio-hermes-runtime-orchestrator.md`
- `docs/hermes/boundary-integracion-conversacional.md`
- `docs/hermes/autoaditoria-hermes-pipeline-minimo-accionable.md`

## Objetivo

Implementar un contrato de ciclo de vida de adjuntos/evidencia para que ningún adjunto recibido por Hermes desaparezca contractualmente antes de llegar a PymIA o antes de ser reconocido explícitamente ante el dueño del negocio.

## Principio central

Hermes no debe ser reducido a gateway ni adaptador pasivo. Hermes opera como runtime/orchestrator capaz: recibe conversación semántica, recibe documento computable, coordina parsing/cómputo, construye input rico y trazable para PymIA, espera output del kernel/core y comunica resultado fidedigno al dueño.

## Invariante obligatorio

Si hubo adjunto, el sistema nunca puede responder como si no hubiera adjunto.

## Contratos a crear

Archivo:

- `pymia/contracts/attachment_lifecycle_v1.py`

Contratos:

- `AttachmentLifecycleState`
- `AttachmentParseStatus`
- `AttachmentProcessingStatus`
- `EvidenceBundle`

## Contratos a modificar

- `pymia/interfaces/conversational_port.py`
  - agregar `evidence_bundle: EvidenceBundle | None` a `ConversationalInput`.
  - mantener `evidence: StructuredEvidence | None` por compatibilidad.

- `pymia/hermes/adapter.py`
  - agregar `evidence_bundle: EvidenceBundle | None` a `HermesInput` como wrapper transitorio.
  - pasar `evidence_bundle` hacia `ConversationalInput`.
  - si existe un adjunto parseado exitosamente con evidence y `evidence` legacy no existe, pasar esa evidence al campo legacy para compatibilidad.

- `pymia/services/initial_laboratory_anamnesis_service.py`
  - aceptar `evidence_bundle`.
  - bloquear fallback textual silencioso si hay adjuntos.
  - responder explícitamente `PARSE_FAILED`, archivo recibido no parseado, o parse exitoso.

- `conversa-engine/operational_audit_runner.py`
  - reemplazar resultado booleano pobre por resultado con `attachment_status`.
  - conservar `parse_error` interno/auditable.
  - exponer `root_cause` y `user_message` seguros.

- `conversa-engine/document_intake.py`
  - no absorber excepciones con `except Exception: audit_active = False`.
  - convertir fallos en `AttachmentProcessingStatus(parse_status="failed", lifecycle_state="PARSE_FAILED")`.
  - comunicar `user_message` seguro.

## Tests contractuales

Crear o extender tests para validar:

1. `StructuredEvidence` no contiene campos de lifecycle.
2. `AttachmentProcessingStatus` modela `PARSE_FAILED` sin `evidence` válida.
3. `EvidenceBundle` agrupa attachments.
4. `ConversationalInput` acepta `evidence_bundle`.
5. `HermesInput` wrapper pasa `evidence_bundle`.
6. `PARSE_SUCCEEDED` pasa `evidence` al port.
7. `PARSE_FAILED` genera respuesta explícita al usuario.
8. Excepción del parser se convierte en `parse_status="failed"` contractual.
9. `metadata` no transporta `parse_status`/`parse_error` como estado obligatorio.
10. Fallback textual queda bloqueado si `attachments` no está vacío.

## Antipatrones prohibidos

- Meter lifecycle en `StructuredEvidence`.
- Usar `metadata` opaca como transporte semántico obligatorio.
- Devolver `parse_error` técnico crudo al dueño.
- Absorber excepciones sin estado contractual.
- Formatter hacks.
- Ifs sobre texto libre para simular lifecycle.
- Responder pidiendo ventas/costos cuando ya hubo Excel.
- Tratar Hermes como gateway tonto.

## Criterios de aceptación

- Un adjunto recibido siempre queda representado por contrato.
- Un parse exitoso transporta `StructuredEvidence` al input del kernel/core.
- Un parse fallido transporta `PARSE_FAILED` y comunica causa segura al dueño.
- `StructuredEvidence` permanece limpio.
- `pytest -q` pasa.
- Ningún adjunto recibido puede desaparecer contractualmente.
