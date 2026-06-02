# M19.5 — Negative Scenarios Audit

Fecha: 2026-06-02  
Estado: auditoría de lectura pesada  
Alcance: matriz mínima de escenarios negativos viables según contratos reales.

---

## 1. Escenarios negativos existentes

### 1.1 Ya implementados

| Escenario | Archivo | Qué prueba |
|---|---|---|
| `margin_excel_missing_evidence` | `tests/smartpyme/e2e/test_pipeline_radiography_excel.py` | Bloqueo antes de dispatch por falta de evidencia (`evidence_gate` → `NEEDS_MORE_EVIDENCE`, `readiness` → `NEEDS_EVIDENCE`). |

### 1.2 Cobertura actual

- **no dispatch prematuro**: ✅ Cubierto.
- **unsupported classification**: ❌ No cubierto.
- **execution failure**: ❌ No cubierto.
- **undeliverable output_refs**: ❌ No cubierto.
- **evidence mismatch**: ❌ No cubierto (solo falta total de evidencia).

---

## 2. Escenarios negativos viables sin cambiar contratos

### 2.1 Unsupported classification

**Contrato real**:
- `readiness.py` → `READINESS_UNSUPPORTED` si no se puede resolver `runtime_classification` (ambigüedad o ninguna habilitada).
- `microservice_dispatcher.py` → `EXECUTION_UNSUPPORTED` si `runtime_classification != "excel_diagnostic"`.

**Escenario viable**:
```python
scenario_id: unsupported_runtime_classification
owner_message: "Quiero verificar duplicados de proveedores"
evidence: excel_proveedores (evidence_type que habilita supplier_duplicate_check)
expected:
  final_status: UNSUPPORTED
  must_not_dispatch: true
```

**Flujo esperado**:
1. `intake` → `NEEDS_EVIDENCE` o `READY_FOR_ANALYSIS`.
2. `evidence` → registra evidencia.
3. `evidence_gate` → `READY` (si la evidencia satisface el request).
4. `readiness` → `UNSUPPORTED` (si solo `supplier_duplicate_check` está habilitado, o si hay ambigüedad sin desempate).
5. `runtime_bridge` → `UNSUPPORTED` (si `readiness` retornó `UNSUPPORTED`).
6. **No llega a `microservice_dispatcher`** porque `can_dispatch == False`.

**Alternativa**: Forzar que `readiness` retorne `READY_FOR_ANALYSIS` con `runtime_classification="supplier_duplicate_check"`. Esto requiere que el `IntakeRecord` tenga `evidence_requests` que habiliten solo `supplier_duplicate_check` y que `tank_selection_result` no cause ambigüedad. Luego `microservice_dispatcher` retornaría `EXECUTION_UNSUPPORTED`.

**Viabilidad**: ✅ Alta. No requiere refactor.

### 2.2 Execution failure

**Contrato real**:
- `microservice_dispatcher.py` → `EXECUTION_FAILED` si `diagnose_excel` lanza excepción.
- `execution_result_gate.py` → `VERDICT_FAILED` si `status == "FAILED"`.

**Escenario viable**:
```python
scenario_id: excel_diagnostic_execution_failure
owner_message: "No sé si vendo con margen"
evidence: excel_corrupto.xlsx (archivo que causa excepción en diagnose_excel)
expected:
  final_status: FAILED
  dispatch_status: FAILED
```

**Flujo esperado**:
1. `intake` → `NEEDS_EVIDENCE` o `READY_FOR_ANALYSIS`.
2. `evidence` → registra evidencia con `source_ref=excel_corrupto.xlsx`.
3. `evidence_gate` → `READY`.
4. `readiness` → `READY_FOR_ANALYSIS`, `runtime_classification="excel_diagnostic"`.
5. `runtime_bridge` → `READY_TO_EXECUTE`.
6. `microservice_dispatcher` → `EXECUTION_FAILED` (excepción en `diagnose_excel`).
7. `execution_result_gate` → `VERDICT_FAILED`.
8. `delivery_package` → `FAILED`.

**Viabilidad**: ✅ Alta. Requiere fixture `excel_corrupto.xlsx` que cause excepción real en `diagnose_excel`. Alternativa: mockear `diagnose_excel` para lanzar excepción (pero eso no es e2e real).

### 2.3 Undeliverable output_refs

**Contrato real**:
- `execution_result_gate.py` → `VERDICT_UNDELIVERABLE` si `output_refs` está vacío o contiene rutas que no existen físicamente.

