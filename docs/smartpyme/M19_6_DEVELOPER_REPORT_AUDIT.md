# M19.6 — Developer Report Audit

Fecha: 2026-06-03
Estado: auditoría de lectura (sin cambios de código)
Alcance: formato mínimo de reporte developer para PipelineTrace.

---

## 1. Qué información ya existe en PipelineTrace

### 1.1 PipelineTrace (pymia/pipeline_radiography/trace.py)

```python
@dataclass
class PipelineTrace:
    trace_id: str
    scenario_id: str
    stages: list[PipelineStageTrace]
    overall_status: str  # PASS, BLOCKED_EXPECTED, FAIL, AMBIGUOUS
    blocked_at: str | None
    final_summary: dict[str, Any]
```

### 1.2 PipelineStageTrace

```python
@dataclass
class PipelineStageTrace:
    name: str
    status: str
    input_type: str | None
    output_type: str | None
    summary: dict[str, Any]
    error: str | None
```

### 1.3 PipelineRunResult (pymia/pipeline_radiography/runner.py)

```python
@dataclass
class PipelineRunResult:
    trace: PipelineTrace
    intake_record: dict[str, Any]
    evidence_records: list[dict[str, Any]]
    sufficiency_result: dict[str, Any]
    readiness_result: dict[str, Any]
    runtime_candidate: dict[str, Any]
    execution_result: dict[str, Any] | None
    execution_gate_verdict: dict[str, Any] | None
    delivery_package: dict[str, Any] | None
```

### 1.4 Información capturada por el runner

El runner (`run_pipeline_scenario`) ya registra:
- `intake`: `intake_state`, `suggested_next_state`, `evidence_request_count`.
- `evidence`: `evidence_count`, `evidence_types`.
- `evidence_gate`: `suggested_next_state`, `missing_request_ids`, `matched_evidence_ids`.
- `readiness`: `runtime_classification`, `can_execute`, `blocking_reasons`.
- `runtime_bridge`: `runtime_classification`, `microservice_name`, `can_dispatch`, `blocking_reasons`.
- `microservice_dispatcher`: `output_refs`, `findings_count`, `warnings`.
- `execution_result_gate`: `reasons`, `warnings`.
- `delivery_package`: `gate_verdict`, `output_refs`.

---

## 2. Qué información falta para un reporte developer útil

### 2.1 Metadatos de ejecución

- **Timestamp:** cuándo se ejecutó el escenario.
- **Duración total:** tiempo total de ejecución del pipeline.
- **Duración por etapa:** tiempo que tomó cada fase (intake, evidence, evidence_gate, etc.).

### 2.2 Contexto del escenario

- **tenant_id:** del escenario.
- **owner_message:** mensaje original del usuario.
- **evidence_items:** lista de evidencias proporcionadas (source_ref, evidence_type).
- **expected:** valores esperados del escenario (final_status, runtime_classification, dispatch_status, min_findings_count, must_not_dispatch).

### 2.3 Detalles de error

- **Stack trace:** si una etapa lanzó excepción, el `error: str` actual no captura el traceback completo.
- **Rutas de archivos:** `source_ref` de las evidencias y `output_refs` generados (útil para debug).

### 2.4 Resumen legible

- **Motivo de PASS/FAIL:** por qué el pipeline pasó o falló (comparación entre expected y actual).
- **Stage alcanzado:** hasta qué fase llegó el pipeline antes de bloquearse o completar.

---

## 3. Formato recomendado para report.md

### 3.1 Estructura

```markdown
# Pipeline Radiography Report

## Summary
- **Scenario ID:** {scenario_id}
- **Trace ID:** {trace_id}
- **Overall Status:** {overall_status}
- **Blocked At:** {blocked_at or "N/A"}
- **Execution Time:** {total_duration}ms

## Scenario Context
- **Tenant ID:** {tenant_id}
- **Owner Message:** {owner_message}
- **Evidence Items:** {evidence_count}
  - {evidence_type}: {source_ref}

## Expected vs Actual
| Field | Expected | Actual | Match |
|---|---|---|---|
| final_status | {expected.final_status} | {final_summary.final_status} | ✅/❌ |
| runtime_classification | {expected.runtime_classification} | {final_summary.runtime_classification} | ✅/❌ |
| dispatch_status | {expected.dispatch_status} | {final_summary.dispatch_status} | ✅/❌ |
| findings_count | >= {expected.min_findings_count} | {final_summary.findings_count} | ✅/❌ |
| must_not_dispatch | {expected.must_not_dispatch} | {final_summary.must_not_dispatch} | ✅/❌ |

## Stage-by-Stage Execution

### 1. intake
- **Status:** {status}
- **Input:** {input_type}
- **Output:** {output_type}
- **Summary:** {summary}
- **Duration:** {duration}ms

### 2. evidence
...

### 3. evidence_gate
...

### 4. readiness
...

### 5. runtime_bridge
...

### 6. microservice_dispatcher
...

### 7. execution_result_gate
...

### 8. delivery_package
...

## Errors/Warnings
- {error or warning messages}

## Verdict
{overall_status}: {reason}
```

