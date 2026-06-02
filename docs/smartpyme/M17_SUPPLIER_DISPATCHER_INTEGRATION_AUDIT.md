# M17 — Auditoría de integración supplier_duplicate_check al dispatcher formal

Fecha: 2026-06-03
Estado: auditoría de lectura pesada completada
Alcance: Conexión formal de `supplier_duplicate_check` al dispatcher, aprovechando `capabilities.yaml` (M20).

---

## 1. Estado real actual de supplier_duplicate_check

- **Módulo:** `pymia/smartpyme/classifications/supplier_duplicate_check.py`
- **Función principal:** `diagnose_supplier_duplicates`
- **Estado en registry (M20):** `PARTIALLY_AVAILABLE_BY_PATH`
- **Dispatcher:** `dispatcher_available: false`
- **Tests unitarios:** `tests/smartpyme/test_supplier_duplicate_check.py` (cubre PASS, BLOCKED, PARTIAL, DUPLICATE_CUIT, MISSING_CUIT, MISSING_RAZON_SOCIAL, NORMALIZATION_NEEDED, LEGAL_SUFFIX_VARIATION).
- **Conexión actual:** Solo por CLI (`pymia/smartpyme/e2e_cli.py`).

---

## 2. Qué función exacta debe invocar el dispatcher

```python
from pymia.smartpyme.classifications.supplier_duplicate_check import diagnose_supplier_duplicates
```

---

## 3. Qué input espera el plugin

```python
def diagnose_supplier_duplicates(
    *,
    excel_path: str | Path,
    tenant_id: str,
    markdown_output_path: str | Path | None = None,
) -> tuple[ExcelDiagnosticResult, str]:
```

- `excel_path`: Ruta al archivo Excel de proveedores.
- `tenant_id`: Identificador del tenant.
- `markdown_output_path`: Ruta opcional para guardar el reporte Markdown.

---

## 4. Qué output produce

Retorna una tupla `(result, status)`:
- `result`: `ExcelDiagnosticResult` (dataclass con `evidence`, `findings`, `markdown`).
- `status`: String con el estado del diagnóstico (`"BLOCKED"`, `"PASS"`, `"PARTIAL"`).

---

## 5. Qué contrato debe devolver MicroserviceExecutionResult

El dispatcher debe construir `MicroserviceExecutionResult` con:
- `tenant_id`: Extraído del candidate.
- `intake_id`: Extraído del candidate.
- `runtime_classification`: `"supplier_duplicate_check"`
- `microservice_name`: `"supplier_duplicate_check_worker"` (según `MICROSERVICE_MAP` en `runtime_bridge.py`).
- `status`: `"EXECUTED"`, `"FAILED"` o `"BLOCKED"`.
- `output_refs`: Lista con la ruta del `markdown_output_path` si se generó.
- `findings_count`: `len(result.findings)`
- `raw_result`: `asdict(result)` del `ExcelDiagnosticResult` (el primer elemento de la tupla).

**Nota crítica:** `diagnose_supplier_duplicates` devuelve una tupla, a diferencia de `diagnose_excel` que devuelve un solo objeto. El dispatcher debe hacer `result, _ = diagnose_supplier_duplicates(...)` o usar `result[0]` para `raw_result`.

---

## 6. Qué tests existentes ya cubren supplier

- `tests/smartpyme/test_supplier_duplicate_check.py`: Tests unitarios del plugin.
- `tests/smartpyme/test_capability_registry.py`: Verifica que `dispatcher_available` es `False` y `status` es `PARTIALLY_AVAILABLE_BY_PATH`.
- `tests/smartpyme/test_one_microservice_smoke.py`: Defiende explícitamente que el dispatcher NO carga supplier y que es `UNSUPPORTED`.
- `tests/smartpyme/e2e/test_pipeline_radiography_excel.py`: El escenario `unsupported_runtime_classification` usa `excel_proveedores` y espera que el pipeline bloquee o devuelva `UNSUPPORTED`.

---

## 7. Qué tests nuevos requiere M17

### 7.1. Tests de dispatcher (reemplazos y nuevos)

