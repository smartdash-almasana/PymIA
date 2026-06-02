# SmartPyme — Plan concreto de radiografía operacional del pipeline

Fecha: 2026-06-01  
Estado: plan de implementación  
Alcance: testing real del pipeline determinístico central SmartPyme, sin bordes externos.

---

## 1. Propósito

Este documento define un plan concreto para dejar atrás inferencias y ambigüedades sobre el pipeline determinístico de SmartPyme.

Objetivo:

```text
radiografiar el pipeline fase por fase,
ejecutar escenarios operativos controlados,
registrar evidencia computacional de cada etapa,
y producir un veredicto trazable: PASS, BLOCKED_EXPECTED, FAIL o AMBIGUOUS.
```

---

## 2. Problema actual

El repo tiene muchos tests verdes y varias piezas sanas.

Pero eso no equivale automáticamente a:

```text
pipeline determinístico central certificado end-to-end.
```

Hoy existen tests unitarios, tests contractuales y caminos parciales, pero falta un mecanismo que diga con evidencia:

```text
este caso entró por el inicio correcto,
pasó por estas fases,
se bloqueó aquí o entregó allá,
y el resultado coincide con el contrato.
```

---

## 3. Qué NO entra en este plan

Este plan no certifica:

```text
Telegram
PDF
HTML
Docling
UI
supracorteza IA runtime
resident AI harness
memoria avanzada
nuevos plugins
```

Sólo certifica el pipeline determinístico central.

---

## 4. Pipeline central a radiografiar

El circuito canónico es:

```text
intake
→ evidence_requirement
→ evidence
→ evidence_gate
→ readiness
→ runtime_bridge
→ microservice_dispatcher
→ plugin
→ microservice_execution_result
→ execution_result_gate
→ delivery_package
```

Primera ficha a certificar:

```text
excel_diagnostic
```

---

## 5. Concepto: Pipeline Radiography

Pipeline Radiography es un banco de pruebas operacional.

No reemplaza pytest.

Usa pytest para ejecutar escenarios, pero produce una traza estructurada de todo el circuito.

Debe responder:

```text
qué fase corrió,
qué input recibió,
qué output produjo,
qué estado devolvió,
qué contrato aplicaba,
y si el resultado coincide con lo esperado.
```

---

## 6. Veredictos posibles

```text
PASS
BLOCKED_EXPECTED
FAIL
AMBIGUOUS
```

### PASS

El escenario completó el pipeline y entregó el resultado esperado.

### BLOCKED_EXPECTED

El escenario se bloqueó donde debía bloquearse.

Ejemplo:

```text
falta evidencia → no debe despachar.
```

### FAIL

El escenario produjo un estado contrario al contrato.

Ejemplo:

```text
faltaba evidencia pero igual despachó.
```

### AMBIGUOUS

El escenario no puede evaluarse porque falta contrato, registry o expectativa clara.

---

## 7. Estructura propuesta en repo

```text
pymia/pipeline_radiography/
  __init__.py
  scenario.py
  trace.py
  runner.py
  contract_checker.py
  registry_checker.py
  report.py

tests/smartpyme/e2e/
  test_pipeline_radiography_excel.py

tests/fixtures/smartpyme/
  ventas_costos_margen.xlsx
  ventas_costos_sin_evidencia.json

docs/smartpyme/
  SMARTPYME_PIPELINE_RADIOGRAPHY_IMPLEMENTATION_PLAN.md
```

---

## 8. Módulo 1 — Scenario Catalog

Archivo sugerido:

```text
pymia/pipeline_radiography/scenario.py
```

Responsabilidad:

```text
definir escenarios operativos controlados.
```

Modelo mínimo:

```python
@dataclass(frozen=True)
class PipelineScenario:
    scenario_id: str
    tenant_id: str
    owner_message: str
    evidence_items: tuple[ScenarioEvidence, ...]
    expected: ScenarioExpectation
```

Evidencia:

```python
@dataclass(frozen=True)
class ScenarioEvidence:
    evidence_type: str
    source_kind: str
    source_ref: str
    metadata: dict[str, object]
```

