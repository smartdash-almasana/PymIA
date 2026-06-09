# M44 — Visible Owner Report Output CapabilitySpec

Fecha: 2026-06-09
Estado: VIGENTE
Frente: `M44_VISIBLE_OWNER_REPORT_OUTPUT`

---

## 1. Capacidad

PymIA puede exponer de forma visible el `summary` del `OwnerFacingReport` ya calculado, dentro de la respuesta/state existente del sistema, sin abrir un canal externo nuevo.

La capacidad autorizada es:

```text
CoreAuditDeliveryBundle.owner_facing_report["summary"]
→ PymIAState.delivery_summary
→ render_response existente
```

---

## 2. Autoridad heredada

M44 hereda sus límites de:

- `ADR-018 — Owner-Facing Report Boundary`
- `M42 — Owner-Facing Report V1 CapabilitySpec`
- `M42 — Owner-Facing Report V1 ModuleContract`
- `M43 — Owner Report Delivery Integration Checkpoint`

M44 no crea una nueva autoridad diagnóstica.

---

## 3. Qué puede hacer

M44 puede:

- tomar el `summary` ya producido por `OwnerFacingReport`;
- proyectarlo a `PymIAState.delivery_summary`;
- permitir que la respuesta ya existente del sistema muestre ese resumen;
- conservar fallback seguro a `DeliveryPackage.summary` si el summary owner-facing está vacío;
- mantener `output_refs` existentes, incluyendo `owner_facing_report.json` cuando esté integrado al bundle.

---

## 4. Inputs requeridos

- `CoreAuditDeliveryBundle`
- `bundle.owner_facing_report`
- `bundle.owner_facing_report["summary"]`
- `bundle.delivery_package.summary`
- `bundle.delivery_package.output_refs`
- `bundle.execution_result`
- `bundle.gate_verdict`

---

## 5. Outputs requeridos

- `PymIAState.delivery_summary` prioriza `owner_facing_report["summary"]` cuando existe y no está vacío.
- `PymIAState.delivery_summary` usa `delivery_package.summary` como fallback.
- La respuesta visible del grafo puede reflejar ese `delivery_summary` sin recalcular ni enriquecer contenido.

---

## 6. Limitaciones obligatorias

M44 no autoriza:

- Telegram;
- Hermes;
- FastAPI;
- canal productivo;
- parser Excel;
- cambios en `DiagnosticCoreV1`;
- cambios en fórmulas;
- nuevos findings;
- nuevo diagnóstico;
- narrativa libre;
- ocultar bloqueos;
- presentar estados `CANDIDATE` como `CONFIRMED`.

---

## 7. Failure states

La capacidad debe admitir:

- `owner_facing_report.summary` presente → usar summary owner-facing;
- `owner_facing_report.summary` vacío o faltante → fallback a `delivery_package.summary`;
- bundle bloqueado → mantener estado bloqueado y summary bloqueado;
- bundle entregable candidato → mantener estado candidato sin confirmarlo.

---

## 8. Criterios de aceptación

M44 sólo puede considerarse cerrado si existe evidencia de que:

- `project_bridge_result_to_state(...)` propaga `owner_facing_report.summary`;
- existe fallback a `delivery_package.summary`;
- un replay/grafo real muestra el summary visible esperado;
- no se tocaron canales externos ni runtime productivo;
- no se alteró `OwnerFacingReport` ni `DiagnosticCoreV1`.

---

## 9. Estado

```text
M44 = AUTHORIZED_DOCUMENTARY
```

Este documento autoriza el frente mínimo de visibilidad controlada.

No certifica implementación ni PASS.
