# SMARTPYME_KNOWLEDGE_TANKS_ARCHITECTURE

Estado: **DISEÑO v1 — Subarquitectura de tanques (sin implementación runtime)**

---

## 1. Estado y propósito

Este documento diseña la **subarquitectura interna** de KnowledgeTanks y DomainPacks para SmartPyme.

**No es implementación.**
**No habilita capacidades runtime nuevas.**
**No reemplaza el contrato existente** (`SMARTPYME_KNOWLEDGE_TANKS_CONTRACT.md`).

Este documento **complementa** el contrato definiendo:

- ciclo de vida completo de un tanque;
- estados y transiciones;
- política de activación/desactivación;
- resolución de conflictos;
- estructura de `TankSelectionResult`;
- composición de DomainPacks;
- ejemplos end-to-end;
- criterios de aceptación para futura implementación.

**Regla rectora:** Git/runtime real manda sobre documentación aspiracional.

---

## 2. Problema arquitectónico

El conocimiento PyME estaba disperso y embebido rígidamente, generando:

### 2.1 Conocimiento embebido en código

- Lógica de diagnóstico hardcodeada en clasificaciones específicas.
- Imposibilidad de agregar industria sin tocar runtime.
- Reglas de activación implícitas en prompts.

### 2.2 Mezcla de dominios

- Análisis financiero arrastrando reglas de stock.
- Tanque de proveedores emitiendo afirmaciones sobre margen.
- Falta de aislamiento entre capacidades.

### 2.3 Diagnóstico prematuro

- Sistema afirmando patologías sin evidencia suficiente.
- Activación por señales débiles (un selector aislado).
- Confusión entre "candidato" y "confirmado".

### 2.4 Activación caótica

- No hay política clara de cuándo cargar/descargar tanques.
- Selectores estructurales activando diagnóstico por sí solos.
- Falta de trazabilidad de qué conocimiento se activó y por qué.

### 2.5 Evidencia excesiva o insuficiente

- Tanques pidiendo todos los documentos posibles.
- Falta de criterio de suficiencia.
- No hay distinción entre evidencia mínima, deseable y bloqueante.

### 2.6 Promesas no soportadas

- Tanques sugiriendo outputs que el runtime no tiene.
- HTML cuando no hay `--html-out`.
- Routing automático cuando no existe.

### 2.7 Falta de versionado

- No hay forma de saber qué versión de conocimiento se aplicó.
- Casos antiguos usando reglas nuevas.
- Imposibilidad de rollback por caso.

### 2.8 Conflictos no resueltos

- Múltiples tanques aplicando simultáneamente sin prioridad.
- Selector contradiciendo relato sin resolución.
- Evidencia contradictoria sin política clara.

---

## 3. Principios rectores

1. **Git/runtime real manda sobre documentación aspiracional.**
   No implementar capacidades que no existen en código.

2. **Un tanque no diagnostica por sí solo.**
   Solo sugiere síntomas, aporta preguntas, define evidencia.

3. **Evidencia antes de afirmación.**
   Ningún tanque emite diagnóstico sin evidencia validada.

4. **Confirmación del usuario antes de cierre semántico.**
   Respetar fase semántico-dialéctica completa.

5. **Selector estructural no activa diagnóstico por sí solo.**
   Los selectores son contexto, no dolor.

6. **Activación y desactivación son simétricamente importantes.**
   Saber cuándo NO usar un tanque es tan crítico como saber cuándo usarlo.

7. **Dominio aislado por defecto.**
   Un tanque de finanzas no emite afirmaciones sobre stock.

8. **Todo tanque debe versionarse.**
   Formato semver, referenciación explícita por caso.

9. **Todo tanque debe declarar límites.**
   Qué NO puede hacer es tan importante como qué puede hacer.

10. **Todo tanque debe declarar outputs permitidos.**
    No prometer lo que el runtime no soporta.

11. **Todo tanque debe ser auditable.**
    Registro de activación, desactivación, conflictos y decisiones.

---

## 4. Ubicación en el flujo SmartPyme

```text
raw_text + structured_selectors
    ↓
[1] InterrogationSlice
    ↓
InterrogationResult
    ↓
[2] TankSelection (evalúa activation_conditions)
    ↓
TankSelectionResult
    ↓
[3] EvidenceRequest (basado en tanques activos)
    ↓
[4] EvidenceCandidate (usuario entrega evidencia)
    ↓
[5] EvidenceValidation (Boundary Layer)
    ↓
[6] ExecutableClassification (excel_diagnostic, supplier_duplicate_check, etc.)
    ↓
[7] Analysis (fórmulas, hipótesis, cálculos)
    ↓
[8] Report (Markdown, JSON, HTML si aplica)
```

**Los tanques se ubican:**

- **Después** de la fase semántico-dialéctica (interrogación).
- **Antes** del análisis.
- **Antes** de routing ejecutable.
- **Antes** de pedir evidencia final.

**Los tanques NO sustituyen:**

- La conversación real.
- La reformulación.
- La confirmación del usuario.
- La validación de evidencia.

---

## 5. Definición operacional de KnowledgeTank

Partiendo del contrato (`SMARTPYME_KNOWLEDGE_TANKS_CONTRACT.md`), un KnowledgeTank es:

**Unidad modular de conocimiento activable/desenchufable que aporta:**

- síntomas soportados;
- dominios;
- preguntas de desambiguación;
- hipótesis abiertas;
- evidencia requerida;
- campos esperados;
- fórmulas ejecutables;
- criterios de suficiencia;
- límites de seguridad;
- warnings;
- compatibilidad runtime;
- outputs permitidos.

### Diferenciación conceptual

| Concepto | Definición |
|---|---|
| **Catálogo** | Lista de elementos (patologías, fórmulas, preguntas) |
| **KnowledgeTank** | Catálogo + políticas + límites + activación + outputs |
| **Capability** | Acción ejecutable (ej: `run_excel_diagnostic`) |
| **Classification** | Ruta de análisis (ej: `supplier_duplicate_check`) |
| **DomainPack** | Composición versionada de tanques por dominio/industria |
| **Report** | Salida posterior al análisis (Markdown, JSON, HTML) |

**Regla fundamental:** Un tanque nunca ejecuta. Solo habilita, sugiere, limita.

---

