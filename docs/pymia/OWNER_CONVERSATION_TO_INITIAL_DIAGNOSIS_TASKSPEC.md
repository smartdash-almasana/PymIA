# Owner Conversation to Initial Diagnosis TaskSpec

## Estado

**CANDIDATO_OPERATIVO**

**Fecha:** 2026-06-13

## Objetivo

Definir el flujo mínimo para convertir una conversación inicial del dueño PyME en un diagnóstico inicial candidato, sin diagnóstico final, sin runtime nuevo y sin saltar evidencia.

## Alcance

Este frente cubre:

- mensaje inicial del dueño,
- apertura de caso,
- comprensión semántica candidata,
- repregunta mínima,
- pedido de evidencia,
- bloqueo accionable,
- diagnóstico inicial candidato P1,
- reingreso al dueño.

No cubre:

- Telegram,
- Hermes productivo,
- FastAPI,
- PDF,
- delivery externo,
- FormulaPack,
- pronóstico implementado,
- cambios en DiagnosticCoreV1,
- diagnóstico final.

## Entrada mínima

```text
owner_message
tenant_id
cliente_id opcional
case_id opcional
attachments opcionales
progressive_context opcional
```

## Salidas permitidas

| Output | Cuándo |
|---|---|
| `context_request` | falta dato básico del caso |
| `evidence_request` | falta evidencia material |
| `blocked_actionable` | no puede avanzar, pero puede pedir algo concreto |
| `initial_diagnosis_candidate` | hay comprensión inicial suficiente, no final |
| `owner_reentry_question` | el dueño debe confirmar/corregir/aportar |

## Estados operativos

| Estado | Significado |
|---|---|
| `OWNER_MESSAGE_RECEIVED` | Se recibió relato inicial |
| `CASE_CONTEXT_OPENED` | Se abrió contexto mínimo de caso |
| `SEMANTIC_HYPOTHESIS_CANDIDATE` | Hay lectura candidata del problema |
| `NEEDS_OWNER_CLARIFICATION` | Falta sentido operativo |
| `NEEDS_EVIDENCE` | Falta evidencia material |
| `BLOCKED_ACTIONABLE` | Bloqueo con pedido concreto |
| `INITIAL_DIAGNOSIS_CANDIDATE` | Diagnóstico inicial pre-core, no final |
| `OWNER_REENTRY_PENDING` | Espera respuesta del dueño |

## Flujo mínimo

```text
owner_message
  → normalize/record
  → identify declared pain
  → create semantic hypothesis candidate
  → check minimal case context
  → check available evidence
  → if context missing: ask clarification
  → if evidence missing: blocked_actionable/evidence_request
  → if enough for P1: initial_diagnosis_candidate
  → ask owner to confirm/correct/attach evidence
```

## Reglas de diagnóstico inicial

Un diagnóstico inicial candidato puede decir:

- qué problema parece estar declarando el dueño,
- qué área operativa parece afectada,
- qué evidencia falta,
- qué riesgo preliminar existe,
- qué próximo dato permitiría avanzar.

No puede decir:

- diagnóstico final,
- patología confirmada,
- conclusión financiera definitiva,
- recomendación ejecutiva automática,
- pronóstico como certeza,
- acción autorizada.

## Preguntas permitidas

La conversación puede preguntar sólo lo necesario para avanzar:

| Falta | Pregunta permitida |
|---|---|
| rubro | ¿A qué se dedica la empresa? |
| período | ¿De qué período estamos hablando? |
| evidencia | ¿Tenés ventas, costos, caja, stock o algún Excel del período? |
| dolor operativo | ¿El problema principal está en caja, ventas, costos, stock, cobros o margen? |
| confirmación | ¿Esto describe correctamente lo que querés revisar? |

## Criterios fail-closed

Debe bloquear si:

- no hay rubro ni contexto mínimo,
- no hay período,
- no hay evidencia para fórmulas,
- el relato es ambiguo,
- la evidencia contradice el relato,
- el dueño no confirma una interpretación crítica,
- la salida podría sonar a diagnóstico final.

## Relación con AAAS

Este TaskSpec operacionaliza el primer tramo del AAAS:

```text
Dueño conversa → agente ordena → PymIA pide evidencia → P1 genera diagnóstico inicial candidato
```

## Relación con P1

P1 es la frontera de diagnóstico inicial pre-core.

Este flujo alimenta P1, pero no lo convierte en core ni en owner-facing report post-core.

## Relación con owner-decision

Una respuesta del dueño puede confirmar, corregir, aportar evidencia o autorizar una acción.

Estas respuestas no son equivalentes.

Este frente no crea DecisionRecord automático.

## Criterios de aceptación documental

- El flujo no abre runtime.
- El flujo no modifica código.
- El flujo no autoriza diagnóstico final.
- El flujo separa aclaración, evidencia y autorización.
- El flujo respeta P1, AAAS, ADR-018, ADR-024 y ADR-025.

## Próximo paso técnico futuro

Sólo después de auditar este TaskSpec:

```text
OWNER_CONVERSATION_TO_INITIAL_DIAGNOSIS_MODULECONTRACT.md
```

## Veredicto

```text
OWNER_CONVERSATION_TO_INITIAL_DIAGNOSIS_TASKSPEC_DEFINED
```
