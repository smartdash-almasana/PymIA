# M19.8 — Pipeline Radiography CI Audit

Fecha: 2026-06-03
Rol: auditor de lectura pesada. No se implementó código.

## 1. Estado actual de workflows

No existe directorio `.github/workflows/` en el repo.
No hay CI configurado actualmente para PymIA.

## 2. Versión de Python recomendada para CI

`pyproject.toml` declara `requires-python = ">=3.11"`.
Dependencias: `pydantic>=2.0`, `openpyxl>=3.1`, `pandas>=2.2`, `mcp>=1.0`.

Recomendación:
- Usar **Python 3.11** o **3.12** en CI.
- No usar 3.14 (no es estable y puede romper dependencias como `pandas` o `pydantic`).
- Fijar versión en el workflow: `python-version: "3.11"`.

## 3. Comandos mínimos que debe correr M19.8

```bash
# Instalación de dependencias
pip install -e .[dev]

# Ejecución de Pipeline Radiography
python -m pymia.pipeline_radiography.run_scenarios --output-dir .pipeline_radiography/ci

# Ejecución de tests focales SmartPyme
pytest tests/smartpyme/
```

## 4. Qué conviene correr en CI

### 4.1 Pipeline Radiography command
**SÍ**. Es el corazón de M19.8.
Debe ejecutarse con `--output-dir .pipeline_radiography/ci` y retornar exit code 0.
Si retorna 1 (algún escenario FAIL o AMBIGUOUS), el job de CI debe fallar.

### 4.2 Tests focales radiography
**SÍ**. Son rápidos y críticos:
- `tests/smartpyme/e2e/test_pipeline_radiography_excel.py` (5 tests)
- `tests/smartpyme/test_pipeline_radiography_run_scenarios.py` (2 tests)

### 4.3 test_capability_registry
**SÍ**. Valida que el registry machine-readable (M20) carga correctamente y que `excel_diagnostic` y `supplier_duplicate_check` están certificados.
- `tests/smartpyme/test_capability_registry.py` (5 tests)

### 4.4 test_one_microservice_smoke
**SÍ**. Valida que el dispatcher ejecuta correctamente ambos plugins.
- `tests/smartpyme/test_one_microservice_smoke.py` (14 tests)

### 4.5 tests/smartpyme completo
**SÍ, RECOMENDADO**. La suite completa tiene ~602 tests, no depende de servicios externos, no requiere VM, no usa Telegram/PDF/HTML/UI, y corre en segundos.
Ejecutar `pytest tests/smartpyme/` garantiza que no hay regresiones en contratos, readiness, evidence_gate, etc.

## 5. Artefactos que conviene subir

### 5.1 Artefactos de Pipeline Radiography
- `.pipeline_radiography/ci/summary.json` (resumen global con conteos de PASS/BLOCKED/FAIL/AMBIGUOUS)
- `.pipeline_radiography/ci/index.md` (tabla de escenarios con status y duración)
- `.pipeline_radiography/ci/*/report.md` (reporte developer por escenario)
- `.pipeline_radiography/ci/*/trace.json` (traza completa por escenario)

### 5.2 Artefactos de pytest (opcional)
- Reporte de cobertura o resultados de pytest si se configura `--junitxml`.

Recomendación: subir `.pipeline_radiography/ci/` como artifact con retención de 7 días.

## 6. Paths que deberían disparar el workflow

```yaml
on:
  push:
    paths:
      - 'pymia/**'
      - 'tests/smartpyme/**'
      - 'pyproject.toml'
      - '.github/workflows/smartpyme-radiography.yml'
  pull_request:
    paths:
      - 'pymia/**'
      - 'tests/smartpyme/**'
      - 'pyproject.toml'
```

No disparar en cambios de `docs/`, `landing/`, `conversa-engine/`, `Pymia-memoria/`, etc.

## 7. Riesgos identificados

### 7.1 Fixtures Excel
`scenarios_registry.py` resuelve rutas de fixtures con:
```python
Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "smartpyme" / "ventas_costos_margen.xlsx"
```
Esto funciona correctamente en CI siempre que la estructura del repo se preserve (que es el caso estándar de `actions/checkout`).
**Riesgo bajo**.

### 7.2 Dependencias
Todas las dependencias están en `pyproject.toml` y son paquetes estándar de PyPI.
**Riesgo bajo**.

