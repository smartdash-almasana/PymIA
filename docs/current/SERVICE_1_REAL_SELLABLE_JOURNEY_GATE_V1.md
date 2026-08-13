# SERVICE_1_REAL_SELLABLE_JOURNEY_GATE_V1

## STATUS

```text
SERVICE_1_REAL_SELLABLE_JOURNEY_GATE: PASS
SCOPE: SELLABLE_PRODUCT_V1
PRODUCTIVE_RUNTIME_CHANGED: NO
NEW_CAPABILITY: NO
NEW_ARCHITECTURE: NO
```

## PURPOSE

Probar físicamente el recorrido vendible de los tres servicios declarados `DISPONIBLE` en `SERVICE_1_SELLABLE_PRODUCT_CONTRACT_V1.md`, reutilizando la web asistida, la cadena gobernada existente y los entregables actuales.

Este gate no autoriza ampliar el portfolio.

## SELLABLE SERVICES PROVEN

```text
S1-01 Control de Cobros y Conciliación
S1-02 Conciliación Bancaria
S1-03 Margen Real
```

## PHYSICAL JOURNEYS

### S1-01 — Control de Cobros y Conciliación

```text
HOME service-first
→ selección sold_vs_collected_gap
→ XLSX real generado por fixture
→ confirmación semántica
→ ejecución del control seleccionado
→ resultado visible
→ descarga XLSX disponible
```

Test observado:

```text
tests/smartpyme/test_service_1_assisted_web_http_v1.py::test_launch_service_first_flow_runs_selected_control_after_confirmation
```

### S1-02 — Conciliación Bancaria

```text
HOME
→ iniciar conciliación bancaria
→ dos XLSX reales generados por fixture
→ confirmación explícita de columnas
→ matching gobernado
→ revisión humana requerida
→ decisión humana registrada
→ workpaper XLSX descargable
```

La prueba confirma además que PymIA no marca movimientos como conciliados automáticamente.

Test observado:

```text
tests/smartpyme/test_service_1_assisted_web_reconciliation_http_v1.py::test_bank_reconciliation_web_flow_reaches_human_review
```

### S1-03 — Margen Real

```text
HOME service-first
→ selección net_margin_real
→ XLSX real con ventas/costos/impuestos
→ confirmación semántica
→ raíz productiva real
→ P6/P7/P8 gobernados
→ ejecución determinística
→ P10/delivery existente
→ descarga service_1_ren_001_result.xlsx
```

El cierre de este gate agregó únicamente la prueba HTTP física que faltaba para unir la web real con el delivery real de REN_001. No se usó monkeypatch en ese recorrido.

Test observado:

```text
tests/smartpyme/test_service_1_assisted_web_http_v1.py::test_launch_margin_real_flow_reaches_real_delivery
```

## OBSERVED EVIDENCE

Ejecutado por el agente actuante en el checkout local real:

```text
python -m pytest \
  tests/smartpyme/test_service_1_assisted_web_http_v1.py::test_launch_service_first_flow_runs_selected_control_after_confirmation \
  tests/smartpyme/test_service_1_assisted_web_http_v1.py::test_launch_margin_real_flow_reaches_real_delivery \
  tests/smartpyme/test_service_1_assisted_web_reconciliation_http_v1.py::test_bank_reconciliation_web_flow_reaches_human_review -q
```

Resultado observado:

```text
3 passed in 4.36s
0 failed
```

Prueba focal adicional del nuevo recorrido REN_001:

```text
1 passed in 3.51s
0 failed
```

## SELLABLE GATE ASSERTIONS

```text
S1_01_REAL_HTTP_JOURNEY: PASS
S1_02_REAL_HTTP_JOURNEY: PASS
S1_03_REAL_HTTP_JOURNEY: PASS
OWNER_CONFIRMATION_PRESENT_WHERE_REQUIRED: PASS
HUMAN_REVIEW_PRESERVED_FOR_RECONCILIATION: PASS
REAL_XLSX_DELIVERY_OR_WORKPAPER: PASS
NO_MONKEYPATCH_IN_NEW_REN_HTTP_E2E: PASS
FAIL_CLOSED_BOUNDARIES: PRESERVED
ONE_CANONICAL_PRODUCT_ROOT: PRESERVED
```

## NON-CLAIMS

Este gate no prueba todavía:

```text
production deployment
restart durability of recent-case snapshots
multi-instance case persistence
production resource limits
production observability
production rollback/release reproducibility
first real paying client
```

No se declaran esos puntos como PASS.

## DECISION

```text
PROVE_REAL_SELLABLE_JOURNEY: CLOSED_PASS
NEXT_GATE: CLOSE_REAL_PRODUCTION_BLOCKERS + PRODUCTION_SMOKE
```

No se autoriza nueva capability ni ampliación de portfolio antes del siguiente gate.
