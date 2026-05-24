# PymIA Technical Debt Register (Docs-Only)

## Estado
VIGENTE

## Fecha
2026-05-24

## Alcance
Registro documental de deuda técnica acumulada en el ciclo Hermes MCP-0/MCP-1/MCP-2.  
Solo cubre deuda cerrable mediante documentos. No incluye deuda de código, runtime, infraestructura ni configuración productiva.

**MCP-3 NO habilitado.**  
**No autoriza cambios productivos.**

## Criterios de priorización

| Prioridad | Definición |
| :--- | :--- |
| **P0** | Bloquea diseño MCP-3 o implica riesgo de suplantación/alucinación clínica sin documentación aprobada. |
| **P1** | Requiere cierre documental antes de cualquier ejecución pre-productiva controlada. |
| **P2** | Mejora documental deseable pero no bloqueante para diseño MCP-3. |

## Matriz de deuda

| ID | Tipo (Doc) | Tema | Riesgo | Evidencia | Acción documental | Dueño | Estado | Prioridad |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| TD-001 | Doc | SOUL.md productivo vs SOUL PymIA en repo | Alucinación/diagnóstico autónomo sin boundary clínico | `HERMES_LOCAL_STRUCTURE_AUDIT.md` §Gaps, §Riesgos | Formalizar baseline de identidad y boundary clínico en doc aprobado | Arquitectura | ABIERTO | P0 |
| TD-002 | Doc | MCP servers: bridge legacy productivo vs MCP real validado en sandbox | Desalineación crítica entre productivo y arquitectura MCP | `HERMES_LOCAL_STRUCTURE_AUDIT.md` §Mapa, `HERMES_MCP1_SANDBOX_EXECUTION_RESULT.md` | Documentar transición y allowlist de servidores MCP por etapa | Arquitectura | ABIERTO | P0 |
| TD-003 | Doc | Telegram toolset: exposición de tools de alto privilegio | Riesgo de acceso no autorizado vía canal público | `HERMES_LOCAL_STRUCTURE_AUDIT.md` §Mapa, §Riesgos | Definir política de toolset mínimo clínico por canal | Arquitectura | ABIERTO | P0 |
| TD-004 | Doc | Tool include/exclude sin política formal | Superficie de ataque amplia por registry global | `HERMES_CONFIG_HARDENING_PLAN.md` §4, `HERMES_RUNTIME_SOURCE_AUDIT.md` §Tool Registry | Matriz documental de tools permitidas/prohibidas por contexto | Arquitectura | ABIERTO | P0 |
| TD-005 | Doc | HERMES_HOME isolation sin política escrita | Contaminación cruzada de state.db y perfiles | `HERMES_LOCAL_STRUCTURE_AUDIT.md` §Mapa, `HERMES_CONFIG_HARDENING_PLAN.md` §1 | Política documental de aislamiento + matriz de entornos | Arquitectura | ABIERTO | P1 |
| TD-006 | Doc | Fail-closed behavior no formalizado | Bucles LLM inútiles ante fallo MCP | `HERMES_CONFIG_HARDENING_PLAN.md` §6, §10 | Taxonomía de fallas + respuestas esperadas por estado | Arquitectura | ABIERTO | P1 |
| TD-007 | Doc | Circuit breaker y MCP failure policy | Degradación conversacional por cooldown | `HERMES_CONFIG_HARDENING_PLAN.md` §10, `HERMES_RUNTIME_SOURCE_AUDIT.md` §MCP Runtime | Flujos de error documentados + criterios PASS/BLOCKED/FAIL | Arquitectura | ABIERTO | P1 |
| TD-008 | Doc | Provider/model policy sin gobernanza | Caída operativa por fallo de proveedor principal | `HERMES_LOCAL_STRUCTURE_AUDIT.md` §Mapa (Gemini key inválida) | Matriz de proveedores, fallback y criterio de bloqueo | Arquitectura | ABIERTO | P1 |
| TD-009 | Doc | SessionDB/SQLite concurrency risk | `database is locked` bajo alta concurrencia | `HERMES_RUNTIME_SOURCE_AUDIT.md` §Session Storage | Escenarios de carga definidos + umbrales de aceptación | Arquitectura | ABIERTO | P1 |
| TD-010 | Doc | Logs/sessions audit policy | Auditoría inconsistente de eventos críticos | `HERMES_LOCAL_STRUCTURE_AUDIT.md` §Mapa, `HERMES_CONFIG_HARDENING_PLAN.md` §11 | Esquema mínimo de evidencias + checklist de auditoría | Arquitectura | ABIERTO | P2 |
| TD-011 | Doc | Secrets/.env handling policy | Riesgo operativo por manejo en /tmp | `HERMES_LOCAL_STRUCTURE_AUDIT.md` §Mapa, `HERMES_CONFIG_HARDENING_PLAN.md` §9 | Política de no exposición + trazabilidad de acceso | Arquitectura | ABIERTO | P2 |
| TD-012 | Doc | Rollback principles no formalizados | Estado inestable tras fallo de configuración | `HERMES_CONFIG_HARDENING_PLAN.md` §12 | Principios de reversión aprobados y verificables | Arquitectura | ABIERTO | P2 |
| TD-013 | Doc | Config version obsolescence (v22 vs oficial) | Desalineación con referencia oficial | `HERMES_LOCAL_STRUCTURE_AUDIT.md` §Mapa, `HERMES_OFFICIAL_DOCS_DIGEST.md` | Verificación documental de versión objetivo contra docs oficiales | Arquitectura | ABIERTO | P2 |
| TD-014 | Doc | MCP tool naming sanitization | Traducción de identificadores (puntos/guiones a underscores) | `HERMES_OFFICIAL_DOCS_DIGEST.md` §MCP client, `HERMES_RUNTIME_SOURCE_AUDIT.md` §MCP Runtime | Documentar regla de traducción y mapeo en frontera PymIA | Arquitectura | ABIERTO | P2 |

