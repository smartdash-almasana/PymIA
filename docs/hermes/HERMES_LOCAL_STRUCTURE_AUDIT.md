# Hermes Local Structure Audit for PymIA

## Estado
LOCAL AUDIT PASS

## Fecha
2026-05-23

## Propósito
Registrar la estructura real de Hermes observada en VM antes de diseñar MCP-3. Este documento no autoriza cambios productivos.

## Entorno auditado
- path: `/opt/PymIA`
- branch: `main`
- commit: `46a9b17` (`docs(arquitectura): define MCP2 sandbox repeatability decision`)
- worktree: limpio y único

## Hermes local
- binario: `/opt/PymIA/conversa-engine/.venv/bin/hermes`
- versión: Hermes Agent `v0.13.0 (2026.5.7)` sobre Python `3.11.2`
- venv: `/opt/PymIA/conversa-engine/.venv` (reporte indica OpenAI SDK `2.24.0`)
- paquete/código instalado: no hay repo fuente Hermes dentro de PymIA; está instalado como paquete en `site-packages` (`hermes_cli`, `hermes_agent`, etc.)
- config productiva detectada: `/home/neoalmasana/.hermes/config.yaml` (`_config_version: 22`)
- config sandbox MCP-1: `/tmp/pymia-mcp1-gateway-sandbox/hermes-home/config.yaml` (`_config_version: 22`)
- config sandbox MCP-2: `/tmp/pymia-mcp2-repeatability/hermes-home/config.yaml` (`_config_version: 22`)
- HERMES_HOME productivo: `/home/neoalmasana/.hermes`
- HERMES_HOME sandbox: definido por variable de entorno en `/tmp/pymia-mcp1-gateway-sandbox/hermes-home` y `/tmp/pymia-mcp2-repeatability/hermes-home`
- logs observados: `/home/neoalmasana/.hermes/logs/` con `gateway.log`, `agent.log`, `mcp-stderr.log`, `errors.log`
- sessions observadas: `/home/neoalmasana/.hermes/sessions/` + `state.db` SQLite
- prompts/SOUL:
  - productivo: `~/.hermes/SOUL.md` con personalidad default Nous
  - repo PymIA: `/opt/PymIA/docs/hermes/soul.md` con directiva clínica/operativa de PymIA

## Componentes observados
- CLI: disponible y ejecutable en venv.
- gateway: activo en despliegue user-level systemd según reporte.
- MCP client: discovery y ejecución de tool reportadas en sandbox MCP-1/MCP-2.
- systemd user units: detectadas en `/home/neoalmasana/.config/systemd/user/`.
- Telegram: canal activo en producción según reporte.
- sessions/logs: persistencia local en `~/.hermes` y SQLite.
- prompts: coexistencia de prompt productivo default y prompt PymIA en docs.
- providers/modelos: configuración con proveedor principal Gemini y fallbacks.
- secrets/.env: archivo `.env` en `HERMES_HOME`; copia a sandbox reportada en `/tmp`.

## Configuración observada
- `config.yaml` productivo observado en `~/.hermes/config.yaml`.
- `config.yaml` sandbox MCP-1 observado en `/tmp/pymia-mcp1-gateway-sandbox/hermes-home/config.yaml`.
- `config.yaml` sandbox MCP-2 observado en `/tmp/pymia-mcp2-repeatability/hermes-home/config.yaml`.
- `_config_version` observada: `22` en productivo y sandboxes.
- `mcp_servers`: reporte indica desalineación entre bridge legacy y servidor MCP real esperado.
- `toolsets`: reporte indica habilitación amplia de herramientas en Telegram.
- `providers`: reporte indica proveedor principal Gemini con fallo de clave y uso de fallbacks.
- `prompts`: reporte indica SOUL productivo default, distinto del SOUL clínico PymIA documentado.

