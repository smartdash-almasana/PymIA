# PACK_BOUNDARY_CODE_RECONCILIATION

## Estado

`DRAFT_DOCUMENTARY_RECONCILIATION`

## Fecha

2026-06-12

## Propósito

Registrar, en una sola pieza documental, qué conocimiento de dominio hardcodeado existe hoy en PymIA / SmartPyme, dónde vive, a qué tipo de pack debe migrar en el futuro y qué queda explícitamente fuera de alcance.

Este documento no implementa el Pack System.

Este documento es una auditoría de frontera para sostener la coherentización documental, conceptual y de código antes de cualquier migración.

## Autoridad documental

Fuentes rectoras:

- `AGENTS.md`
- `ARCHITECTURE_GUARDRAILS.md`
- `docs/pymia/PYMIA_DEVELOPMENT_METHOD.md`
- `docs/pymia/SUPERAUDITORIA_INFORME_0.md`
- `docs/adr/ADR-024-pack-system-foundation.md`
- `docs/DOCUMENTATION_INDEX.md`

Decisión rectora aceptada:

```text
El conocimiento de dominio es enchufable.
El kernel permanece estable.
Kernel PymIA ≠ catálogos enchufables.
```

## No autorizaciones

Este documento no autoriza:

- Modificar código.
- Ejecutar tests.
- Crear packs ejecutables.
- Crear loaders productivos de packs.
- Migrar fórmulas.
- Migrar patologías.
- Migrar anamnesis.
- Tocar `diagnostic_core/core.py`.
- Tocar `anamnesis_fsm.py`.
- Tocar `formula_contract.py`.
- Tocar runtime, Telegram, Hermes, MCP, graph productivo, PDF, ERP o UI.

## Tipos de pack aceptados por ADR-024

| Tipo | Rol |
|---|---|
| `DomainPack` | Conocimiento transversal de dominio, mapeos semánticos, variables organizacionales y reglas de interpretación no universales. |
| `KnowledgePack` | Conocimiento experto estructurado, frameworks sectoriales o modelos de madurez. |
| `FormulaPack` | Fórmulas financieras u operativas, inputs requeridos, expresión, unidades y metadata. |
| `PathologyPack` | Patologías operativas, mapping con fórmulas, umbrales, severidad y acciones sugeridas. |
| `SectorPack` | Conocimiento de rubro o vertical: textil, gastronomía, distribución, servicios, agro, etc. |
| `CatalogPack` | Opciones, listas, taxonomías y catálogos consumibles por anamnesis o UI conversacional. |

## Principio de clasificación

Un elemento debe migrar a pack si cumple al menos una condición:

1. Cambia al agregar una fórmula, rubro, patología, benchmark, síntoma o variable organizacional.
2. No es una regla universal del kernel.
3. Puede variar por país, sector, vertical, tipo de PyME o modelo operativo.
4. Podría ser versionado sin cambiar el core.
5. Hoy obliga a modificar Python para ampliar conocimiento de dominio.

Un elemento debe permanecer en kernel si cumple estas condiciones:

1. Define contratos, estados universales, validaciones estructurales o fail-closed.
2. No contiene conocimiento sectorial ni fórmula específica.
3. Se limita a cargar, validar, rechazar, registrar o bloquear.
4. No confirma hallazgos por sí mismo.

---

# 1. Mapa general de contaminación kernel ↔ dominio

