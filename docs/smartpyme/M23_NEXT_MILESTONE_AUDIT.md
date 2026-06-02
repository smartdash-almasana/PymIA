# M23 — Auditoría para próximo hito después de M22

## Estado

AUDIT_COMPLETE

## Fecha

2026-06-03

## Contexto

Hitos cerrados y pusheados:

```text
M21 — Minimal Operational Harness v0 (commit 866fbed)
M22A — Checkpoint documental M21 (commit a694742)
M22 — Registry Hardening (commit 425d9f3)
M22B — Checkpoint documental M22
```

---

# 1. VEREDICTO

```text
M23_CI_INTEGRATION
```

Integrar el Operational Harness al flujo de CI de Pipeline Radiography.

---

# 2. EVIDENCIA DOCUMENTAL

## 2.1 Pymia-memoria/_estado_actual.md

**Afirmaciones verificadas:**

- Protocolo operativo vigente: Coder descubre → Reviewer presiona → ChatGPT ordena → Codex implementa → Pytest certifica → CI vigila.
- M19-M22 cerrados.
- M21 v0 implementado como lector determinístico mínimo.
- `build_operational_status()` y `load_radiography_bundle()` son las únicas funciones expuestas.
- Tests: 618 passed en suite completa.
- GitHub Actions verde.

**NO se puede afirmar:**

- Que el harness se ejecute en CI. No hay evidencia de eso en el estado actual.
- Que exista un CLI para el harness.

## 2.2 Pymia-memoria/_task_actual.md

**Afirmaciones verificadas:**

- M22 CLOSED_PUSHED.
- `stale_certified_capabilities` detectado correctamente.
- Prioridad de `next_action`: FAIL > AMBIGUOUS > orphan/stale > PARTIAL.
- Advertencia explícita: "No tratar report_html como capacidad candidata real".

**NO se puede afirmar:**

- Que el output del harness esté siendo consumido por algún flujo automatizado.

## 2.3 Pymia-memoria/_decisiones_vigentes.md

**Decisiones vigentes relevantes:**

1. M21 v0 no debe expandirse retroactivamente sin nuevo hito.
2. No se implementó CLI en M21 v0.
3. No se integró M21 al CI en M21 v0.
4. El arnés consume artefactos de Pipeline Radiography, no ejecuta Pipeline Radiography.
5. IA residente v0 sólo después de arnés + registry + radiography + CI suficientemente estables.

**NO se puede afirmar:**

- Que se haya decidido el orden entre M23_CI_INTEGRATION y M23_NEXT_CAPABILITY.

## 2.4 Pymia-memoria/_no_volver_a_hacer.md

**Prohibiciones vigentes:**

- No ampliar scope cuando el hito pide mínimo.
- No convertir M21 en IA residente.
- No declarar PIPELINE_CERTIFIED sin registry + dispatcher + radiography + tests.
- No tocar dispatcher/plugins durante M21.
- No editar Pymia-memoria como parte de commits.

## 2.5 docs/smartpyme/M21_OPERATIONAL_HARNESS_CHECKPOINT.md

**Afirmaciones verificadas:**

- M21 v0 CLOSED_PUSHED.
- API: `load_radiography_bundle()`, `build_operational_status()`.
- Output: `harness_version`, `pipeline_status`, `next_action`, `counts`, listas de escenarios y capacidades.
- Reglas de semaforización: RED/YELLOW/GREEN.
- Validación de imports prohibidos: limpia.

**NO se puede afirmar:**

- Que el harness se ejecute fuera de los tests unitarios.

## 2.6 docs/smartpyme/M22_REGISTRY_HARDENING_CHECKPOINT.md

**Afirmaciones verificadas:**

- M22 CLOSED_PUSHED.
- Detección de `stale_certified_capabilities` implementada.
- Tests agregados: 5 nuevos, total 16 en test_operational_harness.py.
- Validación: 618 passed en suite completa.

**NO se puede afirmar:**

- Que el output del harness se publique como artefacto en CI.

## 2.7 pymia/operational_harness/harness.py

**Afirmaciones verificadas:**

- `load_radiography_bundle()` lee `summary.json` + `trace.json` por escenario.
- `build_operational_status()` consume `capability_registry.load_registry()` (no parsea YAML directo).
- Detección de stale certified capabilities implementada.
- Prioridad de `next_action`: FIX_SCENARIO > FIX_SCENARIOS > RE_RUN_RADIOGRAPHY > REVIEW_REGISTRY > REVIEW_PARTIAL_CAPABILITY > NONE.
- No hay imports prohibidos (requests, httpx, urllib, langchain, openai, google, telegram, pdf, html, dashboard, microservice_dispatcher, diagnose_excel, diagnose_supplier).