## Mapa observado VM
| Tema | Estado observado | Gap | Riesgo | Recomendación observacional |
| :--- | :--- | :--- | :--- | :--- |
| HERMES_HOME | Producción en `~/.hermes`; sandboxes aislados en `/tmp/...` | Perfil productivo y de test dependen de disciplina operativa manual | Alto | Mantener separación explícita y auditable de perfiles en futuras etapas |
| config.yaml | `_config_version: 22` en producción y sandbox | Esquema reportado como obsoleto frente a referencia oficial mencionada | Medio | Verificar versión objetivo contra docs oficiales antes de MCP-3 |
| MCP servers | Producción reportada con bridge legacy; sandbox con servidor MCP real validado | Desalineación entre productivo y arquitectura MCP validada | Crítico | Diseñar transición documental previa, sin cambios en este ciclo |
| tools | Reporte indica toolset amplio en Telegram productivo | Falta restricción al set mínimo clínico | Crítico | Definir política de toolset mínimo antes de cualquier etapa pre-productiva |
| tool invocation | Sandbox validó invocación MCP real; histórico incluye fallo por stubs | Robustez depende de contrato MCP real y manejo de fallos | Medio | Conservar validación fail-closed como requisito |
| CLI oneshot | Disponible pero subutilizado según reporte | Falta estandarización de chequeos rápidos | Bajo | Evaluar su uso en auditorías no invasivas futuras |
| agent | Funciona con defaults y sin alineación completa de directivas | Subutilización de controles de contexto/compresión | Medio | Analizar settings tras cerrar auditoría oficial |
| gateway | Operativo por systemd user y canal activo | Estado legacy no alineado a sandbox MCP validado | Alto | Tratar como topología productiva separada, no tocar en este ciclo |
| runtime | Reporte menciona warning de entry point | Fragilidad de instalación/runtime | Medio | Confirmar estado del entorno con auditoría técnica dedicada |
| SOUL.md/prompts | SOUL productivo default; SOUL PymIA en docs del repo | Desacople entre comportamiento esperado y guía PymIA | Crítico | Resolver en diseño aprobado de etapas futuras, no ejecutar cambios ahora |
| sessions/logs | Persistencia activa en `~/.hermes` | Sin política observada de monitoreo/rotación robusta | Medio | Incluir gobernanza de logs en diseño previo a MCP-3 |
| providers/modelos | Proveedor principal Gemini con fallo de clave reportado | Dependencia de fallback con impacto operativo | Alto | Revalidar conectividad de proveedores en auditoría aprobada |
| secretos/.env | `.env` presente en producción y copiado a sandbox | Riesgo operativo por manejo en `/tmp` | Medio | Mantener política de no exposición y manejo mínimo de secretos |
| systemd | Unidades user-level detectadas para gateway y servicios relacionados | Convivencia con componentes legacy | Medio | Documentar topología antes de cualquier cambio aprobado |
| Telegram | Canal activo productivo | Posible exposición de jerga interna/acciones de alto riesgo | Alto | Mantener fuera de alcance hasta decisión explícita |
| producción | Entorno productivo reportado como legacy y frágil para integración inmediata | Brecha entre éxito sandbox y readiness productivo | Crítico | Mantener bloqueo de MCP-3 hasta auditorías y diseño aprobados |

## Recursos Hermes aprovechables para PymIA
- Perfiles/HERMES_HOME para aislamiento de estado.
- Gateway multicanal integrado.
- Gestión de contexto y compresión.
- Session search (FTS5) y memoria persistente.
- Jobs/Cron integrados.
- Fallback entre proveedores.
- MCP client integrado.

Nota: “Requiere confirmación con documentación oficial” para capacidades no verificadas en este documento con evidencia primaria local.

## Gaps observados
- Desalineación crítica de SOUL productivo vs prompt PymIA en repo.
- Ausencia del servidor MCP clínico real en configuración productiva reportada.
- Clave API de Gemini reportada como inválida.
- Exposición de herramientas de alto privilegio en Telegram reportada.
- Versión de configuración `v22` reportada como obsoleta frente a referencia oficial.
- Falta de mapeo explícito del prompt de canal Telegram reportada.
- Warning de entry point del binario Hermes en venv reportado.

## Riesgos observados
- Crítico: alucinación/diagnóstico autónomo sin boundary clínico correcto.
- Alto: contaminación de datos de producción por mal aislamiento de HERMES_HOME.
- Crítico: superficie de riesgo por herramientas de alto privilegio vía Telegram.
- Alto: degradación de experiencia por fuga de jerga interna.
- Alto: caída o degradación de canal principal por falla de proveedor principal.

## Recomendación local
Estado: `NOT_READY_FOR_MCP3`

Motivo:
- Antes de MCP-3 hace falta digest de documentación oficial Hermes.
- Hace falta auditoría de topología productiva con aprobación explícita.
- Hace falta diseño de cambios seguro sin tocar producción.

## Límites
Este documento no autoriza:
- editar `~/.hermes`
- tocar systemd
- tocar Telegram
- tocar `.env`
- promover MCP a productivo
- habilitar nuevas tools
