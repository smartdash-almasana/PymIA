# Servicio 1 — Cierre productivo LIQ_002

**Ciclo:** `CYCLE_042_CONNECT_LIQ_002_TO_PRODUCTIVE_ROOT`
**Estado:** `CLOSED_PASS`

## Resultado

`LIQ_002` quedó conectado a la única raíz productiva de Servicio 1 mediante solicitud explícita de la capacidad `projected_closing_cash_balance`.

```text
XLSX real
→ confirmación semántica del dueño
→ plan gobernado (CASH_PROJECTION family)
→ resolución determinística de initial_balance, expected_collections y expected_payments
→ agregación de evidencia normalizada
→ evaluación LIQ_002
→ saldo final proyectado
→ clasificación acotada
→ hallazgo y tratamiento determinísticos
```

## Clasificaciones certificadas

```text
POSITIVE_PROJECTED_BALANCE
ZERO_PROJECTED_BALANCE
NEGATIVE_PROJECTED_BALANCE
```

## Qué certifica

- La capacidad sólo se ejecuta ante solicitud explícita `projected_closing_cash_balance`.
- El plan de cómputo debe estar listo y los bindings semánticos confirmados.
- Las tres variables requeridas deben resolver de forma determinística desde evidencia normalizada.
- Se calcula `initial_balance + expected_collections - expected_payments`.
- Se producen saldo final proyectado y clasificación acotada.
- No se crea una segunda raíz productiva.
- Los nuevos módulos LIQ_002 quedaron absorbidos por la disposición modular, lock y completion gate.
- Se agregó `CASH_PROJECTION` como la sexta familia de variables priorizadas.
- Se actualizaron pathology_catalog, evidence_matrix y 8 tests por ripple consistency.

## Regresión observada

```text
1690 passed
0 failed
git diff --check: clean
working tree final: clean
```

## Límites

- No existe selección automática de capacidad.
- No se atribuyen causas, responsabilidad, fraude, error de caja ni proyección contable.
- `runtime_authorized`, `tool_execution_authorized`, `product_ready`, `delivery_authorized` y `diagnosis_generated` permanecen en falso.
- La entrega XLSX de `LIQ_002` permanece bloqueada.
- El ciclo no incorpora otras patologías ni capacidades de scrap/OEE.

## Evidencia

```text
docs/service_1_cycle_042_liq_002_productive_root_closure.v1.json
pymia/smartpyme/service_1_liq_002_evaluator_v1.py
pymia/smartpyme/service_1_liq_002_normalized_evidence_v1.py
pymia/smartpyme/service_1_liq_002_outcome_v1.py
pymia/smartpyme/service_1_product_pipeline_v1.py
pymia/smartpyme/service_1_variable_family_bindings_v1.py
tests/smartpyme/test_service_1_liq_002_semantic_governance_v1.py
```

## Próximo ciclo autorizado

```text
CYCLE_043_CONNECT_PYME_011_TO_PRODUCTIVE_ROOT
```

Este ciclo siguiente conecta `PYME_011` (DSO — Days Sales Outstanding) a la raíz productiva. Debe reutilizar la raíz, plan, guards y contratos existentes, sin implementar otras patologías ni autorizar entrega XLSX sin decisión explícita del propio ciclo.