**NO se puede afirmar:**

- Que alguien llame `build_operational_status()` fuera de tests.

## 2.8 pymia/smartpyme/capabilities.yaml

**Afirmaciones verificadas:**

- 4 capacidades registradas.
- 2 PIPELINE_CERTIFIED: `excel_diagnostic`, `supplier_duplicate_check`.
- 2 NOT_FOUND: `report_html`, `document_parser_front`.
- 0 PARTIAL.
- Ambas certificadas tienen `dispatcher_classification` que matchea con traces de escenarios.

**NO se puede afirmar:**

- Que existan capacidades candidatas reales más allá de las 4 registradas.

## 2.9 pymia/smartpyme/capability_registry.py

**Afirmaciones verificadas:**

- `load_registry()` valida schema completo.
- 7 estados permitidos: PIPELINE_CERTIFIED, AVAILABLE, PARTIALLY_AVAILABLE_BY_PATH, UNSUPPORTED_IN_DISPATCHER, DOCUMENTED_NOT_IMPLEMENTED, NOT_FOUND, CONCEPTUAL.
- Funciones públicas: `list_capabilities()`, `get_capability()`, `is_pipeline_certified()`, `is_dispatcher_available()`.

**NO se puede afirmar:**

- Que el registry necesite endurecimiento adicional.

## 2.10 pymia/pipeline_radiography/run_scenarios.py

**Afirmaciones verificadas:**

- CLI: `python -m pymia.pipeline_radiography.run_scenarios --output-dir <dir>`.
- Genera `summary.json` + `index.md` + reportes por escenario.
- Exit code 1 si hay FAIL o AMBIGUOUS.
- No consume el harness.

**NO se puede afirmar:**

- Que `run_scenarios.py` necesite integrarse con el harness.

## 2.11 pymia/pipeline_radiography/scenarios_registry.py

**Afirmaciones verificadas:**

- 5 escenarios registrados:
  - `margin_excel_happy_path` → `excel_diagnostic`
  - `margin_excel_missing_evidence` → BLOCKED_EXPECTED
  - `evidence_type_mismatch` → BLOCKED_EXPECTED
  - `unsupported_runtime_classification` → BLOCKED_EXPECTED
  - `supplier_duplicate_check_happy_path` → `supplier_duplicate_check`

**NO se puede afirmar:**

- Que necesiten escenarios adicionales de radiografía.

## 2.12 .github/workflows/smartpyme-radiography.yml

**Afirmaciones verificadas:**

- Corre `python -m pymia.pipeline_radiography.run_scenarios --output-dir .pipeline_radiography/ci`.
- Corre `python -m pytest tests/smartpyme -q`.
- Sube artefactos de `.pipeline_radiography/ci`.
- No ejecuta el harness.
- No publica output del harness como artefacto.

**NO se puede afirmar:**

- Que el CI necesite ejecutar el harness para ser funcional.

## 2.13 tests/smartpyme/test_operational_harness.py

**Afirmaciones verificadas:**

- 16 tests pasantes.
- Cobertura: GREEN, YELLOW, RED, stale, orphan, partial, deterministic, forbidden imports.

**NO se puede afirmar:**

- Que el harness se ejecute en producción/CI.

---

# 3. MAPA DE RIESGOS

## 3.1 Riesgos si integramos harness al CI ahora

| Riesgo | Severidad | Mitigación |
|--------|-----------|------------|
| Aumentar tiempo de CI | Baja | El harness lee archivos JSON locales, <1 segundo. |
| Romper CI si el harness falla | Media | `build_operational_status()` tiene 16 tests. Se puede agregar un paso `if: always()` que no falle el job. |
| Duplicar artefactos | Baja | Publicar en subdirectorio `.pipeline_radiography/ci/harness/`. |
| Confundir rol del harness | Media | Documentar que el harness es lector, no ejecutor. |

## 3.2 Riesgos si vamos a nueva capacidad ahora

| Riesgo | Severidad | Mitigación |
|--------|-----------|------------|
| No hay evidencia de capacidad candidata real | Alta | `report_html` y `document_parser_front` están NOT_FOUND. No hay tercera capacidad en el registry. |
| Romper restricción "No tratar NOT_FOUND como candidata" | Alta | Documentada en `_task_actual.md`. |
| Sobre-diseño sin auditoría | Alta | Protocolo: Coder descubre antes de Codex implementa. |
| Mezclar bordes (Telegram/PDF/HTML/UI) | Alta | Restricción explícita en `_no_volver_a_hacer.md`. |

