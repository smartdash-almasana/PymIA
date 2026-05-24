# HERMES Runtime Source Audit for PymIA

## Estado
PASS

## Fecha
2026-05-23

## Propósito
Registrar hallazgos de auditoría de código fuente runtime de Hermes (modo observacional/read-only) para orientar decisiones posteriores.  
Este documento no autoriza cambios productivos ni promoción a MCP-3.

## Fuente
Reporte provisto en este ciclo: bloque “HERMES RUNTIME SOURCE AUDIT: PASS” y secciones asociadas (`SYNC`, `ENTORNO`, `HERMES SOURCE`, `MCP RUNTIME`, `TOOL REGISTRY`, `AIAGENT / RUN LOOP`, `GATEWAY`, `SESSION STORAGE`, `CONFIG / PROMPTS`, `RISKS FOR PYMIA`, `RECOMMENDATION`, `WORKTREE`).

## Entorno auditado (según reporte)
- path: `/opt/PymIA`
- branch: `main`
- commit: `5ad314a`
- worktree: clean (con `?? .antigravitycli/`)

## Alcance de módulos inspeccionados (según reporte)
- `/opt/PymIA/conversa-engine/.venv/lib/python3.11/site-packages/run_agent.py`
- `/opt/PymIA/conversa-engine/.venv/lib/python3.11/site-packages/model_tools.py`
- `/opt/PymIA/conversa-engine/.venv/lib/python3.11/site-packages/tools/registry.py`
- `/opt/PymIA/conversa-engine/.venv/lib/python3.11/site-packages/tools/mcp_tool.py`
- `/opt/PymIA/conversa-engine/.venv/lib/python3.11/site-packages/gateway/run.py`
- `/opt/PymIA/conversa-engine/.venv/lib/python3.11/site-packages/gateway/session.py`
- `/opt/PymIA/conversa-engine/.venv/lib/python3.11/site-packages/hermes_state.py`
- `/opt/PymIA/conversa-engine/.venv/lib/python3.11/site-packages/hermes_constants.py`
- `/opt/PymIA/conversa-engine/.venv/lib/python3.11/site-packages/hermes_cli/env_loader.py`

## Runtime Hermes observado
- version: Hermes Agent `v0.13.0` sobre Python `3.11.2`
- package path: `/opt/PymIA/conversa-engine/.venv/lib/python3.11/site-packages/`
- arquitectura observada: core conversacional (`AIAgent`), despachador de tools, registry global, cliente MCP integrado, gateway asíncrono y persistencia SQLite.

## Hallazgos técnicos observacionales

### MCP Runtime
- Carga `mcp_servers` vía `_load_mcp_config()`, con `load_config()` + dotenv e interpolación `${VAR_NAME}` mediante `_interpolate_env_vars()`.
- Filtrado de entorno para stdio mediante `_build_safe_env(user_env)` con allowlist `_SAFE_ENV_KEYS` (`PATH`, `HOME`, `USER`, `LANG`, `LC_ALL`, `TERM`, `SHELL`, `TMPDIR`) y prefijos `XDG_`.
- Discovery en `discover_mcp_tools()`, incluyendo refresco dinámico por `ToolListChangedNotification()`.
- Saneamiento de nombres con `sanitize_mcp_name_component()` (`re.sub(r"[^A-Za-z0-9_]", "_", value)`), exponiendo tools como `mcp_{safe_server_name}_{safe_tool_name}`.
- Include/Exclude aplicado en `_register_server_tools()` (prioridad de `include` sobre `exclude`).
- Invocación MCP mediada por LLM: `handle_function_call()` -> `registry.dispatch()` -> handler de `_make_tool_handler()` -> `session.call_tool()` asíncrono.
- Timeouts por defecto reportados: `120s` ejecución y `60s` conexión.
- Tolerancia a fallos: circuit breaker (3 fallos consecutivos, cooldown 60s) + reconexión exponencial.

### Tool Registry
- Singleton global mutable: `registry = ToolRegistry()` con diccionario `_tools`.
- Concurrencia: uso de `threading.RLock()` + contador `_generation`.
- Sin aislamiento per-instancia de `AIAgent`: todas las instancias comparten catálogo global.

### AIAgent / Run Loop
- Bucle principal en `run_conversation()` con presupuesto de iteraciones, ejecución de tool calls y retorno al LLM.
- Ruta directa programática existe (`registry.dispatch()`), pero no se reporta endpoint CLI de invocación directa de tools MCP para usuario final.
- Fail-closed parcial: guardrails para cortar loops repetitivos (`repeated_exact_failure_block`, `idempotent_no_progress_block`), pero errores generales dependen del comportamiento del LLM/prompt.

### Gateway
- `GatewayRunner` instancia agentes efímeros por evento/sesión en ejecución concurrente por hilos.
- Manejo de interrupciones vía `agent.interrupt()` y señalización global de interrupción.
- Cola FIFO por `session_key`; procesamiento secuencial por sesión y concurrente entre sesiones.
- Errores de tools se devuelven como observaciones JSON al LLM; fallos sostenidos de MCP activan circuit breaker.

### Session Storage
- `SessionDB` en SQLite `state.db`; intenta WAL con fallback a `journal_mode=DELETE` ante `locking protocol`.
- Escrituras con `BEGIN IMMEDIATE`, `timeout=1.0`, jitter (`20-150ms`) y hasta 15 reintentos.
- Riesgo reportado: bajo alta concurrencia puede agotarse retry y aparecer `database is locked`.

### Config / Prompts
- Resolución de `HERMES_HOME` vía `get_hermes_home()` con fallback a `~/.hermes` y warnings de desalineación de perfil.
- `config.yaml` en `${HERMES_HOME}/config.yaml`; `.env` en `${HERMES_HOME}/.env`.
- Carga/saneamiento de credenciales en `env_loader.py`, incluyendo sanitización ASCII y redacción de secretos en errores.
- `SOUL.md` cargado desde `${HERMES_HOME}/SOUL.md`; hints dinámicos adicionales vía `SubdirectoryHintTracker`.

## Riesgos para PymIA (según reporte)
1. Inyección/alucinación del LLM que derive en llamadas MCP clínicas con argumentos no esperados.
2. Exposición de herramientas de alto privilegio a canales públicos por falta de segregación estricta por canal en el registry global.
3. Dependencia fuerte en `SOUL.md` como barrera clínica susceptible a jailbreak.
4. Bloqueos de escritura recurrentes en `state.db` bajo concurrencia alta.
5. Contaminación cruzada de perfiles por propagación deficiente de `HERMES_HOME`.
6. Resiliencia semántica insuficiente ante indisponibilidad/circuit breaker MCP (bucles de repetición del LLM).

## Recomendación formal del reporte fuente
`NOT_READY_FOR_MCP3_NEEDS_HERMES_CONFIG_HARDENING_PLAN`

## Observación de límites
Este documento es de auditoría observacional y no autoriza:
- editar `~/.hermes`
- tocar `systemd`
- tocar `Telegram`
- tocar `.env`
- ejecutar cambios en producción
- habilitar nuevas tools
- promover MCP-3