## 6. Ciclo de vida de un KnowledgeTank

### Estados

| Estado | Significado |
|---|---|
| `DEFINED` | Tanque existe en documentación/YAML pero no está cargado |
| `AVAILABLE` | Tanque cargado y disponible para evaluación |
| `CANDIDATE` | Tanque pasó evaluación inicial de activación |
| `ACTIVE` | Tanque activo, aportando preguntas/evidencia/clasificación |
| `SUSPENDED` | Tanque temporalmente inactivo (puede reactivarse) |
| `DEACTIVATED` | Tanque desactivado para este caso (no aplica) |
| `UNSUPPORTED` | Tanque aplica conceptualmente pero runtime no lo soporta |
| `RETIRED` | Tanque obsoleto, no debe usarse |

### Transiciones detalladas

#### DEFINED → AVAILABLE

**Condición:** Loader YAML carga el tanque en memoria.
**Quién:** Sistema al inicio o hot-reload.
**Ejemplo:** `operational_pathology_core` cargado desde YAML.

#### AVAILABLE → CANDIDATE

**Condición:** `InterrogationResult` cumple `activation_conditions`.
**Quién:** `TankSelection` tras interrogación.
**Ejemplo:** Síntoma `DESCUADRE_DINERO` detectado → tanque pasa a CANDIDATE.

#### CANDIDATE → ACTIVE

**Condición:**
- Contexto mínimo satisfecho.
- Confirmación o no-contradicción del usuario.
- No viola `safety_constraints`.
- Runtime compatible.
**Quién:** `TankSelection` tras validación de gates.
**Ejemplo:** Usuario confirma reformulación → tanque se activa.

#### CANDIDATE → SUSPENDED

**Condición:** Falta contexto/evidencia pero puede aparecer después.
**Quién:** `TankSelection` o usuario corrige relato.
**Ejemplo:** Selector Mercado Libre pero sin relato compatible → SUSPENDED.

#### CANDIDATE → DEACTIVATED

**Condición:** No aplica para este caso.
**Quién:** `TankSelection`.
**Ejemplo:** Tanque de stock pero usuario habla solo de proveedores.

#### ACTIVE → SUSPENDED

**Condición:** Usuario corrige reformulación o aparece contradicción.
**Quién:** Usuario o nueva evidencia.
**Ejemplo:** Usuario dice "no es margen, es caja" → tanque de margen se suspende.

#### ACTIVE → DEACTIVATED

**Condición:** Evidencia invalida hipótesis o conflicto irresoluble.
**Quién:** `EvidenceValidation` o resolución de conflictos.
**Ejemplo:** Evidencia muestra que no hay duplicados → tanque de duplicados se desactiva.

#### ACTIVE → UNSUPPORTED

**Condición:** Tanque sugiere output que runtime no tiene.
**Quién:** `TankSelection` al validar `runtime_capabilities`.
**Ejemplo:** Tanque sugiere HTML pero no hay `--html-out`.

#### AVAILABLE → RETIRED

**Condición:** Versión obsoleta reemplazada por nueva.
**Quién:** Administrador o migración.
**Ejemplo:** `operational_pathology_core v1.0.0` reemplazado por `v2.0.0`.

---

## 7. Tabla de transiciones de estado

| Desde | Hacia | Condición | Ejemplo | Riesgo |
|---|---|---|---|---|
| `DEFINED` | `AVAILABLE` | Loader YAML carga tanque | Sistema inicia | Ninguno |
| `AVAILABLE` | `CANDIDATE` | `activation_conditions` satisfechas | Síntoma detectado | Activación prematura si señal débil |
| `CANDIDATE` | `ACTIVE` | Gates de seguridad pasados | Usuario confirma | Diagnóstico prematuro si se saltea confirmación |
| `CANDIDATE` | `SUSPENDED` | Falta contexto/evidencia | Selector sin relato | Pérdida de información relevante |
| `CANDIDATE` | `DEACTIVATED` | No aplica | Dominio incompatible | Ninguno |
| `ACTIVE` | `SUSPENDED` | Usuario corrige | "No es margen, es caja" | Confusión si no se registra motivo |
| `ACTIVE` | `DEACTIVATED` | Evidencia invalida | No hay duplicados | Ninguno |
| `ACTIVE` | `UNSUPPORTED` | Runtime incompatible | Sugiere HTML sin `--html-out` | Promesa incumplida |
| `SUSPENDED` | `ACTIVE` | Aparece contexto/evidencia | Usuario aporta Excel | Reactivación incorrecta si evidencia insuficiente |
| `SUSPENDED` | `DEACTIVATED` | Caso avanza sin reactivación | Usuario cambia de tema | Ninguno |
| `AVAILABLE` | `RETIRED` | Versión obsoleta | Nueva versión disponible | Casos antiguos con reglas nuevas |

---

## 8. Política de activación

### 8.1 Activación por señales combinadas

Un tanque puede pasar a `CANDIDATE` por combinación de:

| Señal | Peso | Puede activar sola | Observación |
|---|---:|---|---|
| `raw_text` con señal fuerte | Alto | ✅ (como CANDIDATE) | "Tengo proveedores duplicados" |
| `candidate_symptoms` match | Alto | ✅ (como CANDIDATE) | `DATOS_DUPLICADOS` detectado |
| `candidate_domains` match | Medio | ❌ | Necesita síntoma o texto |
| Selector estructural | Bajo | ❌ | Solo refina, no activa |
| `evidence_available` compatible | Medio/Alto | ❌ | Necesita síntoma compatible |
| `suggested_classification` match | Alto | ✅ (como CANDIDATE) | `supplier_duplicate_check` |
| Tipo documental recibido | Alto | ✅ (como CANDIDATE) | Excel de proveedores cargado |

### 8.2 Condiciones para pasar de CANDIDATE a ACTIVE

Un tanque solo puede activarse si:

1. **Contexto mínimo satisfecho** (`required_context`).
2. **Confirmación o no-contradicción** del usuario.
3. **Síntoma/dominio compatible** con `supported_symptoms` y `supported_domains`.
4. **No viola `safety_constraints`**.
5. **Evidencia suficiente** o pregunta/evidence request válida.
6. **No promete output no soportado** por runtime.
7. **Runtime compatible** (`runtime_capabilities`).

### 8.3 Matriz de activación