### 3.2 Ventajas

- Legible por humanos.
- Comparación directa expected vs actual.
- Timeline de ejecución por etapa.
- Contexto completo del escenario.

---

## 4. Formato recomendado para trace.json

### 4.1 Estructura

```json
{
  "trace_id": "trace_abc123",
  "scenario_id": "margin_excel_happy_path",
  "timestamp": "2026-06-03T10:00:00Z",
  "duration_ms": 1234,
  "scenario": {
    "tenant_id": "tenant_demo",
    "owner_message": "No se si vendo con margen",
    "evidence_items": [
      {
        "evidence_type": "excel_ventas_costos",
        "source_kind": "uploaded_file",
        "source_ref": "/path/to/ventas_costos_margen.xlsx"
      }
    ],
    "expected": {
      "final_status": "READY_TO_DELIVER",
      "runtime_classification": "excel_diagnostic",
      "dispatch_status": "EXECUTED",
      "min_findings_count": 1,
      "must_not_dispatch": false
    }
  },
  "trace": {
    "overall_status": "PASS",
    "blocked_at": null,
    "final_summary": {
      "final_status": "READY_TO_DELIVER",
      "runtime_classification": "excel_diagnostic",
      "dispatch_status": "EXECUTED",
      "findings_count": 5,
      "must_not_dispatch": false
    },
    "stages": [
      {
        "name": "intake",
        "status": "NEEDS_EVIDENCE",
        "input_type": "owner_message",
        "output_type": "IntakeRecord",
        "summary": {
          "intake_state": "NEEDS_EVIDENCE",
          "suggested_next_state": "NEEDS_EVIDENCE",
          "evidence_request_count": 3
        },
        "error": null,
        "duration_ms": 10
      },
      ...
    ]
  },
  "result": {
    "intake_record": {...},
    "evidence_records": [...],
    "sufficiency_result": {...},
    "readiness_result": {...},
    "runtime_candidate": {...},
    "execution_result": {...},
    "execution_gate_verdict": {...},
    "delivery_package": {...}
  }
}
```

### 4.2 Ventajas

- Machine-readable.
- Incluye todo el contexto del escenario.
- Incluye todos los resultados intermedios (no solo el trace).
- Útil para análisis posterior, dashboards, debugging.

---

## 5. Escenarios actuales que deben cubrirse

### 5.1 Happy path

- **Scenario ID:** `margin_excel_happy_path`
- **Expected:**
  - `final_status`: `READY_TO_DELIVER`
  - `runtime_classification`: `excel_diagnostic`
  - `dispatch_status`: `EXECUTED`
  - `min_findings_count`: `>= 1`
  - `must_not_dispatch`: `false`
- **Verdict esperado:** `PASS`
- **Stages presentes:** todos (intake → delivery_package).

### 5.2 Missing evidence

- **Scenario ID:** `margin_excel_missing_evidence`
- **Expected:**
  - `final_status`: `NEEDS_EVIDENCE`
  - `must_not_dispatch`: `true`
- **Verdict esperado:** `BLOCKED_EXPECTED`
- **Blocked at:** `evidence_gate` o `readiness`.
- **Stages presentes:** solo intake, evidence, evidence_gate (no microservice_dispatcher).

### 5.3 Evidence type mismatch

- **Scenario ID:** `evidence_type_mismatch`
- **Expected:**
  - `final_status`: `NEEDS_EVIDENCE`
  - `must_not_dispatch`: `true`
- **Verdict esperado:** `BLOCKED_EXPECTED`
- **Blocked at:** `evidence_gate`.
- **Stages presentes:** solo intake, evidence, evidence_gate (no microservice_dispatcher).

### 5.4 Unsupported runtime classification

