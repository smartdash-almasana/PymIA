# Hermes Operational Verification — Auditoría Anti-Alucinación

**Fecha:** 2026-05-24  
**Estado:** VIGENTE  
**Relación con otros documentos:**
- `HERMES_CAPABILITY_AUDIT.md` (auditoría de capacidades)
- `ONTOLOGIA_AGENTES_SISTEMA.md` (ontología vigente)
- `ADR-008-hermes-mcp-client-pymia-mcp-server.md` (propuesta de integración)
- `pymia_first_clinical_interview_mcp_contract.md` (contrato MCP)

---

## 1. Alcance de la auditoría

Esta auditoría verifica **qué capacidades de Hermes Agent Nous están realmente integradas, probadas o documentadas** en el repo PymIA, separando evidencia real de inferencia para evitar alucinaciones sobre "Hermes GPT".

**Objetivo:** prevenir diseños basados en capacidades no probadas y establecer frontera dura entre Hermes (organismo operativo) y PymIA (inteligencia computacional).

---

## 2. Fuentes revisadas

| # | Fuente | Ubicación | Etiqueta |
|---|--------|-----------|----------|
| F1 | HERMES_CAPABILITY_AUDIT.md | `docs/arquitectura/` | `VERIFICADO_EN_DOC_LOCAL` |
| F2 | ONTOLOGIA_AGENTES_SISTEMA.md | `docs/arquitectura/` | `VERIFICADO_EN_DOC_LOCAL` |
| F3 | ADR-008 | `docs/adr/` | `VERIFICADO_EN_DOC_LOCAL` |
| F4 | pymia_first_clinical_interview_mcp_contract.md | `docs/contracts/` | `VERIFICADO_EN_DOC_LOCAL` |
| F5 | conversa-engine/main.py | Repo PymIA | `VERIFICADO_EN_REPO` |
| F6 | pymia/hermes/adapter.py | Repo PymIA | `VERIFICADO_EN_REPO` |
| F7 | https://hermes-agent.nousresearch.com/docs/ | Web externa | `EXTERNO_NO_VERIFICADO` |

---

## 3. Capacidades Hermes verificadas

| # | Capacidad | Etiqueta | Evidencia |
|---|-----------|----------|-----------|
| C1 | Hermes Agent es un agente autónomo, no un copilot IDE | `EXTERNO_NO_VERIFICADO` | F7: "It's not a coding copilot tethered to an IDE or a chatbot wrapper around a single API. It's an autonomous agent" |
| C2 | Hermes soporta 20+ canales (Telegram, Discord, Slack, WhatsApp, Signal, Matrix, Teams, Google Chat, Email, SMS, DingTalk, Feishu, WeCom, Weixin, QQ Bot, Yuanbao, BlueBubbles, Home Assistant, Microsoft Teams, Google Chat, Mattermost) | `EXTERNO_NO_VERIFICADO` | F7: "20+ platforms from one gateway" |
| C3 | Hermes corre en 6 backends: local, Docker, SSH, Daytona, Singularity, Modal | `EXTERNO_NO_VERIFICADO` | F7: "6 terminal backends" |
| C4 | Hermes tiene skills system (memoria procedural auto-creada) | `EXTERNO_NO_VERIFICADO` | F7: "Skills System: Procedural memory the agent creates and reuses" |
| C5 | Hermes integra MCP como client y puede exponerse como server | `EXTERNO_NO_VERIFICADO` | F7: "MCP Integration: Connect to MCP servers, filter their tools, and extend Hermes safely" |
| C6 | Hermes tiene memory persistente cross-session (MEMORY.md / USER.md) | `EXTERNO_NO_VERIFICADO` | F7: "Memory System: Persistent memory that grows across sessions" |
| C7 | Hermes tiene SOUL.md (personalidad global) y Context Files (contexto por proyecto) | `EXTERNO_NO_VERIFICADO` | F7: "Personality & SOUL.md" y "Context Files" |
| C8 | Hermes tiene cron / jobs / scheduled automations | `EXTERNO_NO_VERIFICADO` | F7: "Scheduled automations: Built-in cron with delivery to any platform" |
| C9 | Hermes soporta voice mode (CLI, Telegram, Discord) | `EXTERNO_NO_VERIFICADO` | F7: "Voice Mode: Real-time voice interaction in CLI, Telegram, Discord, and Discord VC" |
| C10 | Hermes tiene API server con `/v1/runs` SSE y `previous_response_id` | `EXTERNO_NO_VERIFICADO` | F7: menciona "Full web control" pero no detalla API server SSE |
| C11 | Hermes tiene 70+ tools built-in | `EXTERNO_NO_VERIFICADO` | F7: "70+ built-in tools and how to configure them" |
| C12 | Hermes permite `delegate_task` para sub-agentes aislados | `EXTERNO_NO_VERIFICADO` | F7: "Delegates & parallelizes: Spawn isolated subagents for parallel workstreams" |
| C13 | Hermes integra con Honcho (dialectic user modeling) | `EXTERNO_NO_VERIFICADO` | F7: "Honcho dialectic user modeling" |
| C14 | PymIA hoy no usa ninguna capacidad real de Hermes Agent | `VERIFICADO_EN_REPO` | F5, F6: adapter es PymIA-propio, no importa hermes_agent |
| C15 | `conversa-engine/main.py` hardcodea `channel="telegram"` y no usa Hermes Agent gateway | `VERIFICADO_EN_REPO` | F5: línea ~90 `channel="telegram"` |
| C16 | Frontera Hermes↔PymIA formalizada en ADR-008 como MCP client→server | `VERIFICADO_EN_DOC_LOCAL` | F3: ADR-008 sección "Decisión" |
| C17 | Ontología vigente define Hermes como organismo operativo, no computacional | `VERIFICADO_EN_DOC_LOCAL` | F2: sección "Definición de cada agente" |