| Escenario | Señales | Estado resultante |
|---|---|---|
| Texto fuerte + síntoma + selector | Alto + Alto + Bajo | `CANDIDATE` → `ACTIVE` |
| Solo selector | Bajo | `AVAILABLE` (no activar) |
| Texto fuerte + selector incompatible | Alto + Bajo (contradice) | `CANDIDATE` → `SUSPENDED` |
| Síntoma + evidencia compatible | Alto + Medio | `CANDIDATE` → `ACTIVE` |
| Síntoma + evidencia incompatible | Alto + Bajo (contradice) | `CANDIDATE` → `DEACTIVATED` |
| Sugerencia de clasificación + evidencia | Alto + Alto | `CANDIDATE` → `ACTIVE` |

---

## 9. Política de desactivación

### 9.1 Cuándo desactivar

Un tanque debe desactivarse o suspenderse si:

- Usuario **corrige** la reformulación.
- Contexto de organismo **contradice** dominio.
- Evidencia **no coincide** con campos esperados.
- Falta **campo mínimo** requerido.
- Runtime **no soporta** output sugerido.
- Otro tanque **más específico** lo reemplaza.
- Selector era **falso positivo**.
- Riesgo de **diagnóstico prematuro**.

### 9.2 Diferencia entre SUSPENDED y DEACTIVATED

| Estado | Significado | Puede reactivarse |
|---|---|---|
| `SUSPENDED` | Temporalmente inactivo, puede aplicar después | ✅ Sí |
| `DEACTIVATED` | No aplica para este caso | ❌ No |
| `UNSUPPORTED` | Aplica conceptualmente pero runtime no soporta | ❌ No (salvo upgrade) |
| `RETIRED` | Obsoleto, no debe usarse | ❌ No |

### 9.3 Ejemplos de desactivación

| Motivo | Estado | Ejemplo |
|---|---|---|
| Usuario corrige | `SUSPENDED` | "No es margen, es caja" |
| Evidencia invalida | `DEACTIVATED` | Excel muestra 0 duplicados |
| Runtime incompatible | `UNSUPPORTED` | Sugiere HTML sin `--html-out` |
| Conflicto irresoluble | `DEACTIVATED` | Dos tanques con hipótesis incompatibles |
| Versión obsoleta | `RETIRED` | `v1.0.0` reemplazado por `v2.0.0` |

---

## 10. Resolución de conflictos

### 10.1 Conflictos posibles

1. **Múltiples tanques aplican.**
   Ejemplo: `operational_pathology_core` y `evidence_formula_core` ambos candidatos.

2. **Selector contradice relato.**
   Ejemplo: Selector "Mercado Libre" pero texto habla de "local físico".

3. **Evidencia contradice relato.**
   Ejemplo: Usuario dice "tengo duplicados" pero Excel muestra 0 duplicados.

4. **Un tanque pide evidencia excesiva.**
   Ejemplo: Tanque pide 5 tipos de documento simultáneamente.

5. **Dos tanques piden documentos distintos.**
   Ejemplo: Uno pide Excel ventas, otro pide Excel stock.

6. **Un tanque sugiere clasificación no implementada.**
   Ejemplo: Tanque sugiere `stock_reconciliation` pero no existe en runtime.

7. **Un tanque sectorial contradice tanque transversal.**
   Ejemplo: Tanque Mercado Libre dice "comisiones 15%" pero tanque general dice "revisar costos".

8. **Dos tanques generan hipótesis incompatibles.**
   Ejemplo: Uno dice "margen erosionado", otro dice "margen saludable".

### 10.2 Regla de prioridad

Orden de resolución (de mayor a menor prioridad):

1. **Safety** (no violar `safety_constraints`).
2. **Evidencia** (evidencia validada > relato).
3. **Confirmación/corrección del usuario** (usuario > sistema).
4. **Compatibilidad runtime** (solo lo que el runtime soporta).
5. **Especificidad** (tanque sectorial > tanque transversal).
6. **Menor carga documental** (pedir menos evidencia).
7. **Amplitud del DomainPack** (pack completo > tanque aislado).

### 10.3 Ejemplos de resolución

| Conflicto | Resolución |
|---|---|
| Múltiples tanques aplican | Activar todos los compatibles, registrar en `selected_tanks` |
| Selector contradice relato | Priorizar relato, suspender tanque sectorial |
| Evidencia contradice relato | Priorizar evidencia, desactivar tanque |
| Tanque pide >3 documentos | Limitar a 3, priorizar por `sufficiency_criteria` |
| Dos tanques piden documentos distintos | Combinar requests si son compatibles, sino priorizar por especificidad |
| Clasificación no implementada | Marcar tanque como `UNSUPPORTED`, no sugerir clasificación |
| Tanque sectorial vs transversal | Priorizar sectorial si evidencia compatible, sino transversal |
| Hipótesis incompatibles | Registrar conflicto, pedir desambiguación al usuario |

---

## 11. Evidence sufficiency policy

### 11.1 Tipos de evidencia

| Tipo | Definición | Ejemplo |
|---|---|---|
| **Mínima** | Indispensable para activar tanque | Proveedor + CUIT para duplicados |
| **Deseable** | Mejora calidad de análisis | Proveedor + CUIT + razón social |
| **Bloqueante** | Si falta, no se puede analizar | Ausencia de proveedor |
| **Opcional** | Enriquece pero no bloquea | Domicilio, email, categoría |
| **Contradictoria** | Invalida hipótesis | Excel muestra 0 duplicados |
| **Insuficiente pero orientadora** | No alcanza para diagnóstico pero da pistas | Ventas solas (sin costos) |

### 11.2 Ejemplos por síntoma

#### Proveedores duplicados

- **Mínima:** `proveedor` + (`cuit` o `razon_social`).
- **Deseable:** `proveedor` + `cuit` + `razon_social`.
- **Opcional:** `domicilio`, `email`, `categoría`.
- **Bloqueante:** Ausencia de `proveedor`.

#### Margen dudoso

- **Mínima:** `ventas` + (`costo` o `lista_precios`).
- **Deseable:** `ventas` + `costo` + `fecha` + `producto`.
- **Bloqueante:** `ventas` sin `costo` si se quiere calcular margen.
- **Orientadora:** `ventas` solas permiten detectar columnas/faltantes pero no margen.