Expectativa:

```python
@dataclass(frozen=True)
class ScenarioExpectation:
    final_status: str
    runtime_classification: str | None = None
    dispatch_status: str | None = None
    min_findings_count: int = 0
    must_not_dispatch: bool = False
```

---

## 9. Primer escenario obligatorio

### `margin_excel_happy_path`

```yaml
scenario_id: margin_excel_happy_path
tenant_id: tenant_demo
owner_message: "No sé si vendo con margen"
evidence:
  - type: excel_ventas_costos
    source_kind: uploaded_file
    source_ref: tests/fixtures/smartpyme/ventas_costos_margen.xlsx
    metadata:
      columns:
        - producto
        - ventas
        - costo
expected:
  final_status: READY_TO_DELIVER
  runtime_classification: excel_diagnostic
  dispatch_status: EXECUTED
  min_findings_count: 1
```

---

## 10. Fixture inicial

Archivo:

```text
tests/fixtures/smartpyme/ventas_costos_margen.xlsx
```

Contenido mínimo:

```text
producto | ventas | costo
A        | 100    | 95
B        | 120    | vacío
C        | 200    | 80
C        | 200    | 80
```

Debe producir al menos un hallazgo.

---

## 11. Módulo 2 — Pipeline Trace

Archivo sugerido:

```text
pymia/pipeline_radiography/trace.py
```

Responsabilidad:

```text
capturar una radiografía estructurada de cada fase.
```

Modelo mínimo:

```python
@dataclass
class PipelineStageTrace:
    name: str
    status: str
    input_type: str | None = None
    output_type: str | None = None
    summary: dict[str, object] = field(default_factory=dict)
    error: str | None = None

@dataclass
class PipelineTrace:
    trace_id: str
    scenario_id: str
    stages: list[PipelineStageTrace]
    overall_status: str
    blocked_at: str | None = None
    final_summary: dict[str, object] = field(default_factory=dict)
```

Ejemplo de traza:

```yaml
trace_id: trace_001
scenario_id: margin_excel_happy_path
stages:
  - name: intake
    status: OK
    output_type: IntakeRecord
  - name: evidence_gate
    status: READY
    output_type: EvidenceSufficiencyResult
  - name: readiness
    status: READY_FOR_ANALYSIS
    runtime_classification: excel_diagnostic
  - name: dispatcher
    status: EXECUTED
    findings_count: 3
overall_status: PASS
```

---

## 12. Módulo 3 — Runner determinístico

Archivo sugerido:

```text
pymia/pipeline_radiography/runner.py
```

Responsabilidad:

```text
ejecutar el pipeline formal paso a paso y registrar la traza.
```

No debe usar:

```text
e2e_cli
Telegram
IA
HTML
PDF
```

Debe usar módulos reales:

```text
create_intake_record
evidence_requirement / EvidenceRecord
evaluate_evidence_sufficiency
evaluate_analysis_readiness
prepare_runtime_execution
dispatch_candidate
execution_result_gate
build_delivery_package
```

---

## 13. Módulo 4 — Contract Checker

Archivo sugerido:

```text
pymia/pipeline_radiography/contract_checker.py
```

Responsabilidad:

```text
validar si cada fase recibió y produjo lo que el contrato esperaba.
```

Debe detectar:

```text
fase faltante
fase ejecutada de más
input incorrecto
output incorrecto
estado inválido
dispatch prematuro
entrega sin gate PASS
```

---

## 14. Módulo 5 — Registry Checker

Archivo sugerido:

```text
pymia/pipeline_radiography/registry_checker.py
```

Responsabilidad:

```text
comparar ejecución real contra el registry de capacidades.
```

Ejemplo:

```yaml
classification: supplier_duplicate_check
registry:
  dispatcher_available: false
  cli_available: true
actual:
  dispatcher_status: UNSUPPORTED
result: EXPECTED_UNSUPPORTED
```

Esto separa bug de capacidad parcial.

---

## 15. Módulo 6 — Developer Report

Archivo sugerido:

```text
pymia/pipeline_radiography/report.py
```