---

## 4. Capacidades Hermes inferidas/no probadas

| # | Afirmación | Etiqueta | Nota |
|---|-----------|----------|------|
| I1 | Hermes Agent Nous **no está instalado ni configurado** en este repo | `INFERIDO_NO_PROBADO` | No se evidencia `hermes-agent` en `pyproject.toml`, `requirements.txt` ni `.env.local` |
| I2 | El adapter actual en `pymia/hermes/adapter.py` es un nombre heredado, no integración real con Hermes Agent Nous | `INFERIDO_NO_PROBADO` | El archivo importa solo `pymia/interfaces/...`, no hay `import hermes_agent` |
| I3 | Los "20+ canales" de Hermes Agent Nous podrían reemplazar la lógica de canal propia de `conversa-engine/` | `INFERIDO_NO_PROBADO` | Requiere evaluación de migración |
| I4 | `MEMORY.md/USER.md` de Hermes podría entrar en conflicto con `Pymia-memoria/` Obsidian vault | `INFERIDO_NO_PROBADO` | Dos sistemas de memoria coexistirían sin gobernanza clara |
| I5 | Skills de Hermes podrían aprender patrones clínicos que deben ser soberanía de PymIA | `INFERIDO_NO_PROBADO` | Riesgo de fuga de computabilidad |
| I6 | Honcho (dialectic user modeling) podría duplicar `ProgressiveTenantClinicalContext` | `INFERIDO_NO_PROBADO` | Dos modelos de usuario compitiendo |

---

## 5. Capacidades externas/no verificadas

| # | Capacidad | Etiqueta | Origen |
|---|-----------|----------|--------|
| E1 | Learning loop cerrado (skill self-improvement) | `EXTERNO_NO_VERIFICADO` | F7: "The only agent with a built-in learning loop" |
| E2 | FTS5 cross-session recall con LLM summarization | `EXTERNO_NO_VERIFICADO` | F7: "FTS5 cross-session recall with LLM summarization" |
| E3 | Atropos RL training / batch processing / trajectory export | `EXTERNO_NO_VERIFICADO` | F7: "Research-ready: Batch processing, trajectory export, RL training with Atropos" |
| E4 | BlueBubbles, DingTalk, Feishu, WeCom, Weixin, QQ Bot, Yuanbao | `EXTERNO_NO_VERIFICADO` | F7: lista de canales |
| E5 | Home Assistant integration | `EXTERNO_NO_VERIFICADO` | F7: "Home Assistant" en lista de canales |
| E6 | Serverless persistence (Daytona/Modal hibernate) | `EXTERNO_NO_VERIFICADO` | F7: "Daytona and Modal offer serverless persistence" |
| E7 | Compatible con agentskills.io (skills portables) | `EXTERNO_NO_VERIFICADO` | F7: "Compatible with agentskills.io" |