| Ubicación actual | Elemento hardcodeado | Clasificación | Destino futuro | Prioridad | Motivo |
|---|---|---|---|---|---|
| `pymia/contracts/formula_contract.py` | `SUPPORTED_FORMULAS` con 17 fórmulas | `PACK_CANDIDATE` | `FormulaPack` | P0 | Nueva fórmula requiere tocar contrato Python. |
| `pymia/services/formula_engine_service.py` | Branches `if formula_id == ...` con lógica de cálculo | `PACK_CANDIDATE` / `ENGINE_BOUNDARY` | `FormulaPack` + executor seguro | P0 | La expresión/lógica de fórmula vive dentro del servicio. |
| `pymia/diagnostic_core/core.py` | `_pathology_for_formula()` con mapping `formula_id → pathology_code` | `PACK_CANDIDATE` | `PathologyPack` o metadata de `FormulaPack` | P0 | El core contiene vínculo clínico-operativo de dominio. |
| `pymia/smartpyme/anamnesis_fsm.py` | Tuplas de opciones visibles al dueño | `PACK_CANDIDATE` | `CatalogPack` | P1 | Las opciones cambian por contexto, sector o estrategia conversacional. |
| `pymia/smartpyme/anamnesis_fsm.py` | Funciones `_map_*` | `PACK_CANDIDATE` | `DomainPack` | P1 | Mapean lenguaje del dueño a categorías de dominio. |
| `pymia/smartpyme/anamnesis_fsm.py` | Funciones `_detect_*` | `PACK_CANDIDATE` | `DomainPack` / `SectorPack` | P1 | Contienen keywords y síntomas sectoriales. |
| `pymia/services/catalog_loader_v1.py` | `_DOCS_DIR = _REPO_ROOT / "docs"` | `ARCHITECTURAL_RISK` | `PackRegistry` | P1 | El loader está acoplado a docs del repo, no a registry configurable. |
| `pymia/services/pathology_knowledge_tank.py` | `LocalPathologyKnowledgeTank` con patología local hardcodeada | `PACK_CANDIDATE_WITH_ADAPTER` | `PathologyPack` | P1 | Ya existe forma conceptual enchufable, pero el corpus local está hardcodeado. |
| `pymia/contracts/catalogs_v1.py` | `FormulaCatalogV1` y `PathologyCatalogV1` | `BRIDGE_CANDIDATE` | Base contractual para `FormulaPack` / `PathologyPack` | P1 | Puede servir como puente, pero todavía no es Pack System. |
| `docs/formula_catalog.v1.json` | Catálogo documental de fórmulas | `MIGRATION_SOURCE` | `FormulaPack` semilla | P1 | Ya contiene metadata rica, pero vive en docs. |
| `docs/pathology_catalog.v1.json` | Catálogo documental de patologías | `MIGRATION_SOURCE` | `PathologyPack` semilla | P1 | Ya contiene conocimiento de patología, pero no pack validado. |

---

# 2. Formula boundary

## 2.1 Ubicaciones auditadas

- `pymia/contracts/formula_contract.py`
- `pymia/services/formula_engine_service.py`
- `docs/formula_catalog.v1.json`
- `pymia/contracts/catalogs_v1.py`

## 2.2 Conocimiento hardcodeado detectado

### 2.2.1 Definiciones de fórmula

En `formula_contract.py`, `SUPPORTED_FORMULAS` declara fórmulas con:

- `formula_id`
- `required_inputs`
- `description`

Ejemplos auditados:

- `margen_bruto`
- `ganancia_bruta`
- `REN_001_margen_neto_real`
- `LIQ_001_vendido_cobrado`
- `INV_002_rotacion_stock`
- `INV_001_punto_reposicion`
- `PYME_011_dso`
- `PYME_013_dso_dpo_gap`
- `LIQ_002_saldo_final_proyectado`
- `PYME_024_liquidez_corriente`
- `PYME_017_pricing_drift`
- `punto_equilibrio_ventas`
- `PYME_026_flujo_operativo`
- `PYME_027_intereses_ebitda`
- `PYME_044_margen_cliente`
- `PYME_033_concentracion_sku`
- `REN_002_coeficiente_reposicion`

### 2.2.2 Lógica de cálculo

En `formula_engine_service.py`, `FormulaEngineService.calculate()` contiene branches por `formula_id`.

El servicio resuelve:

- fórmula no soportada;
- inputs faltantes;
- divisiones por cero;
- cálculo específico;
- fórmula no implementada.

## 2.3 Clasificación

