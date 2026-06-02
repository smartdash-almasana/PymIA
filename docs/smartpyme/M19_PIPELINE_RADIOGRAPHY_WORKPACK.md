# M19 — Pipeline Radiography v0 Workpack

Fecha: 2026-06-02  
Estado: paquete único de trabajo  
Alcance: protocolo industrial mínimo para Coder, Codex, Gemini y auditoría humana/ChatGPT.

---

## 1. Propósito

Este workpack existe para dejar de trabajar por prompts sueltos.

Objetivo:

```text
coordinar M19 — Pipeline Radiography v0
con contrato, mapa de archivos, criterios de aceptación, tests obligatorios,
prompts por agente y veredicto final.
```

El resultado esperado no es agregar features.

El resultado esperado es construir el primer Test Drive interno que radiografíe el pipeline determinístico central de SmartPyme.

---

## 2. Hito

```text
M19 — Pipeline Radiography v0
```

Definición:

```text
Banco de prueba operacional interno que ejecuta escenarios controlados,
registra una traza fase por fase,
verifica contratos,
y devuelve PASS / BLOCKED_EXPECTED / FAIL / AMBIGUOUS.
```

---

## 3. Alcance permitido

Sólo pipeline determinístico central:

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

Primera ficha canónica:

```text
excel_diagnostic
```

---

## 4. Alcance prohibido

No mezclar en M19:

```text
Telegram
PDF
HTML
Docling
UI
supracorteza IA runtime
resident AI harness runtime
memoria avanzada
nuevos plugins
supplier_duplicate_check dispatcher fix
```

`supplier_duplicate_check` queda fuera de M19 salvo como referencia de capacidad parcial documentada.

Su frente específico es M17.

---

## 5. Estructura estándar por hito

Todo hito PymIA debe tender a esta estructura:

```text
HITO
├── contrato
├── mapa de archivos
├── criterios de aceptación
├── tests obligatorios
├── prompt Coder
├── prompt Codex
├── prompt Gemini
└── veredicto final
```

M19 inaugura este protocolo.

---

## 6. Fases M19

### M19.0 — Preparación

Salida:

```text
docs/smartpyme/M19_PIPELINE_RADIOGRAPHY_WORKPACK.md
```

Este documento.

---

### M19.1 — Auditoría automática dirigida

Responsable sugerido:

```text
Coder
```

Objetivo:

```text
extraer el mapa real de contratos del pipeline.
```

Salida esperada:

```text
docs/smartpyme/M19_CONTRACT_MAP.md
```

---

### M19.2 — Implementación mínima

Responsable sugerido:

```text
Codex
```

Objetivo:

```text
implementar Scenario + Trace + Runner mínimo + test e2e Excel
contra el mapa real de contratos.
```

---

### M19.3 — Revisión externa

Responsable sugerido:

```text
Gemini
```

Objetivo:

```text
verificar que el resultado no sea humo falso ni atajo por CLI.
```

---

### M19.4 — Corrección y cierre

Responsables:

```text
Codex + ChatGPT/auditor + humano
```

Objetivo:

```text
corregir, ejecutar suite focal, producir veredicto final.
```

---

## 7. M19.1 — Tabla de auditoría dirigida

Coder debe extraer exactamente esto:

| Archivo | Qué extraer |
|---|---|
| `pymia/smartpyme/intake.py` | función principal, input, output, estados relevantes |
| `pymia/smartpyme/evidence_requirement.py` | dataclass/constructor, input, output, campos obligatorios |
| `pymia/smartpyme/evidence.py` | dataclass, estados, metadata esperada |
| `pymia/smartpyme/evidence_gate.py` | función gate, input, output, estados |
| `pymia/smartpyme/readiness.py` | función readiness, input, output, estados |
| `pymia/smartpyme/runtime_bridge.py` | función bridge, input, output, estados |
| `pymia/smartpyme/microservice_dispatcher.py` | función dispatch, input, output, estados |
| `pymia/smartpyme/delivery_package.py` | función delivery, input, output, estados |
| `execution_result_gate` donde exista | función gate, input, output, estados, path real |

Formato de salida esperado:

```markdown
# M19 Contract Map

## Phase: intake
- File:
- Function:
- Input:
- Output:
- States:
- Notes:

## Phase: evidence_requirement
...
```

Regla:

```text
No inferir nombres.
Si un path o función no existe, marcar NOT_FOUND y proponer búsqueda exacta.
```

---

## 8. M19.2 — Archivos de implementación mínima

Codex debe implementar, sólo después de tener M19_CONTRACT_MAP:

