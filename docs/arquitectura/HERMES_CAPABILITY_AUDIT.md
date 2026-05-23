# HERMES CAPABILITY AUDIT — FASE 1

**Fecha:** 24 de mayo de 2026
**Fuente:** https://hermes-agent.nousresearch.com/docs/
**Estado:** VIGENTE
**Propósito:** radiografía real de Hermes Agent (Nous Research) para establecer la frontera exacta con PymIA.
**Relación con otros documentos:** deriva de `ONTOLOGIA_AGENTES_SISTEMA.md` y gobierna la integración en `pymia/hermes/adapter.py` y `conversa-engine/`.

---

## 1. Qué existe

Hermes Agent es un **agente autónomo open-source** construido por Nous Research. No es un chatbot ni un wrapper: es un runtime de agente completo.

**Componentes reales identificados:**

| Componente | Qué es | Ubicación |
|---|---|---|
| **`AIAgent`** (run_agent.py) | Orquestador central (~15k líneas). Ensambla prompts, despacha tools, maneja providers, failover, compresión, memory flush. | `run_agent.py` |
| **`prompt_builder.py`** | Ensambla system prompt: SOUL.md → tool guidance → memory/user → skills → context files → timestamp → plataformas. | `agent/prompt_builder.py` |
| **`ContextEngine`** (ABC) | Motor de contexto pluggeable; implementación default = compresor con summarización lossy. | `agent/context_engine.py`, `context_compressor.py` |
| **Gateway** | Proceso multiplataforma que rutea mensajes desde canales al agente. SQLite-backed state. | `hermes gateway` |
| **API Server** | Endpoint OpenAI-compatible (`/v1/chat/completions`, `/v1/responses`, `/v1/runs`). Permite usar Hermes como backend de cualquier frontend. | `API_SERVER_ENABLED=true` |
| **MCP client/server** | Se conecta a MCP servers externos (stdio/HTTP) **y** puede exponerse como MCP server (`hermes mcp serve`) para que otros agentes lo consuman. | `mcp_servers:` en config |
| **SQLite state.db** | Persistencia canónica: sesiones, mensajes, FTS5, session search. | `~/.hermes/state.db` |
| **Skill system** | Documentos SKILL.md con progressive disclosure, creados por el agente durante el uso. | `~/.hermes/skills/` |
| **Kanban + workers** | Task board multi-agente con lanes, dispatcher, reconciliación. | `kanban_*` |
| **Cron + Jobs API** | Scheduled work + CRUD remoto vía HTTP. | `hermes cron`, `/api/jobs` |

**Canales soportados (gateway):** cli, telegram, discord, slack, whatsapp, signal, matrix, mattermost, email, sms, dingtalk, feishu, wecom, weixin, bluebubbles, qqbot, homeassistant, webhook, api-server, acp, cron, batch. **20+ plataformas desde un solo gateway.**

**Terminal backends:** local, docker (persistent container), ssh, modal, daytona, vercel_sandbox, singularity. Cada uno con aislamiento, snapshots y credential forwarding propio.

---

## 2. Qué hace

**Ciclo de vida de un turno (turn lifecycle):**

```
run_conversation()
  1. Genera task_id
  2. Append user message
  3. Build/reuse cached system prompt
  4. Preflight compression si >50% context
  5. Build API messages (chat_completions | codex_responses | anthropic_messages)
  6. Inject ephemeral layers (budget warnings, context pressure)
  7. Prompt caching markers (Anthropic)
  8. Interruptible API call
  9. Parse:
     - tool_calls → execute → append → loop a (5)
     - text response → persist session → flush memory → return
```

**Tool execution:**
- Single call → main thread.
- Multiple calls → `ThreadPoolExecutor` concurrente (excepto `clarify` y tools interactivos).
- Agent-level tools interceptados antes del registry: `todo`, `memory`, `session_search`, `delegate_task`.

**Memory:**
- `MEMORY.md` (2.200 chars) + `USER.md` (1.375 chars). Frozen snapshot al inicio de sesión. Mutaciones persistidas a disco inmediatamente, visibles en prompt en próxima sesión.
- `session_search` con FTS5 sobre toda la historia (tres formas: discovery / scroll / browse).
- 8 memory providers externos pluggeables: Honcho, OpenViking, Mem0, Hindsight, Holographic, RetainDB, ByteRover, Supermemory.

**SOUL.md vs AGENTS.md vs `/personality`:**
- `SOUL.md` = identidad primaria, slot #1 del system prompt, vive en `HERMES_HOME`, estable.
- `AGENTS.md` = instrucciones de proyecto, jerárquico.
- `/personality` = overlay de sesión.

