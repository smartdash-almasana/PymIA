# KNOWLEDGETANKS_PACKSYSTEM_RECONCILIATION_AUDIT

## Estado

`DRAFT_DOCUMENTARY_AUDIT`

## Fecha

2026-06-12

## Propósito

Reconciliar la arquitectura histórica de SmartPyme basada en `KnowledgeTanks` y `DomainPacks` con la decisión aceptada en `ADR-024-pack-system-foundation.md`, que define el `Pack System` como frontera formal kernel ↔ conocimiento enchufable.

Este documento evita crear dos arquitecturas paralelas:

```text
SmartPyme KnowledgeTanks
vs
PymIA Pack System
```

La conclusión esperada no es elegir una y descartar la otra, sino fijar una jerarquía coherente.

## Fuentes leídas

- `docs/adr/ADR-024-pack-system-foundation.md`
- `docs/pymia/PACK_BOUNDARY_CODE_RECONCILIATION.md`
- `docs/smartpyme/SMARTPYME_KNOWLEDGE_TANKS_CONTRACT.md`
- `docs/smartpyme/SMARTPYME_KNOWLEDGE_TANKS_ARCHITECTURE.md`
- `docs/smartpyme/SMARTPYME_OPERATIONAL_PATHOLOGY_TANK.md`
- `docs/smartpyme/SMARTPYME_EVIDENCE_AND_FORMULA_TANK.md`

## No autorizaciones

Este documento no autoriza:

- Modificar código.
- Ejecutar tests.
- Crear packs ejecutables.
- Crear loaders runtime.
- Migrar KnowledgeTanks.
- Migrar fórmulas.
- Migrar patologías.
- Tocar `diagnostic_core`.
- Tocar `anamnesis_fsm`.
- Abrir runtime, Telegram, Hermes, MCP, PDF, ERP o UI.

---

# 1. Veredicto ejecutivo

`PASS_DOCUMENTARY_RECONCILIATION_DRAFT`

Los documentos históricos de KnowledgeTanks no contradicen ADR-024 en su principio de fondo. Al contrario: anticipan una parte del Pack System.

Pero sí existe un riesgo de deriva si se mantienen como arquitectura paralela.

La reconciliación correcta es:

```text
ADR-024 Pack System = frontera superior de gobernanza enchufable.
KnowledgeTank = unidad interna especializada dentro de un KnowledgePack o DomainPack.
DomainPack histórico = precursor compatible del DomainPack de ADR-024, pero debe subordinarse al schema general de Pack.
```

En otras palabras:

```text
Pack System gobierna.
KnowledgeTanks componen.
Kernel carga/valida/rechaza.
Tanks nunca deciden ni diagnostican.
```

---

# 2. Diferencia conceptual entre Pack y KnowledgeTank

| Concepto | Nivel | Rol | Autoridad |
|---|---|---|---|
| `Pack` | Gobernanza superior | Artefacto versionado enchufable que cruza frontera kernel ↔ dominio | ADR-024 |
| `KnowledgePack` | Tipo de Pack | Contiene conocimiento experto estructurado y puede incluir KnowledgeTanks | ADR-024 + este documento |
| `DomainPack` | Tipo de Pack | Agrupa conocimiento por rubro, sector, canal u operación | ADR-024; KnowledgeTanks histórico queda subordinado |
| `KnowledgeTank` | Componente interno | Unidad mínima de conocimiento activable, con síntomas, preguntas, evidencia, límites y outputs | SmartPyme docs; debe vivir dentro de un Pack |
| `CatalogPack` | Tipo de Pack | Opciones, taxonomías y listas consumibles por anamnesis | ADR-024 |
| `FormulaPack` | Tipo de Pack | Fórmulas y metadata de cálculo | ADR-024 |
| `PathologyPack` | Tipo de Pack | Patologías, umbrales, vínculos a fórmula y acciones sugeridas | ADR-024 |
| `SectorPack` | Tipo de Pack | Conocimiento de vertical/rubro | ADR-024 |

## Decisión de reconciliación

`KnowledgeTank` no debe ser tratado como alternativa a `Pack`.

Debe ser tratado como:

```text
KnowledgeTank = internal_unit dentro de KnowledgePack / DomainPack / SectorPack
```

---

# 3. Compatibilidad entre ambos modelos

## 3.1 Compatibilidades fuertes

