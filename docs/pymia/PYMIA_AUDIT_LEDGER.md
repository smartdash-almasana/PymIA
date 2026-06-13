# PYMIA_AUDIT_LEDGER

## Estado

`DRAFT_AUTHORITY_LEDGER`

## Fecha

2026-06-12

## Propósito

Registrar la cadena de auditorías, decisiones y documentos de coherentización que ordenan PymIA / SmartPyme antes de construir la síntesis atómica.

Este ledger existe para evitar que las próximas decisiones salgan de memoria conversacional, intuición o documentos aislados.

Su función es responder:

```text
qué documento manda,
qué documento informa,
qué documento audita,
qué documento corrige,
qué documento habilita,
qué documento NO habilita,
y cómo cada pieza alimenta la síntesis atómica final.
```

## No autorizaciones

Este documento no autoriza:

- Modificar código.
- Ejecutar tests.
- Crear packs ejecutables.
- Migrar fórmulas.
- Migrar patologías.
- Migrar anamnesis.
- Abrir runtime, Telegram, Hermes, MCP productivo, ERP, PDF o UI.
- Promover memoria operativa a fuente canónica.
- Tratar auditorías como implementación.
- Convertir Qwen, ChatGPT u otra IA en fuente soberana sin respaldo documental/código.

---

# 1. Jerarquía de referencia documental

## 1.1 Nivel 0 — Contrato de arranque y guardrails

| Documento | Estado | Rol | Función | Observación |
|---|---|---|---|---|
| `AGENTS.md` | CANONICAL | Contrato operativo de agentes | Define cómo iniciar, leer, auditar, detener y no inventar | Debe leerse antes de cualquier trabajo serio. |
| `ARCHITECTURE_GUARDRAILS.md` | CANONICAL | Guardrails arquitectónicos | Define prohibiciones y límites de arquitectura | Bloquea deriva runtime, jobs, Hermes duplicado, imports indebidos y claims falsos. |
| `docs/pymia/PYMIA_DEVELOPMENT_METHOD.md` | CANONICAL | Método de fabricación | Define cadena ADR → Spec → Contract → TaskSpec → tests → code → evidence | No habilita saltos directos a código. |
| `docs/DOCUMENTATION_INDEX.md` | CANONICAL | Índice documental | Registra documentos vigentes, drafts, checkpoints y contratos | Debe mantenerse actualizado según ADR-007. |

## 1.2 Nivel 1 — ADRs y contratos rectores

| Documento | Estado | Rol | Función | Observación |
|---|---|---|---|---|
| `docs/adr/ADR-007-documentation-governance.md` | ACCEPTED | Gobierno documental | Define que el índice documental es soberano | Regla: documento nuevo debe estar en índice. |
| `docs/adr/ADR-010-conversational-anamnesis-contract.md` | ACCEPTED | Anamnesis conversacional | Define límites de anamnesis y conversación | No autoriza diagnóstico ni runtime nuevo. |
| `docs/adr/ADR-017-identity-scope-boundary.md` | ACCEPTED | Identidad tenant/cliente | Separa `tenant_id` técnico de `cliente_id` negocio | Rige contratos owner/evidence. |
| `docs/adr/ADR-018-owner-facing-report-boundary.md` | ACCEPTED | Frontera owner-facing | Define traducción al dueño sin diagnóstico nuevo | Clave para reportes. |
| `docs/adr/ADR-024-pack-system-foundation.md` | ACCEPTED | Frontera kernel ↔ conocimiento enchufable | Define Pack System como decisión rectora | No implementa packs; gobierna migraciones futuras. |
| `docs/contratos/evidence-chain-v1.md` | ACTIVE_CONTRACT | Cadena de evidencia | Define evidencia y trazabilidad | Debe alinearse con terminología vigente. |
| `docs/contratos/owner-decision-v1.md` | ACTIVE_CONTRACT | Decisión del dueño | Define límites de decisión owner | No convierte respuestas del dueño en evidencia dura automática. |

## 1.3 Nivel 2 — Auditorías y reconciliaciones recientes