#### Stock inconsistente

- **Mínima:** `stock_sistema` + (`stock_real` o `movimientos`).
- **Deseable:** `producto` + `stock_sistema` + `stock_real` + `fecha`.
- **Bloqueante:** Ausencia de `producto`.
- **Orientadora:** Solo `stock_sistema` permite detectar faltantes pero no inconsistencia.

### 11.3 Criterio de suficiencia

Un tanque puede emitir `EvidenceRequest` solo si:

- Evidencia mínima está disponible o puede solicitarse.
- No se piden más de 3 tipos de evidencia simultáneamente.
- Cada tipo de evidencia tiene `required_fields` claros.
- Hay `sufficiency_criteria` explícitos (ej: ">= 3 meses de datos").

---

## 12. TankSelectionResult

### 12.1 Contrato conceptual

```yaml
tank_selection_result:
  tenant_id: <tenant>
  conversation_id: <conv>
  timestamp: <ISO8601>
  
  input_summary:
    raw_input_length: 120
    structured_selectors_present: true
    symptoms_detected: [DESCUADRE_DINERO, MARGEN_DUDOSO]
    domains_detected: [finanzas, comercial]
    interrogation_status: NEEDS_EVIDENCE
  
  selected_tanks:
    - tank_id: operational_pathology_core
      version: "1.0.0"
      lifecycle_state: ACTIVE
      activation_score: 0.85
      activation_reasons:
        - symptom_match: DESCUADRE_DINERO
        - domain_match: finanzas
      supported_outputs:
        - candidate_pathologies
        - clarifying_questions
        - evidence_requirements
      next_action: request_evidence
  
  candidate_tanks:
    - tank_id: evidence_formula_core
      version: "1.0.0"
      lifecycle_state: CANDIDATE
      activation_score: 0.70
      missing_evidence:
        - excel_ventas_costos
      next_action: wait_for_evidence
  
  suspended_tanks:
    - tank_id: marketplace_specific_ml
      version: "1.0.0"
      lifecycle_state: SUSPENDED
      deactivation_reasons:
        - selector_without_text_support
      can_reactivate: true
  
  rejected_tanks:
    - tank_id: stock_reconciliation
      version: "1.0.0"
      lifecycle_state: DEACTIVATED
      deactivation_reasons:
        - domain_incompatible
      can_reactivate: false
  
  unsupported_tanks:
    - tank_id: advanced_benchmark
      version: "1.0.0"
      lifecycle_state: UNSUPPORTED
      reason: runtime_lacks_sector_data
  
  conflicts:
    - type: multiple_tanks_apply
      tanks: [operational_pathology_core, evidence_formula_core]
      resolution: activate_both
      notes: "Ambos compatibles, sin contradicción"
  
  evidence_requests:
    - evidence_type: excel_ventas_costos
      required_fields: [fecha, producto, precio_venta, costo]
      reason: "Permite contrastar hipótesis de margen erosionado"
      sufficiency_criteria: ">= 3 meses de datos, >= 10 productos"
      enables_hypotheses: [margen_erosionado]
      source_tank: evidence_formula_core
  
  warnings:
    - "Tanque operational_pathology_core activo pero sin evidencia aún"
    - "Máximo 3 tipos de evidencia solicitados"
  
  suggested_next_state: NEEDS_EVIDENCE
  
  suggested_classifications:
    - classification: excel_diagnostic
      confidence: 0.75
      requires_evidence: [excel_ventas_costos]
  
  runtime_compatibility:
    runtime_version: local_mvp_runtime
    all_tanks_compatible: true
  
  audit_notes: |
    Selección basada en InterrogationResult con status NEEDS_EVIDENCE.
    Dos tanques activos, uno candidato esperando evidencia.
    Sin conflictos irresolubles.
```

---

## 13. Estructura de TankSelectionResult por tanque

Para cada tanque en `selected_tanks`, `candidate_tanks`, `suspended_tanks`, `rejected_tanks`, `unsupported_tanks`:

```yaml
tank_entry:
  tank_id: <string>
  version: <semver>
  lifecycle_state: <DEFINED|AVAILABLE|CANDIDATE|ACTIVE|SUSPENDED|DEACTIVATED|UNSUPPORTED|RETIRED>
  
  activation_score: <0.0-1.0>  # Solo si CANDIDATE o ACTIVE
  
  activation_reasons:  # Solo si CANDIDATE o ACTIVE
    - type: <symptom_match|domain_match|selector_match|evidence_match|classification_match>
      detail: <string>
  
  deactivation_reasons:  # Solo si SUSPENDED, DEACTIVATED, UNSUPPORTED
    - type: <no_context|no_evidence|domain_incompatible|user_correction|safety_violation|runtime_incompatible|conflict|obsolete>
      detail: <string>
  
  missing_context:  # Solo si falta required_context
    - <string>
  
  missing_evidence:  # Solo si falta required_evidence
    - evidence_type: <string>
      required_fields: [<string>]
  
  supported_outputs:  # Solo si ACTIVE
    - <candidate_pathologies|clarifying_questions|evidence_requirements|risk_warnings|suggested_classification>
  
  unsupported_outputs:  # Solo si UNSUPPORTED
    - <string>
  
  safety_warnings:  # Si aplica
    - <string>
  
  can_reactivate: <boolean>  # Solo si SUSPENDED
  
  next_action: <request_evidence|wait_for_evidence|ask_clarification|deactivate|none>
```

---

## 14. DomainPack

### 14.1 Definición

Un **DomainPack** es una agrupación versionada de KnowledgeTanks orientada a:

- **Rubro** (textil, agro, construcción).
- **Canal** (Mercado Libre, ecommerce, local físico).
- **Dominio funcional** (finanzas, operaciones, comercial).
- **Tipo de operación** (manufactura, servicios, reventa).
- **Madurez operacional** (básico, intermedio, avanzado).
- **Combinación transversal + sectorial**.

### 14.2 Ejemplos