**Escenario viable**:
```python
scenario_id: undeliverable_output_refs
owner_message: "No sé si vendo con margen"
evidence: excel_ventas_costos_margen.xlsx
expected:
  final_status: FAILED
  dispatch_status: EXECUTED
  gate_verdict: UNDELIVERABLE
```

**Flujo esperado**:
1. `intake` → `READY_FOR_ANALYSIS`.
2. `evidence` → registra evidencia.
3. `evidence_gate` → `READY`.
4. `readiness` → `READY_FOR_ANALYSIS`.
5. `runtime_bridge` → `READY_TO_EXECUTE`.
6. `microservice_dispatcher` → `EXECUTED` (pero no genera `output_refs` o los genera en rutas inexistentes).
7. `execution_result_gate` → `VERDICT_UNDELIVERABLE` (porque `output_refs` está vacío o las rutas no existen).
8. `delivery_package` → `FAILED`.

**Cómo forzar**:
- Opción A: Modificar `microservice_dispatcher` para que no genere `output_refs` (pero eso cambia el contrato).
- Opción B: Mockear `diagnose_excel` para que no cree el archivo de salida (pero eso no es e2e real).
- Opción C: Ejecutar el pipeline, luego borrar manualmente el archivo de salida antes de que `execution_result_gate` lo valide (pero el runner ejecuta todo secuencialmente, no hay punto de inyección).
- Opción D: Pasar `output_dir=None` al runner (pero el runner siempre crea un `output_dir` temporal).

**Viabilidad**: ⚠️ Media. Requiere inyección de dependencia o mock para simular que `diagnose_excel` no genera el archivo. Alternativa: crear un escenario donde `diagnose_excel` retorne un resultado válido pero no cree el archivo Markdown (si eso es posible según el contrato de `diagnose_excel`).

### 2.4 Evidence mismatch

**Contrato real**:
- `evidence_gate.py` → `NEEDS_MORE_EVIDENCE` si los `EvidenceRecord` no satisfacen los `IntakeEvidenceRequest`.

**Escenario viable**:
```python
scenario_id: evidence_type_mismatch
owner_message: "No sé si vendo con margen"
evidence: excel_incorrecto.xlsx (evidence_type="excel_proveedores" en lugar de "excel_ventas_costos")
expected:
  final_status: NEEDS_EVIDENCE
  must_not_dispatch: true
```

**Flujo esperado**:
1. `intake` → `NEEDS_EVIDENCE` (solicita `excel_ventas_costos`).
2. `evidence` → registra evidencia con `evidence_type="excel_proveedores"` (no matchea el request).
3. `evidence_gate` → `NEEDS_MORE_EVIDENCE` (porque no hay evidencia que satisfaga `excel_ventas_costos`).
4. `readiness` → `NEEDS_EVIDENCE`.
5. **No llega a `runtime_bridge`** porque `can_execute == False`.

**Viabilidad**: ✅ Alta. Solo requiere proporcionar evidencia con `evidence_type` incorrecto.

---

## 3. Escenarios negativos que requieren refactor

### 3.1 Ninguno crítico

Los contratos actuales ya soportan todos los modos de fallo relevantes:
- `readiness` → `UNSUPPORTED`.
- `microservice_dispatcher` → `UNSUPPORTED`, `FAILED`.
- `execution_result_gate` → `UNDELIVERABLE`, `FAILED`, `BLOCKED`.
- `evidence_gate` → `NEEDS_MORE_EVIDENCE`, `BLOCKED`.

### 3.2 Refactor menor opcional

El runner actualmente calcula `overall_status` comparando `final_status` con `scenario.expected.final_status`. Si el escenario espera `FAILED` pero el runner retorna `FAIL` (porque `final_status != scenario.expected.final_status`), el test fallará.

**Problema**:
```python
if final_status != scenario.expected.final_status:
    overall_status = "FAIL"
```

Si `scenario.expected.final_status = "FAILED"` y `final_status = "FAILED"`, entonces `overall_status = "PASS"`. Esto es correcto.

Pero si el escenario espera `dispatch_status = "FAILED"` y `execution_result.status = "FAILED"`, el runner debe asegurar que `dispatch_status` se extraiga correctamente de `execution_result`.

**Estado actual**: El runner ya extrae `dispatch_status = str((execution_result or {}).get("status") or "")`. Esto es correcto.