## 3.3 Riesgos si tocamos registry ahora

| Riesgo | Severidad | Mitigación |
|--------|-----------|------------|
| No hay inconsistencias reales que resolver | Alta | Ambas capacidades PIPELINE_CERTIFIED tienen traces. 0 stale. 0 orphan. |
| Romper contratos existentes | Media | `capability_registry.py` ya valida schema completo. |
| Agregar capacidades ficticias | Alta | Restricción explícita en `_task_actual.md`. |

## 3.4 Riesgos si agregamos CLI al harness

| Riesgo | Severidad | Mitigación |
|--------|-----------|------------|
| Sobre-diseño para v0 | Media | M21 v0 explícitamente no incluyó CLI. |
| Confundir con `run_scenarios.py` | Media | Dos CLIs similares causarían confusión. |
| No aporta valor si CI ya lo ejecuta | Media | CI puede llamar `build_operational_status()` directamente. |

## 3.5 Riesgos si integramos harness a `run_scenarios.py`

| Riesgo | Severidad | Mitigación |
|--------|-----------|------------|
| Acoplamiento innecesario | Alta | `run_scenarios.py` ejecuta pipeline. Harness lee resultados. Separación de responsabilidades. |
| Romper contrato de `run_scenarios.py` | Media | Actualmente retorna exit code basado en FAIL/AMBIGUOUS. No debe cambiar. |
| Duplicar lógica | Media | El harness ya existe como módulo independiente. |

---

# 4. RECOMENDACIÓN

## 4.1 Una sola tarea M23

```text
M23_CI_INTEGRATION
```

Integrar el Operational Harness al flujo de CI de Pipeline Radiography.

## 4.2 Alcance mínimo

1. Agregar un paso en `.github/workflows/smartpyme-radiography.yml` después de "Run Pipeline Radiography" y antes de "Run SmartPyme tests".
2. El paso ejecuta `build_operational_status(".pipeline_radiography/ci")` y escribe el resultado a `.pipeline_radiography/ci/harness_status.json`.
3. El paso no falla el job si el harness reporta YELLOW (solo RED podría fallar, pero eso ya lo detecta `run_scenarios.py`).
4. Subir `harness_status.json` como parte de los artefactos existentes.

## 4.3 Archivos que tocaría

```text
.github/workflows/smartpyme-radiography.yml (agregar paso)
pymia/operational_harness/__main__.py (nuevo, entry point mínimo para CI)
```

**Nota:** `__main__.py` es un entry point mínimo para que CI pueda ejecutar `python -m pymia.operational_harness --output-dir <dir>`. Esto NO es un CLI público con argparse complejo. Es un wrapper de 10 líneas que llama `build_operational_status()` y escribe JSON.

Alternativa sin `__main__.py`:

```yaml
- name: Run Operational Harness
  run: |
    python -c "
    import json
    from pymia.operational_harness.harness import build_operational_status
    status = build_operational_status('.pipeline_radiography/ci')
    with open('.pipeline_radiography/ci/harness_status.json', 'w') as f:
        json.dump(status, f, indent=2)
    "
```

## 4.4 Archivos que NO tocaría

```text
pymia/smartpyme/capabilities.yaml
pymia/smartpyme/capability_registry.py
pymia/pipeline_radiography/*
pymia/operational_harness/harness.py (no modificar)
pymia/smartpyme/microservice_dispatcher.py
pymia/smartpyme/excel_diagnostic.py
pymia/smartpyme/classifications/supplier_duplicate_check.py
tests/smartpyme/*
docs/smartpyme/* (excepto checkpoint M23)
conversa-engine/*
landing/*
Pymia-memoria/*
```

## 4.5 Tests esperados

**Tests nuevos:**

1. `test_harness_main_writes_status_json(tmp_path)`:
   - Verifica que `python -m pymia.operational_harness --output-dir <dir>` escribe `harness_status.json`.
   - Verifica que el JSON es válido y tiene `pipeline_status`, `next_action`, `counts`.

**Tests existentes a preservar:**

- 16 tests en `test_operational_harness.py`.
- 618 tests en suite completa `tests/smartpyme`.

**Validaciones esperadas:**

```bash
python -m pytest tests/smartpyme/test_operational_harness.py -q
python -m pytest tests/smartpyme -q
rg -n "requests|httpx|urllib|langchain|openai|google|telegram|pdf|html|dashboard|microservice_dispatcher|diagnose_excel|diagnose_supplier" pymia/operational_harness
```

