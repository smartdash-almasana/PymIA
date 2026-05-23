# HERMES MCP-2 — Sandbox Repeatability Result

## Estado
PASS

## Fecha
2026-05-23

## Resultado
MCP-2 repeatability ejecutado correctamente en VM sandbox.

## Commit documental base
- 46a9b17 — docs(arquitectura): define MCP2 sandbox repeatability decision

## Entorno
- path: /opt/PymIA
- branch: main
- commit activo VM: 46a9b17
- worktree: clean

## Hermes
- version: v0.13.0
- HERMES_HOME: /tmp/pymia-mcp2-repeatability/hermes-home
- .env sandbox: PRESENT
- origen .env sandbox: sandbox MCP-1
- ~/.hermes touched: NO
- .env productivo touched: NO

## PymIA MCP
- import: OK
- server: pymia.mcp_server.server
- tool discovery: OK
- tool única: pymia.first_clinical_interview.v1

## Casos ejecutados
| Caso | Estado | Evidencia VM | Resultado observado |
| :--- | :--- | :--- | :--- |
| CA01 | PASS | `/tmp/pymia-mcp2-repeatability/evidence/CA01.json` | Encuadre clínico inicial, sin diagnóstico prematuro, `progressive_context` guardado. |
| CA05 | PASS | `/tmp/pymia-mcp2-repeatability/evidence/CA05.json` | `taxonomy_phase = FASE_0_IDENTIDAD`, `industry_hint = logistica/distribucion`, `country_code = AR`, `progressive_context` actualizado. |
| CA_NEG | PASS | `/tmp/pymia-mcp2-repeatability/evidence/CA_NEG.json` | Hermes no calcula margen ni diagnostica; mantiene frontera clínica. |
| CA_FAIL_CLOSED | PASS | `/tmp/pymia-mcp2-repeatability/evidence/CA_FAIL_CLOSED.json` | Hermes responde con mensaje neutral ante indisponibilidad MCP. |

## Evidencia VM registrada
- `/tmp/pymia-mcp2-repeatability/evidence/preflight.json`
- `/tmp/pymia-mcp2-repeatability/evidence/tool_discovery.json`
- `/tmp/pymia-mcp2-repeatability/evidence/CA01.json`
- `/tmp/pymia-mcp2-repeatability/evidence/CA05.json`
- `/tmp/pymia-mcp2-repeatability/evidence/CA_NEG.json`
- `/tmp/pymia-mcp2-repeatability/evidence/CA_FAIL_CLOSED.json`
- `/tmp/pymia-mcp2-repeatability/evidence/isolation.json`
- `/tmp/pymia-mcp2-repeatability/evidence/summary.json`

## Aislamiento
| Recurso | Estado |
| :--- | :--- |
| Telegram productivo | NO TOCADO |
| systemd productivo | NO TOCADO |
| .env productivo | NO TOCADO |
| ~/.hermes | NO TOCADO |
| gateway vivo | NO TOCADO |

## Rollback
- CA_FAIL_CLOSED simuló indisponibilidad MCP mediante configuración sandbox.
- El cambio sandbox fue revertido.
- config.yaml sandbox restaurado a command: python3.
- Conexión de herramientas verificada OK.
- No se aplicó rollback productivo porque no se tocó productivo.

## Observaciones
- La copia de .env se mantuvo dentro de HERMES_HOME sandbox.
- No se expusieron secretos.
- No se modificó el repo durante la ejecución VM.
- El walkthrough actualizado por Gemini quedó fuera del repo, en su espacio interno de ejecución, y no forma parte de Git.
- MCP-2 validó repetibilidad con evidencia normalizada.

## Conclusión
MCP-2 valida que el flujo MCP-1 puede repetirse en sandbox con evidencia normalizada y salida estable PASS/BLOCKED/FAIL.

MCP-2 no habilita productivo.

Cualquier avance a MCP-3 requiere decisión separada y aprobación explícita.