- **Reemplazar** `test_dispatcher_does_not_import_supplier_duplicate_check` por un test que verifique que supplier se ejecuta correctamente al despachar.
- **Reemplazar** `test_unsupported_runtime_returns_unsupported` para que use `unknown_runtime_classification` en lugar de `supplier_duplicate_check`.
- **Nuevo** `test_supplier_duplicate_check_ready_candidate_executes`:
  - Crear fixture Excel mínimo de proveedores (columnas: `proveedor`, `cuit`, `razon_social`).
  - Construir `RuntimeExecutionCandidate` con `runtime_classification="supplier_duplicate_check"`, `status="READY_TO_EXECUTE"`, `can_dispatch=True`.
  - Aserciones: `status == "EXECUTED"`, `findings_count >= 0`, `output_refs` poblado si `output_dir` fue provisto, `raw_result` contiene `findings`.

### 7.2. Tests de registry

- **Actualizar** `test_supplier_duplicate_check_is_not_dispatcher_available` en `test_capability_registry.py`:
  - Cambiar a `test_supplier_duplicate_check_is_dispatcher_available`.
  - Aserciones: `dispatcher_available == True`, `status` en `{"AVAILABLE", "PIPELINE_CERTIFIED"}`.

### 7.3. Tests de Pipeline Radiography (e2e)

- **Nuevo escenario** en `scenarios_registry.py`: `supplier_duplicate_check_happy_path`.
  - `evidence_type`: `"excel_proveedores"`
  - `expected.runtime_classification`: `"supplier_duplicate_check"`
  - `expected.dispatch_status`: `"EXECUTED"`
- **Nuevo test** en `test_pipeline_radiography_excel.py`: `test_supplier_pipeline_happy_path_reaches_ready_to_deliver`.
  - Aserciones: `overall_status == "PASS"`, `final_status == "READY_TO_DELIVER"`, `runtime_classification == "supplier_duplicate_check"`, `dispatch_status == "EXECUTED"`.

---

## 8. Qué cambios mínimos haría Codex

### 8.1. Código

- `pymia/smartpyme/microservice_dispatcher.py`:
  - Agregar import de `diagnose_supplier_duplicates`.
  - Agregar rama en `dispatch_candidate`:
    ```python
    if runtime_classification == "supplier_duplicate_check":
        result, _ = diagnose_supplier_duplicates(
            excel_path=evidence_path,
            tenant_id=tenant_id,
            markdown_output_path=markdown_output_path,
        )
        # construir MicroserviceExecutionResult
    ```

### 8.2. Registry

- `pymia/smartpyme/capabilities.yaml`:
  - `supplier_duplicate_check`:
    - `status: AVAILABLE` (o `PIPELINE_CERTIFIED` si pasa radiografía).
    - `dispatcher_available: true`
    - `pipeline_certified: true` (si pasa radiografía).

### 8.3. Tests

- `tests/smartpyme/test_one_microservice_smoke.py`: Reemplazar tests de contrato viejo.
- `tests/smartpyme/test_capability_registry.py`: Actualizar aserciones de supplier.
- `pymia/pipeline_radiography/scenarios_registry.py`: Agregar escenario `supplier_duplicate_check_happy_path`.
- `tests/smartpyme/e2e/test_pipeline_radiography_excel.py`: Agregar test e2e de supplier.

---

## 9. Cómo debe actualizarse capabilities.yaml después de conectar

```yaml
  - capability_id: supplier_duplicate_check
    label: Revision de proveedores duplicados
    status: PIPELINE_CERTIFIED  # o AVAILABLE si no pasa radiografía aún
    pipeline_certified: true
    dispatcher_available: true
    cli_available: true
    plugin_module: pymia.smartpyme.classifications.supplier_duplicate_check
    plugin_function: diagnose_supplier_duplicates
    dispatcher_classification: supplier_duplicate_check
    # ... tests y docs ...
    no_promise_reason: null  # eliminar este campo
```

---

## 10. Qué riesgos hay de falso positivo o contrato roto

