# FIRST_AID_TRIAGE_COMPONENTS_DECISION_V1

## Estado

Tipo: PRODUCT_DECISION
Estado: DRAFT_APPLIED
Runtime impact: NONE
Code impact: NONE
Tests impact: CONTRACT_ONLY

## Contexto

La auditoría técnica-documental del seed reconciliado
(`PymIA-Live/pymia/contracts/first_aid_toolbox_pack_seed_v1.json`)
detectó `PARTIAL_MATCH / CONTRACT_MISMATCH` entre el contrato implementado
y el contrato documental.

De los 5 `tool_refs` declarados en el contrato documental, 2 tenían
`mapping_status: MISSING_COMPONENT`:

- `gastos_triage` → el componente existente `control_de_gastos` tiene
  decision `NOT_FOR_PHASE_1_PHASE_2`
- `proveedores_precio_variacion_triage` → el componente existente
  `compras_y_proveedores` tiene decision `NOT_FOR_PHASE_1_PHASE_2`

El contrato documental (`FIRST_AID_TOOLBOX_PACK_CONTRACT_V1.md`) y el
catálogo maestro (`PYMIA_SERVICE_1_FULL_CATALOG_V1.md`) declaran que
estas 5 herramientas son parte del toolbox pack FIRST_AID. El gap era
real y documentado.

## Decisión

Crear **2 componentes nuevos específicos de triage FIRST_AID**:

- `gastos_triage`
- `proveedores_precio_variacion_triage`

**No reclasificar** los componentes amplios existentes:

- `control_de_gastos` (permanece `NOT_FOR_PHASE_1_PHASE_2`)
- `compras_y_proveedores` (permanece `NOT_FOR_PHASE_1_PHASE_2`)

## Razón

Los componentes amplios (`control_de_gastos`, `compras_y_proveedores`)
pueden inducir alcance contable, fiscal o de diagnóstico que excede
la frontera de Primeros Auxilios. Los componentes nuevos son:

- **Pequeños**: scope limitado a triage (ordenar, agrupar, detectar faltantes)
- **Limitados**: decision `USE_IN_PHASE_1_WITH_GUARDRAILS`
- **Seguros**: forbidden_claims explícitos que prohíben diagnóstico,
  auditoría, clasificación fiscal y decisiones definitivas
- **Owner-facing**: owner_limit que declara lo que NO hacen

## Componentes nuevos

### gastos_triage

| Campo | Valor |
|---|---|
| source | FirstAidPack |
| component_type | ChecklistPack |
| decision | USE_IN_PHASE_1_WITH_GUARDRAILS |
| family | expense_triage |
| scope | FIRST_AID |
| purpose | ordenar gastos de forma inicial, detectar faltantes y pedir clasificación mínima |
| owner_limit | Agrupa egresos; no clasifica fiscalmente ni audita gastos. |
| forbidden_claims | clasificación contable definitiva, clasificación fiscal definitiva, auditoría de gastos, diagnóstico de rentabilidad, decisión impositiva |

### proveedores_precio_variacion_triage

| Campo | Valor |
|---|---|
| source | FirstAidPack |
| component_type | HeuristicPack |
| decision | USE_IN_PHASE_1_WITH_GUARDRAILS |
| family | supplier_triage |
| scope | FIRST_AID |
| purpose | revisar aumentos visibles de proveedores, comparar costos básicos y detectar faltantes |
| owner_limit | Detecta aumentos visibles; no decide estrategia de compras ni confirma rentabilidad. |
| forbidden_claims | estrategia de compras definitiva, rentabilidad por proveedor confirmada, recomendación final de compra, auditoría de proveedores, diagnóstico financiero completo |

## Mappings actualizados

| tool_ref | component_id | mapping_status | antes |
|---|---|---|---|
| gastos_triage | gastos_triage | ALIGNED | MISSING_COMPONENT |
| proveedores_precio_variacion_triage | proveedores_precio_variacion_triage | ALIGNED | MISSING_COMPONENT |

## Límites

Esta decisión:

- **No autoriza runtime**
- **No autoriza loader**
- **No autoriza activación de herramientas**
- **No autoriza diagnóstico**
- **No autoriza decisiones fiscales ni contables definitivas**
- **No reclasifica** `control_de_gastos` ni `compras_y_proveedores`
- **No mezcla** Servicio 1 con Servicio 2/3

## Componentes amplios que NO se tocaron

Los siguientes componentes siguen siendo `NOT_FOR_PHASE_1_PHASE_2`:

- `control_de_gastos` — requiere diagnóstico específico de gastos
- `compras_y_proveedores` — requiere diagnóstico específico de compras/proveedores

Estos componentes amplios podrán considerarse en Fase 2 cuando haya
evidencia suficiente, cruce de fuentes y owner con intención de
diagnóstico. Por ahora permanecen fuera del scope de Primeros Auxilios.

## Resultado esperado

- Los 5 tool_refs del pack quedan mapeados a componentes.
- No quedan `MISSING_COMPONENT` en `tool_component_mapping`.
- El seed pasa de 27 a 29 componentes totales.
- `USE_IN_PHASE_1_WITH_GUARDRAILS` pasa de 9 a 11 componentes.
- `expected_counts.tool_component_mapping_aligned` pasa de 3 a 5.
- `expected_counts.tool_component_mapping_missing` pasa de 2 a 0.
- El seed sigue siendo candidato documental/técnico, no runtime.
- Los componentes amplios (`control_de_gastos`, `compras_y_proveedores`)
  permanecen intactos en `NOT_FOR_PHASE_1_PHASE_2`.