**Conclusión**: No se requiere refactor para los escenarios negativos propuestos.

---

## 4. Escenarios negativos de humo o demasiado artificiales

### 4.1 Unit tests disfrazados

- **intake ValueError**: Probar que `create_intake_record` lanza `ValueError` si `tenant_id` está vacío. Esto es un test unitario, no un escenario de pipeline.
- **evidence ValueError**: Probar que `create_evidence_record` lanza `ValueError` si `source_kind` es inválido. Test unitario.
- **readiness ValueError**: Probar que `evaluate_analysis_readiness` lanza `ValueError` si `tenant_id` no coincide. Test unitario.

**Veredicto**: ❌ No incluir en M19.5. Estos tests ya existen en `tests/smartpyme/test_intake.py`, `test_evidence.py`, etc.

### 4.2 Escenarios demasiado específicos

- **evidence_gate BLOCKED por intake_state=BLOCKED**: Requiere que `intake` retorne `intake_state="BLOCKED"`. Esto es posible, pero es un caso borde que no aporta valor al Test Drive de M19.
- **execution_result_gate UNDELIVERABLE por findings_count negativo**: `diagnose_excel` nunca retorna `findings_count` negativo. Sería artificial forzarlo.

**Veredicto**: ❌ No incluir en M19.5.

---

## 5. Matriz de escenarios recomendados

### 5.1 Prioridad alta (implementar en M19.5)

| ID | Escenario | Qué prueba | Archivo | Fixture |
|---|---|---|---|---|
| NEG-01 | `evidence_type_mismatch` | Evidence mismatch → bloqueo en `evidence_gate`. | `test_pipeline_radiography_excel.py` | `ventas_costos_margen.xlsx` (reutilizar, cambiar `evidence_type`). |
| NEG-02 | `unsupported_runtime_classification` | Unsupported classification → bloqueo en `readiness` o `microservice_dispatcher`. | `test_pipeline_radiography_excel.py` | `ventas_costos_margen.xlsx` (reutilizar, cambiar `owner_message` para forzar `supplier_duplicate_check`). |

### 5.2 Prioridad media (implementar si hay tiempo)

| ID | Escenario | Qué prueba | Archivo | Fixture |
|---|---|---|---|---|
| NEG-03 | `excel_diagnostic_execution_failure` | Execution failure → `FAILED` en `microservice_dispatcher` y `execution_result_gate`. | `test_pipeline_radiography_excel.py` | `excel_corrupto.xlsx` (nuevo fixture). |
| NEG-04 | `undeliverable_output_refs` | Undeliverable output_refs → `UNDELIVERABLE` en `execution_result_gate`. | `test_pipeline_radiography_excel.py` | `ventas_costos_margen.xlsx` (reutilizar, requiere mock o inyección). |

### 5.3 Prioridad baja (post-M19.5)

| ID | Escenario | Qué prueba | Archivo | Fixture |
|---|---|---|---|---|
| NEG-05 | `intake_blocked` | Intake bloqueado → bloqueo en `readiness`. | `test_pipeline_radiography_excel.py` | N/A (requiere `owner_message` que cause `intake_state="BLOCKED"`). |

---

## 6. Casos que prueban mejor

### 6.1 no dispatch prematuro

**Mejor caso**: `margin_excel_missing_evidence` (ya implementado).

**Por qué**: Prueba que si no hay evidencia, el pipeline se bloquea en `evidence_gate` o `readiness` y no llega a `microservice_dispatcher`. Es el negativo más importante porque garantiza que el pipeline no ejecuta análisis sin evidencia suficiente.

### 6.2 unsupported classification

**Mejor caso**: `unsupported_runtime_classification` (NEG-02).

**Por qué**: Prueba que si el pipeline no puede resolver una clasificación runtime soportada, se bloquea con `UNSUPPORTED` y no ejecuta. Esto es crítico para evitar que el pipeline intente ejecutar clasificaciones no implementadas.

### 6.3 execution failure

**Mejor caso**: `excel_diagnostic_execution_failure` (NEG-03).

**Por qué**: Prueba que si el plugin (`diagnose_excel`) falla, el pipeline captura el error y retorna `FAILED` en lugar de crashar. Esto es crítico para la robustez del pipeline.

### 6.4 undeliverable output_refs

**Mejor caso**: `undeliverable_output_refs` (NEG-04).

**Por qué**: Prueba que si el plugin no genera los archivos de salida esperados, el `execution_result_gate` lo detecta y retorna `UNDELIVERABLE`. Esto es crítico para garantizar que solo se entregan resultados completos.