| Documento | Estado | Rol | Función | Observación |
|---|---|---|---|---|
| `docs/pymia/SUPERAUDITORIA_INFORME_0.md` | ACTIVE_CHECKPOINT | Evidencia base | Detecta contaminación kernel/dominio y justifica ADR-024 | No autoriza migración. |
| `docs/pymia/PACK_BOUNDARY_CODE_RECONCILIATION.md` | DRAFT_DOCUMENTARY_RECONCILIATION | Mapa de frontera | Mapea hardcode actual a tipos de pack futuros | No autoriza código ni tests. |
| `docs/pymia/KNOWLEDGETANKS_PACKSYSTEM_RECONCILIATION_AUDIT.md` | DRAFT_DOCUMENTARY_AUDIT | Reconciliación conceptual | Subordina KnowledgeTanks al Pack System | Imprescindible antes de PACK_SYSTEM_CONTRACT_V1. |
| Informe Qwen de ingeniería/producto | EXTERNAL_AUDIT_SOURCE | Auditoría externa | Evalúa PymIA como producto PyME: qué es, qué no hace, qué podría hacer si | Debe registrarse como insumo, no como fuente soberana. |
| `Pymia-memoria/_estado_actual.md` | MEMORY_ONLY | Memoria operativa | Registra estado de trabajo y contexto reciente | No reemplaza docs canónicos. |
| `Pymia-memoria/_decisiones_vigentes.md` | MEMORY_ONLY | Memoria operativa | Registra decisiones de operación recientes | No reemplaza ADRs. |

## 1.4 Nivel 3 — Diseño SmartPyme histórico

| Documento | Categoría | Puede informar | No puede gobernar solo |
|---|---|---|---|
| `docs/smartpyme/SMARTPYME_KNOWLEDGE_TANKS_CONTRACT.md` | DESIGN_ONLY / HISTORICAL_SOURCE | Diseño de KnowledgeTanks y DomainPacks | Cruzar frontera kernel sin ADR-024 y Pack Contract. |
| `docs/smartpyme/SMARTPYME_KNOWLEDGE_TANKS_ARCHITECTURE.md` | DESIGN_ONLY / HISTORICAL_SOURCE | Lifecycle, TankSelectionResult, EvidenceRequest conceptual | Autorizar runtime. |
| `docs/smartpyme/SMARTPYME_OPERATIONAL_PATHOLOGY_TANK.md` | DOCUMENTED_ONLY | Síntomas, patologías candidatas, preguntas y evidencia sugerida | Diagnosticar o ejecutar. |
| `docs/smartpyme/SMARTPYME_EVIDENCE_AND_FORMULA_TANK.md` | DOCUMENTED_ONLY | Evidencia, fórmulas contrastables, suficiencia | Ejecutar fórmulas o validar evidencia final. |

---

# 2. Cadena de coherentización vigente

La cadena documental válida para la síntesis atómica es:

```text
SUPERAUDITORIA_INFORME_0
→ ADR-024 Pack System Foundation
→ DOCUMENTATION_INDEX actualizado
→ Pymia-memoria actualizada
→ PACK_BOUNDARY_CODE_RECONCILIATION
→ KNOWLEDGETANKS_PACKSYSTEM_RECONCILIATION_AUDIT
→ Informe Qwen de ingeniería/producto
→ PYMIA_AUDIT_LEDGER
→ OWNER_INTERACTION_ATOMIC_TRACE
→ DIAGNOSIS_PROGNOSIS_OWNER_INTERVENTION_AUDIT
→ PYMIA_ATOMIC_SYNTHESIS
```

Este ledger ocupa el lugar:

```text
PYMIA_AUDIT_LEDGER
```

---

# 3. Registro de documentos de auditoría y qué habilitan

## 3.1 SUPERAUDITORIA_INFORME_0

| Campo | Valor |
|---|---|
| Ruta | `docs/pymia/SUPERAUDITORIA_INFORME_0.md` |
| Tipo | Auditoría base |
| Estado | `ACTIVE_CHECKPOINT` |
| Rol | Evidencia del problema arquitectónico |
| Corrige | Visibiliza contaminación kernel/dominio |
| Habilita | Crear/aceptar ADR-024; mapear frontera kernel↔packs |
| No habilita | No habilita tocar código, migrar fórmulas, crear packs, ejecutar tests |
| Alimenta | ADR-024, PACK_BOUNDARY_CODE_RECONCILIATION, síntesis atómica |

Hallazgo central:

```text
Kernel sólido, pero frontera kernel ↔ conocimiento enchufable no implementada.
```

## 3.2 ADR-024 Pack System Foundation

| Campo | Valor |
|---|---|
| Ruta | `docs/adr/ADR-024-pack-system-foundation.md` |
| Tipo | ADR |
| Estado | `ACCEPTED` |
| Rol | Decisión rectora sobre conocimiento enchufable |
| Corrige | Define que fórmulas, patologías, rubros, variables organizacionales y catálogos son packs externos |
| Habilita | Contratos futuros de Pack System; auditorías de frontera |
| No habilita | No habilita migración directa, loaders, runtime ni packs ejecutables |
| Alimenta | PACK_BOUNDARY_CODE_RECONCILIATION, PACK_SYSTEM_CONTRACT_V1 futuro |