```text
pymia/pipeline_radiography/__init__.py
pymia/pipeline_radiography/scenario.py
pymia/pipeline_radiography/trace.py
pymia/pipeline_radiography/runner.py
tests/smartpyme/e2e/test_pipeline_radiography_excel.py
```

Si el repo aún no tiene carpeta `tests/smartpyme/e2e/`, crearla.

No usar:

```text
pymia/smartpyme/e2e_cli.py
```

---

## 9. Scenario model esperado

Modelo conceptual mínimo:

```python
@dataclass(frozen=True)
class PipelineScenario:
    scenario_id: str
    tenant_id: str
    owner_message: str
    evidence_items: tuple[ScenarioEvidence, ...]
    expected: ScenarioExpectation
```

```python
@dataclass(frozen=True)
class ScenarioEvidence:
    evidence_type: str
    source_kind: str
    source_ref: str
    metadata: dict[str, object]
```

```python
@dataclass(frozen=True)
class ScenarioExpectation:
    final_status: str
    runtime_classification: str | None = None
    dispatch_status: str | None = None
    min_findings_count: int = 0
    must_not_dispatch: bool = False
```

Ajustar nombres si el mapa de contratos indica mejor integración.

---

## 10. Trace model esperado

Modelo conceptual mínimo:

```python
@dataclass
class PipelineStageTrace:
    name: str
    status: str
    input_type: str | None = None
    output_type: str | None = None
    summary: dict[str, object] = field(default_factory=dict)
    error: str | None = None
```

```python
@dataclass
class PipelineTrace:
    trace_id: str
    scenario_id: str
    stages: list[PipelineStageTrace]
    overall_status: str
    blocked_at: str | None = None
    final_summary: dict[str, object] = field(default_factory=dict)
```

Estados permitidos iniciales:

```text
PASS
BLOCKED_EXPECTED
FAIL
AMBIGUOUS
```

---

## 11. Primer escenario obligatorio

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

Fixture esperado:

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

---

## 12. Runner mínimo esperado

El runner debe ejecutar el pipeline formal, no atajos.

Debe pasar por funciones reales según M19_CONTRACT_MAP:

```text
intake
evidence_requirement
evidence
evidence_gate
readiness
runtime_bridge
microservice_dispatcher
execution_result_gate
delivery_package
```

Debe producir:

```text
PipelineTrace
```

Debe marcar:

```text
blocked_at
stage status
overall_status
final_summary
```

---

## 13. Tests obligatorios M19 v0

### 13.1 Model tests

```text
tests/smartpyme/test_pipeline_radiography_models.py
```

Debe validar:

```text
Scenario serializable
Trace serializable
stage append / final_summary básico
estados explícitos
```

### 13.2 E2E happy path Excel

```text
tests/smartpyme/e2e/test_pipeline_radiography_excel.py
```

Debe validar:

```text
overall_status == PASS
final_status == READY_TO_DELIVER
runtime_classification == excel_diagnostic
dispatch_status == EXECUTED
findings_count >= 1
no uso de e2e_cli
```

### 13.3 Negativo mínimo sin evidencia

Debe validar:

```text
overall_status == BLOCKED_EXPECTED
must_not_dispatch == true
blocked_at in evidence_gate/readiness
```

Si no entra en M19.2, entra en M19.4 como mínimo antes de cierre.

---

## 14. Prompt para Coder

```text
Repo: smartdash-almasana/PymIA
Hito: M19 — Pipeline Radiography v0
Rol: auditor de contratos reales. No implementes código.

Objetivo:
Crear docs/smartpyme/M19_CONTRACT_MAP.md con el mapa real fase → archivo → función → input → output → estados.

Alcance:
Sólo pipeline determinístico central:
intake → evidence_requirement → evidence → evidence_gate → readiness → runtime_bridge → microservice_dispatcher → plugin → execution_result_gate → delivery_package.

No mezclar:
Telegram, PDF, HTML, UI, IA residente, e2e_cli, supplier dispatcher fix.

Archivos a auditar:
- pymia/smartpyme/intake.py
- pymia/smartpyme/evidence_requirement.py
- pymia/smartpyme/evidence.py
- pymia/smartpyme/evidence_gate.py
- pymia/smartpyme/readiness.py
- pymia/smartpyme/runtime_bridge.py
- pymia/smartpyme/microservice_dispatcher.py
- pymia/smartpyme/delivery_package.py
- buscar execution_result_gate y reportar path real.

Para cada fase extraer:
- función/clase principal real
- input esperado
- output producido
- estados válidos
- errores/bloqueos
- notas de integración para runner.

Reglas:
- No inferir nombres.
- Si algo no existe, marcar NOT_FOUND.
- No proponer features.
- No editar código.

Entrega:
- docs/smartpyme/M19_CONTRACT_MAP.md
- resumen de hallazgos
- riesgos para el runner
- veredicto READY_FOR_CODEX o BLOCKED con causa.
```