**Compression:**
- Preflight a 50% del context window.
- Gateway auto-compression a 85%.
- Memory flush previo, middle turns resumidos, últimos N mensajes intactos (`protect_last_n=20`), tool call/result pairs inseparables, nuevo session lineage ID.

**Delegation (subagentes):**
- `delegate_task` con budgets independientes (cap 50), max_spawn_depth 1-3, max_concurrent_children configurable.
- Provider/model override para routing a modelos baratos por subtarea.

**Interrupción:** `_interruptible_api_call()` en background thread, abandona respuesta si llega interrupción, sin inyectar parcial.

**Fallback providers:** cadena por 429/5xx/401/403, con credential refresh antes de fallar. Auxiliares (vision, compression, web extract) tienen fallback chain independiente.

---

## 3. Qué input recibe

**Entry points documentados:**

```python
# Simple
response = agent.chat("Fix the bug in main.py")

# Full
result = agent.run_conversation(
    user_message="...",
    system_message=None,           # auto-built si omitido
    conversation_history=None,     # auto-loaded from session
    task_id="task_abc123"
)
```

**Entradas por canal (gateway):**

| Canal | Formato de entrada | Session key |
|---|---|---|
| CLI | texto directo | sesión única |
| Telegram DM | texto + attachments + voice | `agent:main:telegram:dm:<chat_id>` |
| Telegram grupo/topic | texto, thread-aware | `agent:main:telegram:group:<chat_id>:<thread_id>` |
| Discord | texto, thread, @mention gating | por canal/thread con `group_sessions_per_user` |
| Slack | texto, `ts` como anchor | por thread |
| WhatsApp / Signal / Matrix | texto + attachments | DM por user; grupo con `user_id` si disponible |
| API server (`/v1/chat/completions`) | messages[] OpenAI format | stateless |
| API server (`/v1/responses`) | `input` + `previous_response_id` | stateful, chained |
| API server (`/v1/runs`) | `input` + `session_id` + `instructions` | SSE progress events |

**Attachments (scope por turno):**
- Imágenes: nativas o pre-analizadas a texto si el modelo no soporta vision.
- Audio: transcrito a texto si STT está configurado.
- Documentos: texto extraído incluido; otros tipos representados por path + nota.
- **No se re-envían bytes crudos en futuros prompts.** Solo lo escrito en el transcript sobrevive.

**Payloads programáticos (para integración PymIA):**
- `HermesInput` en PymIA mapea naturalmente a `HermesPayload` vía adapter.
- API server acepta `Bearer` auth, `Idempotency-Key` (cache 5 min), CORS opt-in.
- Runs API: `POST /v1/runs` → `run_id`, `GET /v1/runs/{id}/events` (SSE), `POST /v1/runs/{id}/stop`.

**Context files inyectados (prompt stack):**
1. SOUL.md (identidad primaria)
2. Tool-aware behavior guidance
3. Memory/user context
4. Skills guidance
5. AGENTS.md, .cursorrules (proyecto)
6. Timestamp
7. Platform-specific hints
8. `/personality` overlays

---

## 4. Qué output produce

**Salidas por tipo:**

| Salida | Dónde va | Estructura |
|---|---|---|
| **Reply text** | Canal / API response | string, chunked si streaming |
| **Tool calls** | Ejecutados y anexados a historia | OpenAI format `role=tool` |
| **Memory mutations** | `MEMORY.md` / `USER.md` disco | acciones: add / replace / remove |
| **Session state** | `~/.hermes/state.db` (WAL mode) | messages, metadata, FTS5 |
| **Progress events** | SSE (`hermes.tool.progress`) o callback | `tool_progress_callback`, `stream_delta_callback` |
| **Reasoning content** | `assistant_msg["reasoning"]` | opcional, vía `reasoning_callback` |
| **Payload programático** | `HermesOutput.payload` | `progressive_context`, `anamnesis`, `laboratorio`, `input_metadata` |
| **Run status** | `/v1/runs/{id}` | `started` / `running` / `completed` / `failed` / `cancelled` |
| **Job events** | `/api/jobs` CRUD + `/api/jobs/{id}/run` | scheduled background work |

**Callbacks disponibles para integraciones (clave para PymIA):**

| Callback | Disparo | Uso |
|---|---|---|
| `tool_progress_callback` | antes/después de cada tool | spinner CLI, progress en gateway |
| `thinking_callback` | inicio/fin de thinking | indicador "thinking..." |
| `reasoning_callback` | reasoning content | bloques de razonamiento |
| `clarify_callback` | `clarify` tool | input prompt interactivo |
| `step_callback` | fin de turno completo | step tracking ACP/gateway |
| `stream_delta_callback` | cada token streaming | display en vivo |
| `tool_gen_callback` | tool call parseado | preview en spinner |
| `status_callback` | cambio de estado | updates ACP |

