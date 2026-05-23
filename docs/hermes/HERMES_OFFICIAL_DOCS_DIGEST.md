# Hermes Official Docs Digest for PymIA

## Estado
RESEARCH DIGEST

## Fecha de consulta
23 de mayo de 2026

## Propósito
Este documento resume documentación oficial de Hermes relevante para PymIA. No es runbook de ejecución ni autorización productiva.

## Fuentes oficiales consultadas
| Fuente | URL | Secciones consultadas | Relevancia para PymIA |
| :--- | :--- | :--- | :--- |
| Documentación de Integración MCP | https://hermes-agent.nousresearch.com/docs/user-guide/features/mcp | Características de MCP, registro de herramientas y filtros | Diseño del cliente MCP integrado y sanitización de esquemas |
| Referencia de Comandos CLI | https://hermes-agent.nousresearch.com/docs/reference/cli-commands | Comandos globales, modos de ejecución y diagnóstico | Interfaz programática y opciones no interactivas |
| Referencia de Configuración MCP | https://hermes-agent.nousresearch.com/docs/reference/mcp-config-reference | Estructura de `mcp_servers`, políticas include/exclude y OAuth | Esquema de validación y sintaxis de filtros |
| Guía de Configuración Central | https://hermes-agent.nousresearch.com/docs/user-guide/configuration | `config.yaml`, variables y sandboxes | Backends de terminal y precedencia de configuración |
| Internos del Gateway | https://hermes-agent.nousresearch.com/docs/developer-guide/gateway-internals | GatewayRunner, adaptadores y colas | Procesamiento asíncrono y bloqueos de hilos de mensajería |
| Almacenamiento de Sesiones | https://hermes-agent.nousresearch.com/docs/developer-guide/session-storage | Esquema SQLite, mitigación de bloqueos y modo WAL | Modelo relacional de persistencia conversacional |
| Guía de Seguridad y Sandbox | https://hermes-agent.nousresearch.com/docs/user-guide/security | YOLO, aprobaciones de comandos y aislamiento | Filtros regex y lista negra dura de ejecución |

## Resumen ejecutivo
- Qué está claro:
  - Desacoplamiento avanzado entre inferencia del modelo y ejecución física de herramientas.
  - Seguridad por defecto con filtros de variables en subprocessos stdio y aislamiento en sandboxes.
  - Integración MCP nativa y asíncrona con transportes locales/remotos bajo políticas de inclusión/exclusión.
- Qué no está claro (NO ENCONTRADO EN DOC OFICIAL):
  - Comportamiento de concurrencia no controlada sobre `AIAgent` al instanciarlo como librería Python en hilos paralelos externos.
  - Sintaxis para invocar herramientas MCP directamente por CLI sin pasar por el LLM.
- Qué afecta una futura integración:
  - Persistencia SQLite + WAL exige control estricto de hilos de escritura para evitar `database is locked`.
  - Sanitización de nombres MCP (puntos/guiones a guiones bajos) requiere traductor de esquemas entre config e identificadores de llamada.

## Identidad y componentes Hermes
- Hermes se describe como ecosistema con agente conversacional + gateway persistente multiplataforma.
- Núcleo: clase `AIAgent` para bucle de pensamiento, tools, compresión de contexto y fallbacks de proveedores.
- Componentes operacionales:
  - CLI (`hermes`) para sesión local, one-shot y configuración.
  - Gateway daemon para adaptadores asíncronos de mensajería y tareas cron.
  - Runtime de tools/backends de terminal (local y sandboxes como Docker/Modal/SSH/Daytona/Vercel/Singularity).
- Versiones y referencias mencionadas en fuente:
  - esquema DB `11`
  - FastMCP `1.0.0`
  - Bitwarden Secrets Manager `2.0.0`
  - trazas de release como `v0.6.0`

## Instalación y layout
- Canales de instalación mencionados:
  - instalador rápido POSIX
  - `pip install` directo
  - Nix Flake
  - Termux
