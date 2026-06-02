# M19.7 — Pipeline Radiography Single Command Audit

Fecha: 2026-06-03
Estado: auditoría de lectura completada
Rol: auditor de lectura. No se implementó código.

---

## 1. Veredicto

```text
M19.7 Pipeline Radiography Single Command = READY_FOR_GEMINI_REVIEW
```

La estructura actual de Pipeline Radiography permite extraer los escenarios de los tests y ejecutarlos mediante un comando único sin refactor de contratos.

---

## 2. Escenarios existentes hoy en los tests

Archivo auditado: `tests/smartpyme/e2e/test_pipeline_radiography_excel.py`

```text
1. test_excel_pipeline_happy_path_reaches_ready_to_deliver
   - scenario_id: margin_excel_happy_path
   - expected: READY_TO_DELIVER, excel_diagnostic, EXECUTED, min_findings=1

2. test_margin_without_evidence_blocks_before_dispatch
   - scenario_id: margin_excel_missing_evidence
   - expected: NEEDS_EVIDENCE, must_not_dispatch=True

3. test_evidence_type_mismatch_blocks_at_gate
   - scenario_id: evidence_type_mismatch
   - expected: NEEDS_EVIDENCE, must_not_dispatch=True

4. test_unsupported_runtime_classification
   - scenario_id: unsupported_runtime_classification
   - expected: BLOCKED, dispatch_status=UNSUPPORTED
```

Total: 4 escenarios (1 happy path + 3 negativos).

---

## 3. Cómo construirlos sin depender de pytest

Los escenarios están hardcodeados como instancias de `PipelineScenario` dentro de las funciones de test. Para ejecutarlos sin pytest:

1. **Extraer definiciones**: Mover las instancias de `PipelineScenario` a un módulo de registro (ej. `scenarios_registry.py`).
2. **Reemplazar `tmp_path`**: Usar un directorio real (ej. `./radiography_output/`) como `output_root`.
3. **Resolver `FIXTURE_PATH`**: Calcular la ruta absoluta al fixture Excel desde el directorio de trabajo actual o desde `__file__`.
4. **Iterar y ejecutar**: Loop sobre los escenarios, llamando a `run_pipeline_scenario()` y `generate_developer_report()`.
5. **Evaluar resultados**: Verificar `overall_status` de cada escenario para determinar el exit code.

---

## 4. Qué comando conviene

### Opciones evaluadas:

| Opción | Comando | Pros | Contras |
|---|---|---|---|
| A | `python -m pymia.pipeline_radiography.run_scenarios` | Pythonic, estándar, sin scripts externos | Requiere agregar `run_scenarios.py` |
| B | `scripts/smartpyme_pipeline_radiography.py` | Explícito, visible | Script adicional fuera del paquete |
| C | `make smartpyme-radiography` | Integrado con Makefile | Requiere Makefile, dependencia externa |

### Recomendación: **Opción A**

```bash
python -m pymia.pipeline_radiography.run_scenarios
```

Razones:
- Es el patrón estándar para módulos ejecutables en Python.
- No requiere scripts externos ni Makefile.
- Permite pasar argumentos CLI fácilmente (ej. `--output-dir`, `--scenario-id`).
- Mantiene la lógica dentro del paquete `pymia.pipeline_radiography`.

---

## 5. Qué outputs debería escribir

### Por escenario:

```text
radiography_output/
├── {trace_id_1}/
│   ├── report.md
│   └── trace.json
├── {trace_id_2}/
│   ├── report.md
│   └── trace.json
...
```

### Global:

```text
radiography_output/
├── summary.json  # Lista de escenarios con overall_status
└── index.md      # Resumen legible de todos los escenarios
```

### Contenido de `summary.json`:

```json
{
  "timestamp": "2026-06-03T12:00:00Z",
  "total_scenarios": 4,
  "passed": 3,
  "blocked_expected": 1,
  "failed": 0,
  "ambiguous": 0,
  "scenarios": [
    {
      "scenario_id": "margin_excel_happy_path",
      "trace_id": "trace_abc123",
      "overall_status": "PASS",
      "blocked_at": null,
      "duration_ms": 150
    }
  ]
}
```

---

## 6. Qué status code debería devolver

```text
Exit Code 0:
  - Todos los escenarios tienen overall_status en {PASS, BLOCKED_EXPECTED}
  - Es decir, todos los resultados coinciden con lo esperado

Exit Code 1:
  - Al menos un escenario tiene overall_status en {FAIL, AMBIGUOUS}
  - Es decir, hay resultados inesperados
```

Lógica de evaluación:

```python
exit_code = 0
for result in results:
    if result.trace.overall_status in {"FAIL", "AMBIGUOUS"}:
        exit_code = 1
        break
sys.exit(exit_code)
```