### 7.3 Python 3.14
Si se usa `python-version: "3.x"` sin fijar, GitHub Actions podría usar 3.14 cuando esté disponible, lo cual podría romper `pandas` o `pydantic`.
**Mitigación**: Fijar `python-version: "3.11"` en el workflow.

### 7.4 Exit code de run_scenarios
El comando retorna 1 si algún escenario queda en FAIL o AMBIGUOUS.
En CI, esto debe traducirse en un job fallido.
**Riesgo bajo**, el comportamiento es el esperado.

### 7.5 Duración de tests
La suite `tests/smartpyme/` tiene ~602 tests. En un runner gratuito de GitHub Actions, esto debería tomar menos de 2 minutos.
**Riesgo bajo**.

## 8. Workflow YAML recomendado

Archivo: `.github/workflows/smartpyme-radiography.yml`

```yaml
name: SmartPyme Pipeline Radiography CI

on:
  push:
    paths:
      - 'pymia/**'
      - 'tests/smartpyme/**'
      - 'pyproject.toml'
      - '.github/workflows/smartpyme-radiography.yml'
  pull_request:
    paths:
      - 'pymia/**'
      - 'tests/smartpyme/**'
      - 'pyproject.toml'

jobs:
  radiography-and-tests:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
      
      - name: Set up Python 3.11
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e .[dev]
      
      - name: Run Pipeline Radiography
        run: |
          python -m pymia.pipeline_radiography.run_scenarios --output-dir .pipeline_radiography/ci
      
      - name: Run SmartPyme tests
        run: |
          pytest tests/smartpyme/ --junitxml=test-results.xml
      
      - name: Upload Radiography artifacts
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: pipeline-radiography-ci
          path: .pipeline_radiography/ci/
          retention-days: 7
      
      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: pytest-results
          path: test-results.xml
          retention-days: 7
```

## 9. Validaciones locales que debe correr Codex antes de commit

Antes de hacer push, Codex debe ejecutar localmente:

```bash
# 1. Radiografía completa
python -m pymia.pipeline_radiography.run_scenarios

# 2. Suite completa SmartPyme
pytest tests/smartpyme/

# 3. Verificar que no hay cambios en archivos prohibidos
# (Telegram, PDF, HTML, UI, e2e_cli, etc.)
```

Si ambos comandos retornan exit code 0, el push es seguro.

## 10. Archivos que tocaría Codex

### 10.1 Archivos nuevos
- `.github/workflows/smartpyme-radiography.yml` (workflow de CI)

### 10.2 Archivos a actualizar
- `docs/smartpyme/M19_8_PIPELINE_RADIOGRAPHY_CI_CHECKPOINT.md` (nuevo checkpoint)

### 10.3 Archivos que NO debe tocar
- Código de `pymia/` (ya está listo para CI).
- Tests de `tests/smartpyme/` (ya están pasando).
- `pyproject.toml` (dependencias correctas).
- Cualquier archivo de Telegram, PDF, HTML, UI, conversa-engine.

## 11. Qué no mezcla este CI

- No corre `e2e_cli.py`.
- No corre tests de Telegram.
- No corre tests de PDF/HTML.
- No corre tests de UI.
- No corre tests de conversa-engine.
- No requiere VM.
- No requiere secretos.
- No requiere Gemini/Vertex.
- No requiere servicios externos.

## 12. Veredicto

**READY_FOR_GEMINI_REVIEW**

### Causa
- No existen workflows previos, por lo tanto no hay conflictos.
- `pyproject.toml` tiene todas las dependencias necesarias.
- `run_scenarios.py` está listo para ejecutarse en CI con exit code operativo.
- La suite `tests/smartpyme/` es autocontenida, rápida y no requiere servicios externos.
- El workflow YAML propuesto es simple, gratuito y cumple con todos los requisitos de M19.8.
- Los artefactos generados (summary.json, index.md, report.md, trace.json) son suficientes para auditar el estado del pipeline en cada push/PR.

### Próximos pasos para Codex
1. Crear `.github/workflows/smartpyme-radiography.yml` con el contenido propuesto.
2. Hacer commit y push.
3. Verificar en GitHub Actions que el workflow corre y pasa.
4. Crear `docs/smartpyme/M19_8_PIPELINE_RADIOGRAPHY_CI_CHECKPOINT.md` documentando el cierre de M19.8.

## Frase rectora

Una radiografía útil debe poder correrse automáticamente en cada push sin intervención humana.
