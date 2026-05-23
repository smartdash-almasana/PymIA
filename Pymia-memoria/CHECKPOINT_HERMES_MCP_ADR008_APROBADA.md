# CHECKPOINT — Hermes MCP / ADR-008 Aprobada

Estado: VIGENTE
Fecha: 2026-05-23

## Resumen

- ADR-008: APROBADO
- MCP-0: PASS
- SM2-VM retry: PASS
- Próxima etapa: MCP-1

## Límites operativos

- No usar stub stdin/stdout falso como reemplazo de MCP real.
- No tocar gateway productivo sin runbook aprobado.

## Cadena relevante

- a5fa813 docs(adr): approve Hermes MCP client architecture for first interview
- 795984e docs(arquitectura): record SM2 VM MCP retry success
- e6c3df8 feat(mcp): add first clinical interview MCP server

## Alcance aprobado

- Hermes MCP client -> PymIA MCP server.
- Tool inicial: `pymia.first_clinical_interview.v1`.
- Server real: `python -m pymia.mcp_server.server`.