## Supuestos y límites

### Supuestos
- Toda la deuda listada es cerrable exclusivamente con documentos.
- Las fuentes usadas son las únicas válidas para este registro.
- El Hardening Plan (`HERMES_CONFIG_HARDENING_PLAN.md`) está aprobado para diseño documental MCP-3 (`HERMES_CONFIG_HARDENING_PLAN_REVIEW.md`).
- MCP-1 y MCP-2 tienen PASS documentado en sandbox.

### Límites
- Este registro **no autoriza cambios productivos**.
- **MCP-3 NO habilitado** por este documento.
- No se autoriza tocar código, runtime, VM, Telegram, systemd, `.env` ni `~/.hermes`.
- No se autoriza crear nuevas tools MCP.
- No se autoriza promover ADR-008 más allá de su estado actual.
- Los items P0 deben cerrarse antes de cualquier diseño MCP-3.
- Los items P1 deben cerrarse antes de cualquier ejecución pre-productiva.
- Los items P2 son deseables pero no bloqueantes.

## Fuentes obligatorias
- `docs/hermes/HERMES_LOCAL_STRUCTURE_AUDIT.md`
- `docs/hermes/HERMES_OFFICIAL_DOCS_DIGEST.md`
- `docs/hermes/HERMES_RUNTIME_SOURCE_AUDIT.md`
- `docs/hermes/HERMES_CONFIG_HARDENING_PLAN.md`
- `docs/hermes/HERMES_CONFIG_HARDENING_PLAN_REVIEW.md`
- `docs/adr/ADR-008-hermes-mcp-client-pymia-mcp-server.md`
- `docs/arquitectura/HERMES_MCP1_GATEWAY_CONTROLLED_INTEGRATION.md`
- `docs/arquitectura/HERMES_MCP1_SANDBOX_EXECUTION_CHECKLIST.md`
- `docs/arquitectura/HERMES_MCP1_SANDBOX_EXECUTION_RESULT.md`
- `docs/arquitectura/HERMES_MCP2_SANDBOX_REPEATABILITY_DECISION.md`
- `docs/arquitectura/HERMES_MCP2_SANDBOX_REPEATABILITY_RESULT.md`
