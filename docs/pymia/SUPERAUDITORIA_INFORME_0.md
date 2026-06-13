# SUPERAUDITORÍA PYMIA / SMARTPYME — INFORME 0

## Metadata

| Campo | Valor |
|---|---|
| **Estado** | CLOSED_DOCUMENTARY_AUDIT |
| **Fecha** | 2026-06-12 |
| **Propósito** | Evidencia base para ADR-024 Pack System Foundation |
| **Alcance** | Reconciliación documental + dimensión interaccional PymIA–Dueño |
| **Pregunta central** | ¿PymIA puede recibir caos del dueño PyME, pedir evidencia, clasificar, diagnosticar sin inventar, generar hallazgos y sostener continuidad sin contaminar el kernel con conocimiento de dominio? |

---

## 1. Archivos auditados

### 1.1 Código kernel

| Archivo | Zona | Responsabilidad |
|---|---|---|
| `pymia/contracts/formula_contract.py` | Contratos | Definición de fórmulas soportadas |
| `pymia/diagnostic_core/core.py` | Core diagnóstico | Ejecución de fórmulas y generación de findings |
| `pymia/smartpyme/anamnesis_fsm.py` | Anamnesis | FSM determinística para ficha PyME |
| `pymia/smartpyme/reception.py` | Recepción | Captura de mensaje crudo y clasificación |
| `pymia/smartpyme/evidence_gate.py` | Gate evidencia | Evaluación de suficiencia de evidencia |
| `pymia/services/catalog_loader_v1.py` | Carga catálogos | Lectura de catálogos desde filesystem |
| `pymia/narrative/report_generator.py` | Narrativa | Generación de reportes para dueño |
| `pymia/orchestration/graph.py` | Orquestación | Grafo de ejecución con reentry de dueño |

### 1.2 Documentación arquitectónica

| Archivo | Rol |
|---|---|
| `AGENTS.md` | Contrato de arranque para agentes |
| `ARCHITECTURE_GUARDRAILS.md` | Invariantes arquitectónicos |
| `docs/pymia/PYMIA_DEVELOPMENT_METHOD.md` | Método de desarrollo |
| `docs/pymia/M34_DIAGNOSTIC_CORE_V1_CLOSURE.md` | Cierre histórico del núcleo |
| `docs/pymia/M35_EVIDENCE_TO_CORE_CHECKPOINT.md` | Binding evidencia → core |
| `docs/contratos/evidence-chain-v1.md` | Contrato cadena de evidencia |
| `docs/contratos/owner-decision-v1.md` | Contrato decisión del dueño |

---

## 2. Hallazgos críticos

### 2.1 Fórmulas hardcodeadas en `formula_contract.py`

**Archivo:** `pymia/contracts/formula_contract.py`

**Hallazgo:** 17 fórmulas definidas como dict `SUPPORTED_FORMULAS` dentro del kernel.

**Riesgo:**
- Kernel acoplado a catálogo de fórmulas específico.
- Nueva fórmula requiere modificar código del core.
- Viola principio "conocimiento de dominio es enchufable".

**Clasificación:** `PACK_CANDIDATE`

**Acción recomendada:** Migrar a `FormulaPack` externo cargado vía `catalog_loader_v1` (o equivalente). Kernel solo valida schema.

---

### 2.2 Mapping fórmula → patología hardcodeado en `diagnostic_core/core.py`

**Archivo:** `pymia/diagnostic_core/core.py`

**Hallazgo:** Método `_pathology_for_formula` mapea `formula_id` → `pathology_code` con if/elif dentro del core.

**Riesgo:**
- Lógica de vinculación fórmula-patología dentro del core.
- Nueva patología requiere modificar código del core.
- DiagnosticCore convertido en catálogo clínico.

**Clasificación:** `PACK_CANDIDATE`

**Acción recomendada:** Debe resolverse vía catálogo externo (`FormulaCatalog` ya tiene `pathology_code`). Eliminar hardcode.

---

### 2.3 Opciones y mapeos de anamnesis hardcodeados en `anamnesis_fsm.py`

**Archivo:** `pymia/smartpyme/anamnesis_fsm.py`

**Hallazgo:**
- Opciones de actividad, rubro, dolor, canales, herramientas hardcodeadas como tuplas Python.
- Métodos `_map_activity_type`, `_map_primary_pain` contienen lógica de mapeo sectorial.