| Pack ID | Industria/Dominio | Tanques incluidos |
|---|---|---|
| `retail_basic_pack` | Retail básico | operational_pathology_core, evidence_formula_core |
| `marketplace_meli_pack` | Mercado Libre | operational_pathology_core, evidence_formula_core, marketplace_specific_ml |
| `textile_operations_pack` | Textil | operational_pathology_core, evidence_formula_core, textile_specific |
| `financial_control_pack` | Control financiero | operational_pathology_core, evidence_formula_core, financial_advanced |
| `data_quality_pack` | Calidad de datos | operational_pathology_core, data_quality_specific |

### 14.3 Regla fundamental

Un DomainPack **no diagnostica**.
Un DomainPack **no activa todos sus tanques**.
Un DomainPack **propone universo de tanques disponibles** según contexto.

---

## 15. Política de activación de DomainPack

### 15.1 Estados

| Estado | Significado |
|---|---|
| `AVAILABLE` | Pack cargado, disponible para evaluación |
| `CANDIDATE` | Pack pasó evaluación inicial |
| `ACTIVE` | Pack activo, algunos tanques activos |
| `PARTIAL` | Pack activo pero algunos tanques suspendidos/desactivados |
| `DEACTIVATED` | Pack no aplica para este caso |
| `UNSUPPORTED` | Pack aplica pero runtime no soporta algunos tanques |

### 15.2 Activadores

Un DomainPack puede activarse por:

- **Rubro** declarado en selectores.
- **Canal de venta** (Mercado Libre, ecommerce, local).
- **Marketplace presence** (true/false).
- **Operation type** (manufactura, servicios, reventa).
- **Evidencia** disponible.
- **Síntomas** detectados.
- **Tenant history** (futura capacidad).

### 15.3 Regla de activación

**No activar por un solo selector** salvo como `CANDIDATE`.

Ejemplo:
- Selector "Mercado Libre" solo → `marketplace_meli_pack` como `CANDIDATE`.
- Selector "Mercado Libre" + texto "vendo pero no me queda nada" → `CANDIDATE` → `ACTIVE`.

---

## 16. Relación DomainPack ↔ KnowledgeTank

### 16.1 Reglas

- Un tanque puede existir en **múltiples packs**.
- Un pack puede combinar tanques **transversales y sectoriales**.
- Un tanque sectorial puede **extender** un tanque transversal.
- Conflictos se resuelven por **especificidad y evidencia**.

### 16.2 Ejemplo

```text
SMARTPYME_EVIDENCE_AND_FORMULA_TANK (transversal)
    ↓ incluido en
marketplace_meli_pack
    ↓ combinado con
MARKETPLACE_FEES_TANK (sectorial)
```

Si el usuario vende por Mercado Libre pero no aporta reportes/comisiones:
- `MARKETPLACE_FEES_TANK` queda `CANDIDATE` o `SUSPENDED`.
- `SMARTPYME_EVIDENCE_AND_FORMULA_TANK` puede seguir `ACTIVE` si hay evidencia compatible.

---

## 17. Relación con InterrogationResult

### 17.1 Mapeo de campos

| Campo de InterrogationResult | Uso en TankSelection |
|---|---|
| `raw_input` | Validación de no-vacío, extracción de señales |
| `normalized_terms` | Match contra `activation_conditions` léxicas |
| `business_context` | Match contra `activation_conditions` tipo selector |
| `semantic_signals` | Refuerzo de match |
| `candidate_symptoms` | Match contra `supported_symptoms` |
| `candidate_domains` | Match contra `supported_domains` |
| `clarification_questions` | Alimentadas por tanques activos |
| `evidence_needs` | Cruce con `required_evidence` de tanques |
| `status` | Gate de activación (no activar si `BLOCKED`) |
| `suggested_classification` | Cruce con `supported_classifications` |

### 17.2 Regla

`InterrogationResult` **no elige tanques definitivamente**.
Solo **alimenta** selección.

---

## 18. Relación con EvidenceRequest

### 18.1 Cómo los tanques generan EvidenceRequest

Un `EvidenceRequest` derivado de tanques debe responder:

- **Qué pedir** (evidence_type).
- **Por qué** (reason).
- **Para qué hipótesis** (enables_hypotheses).
- **Con qué campos mínimos** (required_fields).
- **Si bloquea análisis** (blocking).
- **Si habilita clasificación ejecutable** (enables_classification).
- **Si es opcional** (optional).

### 18.2 Regla de mínima evidencia

Los tanques deben evitar pedir **todos los documentos posibles**.
Deben pedir la **menor evidencia suficiente**.

Ejemplo:
- Tanque de margen: pedir `excel_ventas_costos` (no pedir también stock, proveedores, caja).
- Tanque de duplicados: pedir `excel_proveedores` (no pedir también ventas, stock).

---

## 19. Relación con runtime real

### 19.1 Capacidades existentes en Git real (HEAD `a87989b`)

- `excel_diagnostic` (slice de diagnóstico de Excel).
- `supplier_duplicate_check` (spec y slice de proveedores duplicados).
- `interrogation_slice` (detección determinística de síntomas).
- Documentación de taxonomía de interrogatorio.
- Documentación de fase semántico-dialéctica.
- Selectores estructurales documentados.
- Contrato de KnowledgeTanks documentado.
- Catálogos JSON de patologías y fórmulas (solo documentación).

### 19.2 Capacidades NO implementadas en Git real

- `--classification auto` (routing automático).
- `--html-out` (output HTML).
- Tanque loader.
- Selector runtime de tanques.
- `TankSelectionResult`.
- `EvidenceRequest` formal.
- `DomainPack` ejecutable.
- Validación YAML de tanques.
- Demo package reproducible.

### 19.3 Implicancia

Un tanque puede:
- **Sugerir** clasificación compatible (`excel_diagnostic`, `supplier_duplicate_check`).
- **No puede ejecutarla** (eso lo hace el runtime).
- **No puede prometer HTML** (si no hay `--html-out`).
- **No puede asumir routing automático** (si no existe).

---

## 20. Safety gates

### 20.1 Gates obligatorios

