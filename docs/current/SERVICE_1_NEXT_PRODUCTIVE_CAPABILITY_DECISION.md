# Servicio 1 — próxima decisión de capacidad productiva

## Decisión vigente

```text
STATUS: DECIDED
NEW_PRODUCTIVE_CAPABILITY_AUTHORIZED: NO
NEXT_GATE: STAGE_3_PRODUCT_AND_OPERATIONAL_HARDENING → PRODUCTION_CERTIFICATION
```

Servicio 1 conserva **12/12 patologías productivas conectadas** y el kernel genérico productivo activo. `REN_001 / net_margin_real`, que el registro histórico de CYCLE_039 identificaba como próximo incremento, ya está integrado en la raíz canónica y dispone de recorrido web y delivery XLSX acotado.

Por lo tanto, la decisión vigente no es promover una decimotercera capacidad ni abrir otra arquitectura. La expansión de capacidades queda detenida hasta que exista evidencia de hardening operativo y certificación de producción.

## Decisión pendiente dentro del portfolio existente

La composición `working_capital` usa capacidades ya gobernadas. La posible incorporación de `payment_collection_gap` permanece diferida hasta demostrar sus prerrequisitos físicos, incluido DPO, sin sobrecargar el journey ni relajar el comportamiento fail-closed.

Esto es una condición de evaluación futura sobre capacidades existentes, no una autorización de implementación.

## Evidencia actual

- `docs/current/SERVICE_1_STATUS.md` — registra 12/12 patologías conectadas y kernel genérico activo.
- `docs/current/ACTIVE_ROADMAP.md` — ubica hardening y certificación antes de reconsiderar expansión autónoma.
- `docs/current/SERVICE_1_SAAS_LAUNCH_DAY6_WORKING_CAPITAL_COMPOSITION_2026-08-11.md` — registra la composición actual y sus gaps de producto.
- `docs/service_1_next_productive_capability_decision.v1.json` — conserva la decisión histórica previa a la integración de `REN_001`; no describe el próximo incremento vigente.

## Límites

```text
ONE_CANONICAL_PRODUCT_ROOT
NO_LLM_RUNTIME_AUTHORITY
NO_SECOND_XLSX_PARSER
FAIL_CLOSED
OWNER_CONFIRMATION_IS_EVIDENCE_NOT_PERMISSION
NO_NEW_FORMULA_WITHOUT_CONTRACT_TEST_AND_EVIDENCE
```

