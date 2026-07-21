# Servicio 1 — CYCLE_045B: PYME_013 como primera capacidad compuesta

**Estado:** DECIDED_FOR_IMPLEMENTATION  
**Capacidad:** `payment_collection_gap`  
**Patología:** `PYME_013`  
**Tipo:** `COMPOSITE`

## Objetivo

Conectar `PYME_013` a la raíz productiva única mediante el Generic Capability Kernel, consumiendo exclusivamente resultados gobernados previos de `dso` y `dpo`.

## Fórmula

```text
payment_collection_gap_days = dso_days - dpo_days
```

## Principio rector

`PYME_013` no lee evidencia cruda, no reconstruye DSO ni DPO y no ejecuta capacidades prerequisito de manera implícita.

Flujo autorizado:

```text
resultado gobernado DSO + resultado gobernado DPO
→ validación de identidad, estado, unidad y flags
→ fórmula compuesta
→ clasificación
→ outcome acotado
```

## Entrada compuesta

La ejecución genérica extiende su interfaz con:

```python
governed_results: object = None
```

Para capacidades `ATOMIC`, `governed_results` no participa en la resolución de inputs.

Para capacidades `COMPOSITE`, `normalized_tables` y `column_refs` no son fuente de variables. Cada variable debe resolverse exactamente una vez desde `governed_results`.

Forma mínima de cada resultado gobernado:

```json
{
  "status": "EVALUATED",
  "capability_ref": "dso",
  "pathology_code": "PYME_011",
  "computed": {
    "typed_result": {
      "value": 30.0,
      "unit": "days",
      "provenance": "owner_confirmed_normalized_evidence"
    }
  },
  "runtime_authorized": false,
  "tool_execution_authorized": false,
  "product_ready": false,
  "delivery_authorized": false,
  "diagnosis_generated": false
}
```

## Bindings compuestos

El `computation_plan` debe declarar:

```json
{
  "source_bindings": {
    "dso_days": {
      "capability_ref": "dso",
      "result_key": "dso_days"
    },
    "dpo_days": {
      "capability_ref": "dpo",
      "result_key": "dpo_days"
    }
  }
}
```

No se admiten bindings por nombre de columna para una capacidad `COMPOSITE`.

## Validaciones obligatorias

Cada prerequisito debe:

1. existir exactamente una vez;
2. tener `status = EVALUATED`;
3. coincidir con el `capability_ref` declarado;
4. contener el `result_key` declarado;
5. contener `typed_result.value` numérico y finito;
6. usar unidad `days`;
7. mantener todos los flags de autorización explícitamente en `false`;
8. no contener diagnóstico causal habilitado.

Ante cualquier incumplimiento, `PYME_013` queda `BLOCKED` y no se ejecuta la fórmula.

## Definición de capacidad

```text
capability_ref: payment_collection_gap
pathology_code: PYME_013
formula_ref: PYME_013_dso_dpo_gap
kind: COMPOSITE
variables:
  - dso_days, SINGLE_VALUE, minimum 0 inclusive, unit days
  - dpo_days, SINGLE_VALUE, minimum 0 inclusive, unit days
formula: SUBTRACT(VARIABLE(dso_days), VARIABLE(dpo_days))
result_key: payment_collection_gap_days
result_unit: days
```

## Clasificaciones

| Regla | Código |
|---|---|
| resultado `< 0` | `COLLECTIONS_BEFORE_PAYMENTS` |
| resultado `= 0` | `COLLECTIONS_MATCH_PAYMENTS` |
| resultado `> 0` | `COLLECTIONS_AFTER_PAYMENTS` |

## Outcome

El hallazgo describe únicamente la relación temporal observada entre cobros y pagos. No afirma causas, insolvencia, mala gestión ni necesidad automática de financiamiento.

## Integración en raíz

La raíz acepta `requested_capability="payment_collection_gap"` sólo cuando recibe resultados gobernados explícitos mediante un nuevo argumento público opcional:

```python
governed_results: object = None
```

La raíz no ejecuta `dso` ni `dpo` para completar faltantes.

La entrega física permanece bloqueada con:

```text
PYME_013_DELIVERY_NOT_AUTHORIZED
```

## Invariantes

- una sola raíz productiva;
- una sola ejecución del kernel por solicitud;
- prerequisitos explícitos;
- sin lectura de evidencia cruda para `PYME_013`;
- sin selección automática;
- sin ejecución implícita;
- sin LLM;
- sin diagnóstico causal;
- todos los flags cerrados;
- DSO y DPO continúan siendo capacidades atómicas independientes.

## Criterio de cierre

`CYCLE_045B` cierra en PASS cuando `PYME_013` funciona con resultados gobernados válidos, bloquea todos los prerequisitos inválidos o ausentes, permanece sin delivery y la regresión completa queda verde.