**Advertencia:** nada de E1–E7 está probado en el repo PymIA. Cualquier roadmap que los incluya debe marcarlos como `PENDIENTE_DE_VALIDACION` antes de diseñar sobre ellos.

---

## 6. Riesgos de alucinación sobre Hermes

| # | Alucinación posible | Etiqueta | Mitigación |
|---|--------------------|----------|------------|
| H1 | Asumir que "Hermes" en el repo = Hermes Agent Nous | `INFERIDO_NO_PROBADO` | Confirmar que `pymia/hermes/adapter.py` es un adapter PymIA-propio, no Hermes Nous |
| H2 | Creer que PymIA ya usa MCP client de Hermes | `PROHIBIDO_POR_CONTRATO` | ADR-008 es **propuesta**, no implementado |
| H3 | Asumir que Hermes Nous ya diagnostica PyMEs | `PROHIBIDO_POR_CONTRATO` | Viola F2: Hermes no computa |
| H4 | Diseñar sobre `delegate_task` sin probar latencia y aislamiento | `PENDIENTE_DE_VALIDACION` | Requiere smoke test |
| H5 | Asumir que `MEMORY.md` reemplaza `Pymia-memoria/` | `PROHIBIDO_POR_CONTRATO` | `Pymia-memoria/` es vault de decisiones arquitectónicas, no memoria conversacional |
| H6 | Asumir que los 20+ canales están todos mantenidos | `EXTERNO_NO_VERIFICADO` | Verificar support matrix real por versión |
| H7 | Asumir que skills auto-mejorados no afectan contratos clínicos | `PENDIENTE_DE_VALIDACION` | Skills deben tener sandbox clínico aislado |

---

## 7. Riesgos de suplantación de PymIA

| # | Riesgo | Etiqueta | Mitigación |
|---|--------|----------|------------|
| S1 | Hermes (Nous) genera diagnóstico por su cuenta vía LLM raw | `PROHIBIDO_POR_CONTRATO` | F3 §11: "Hermes no diagnostica" |
| S2 | Hermes interpreta Excel/PDF sin llamar tool PymIA | `PROHIBIDO_POR_CONTRATO` | F3 §11: "Hermes no interpreta Excel" |
| S3 | Hermes calcula margen/rentabilidad con chain-of-thought propio | `PROHIBIDO_POR_CONTRATO` | F3 §11: "Hermes no calcula margen" |
| S4 | Hermes inventa taxonomía (industry_hint) sin llamar `pymia.taxonomic_classify` | `PROHIBIDO_POR_CONTRATO` | F3 §11 + Flujo Semántico-Dialéctico v1 |
| S5 | Hermes pide evidencia clínica sin output de `pymia.evidence_requirements` | `PROHIBIDO_POR_CONTRATO` | F3 §11 |
| S6 | Hermes crea hallazgos (`DiagnosticReport`) en su propio reasoning | `PROHIBIDO_POR_CONTRATO` | Hallazgos solo desde `pymia.operational_audit` |
| S7 | Hermes persiste contexto clínico en `MEMORY.md` en lugar de `pymia.progressive_context_save` | `PROHIBIDO_POR_CONTRATO` | Contexto clínico es soberanía PymIA |
| S8 | Hermes aprende skill que encapsula lógica clínica (fuga de computabilidad) | `PENDIENTE_DE_VALIDACION` | Skills deben filtrarse: ningún skill puede llamar LLM para diagnóstico |

---

## 8. Sincronización Hermes ↔ PymIA