| Elemento | Clasificación | Destino |
|---|---|---|
| IDs de fórmulas | `PACK_CANDIDATE` | `FormulaPack` |
| Required inputs | `PACK_CANDIDATE` | `FormulaPack` |
| Description / expression | `PACK_CANDIDATE` | `FormulaPack` |
| Categoría / unidad / interpretación | `PACK_CANDIDATE` | `FormulaPack` |
| Manejo universal de missing inputs | `KERNEL_OK` | Kernel / engine |
| Manejo universal de unsupported formula | `KERNEL_OK` | Kernel / engine |
| Manejo universal de division by zero | `KERNEL_OK` si está parametrizado | Kernel / engine |
| Branch por formula_id | `PACK_CANDIDATE` | `FormulaPack` + executor seguro |

## 2.4 Regla futura de migración

No migrar todavía.

Antes debe existir:

1. `PACK_SYSTEM_CONTRACT_V1.md`
2. `FormulaPack` schema
3. `FormulaPack` validator
4. `FormulaPack` fixture semilla
5. Compat layer que preserve comportamiento actual
6. Tests de equivalencia contra `SUPPORTED_FORMULAS`

## 2.5 Riesgo de migración

Riesgo principal:

```text
Si se extrae SUPPORTED_FORMULAS sin compat layer, DiagnosticCoreV1 puede quedar sin fórmulas calculables.
```

Regla fail-closed futura:

```text
Si FormulaPack no carga o no valida, el sistema debe bloquear con motivo explícito, no inventar fórmula ni resultado.
```

---

# 3. Pathology boundary

## 3.1 Ubicaciones auditadas

- `pymia/diagnostic_core/core.py`
- `pymia/contracts/pathology_contract.py`
- `pymia/services/pathology_engine_service.py`
- `pymia/services/pathology_knowledge_tank.py`
- `docs/pathology_catalog.v1.json`
- `pymia/contracts/catalogs_v1.py`

## 3.2 Conocimiento hardcodeado detectado

### 3.2.1 Mapping fórmula → patología en core

En `diagnostic_core/core.py`, `_pathology_for_formula()` resuelve:

```text
REN_001* → REN_001
LIQ_001* → LIQ_001
si hay hypothesis_codes → primer código
fallback → UNSPECIFIED
```

Clasificación:

```text
PACK_CANDIDATE → PathologyPack / FormulaPack metadata
```

Motivo:

```text
DiagnosticCoreV1 no debe contener conocimiento de vinculación fórmula-patología.
```

### 3.2.2 Tanque local de patología

En `pathology_knowledge_tank.py`, `LocalPathologyKnowledgeTank` contiene:

```text
margen_bruto_negativo
formula_id = margen_bruto
severity = HIGH
suggested_action = Revisar costos o precios de venta
category = rentabilidad
source = local_chip1
```

Clasificación:

```text
PACK_CANDIDATE_WITH_ADAPTER
```

Motivo:

```text
Ya existe una interfaz conceptual enchufable (`PathologyKnowledgeTank`), pero el corpus local y el evaluador están hardcodeados.
```

## 3.3 Clasificación

| Elemento | Clasificación | Destino |
|---|---|---|
| `PathologyDefinition` | `KERNEL_CONTRACT_OK` | Contrato base |
| `PathologyFinding` | `KERNEL_CONTRACT_OK` | Contrato base |
| `PathologyEngineService` | `KERNEL_OK_WITH_PACK_PORT` | Servicio consumidor de pack/tank |
| `LocalPathologyKnowledgeTank._definitions` | `PACK_CANDIDATE` | `PathologyPack` |
| `LocalPathologyKnowledgeTank._metadata` | `PACK_CANDIDATE` | `PathologyPack` |
| `LocalPathologyKnowledgeTank._evaluators` | `PACK_CANDIDATE` / `ENGINE_POLICY` | Evaluador seguro parametrizable |
| `_pathology_for_formula()` | `PACK_CANDIDATE` | `PathologyPack` / `FormulaPack` metadata |

## 3.4 Regla futura de migración

No migrar todavía.

Antes debe existir:

