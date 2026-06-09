# M44 — Visible Owner Report Output TaskSpec

Fecha: 2026-06-09
Estado: VIGENTE
Frente: `M44_VISIBLE_OWNER_REPORT_OUTPUT`

---

## 1. Objetivo

Implementar el slice mínimo que hace visible el `summary` del `OwnerFacingReport` ya integrado en M43.

La visibilidad debe ocurrir dentro del circuito existente de state/respuesta, sin abrir canales externos ni crear narrativa nueva.

---

## 2. Fuente metodológica

Este TaskSpec deriva de:

- `AGENTS.md`
- `docs/pymia/PYMIA_DEVELOPMENT_METHOD.md`
- `docs/adr/ADR-018-owner-facing-report-boundary.md`
- `docs/pymia/M42_OWNER_FACING_REPORT_V1_CAPABILITYSPEC.md`
- `docs/pymia/M42_OWNER_FACING_REPORT_V1_MODULECONTRACT.md`
- `docs/pymia/M43_OWNER_REPORT_DELIVERY_INTEGRATION_CHECKPOINT.md`
- `docs/pymia/M44_VISIBLE_OWNER_REPORT_OUTPUT_CAPABILITYSPEC.md`
- `docs/pymia/M44_VISIBLE_OWNER_REPORT_OUTPUT_MODULECONTRACT.md`

---

## 3. Scope permitido

Archivos permitidos para implementación:

```text
pymia/audit_result/core_delivery_bridge.py
tests/diagnosticcore/test_core_audit_delivery_bridge.py
tests/orchestration/test_graph.py
```

---

## 4. Archivos prohibidos

No tocar:

```text
pymia/smartpyme/owner_facing_report.py
pymia/orchestration/graph.py
pymia/diagnostic_core/
pymia/telegram*
conversa-engine/
Hermes / hermes /
parser Excel
fórmulas
FastAPI
```

---

## 5. Cambio autorizado

En `project_bridge_result_to_state(...)`, la asignación de `delivery_summary` debe priorizar:

```python
bundle.owner_facing_report["summary"]
```

con fallback a:

```python
bundle.delivery_package.summary
```

Regla esperada:

```text
owner_summary no vacío → delivery_summary = owner_summary
owner_summary vacío/faltante → delivery_summary = delivery_package.summary
```

---

## 6. Tests requeridos

Agregar o preservar tests que prueben:

1. `project_bridge_result_to_state(...)` propaga `owner_facing_report.summary`.
2. `project_bridge_result_to_state(...)` hace fallback a `delivery_package.summary` si el owner summary está vacío.
3. Un flujo/replay de grafo con fixture real muestra el summary owner-facing como salida visible.

---

## 7. Validación esperada

Comando de validación para el actor implementador:

```powershell
python -m pytest tests/orchestration/test_graph.py tests/diagnosticcore/test_core_audit_delivery_bridge.py -q --basetemp .tmp_pytest_m44
```

La evidencia debe ser atribuida al actor que la ejecute.

---

## 8. Criterios PASS

M44 puede cerrarse sólo si:

- los tests requeridos pasan;
- el diff toca sólo archivos permitidos;
- no se toca Telegram, Hermes, FastAPI, parser Excel ni DiagnosticCore;
- no se modifica `owner_facing_report.py`;
- no se agregan findings ni diagnóstico;
- se registra checkpoint M44 con evidencia;
- se informa commit hash si se commitea.

---

## 9. Criterios PARTIAL

Reportar `PARTIAL` si:

- la proyección a state queda implementada pero falta replay de grafo;
- los tests unitarios pasan pero falta checkpoint;
- existe evidencia incompleta o atribuida a otro actor.

---

## 10. Criterios BLOCKED

Reportar `BLOCKED` si:

- el repo tiene cambios ajenos no relacionados;
- la implementación requiere tocar archivos prohibidos;
- falta evidencia para afirmar salida visible;
- aparece necesidad de canal externo;
- el owner summary no existe en el bundle;
- hay que reinterpretar diagnóstico para mostrar una respuesta.

---

## 11. No objetivos

M44 no busca:

- lanzar producto;
- abrir Telegram;
- abrir endpoint;
- generar PDF;
- crear HTML;
- modificar diseño comercial;
- implementar Guided Evidence Recovery;
- implementar memoria;
- ampliar `OwnerFacingReport`;
- mejorar narrativa.

---

## 12. Salida obligatoria del actor implementador

El actor que implemente debe devolver:

```text
Repo state
Files changed
Diff summary
Validation command
Validation output
Commit hash, si aplica
PASS / PARTIAL / BLOCKED
```

---

## 13. Estado

```text
M44 = AUTHORIZED_FOR_IMPLEMENTATION
```

Este TaskSpec autoriza sólo el slice mínimo descrito.