## 4.6 Criterio de éxito

- CI corre `run_scenarios` → genera artefactos de radiografía.
- CI corre harness → genera `harness_status.json` con `pipeline_status: GREEN`.
- Artefactos de CI incluyen `harness_status.json`.
- 0 tests rotos.
- 0 imports prohibidos en `pymia/operational_harness/`.

---

# 5. RESPUESTAS A PREGUNTAS DE AUDITORÍA

## 5.1 ¿Qué inconsistencia real queda hoy entre registry, radiography y harness?

**Respuesta:** Ninguna.

- Ambas capacidades PIPELINE_CERTIFIED (`excel_diagnostic`, `supplier_duplicate_check`) tienen traces correspondientes en los 5 escenarios.
- 0 stale certified capabilities.
- 0 orphan classifications.
- 0 partial capabilities.
- El harness reporta GREEN con los escenarios actuales.

## 5.2 ¿El harness está siendo usado por algún flujo o solo existe como API?

**Respuesta:** Solo existe como API.

- `run_scenarios.py` no lo consume.
- CI no lo ejecuta.
- No hay CLI.
- Solo se consume en `tests/smartpyme/test_operational_harness.py`.

## 5.3 ¿Tiene sentido integrarlo ahora, o sería sobreingeniería?

**Respuesta:** Tiene sentido integrarlo al CI.

**Razones:**

1. El harness existe y funciona (16 tests pasantes).
2. Nadie lo consume fuera de tests.
3. CI ya genera los artefactos que el harness necesita (`.pipeline_radiography/ci/summary.json` + `trace.json`).
4. Integración es un paso de ~10 líneas en workflow YAML.
5. Aporta visibilidad del estado operacional consolidado en cada push/PR.
6. No rompe restricciones de M21 (no es CLI público, no es dashboard, no es IA).

**NO sería sobreingeniería** porque:

- No requiere refactor de contratos.
- No requiere nuevos módulos.
- No requiere tocar `run_scenarios.py`.
- No requiere tocar dispatcher/plugins.
- No requiere IA/red/UI.

## 5.4 ¿Qué evidencia hay para elegir una nueva capacidad?

**Respuesta:** Ninguna.

**Evidencia documental:**

- `capabilities.yaml` tiene 4 capacidades: 2 PIPELINE_CERTIFIED, 2 NOT_FOUND.
- `report_html` tiene `status: NOT_FOUND`, `no_promise_reason: no localizado en pymia.smartpyme al cierre de M20`.
- `document_parser_front` tiene `status: NOT_FOUND`, `no_promise_reason: no localizado en pymia.smartpyme al cierre de M20`.
- `_task_actual.md` advierte explícitamente: "No tratar report_html como capacidad candidata real".

**Conclusión:** No hay evidencia de capacidad candidata real. Proponer M23_NEXT_CAPABILITY sería inventar roadmap.

## 5.5 ¿Hay capacidades NOT_FOUND que no deben tocarse?

**Respuesta:** Sí.

- `report_html`: NOT_FOUND, sin module/function/tests.
- `document_parser_front`: NOT_FOUND, sin module/function/tests.

**Restricción vigente:** "No tratar entradas NOT_FOUND como capacidades candidatas reales sin auditoría previa" (M22 Registry Hardening Checkpoint).

## 5.6 ¿Cuál es el próximo paso más pequeño que reduce riesgo real?

**Respuesta:** Integrar el harness al CI.

**Riesgo real que reduce:**

- Hoy el harness existe pero nadie lo consume. Si en un futuro una capacidad certificada queda stale (sin traces en radiografía), el CI no lo detectará.
- Integrar el harness al CI hace observable el estado operacional consolidado en cada push/PR.
- Es un paso de ~10 líneas en workflow YAML.
- No rompe restricciones de M21.
- No requiere refactor de contratos.

---

# 6. OPCIONES DESCARTADAS

## 6.1 M23_HARNESS_INTEGRATION (integrar a run_scenarios.py)

**Razón de descarte:**

- Acoplamiento innecesario.
- `run_scenarios.py` ejecuta pipeline. Harness lee resultados. Separación de responsabilidades.
- Rompería contrato de `run_scenarios.py` (exit code basado en FAIL/AMBIGUOUS).

## 6.2 M23_CLI

**Razón de descarte:**

- Sobre-diseño para v0.
- M21 v0 explícitamente no incluyó CLI.
- CI puede llamar `build_operational_status()` directamente.
- No aporta valor si CI ya lo ejecuta.