### Riesgo 1: Manejo de la tupla de retorno
`diagnose_supplier_duplicates` devuelve `tuple[ExcelDiagnosticResult, str]`, mientras que `diagnose_excel` devuelve solo `ExcelDiagnosticResult`.
**Mitigación:** El dispatcher debe desempaquetar la tupla: `result, _ = diagnose_supplier_duplicates(...)`.

### Riesgo 2: Escenario `unsupported_runtime_classification` roto
El escenario actual en `scenarios_registry.py` usa `evidence_type="excel_proveedores"` y espera `UNSUPPORTED`.
Sin embargo, `readiness.py` ya tiene `RUNTIME_CLASSIFICATION_SUPPLIER_DUPLICATE_CHECK` en `ALLOWED_RUNTIME_CLASSIFICATIONS`. Si el `evidence_type` `"excel_proveedores"` habilita la clasificación `supplier_duplicate_check` en `intake.py`, el pipeline ya no devolverá `UNSUPPORTED`, sino que intentará ejecutarlo.
**Mitigación:** Cambiar el escenario `unsupported_runtime_classification` para usar un `evidence_type` que no habilite ninguna clasificación soportada, o usar un `owner_message` que no mapee a ninguna clasificación.

### Riesgo 3: Import perezoso vs directo
Si `microservice_dispatcher.py` importa `diagnose_supplier_duplicates` al nivel del módulo, se rompe el contrato de lazy loading defendido por `test_dispatcher_does_not_import_supplier_duplicate_check`.
**Mitigación:** Decidir explícitamente si se acepta import directo (más simple) o se mantiene lazy import (importar dentro de la función `dispatch_candidate`). Si se mantiene lazy, el test debe reescribirse para verificar que no se carga al importar, pero sí al despachar.

### Riesgo 4: Fixture Excel de proveedores
Se necesita un fixture Excel válido para supplier (`proveedor`, `cuit`, `razon_social`) en `tests/fixtures/smartpyme/`.
**Mitigación:** Crear `proveedores_duplicados.xlsx` con datos mínimos que generen al menos un finding (ej. CUIT duplicado).

---

## 11. Mapa de archivos a tocar

| Archivo | Acción |
|---------|--------|
| `pymia/smartpyme/microservice_dispatcher.py` | Agregar rama para `supplier_duplicate_check`. |
| `pymia/smartpyme/capabilities.yaml` | Actualizar `status` y `dispatcher_available`. |
| `tests/smartpyme/test_one_microservice_smoke.py` | Reemplazar tests de contrato viejo. |
| `tests/smartpyme/test_capability_registry.py` | Actualizar aserciones de supplier. |
| `pymia/pipeline_radiography/scenarios_registry.py` | Agregar escenario `supplier_duplicate_check_happy_path`. |
| `tests/smartpyme/e2e/test_pipeline_radiography_excel.py` | Agregar test e2e de supplier. |
| `tests/fixtures/smartpyme/proveedores_duplicados.xlsx` | Crear fixture (nuevo). |

---

## 12. Tests mínimos requeridos

1. `test_supplier_duplicate_check_ready_candidate_executes` (dispatcher smoke).
2. `test_supplier_duplicate_check_is_dispatcher_available` (registry).
3. `test_supplier_pipeline_happy_path_reaches_ready_to_deliver` (e2e radiography).
4. `test_unknown_runtime_returns_unsupported` (reemplazo del test viejo de unsupported).

---

## 13. Veredicto

**READY_FOR_GEMINI_REVIEW**

### Causa

- El plugin `supplier_duplicate_check` existe, está testeado y tiene contrato claro.
- `capabilities.yaml` (M20) ya lo registra con `dispatcher_classification: supplier_duplicate_check`.
- `runtime_bridge.py` ya mapea `supplier_duplicate_check` a `supplier_duplicate_check_worker`.
- `readiness.py` ya incluye `RUNTIME_CLASSIFICATION_SUPPLIER_DUPLICATE_CHECK` en `ALLOWED_RUNTIME_CLASSIFICATIONS`.
- Los cambios requeridos son locales al dispatcher y tests, sin refactor de contratos del pipeline.
- Los riesgos (tupla de retorno, escenario unsupported roto) están identificados y tienen mitigación clara.

Codex puede implementar M17 sin ambigüedades siguiendo este mapa.