| Dimensión | Estado actual | Estado objetivo (ADR-008) | Etiqueta |
|-----------|---------------|---------------------------|----------|
| Integración | Adapter PymIA-propio (`pymia/hermes/adapter.py`) | MCP client→server | `VERIFICADO_EN_DOC_LOCAL` |
| Canal | Hardcoded `telegram` en `conversa-engine/main.py` | Gateway Hermes (20+ canales) | `INFERIDO_NO_PROBADO` |
| Memoria clínica | `progressive_context_sessions.json` (JSON plano) | Tool `pymia.progressive_context_save` | `VERIFICADO_EN_REPO` / `PENDIENTE_DE_VALIDACION` |
| Memoria decisiones | `Pymia-memoria/` (Obsidian vault) | Sin cambio (separada) | `VERIFICADO_EN_DOC_LOCAL` |
| Memoria conversacional global | No existe | `MEMORY.md/USER.md` de Hermes | `EXTERNO_NO_VERIFICADO` |
| Taxonomía | Contrato interno PymIA | Tool `pymia.taxonomic_classify` | `VERIFICADO_EN_REPO` / `PENDIENTE_DE_VALIDACION` |
| Evidencia | Contrato interno PymIA | Tool `pymia.evidence_requirements` | `VERIFICADO_EN_REPO` / `PENDIENTE_DE_VALIDACION` |
| Diagnóstico | Contrato interno PymIA | Tool `pymia.operational_audit` | `VERIFICADO_EN_REPO` / `PENDIENTE_DE_VALIDACION` |

---

## 9. Matriz de capacidades

| Capacidad Hermes | Evidencia | Nodo PymIA relacionado | Input esperado | Output esperado | Riesgo suplantación | Validación pendiente |
|------------------|-----------|------------------------|----------------|-----------------|---------------------|----------------------|
| MCP client mode | `EXTERNO_NO_VERIFICADO` | Todas las tools ADR-008 §10 | Tool name + params JSON | Tool result tipado | Bajo (si se fuerza ruta MCP) | Instalar Hermes + conectar a PymIA MCP server |
| `agent.chat` / `run_conversation` | `EXTERNO_NO_VERIFICADO` | `pymia.first_clinical_interview` | `user_text`, `session_id` | Reply + tool calls | Alto (si Hermes responde sin llamar tool) | Test: forzar que Hermes SIEMPRE llame tool clínica antes de responder |
| `MEMORY.md` | `EXTERNO_NO_VERIFICADO` | Ninguno (solo datos de dueño, no clínica) | Auto-curado | Memoria global | Alto si almacena hallazgos | Política: MEMORY.md prohibido contener `industry_hint`, `diagnóstico`, `evidence` |
| `delegate_task` | `EXTERNO_NO_VERIFICADO` | `pymia.operational_audit` (potencial) | Task description + sub-agent | Resultado agregado | Alto si sub-agente diagnostica | Sandbox: sub-agent no puede invocar LLM clínico |
| Skills | `EXTERNO_NO_VERIFICADO` | Ninguno | Auto-creado | Procedural memory | Crítico si skill encapsula clínica | Filtro: skills no pueden llamar `pymia.*` tools sin aprobación |
| Context Files | `EXTERNO_NO_VERIFICADO` | `pymia.first_clinical_interview` (contexto) | Archivo por proyecto | Contexto inyectado | Medio si inyecta taxonomía falsa | Revisar que context files no contengan contratos clínicos hardcoded |
| Cron / Jobs | `EXTERNO_NO_VERIFICADO` | `pymia.operational_audit` (reportes agendados) | Schedule + task | Ejecución diferida | Medio | Solo jobs de reporting, no de diagnóstico autónomo |
| Gateway (20+ canales) | `EXTERNO_NO_VERIFICADO` | Reemplaza `conversa-engine/` canal | Channel config | Delivery multi-canal | Bajo (si PymIA sigue siendo quien responde) | Test: mensaje entra por Telegram/WhatsApp y sale vía tool PymIA |
| Voice mode | `EXTERNO_NO_VERIFICADO` | `pymia.first_clinical_interview` (modalidad voice) | Audio transcript | Reply + TTS | Bajo | Test: flujo FASE_0 por voz |
| API server `/v1/runs` SSE | `EXTERNO_NO_VERIFICADO` | Streaming de `pymia.first_clinical_interview` | HTTP request | Stream events | Medio | Test: SSE entrega eventos de `progressive_context` |
| Honcho user modeling | `EXTERNO_NO_VERIFICADO` | Colisión con `ProgressiveTenantClinicalContext` | Interacción | User model | Alto si reemplaza contexto clínico | Decisión: Honcho para preferencias UX, PymIA para clínica |

