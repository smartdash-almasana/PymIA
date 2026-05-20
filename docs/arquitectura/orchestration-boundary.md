Contexto alineado. No autoriza runtime, MCP, jobs, workflows ni orquestación dentro de PymIA. Rige ARCHITECTURE_GUARDRAILS.md y la doctrina de SEMANTICA_CONVERSACIONAL_PYMIA_HERMES_BEM.md.

# Hermes — Boundary de Orquestación y Conexión Semántica

## Estado
Documento canónico corregido y alineado  
**Fecha:** Mayo 2026

---

## 1. Reglas Canónicas y Rectoras

* **PymIA no cree: contrasta.**
* **Hermes no supone: pregunta.**
* **BEM no diagnostica: extrae.**
* **La hipótesis no es diagnóstico.**

---

## 2. Regla Obligatoria de Aislamiento y Roles

* **PymIA (Kernel) es el único soberano del cómputo y decisión clínica:** Procesa las fórmulas, evalúa el catálogo de patologías y consolida diagnósticos en el `OperationalAuditResult`.
* **Hermes es el sirviente conversacional de PymIA:** No es un agente autónomo. Su función es conectar semánticamente el relato del dueño con la computadora lógica PymIA, formulando preguntas de rigor e inteligencia sin inventar findings.
* **BEM es una frontera documental auxiliar y externa:** No es una capacidad interna de PymIA. Asiste en la extracción compleja de evidencia física de alta entropía (como PDFs o imágenes) y la convierte en registros limpios de bajo acoplamiento.

---

## 3. Flujo Correcto de Orquestación (AuditBoundaryGraph v1)

La orquestación del primer contacto e ingesta documental se rige estrictamente por el grafo determinista síncrono `AuditBoundaryGraph` en `conversa-engine`:

```text
       Telegram / Canal Externo
                  │
                  ▼
   [intake_node] (Registra y clasifica la entrada: NARRATIVE o INTERNAL_FACT)
                  │
                  ▼
   [locate_audit_node] (Localiza y valida el JSON de auditoría precalculado en sesión)
                  │
                  ▼
   [routing_node] (Carga OperationalAuditResult y rutea la respuesta de Hermes)
```

### Flujo incorrecto y prohibido (Bypass)
```text
Telegram ──> [LLM / AI Layer] ──> Diagnóstico / Acciones directas (Bypass de PymIA)
Telegram ──> BEM autónomo ──> Diagnóstico inmediato (Bypass de contraste)
```

---

## 4. Límites Conversacionales de Primer Contacto

Hermes tiene estrictamente prohibido crear Jobs de factoría, iniciar workflows destructivos o disparar tareas pesadas de procesamiento documental en el primer contacto.

### Boundary de herramientas en el primer contacto:

```text
PERMITIDAS (Lectura y Aclaración Síncrona):
- resolve_clarification
- save_clarification
- get_evidence
- ingest_document (local síncrono para INTERNAL_FACT)

PROHIBIDAS (Causan bypass o acoplamiento asíncrono):
- create_job
- factory_process_intake
- factory_start_authorized_job
- factory_build_operational_case
- bem_submit_workflow (ejecución autónoma sin comando del kernel)
```

El flujo correcto para la admisión conversacional es determinista y no reactivo:
```text
Mensaje inicial / Archivo
──> AuditBoundaryGraph.invoke()
──> Ingesta local de bajo coste (INTERNAL_FACT)
──> Carga de OperationalAuditResult / pathology_routing_summary
──> Respuesta conversacional orientativa o pedido de documentación específica.
```
