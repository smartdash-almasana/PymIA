# M45 — Guided Evidence Recovery Authorization TaskSpec

Fecha: 2026-06-09
Estado: VIGENTE
Frente: `M45_GUIDED_EVIDENCE_RECOVERY_AUTHORIZATION`

---

## 1. Objetivo

Autorizar documentalmente el próximo frente que permita implementar `Guided Evidence Recovery` como capacidad gobernada para pedir evidencia o sentido operativo faltante al dueño PyME.

La autorización es metodológica.

No implica implementación inmediata.

---

## 2. Fuente metodológica

Este TaskSpec deriva de:

- `AGENTS.md`
- `docs/pymia/PYMIA_DEVELOPMENT_METHOD.md`
- `docs/adr/ADR-019-guided-evidence-recovery-authority.md`
- `docs/adr/ADR-018-owner-facing-report-boundary.md`
- `docs/pymia/M42_OWNER_FACING_REPORT_V1_CAPABILITYSPEC.md`
- `docs/pymia/M42_OWNER_FACING_REPORT_V1_MODULECONTRACT.md`
- `docs/pymia/M43_OWNER_REPORT_DELIVERY_INTEGRATION_CHECKPOINT.md`
- `docs/pymia/M44_VISIBLE_OWNER_REPORT_OUTPUT_CHECKPOINT.md`
- `docs/pymia/M45_GUIDED_EVIDENCE_RECOVERY_AUTHORIZATION_CAPABILITYSPEC.md`
- `docs/pymia/M45_GUIDED_EVIDENCE_RECOVERY_AUTHORIZATION_MODULECONTRACT.md`

---

## 3. Scope autorizado para un ciclo futuro

La futura implementación de M45 podrá abrir, como mínimo, slices separados para:

- contrato mínimo del recovery guiado;
- clasificación de faltantes de evidencia vs faltantes de sentido operativo;
- proyección controlada de preguntas/pedidos;
- integración mínima al state o a un artefacto documental futuro;
- tests focales y evidencia de cierre.

---

## 4. Archivos prohibidos para el frente documental actual

Este ciclo M45 es:

```text
DOCUMENTAL ONLY
```

No autoriza tocar:

- código productivo;
- tests ejecutables;
- Telegram;
- Hermes;
- FastAPI;
- runtime;
- parser Excel;
- fórmulas;
- `DiagnosticCoreV1`.

---

## 5. Criterios PASS futuros

M45 sólo podrá cerrarse implementativamente en un ciclo posterior si existe evidencia de que:

- el recovery guiado pide evidencia o sentido operativo faltante de forma trazable;
- no inventa datos;
- no diagnostica;
- no cambia findings ni veredictos;
- distingue dato faltante de significado faltante;
- mantiene comportamiento fail-closed;
- tiene tests focales;
- tiene evidencia atribuida al actor ejecutor.

---

## 6. Criterios BLOCKED futuros

El frente futuro deberá quedar bloqueado si:

- no existe artefacto fuente que justifique la pregunta;
- el recovery requiere inventar contexto;
- aparece necesidad de canal productivo no autorizado;
- la implementación mezcla recovery con diagnóstico;
- la trazabilidad del faltante no puede mantenerse.

---

## 7. No objetivos

M45 no busca:

- lanzar producto;
- abrir conversación productiva;
- abrir Telegram;
- abrir Hermes;
- abrir FastAPI;
- resolver automáticamente la falta de evidencia;
- imputar valores;
- mejorar narrativa comercial;
- expandir el diagnóstico.

---

## 8. Salida obligatoria del futuro actor implementador

El actor que implemente una futura versión de M45 deberá devolver:

```text
Repo state
Sources read
Certified / hypothesis / gap / next methodological step
Files changed
Validation evidence
Commit / push status
Next step
```

---

## 9. Estado

```text
M45 = AUTHORIZED_FOR_FUTURE_IMPLEMENTATION
```

Este TaskSpec autoriza el frente futuro de recuperación guiada.

No certifica código, tests ni PASS operativo.