| KnowledgeTanks histórico | ADR-024 Pack System | Compatibilidad |
|---|---|---|
| Conocimiento enchufable/desenchufable | Pack versionado enchufable | Alta |
| No modificar runtime core | Kernel estable | Alta |
| No diagnosticar | Pack no confirma hallazgos | Alta |
| Versionado semver | Versionado de pack | Alta |
| Activación/desactivación | Validación/rechazo/fail-closed | Alta |
| EvidenceRequest | required_evidence | Alta |
| Outputs permitidos/prohibidos | exposed_items + prohibiciones | Alta |
| DomainPack como agrupación | DomainPack ADR-024 | Alta, requiere subordinación |

## 3.2 Diferencias a resolver

| Diferencia | Riesgo | Resolución |
|---|---|---|
| KnowledgeTank define ciclo `DEFINED/AVAILABLE/CANDIDATE/ACTIVE/...` | No coincide con ciclo ADR-024 `DRAFT/CANDIDATE/VALIDATED/ACTIVE/...` | Separar ciclo de vida de Pack y estado operativo de Tank dentro del caso. |
| KnowledgeTank habla de activación runtime futura | Puede parecer que autoriza implementación | Marcarlo como componente interno no ejecutable hasta Pack Contract + TaskSpec. |
| DomainPack histórico agrupa KnowledgeTanks | Puede competir con DomainPack ADR-024 | DomainPack histórico queda como diseño precursor subordinado a ADR-024. |
| Tanks incluyen fórmulas soportadas | Puede duplicar FormulaPack | Las fórmulas referenciadas por Tank deben venir de FormulaPack, no definirse ad hoc. |
| Tanks incluyen patologías candidatas | Puede duplicar PathologyPack | Las patologías referenciadas por Tank deben venir de PathologyPack. |
| Tanks definen evidencia requerida | Puede duplicar Evidence Gate | Tank puede proponer required_evidence; kernel/evidence_gate decide suficiencia. |

---

# 4. Jerarquía reconciliada

La jerarquía coherente queda así:

```text
PackRegistry
  ├── KnowledgePack
  │     ├── KnowledgeTank: SMARTPYME_OPERATIONAL_PATHOLOGY_TANK
  │     └── KnowledgeTank: SMARTPYME_EVIDENCE_AND_FORMULA_TANK
  │
  ├── FormulaPack
  │     └── formula definitions / expressions / required variables
  │
  ├── PathologyPack
  │     └── pathology definitions / thresholds / severity / suggestions
  │
  ├── CatalogPack
  │     └── anamnesis options / menus / visible choices
  │
  ├── DomainPack
  │     └── composition of tanks and domain-specific policies
  │
  └── SectorPack
        └── vertical-specific taxonomy, symptoms, benchmarks, sector mappings
```

## Regla

Un `KnowledgeTank` puede referenciar:

- fórmulas de `FormulaPack`;
- patologías de `PathologyPack`;
- opciones de `CatalogPack`;
- rubros de `SectorPack`;
- mapeos de `DomainPack`.

Pero no debe convertirse en dueño de todo ese conocimiento.

---

# 5. Reconciliación de ciclos de vida

## 5.1 Pack lifecycle según ADR-024

```text
DRAFT
→ CANDIDATE
→ VALIDATED
→ ACTIVE
→ DEPRECATED
→ REJECTED
```

Este ciclo aplica al artefacto versionado como unidad de distribución/gobernanza.

## 5.2 Tank lifecycle histórico

```text
DEFINED
→ AVAILABLE
→ CANDIDATE
→ ACTIVE
→ SUSPENDED
→ DEACTIVATED
→ UNSUPPORTED
→ RETIRED
```

Este ciclo aplica al comportamiento de un tank dentro de un caso o dentro de la selección operacional.

## 5.3 Reconciliación

| Ciclo | Aplica a | Ejemplo |
|---|---|---|
| Pack lifecycle | Artefacto versionado | `knowledgepack-smartpyme-core@1.0.0` está `ACTIVE` |
| Tank lifecycle | Estado de uso en un caso | `SMARTPYME_OPERATIONAL_PATHOLOGY_TANK` queda `SUSPENDED` en un caso ambiguo |

Regla:

```text
Un Pack ACTIVE puede contener Tanks que, en un caso concreto, estén AVAILABLE, CANDIDATE, ACTIVE, SUSPENDED, DEACTIVATED o UNSUPPORTED.
```

Nunca confundir:

```text
Pack ACTIVE ≠ Tank ACTIVE en el caso.
```

---

# 6. Reconciliación de los dos tanques canónicos

## 6.1 SMARTPYME_OPERATIONAL_PATHOLOGY_TANK

Estado histórico:

```text
DOCUMENTADO (v0.1.0-doc) — Sin implementación runtime
```

Rol real:

```text
KnowledgeTank canónico de síntomas, patologías candidatas, preguntas y evidencia sugerida.
```

Destino reconciliado:

```text
KnowledgePack: smartpyme-core-knowledge-pack
  └── internal_unit: SMARTPYME_OPERATIONAL_PATHOLOGY_TANK
```

Referencias futuras obligatorias:

| Contenido | Fuente futura |
|---|---|
| Patologías candidatas | `PathologyPack` |
| Preguntas de desambiguación | `KnowledgePack` / `CatalogPack` según tipo |
| Síntomas soportados | `DomainPack` / `SectorPack` si son generales o sectoriales |
| Evidence suggestions | `KnowledgePack`, pero validación final por kernel |

## 6.2 SMARTPYME_EVIDENCE_AND_FORMULA_TANK

Estado histórico:

```text
DOCUMENTADO (v0.1.0-doc) — Sin implementación runtime
```

Rol real:

```text
KnowledgeTank canónico de tipos documentales, campos esperados, fórmulas contrastables y criterios de suficiencia.
```

Destino reconciliado:

```text
KnowledgePack: smartpyme-core-knowledge-pack
  └── internal_unit: SMARTPYME_EVIDENCE_AND_FORMULA_TANK
```

Referencias futuras obligatorias:

| Contenido | Fuente futura |
|---|---|
| Fórmulas soportadas | `FormulaPack` |
| Patologías contrastables | `PathologyPack` |
| Tipos documentales | `CatalogPack` / `KnowledgePack` |
| Criterios de suficiencia | Propuestos por KnowledgeTank; decididos por kernel/evidence gate |
| Runtime compatibility | Kernel / PackRegistry |

---

# 7. Mapeo KnowledgeTanks → Pack System

| Elemento histórico | Nuevo lugar reconciliado | Comentario |
|---|---|---|
| `SMARTPYME_KNOWLEDGE_TANKS_CONTRACT.md` | Fuente histórica subordinada a `PACK_SYSTEM_CONTRACT_V1` | No eliminar; usar como insumo. |
| `SMARTPYME_KNOWLEDGE_TANKS_ARCHITECTURE.md` | Diseño de subarquitectura interna de KnowledgePack | Debe perder autoridad superior frente a ADR-024. |
| `SMARTPYME_OPERATIONAL_PATHOLOGY_TANK.md` | Tank interno de `KnowledgePack` | No ejecutable hasta contrato pack. |
| `SMARTPYME_EVIDENCE_AND_FORMULA_TANK.md` | Tank interno de `KnowledgePack` | Sus fórmulas deben venir de FormulaPack. |
| `SMARTPYME_TANK_SELECTION_SLICE.md` | Futuro selector interno de KnowledgePack / DomainPack | No abrir hasta Pack Contract. |
| `DomainPack` histórico | `DomainPack` ADR-024 | Compatible, pero schema debe ajustarse a Pack general. |
| `TankSelectionResult` | Output interno de selección de tanks | No es output del kernel final. |
| `EvidenceRequest` histórico | Candidate input hacia owner questions/evidence recovery | Debe reconciliarse con `OwnerQuestionsBundle` y evidence gate. |

---

# 8. Riesgos de doble arquitectura

| Riesgo | Severidad | Descripción | Prevención |
|---|---|---|---|
| Crear `PackSystem` nuevo ignorando KnowledgeTanks | Alta | Repetiría contratos ya pensados | Usar KnowledgeTanks como insumo de KnowledgePack. |
| Implementar `TankSelection` antes de Pack Contract | Alta | Runtime sin frontera de gobernanza | Bloquear hasta `PACK_SYSTEM_CONTRACT_V1`. |
| Mantener DomainPack histórico como autoridad paralela | Alta | Dos definiciones de DomainPack | Subordinar a ADR-024. |
| KnowledgeTank absorbe fórmulas y patologías | Alta | Reproduce kernel inflado dentro de tank | Tank referencia FormulaPack/PathologyPack. |
| EvidenceRequest compite con OwnerQuestions | Media | Dos caminos para pedir evidencia al dueño | Reconciliar EvidenceRequest como fuente candidata de OwnerQuestionsBundle. |
| Safety gates duplicados | Media | Reglas repetidas en varios docs | Consolidar en Pack Contract. |
| Lifecycle confundido | Media | Pack ACTIVE vs Tank ACTIVE | Separar lifecycle de artefacto y estado por caso. |