**Mensajes alternation rules (no romper):**
- Nunca dos `assistant` consecutivos.
- Nunca dos `user` consecutivos.
- Solo `role=tool` admite entradas consecutivas (resultados paralelos).

---

## 5. Qué parte depende de PymIA

Hermes **no hace diagnóstico clínico-operacional** de PyMEs. Lo que PymIA debe proveer a Hermes vía `pymia/hermes/adapter.py`:

| Responsabilidad | Dueño | Contrato PymIA |
|---|---|---|
| **Clasificación taxonómica** (rubro/naturaleza PyME) | PymIA | `ProgressiveBusinessIdentity` |
| **Detección de síntoma** (semántica, no keyword) | PymIA | `symptom_summary` |
| **Anamnesis clínica inicial** | PymIA | `initial_laboratory_anamnesis_service` |
| **Contexto clínico progresivo** | PymIA | `ProgressiveTenantClinicalContext` |
| **Pedido de evidencia** (ventas, costos, precios, caja) | PymIA | `documents_requested` |
| **Document Intelligence** (schema inference, validación matemática) | PymIA | `SchemaInferenceEngine`, Polars |
| **Análisis / hallazgos** | PymIA | `DiagnosticReport`, hallazgos con entidad/número/diferencia/fuente |
| **Transporte roundtrip** de contexto | Hermes (adapter) | `HermesInput.previous_progressive_context` / `HermesPayload.progressive_context` |
| **Persistencia de sesión** (canal) | Hermes | `state.db` + `progressive_context_sessions.json` |
| **Orquestación conversacional** | Hermes | `AIAgent`, `prompt_builder`, callbacks |
| **Delivery a canal** (Telegram, Discord, etc.) | Hermes | gateway + adapters |
| **Memoria de usuario global** (USER.md) | Hermes | `memory` tool |
| **Memory clínica específica por tenant** | PymIA | aún no construida (gap) |

**Frontera dura (regla soberana):**
- Hermes **nunca** interpreta Excel, PDF o hallazgos.
- Hermes **nunca** decide qué evidencia pedir sin preguntar al kernel PymIA.
- Hermes **nunca** diagnostica. Solo transporta lo que PymIA produce.

**Mecanismo de integración recomendado:** Hermes como MCP **client** que conecta a un MCP **server** de PymIA, o bien API server de Hermes consumido por un orquestador PymIA vía `/v1/responses` con `previous_response_id`.

---

## 6. Qué riesgos tiene

| # | Riesgo | Impacto | Mitigación |
|---|---|---|---|
| R1 | **Hermes diagnostica por su cuenta** si se le pasa system prompt clínico sin pasar por PymIA. | Alto — viola `ONTOLOGIA_AGENTES_SISTEMA.md`. | SOUL.md explícito: "no diagnostiques PyMEs, delegá a PymIA". Tool `pymia_diagnose` obligatoria para cualquier output clínico. |
| R2 | **Compresión borra contexto clínico progresivo** si el kernel no persiste `progressive_context` antes del flush. | Alto — pierde FASE_0 taxonomía. | Memory flush hook: PymIA expone endpoint que Hermes llama antes de comprimir. |
| R3 | **`channel="telegram"` hardcodeado** en `conversa-engine/main.py` rompe multi-canal. | Medio — impide WhatsApp/API. | Inferir `channel` de metadata del gateway. |
| R4 | **Session ID collision** si no se usa `tenant_id/user_id` estricto. | Alto — contaminación cross-tenant. | Mantener `_session_id(tenant_id, user_id)` como única fuente. |
| R5 | **MCP sampling runaway**: server MCP externo pide LLM sin rate limit → costo. | Medio. | `sampling.max_rpm`, `max_tool_rounds`, `max_tokens_cap` en config. |
| R6 | **`MEMORY.md`/`USER.md` mezclan memoria clínica con memoria global de Hermes**. | Alto — ruido en prompts. | Separar: USER.md = dueño humano; memoria PyME = contrato PymIA (`ProgressiveTenantClinicalContext`). |
| R7 | **`object.__setattr__` en `RawInboundEvent`** bypasea dataclass frozen. | Medio — rompe serialización. | Agregar campos formales al dataclass. |
| R8 | **Silenciamiento `except Exception: audit_active = False`** en `document_intake.py`. | Alto — oculta fallos. | Error tipado + logging. |
| R9 | **Hermes como MCP server** expone 10 tools de mensajería. Si PymIA no filtra, cualquier agente externo puede enviar mensajes en nombre del dueño. | Crítico. | `tools.include` whitelist estricta cuando Hermes actúa como server. |
| R10 | **Auto-titling de sesiones con LLM auxiliar** puede filtrar datos del dueño a providers no auditados. | Medio. | `auxiliary.titling.provider` apuntando a modelo local o Nous Portal auditado. |
| R11 | **Session lineage por compresión** puede romper `session_id` estable si PymIA cachea por ID viejo. | Medio. | PymIA debe cachear por `tenant_id/user_id`, nunca por `session_id` de Hermes. |
| R12 | **Fallback provider swap** puede mover datos clínicos a provider no autorizado (p. ej. fallback a endpoint público). | Crítico. | `fallback_providers` whitelist explícita, nunca default abierto. |

