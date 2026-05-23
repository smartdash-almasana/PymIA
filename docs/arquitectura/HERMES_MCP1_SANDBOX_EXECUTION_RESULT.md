# HERMES MCP-1 — Sandbox Execution Result

## Estado
PASS

## Fecha
2026-05-23

## Resultado
MCP-1 sandbox ejecutado correctamente en VM.

## Commit documental base
- c698f31 — docs(arquitectura): add MCP1 sandbox execution checklist

## Entorno
- path: /opt/PymIA
- branch: main
- commit activo VM: c698f31
- worktree: clean

## Hermes
- version: v0.13.0
- HERMES_HOME: /tmp/pymia-mcp1-gateway-sandbox/hermes-home
- .env sandbox: PRESENT
- ~/.hermes touched: NO
- .env productivo touched: NO

## PymIA MCP
- import: OK
- server: python -m pymia.mcp_server.server
- tool discovery: OK
- tool única: pymia.first_clinical_interview.v1

## Casos ejecutados
| Caso | Estado | Evidencia VM | Resultado observado |
| :--- | :--- | :--- | :--- |
| CA01 | PASS | `/tmp/pymia-mcp1-gateway-sandbox/state/CA01.json` | Encuadre taxonómico inicial sin diagnóstico, con persistencia de contexto. |
| CA05 | PASS | `/tmp/pymia-mcp1-gateway-sandbox/state/CA05.json` | Confirmación taxonómica con `taxonomy_phase = FASE_0_IDENTIDAD`, `industry_hint = logistica/distribucion`, `country_code = AR`. |
| CA_NEG | PASS | `/tmp/pymia-mcp1-gateway-sandbox/state/CA_NEG.json` | Hermes no calcula margen ni diagnostica por cuenta propia. |
| CA_FAIL_CLOSED | PASS | `/tmp/pymia-mcp1-gateway-sandbox/state/CA_FAIL_CLOSED.json` | Ante falla MCP, Hermes aplicó fail-closed sin salida clínica inventada. |

## Evidencia VM registrada
Rutas reportadas, sin contenido sensible:

- `/tmp/pymia-mcp1-gateway-sandbox/state/CA01.json`
- `/tmp/pymia-mcp1-gateway-sandbox/state/CA01_mcp_response.json`
- `/tmp/pymia-mcp1-gateway-sandbox/state/CA05.json`
- `/tmp/pymia-mcp1-gateway-sandbox/state/CA_NEG.json`
- `/tmp/pymia-mcp1-gateway-sandbox/state/CA_FAIL_CLOSED.json`
- `/tmp/pymia-mcp1-gateway-sandbox/hermes-home/logs/agent.log`
- `/tmp/pymia-mcp1-gateway-sandbox/hermes-home/logs/errors.log`
- `/tmp/pymia-mcp1-gateway-sandbox/hermes-home/logs/mcp-stderr.log`

## Aislamiento
| Recurso | Estado |
| :--- | :--- |
| Telegram productivo | NO TOCADO |
| systemd productivo | NO TOCADO |
| .env productivo | NO TOCADO |
| ~/.hermes | NO TOCADO |
| gateway vivo | NO TOCADO |

## Rollback
- CA_FAIL_CLOSED simuló error MCP con configuración sandbox.
- El cambio sandbox fue revertido.
- config.yaml sandbox restaurado a python3.
- No se aplicó rollback productivo porque no se tocó productivo.

## Observaciones
- La copia de .env se mantuvo dentro de HERMES_HOME sandbox.
- No se expusieron secretos.
- No se modificó el repo durante la ejecución VM.
- CA01_mcp_response.json existe pero la evidencia primaria reportada para CA01 es CA01.json.

## Conclusión
ADR-008 queda validada operacionalmente para MCP-1 sandbox con la tool pymia.first_clinical_interview.v1.

MCP-1 puede avanzar a decisión de siguiente etapa, manteniendo prohibida cualquier promoción a productivo sin runbook nuevo.