---

# 9. Reglas de reconciliación obligatorias

## Regla 1 — ADR-024 manda

Cualquier documento SmartPyme anterior queda subordinado a ADR-024 si habla de conocimiento enchufable.

## Regla 2 — KnowledgeTank no cruza solo la frontera kernel

El kernel no carga un `KnowledgeTank` suelto.

El kernel sólo debería cargar un `Pack` validado.

## Regla 3 — KnowledgeTank vive dentro de Pack

Un `KnowledgeTank` puede existir como unidad interna, pero debe estar empaquetado dentro de:

- `KnowledgePack`, o
- `DomainPack`, o
- `SectorPack`.

## Regla 4 — Tanks no poseen fórmulas

Un tank puede referenciar fórmulas, pero las definiciones deben vivir en `FormulaPack`.

## Regla 5 — Tanks no poseen patologías como fuente soberana

Un tank puede sugerir patologías candidatas, pero las definiciones deben vivir en `PathologyPack`.

## Regla 6 — Tanks no validan evidencia como autoridad final

Un tank puede proponer evidencia requerida. El kernel/evidence gate decide suficiencia.

## Regla 7 — Tanks no diagnostican

Esta regla coincide con ambos mundos y queda preservada.

## Regla 8 — Selector de tanks no se implementa todavía

Hasta que existan:

```text
PACK_SYSTEM_CONTRACT_V1
Pack schema
PackRegistry contract
compatibility rules
fail-closed rules
```

no debe implementarse selector runtime.

---

# 10. Implicancia para PACK_SYSTEM_CONTRACT_V1

El futuro `PACK_SYSTEM_CONTRACT_V1.md` debe incluir explícitamente:

1. Campo opcional `internal_units` para packs compuestos.
2. Tipo permitido de unidad interna: `KnowledgeTank`.
3. Diferencia entre `pack_lifecycle_status` y `case_activation_status`.
4. Prohibición de cargar tanks sueltos desde kernel.
5. Regla de referencias cruzadas:
   - Tank → FormulaPack por `formula_id`.
   - Tank → PathologyPack por `pathology_id` o `pathology_code`.
   - Tank → CatalogPack por `catalog_ref`.
   - Tank → SectorPack por `sector_ref`.
6. Regla de fail-closed si una referencia cruzada no existe.
7. Regla de no diagnóstico.
8. Regla de no ejecución arbitraria desde tank YAML.
9. Regla de no prometer runtime no implementado.
10. Regla de máximo alcance documental hasta que haya TaskSpec.

---

# 11. Próximos documentos para síntesis atómica

Orden recomendado:

```text
1. PACK_BOUNDARY_CODE_RECONCILIATION.md — creado.
2. KNOWLEDGETANKS_PACKSYSTEM_RECONCILIATION_AUDIT.md — este documento.
3. DOCUMENTATION_AUTHORITY_LEDGER.md — registrar auditorías y autoridad.
4. OWNER_INTERACTION_ATOMIC_TRACE.md — traza mínima Dueño → Evidencia → Core → Reporte → Reentry.
5. PYMIA_ATOMIC_SYNTHESIS.md — síntesis final de invariantes y próximos frentes.
```

---

# 12. Veredicto

`PASS_DOCUMENTARY_RECONCILIATION_DRAFT`

La arquitectura de KnowledgeTanks no debe descartarse.

Debe reclasificarse así:

```text
KnowledgeTanks = subarquitectura interna de KnowledgePack / DomainPack
Pack System = frontera superior de gobernanza enchufable aceptada por ADR-024
```

Queda bloqueado cualquier `PACK_SYSTEM_CONTRACT_V1` que no contemple esta reconciliación.

---

# 13. Síntesis mínima

```text
Pack es el contenedor gobernado.
Tank es una unidad interna de conocimiento.
FormulaPack define fórmulas.
PathologyPack define patologías.
CatalogPack define opciones.
DomainPack/SectorPack componen contexto.
KnowledgeTank no diagnostica, no ejecuta y no cruza solo la frontera kernel.
```
