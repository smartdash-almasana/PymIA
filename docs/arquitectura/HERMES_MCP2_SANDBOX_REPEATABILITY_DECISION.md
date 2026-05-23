# HERMES MCP-2 — Sandbox Repeatability Decision

## Estado
PROPUESTA

## Contexto
MCP-1 validó en VM sandbox que Hermes v0.13.0 puede invocar el PymIA MCP server real para la tool `pymia.first_clinical_interview.v1`.

Documentos base:
- `docs/arquitectura/HERMES_MCP1_GATEWAY_CONTROLLED_INTEGRATION.md`
- `docs/arquitectura/HERMES_MCP1_SANDBOX_EXECUTION_CHECKLIST.md`
- `docs/arquitectura/HERMES_MCP1_SANDBOX_EXECUTION_RESULT.md`

Commit base:
- `048ef04`

## Decisión
MCP-2 será una etapa de repetibilidad sandbox.

No promueve a productivo.

Busca transformar la ejecución manual de MCP-1 en un procedimiento reproducible con:
- comando único o runner sandbox
- captura de evidencia normalizada
- fail-closed verificable
- aislamiento comprobable
- salida PASS/BLOCKED/FAIL estable

## Objetivo MCP-2
Definir y validar un runner sandbox repetible para ejecutar los casos MCP-1 sin intervención manual excesiva.

## Alcance aprobado
- Sandbox bajo `/tmp/pymia-mcp2-repeatability/`
- `HERMES_HOME` aislado
- PymIA MCP server real
- Tool única `pymia.first_clinical_interview.v1`
- Casos:
  - CA01
  - CA05
  - CA_NEG
  - CA_FAIL_CLOSED
- Evidencia JSON por caso
- Logs sandbox
- reporte final normalizado

## Fuera de alcance
- Telegram productivo
- systemd productivo
- `.env` productivo
- `~/.hermes`
- gateway vivo
- nuevas tools MCP
- `operational_audit`
- Excel/documentos
- cambios en `pymia` core
- deployment
- daemonización
- monitoreo productivo

## Requisitos del runner sandbox
El runner debe:
- crear directorios sandbox
- exportar `HERMES_HOME`
- exportar `PYTHONPATH`
- verificar import de PymIA MCP server
- verificar Hermes disponible
- verificar tool discovery
- ejecutar CA01
- persistir progressive_context
- ejecutar CA05 con contexto previo
- ejecutar CA_NEG
- simular CA_FAIL_CLOSED sin tocar productivo
- restaurar configuración sandbox
- generar reporte final

## Evidencia mínima
Guardar bajo:

`/tmp/pymia-mcp2-repeatability/evidence/`

Archivos esperados:
- `preflight.json`
- `tool_discovery.json`
- `CA01.json`
- `CA05.json`
- `CA_NEG.json`
- `CA_FAIL_CLOSED.json`
- `isolation.json`
- `summary.json`

## Criterios PASS
- runner ejecutable en VM sandbox
- tool única descubierta
- CA01 PASS
- CA05 PASS
- CA_NEG PASS
- CA_FAIL_CLOSED PASS
- no se toca productivo
- repo queda clean
- evidencia generada completa

## Criterios BLOCKED
- Hermes no permite runner no interactivo
- no se puede aislar `HERMES_HOME`
- no se puede usar `.env` solo sandbox
- server MCP no importa
- no hay forma estable de invocar la tool sin improvisación

## Criterios FAIL
- Hermes diagnostica sin MCP
- Hermes calcula margen
- Hermes reescribe salida clínica
- se mezcla contexto entre tenants
- se toca productivo
- se habilita una tool no aprobada

## Promoción prohibida
Aunque MCP-2 pase, sigue prohibido:
- conectar Telegram
- tocar systemd
- tocar `.env` productivo
- activar gateway vivo
- exponer a usuarios reales

## Próximo paso posterior
Si MCP-2 PASS:
crear MCP-3 como decisión separada para integración pre-productiva controlada.

MCP-3 deberá tener aprobación explícita antes de tocar cualquier componente vivo.
