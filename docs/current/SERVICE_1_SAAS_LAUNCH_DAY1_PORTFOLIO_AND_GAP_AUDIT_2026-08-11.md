# SERVICE_1_SAAS_LAUNCH — DAY 1 PORTFOLIO FREEZE + PHYSICAL GAP AUDIT

**Fecha:** 2026-08-11
**Checkout:** `E:\BuenosPasos\smartbridge\PymIA`
**Rama verificada:** `main`
**HEAD verificado:** `a44160624615f6a61e9541c3fe06f77498802c7b`
**Objetivo:** congelar el portfolio de salida SaaS de Servicio 1 y determinar, sobre evidencia física del repo, qué existe, qué falta y qué bloquea.

---

## 1. PORTFOLIO DE LANZAMIENTO CONGELADO

### MANDATORIOS

1. `S1-01` — **Control de Cobros y Conciliación**
2. `S1-02` — **Conciliación Bancaria**
3. `S1-03` — **Margen Real**
4. `S1-04` — **Caja y Capital de Trabajo**
5. `S1-R` — **RADAR transversal**

### GATE DE INCLUSIÓN

6. `S1-05` — **Stock y Reposición**

Si `S1-05` no alcanza recorrido sintético E2E + UX común antes del freeze de lanzamiento, aparece como `PRÓXIMAMENTE`, no como `DISPONIBLE`.

### FUERA DEL LAUNCH V1

- Consorcios como suite general;
- Marketplace / Mercado Libre / Mercado Pago como vertical completa;
- Secretario Digital;
- ARCA / impuestos como suite;
- CRM;
- ERP;
- WhatsApp;
- gestión general de tareas;
- billing propio;
- agentes autónomos;
- nueva arquitectura.

---

## 2. EVIDENCIA DE BASE VERIFICADA

El Product Completion Gate existente declara una raíz productiva única:

`pymia/smartpyme/service_1_product_pipeline_v1.py`

El catálogo web actual ya expone las capacidades:

- `sold_vs_collected_gap`
- `net_margin_real`
- `projected_closing_cash_balance`
- `dso`
- `payment_collection_gap`
- `reorder_point`
- `inventory_turnover`
- `current_ratio`
- `sales_concentration`
- `interest_burden_ratio`
- `adjusted_operating_cash_flow`
- `index_update_ratio`

Y conciliación bancaria está expuesta como recorrido separado.

No se crea segunda raíz productiva.

---

## 3. PRUEBA FÍSICA EJECUTADA HOY

### Pack principal

Se ejecutaron tests focales sobre:

- LIQ_001 / vendido vs cobrado;
- conciliación + human review + workpaper;
- REN_001 / margen real;
- LIQ_002 / caja proyectada;
- DSO;
- INV_001 / punto de reposición;
- INV_002 / rotación;
- RADAR engine/policy/persistence.

Resultado:

`94 passed, 1 failed`

Único fallo:

`test_service_1_pyme_011_productive_root_v1.py::test_pyme_011_builds_real_governed_plan_without_monkeypatch`

Causa observada:

`P7 requires only APPROVED P6 decisions`

No se atribuye aún causa raíz. Debe tratarse como gap real a aislar antes de usar DSO dentro del servicio compuesto de Caja y Capital de Trabajo.

### Pack complementario

Se ejecutaron tests sobre:

- `payment_collection_gap`;
- `current_ratio`;
- `interest_burden_ratio`;
- `adjusted_operating_cash_flow`;
- `sales_concentration`;
- catálogo web;
- conciliación web HTTP;
- web asistida HTTP.

Resultado:

`59 passed`

---

## 4. MATRIZ DAY 1 — EXISTE / GAP / BLOCKER

| Servicio | Núcleo determinístico | Evidencia sintética/focal | Web actual | Entregable | Estado Day 1 | Bloqueador actual |
|---|---|---|---|---|---|---|
| **S1-01 Cobros y Conciliación** | Sí | PASS | Sí | XLSX/delivery existente | `READY_FOR_LAUNCH_CLOSURE` | Ninguno estructural detectado |
| **S1-02 Conciliación Bancaria** | Sí | PASS | Sí | Workpaper XLSX | `READY_FOR_LAUNCH_CLOSURE` | Ninguno estructural detectado |
| **S1-03 Margen Real** | Sí | PASS | Sí | Delivery existente | `READY_FOR_LAUNCH_CLOSURE` | Validar inputs + UX E2E final |
| **S1-04 Caja y Capital de Trabajo** | Parcialmente compuesto | Parcial: mayoría PASS, 1 fallo DSO | Capacidades individuales visibles | No hay todavía entrega única de servicio compuesto | `GAP` | DSO focal fallando + falta composición E2E del servicio |
| **S1-R RADAR** | Sí | PASS | Sí, especialmente recorrido Consorcios | Persistencia/eventos | `READY_AS_TRANSVERSAL_LAYER` | Falta UX común sobre servicios launch, no motor nuevo |
| **S1-05 Stock y Reposición** | Sí: reorder + turnover + concentración | PASS focal | Capacidades individuales visibles | No hay todavía producto compuesto uniforme | `GATED` | Falta recorrido sintético E2E + UX/entrega común |

---

## 5. LECTURA PRÁCTICA

### Tres servicios seguros para cerrar primero

`S1-01`, `S1-02` y `S1-03` no requieren nueva arquitectura. El trabajo pendiente debe ser cierre de experiencia SaaS, recorrido sintético, resultado uniforme y demo.

### Caja y Capital de Trabajo

No debe declararse disponible todavía. Existe una base amplia y la mayoría de sus piezas focales pasan, pero hoy hay dos gaps concretos:

1. un fallo reproducible en el recorrido gobernado de DSO;
2. no existe todavía una composición comercial única que convierta las capacidades individuales en el servicio `Caja y Capital de Trabajo`.

### RADAR

No debe abrir otro producto raíz. Se reutiliza como capa transversal sobre resultados ya gobernados. El motor/persistencia tienen tests verdes en el pack ejecutado hoy.

### Stock y Reposición

Tiene mejor situación técnica que comercial: `reorder_point` e `inventory_turnover` pasan focalmente y `sales_concentration` también pasó en el pack complementario, pero todavía no existe un recorrido SaaS unificado que merezca llamarse servicio terminado. Mantener bajo gate.

---

## 6. GATE DE LANZAMIENTO APLICABLE DESDE MAÑANA

Un servicio sólo puede aparecer como `DISPONIBLE` si pasa:

1. caso sintético realista;
2. login/tenant;
3. creación o selección de control;
4. ingesta de archivos;
5. confirmación semántica cuando corresponda;
6. ejecución determinística;
7. caso imperfecto / excepción;
8. fail-closed;
9. resultado comprensible;
10. evidencia/provenance;
11. revisión humana cuando aplique;
12. persistencia y reentrada;
13. entregable;
14. aislamiento tenant;
15. interfaz responsive y coherente;
16. RADAR cuando el servicio lo permita.

---

## 7. DECISIÓN DAY 1

`PORTFOLIO_FREEZE: PASS`

`CORE_REOPEN: NO`

`NEW_ARCHITECTURE: NO`

`DAY_2_PRIORITY:`

1. aislar el único fallo DSO sin ampliar alcance;
2. definir el recorrido SaaS común mínimo para los servicios launch;
3. preparar el cierre sintético E2E de `S1-01`, `S1-02`, `S1-03`;
4. mantener `S1-04` en GAP hasta resolver composición + DSO;
5. mantener `S1-05` bajo gate.

No se autoriza desarrollo de nuevas capacidades en Day 1.