| Gate | Descripción | Ejemplo | Consecuencia |
|---|---|---|---|
| `NO_DIAGNOSIS_WITHOUT_EVIDENCE` | No afirmar patología sin evidencia validada | Tanque activo pero sin Excel | Solo emitir `candidate_pathologies`, no `diagnostic_conclusion` |
| `NO_SELECTOR_ONLY_ACTIVATION` | No activar tanque solo por selector | Selector "Mercado Libre" sin texto | Tanque queda `AVAILABLE`, no `CANDIDATE` |
| `NO_UNSUPPORTED_OUTPUT_PROMISE` | No prometer output que runtime no soporta | Tanque sugiere HTML sin `--html-out` | Marcar tanque como `UNSUPPORTED` |
| `NO_DOMAIN_CONTAMINATION` | No mezclar dominios | Tanque de finanzas emitiendo sobre stock | Bloquear output, registrar warning |
| `NO_EXCESSIVE_EVIDENCE_REQUEST` | Máximo 3 tipos de evidencia simultáneos | Tanque pide 5 documentos | Limitar a 3, priorizar por suficiencia |
| `USER_CONFIRMATION_REQUIRED_FOR_AMBIGUOUS_CASES` | Confirmación obligatoria si caso ambiguo | Status `NEEDS_DISAMBIGUATION` | No activar tanque hasta confirmación |
| `RUNTIME_COMPATIBILITY_REQUIRED` | Solo activar si runtime compatible | Tanque requiere `interrogation_slice` pero no existe | Marcar como `UNSUPPORTED` |
| `FAIL_CLOSED_ON_CONFLICT` | Ante conflicto irresoluble, no activar | Dos tanques con hipótesis incompatibles | Registrar conflicto, pedir desambiguación |

---

## 21. Dos tanques iniciales en arquitectura

### 21.1 SMARTPYME_OPERATIONAL_PATHOLOGY_TANK

**Propósito:**
Mapear lenguaje crudo, señales y síntomas a patologías operacionales PyME sin diagnosticar.

**Síntomas soportados:**
- `DESCUADRE_DINERO`
- `MARGEN_DUDOSO`
- `DATOS_DUPLICADOS`
- `STOCK_INCONSISTENTE`
- `SOBRECARGA_MANUAL`
- `COSTO_INCIERTO`
- `DOCUMENTACION_DESORDENADA`
- `MAESTRO_DESORDENADO`

**Dominios soportados:**
- `finanzas`, `comercial`, `proveedores`, `stock`, `produccion`, `datos_maestros`, `automatizacion`, `administracion`

**Condiciones de activación:**
- Cualquier síntoma de `candidate_symptoms` presente en `supported_symptoms`.
- Dominio candidato en `supported_domains`.

**Condiciones de desactivación:**
- `status == BLOCKED_INSUFFICIENT_CONTEXT`.
- Sin síntomas y sin selectores compatibles.
- Violación de `safety_constraints`.

**Preguntas soportadas:**
- `DESCUADRE_DINERO`: "¿Hablás de caja/banco, ventas/cobros, costos/margen o gastos?"
- `MARGEN_DUDOSO`: "¿Querés revisar precios vs costos, productos sin costo o margen histórico?"
- `DATOS_DUPLICADOS`: "¿Los duplicados están en proveedores, clientes, productos u otro listado?"
- `STOCK_INCONSISTENTE`: "¿La diferencia es entre sistema y depósito, o en movimientos sin registrar?"
- `SOBRECARGA_MANUAL`: "¿Qué tarea se repite, con qué frecuencia y en qué archivos ocurre?"

**Hipótesis soportadas:**
- `margen_erosionado`: síntoma `MARGEN_DUDOSO`, test "margen_neto_real < 20% en >50% productos".
- `proveedores_duplicados`: síntoma `DATOS_DUPLICADOS`, test "count(cuit_duplicado) > 0".

**Evidencia sugerida:**
- `DESCUADRE_DINERO` → excel financiero o extracto bancario.
- `MARGEN_DUDOSO` → excel ventas + costos.
- `DATOS_DUPLICADOS` → excel proveedores con CUIT.
- `STOCK_INCONSISTENTE` → excel stock + ventas.
- `SOBRECARGA_MANUAL` → descripción del flujo + archivos involucrados.

**Outputs permitidos:**
- `candidate_pathologies`
- `clarifying_questions`
- `evidence_requirements`
- `risk_warnings`
- `suggested_classification`

**Outputs prohibidos:**
- `diagnostic_conclusion`
- `root_cause_assertion`
- `benchmark_comparison_without_sector`

**Safety gates:**
- `NO_DIAGNOSIS_WITHOUT_EVIDENCE`
- `NO_SELECTOR_ONLY_ACTIVATION`
- `NO_DOMAIN_CONTAMINATION`

**Relación con runtime real:**
- Compatible con `excel_diagnostic` cuando hay Excel.
- Compatible con `supplier_duplicate_check` cuando hay maestro proveedores.

---

### 21.2 SMARTPYME_EVIDENCE_AND_FORMULA_TANK

**Propósito:**
Mapear evidencia disponible a tipos documentales, campos esperados, fórmulas ejecutables y análisis posibles.

**Tipos documentales soportados:**
- `excel_ventas_costos`
- `excel_proveedores`
- `excel_stock`
- `pdf_facturas`
- `capturas_panel`

**Campos esperados:**
- `excel_ventas_costos`: `[fecha, producto, precio_venta, costo, cantidad]`
- `excel_proveedores`: `[proveedor, cuit, razon_social]`
- `excel_stock`: `[producto, stock_sistema, stock_real, fecha]`

**Fórmulas soportadas:**
- `REN_001_margen_neto_real`
- `LIQ_001_vendido_cobrado`
- `INV_002_rotacion_stock`
- `PYME_011_dso`
- `PYME_013_dso_dpo_gap`
- `PYME_024_liquidez_corriente`
- `PYME_033_concentracion_sku`

**Criterios de suficiencia:**
- `excel_ventas_costos`: ">= 3 meses de datos, >= 10 productos".
- `excel_proveedores`: "al menos 20 filas".
- `excel_stock`: "al menos 1 mes de movimientos".

**Hipótesis soportadas:**
- `margen_erosionado`: fórmula `REN_001_margen_neto_real`, evidencia `excel_ventas_costos`.
- `proveedores_duplicados`: fórmula `count(cuit_duplicado)`, evidencia `excel_proveedores`.
- `stock_inconsistente`: fórmula `INV_002_rotacion_stock`, evidencia `excel_stock`.

**Compatibilidad runtime:**
- `local_mvp_runtime`
- `interrogation_slice`

**Outputs permitidos:**
- `evidence_requirements`
- `formula_applicability`
- `sufficiency_assessment`
- `calculation_warnings`