Frase rectora:

```text
El conocimiento de dominio es enchufable.
El kernel permanece estable.
Kernel PymIA ≠ catálogos enchufables.
```

## 3.3 PACK_BOUNDARY_CODE_RECONCILIATION

| Campo | Valor |
|---|---|
| Ruta | `docs/pymia/PACK_BOUNDARY_CODE_RECONCILIATION.md` |
| Tipo | Auditoría de frontera código/conocimiento |
| Estado | `DRAFT_DOCUMENTARY_RECONCILIATION` |
| Rol | Mapa previo a contrato |
| Corrige | Clasifica hardcode actual por destino de pack |
| Habilita | Diseñar PACK_SYSTEM_CONTRACT_V1 con mapa real de migraciones |
| No habilita | No autoriza migrar código ni crear packs ejecutables |
| Alimenta | PACK_SYSTEM_CONTRACT_V1, PYMIA_ATOMIC_SYNTHESIS |

Mapeo principal:

```text
formula_contract.py → FormulaPack
formula_engine_service.py → FormulaPack + executor seguro
core.py::_pathology_for_formula → PathologyPack / FormulaPack metadata
anamnesis_fsm.py opciones → CatalogPack
anamnesis_fsm.py _map/_detect → DomainPack / SectorPack
catalog_loader_v1.py → PackRegistry
pathology_knowledge_tank.py → PathologyPack con adapter conceptual
```

## 3.4 KNOWLEDGETANKS_PACKSYSTEM_RECONCILIATION_AUDIT

| Campo | Valor |
|---|---|
| Ruta | `docs/pymia/KNOWLEDGETANKS_PACKSYSTEM_RECONCILIATION_AUDIT.md` |
| Tipo | Auditoría de reconciliación conceptual |
| Estado | `DRAFT_DOCUMENTARY_AUDIT` |
| Rol | Puente entre diseño histórico y ADR-024 |
| Corrige | Evita doble arquitectura KnowledgeTanks vs Pack System |
| Habilita | Definir packs con `internal_units` y KnowledgeTank subordinado |
| No habilita | No autoriza TankSelection runtime ni loaders |
| Alimenta | PACK_SYSTEM_CONTRACT_V1, síntesis atómica |

Decisión registrada:

```text
Pack System gobierna.
KnowledgeTanks componen.
Kernel carga / valida / rechaza.
Tanks nunca deciden ni diagnostican.
```

## 3.5 Informe Qwen de ingeniería/producto

| Campo | Valor |
|---|---|
| Ruta | Archivo externo aportado por usuario / resultado Qwen |
| Tipo | Auditoría externa de producto e ingeniería |
| Estado | `EXTERNAL_AUDIT_SOURCE` |
| Rol | Validación externa contrastable |
| Corrige | Ordena PymIA como producto PyME: qué es, qué no hace y qué podría hacer si |
| Habilita | Construir síntesis atómica de producto con cautela |
| No habilita | No autoriza implementación ni claims comerciales no verificados |
| Alimenta | PYMIA_ATOMIC_SYNTHESIS, mapa producto |

Veredicto adoptado:

```text
PARTIAL
```

Uso correcto:

```text
Usar como auditoría externa respetada, contrastada con documentos y código.
No tratar como fuente canónica independiente.
```

---

# 4. Registro de documentos que informan pero no gobiernan solos

| Documento | Categoría | Puede informar | No puede gobernar solo |
|---|---|---|---|
| `Pymia-memoria/_estado_actual.md` | MEMORY_ONLY | Estado operativo reciente | Arquitectura, contratos, claims de producto |
| `Pymia-memoria/_decisiones_vigentes.md` | MEMORY_ONLY | Decisiones operativas y restricciones recientes | Sustituir ADRs o index |
| KnowledgeTanks docs | DESIGN_ONLY | Diseño de subarquitectura interna | Cruzar frontera kernel sin ADR-024/Pack Contract |
| Informe Qwen | EXTERNAL_AUDIT_SOURCE | Síntesis producto/ingeniería | Cambiar arquitectura por sí solo |
| Conversación actual | WORKING_CONTEXT | Dirección de trabajo | Fuente canónica final |

---

# 5. Qué queda habilitado ahora

Este ledger habilita únicamente:

1. Construir `OWNER_INTERACTION_ATOMIC_TRACE.md`.
2. Construir `DIAGNOSIS_PROGNOSIS_OWNER_INTERVENTION_AUDIT.md`.
3. Construir `PYMIA_ATOMIC_SYNTHESIS.md` después de esas dos piezas.
4. Preparar `PACK_SYSTEM_CONTRACT_V1.md` sólo después de cerrar autoridad, frontera y traza owner.

