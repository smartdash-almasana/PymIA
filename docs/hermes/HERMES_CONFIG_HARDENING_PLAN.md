# Hermes Config Hardening Plan for PymIA

## Estado
DRAFT / NO AUTORIZA EJECUCIÓN

## Fecha
2026-05-23

## Propósito
Definir el endurecimiento de configuración Hermes requerido antes de diseñar MCP-3. Este documento no autoriza ejecución, cambios productivos ni promoción MCP-3.

## Fuentes usadas
- `docs/hermes/HERMES_RUNTIME_SOURCE_AUDIT.md`
- `docs/hermes/HERMES_LOCAL_STRUCTURE_AUDIT.md`
- `docs/hermes/HERMES_OFFICIAL_DOCS_DIGEST.md`
- `docs/hermes/soul.md`

## Riesgos que resuelve
1. Inyección de prompts indirectas o alucinaciones del modelo que ejecuten herramientas MCP clínicas con argumentos arbitrarios.
2. Exposición de herramientas de alto privilegio a canales de mensajería pública (Telegram) por ausencia de políticas de exclusión estrictas por origen.
3. Dependencia exclusiva de `SOUL.md` como barrera clínica frente a jailbreak.
4. Bloqueos recurrentes de escritura (`database is locked`) en `state.db` bajo concurrencia alta.
5. Contaminación cruzada de perfiles por mala propagación de `HERMES_HOME`.
6. Falta de resiliencia semántica ante indisponibilidad/Circuit Breaker de servidores MCP, con riesgo de bucles inútiles del LLM.

## Principios
- No tocar producción.
- No activar MCP-3.
- No Telegram productivo.
- No systemd productivo.
- No `.env` productivo.
- No nuevas tools.
- No plugins todavía.
- No implementación física.

## Hardening propuesto

### 1. HERMES_HOME isolation
- Problema: Riesgo de contaminación cruzada de `state.db` y perfiles por fallback a `~/.hermes`.
- Propuesta: Definir política documental obligatoria de perfiles aislados por etapa y validación de contexto antes de cualquier ejecución.
- Riesgo mitigado: 5.
- Qué archivo tocaría en el futuro: `~/.hermes/config.yaml` y perfiles sandbox dedicados.
- Por qué NO se ejecuta todavía: Falta aprobación explícita para cambios en entornos vivos.
- Criterio de aceptación documental: Política escrita de aislamiento + matriz de entornos + reglas de verificación previas.

### 2. SOUL.md / prompt boundary
- Problema: `SOUL.md` como única barrera de comportamiento clínico.
- Propuesta: Definir baseline obligatorio de identidad y boundary clínico con controles de consistencia documental.
- Riesgo mitigado: 1, 3.
- Qué archivo tocaría en el futuro: `docs/hermes/soul.md` y mapeo de prompt de runtime.
- Por qué NO se ejecuta todavía: Requiere revisión de seguridad conversacional y aprobación formal.
- Criterio de aceptación documental: Checklist de alineación de identidad + criterios anti-jailbreak declarativos.

### 3. MCP server allowlist
- Problema: Desalineación entre bridge legacy y servidor MCP clínico esperado.
- Propuesta: Establecer allowlist documental de servidores MCP permitidos por etapa.
- Riesgo mitigado: 1, 6.
- Qué archivo tocaría en el futuro: bloque `mcp_servers` en configuración Hermes.
- Por qué NO se ejecuta todavía: Cualquier cambio de runtime está fuera de alcance en este ciclo.
- Criterio de aceptación documental: Tabla de servidores aprobados + estados permitidos/denegados.

### 4. Tool include/exclude
- Problema: Exposición transversal de tools por registry global y políticas no estrictas.
- Propuesta: Definir estándar de include/exclude por servidor y por etapa para reducir superficie de ataque.
- Riesgo mitigado: 1, 2, 6.
- Qué archivo tocaría en el futuro: políticas `tools.include` / `tools.exclude` de config.
- Por qué NO se ejecuta todavía: Necesita validación cruzada con contratos MCP y revisión de impacto.
- Criterio de aceptación documental: Matriz de tools permitidas/prohibidas por contexto.

### 5. Telegram toolset minimization
- Problema: Canal público con riesgo de acceso a tools de alto privilegio.
- Propuesta: Restringir documentalmente el toolset Telegram a mínimo clínico no peligroso.
- Riesgo mitigado: 2.
- Qué archivo tocaría en el futuro: `platform_toolsets` para Telegram.
- Por qué NO se ejecuta todavía: Telegram productivo está explícitamente fuera de alcance.
- Criterio de aceptación documental: Política de minimización de toolset por canal y justificación.