**Outputs prohibidos:**
- `diagnostic_conclusion`
- `calculation_execution` (eso lo hace el runtime)

**Safety gates:**
- `NO_DIAGNOSIS_WITHOUT_EVIDENCE`
- `NO_EXCESSIVE_EVIDENCE_REQUEST`

**Relación con runtime real:**
- Alimenta a `excel_diagnostic` con campos esperados.
- Alimenta a `supplier_duplicate_check` con campos de maestro.

---

## 22. Ejemplos end-to-end

### Caso 1 — Proveedores repetidos

**Input:**
```text
"Tengo proveedores repetidos y CUIT mezclados."
```

**Flujo:**
1. `InterrogationSlice` detecta:
   - `candidate_symptoms`: `[DATOS_DUPLICADOS, MAESTRO_DESORDENADO]`
   - `candidate_domains`: `[proveedores, datos_maestros]`
   - `status`: `NEEDS_EVIDENCE`
   - `suggested_classification`: `supplier_duplicate_check`

2. `TankSelection` evalúa:
   - `operational_pathology_core`: `CANDIDATE` → `ACTIVE` (symptom_match, domain_match).
   - `evidence_formula_core`: `CANDIDATE` (evidence_match).

3. `TankSelectionResult`:
   - `selected_tanks`: `[operational_pathology_core]`
   - `candidate_tanks`: `[evidence_formula_core]`
   - `evidence_requests`: `excel_proveedores` con campos `[proveedor, cuit, razon_social]`.

4. `EvidenceRequest`:
   - Pedir Excel de proveedores.
   - Reason: "Permite verificar proveedores duplicados".
   - Sufficiency: "al menos 20 filas".

5. **Clasificación posible:** `supplier_duplicate_check`.

6. **Límites:**
   - No diagnosticar sin evidencia.
   - No afirmar causa raíz (ej: "el problema es que cargaste mal").

---

### Caso 2 — No me cierra la plata

**Input:**
```text
"No me cierra la plata."
```

**Flujo:**
1. `InterrogationSlice` detecta:
   - `candidate_symptoms`: `[DESCUADRE_DINERO]`
   - `candidate_domains`: `[finanzas]`
   - `status`: `NEEDS_DISAMBIGUATION`
   - `suggested_classification`: `null`

2. `TankSelection` evalúa:
   - `operational_pathology_core`: `CANDIDATE` (symptom_match).
   - Pero `status == NEEDS_DISAMBIGUATION` → no activar todavía.

3. `TankSelectionResult`:
   - `candidate_tanks`: `[operational_pathology_core]`
   - `clarification_questions`: "¿Hablás de caja/banco, ventas/cobros, costos/margen o gastos?"

4. **Acción:** Preguntar desambiguación antes de activar tanque.

5. **Límites:**
   - No clasificación cerrada.
   - No evidence request hasta desambiguación.

---

### Caso 3 — Marketplace/Mercado Libre

**Input:**
```text
Selector: sales_channel = "Mercado Libre"
Texto: "vendo pero no me queda nada."
```

**Flujo:**
1. `InterrogationSlice` detecta:
   - `business_context`: `{sales_channel: "Mercado Libre"}`
   - `candidate_symptoms`: `[MARGEN_DUDOSO]`
   - `candidate_domains`: `[comercial]`
   - `status`: `NEEDS_EVIDENCE`

2. `TankSelection` evalúa:
   - `operational_pathology_core`: `CANDIDATE` → `ACTIVE` (symptom_match).
   - `marketplace_meli_pack`: `CANDIDATE` (selector_match).
   - Dentro del pack: `marketplace_specific_ml`: `CANDIDATE` → `SUSPENDED` (falta evidencia ML).

3. `TankSelectionResult`:
   - `selected_tanks`: `[operational_pathology_core]`
   - `suspended_tanks`: `[marketplace_specific_ml]`
   - `evidence_requests`: `export_mercadolibre` + `excel_ventas_costos`.

4. **Acción:** Pedir export ML y Excel ventas/costos.

5. **Límites:**
   - No benchmark sin datos.
   - No diagnóstico cerrado sin comisiones/envíos.

---

### Caso 4 — Stock inconsistente

**Input:**
```text
"El sistema dice un stock y el depósito otro."
```

**Flujo:**
1. `InterrogationSlice` detecta:
   - `candidate_symptoms`: `[STOCK_INCONSISTENTE]`
   - `candidate_domains`: `[stock]`
   - `status`: `NEEDS_EVIDENCE`

2. `TankSelection` evalúa:
   - `operational_pathology_core`: `CANDIDATE` → `ACTIVE` (symptom_match).
   - `evidence_formula_core`: `CANDIDATE` (evidence_match).

3. `TankSelectionResult`:
   - `selected_tanks`: `[operational_pathology_core]`
   - `candidate_tanks`: `[evidence_formula_core]`
   - `evidence_requests`: `excel_stock` con campos `[producto, stock_sistema, stock_real, fecha]`.

4. **Acción:** Pedir Excel de stock.

5. **Límites:**
   - No clasificación ejecutable si no existe runtime de stock.
   - No afirmar causa (ej: "el sistema está mal configurado").

---

### Caso 5 — Copio todo a mano

**Input:**
```text
"Copio todo a mano todos los días."
```

**Flujo:**
1. `InterrogationSlice` detecta:
   - `candidate_symptoms`: `[SOBRECARGA_MANUAL, DOCUMENTACION_DESORDENADA]`
   - `candidate_domains`: `[automatizacion, administracion]`
   - `status`: `NEEDS_DISAMBIGUATION`

2. `TankSelection` evalúa:
   - `operational_pathology_core`: `CANDIDATE` (symptom_match).
   - Pero `status == NEEDS_DISAMBIGUATION` → no activar todavía.

3. `TankSelectionResult`:
   - `candidate_tanks`: `[operational_pathology_core]`
   - `clarification_questions`: "¿Qué tarea se repite, con qué frecuencia y en qué archivos ocurre?"

4. **Acción:** Preguntar desambiguación.

5. **Límites:**
   - No diagnóstico financiero.
   - No evidence request hasta desambiguación.

---

## 23. Criterios de aceptación para futura implementación

### 23.1 Requisitos funcionales

