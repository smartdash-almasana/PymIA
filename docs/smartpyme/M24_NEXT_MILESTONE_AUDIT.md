# M24 — Auditoría para próximo hito después de M23 CI Integration

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
M23 — CI Integration (commit e87d8be)
M23 Audit — Auditoría operacional harness CI integration (commit af52536)
```

---

# 1. VEREDICTO

```text
M24_CHECKPOINT_CI_HARNESS
```

Crear checkpoint documental formal de M23 CI Integration para cerrar el hito con trazabilidad completa.

---

# 2. EVIDENCIA DOCUMENTAL

## 2.1 Pymia-memoria/_estado_actual.md

**Afirmaciones verificadas:**

- Protocolo operativo vigente: Coder → Reviewer → ChatGPT → Codex → Pytest → CI.
- M19-M22 cerrados.
- M21 v0 implementado como lector determinístico mínimo.
- M22 Registry Hardening: detección de stale certified capabilities.
- GitHub Actions verde.
- 618 tests en suite completa.

**NO se puede afirmar:**

- Que M23 esté cerrado documentalmente.
- Que exista checkpoint M23 en docs/smartpyme/.

## 2.2 Pymia-memoria/_task_actual.md

**Afirmaciones verificadas:**

- M22 CLOSED_PUSHED.
- `stale_certified_capabilities` detectado correctamente.
- Prioridad de `next_action`: FAIL > AMBIGUOUS > orphan/stale > PARTIAL.
- Advertencia explícita: "No tratar report_html como capacidad candidata real".

**NO se puede afirmar:**

- Que M23 esté marcado como CLOSED_PUSHED en task_actual.

## 2.3 Pymia-memoria/_decisiones_vigentes.md

**Decisiones vigentes relevantes:**

1. M21 v0 no debe expandirse retroactivamente sin nuevo hito.
2. No se implementó CLI en M21 v0.
3. No se integró M21 al CI en M21 v0.
4. IA residente v0 sólo después de arnés + registry + radiography + CI suficientemente estables.

**NOTA:** Este archivo no menciona M22 ni M23. Requiere actualización.

## 2.4 docs/smartpyme/M21_OPERATIONAL_HARNESS_CHECKPOINT.md

**Afirmaciones verificadas:**

- M21 v0 CLOSED_PUSHED.
- API: `load_radiography_bundle()`, `build_operational_status()`.
- Output: `harness_version`, `pipeline_status`, `next_action`, `counts`, listas de escenarios y capacidades.
- Reglas de semaforización: RED/YELLOW/GREEN.
- Validación de imports prohibidos: limpia.
- 11 tests pasantes en M21.

## 2.5 docs/smartpyme/M22_REGISTRY_HARDENING_CHECKPOINT.md

**Afirmaciones verificadas:**

- M22 CLOSED_PUSHED.
- Detección de `stale_certified_capabilities` implementada.
- Tests agregados: 5 nuevos, total 16 en test_operational_harness.py.
- Validación: 618 passed en suite completa.
- Regla de continuidad: "No tratar entradas NOT_FOUND del registry como capacidades candidatas reales".

## 2.6 docs/smartpyme/M23_NEXT_MILESTONE_AUDIT.md

**Afirmaciones verificadas:**

- Auditoría completa recomendando M23_CI_INTEGRATION.
- Análisis de riesgos detallado.
- Opciones descartadas con justificación.
- Recomendación: integrar harness al CI con paso mínimo en workflow YAML.

**NO se puede afirmar:**

- Que M23 CI Integration haya sido implementado (esto se verifica en workflow YAML).

## 2.7 .github/workflows/smartpyme-radiography.yml

**Afirmaciones verificadas:**

- **M23 CI Integration IMPLEMENTADO:**
  - Paso "Build Operational Harness Status" ejecuta `python -m pymia.operational_harness --output-dir .pipeline_radiography/ci`.
  - Paso "Upload Operational Harness Status" sube `.pipeline_radiography/ci/harness_status.json` como artefacto `operational-harness-status`.
  - Workflow ejecuta: checkout → Python 3.11 → install deps → run_scenarios → harness → pytest → upload artifacts.

**Conclusión:** M23 CI Integration está implementado y funcional.

## 2.8 pymia/operational_harness/__main__.py

**Afirmaciones verificadas:**

- Entry point mínimo con argparse.
- Lee `--output-dir` como argumento requerido.
- Llama `build_operational_status(output_dir)`.
- Escribe `harness_status.json` en el directorio de salida.
- Retorna exit code 0.

**Conclusión:** Entry point funcional para CI.

## 2.9 pymia/operational_harness/harness.py

**Afirmaciones verificadas:**

- `load_radiography_bundle()` lee `summary.json` + `trace.json` por escenario.
- `build_operational_status()` consume `capability_registry.load_registry()`.
- Detección de stale certified capabilities implementada.
- Prioridad de `next_action`: FIX_SCENARIO > FIX_SCENARIOS > RE_RUN_RADIOGRAPHY > REVIEW_REGISTRY > REVIEW_PARTIAL_CAPABILITY > NONE.
- No hay imports prohibidos.

**Conclusión:** Harness completo y funcional.

## 2.10 tests/smartpyme/test_operational_harness.py

**Afirmaciones verificadas:**

- 17 tests pasantes (incluyendo `test_harness_main_writes_status_json`).
- Cobertura: GREEN, YELLOW, RED, stale, orphan, partial, deterministic, forbidden imports, __main__.py.
- Tests usan monkeypatch para mockear `load_registry()`.

**Conclusión:** Suite de tests completa.

## 2.11 pymia/smartpyme/capabilities.yaml

**Afirmaciones verificadas:**

- 4 capacidades registradas.
- 2 PIPELINE_CERTIFIED: `excel_diagnostic`, `supplier_duplicate_check`.
- 2 NOT_FOUND: `report_html`, `document_parser_front`.
- 0 PARTIAL.
- Ambas certificadas tienen `dispatcher_classification` que matchea con traces de escenarios.

**NO se puede afirmar:**

- Que existan capacidades candidatas reales más allá de las 4 registradas.

## 2.12 pymia/smartpyme/capability_registry.py

**Afirmaciones verificadas:**

- `load_registry()` valida schema completo.
- 7 estados permitidos: PIPELINE_CERTIFIED, AVAILABLE, PARTIALLY_AVAILABLE_BY_PATH, UNSUPPORTED_IN_DISPATCHER, DOCUMENTED_NOT_IMPLEMENTED, NOT_FOUND, CONCEPTUAL.
- Funciones públicas: `list_capabilities()`, `get_capability()`, `is_pipeline_certified()`, `is_dispatcher_available()`.

**Conclusión:** Registry completo y validado.

## 2.13 pymia/pipeline_radiography/scenarios_registry.py

**Afirmaciones verificadas:**

- 5 escenarios registrados:
  - `margin_excel_happy_path` → `excel_diagnostic` (PASS)
  - `margin_excel_missing_evidence` → BLOCKED_EXPECTED
  - `evidence_type_mismatch` → BLOCKED_EXPECTED
  - `unsupported_runtime_classification` → BLOCKED_EXPECTED
  - `supplier_duplicate_check_happy_path` → `supplier_duplicate_check` (PASS)

**Conclusión:** Escenarios completos cubriendo ambas capacidades certificadas.

## 2.14 pymia/pipeline_radiography/run_scenarios.py

**Afirmaciones verificadas:**

- CLI: `python -m pymia.pipeline_radiography.run_scenarios --output-dir <dir>`.
- Genera `summary.json` + `index.md` + reportes por escenario.
- Exit code 1 si hay FAIL o AMBIGUOUS.
- No consume el harness.

**Conclusión:** Runner de radiografía funcional.

---

# 3. MAPA DE RIESGOS

## 3.1 Riesgos si creamos checkpoint M23 ahora

| Riesgo | Severidad | Mitigación |
|--------|-----------|------------|
| Duplicar documentación | Baja | Checkpoint es resumen ejecutivo, no replica auditoría. |
| Perder tiempo en docs | Baja | Checkpoint toma 10-15 minutos. |
| Confundir estado del hito | Baja | Checkpoint aclara que M23 está CLOSED_PUSHED. |

**Conclusión:** Riesgo bajo. Beneficio: trazabilidad completa.

## 3.2 Riesgos si agregamos aserción CI harness ahora

| Riesgo | Severidad | Mitigación |
|--------|-----------|------------|
| Romper CI si harness reporta YELLOW | Media | Aserción solo verifica existencia de `harness_status.json`, no su contenido. |
| Sobre-ingeniería | Media | CI ya ejecuta harness y sube artefacto. Aserción adicional no aporta valor real. |
| Duplicar validaciones | Media | `run_scenarios.py` ya retorna exit code 1 si hay FAIL/AMBIGUOUS. |

**Conclusión:** No necesario. CI ya funciona correctamente.

## 3.3 Riesgos si vamos a nueva capacidad ahora

| Riesgo | Severidad | Mitigación |
|--------|-----------|------------|
| No hay evidencia de capacidad candidata real | Alta | `report_html` y `document_parser_front` están NOT_FOUND. |
| Romper restricción "No tratar NOT_FOUND como candidata" | Alta | Documentada en M22 checkpoint y `_task_actual.md`. |
| Sobre-diseño sin auditoría | Alta | Protocolo: Coder descubre antes de Codex implementa. |
| Mezclar bordes (Telegram/PDF/HTML/UI) | Alta | Restricción explícita en `_no_volver_a_hacer.md`. |

**Conclusión:** No viable. No hay capacidad candidata real.

## 3.4 Riesgos si tocamos registry ahora

| Riesgo | Severidad | Mitigación |
|--------|-----------|------------|
| No hay inconsistencias reales que resolver | Alta | Ambas capacidades PIPELINE_CERTIFIED tienen traces. 0 stale. 0 orphan. |
| Romper contratos existentes | Media | `capability_registry.py` ya valida schema completo. |
| Agregar capacidades ficticias | Alta | Restricción explícita en M22 checkpoint. |

**Conclusión:** No necesario. Registry funciona correctamente.

## 3.5 Riesgos si tocamos CI ahora

| Riesgo | Severidad | Mitigación |
|--------|-----------|------------|
| Romper workflow funcional | Alta | CI ya ejecuta run_scenarios + harness + pytest correctamente. |
| Agregar complejidad innecesaria | Media | CI ya sube artefactos de radiografía y harness. |
| Duplicar validaciones | Media | `run_scenarios.py` ya retorna exit code basado en FAIL/AMBIGUOUS. |

**Conclusión:** No necesario. CI funciona correctamente.

## 3.6 Riesgos si actualizamos memoria local ahora

| Riesgo | Severidad | Mitigación |
|--------|-----------|------------|
| Inconsistencia con repo | Baja | Memoria local debe reflejar estado real de commits. |
| Perder trazabilidad | Baja | Actualizar `_estado_actual.md`, `_task_actual.md`, `_decisiones_vigentes.md` es parte del protocolo. |

**Conclusión:** Necesario. Memoria local debe actualizarse después de M23.

---

# 4. RECOMENDACIÓN

## 4.1 Una sola tarea M24

```text
M24_CHECKPOINT_CI_HARNESS
```

Crear checkpoint documental formal de M23 CI Integration.

## 4.2 Alcance mínimo

1. Crear `docs/smartpyme/M23_CI_INTEGRATION_CHECKPOINT.md` con:
   - Estado: CLOSED_PUSHED.
   - Commit: `e87d8be`.
   - Archivos modificados: `.github/workflows/smartpyme-radiography.yml`, `pymia/operational_harness/__main__.py`.
   - Cambios implementados: paso de ejecución de harness + upload de artefacto.
   - Validaciones ejecutadas: workflow completo, 618 tests, forbidden imports limpio.
   - Límites preservados: no tocar registry, pipeline, dispatcher, plugins.
   - Resultado metodológico: CI ahora ejecuta harness y publica `harness_status.json`.

2. Actualizar `Pymia-memoria/_estado_actual.md`:
   - Agregar sección "M23 — CI Integration" con estado CLOSED_PUSHED.
   - Actualizar "Estado actual" para reflejar que M21-M23 están cerrados.

3. Actualizar `Pymia-memoria/_task_actual.md`:
   - Marcar M23 como CLOSED_PUSHED.
   - Actualizar "Próximo paso sugerido" para reflejar que M24 es checkpoint documental.

4. Actualizar `Pymia-memoria/_decisiones_vigentes.md`:
   - Agregar decisión: "M23 CI Integration quedó cerrado. CI ejecuta harness y publica harness_status.json."
   - Actualizar roadmap inmediato.

## 4.3 Archivos que tocaría

```text
docs/smartpyme/M23_CI_INTEGRATION_CHECKPOINT.md (nuevo)
Pymia-memoria/_estado_actual.md (actualizar)
Pymia-memoria/_task_actual.md (actualizar)
Pymia-memoria/_decisiones_vigentes.md (actualizar)
```

## 4.4 Archivos que NO tocaría

```text
pymia/smartpyme/capabilities.yaml
pymia/smartpyme/capability_registry.py
pymia/pipeline_radiography/*
pymia/operational_harness/*
pymia/smartpyme/microservice_dispatcher.py
pymia/smartpyme/excel_diagnostic.py
pymia/smartpyme/classifications/supplier_duplicate_check.py
tests/smartpyme/*
.github/workflows/*
conversa-engine/*
landing/*
```

## 4.5 Tests esperados

**No se requieren tests nuevos.** M24 es puramente documental.

**Validaciones esperadas:**

```bash
git status --short  # debe estar limpio después de commit
git log --oneline -5  # debe mostrar commits de M24
```

## 4.6 Criterio de éxito

- `docs/smartpyme/M23_CI_INTEGRATION_CHECKPOINT.md` existe y está completo.
- `Pymia-memoria/_estado_actual.md` menciona M23 CLOSED_PUSHED.
- `Pymia-memoria/_task_actual.md` marca M23 como CLOSED_PUSHED.
- `Pymia-memoria/_decisiones_vigentes.md` incluye decisión sobre M23.
- Commit con mensaje `docs(smartpyme): checkpoint ci integration`.
- Push a origin/main.

---

# 5. RESPUESTAS A PREGUNTAS DE AUDITORÍA

## 5.1 Después de M23, ¿qué problema real queda sin resolver?

**Respuesta:** Falta trazabilidad documental formal.

**Evidencia:**

- M23 CI Integration fue implementado (commit `e87d8be`).
- Auditoría M23 fue escrita (commit `af52536`).
- Pero no existe `docs/smartpyme/M23_CI_INTEGRATION_CHECKPOINT.md`.
- Memoria local (`Pymia-memoria/`) no menciona M23.

**Conclusión:** Problema de trazabilidad, no técnico.

## 5.2 ¿El CI ya publica harness_status.json correctamente según workflow?

**Respuesta:** Sí.

**Evidencia del workflow YAML:**

```yaml
- name: Build Operational Harness Status
  run: |
    python -m pymia.operational_harness --output-dir .pipeline_radiography/ci

- name: Upload Operational Harness Status
  if: always()
  uses: actions/upload-artifact@v4
  with:
    name: operational-harness-status
    path: .pipeline_radiography/ci/harness_status.json
    retention-days: 7
```

**Conclusión:** CI ejecuta harness y sube artefacto correctamente.

## 5.3 ¿Falta un checkpoint M23 o ya alcanza con M23_NEXT_MILESTONE_AUDIT?

**Respuesta:** Falta checkpoint M23.

**Razones:**

1. M21 tiene checkpoint: `docs/smartpyme/M21_OPERATIONAL_HARNESS_CHECKPOINT.md`.
2. M22 tiene checkpoint: `docs/smartpyme/M22_REGISTRY_HARDENING_CHECKPOINT.md`.
3. M23 solo tiene auditoría: `docs/smartpyme/M23_NEXT_MILESTONE_AUDIT.md`.
4. Protocolo operativo: después de implementación viene checkpoint.

**Conclusión:** Falta checkpoint para mantener consistencia documental.

## 5.4 ¿Hay una inconsistencia documentada entre registry, radiography, harness y CI?

**Respuesta:** No.

**Evidencia:**

- Registry: 2 PIPELINE_CERTIFIED (excel_diagnostic, supplier_duplicate_check).
- Radiography: 5 escenarios (2 happy path cubren ambas capacidades, 3 blocked expected).
- Harness: detecta stale, orphan, partial, fail, ambiguous. Con escenarios actuales reporta GREEN.
- CI: ejecuta run_scenarios + harness + pytest, sube artefactos.

**Conclusión:** Todo funciona correctamente. No hay inconsistencias.

## 5.5 ¿Tiene sentido avanzar a nueva capacidad certificable?

**Respuesta:** No.

**Evidencia:**

- `capabilities.yaml` tiene 4 capacidades: 2 PIPELINE_CERTIFIED, 2 NOT_FOUND.
- `report_html` tiene `status: NOT_FOUND`, `no_promise_reason: no localizado en pymia.smartpyme`.
- `document_parser_front` tiene `status: NOT_FOUND`, `no_promise_reason: no localizado en pymia.smartpyme`.
- Restricción vigente: "No tratar entradas NOT_FOUND del registry como capacidades candidatas reales".

**Conclusión:** No hay capacidad candidata real. Avanzar sería inventar roadmap.

## 5.6 ¿Cuál es el próximo paso más pequeño que reduce riesgo real?

**Respuesta:** Crear checkpoint M23 y actualizar memoria local.

**Riesgo que reduce:**

- Perder trazabilidad de hitos cerrados.
- Inconsistencia entre repo y memoria local.
- Confusión sobre estado actual del proyecto.

**Alcance:**

- 1 archivo nuevo: `M23_CI_INTEGRATION_CHECKPOINT.md`.
- 3 archivos actualizados: `_estado_actual.md`, `_task_actual.md`, `_decisiones_vigentes.md`.
- 1 commit + push.

**Conclusión:** Paso mínimo, reversible, necesario para mantener protocolo operativo.

---

# 6. OPCIONES DESCARTADAS

## 6.1 M24_CI_HARNESS_ASSERTION

**Razón de descarte:**

- CI ya ejecuta harness y sube artefacto.
- `run_scenarios.py` ya retorna exit code 1 si hay FAIL/AMBIGUOUS.
- Aserción adicional no aporta valor real.
- Sería sobre-ingeniería.

## 6.2 M24_REGISTRY_CONTRACT_HARDENING

**Razón de descarte:**

- No hay inconsistencias reales que resolver.
- Ambas capacidades PIPELINE_CERTIFIED tienen traces.
- 0 stale. 0 orphan. 0 partial.
- `capability_registry.py` ya valida schema completo.

## 6.3 M24_NEXT_CAPABILITY_SELECTION

**Razón de descarte:**

- No hay evidencia de capacidad candidata real.
- `report_html` y `document_parser_front` están NOT_FOUND.
- Restricción explícita: "No tratar NOT_FOUND como candidata".
- Sería inventar roadmap.

## 6.4 M24_NEXT_CAPABILITY_IMPLEMENTATION

**Razón de descarte:**

- No hay capacidad candidata real.
- Requiere auditoría previa que no existe.
- Rompería protocolo: Coder descubre antes de Codex implementa.

## 6.5 M24_DOCS_ONLY

**Razón de descarte:**

- Insuficiente.
- M24_CHECKPOINT_CI_HARNESS incluye docs + actualización de memoria local.
- M24_DOCS_ONLY sería incompleto.

## 6.6 M24_BLOCKED

**Razón de descarte:**

- No aplica.
- No hay bloqueos técnicos.
- Hay un paso claro, mínimo y necesario (checkpoint documental).

---

# 7. REGLA DE CONTINUIDAD

No iniciar M25 sin:

1. M24 checkpoint cerrado y pusheado.
2. Memoria local actualizada.
3. Auditoría Coder para decidir M25 real.

No ampliar M24 para incluir:

- Aserciones CI adicionales.
- Nueva capacidad.
- Refactor de contratos.
- CLI público del harness.
- Dashboard.
- IA residente.

---

# 8. PROMPT CANDIDATO PARA REVIEWER

```text
Reviewer, audita la recomendación M24_CHECKPOINT_CI_HARNESS.

Contexto:
- M21 cerró con harness operacional mínimo.
- M22 endureció el harness para detectar stale certified capabilities.
- M23 integró el harness al CI (commit e87d8be).
- Workflow YAML ejecuta harness y sube harness_status.json como artefacto.
- Falta checkpoint documental formal de M23.
- Memoria local no menciona M23.
- No hay evidencia de próxima capacidad candidata real (report_html y document_parser_front están NOT_FOUND).

Propuesta:
- Crear docs/smartpyme/M23_CI_INTEGRATION_CHECKPOINT.md.
- Actualizar Pymia-memoria/_estado_actual.md, _task_actual.md, _decisiones_vigentes.md.
- Alcance mínimo: solo documentación, no tocar código.
- No agregar aserciones CI.
- No tocar registry, pipeline, dispatcher, plugins.

Preguntas:
1. ¿Es este el siguiente paso correcto o conviene priorizar otra cosa?
2. ¿El alcance es suficiente o falta actualizar otros archivos de memoria?
3. ¿Hay riesgos no identificados en la auditoría?
4. ¿Después de M24, qué debería ser M25?

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
docs/smartpyme/M23_NEXT_MILESTONE_AUDIT.md
.github/workflows/smartpyme-radiography.yml
pymia/operational_harness/__main__.py
pymia/operational_harness/harness.py
tests/smartpyme/test_operational_harness.py
pymia/smartpyme/capabilities.yaml
pymia/smartpyme/capability_registry.py
pymia/pipeline_radiography/scenarios_registry.py
pymia/pipeline_radiography/run_scenarios.py
```

---

# 10. VEREDICTO FINAL

```text
M24_CHECKPOINT_CI_HARNESS
```

**Causa:**

- M23 CI Integration fue implementado pero falta checkpoint documental formal.
- Memoria local no menciona M23.
- Crear checkpoint es paso mínimo (~15 minutos), reversible y necesario para trazabilidad.
- No requiere tocar código.
- No requiere aserciones CI adicionales.
- No requiere nueva capacidad candidata (no hay evidencia de capacidad candidata real).
- No requiere endurecimiento adicional de registry (no hay inconsistencias).
- Mantiene consistencia con M21 y M22 (ambos tienen checkpoints).

**Próximo paso metodológico:**

1. ChatGPT sintetiza este documento.
2. Codex crea `M23_CI_INTEGRATION_CHECKPOINT.md` y actualiza memoria local.
3. Commit + push.
4. Coder audita M25.