### 6.5 evidence mismatch

**Mejor caso**: `evidence_type_mismatch` (NEG-01).

**Por qué**: Prueba que si la evidencia proporcionada no coincide con lo solicitado, el `evidence_gate` lo detecta y bloquea el pipeline. Esto es crítico para garantizar que el pipeline solo analiza la evidencia correcta.

---

## 7. Archivos que tocaría Codex después

### 7.1 Tests

- `tests/smartpyme/e2e/test_pipeline_radiography_excel.py`: Agregar NEG-01, NEG-02, NEG-03, NEG-04.

### 7.2 Fixtures

- `tests/fixtures/smartpyme/excel_corrupto.xlsx`: Nuevo fixture para NEG-03 (archivo Excel corrupto o inválido que cause excepción en `diagnose_excel`).

### 7.3 Runner (opcional)

- `pymia/pipeline_radiography/runner.py`: Si se detecta que el cálculo de `overall_status` no maneja correctamente los casos `FAILED` o `UNDELIVERABLE`, ajustar la lógica de comparación con `scenario.expected`.

### 7.4 No tocar

- `pymia/smartpyme/*.py`: No cambiar contratos.
- `pymia/pipeline_radiography/scenario.py`: No cambiar modelo de escenario.
- `pymia/pipeline_radiography/trace.py`: No cambiar modelo de traza.

---

## 8. Riesgos

### 8.1 Riesgo: NEG-03 requiere fixture corrupto real

**Descripción**: Para probar `execution_failure`, se necesita un archivo Excel que cause excepción real en `diagnose_excel`. Si el fixture no es lo suficientemente corrupto, `diagnose_excel` podría retornar un resultado vacío en lugar de lanzar excepción.

**Mitigación**: Crear un fixture `excel_corrupto.xlsx` que sea un archivo de texto plano con extensión `.xlsx`, o un archivo Excel con hojas vacías o estructuras inválidas que `diagnose_excel` no pueda procesar.

### 8.2 Riesgo: NEG-04 es difícil de probar sin mocks

**Descripción**: Para probar `undeliverable_output_refs`, se necesita que `diagnose_excel` no genere el archivo de salida. Pero `diagnose_excel` siempre genera el archivo si se le pasa `markdown_output_path`. La única forma es mockear `diagnose_excel` o modificar `microservice_dispatcher`.

**Mitigación**: Posponer NEG-04 a post-M19.5 o implementar un test unitario separado para `execution_result_gate` que valide el comportamiento con `output_refs` vacíos.

### 8.3 Riesgo: NEG-02 puede ser ambiguo

**Descripción**: Forzar `unsupported_runtime_classification` requiere que `readiness` retorne `UNSUPPORTED`. Esto puede ocurrir por ambigüedad (múltiples clasificaciones habilitadas) o por ninguna clasificación habilitada. El comportamiento exacto depende de cómo `intake` genere los `evidence_requests`.

**Mitigación**: Usar un `owner_message` que claramente apunte a `supplier_duplicate_check` (ej. "Quiero verificar duplicados de proveedores") y asegurar que el fixture Excel tenga columnas que habiliten solo esa clasificación.

---

## 9. Veredicto

**READY_FOR_GEMINI_REVIEW**

La matriz de escenarios negativos es viable y no requiere refactor de contratos. Los escenarios propuestos prueban los modos de fallo más críticos del pipeline:

- **NEG-01** (evidence mismatch): Prueba que el pipeline no analiza evidencia incorrecta.
- **NEG-02** (unsupported classification): Prueba que el pipeline no ejecuta clasificaciones no soportadas.
- **NEG-03** (execution failure): Prueba que el pipeline maneja errores de ejecución sin crashar.
- **NEG-04** (undeliverable output_refs): Prueba que el pipeline no entrega resultados incompletos.

Codex puede proceder a implementar NEG-01 y NEG-02 en M19.5. NEG-03 y NEG-04 pueden implementarse si hay tiempo, o posponerse a un siguiente hito.

Gemini/reviewer debe validar que:
- Los escenarios negativos no usan mocks (son e2e reales).
- Los escenarios negativos no mezclan bordes externos (Telegram, PDF, HTML, UI).
- Los escenarios negativos producen `PipelineTrace` con `overall_status` correcto.
- Los escenarios negativos no modifican contratos públicos.
