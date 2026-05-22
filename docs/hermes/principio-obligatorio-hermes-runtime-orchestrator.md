# Principio obligatorio — Hermes como runtime/orchestrator capaz

**Estado:** obligatorio  
**Ámbito:** integración Hermes ↔ PymIA  
**Fecha:** 2026-05-22

---

## Decisión

Hermes no debe ser reducido a gateway pasivo ni a simple adaptador de texto.

Hermes debe funcionar a su máxima capacidad como runtime/orchestrator conversacional y computacional.

Debe poder:

```text
1. Recibir conversación semántica del dueño del negocio.
2. Recibir documentos computables adjuntos.
3. Ejecutar o coordinar parsing, curaduría y cómputo documental.
4. Construir un input rico, trazable y contractual para PymIA.
5. Esperar el proceso de cómputo del kernel/core operacional.
6. Extraer del output resultados estructurados.
7. Comunicar al dueño una respuesta fidedigna al estado real del proceso.
```

---

## Arquitectura objetivo

No se acepta esta arquitectura como destino final:

```text
Hermes → texto plano → PymIA
```

La arquitectura objetivo es:

```text
Hermes runtime/orchestrator
→ PymIAIngressEnvelope
   ├─ owner_semantics
   ├─ computable_documents
   ├─ evidence_bundle
   ├─ execution_status
   └─ trace
→ PymIA kernel / operational core
→ structured output
→ Hermes comunica fidedignamente al dueño
```

---

## Regla rectora

```text
Hermes conversa, computa, orquesta y entrega contexto rico.
PymIA recibe contrato claro, procesa evidencia y devuelve resultado operacional trazable.
```

El riesgo arquitectónico no es que Hermes haga demasiado.

El riesgo es que Hermes haga trabajo útil y que PymIA no lo reciba contractualmente.

---

## Invariante de adjuntos

```text
Si hubo adjunto, el sistema nunca puede responder como si no hubiera adjunto.
```

Por lo tanto:

```text
- Si el adjunto fue recibido pero no parseado, se informa ese estado.
- Si el parseo falló, se informa explícitamente el fallo al dueño.
- Si el parseo fue exitoso, la evidencia computable debe llegar al input del kernel o fallar contractualmente.
- No se permite degradar silenciosamente un documento computable a narrativa textual.
- No se permite ocultar fallos de parseo detrás de fallback conversacional.
```

---

## Separación contractual obligatoria

### StructuredEvidence

`StructuredEvidence` representa evidencia estructurada válida o parcialmente curada.

Puede contener:

```text
- tablas;
- columnas;
- filas;
- variables calculadas;
- metadata de curación documental.
```

No debe contener como responsabilidad primaria:

```text
- lifecycle_state;
- parse_status;
- parse_error;
- estado de ACK;
- fallback policy.
```

### AttachmentProcessingStatus

El ciclo de vida del adjunto debe vivir en un contrato separado:

```text
AttachmentProcessingStatus
  - attachment_id
  - file_name
  - mime_type
  - source_channel
  - lifecycle_state
  - parse_status
  - parse_error
  - root_cause
  - user_message
  - parser_name
  - evidence: StructuredEvidence | None
```

Regla:

```text
PARSE_SUCCEEDED → puede contener StructuredEvidence.
PARSE_FAILED → no debe fingir StructuredEvidence válida.
```

### EvidenceBundle / PymIAIngressEnvelope

La entrada soberana hacia PymIA debe poder transportar simultáneamente:

```text
- semántica conversacional del dueño;
- adjuntos computables;
- estados de procesamiento;
- evidencia estructurada;
- trazabilidad mínima.
```

Contrato objetivo:

```text
PymIAIngressEnvelope
  - tenant_id
  - channel
  - text / owner_semantics
  - evidence_bundle
```

Donde:

```text
EvidenceBundle
  - attachments: list[AttachmentProcessingStatus]
```

`metadata` de canal puede preservarse para trazabilidad, pero no puede transportar estado semántico obligatorio.

---

## Estados mínimos del lifecycle

```text
RECEIVED
DOWNLOADED
PARSE_ATTEMPTED
PARSE_FAILED
PARSE_SUCCEEDED
PASSED_TO_PORT
ACKNOWLEDGED_TO_USER
```

Estos estados deben ser observables por contrato o test, no inferidos por texto libre.

---

## Comunicación al dueño

La respuesta al dueño debe ser fiel al estado real del proceso.

Si el Excel falla:

```text
Recibí el Excel, pero no pude procesarlo correctamente.
Causa: <causa segura y accionable>.
```

No se acepta responder como si el archivo nunca hubiera sido recibido.

---

## Prohibiciones

No se debe:

```text
- reducir Hermes a gateway tonto;
- degradar documentos computables a narrativa textual;
- ocultar fallos de parseo;
- absorber excepciones sin estado contractual;
- usar metadata opaca como transporte semántico obligatorio;
- meter lifecycle dentro de StructuredEvidence;
- implementar formatter hacks;
- responder como si faltara archivo cuando hubo adjunto.
```

---

## Criterio de aceptación

La integración Hermes ↔ PymIA será aceptable sólo si:

```text
1. Hermes conserva su capacidad de orquestar conversación + documento computable.
2. PymIA recibe input contractual rico y trazable.
3. El kernel/core procesa evidencia real, no narrativa inventada.
4. El output comunica fielmente éxito, fallo o estado pendiente.
5. Ningún adjunto desaparece silenciosamente del flujo.
```