---

## 15. Prompt para Codex

```text
Repo: smartdash-almasana/PymIA
Hito: M19 — Pipeline Radiography v0
Rol: implementador.

Precondición:
Leer docs/smartpyme/M19_PIPELINE_RADIOGRAPHY_WORKPACK.md y docs/smartpyme/M19_CONTRACT_MAP.md.
No implementar antes de leer el mapa de contratos.

Objetivo:
Implementar Test Drive interno mínimo para radiografiar el pipeline formal excel_diagnostic.

Archivos esperados:
- pymia/pipeline_radiography/__init__.py
- pymia/pipeline_radiography/scenario.py
- pymia/pipeline_radiography/trace.py
- pymia/pipeline_radiography/runner.py
- tests/smartpyme/test_pipeline_radiography_models.py
- tests/smartpyme/e2e/test_pipeline_radiography_excel.py
- tests/fixtures/smartpyme/ventas_costos_margen.xlsx

Reglas:
- No usar pymia/smartpyme/e2e_cli.py.
- No tocar Telegram/PDF/HTML/UI.
- No tocar supplier_duplicate_check salvo que sea estrictamente para evitar interferencia, y justificar.
- No cambiar contratos públicos salvo necesidad demostrada.
- El runner debe pasar por dispatcher formal.
- El resultado debe producir PipelineTrace.

Tests mínimos:
python -m pytest tests/smartpyme/test_pipeline_radiography_models.py tests/smartpyme/e2e/test_pipeline_radiography_excel.py -q

Luego, si pasa:
python -m pytest tests/smartpyme -q

Entrega:
- archivos modificados
- comandos ejecutados
- resultados exactos
- git diff resumido
- veredicto READY_TO_COMMIT o BLOCKED con causa.
```

---

## 16. Prompt para Gemini

```text
Repo: smartdash-almasana/PymIA
Hito: M19 — Pipeline Radiography v0
Rol: revisión externa / segunda opinión.

Objetivo:
Revisar el diff de M19 y determinar si el Test Drive realmente radiografía el pipeline formal o si es humo/atajo.

Checklist obligatorio:
[ ] ¿Usa e2e_cli? Si sí, FAIL.
[ ] ¿Pasa por microservice_dispatcher formal?
[ ] ¿Incluye evidence_gate?
[ ] ¿Incluye readiness?
[ ] ¿Incluye runtime_bridge?
[ ] ¿Incluye delivery_package?
[ ] ¿Produce PipelineTrace por fases?
[ ] ¿Tiene happy path excel_diagnostic?
[ ] ¿Tiene al menos un negativo de bloqueo?
[ ] ¿El test valida outputs reales y no sólo mocks?
[ ] ¿El test mezcla Telegram/PDF/HTML/UI? Si sí, FAIL.
[ ] ¿El registry queda coherente con lo certificado?

Entrega:
- veredicto APPROVE / REQUEST_CHANGES
- lista de riesgos
- archivos problemáticos
- cambios mínimos solicitados.
```

---

## 17. Veredicto final esperado

Formato obligatorio:

```text
VEREDICTO: PASS | BLOCKED | FAIL | PARTIAL

ALCANCE:
- M19 Pipeline Radiography v0

EVIDENCIA:
- tests ejecutados
- resultados exactos
- archivos modificados
- trace/report generado si existe

DECISIÓN:
- READY_TO_COMMIT
- o BLOCKED con causa
```

---

## 18. Criterio de aceptación final

M19 v0 se considera cerrado si:

```text
[ ] existe M19_CONTRACT_MAP.md;
[ ] existen Scenario y Trace models;
[ ] existe runner mínimo formal;
[ ] existe fixture Excel realista;
[ ] existe test e2e excel_diagnostic;
[ ] no usa e2e_cli;
[ ] pasa por dispatcher formal;
[ ] produce PipelineTrace;
[ ] hay al menos un negativo de bloqueo;
[ ] pytest focal pasa;
[ ] no mezcla bordes externos;
[ ] Gemini/revisor no detecta humo falso.
```

---

## 19. Frase rectora

```text
Menos prompts sueltos. Más workpack, contrato, mapa, tests y veredicto.
```