---

## 7. Qué capacidad está subutilizada

| Capacidad de Hermes | Uso actual en PymIA | Oportunidad concreta |
|---|---|---|
| **`/v1/runs` SSE API** | No se usa. `main.py` llama adapter sincrónico. | Dashboard clínico web podría suscribirse a `GET /v1/runs/{id}/events` para mostrar progreso de anamnesis en tiempo real. |
| **MCP server mode (`hermes mcp serve`)** | No se usa. | Exponer Hermes como MCP server permitiría que PymIA (u otros agentes clínicos) lean y envíen mensajes a Telegram/Discord sin acoplarse al gateway. |
| **`delegate_task` con subagentes** | No se usa. | Subagente especializado en `evidence_validation`, `taxonomic_classification`, `report_generation` con modelo barato. |
| **`session_search` FTS5** | No se usa. | PymIA podría buscar síntomas/hallazgos históricos cross-session para detectar patrones PyME recurrentes. |
| **Skills system** | No se usa. | Crear skills por industria: `skill-distribuidora-alimentos`, `skill-gastronomica`, con catálogos y fórmulas específicas. |
| **Kanban multi-agente** | No se usa. | Lane `anamnesis`, lane `evidence`, lane `diagnosis`, lane `action_plan` para pipelines clínicos paralelos. |
| **Memory providers (Honcho)** | No se usa. | Modelado dialéctico del dueño PyME a través de sesiones, multi-perfil. |
| **Cron + Jobs API** | No se usa. | Recordatorios de evidencia pendiente, re-checks de hallazgos no tratados, reportes periódicos de estabilización. |
| **API server multi-profile** | No se usa. | Un Hermes por PyME cliente con memoria, skills y SOUL.md aislados. |
| **Auxiliary models** (compression, vision, web) | No se usa. | Visión para PDFs escaneados de facturas; compression barata con `gemini-3-flash`; web search para benchmarks de mercado. |
| **Smart approvals** | No se usa. | Aprobación del dueño antes de emitir diagnóstico de alto impacto (p. ej. "cerrar línea de producto"). |
| **Context files jerárquicos** (`.hermes.md`) | No se usa. | `.hermes.md` por PyME en workspace del dueño con industria, escala, idioma. |
| **Worktree isolation** | No se usa. | Agentes paralelos por cliente sin colisión de archivos. |
| **Tool output truncation (`tool_output.max_bytes`)** | Default. | Ajustar para modelos de contexto grande en análisis de evidencia tabular. |
| **Streaming con progress (`hermes.tool.progress`)** | No se usa. | Frontends clínicos podrían mostrar "analizando ventas..." en vivo. |
| **Checkpoint & rollback** | No se usa. | Snapshot antes de emitir plan de acción destructivo (p. ej. reestructuración). |

---

## Frontera recomendada (próximo paso lógico)

**Hito:** definir el protocolo exacto por el cual PymIA consume a Hermes.

**Tres opciones concretas (elegir UNA antes de implementar):**

1. **Hermes como MCP client de PymIA MCP server** — PymIA expone tools clínicos (`taxonomic_classify`, `evidence_request`, `diagnose`), Hermes los llama durante el turno.
2. **PymIA como MCP client de Hermes MCP server** — PymIA orquesta, usa Hermes para delivery a canal vía `messages_send`.
3. **PymIA consume API server de Hermes (`/v1/responses`)** — estado server-side con `previous_response_id`, PymIA inyecta system prompt clínico.

**Criterio de decisión:**
- Si PymIA es el soberano → opción 1.
- Si Hermes es el orquestador conversacional con PymIA como tool → opción 2.
- Si PymIA es un frontend más del Hermes agent → opción 3.

La ontología vigente (`ONTOLOGIA_AGENTES_SISTEMA.md`) indica que la opción **1** es la coherente: PymIA es inteligencia computacional, Hermes es organismo operativo.

---

## Historial de versiones

| Fecha | Versión | Cambio |
|---|---|---|
| 2026-05-24 | v1.0 | Radiografía inicial basada en docs oficiales. |