## Impacto en contadores

| Métrica | Antes | Después |
|---|---|---|
| components_total | 27 | 29 |
| USE_IN_PHASE_1 | 13 | 13 |
| USE_IN_PHASE_1_WITH_GUARDRAILS | 9 | 11 |
| NOT_FOR_PHASE_1_PHASE_2 | 5 | 5 |
| tool_component_mapping_aligned | 3 | 5 |
| tool_component_mapping_missing | 2 | 0 |
| MISSING_COMPONENT | gastos_triage, proveedores_precio_variacion_triage | (ninguno) |

## Artefactos afectados

### Modificados

- `PymIA-Live/pymia/contracts/first_aid_toolbox_pack_seed_v1.json`
  - 2 componentes nuevos agregados al final de `components[]`
  - 2 mappings actualizados en `tool_component_mapping[]`
  - 10 forbidden_claims nuevos agregados a `forbidden_claims[]`
  - expected_counts actualizados
  - notes actualizadas

- `PymIA-Live/tests/contracts/test_first_aid_toolbox_pack_seed_v1.py`
  - Test `test_components_count_is_29` (era 27)
  - Test `test_mapping_has_5_aligned_and_0_missing` (era 3+2)
  - Clase nueva `TestNewTriageComponents` con 11 tests
  - Clase nueva `TestExpectedCounts` con 6 tests
  - Test de notes actualizado para referenciar la decisión

### Creados

- `docs/producto/FIRST_AID_TRIAGE_COMPONENTS_DECISION_V1.md` (este documento)

## Riesgos mitigados

1. **Riesgo de reclasificación incorrecta**: reclasificar `control_de_gastos`
   o `compras_y_proveedores` a `USE_IN_PHASE_1_WITH_GUARDRAILS` habría
   expuesto componentes amplios a Primera Fase sin las limitaciones
   adecuadas. Se mitiga creando componentes nuevos con scope explícito.

2. **Riesgo de forbidden_claims insuficientes**: los componentes amplios
   no declaraban forbidden_claims específicos para triage. Se mitiga
   agregando 5 forbidden_claims por componente nuevo.

3. **Riesgo de evidencia sin requisitos**: las 2 herramientas faltantes
   ya tenían `evidence_requirements` declarados en el seed anterior.
   Esta decisión no afecta ese campo.

4. **Riesgo de owner-facing limitations faltantes**: las 2 herramientas
   ya tenían limitaciones en `owner_facing_limitations.per_tool`.
   Esta decisión refuerza con `owner_limit` y `forbidden_claims` a
   nivel de componente.

## Riesgos pendientes

1. **Riesgo de implementación prematura**: los 2 componentes nuevos
   existen en el JSON pero no hay código que los implemente. El próximo
   paso seguro es FIRST_AID_TOOL_ACTIVATION_V1, no implementación directa.

2. **Riesgo de composición no definida**: los 2 componentes nuevos no
   están incluidos en ninguna `composition[]`. Si se necesitan
   composiciones que los incluyan, deben definirse en un ciclo posterior.

3. **Riesgo de duplicación con componentes amplios**: existe `control_de_gastos`
   (amplio, NOT_FOR_PHASE_1) y ahora `gastos_triage` (limitado,
   USE_IN_PHASE_1_WITH_GUARDRAILS). El loader debe distinguirlos
   correctamente por `component_id`.

## Relación con documentos existentes

| Documento | Relación |
|---|---|
| FIRST_AID_TOOLBOX_PACK_CONTRACT_V1.md | Contrato documental que declara las 5 tool_refs. Esta decisión cierra el gap de 2 MISSING_COMPONENT. |
| PYMIA_SERVICE_1_FULL_CATALOG_V1.md | Catálogo maestro que lista gastos_triage y proveedores_precio_variacion_triage como capacidades DOCUMENTED_ONLY. Tras esta decisión pasan a NEEDS_WIRING (componente existe, falta activación). |
| first_aid_toolbox_v1.json | Contrato de componentes original. No modificado. Esta decisión sólo afecta al seed reconciliado. |
| first_aid_toolbox_v1.py | Loader del contrato original. No modificado. No depende del seed. |

## Próximo paso recomendado

Auditar la consistencia entre los 2 componentes nuevos y el contrato
documental (`FIRST_AID_TOOLBOX_PACK_CONTRACT_V1.md`) para verificar que:

1. Los `forbidden_claims` declarados en los componentes coinciden con
   los declarados en el contrato documental.
2. Los `owner_limit` coinciden con las limitaciones owner-facing del
   contrato documental.
3. El `scope: FIRST_AID` es coherente con la frontera de Servicio 1.

Después de esta auditoría, el próximo paso seguro es
**FIRST_AID_TOOL_ACTIVATION_V1**: definir el contrato de activación que
permita ejecutar `gastos_triage` y `proveedores_precio_variacion_triage`
bajo evidencia mínima, sin tocar runtime ni vertical_pipeline.py.