### 6. Fail-closed behavior
- Problema: Errores de tools se devuelven al LLM y pueden derivar en reintentos semánticos no útiles.
- Propuesta: Formalizar política fail-closed por tipo de falla MCP y reglas de salida neutra.
- Riesgo mitigado: 1, 6.
- Qué archivo tocaría en el futuro: guardrails/políticas de ejecución de runtime.
- Por qué NO se ejecuta todavía: Requiere diseño técnico aprobado y pruebas dedicadas.
- Criterio de aceptación documental: Taxonomía de fallas + respuestas esperadas por estado.

### 7. Provider/model policy
- Problema: Degradación operativa si proveedor principal falla y fallback no está gobernado.
- Propuesta: Definir política documental de proveedor primario/fallback y criterios de salud.
- Riesgo mitigado: 1, 6.
- Qué archivo tocaría en el futuro: bloques de `model` y providers en config.
- Por qué NO se ejecuta todavía: No se autorizan cambios de configuración productiva.
- Criterio de aceptación documental: Matriz de proveedores, fallback y criterio de bloqueo.

### 8. SessionDB/SQLite risk controls
- Problema: Contención bajo concurrencia puede agotar reintentos y producir `database is locked`.
- Propuesta: Establecer límites documentales de concurrencia y estrategia de observabilidad previa a MCP-3.
- Riesgo mitigado: 4, 5.
- Qué archivo tocaría en el futuro: parámetros runtime relacionados con persistencia/sesiones.
- Por qué NO se ejecuta todavía: Requiere pruebas de estrés aprobadas y aisladas.
- Criterio de aceptación documental: Escenarios de carga definidos + umbrales de aceptación.

### 9. Secrets/.env policy
- Problema: Riesgo de exposición por manejo operativo de secretos y perfiles.
- Propuesta: Definir política documental de manejo de secretos (sin contenido sensible) y prohibiciones operativas.
- Riesgo mitigado: 5.
- Qué archivo tocaría en el futuro: gestión de secretos en entorno Hermes (sin detallar valores).
- Por qué NO se ejecuta todavía: `.env` productivo está fuera de alcance.
- Criterio de aceptación documental: Política de no exposición + trazabilidad de acceso.

### 10. Circuit breaker and MCP failure policy
- Problema: Apertura de circuito puede disparar degradación conversacional si no hay contención semántica.
- Propuesta: Definir comportamiento esperado cuando MCP entra en cooldown y reglas de no-reintento abusivo.
- Riesgo mitigado: 6.
- Qué archivo tocaría en el futuro: políticas de manejo de errores MCP.
- Por qué NO se ejecuta todavía: Requiere validación con casos de falla en sandbox controlado.
- Criterio de aceptación documental: Flujos de error documentados + criterios PASS/BLOCKED/FAIL semánticos.

### 11. Logs/sessions audit policy
- Problema: Sin política documental robusta, la auditoría de eventos críticos puede ser inconsistente.
- Propuesta: Definir qué evidencias mínimas deben preservarse por etapa y cómo auditar sin exponer secretos.
- Riesgo mitigado: 4, 5, 6.
- Qué archivo tocaría en el futuro: lineamientos de observabilidad y retención de logs/sesiones.
- Por qué NO se ejecuta todavía: Requiere acuerdo de gobernanza y privacidad.
- Criterio de aceptación documental: Esquema mínimo de evidencias + checklist de auditoría.

### 12. Rollback principles
- Problema: Sin principios de rollback, fallas de configuración pueden dejar estado inestable.
- Propuesta: Formalizar rollback documental por etapas, con prioridad de no impacto productivo.
- Riesgo mitigado: 2, 5, 6.
- Qué archivo tocaría en el futuro: procedimientos de reversión por perfil/entorno.
- Por qué NO se ejecuta todavía: No corresponde ejecutar cambios ni rollback en este ciclo.
- Criterio de aceptación documental: Principios de reversión aprobados y verificables.

## Elementos explícitamente NO aprobados
- crear/modificar systemd
- modificar `~/.hermes`
- modificar `config.yaml` productivo
- crear/leer/copiar `.env`
- tocar Telegram
- crear `pymia_guard.py`
- crear hooks
- ejecutar `hermes doctor --fix`
- ejecutar `hermes chat`
- crear `task.md`
- promover MCP-3

## Recomendación
`NOT_READY_FOR_MCP3_UNTIL_CONFIG_HARDENING_PLAN_DOC_APPROVED`

## Implicación para MCP-3
MCP-3 no debe diseñarse ni ejecutarse hasta que este plan sea revisado y aprobado explícitamente.

## Límites
Este documento no autoriza:
- ejecución
- edición de producción
- cambios en systemd
- cambios en Telegram
- cambios en `.env`
- creación de plugins
- promoción MCP-3