**Riesgo:**
- Anamnesis base contaminada con taxonomía de dominio.
- Cambiar opciones = tocar código.
- Semántica de negocio incrustada en kernel conversacional.

**Clasificación:** `AMBIGUOUS_BOUNDARY`, `ARCHITECTURAL_RISK`

**Acción recomendada:** Extraer a `SectorPack` / `CatalogPack`. FSM recibe opciones como parámetro inyectable. Mover mapeos a pack de dominio.

---

### 2.4 `catalog_loader_v1` acoplado a `docs/`

**Archivo:** `pymia/services/catalog_loader_v1.py`

**Hallazgo:** Ruta hardcoded `_DOCS_DIR = _REPO_ROOT / "docs"`.

**Riesgo:**
- Catálogos viven en repo, no son packs versionados independientes.
- No hay mecanismo para cargar packs desde ubicaciones externas.

**Clasificación:** `ARCHITECTURAL_RISK`

**Acción recomendada:** Definir contrato de carga que acepte path inyectable o registry de packs.

---

## 3. Veredicto

### **PARTIAL**

**Justificación:**

El kernel de PymIA es sólido, determinístico y fail-closed en sus capas críticas:
- `reception.py`: captura pura sin dominio hardcodeado.
- `evidence_gate.py`: evaluación determinística, fail-closed.
- `diagnostic_core/core.py`: ejecuta fórmulas, genera findings CANDIDATE, bloquea si faltan inputs.
- `orchestration/graph.py`: fail-closed, lazy imports, owner answer reentry implementado.

Los contratos de evidencia y decisión del dueño están bien definidos:
- `evidence-chain-v1.md`: cliente_id obligatorio, inferencia ≠ hallazgo confirmado.
- `owner-decision-v1.md`: SmartPyme propone, dueño decide.

La interacción PymIA ↔ dueño tiene traza completa desde recepción hasta reentry.

**Sin embargo:**

La frontera kernel ↔ packs **no está implementada**. Las fórmulas, patologías, opciones de anamnesis y mapeos semánticos viven dentro del kernel como código Python hardcodeado. Esto viola la decisión arquitectónica obligatoria:

```
El conocimiento de dominio es enchufable.
El kernel permanece estable.
```

La arquitectura deseada (Pack System) no tiene asidero real en el código. Los artefactos `DomainPack`, `KnowledgePack`, `FormulaPack`, `PathologyPack`, `SectorPack`, `CatalogPack` no existen.

---

## 4. Conclusión

Se requiere **frontera formal kernel ↔ packs** para:

1. **Estabilidad del kernel:** El core no se modifica al agregar conocimiento de dominio.
2. **Escalabilidad:** Nuevas verticales se agregan como packs, no como código.
3. **Versionado:** Cada pack tiene ciclo de vida independiente.
4. **Validación:** Packs se validan contra contrato antes de activarse.
5. **Rechazo:** Packs problemáticos se rechazan sin afectar operación.
6. **Fail-closed:** Kernel continúa operando aunque un pack falle.
7. **Claridad:** Frontera kernel ↔ dominio definida formalmente.
8. **Gobernanza:** DiscoveryMemory sugiere packs, humano decide.
9. **Separación:** LearningMemory y KnowledgePack son conceptos distintos.

**Acción inmediata:** Revisar y aceptar ADR-024 Pack System Foundation como decisión rectora para futuras migraciones kernel ↔ packs, antes de cualquier migración de fórmulas o desacople de anamnesis.

---

## 5. Próximos pasos autorizados

Este informe autoriza:

1. **ADR-024 Pack System Foundation** — Definición formal del sistema de packs.
2. **PACK_SYSTEM_CONTRACT_V1.md** — Contrato técnico detallado.
3. **Migraciones futuras** (solo después de ADR aprobado):
   - Fórmulas desde `formula_contract.py` → `FormulaPack`
   - Pathology mapping desde `diagnostic_core/core.py` → `PathologyPack`
   - Opciones/mapeos desde `anamnesis_fsm.py` → `CatalogPack` / `DomainPack`
   - Catálogos desde `docs/` → registry de packs

Este informe **NO autoriza**:
- Modificación de código.
- Ejecución de tests.
- Migración inmediata de fórmulas, anamnesis o catálogos.
- Creación de packs sin ADR aprobado.

---

**Documento cerrado.** Este informe sirve como evidencia base para ADR-024 y futuras decisiones arquitectónicas.