---

## 10. Capacidades útiles para exprimir Hermes

Priorizadas por valor para PymIA (sin violar ontología):

1. **Gateway multi-canal** → reemplaza `conversa-engine/main.py` hardcoded channel (`VERIFICADO_EN_REPO` problema actual)
2. **MCP client mode** → habilita ADR-008 sin reescribir adapter
3. **Context Files** → inyectar `ONTOLOGIA_AGENTES_SISTEMA.md` y `Flujo Semántico-Dialéctico v1` como system prompt automático
4. **Cron/Jobs** → auditorías operativas agendadas con reporte a Telegram
5. **FTS5 cross-session recall** → búsqueda en historial de sesiones del dueño (no clínica)
6. **API server SSE** → streaming de entrevistas clínicas largas
7. **Voice mode** → primer encuentro por voz (diferenciador de producto)

**No exprimir sin validación:** skills auto-mejorados, Honcho, delegate_task (todos con riesgo de suplantación).

---

## 11. Pruebas/smokes recomendados

| # | Smoke | Objetivo | Etiqueta actual |
|---|-------|----------|-----------------|
| SM1 | Instalar Hermes Agent Nous en entorno aislado | Verificar C2, C5, C10 | `PENDIENTE_DE_VALIDACION` |
| SM2 | Conectar Hermes MCP client a un PymIA MCP server mínimo (solo `pymia.first_clinical_interview`) | Validar ADR-008 | `PENDIENTE_DE_VALIDACION` |
| SM3 | Enviar mensaje por Telegram vía gateway Hermes y verificar que llama tool PymIA antes de responder | Validar S1 | `PENDIENTE_DE_VALIDACION` |
| SM4 | Enviar Excel y verificar que Hermes NO interpreta, solo pasa a `pymia.evidence_requirements` | Validar S2 | `PENDIENTE_DE_VALIDACION` |
| SM5 | Verificar que MEMORY.md de Hermes NO contiene hallazgos clínicos tras 10 turnos | Validar S7 | `PENDIENTE_DE_VALIDACION` |
| SM6 | Verificar latencia roundtrip Hermes → PymIA tool → reply | Validar R1 de ADR-008 | `PENDIENTE_DE_VALIDACION` |
| SM7 | Probar voice mode con FASE_0 taxonomica | Validar C9 en contexto PymIA | `PENDIENTE_DE_VALIDACION` |

---

## 12. Conclusión operativa

**Estado real:**
- Hermes Agent Nous existe y es potente, pero **todo lo que sabemos viene de documentación externa** (`EXTERNO_NO_VERIFICADO` respecto al repo).
- El repo PymIA **no tiene Hermes Agent integrado** — solo un adapter propio con nombre heredado (`pymia/hermes/adapter.py`).
- ADR-008 formaliza la intención de integrar como MCP client→server, pero es **propuesta**, no implementación.

**Riesgo principal:**
- La alucinación más probable es creer que "Hermes" ya hace cosas en el repo cuando en realidad **no está presente**. Cualquier diseño basado en capacidades Hermes debe marcarse `PENDIENTE_DE_VALIDACION` hasta pasar SM1.

**Riesgo de suplantación principal:**
- Si Hermes se integra sin frontera dura, sus capacidades nativas (MEMORY.md, skills, delegate_task, Honcho) pueden **invadir la soberanía computacional de PymIA** violando la ontología vigente.

**Próximo paso recomendado:**
- Ejecutar **SM1 + SM2** en un entorno aislado (no en `main`, no en VM de producción).
- Si pasan, promover ADR-008 de PROPUESTA a APROBADO.
- Si fallan, documentar los bloqueos antes de cualquier diseño adicional.

**No se debe:**
- Diseñar features asumiendo capacidades Hermes no probadas en repo.
- Mezclar `Pymia-memoria/` (Obsidian vault de decisiones) con `MEMORY.md` de Hermes.
- Permitir que skills de Hermes aprendan patrones clínicos sin sandbox.

---

## Historial de versiones

| Versión | Fecha | Cambio |
|---------|-------|--------|
| v1.0 | 2026-05-24 | Creación inicial con auditoría completa anti-alucinación |