---

## 7. Qué archivos tocaría Codex

### Nuevos:

```text
pymia/pipeline_radiography/run_scenarios.py
  - Entry point del comando único
  - CLI mínimo (argparse o sys.argv)
  - Itera sobre escenarios, ejecuta, genera reportes
  - Calcula exit code

pymia/pipeline_radiography/scenarios_registry.py
  - Registro de escenarios (extraídos de test_pipeline_radiography_excel.py)
  - Función `get_all_scenarios() -> list[PipelineScenario]`
  - Función `get_scenario_by_id(scenario_id: str) -> PipelineScenario`
```

### Modificados:

```text
tests/smartpyme/e2e/test_pipeline_radiography_excel.py
  - Refactor para importar escenarios desde scenarios_registry.py
  - Evitar duplicación de definiciones
  - Mantener asserts de pytest

pymia/pipeline_radiography/__init__.py
  - Exportar run_scenarios si es necesario (opcional)
```

### Opcionales:

```text
docs/smartpyme/M19_7_SINGLE_COMMAND_CHECKPOINT.md
  - Checkpoint de cierre de M19.7
```

---

## 8. Qué tests mínimos habría que agregar

### 8.1 Test de exit code 0 (todos pasan)

```python
def test_run_scenarios_exits_with_zero_when_all_pass():
    # Ejecutar run_scenarios con escenarios que pasan
    # Verificar sys.exit(0)
```

### 8.2 Test de exit code 1 (al menos uno falla)

```python
def test_run_scenarios_exits_with_one_when_any_fails():
    # Forzar un escenario a FAIL (ej. corromper expectation)
    # Ejecutar run_scenarios
    # Verificar sys.exit(1)
```

### 8.3 Test de generación de artefactos

```python
def test_run_scenarios_generates_report_and_trace_for_each_scenario():
    # Ejecutar run_scenarios
    # Verificar que report.md y trace.json existen para cada escenario
    # Verificar que summary.json existe
```

### 8.4 Test de CLI arguments

```python
def test_run_scenarios_accepts_output_dir_argument():
    # Ejecutar con --output-dir custom
    # Verificar que los archivos se generan en ese directorio
```

---

## 9. Riesgos

### 9.1 Duplicación de escenarios

**Riesgo**: Si los escenarios se definen en `scenarios_registry.py` y los tests los importan, pero alguien modifica los tests sin actualizar el registry, habrá inconsistencia.

**Mitigación**: Los tests deben importar los escenarios del registry, no definirlos localmente.

### 9.2 Rutas de fixtures

**Riesgo**: Al ejecutar fuera de pytest, la ruta al fixture Excel (`tests/fixtures/smartpyme/ventas_costos_margen.xlsx`) puede no resolverse correctamente.

**Mitigación**: Calcular la ruta absoluta desde `__file__` o desde el directorio de trabajo actual.

### 9.3 Escenarios con dependencias externas

**Riesgo**: Si algún escenario requiere archivos que no existen en el sistema de archivos (ej. `source_ref` pointing to a non-existent file), el pipeline fallará.

**Mitigación**: Validar que todos los `source_ref` existen antes de ejecutar el pipeline.

### 9.4 Exit code ambiguo

**Riesgo**: Si un escenario tiene `overall_status == "AMBIGUOUS"`, no está claro si debe contar como FAIL o como PASS.

**Mitigación**: Tratar `AMBIGUOUS` como FAIL (exit code 1), ya que indica incertidumbre.

---

## 10. Matriz de escenarios recomendados para el comando único

| ID | Scenario | Expected Status | Priority |
|---|---|---|---|
| 1 | margin_excel_happy_path | PASS | Alta |
| 2 | margin_excel_missing_evidence | BLOCKED_EXPECTED | Alta |
| 3 | evidence_type_mismatch | BLOCKED_EXPECTED | Alta |
| 4 | unsupported_runtime_classification | BLOCKED_EXPECTED | Alta |

Todos los escenarios actuales son viables para el comando único. No se requieren escenarios adicionales para M19.7.

---

## 11. Frase rectora

```text
Un comando, cuatro escenarios, cero ambigüedad.
```

---

## 12. Próximos pasos

1. Codex implementa `scenarios_registry.py` y `run_scenarios.py`.
2. Codex refactoriza `test_pipeline_radiography_excel.py` para importar escenarios del registry.
3. Codex ejecuta `python -m pymia.pipeline_radiography.run_scenarios` y verifica exit code 0.
4. Codex genera `summary.json` y `index.md` en `radiography_output/`.
5. Gemini revisa el diff y emite veredicto final.

---

Fin del documento.
