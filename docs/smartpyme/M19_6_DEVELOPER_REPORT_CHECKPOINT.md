# M19.6 — Checkpoint Developer Reports

Fecha: 2026-06-02  
Estado: READY_COMMITTED_PUSHED  
Commit: `0441b52 feat(smartpyme): add pipeline radiography developer reports`

---

## 1. Veredicto

```text
M19.6 Pipeline Radiography Developer Reports = CERRADO
```

El Test Drive interno de SmartPyme ahora no sólo ejecuta escenarios y produce trazas, sino que también genera reportes legibles para desarrollador.

---

## 2. Qué se incorporó

```text
pymia/pipeline_radiography/report.py
```

Con:

```text
generate_developer_report(result, output_dir)
```

También se actualizaron:

```text
pymia/pipeline_radiography/__init__.py
pymia/pipeline_radiography/trace.py
pymia/pipeline_radiography/runner.py
tests/smartpyme/e2e/test_pipeline_radiography_excel.py
docs/smartpyme/M19_6_DEVELOPER_REPORT_AUDIT.md
```

---

## 3. Nuevos artefactos generados

Por cada ejecución radiográfica testeada, el sistema puede generar:

```text
report.md
trace.json
```

Bajo un directorio de salida controlado por el test o caller.

---

## 4. Qué contiene el reporte developer

```text
Summary
Scenario Context
Expected vs Actual
Stage-by-Stage Execution
Errors/Warnings
```

Objetivo:

```text
permitir lectura humana clara del estado del pipeline, sin depender sólo de asserts pytest.
```

---

## 5. Trazabilidad temporal

Se agregaron:

```text
duration_ms por stage
duration_ms total del PipelineTrace
```

Esto prepara el terreno para observar cuellos de botella sin introducir aún un sistema externo de observabilidad.

---

## 6. Escenarios cubiertos

Los cuatro escenarios actuales generan `report.md` y `trace.json`:

```text
happy path Excel
missing evidence
evidence_type_mismatch
unsupported_runtime_classification
```

---

## 7. Validaciones reportadas

```text
python -m pytest tests/smartpyme/e2e/test_pipeline_radiography_excel.py -q
→ 4 passed
```

```text
python -m pytest tests/smartpyme/test_pipeline_radiography_models.py tests/smartpyme/e2e/test_pipeline_radiography_excel.py -q
→ 7 passed
```

```text
python -m pytest tests/smartpyme -q
→ 595 passed
```

```text
rg e2e_cli / telegram / pdf / docling / html / supplier_duplicate en scope M19
→ sin matches relevantes
```

---

## 8. Qué significa este cierre

M19.6 convierte Pipeline Radiography en una herramienta más útil para desarrollo.

Antes:

```text
pytest decía si el escenario pasaba o fallaba.
```

Ahora:

```text
el sistema deja una radiografía legible del escenario, sus etapas, su resultado esperado, su resultado real y su veredicto.
```

---

## 9. Limitaciones conocidas

```text
- report.md es developer-facing, no customer-facing.
- No es dashboard.
- No es IA residente.
- No persiste historial entre corridas.
- No convierte todavía el registry en machine-readable.
```

---

## 10. Próximo frente recomendado

Después de M19.6, las opciones sanas son:

```text
M20 — capability registry machine-readable.
M17 — supplier_duplicate_check al dispatcher formal.
M19.7 — comando único local para correr radiografía y emitir artefactos.
```

Recomendación:

```text
M19.7 antes de M20/M17 si se quiere ejecutar la radiografía con un comando único.
M20 antes de M17 si se quiere gobernar capacidades desde una fuente legible por máquina.
M17 después de M20 si se quiere conectar la segunda máquina bajo registry más sólido.
```

---

## 11. Frase rectora

```text
La radiografía no sólo debe existir: debe poder leerse.
```