- Layout esperado bajo `HERMES_HOME`:
  - `config.yaml`
  - `.env`
  - `state.db`
  - `SOUL.md`
  - `skills/`
  - `cron/`
  - `logs/`
- Dependencias citadas por fuente:
  - base: Python 3.11+, Git, uv, ripgrep
  - web/mensajería: Node.js v22
  - audio/voz: ffmpeg, portaudio, espeak-ng, opus
  - termux/mobile: clang, rust, make, pkg-config, libffi, openssl

## CLI oficial
- Comandos principales:
  - `hermes chat`
  - `hermes model`
  - `hermes setup`
  - `hermes gateway`
  - `hermes config`
  - `hermes pairing`
- Modos no interactivos reportados:
  - `hermes -z "<prompt>"`
  - `hermes chat -q "<prompt>"`
- Diagnóstico:
  - `hermes doctor`
  - `hermes dump`
  - `hermes debug`
- Administración MCP vía CLI:
  - `hermes mcp add --preset`
  - `hermes mcp list`
  - `hermes mcp configure`
  - `hermes mcp test`
- Limitación citada:
  - En Windows nativo no hay soporte PTY para ciertos flujos de chat web.

## Configuración oficial
- `config.yaml`: variables no sensibles (modelos, puertos, terminales, compresión).
- `.env`: secretos (API keys, tokens, contraseñas).
- Interpolación `${VAR_NAME}` soportada en YAML.
- Ejemplos de bloques en fuente:
  - `model`
  - `auxiliary`

## HERMES_HOME y entorno
- `HERMES_HOME` opera como conmutador de perfil para aislar estado, sesiones, DB y configuración.
- Fuente menciona integración NixOS con `HERMES_HOME` global.
- Variables adicionales citadas:
  - `HERMES_DEV`
  - `HERMES_YOLO_MODE`

## Providers y modelos
- Soporte para formatos propietarios y genéricos (`chat_completions`).
- Proveedores mencionados: Anthropic, OpenAI Codex, OpenRouter, DeepSeek, Gemini, Azure, Bedrock, Ollama.
- Requisito crítico citado: soporte formal de function-calling para tools.

## MCP client y tools
- Config bajo `mcp_servers` en `config.yaml` para stdio y HTTP.
- Controles de seguridad reportados:
  - allowlist de variables heredadas en subprocessos stdio
  - OAuth 2.1 PKCE para servidores remotos
  - tokens en `~/.hermes/mcp-tokens/<server_name>.json`

## Tool discovery e invocation
- Descubrimiento en inicialización mediante `discover_mcp_tools()`.
- Reglas reportadas:
  - idempotencia de conexión
  - include/exclude de tools
  - bypass con `enabled: false`
- Invocación MCP mediada por el LLM (`AIAgent`).
- Invocación directa de tool MCP por CLI sin LLM: NO ENCONTRADO EN DOC OFICIAL.
- Fallos y tolerancia citados:
  - reconexión exponencial (hasta 5 reintentos)
  - manejo de `ImportError` para transporte HTTP faltante
  - `timeout` y `connect_timeout` configurables

## Agent / Gateway / Runtime
- La fuente describe desacoplamiento asíncrono entre motor conversacional y adaptadores físicos.
- Se enfatiza control del formato de historial conversacional y orden de roles para evitar inconsistencias.

## Prompts / system instructions / SOUL
- Capas documentadas:
  - `SOUL.md` (identidad global)
  - `AGENTS.md` (directrices técnicas de repo)
  - `/personality` (override efímero por sesión)
- Descubrimiento progresivo local citado mediante `SubdirectoryHintTracker` (hasta 5 niveles).

## Sessions y logs
- Persistencia en `state.db` con tablas:
  - `sessions`
  - `messages`
  - `messages_fts`
  - `messages_fts_trigram`
- Logs:
  - `agent.log`
  - `gateway.log`
  - `errors.log`

## Secrets y seguridad
- `approvals.mode` citado con variantes:
  - `manual`
  - `smart`
  - `off`