- **Determinístico:** Mismo input → mismo output.
- **No diagnostica:** Solo sugiere síntomas, evidencia, clasificación.
- **Serializable:** `TankSelectionResult` debe ser JSON/YAML serializable.
- **Consume `InterrogationResult`:** Entrada única.
- **Produce `EvidenceRequest`:** Conceptual o serializable.
- **Registra conflictos:** En `TankSelectionResult.conflicts`.
- **Registra desactivaciones:** En `deactivation_reasons`.

### 23.2 Requisitos de testing

- **Tests por conflicto:** Múltiples tanques aplicando, selector contradiciendo relato, evidencia contradictoria.
- **Tests por desactivación:** Usuario corrige, evidencia invalida, runtime incompatible.
- **Tests por selector aislado:** Selector sin texto no activa tanque.
- **Tests por safety gate:** Violación de `NO_DIAGNOSIS_WITHOUT_EVIDENCE`, `NO_SELECTOR_ONLY_ACTIVATION`, etc.

### 23.3 Requisitos de integración

- **No toca runtime de diagnóstico:** `excel_diagnostic` y `supplier_duplicate_check` sin cambios.
- **No asume auto routing:** No implementar `--classification auto`.
- **No asume HTML:** No implementar `--html-out`.
- **Compatible con `interrogation_slice`:** Usa `InterrogationResult` como entrada.

### 23.4 Requisitos de documentación

- **YAML de tanques:** Al menos 2 tanques documentados (`operational_pathology_core`, `evidence_formula_core`).
- **Ejemplos end-to-end:** Al menos 5 casos documentados.
- **Glosario:** Definiciones de estados, transiciones, gates.

---

## 24. Gaps conocidos

### Críticos (bloquean implementación)

- **No existe loader YAML de tanques.**
- **No existe selector runtime de tanques.**
- **No existe `TankSelectionResult` formal.**
- **No existe contrato de `EvidenceRequest`.**
- **No existe validación JSON Schema de tanques.**

### High (riesgo de mal funcionamiento)

- **No existe DomainPack ejecutable.**
- **No existe política de activación implementada.**
- **No existe persistencia de `applied_tanks` por caso.**
- **No existe matriz de compatibilidad runtime.**

### Medium (mejoran mantenibilidad)

- **Catálogos JSON de patologías y fórmulas no están integrados al runtime.**
- **No hay ejemplo ejecutable end-to-end con tanques.**
- **No hay tests de contratos YAML.**
- **No hay registro en `IntakeRecord`.**

### Future (no hacer ahora)

- Benchmarks por sector.
- Multi-idioma.
- Tanques por industria específicos (textil, agro, construcción).
- Hot-swap en runtime.
- Integración con `e2e_cli`.

---

## 25. Roadmap posterior

Máximo 4 frentes recomendados, en orden de prioridad:

### 1. SMARTPYME_OPERATIONAL_PATHOLOGY_TANK_DOC

**Objetivo:** Documentar en YAML el primer tanque canónico.

**Entregable:** `docs/smartpyme/tanks/operational_pathology_core.yaml`

**Contenido:**
- 5–7 patologías PyME mapeadas a `pathology_catalog.v1.json`.
- Síntomas, señales, preguntas, evidencia, límites.
- Ejemplo completo de activación.

---

### 2. SMARTPYME_EVIDENCE_AND_FORMULA_TANK_DOC

**Objetivo:** Documentar en YAML el segundo tanque canónico.

**Entregable:** `docs/smartpyme/tanks/evidence_formula_core.yaml`

**Contenido:**
- Tipos documentales + campos esperados.
- Fórmulas prioritarias de `formula_catalog.v1.json`.
- Hipótesis contrastables.
- Criterios de suficiencia.

---

### 3. SMARTPYME_TANK_SELECTION_SLICE

**Objetivo:** Implementar el slice mínimo de selección de tanques.

**Entregables:**
- `pymia/smartpyme/tank_selection.py`
- `tests/smartpyme/test_tank_selection.py`

**Funcionalidad:**
- Recibe `InterrogationResult`.
- Evalúa `activation_conditions`.
- Devuelve `TankSelectionResult` con tanques activos.
- Genera `EvidenceRequest` derivado.

---

### 4. SMARTPYME_INTAKE_RECORD_AND_EVIDENCE_REQUEST

**Objetivo:** Implementar la persistencia de interrogación + selección + evidencia.

**Entregables:**
- `pymia/smartpyme/intake_record.py`
- `tests/smartpyme/test_intake_record.py`

**Persistencia:**
- `InterrogationResult`.
- `TankSelectionResult`.
- `EvidenceRequest`.
- `EvidenceCandidate` recibida.
- `applied_tanks` por caso.

---

## 26. Cierre

**Regla rectora:**

> Los tanques no deciden por SmartPyme.
> Habilitan conocimiento trazable bajo evidencia, límites y compatibilidad runtime.

**Principio de producto:**

SmartPyme es un laboratorio operacional PyME: recibe caos, estructura evidencia, detecta síntomas, formula hipótesis, pide evidencia y devuelve claridad incremental.

No debe diagnosticar sin evidencia ni prometer automatización total.

---

## Documentos relacionados

- `SMARTPYME_KNOWLEDGE_TANKS_CONTRACT.md` — contrato canónico
- `SMARTPYME_INTERROGATION_TAXONOMY.md` — capa taxonómica
- `SMARTPYME_SEMANTIC_DIALECTIC_PHASE.md` — capa conversacional
- `SMARTPYME_INTERROGATION_SLICE.md` — slice determinístico implementado
- `SMARTPYME_LOCAL_MVP_RUNTIME.md` — runtime real actual
- `SMARTPYME_SUPPLIER_DUPLICATE_CHECK_SPEC.md` — spec de clasificación existente
- `docs/ingenieria_conversacional.PATOLOGIAS_PYME_Y_TANQUES_DE_CONOCIMIENTO_v1.md`
- `docs/ingenieria_conversacional.CATALOGO_HIPOTESIS_Y_EVIDENCIA_v1.md`
- `docs/pathology_catalog.v1.json`
- `docs/formula_catalog.v1.json`
- `docs/contracts/scn/evidence_candidate.schema.json`

---

*Este documento es diseño de subarquitectura. No implica implementación runtime.*