1. Contrato de `PathologyPack`.
2. Regla sobre umbrales/evaluadores: declarativos vs funciones Python.
3. Resolver explícito fórmula → patología.
4. Test de cobertura de todas las fórmulas activas.
5. Test de no confirmación automática de findings.

## 3.5 Riesgo de migración

Riesgo principal:

```text
Migrar patologías sin resolver cómo se evalúan umbrales puede convertir packs en ejecución arbitraria.
```

Regla futura:

```text
PathologyPack debe ser declarativo por defecto. Si algún evaluador requiere código, debe pasar por contrato separado y lista blanca.
```

---

# 4. Anamnesis / Catalog boundary

## 4.1 Ubicación auditada

- `pymia/smartpyme/anamnesis_fsm.py`
- `pymia/smartpyme/anamnesis_fsm_integration.py`
- `docs/adr/ADR-010-conversational-anamnesis-contract.md`
- `docs/adr/ADR-024-pack-system-foundation.md`

## 4.2 Opciones hardcodeadas detectadas

| Elemento | Tipo | Destino futuro |
|---|---|---|
| `ACTIVITY_OPTIONS` | Opciones visibles | `CatalogPack` |
| `SALES_CHANNEL_OPTIONS` | Opciones visibles | `CatalogPack` |
| `DIGITAL_PRESENCE_OPTIONS` | Opciones visibles | `CatalogPack` |
| `CATALOG_OPTIONS` | Opciones visibles | `CatalogPack` |
| `TEAM_SIZE_OPTIONS` | Opciones visibles | `CatalogPack` |
| `TOOLS_OPTIONS` | Opciones visibles | `CatalogPack` |
| `PAIN_OPTIONS` | Opciones visibles | `CatalogPack` |
| `PERIOD_OPTIONS` | Opciones visibles | `CatalogPack` |
| `EVIDENCE_OPTIONS` | Opciones visibles | `CatalogPack` |

## 4.3 Mapeos hardcodeados detectados

| Función | Rol | Destino futuro |
|---|---|---|
| `_map_activity_type()` | Texto/respuesta → actividad normalizada | `DomainPack` |
| `_map_sales_channels()` | Texto/respuesta → canales | `DomainPack` / `CatalogPack` |
| `_map_digital_presence()` | Texto/respuesta → presencia digital | `DomainPack` / `CatalogPack` |
| `_map_catalog()` | Texto/respuesta → tipo catálogo | `DomainPack` / `CatalogPack` |
| `_map_team_size()` | Texto/respuesta → tamaño equipo | `DomainPack` |
| `_map_tools()` | Texto/respuesta → herramienta principal | `DomainPack` |
| `_map_primary_pain()` | Texto/respuesta → dolor operativo | `DomainPack` |
| `_map_period()` | Texto/respuesta → período | `DomainPack` |
| `_map_evidence()` | Texto/respuesta → evidencia disponible | `DomainPack` / `CatalogPack` |

## 4.4 Detectores hardcodeados detectados

| Función | Rol | Destino futuro |
|---|---|---|
| `_detect_organism_type()` | Keywords → tipo de organismo PyME | `SectorPack` / `DomainPack` |
| `_detect_sales_channels()` | Keywords → canales | `DomainPack` |
| `_detect_areas()` | Keywords → áreas operativas | `DomainPack` |
| `_detect_flow()` | Keywords → flujo operativo | `DomainPack` / `SectorPack` |
| `_detect_systems()` | Keywords → sistemas disponibles | `DomainPack` |
| `_detect_symptoms()` | Keywords → síntomas | `DomainPack` / `PathologyPack candidate` |

## 4.5 Qué debe permanecer en la FSM