No habilita implementación.

---

# 6. Qué queda bloqueado

Queda bloqueado hasta contrato y autorización explícita:

```text
crear PackRegistry ejecutable
migrar SUPPORTED_FORMULAS
migrar FormulaEngineService
migrar _pathology_for_formula
extraer anamnesis_fsm a CatalogPack/DomainPack
implementar TankSelection
crear EvidenceRequest runtime
crear packs YAML ejecutables
correr tests de migración
abrir runtime
vender producto SaaS completo
prometer pronóstico automático
prometer diagnóstico confirmado sin evidencia
```

---

# 7. Riesgos de autoridad detectados

| Riesgo | Severidad | Descripción | Control |
|---|---|---|---|
| Auditorías como implementación | Alta | Tomar documentos como capacidad real | Marcar `DOCUMENTED_ONLY` y `DRAFT`. |
| Qwen como fuente soberana | Media | Aceptar informe externo sin contraste | Usarlo como `EXTERNAL_AUDIT_SOURCE`. |
| Memoria como arquitectura | Alta | Usar `Pymia-memoria` como verdad canónica | Mantener `MEMORY_ONLY`. |
| KnowledgeTanks como arquitectura paralela | Alta | Ignorar ADR-024 | Subordinar a Pack System. |
| PACK_SYSTEM_CONTRACT_V1 prematuro | Media | Crear contrato sin ledger ni traza owner | Cerrar ledger y traza atómica antes. |
| Síntesis atómica incompleta | Alta | Resumir sin diagnóstico/pronóstico/dueño | Crear auditoría específica antes de síntesis final. |

---

# 8. Estado de claims de producto

| Claim | Estado actual | Fuente | Puede usarse |
|---|---|---|---|
| PymIA es un sistema de diagnóstico operativo PyME basado en evidencia | CANDIDATE_PRODUCT_CLAIM | Qwen + docs + código parcial | Sí, con cautela. |
| PymIA es un copiloto operativo PyME | PRODUCT_POSITIONING_CANDIDATE | Qwen | Sí, si se aclara asistido y basado en evidencia. |
| PymIA diagnostica automáticamente cualquier PyME | FALSE / OVERCLAIM | Guardrails | No. |
| PymIA pronostica el futuro de la PyME | FALSE_NOW | Falta contrato/código | No. |
| PymIA podría pronosticar si hay contrato, series y evidencia | FUTURE_CONDITIONED | Qwen | Sí, como potencial condicionado. |
| PymIA incorpora conocimiento enchufable por packs | ARCHITECTURAL_DECISION | ADR-024 | Sí como arquitectura aceptada, no implementada. |
| PymIA ya tiene Pack System runtime | FALSE_NOW | Pack audits | No. |
| SmartPyme KnowledgeTanks son runtime | FALSE_NOW | KnowledgeTanks docs | No. |
| KnowledgeTanks son insumo para KnowledgePack/DomainPack | RECONCILED_DESIGN | Reconciliation audit | Sí. |

---

# 9. Próxima pieza obligatoria

La próxima pieza recomendada es:

```text
OWNER_INTERACTION_ATOMIC_TRACE.md
```

Motivo:

```text
Antes de sintetizar PymIA como producto, hay que fijar con precisión la traza Dueño → Anamnesis → Evidencia → Core → Reporte → Preguntas → Respuestas → Reentry.
```

Esa pieza debe separar:

- lo implementado;
- lo documentado;
- lo conceptual;
- lo bloqueado;
- la intervención real del dueño;
- el punto exacto donde una respuesta del dueño no es evidencia dura automática.

---

# 10. Criterio para síntesis atómica futura

No construir `PYMIA_ATOMIC_SYNTHESIS.md` hasta que existan:

```text
PYMIA_AUDIT_LEDGER.md
OWNER_INTERACTION_ATOMIC_TRACE.md
DIAGNOSIS_PROGNOSIS_OWNER_INTERVENTION_AUDIT.md
```

La síntesis atómica debe poder responder en menos de una página:

```text
Qué es PymIA.
Qué no es PymIA.
Qué hace hoy.
Qué no promete.
Qué podría hacer si.
Qué decide el kernel.
Qué decide el dueño.
Qué entra como pack.
Qué queda bloqueado sin evidencia.
Qué documento manda.
Cuál es el próximo paso autorizado.
```

---

# 11. Veredicto

`PASS_DOCUMENTARY_LEDGER_DRAFT`

La cadena de autoridad queda registrada.

No hay autorización de implementación.

Próximo frente:

```text
OWNER_INTERACTION_ATOMIC_TRACE.md
```