- Lista dura de bloqueo reportada para comandos destructivos extremos.
- Aislamiento físico citado mediante sandboxes de contenedores y políticas restrictivas.
- Integración Bitwarden (BWS) citada con carga remota y scrubbing preventivo de variables sensibles.

## Deployment / producción / systemd
- Fuente cita despliegue persistente vía `hermes gateway install` con systemd/launchd.
- También cita reinicio de sesiones interrumpidas y circuit breakers de plataforma.
- Capacidades de escalamiento distribuido multi-nodo con SQLite distribuida: NO ENCONTRADO EN DOC OFICIAL.

## Telegram y canales
- Soporte multicanal nativo documentado.
- Se menciona integración avanzada de Telegram con Bot API local para cargas grandes en entorno local.
- También se listan otros canales (Discord, Slack, Teams, Mattermost, Matrix, LINE, Signal, WhatsApp, SMS, Email, etc.).

## Tabla de capacidades Hermes para PymIA (síntesis)
- Ejecución asíncrona de `AIAgent`: útil, requiere auditoría de concurrencia antes de integración productiva.
- Aislamiento en Docker sandbox: útil en sandbox; requiere controles estrictos.
- Handshake MCP client: usable con directivas de filtrado de variables.
- `SOUL.md` de identidad: usable como baseline de comportamiento.
- Local Telegram Bot API: limitar a sandbox.
- Persistencia SQLite: requiere auditoría adicional por bloqueo/latencia.
- Bitwarden (BWS): opción más segura que secretos en texto plano local.

## Gaps documentales
- Thread-safety del core para importaciones puras Python y paralelismo de `AIAgent`: NO ENCONTRADO EN DOC OFICIAL.
- Ejecución directa no interactiva de tools MCP sin LLM: NO ENCONTRADO EN DOC OFICIAL.
- Triggers de sincronización FTS5 para cambios complejos: NO ENCONTRADO EN DOC OFICIAL.
- Alta disponibilidad horizontal del gateway con SQLite distribuida: NO ENCONTRADO EN DOC OFICIAL.

## Riesgos para PymIA
- Latencia por bloqueos SQLite en alta concurrencia.
- Riesgo de bypass de seguridad en sandboxes de consola mal aislados.
- Agotamiento de tokens/costos por inyección progresiva de directivas locales.

## Recomendaciones para PymIA
### Aprovechar ahora
- `SOUL.md` como baseline de identidad.
- Gestión remota de secretos con Bitwarden (BWS).

### Aprovechar solo en sandbox
- Bot API local de Telegram para pruebas de carga.
- Backend de terminal local solo en desarrollo no crítico.

### Auditar antes de integración productiva
- Concurrencia/latencia de `SessionDB` en stress.
- Traductor de esquemas para identificadores MCP (puntos/guiones -> guión bajo).

### No usar todavía
- Runtimes de consola en Windows nativo para escenarios PTY críticos.
- Aprobación automática de comandos en producción compartida.

## Impacto sobre MCP-3
Conclusión formal:

`NOT_READY_FOR_MCP3_NEEDS_RUNTIME_SOURCE_AUDIT`

El digest indica que persisten zonas ciegas críticas y sugiere auditoría directa de código fuente runtime (`tools/mcp_tool.py`, `registry.py`, `run_agent.py`) antes de cualquier autorización productiva.

## Apéndice: URLs oficiales y notas
- Portal técnico: https://hermes-agent.nousresearch.com
- Referencia MCP: https://modelcontextprotocol.io
- Código fuente de integración de mensajería (ruta reportada): https://github.com/NousResearch/hermes-agent/tree/main/website
- Documento de seguridad reportado: https://github.com/NousResearch/hermes-agent/blob/main/website/docs/user-guide/security.md

Nota de mantenimiento indicada en fuente:
mapear identificadores estructurados de consulta con firmas de confirmación Git del código base Hermes para coherencia temporal ante cambios de APIs.

## Límite explícito
Este documento es únicamente un digest de investigación y no autoriza ejecución productiva, promoción a MCP-3 ni cambios operativos sobre entornos vivos.