| Elemento | Clasificación | Motivo |
|---|---|---|
| `FSMPhase` | `KERNEL_OK` | Estados conversacionales universales del flujo. |
| `FICHA_PYME_STEPS` | `KERNEL_OK_WITH_REVIEW` | Secuencia base universal; puede parametrizarse después, pero no debe migrarse primero. |
| `AnamnesisFSMState` | `KERNEL_OK` | Estado de proceso, no conocimiento de dominio. |
| `_advance_profile()` | `KERNEL_OK_WITH_PACK_INPUTS` | Orquesta avance; debe consumir catálogos/mapeos inyectados en el futuro. |
| `_profile_state()` | `KERNEL_OK` | Ensambla estado y mensaje. |
| `process_message()` | `KERNEL_OK` | Orquesta fase. No debe saber dominio específico. |

## 4.6 Riesgo de migración

Riesgo principal:

```text
Si se extraen opciones sin fallback, la FSM queda muda o no puede avanzar.
```

Regla futura:

```text
La FSM debe conservar una política fail-closed: si no hay CatalogPack válido, debe responder con bloqueo explicativo o usar un catálogo base versionado explícito.
```

---

# 5. Catalog loader / Registry boundary

## 5.1 Ubicaciones auditadas

- `pymia/services/catalog_loader_v1.py`
- `docs/formula_catalog.v1.json`
- `docs/pathology_catalog.v1.json`
- `pymia/contracts/catalogs_v1.py`

## 5.2 Estado actual

`catalog_loader_v1.py` permite path inyectable en funciones, pero default hardcodea:

```text
_DOCS_DIR = _REPO_ROOT / "docs"
```

Esto permite cargar catálogos documentales actuales, pero no constituye Pack Registry.

## 5.3 Clasificación

| Elemento | Clasificación | Futuro destino |
|---|---|---|
| `load_formula_catalog_v1(path=None)` | `BRIDGE_OK` | Puede adaptarse a registry. |
| `load_pathology_catalog_v1(path=None)` | `BRIDGE_OK` | Puede adaptarse a registry. |
| `_DOCS_DIR` default | `ARCHITECTURAL_RISK` | Reemplazar por registry/config explícita. |
| `validate_formula_pathology_links()` | `KERNEL_OK` | Validación útil para packs. |
| `get_candidate_formula_ids_by_pathology_codes()` | `KERNEL_OK_WITH_PACK_SOURCE` | Debe consumir FormulaPack/PathologyPack futuro. |

## 5.4 Regla futura

No reemplazar `catalog_loader_v1.py` abruptamente.

Primero debe crearse:

```text
PackRegistry documental / contractual
```

Luego:

```text
catalog_loader_v1.py → compat layer hacia registry
```

---

# 6. Kernel elements that must not migrate

| Elemento | Ubicación | Clasificación | Motivo |
|---|---|---|---|
| `ReceptionRecord` | `reception.py` | `KERNEL_OK` | Registro universal de recepción. |
| `EvidenceRecord` | `evidence.py` | `KERNEL_OK` | Registro de evidencia, no dominio. |
| `StructuredEvidence` | `evidence_v1.py` | `KERNEL_OK` | Contrato de evidencia estructurada. |
| `EvidenceSufficiencyResult` | `evidence_gate.py` | `KERNEL_OK` | Gate universal. |
| `DiagnosticCoreResult` | `diagnostic_core/models.py` | `KERNEL_OK` | Resultado estructural del core. |
| `CoreFinding.status = CANDIDATE` | `diagnostic_core/core.py` | `DO_NOT_TOUCH` | Garantiza no confirmación automática. |
| `OwnerFacingReport` | `owner_facing_report.py` | `KERNEL_OK` | Traducción controlada, no diagnóstico nuevo. |
| `OwnerQuestionsBundle` | `owner_questions.py` | `KERNEL_OK` | Preguntas trazables al dueño. |
| `OwnerAnswersBundle` | `owner_answers.py` | `KERNEL_OK` | Respuestas como artefacto, no evidencia dura automática. |
| `PymIAState` | `orchestration/state.py` | `KERNEL_OK` | Estado conversacional. |
| `graph.py` fail-closed orchestration | `orchestration/graph.py` | `KERNEL_OK_WITH_COMPLEXITY` | Orquestación actual; no mover a pack. |

---

