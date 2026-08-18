# Servicio 1 — F2 Canonical Formula Source Spec v1

**Estado:** FROZEN  
**Alcance:** fuente canónica y gobernanza de fórmulas productivas  
**Fuera de alcance:** F3, F8, `AnalysisPlan`, P7/P8 redesign, matemática de UI y lógica de rubro

## Decisión congelada

La única fuente canónica, versionada y ejecutable de reglas de fórmula es:

```text
pymia/contracts/formula_rules_v1.json
```

La única fachada productiva para `BUSINESS_FORMULA` y la ejecución de `FormulaNodeV1` (cuando exista representación interna de AST) es:

```text
pymia/services/formula_engine_service.py::FormulaEngineService
```

El archivo JSON declara `authority=CANONICAL_PRODUCTIVE_FORMULA_SPEC`; cada regla tiene `formula_id`, `formula_version`, `required_inputs`, `expression`, unidad, bloqueo y metadatos de procedencia.

## Responsabilidades por capa

| Capa | Responsabilidad | No hace |
| --- | --- | --- |
| `FormulaEngineService` | Ejecutar reglas canónicas y devolver resultado/bloqueo determinista | Resolver evidencia, clasificar patología o autorizar runtime |
| `formula_contract.py` | Proyectar `formula_rules_v1.json` a `SUPPORTED_FORMULAS` | Mantener una segunda lista manual de fórmulas |
| `GenericCapabilityEngine` | Resolver inputs, validar dominios, clasificar y armar packet/outcome | Ejecutar AST o aritmética de negocio |
| `service_1_capability_registry_v1.py` | Declarar capabilities, variables, clasificación y `formula_ref` | Embebar `FormulaNodeV1` o expresiones ejecutables |
| `service_1_computability_v1.py` (P8) | Validar evidencia, matriz y coherencia canónica; proyectar expresión/variables al input gobernado | Ejecutar fórmulas |
| `docs/formula_catalog.v1.json` | Referencia de metadata, evidencia e interpretación | Ser autoridad ejecutable |

## Nombres de autoridad

```text
BUSINESS_FORMULA_AUTHORITY = FormulaEngineService
AST_EXECUTION_AUTHORITY = FormulaEngineService
AGGREGATION_AUTHORITY_TARGET = FormulaEngineService
AGGREGATION_CURRENT_DEBT = GenericCapabilityEngine SUM
DEBT_CONVERGENCE_PHASE = F8
```

El `SUM` existente de `GenericCapabilityEngine` sólo prepara inputs agregados desde evidencia confirmada. Se clasifica como `AGGREGATION_EXISTING_DEBT` y se conserva sin moverlo en F2. Su convergencia futura a `FormulaEngineService` pertenece exclusivamente a F8.

## Reglas y correcciones congeladas

- `LIQ_001_vendido_cobrado` delega `sold_amount - collected_amount` a `FormulaEngineService`; conserva validación, clasificación y packet/outcome.
- `REN_001_margen_neto_real` ya estaba delegado y se conserva como patrón.
- `PYME_013_PREREQUISITE_dpo` es una regla canónica ejecutable: `(accounts_payable / purchases) * days`, con bloqueo explícito por compras cero. No se incorpora al catálogo de patologías porque es un prerrequisito técnico.
- `PYME_013_dso_dpo_gap` usa variables canónicas `dso` y `dpo`; sus resultados upstream continúan identificados por `dso_days` y `dpo_days`.
- `PYME_026_flujo_operativo` es el `formula_ref` canónico; no se conserva el alias divergente `PYME_026_adjusted_operating_cash_flow`.

## Legacy explícito

Los evaluadores `LIQ_002` y `PYME_011` legacy que todavía contienen matemática directa se clasifican como:

```text
NON_PRODUCT_ROOT_LEGACY_MATH
```

No se modifican en F2. Su futura convergencia se registra como deuda posterior; no se ejecuta dentro de este cierre.

`Derived Evidence._apply_discount` permanece como `GOVERNED_EVIDENCE_TRANSFORMATION`: prepara evidencia derivada bajo contrato y no es autoridad de fórmula final.

## P8 y drift

P8 continúa siendo la autoridad de computabilidad. Antes de emitir un `Service1GovernedComputationInputV1`, valida que:

1. toda `formula_ref` de la Evidence Matrix exista en `formula_rules_v1.json`;
2. `required_variables` de la matriz coincida con `required_inputs` canónicos;
3. `pathology_code`, expresión, unidad y variables coincidan entre regla canónica y catálogo cuando `source_status=CATALOG_MATCH`.

Cualquier divergencia bloquea (`FORMULA_RULES_MATRIX_DRIFT` o `FORMULA_RULES_CATALOG_DRIFT`). El catálogo aporta evidencia, estado de cálculo e interpretación; nunca redefine la fórmula.

## Invariantes de cierre F2

```text
ONE_MATH_AUTHORITY_SPEC = FROZEN
ALL_CURRENT_MATH_CLASSIFIED = YES
BUSINESS_FORMULA_DUPLICATE_AUTHORITY = 0
KNOWN_AGGREGATION_DEBT = EXPLICITLY_DEFERRED_TO_F8
NO_BEHAVIOR_CHANGE = REQUIRED
```

F2 no implementa F8 ni mueve el `SUM` de preparación de inputs.