Responsabilidad:

```text
generar reporte humano para desarrollador.
```

Ejemplo:

```text
Scenario: margin_excel_happy_path
Result: PASS

Pipeline:
- intake: OK
- evidence_requirement: OK
- evidence: OK
- evidence_gate: READY
- readiness: READY_FOR_ANALYSIS
- runtime_bridge: READY_TO_EXECUTE
- dispatcher: EXECUTED
- delivery: READY_TO_DELIVER

Verdict:
Pipeline formal excel_diagnostic certificado para este escenario.
```

---

## 16. Tests requeridos

### 16.1 Happy path

```text
test_excel_pipeline_happy_path_reaches_ready_to_deliver
```

Debe afirmar:

```text
overall_status == PASS
final_status == READY_TO_DELIVER
runtime_classification == excel_diagnostic
dispatch_status == EXECUTED
findings_count > 0
output_refs no vacío
```

### 16.2 Bloqueo sin evidencia

```text
test_margin_without_evidence_blocks_before_dispatch
```

Debe afirmar:

```text
overall_status == BLOCKED_EXPECTED
blocked_at in [evidence_gate, readiness]
must_not_dispatch == true
```

### 16.3 Classification desconocida

```text
test_unknown_classification_is_unsupported
```

Debe afirmar:

```text
status == UNSUPPORTED
no delivery READY_TO_DELIVER
```

### 16.4 Plugin failure

```text
test_corrupt_excel_fails_without_delivery
```

Debe afirmar:

```text
dispatch_status == FAILED
delivery_status != READY_TO_DELIVER
```

---

## 17. Comando focal de certificación

```bash
python -m pytest tests/smartpyme/e2e/test_pipeline_radiography_excel.py -q
```

Luego:

```bash
python -m pytest tests/smartpyme -q
```

---

## 18. Criterio de aceptación M19

M19 puede cerrarse cuando:

```text
[ ] existe Scenario model;
[ ] existe Trace model;
[ ] existe runner determinístico sin CLI;
[ ] existe primer fixture Excel realista;
[ ] existe happy path excel_diagnostic;
[ ] existen negativos mínimos;
[ ] reporta PASS/BLOCKED_EXPECTED/FAIL/AMBIGUOUS;
[ ] registry checker no contradice el registry;
[ ] no mezcla Telegram, HTML, PDF ni IA runtime;
[ ] suite focal pasa.
```

---

## 19. Orden de implementación

### M19.1 — Estructuras base

Crear:

```text
pymia/pipeline_radiography/scenario.py
pymia/pipeline_radiography/trace.py
```

Sin ejecutar pipeline todavía.

### M19.2 — Runner mínimo Excel

Crear:

```text
pymia/pipeline_radiography/runner.py
```

Sólo happy path Excel.

### M19.3 — Test Drive inicial

Crear fixture y test:

```text
tests/fixtures/smartpyme/ventas_costos_margen.xlsx
tests/smartpyme/e2e/test_pipeline_radiography_excel.py
```

### M19.4 — Contract checker

Agregar validaciones de fase y estados.

### M19.5 — Negativos mínimos

Agregar escenarios de bloqueo.

### M19.6 — Registry checker

Comparar ejecución contra registry.

### M19.7 — Developer report

Generar reporte textual o JSON para lectura humana y futura IA residente.

---

## 20. Relación con IA residente

Pipeline Radiography no es la IA residente.

Es la fuente de hechos que la IA residente debe interpretar.

Secuencia sana:

```text
Pipeline determinístico
→ Pipeline Radiography
→ Developer Report
→ IA residente interpreta el reporte
```

No al revés.

---

## 21. Veredicto

La solución para dejar atrás ambigüedades no es seguir discutiendo inferencias.

La solución es construir una radiografía operacional del pipeline.

```text
Cada escenario debe producir una traza.
Cada traza debe compararse contra contratos.
Cada resultado debe devolver un veredicto.
```

---

## 22. Frase rectora

```text
No se declara sano un pipeline por intuición.
Se lo radiografía por escenarios.
```