# 7. Síntesis de migraciones futuras

## 7.1 Secuencia correcta

```text
SUPERAUDITORIA_INFORME_0
→ ADR-024 Accepted
→ PACK_BOUNDARY_CODE_RECONCILIATION
→ PACK_SYSTEM_CONTRACT_V1
→ Pack Schema
→ Pack Registry contract
→ FormulaPack seed
→ FormulaPack compatibility layer
→ PathologyPack resolver
→ CatalogPack/DomainPack for anamnesis
```

## 7.2 Secuencia prohibida

```text
ADR-024 Accepted
→ tocar diagnostic_core directamente
→ borrar SUPPORTED_FORMULAS
→ mover opciones de anamnesis sin fallback
→ crear packs ejecutables sin schema
→ correr tests para justificar arquitectura ausente
```

---

# 8. Riesgos priorizados

| Riesgo | Severidad | Evidencia | Mitigación documental |
|---|---|---|---|
| FormulaPack sin compat layer rompe core | Alta | `FormulaEngineService` depende de `SUPPORTED_FORMULAS` y branches por ID | Definir contrato + tests de equivalencia antes de migrar. |
| PathologyPack con evaluadores arbitrarios introduce ejecución no controlada | Alta | `LocalPathologyKnowledgeTank` usa evaluador Python local | Definir si patologías son declarativas o requieren evaluadores whitelisted. |
| FSM pierde fluidez al extraer catálogos | Alta | `anamnesis_fsm.py` arma mensajes con tuplas locales | Definir catálogo base obligatorio y fallback fail-closed. |
| Pack Registry duplica `catalog_loader_v1.py` | Media | Ya hay loader con path opcional | Crear compat layer, no reemplazo brusco. |
| KnowledgeTanks vs Pack System quedan como arquitecturas paralelas | Alta | `SMARTPYME_KNOWLEDGE_TANKS_*` existe como diseño previo | Reconciliar en auditoría o ADR posterior. |
| Memoria operativa se vuelve fuente canónica | Media | `Pymia-memoria/` actualizado, pero debe seguir MEMORY_ONLY | Mantener AGENTS/DOCUMENTATION_INDEX como autoridad. |

---

# 9. Próximas auditorías a registrar

Para llegar a una síntesis atómica, las próximas auditorías documentales deben acumularse en este orden:

1. `PACK_BOUNDARY_CODE_RECONCILIATION.md` — este documento.
2. `KNOWLEDGETANKS_PACKSYSTEM_RECONCILIATION_AUDIT.md` — reconciliar KnowledgeTanks con Pack System.
3. `DOCUMENTATION_AUTHORITY_LEDGER.md` — ledger de auditorías documentales y de código.
4. `OWNER_INTERACTION_ATOMIC_TRACE.md` — traza mínima Dueño → Evidencia → Core → Reporte → Reentry.
5. `PYMIA_ATOMIC_SYNTHESIS.md` — síntesis final reducida a invariantes, fronteras y próximos 3 frentes.

---

# 10. Criterio de síntesis atómica

La síntesis atómica futura debe poder responder en menos de una página:

```text
Qué es PymIA.
Qué no es PymIA.
Cuál es su kernel.
Qué entra como pack.
Qué decide el dueño.
Qué decide el kernel.
Qué queda bloqueado sin evidencia.
Qué documentos mandan.
Qué código representa cada frontera.
Cuál es el próximo paso autorizado.
```

Si no puede responder eso, todavía falta coherentización.

---

# 11. Veredicto

`PASS_DOCUMENTARY_DRAFT`

Este documento registra la frontera actual kernel ↔ dominio y ordena las migraciones futuras sin ejecutar ninguna.

Queda pendiente:

```text
PACK_SYSTEM_CONTRACT_V1
```

Pero antes conviene cerrar:

```text
KNOWLEDGETANKS_PACKSYSTEM_RECONCILIATION_AUDIT
```

para no crear un Pack Contract que contradiga los KnowledgeTanks históricos de SmartPyme.