## 6.3 M23_REGISTRY_CONTRACT

**Razón de descarte:**

- No hay inconsistencias reales que resolver.
- Ambas capacidades PIPELINE_CERTIFIED tienen traces.
- 0 stale. 0 orphan. 0 partial.
- `capability_registry.py` ya valida schema completo.

## 6.4 M23_NEXT_CAPABILITY

**Razón de descarte:**

- No hay evidencia de capacidad candidata real.
- `report_html` y `document_parser_front` están NOT_FOUND.
- Restricción explícita: "No tratar NOT_FOUND como candidata".
- Sería inventar roadmap.

## 6.5 M23_DOCS_ONLY

**Razón de descarte:**

- Insuficiente.
- Hay un artefacto funcional (harness) que nadie consume.
- Documentar sin integrar no reduce riesgo real.

## 6.6 M23_BLOCKED

**Razón de descarte:**

- No aplica.
- No hay bloqueos técnicos.
- Hay un paso claro, mínimo y testeable.

---

# 7. REGLA DE CONTINUIDAD

No iniciar M23_CI_INTEGRATION sin:

1. Revisión externa (Gemini/Nemotron/Claude).
2. Aprobación explícita.
3. Recorte de scope confirmado.

No ampliar M23 para incluir:

- CLI público.
- Dashboard.
- IA residente.
- Nueva capacidad.
- Refactor de contratos.

---

# 8. PROMPT CANDIDATO PARA REVIEWER

```text
Reviewer, audita la recomendación M23_CI_INTEGRATION.

Contexto:
- M21 cerró con harness operacional mínimo (lector puro, sin CLI, sin CI).
- M22 endureció el harness para detectar stale certified capabilities.
- El harness existe y funciona (16 tests pasantes), pero nadie lo consume fuera de tests.
- CI genera artefactos de radiografía pero no ejecuta el harness.
- No hay evidencia de próxima capacidad candidata real (report_html y document_parser_front están NOT_FOUND).

Propuesta:
- Agregar un paso en .github/workflows/smartpyme-radiography.yml que ejecute build_operational_status(".pipeline_radiography/ci") y escriba harness_status.json.
- Alcance mínimo: workflow YAML + entry point mínimo (__main__.py de 10 líneas).
- No tocar capabilities.yaml, capability_registry.py, pipeline_radiography, dispatcher, plugins.
- No agregar CLI público.
- No integrar a run_scenarios.py.

Preguntas:
1. ¿Es este el siguiente paso correcto o conviene priorizar otra cosa?
2. ¿El entry point __main__.py es aceptable o prefieres inline en workflow YAML?
3. ¿Falta algún test mínimo para cubrir este cambio?
4. ¿Hay riesgos no identificados en la auditoría?

Reglas:
- No implementar.
- No tocar código.
- Solo auditoría de lectura.
```

---

# 9. ARCHIVOS LEÍDOS EN ESTA AUDITORÍA

```text
Pymia-memoria/_estado_actual.md
Pymia-memoria/_task_actual.md
Pymia-memoria/_decisiones_vigentes.md
Pymia-memoria/_no_volver_a_hacer.md
docs/smartpyme/M21_OPERATIONAL_HARNESS_CHECKPOINT.md
docs/smartpyme/M22_REGISTRY_HARDENING_CHECKPOINT.md
pymia/operational_harness/harness.py
pymia/smartpyme/capabilities.yaml
pymia/smartpyme/capability_registry.py
pymia/pipeline_radiography/run_scenarios.py
pymia/pipeline_radiography/scenarios_registry.py
tests/smartpyme/test_operational_harness.py
.github/workflows/smartpyme-radiography.yml
```

---

# 10. VEREDICTO FINAL

```text
M23_CI_INTEGRATION
```

**Causa:**

- El harness existe y funciona, pero nadie lo consume fuera de tests.
- Integrarlo al CI es un paso mínimo (~10 líneas en workflow YAML).
- Reduce riesgo real: hace observable el estado operacional consolidado en cada push/PR.
- No rompe restricciones de M21 (no CLI, no dashboard, no IA, no red, no UI).
- No requiere refactor de contratos.
- No requiere nueva capacidad candidata (no hay evidencia de capacidad candidata real).
- No requiere endurecimiento adicional de registry (no hay inconsistencias).

**Próximo paso metodológico:**

Enviar este documento a reviewer externo (Gemini/Nemotron/Claude) para revisión y aprobación antes de implementar.