- **Scenario ID:** `unsupported_runtime_classification`
- **Expected:**
  - `final_status`: `BLOCKED`
  - `runtime_classification`: `supplier_duplicate_check`
  - `dispatch_status`: `UNSUPPORTED`
- **Verdict esperado:** `BLOCKED_EXPECTED` o `FAIL` (depende de cómo se maneje).
- **Blocked at:** `readiness` o `runtime_bridge` (o llega a dispatcher con `UNSUPPORTED`).
- **Stages presentes:** depende de si llega a dispatcher o no.

---

## 6. Aserciones mínimas que debería tener Codex después

### 6.1 Aserciones de trace

```python
# Overall status
assert result.trace.overall_status in {"PASS", "BLOCKED_EXPECTED", "FAIL"}

# Blocked at
if result.trace.overall_status == "BLOCKED_EXPECTED":
    assert result.trace.blocked_at is not None
    assert result.trace.blocked_at in {"evidence_gate", "readiness", "runtime_bridge"}

# Final summary
assert "final_status" in result.trace.final_summary
assert "runtime_classification" in result.trace.final_summary
assert "dispatch_status" in result.trace.final_summary
assert "findings_count" in result.trace.final_summary
assert "must_not_dispatch" in result.trace.final_summary
```

### 6.2 Aserciones de escenario happy path

```python
assert result.trace.overall_status == "PASS"
assert result.trace.final_summary["final_status"] == "READY_TO_DELIVER"
assert result.trace.final_summary["runtime_classification"] == "excel_diagnostic"
assert result.trace.final_summary["dispatch_status"] == "EXECUTED"
assert result.trace.final_summary["findings_count"] >= 1
assert result.trace.final_summary["must_not_dispatch"] is False

assert result.execution_gate_verdict is not None
assert result.execution_gate_verdict["verdict"] == "PASS"
assert result.delivery_package is not None
assert result.delivery_package["status"] == "READY_TO_DELIVER"
```

### 6.3 Aserciones de escenarios negativos

```python
# Missing evidence / evidence type mismatch
assert result.trace.overall_status == "BLOCKED_EXPECTED"
assert result.trace.blocked_at in {"evidence_gate", "readiness"}
assert result.trace.final_summary["must_not_dispatch"] is True
assert result.execution_result is None
assert result.execution_gate_verdict is None
assert result.delivery_package is None

# Stage presence/absence
stage_names = [stage.name for stage in result.trace.stages]
assert "microservice_dispatcher" not in stage_names
assert "execution_result_gate" not in stage_names
assert "delivery_package" not in stage_names
```

### 6.4 Aserciones de reporte (si se implementa)

```python
# report.md
assert "Summary" in report_md
assert "Scenario Context" in report_md
assert "Expected vs Actual" in report_md
assert "Stage-by-Stage Execution" in report_md
assert scenario.scenario_id in report_md
assert result.trace.overall_status in report_md

# trace.json
assert trace_json["trace_id"] == result.trace.trace_id
assert trace_json["scenario_id"] == scenario.scenario_id
assert trace_json["trace"]["overall_status"] == result.trace.overall_status
assert len(trace_json["trace"]["stages"]) == len(result.trace.stages)
```

---

## 7. Riesgos

1. **Falta de timestamps:** sin duración por etapa, el reporte no puede mostrar cuellos de botella.
2. **Error truncado:** si una etapa lanza excepción, el `error: str` actual puede no capturar el stack trace completo.
3. **Escenarios incompletos:** si no se cubren los 4 escenarios (happy, missing, mismatch, unsupported), el reporte no prueba todos los modos de fallo.
4. **Aserciones débiles:** si Codex solo afirma `overall_status`, puede pasar un escenario que falla en `final_summary` pero tiene `overall_status` correcto por bug.

---

## 8. Veredicto

**READY_FOR_GEMINI_REVIEW**

El formato de reporte developer está claro y es viable. La estructura de `PipelineTrace` ya captura la información esencial. Los formatos propuestos (report.md y trace.json) son complementarios: uno legible por humanos, otro machine-readable. Los 4 escenarios actuales cubren los modos de fallo más críticos. Las aserciones mínimas propuestas son suficientes para validar el pipeline sin ser excesivas.

Codex puede proceder a implementar:
1. Generador de `report.md` a partir de `PipelineRunResult`.
2. Generador de `trace.json` a partir de `PipelineRunResult`.
3. Aserciones adicionales en los tests e2e para validar el contenido del reporte.

No se requiere refactor de contratos ni cambios en el runner.
