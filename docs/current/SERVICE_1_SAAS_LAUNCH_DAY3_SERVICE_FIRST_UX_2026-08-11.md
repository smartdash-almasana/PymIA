# SERVICE_1_SAAS_LAUNCH — DAY 3 SERVICE-FIRST UX

**Fecha:** 2026-08-11
**Checkout:** `E:\BuenosPasos\smartbridge\PymIA`
**Objetivo:** transformar la entrada de Servicio 1 de `upload-first + catálogo técnico` a `service-first + portfolio comercial`, sin nueva arquitectura.

---

## 1. CAMBIO PRINCIPAL IMPLEMENTADO

La home ya no abre con:

`Revisar información de mi negocio → subir Excel → elegir entre 12 capacidades`

Ahora abre con:

`¿Qué querés controlar hoy?`

Y muestra únicamente los servicios de lanzamiento técnicamente cerrados:

- **Control de Cobros y Conciliación**
- **Margen Real**
- **Conciliación Bancaria** como flujo de dos fuentes separado

RADAR aparece como capa transversal.

Consorcios queda explícitamente en validación y fuera del portfolio general de lanzamiento.

---

## 2. FLUJO SERVICE-FIRST

Para controles de una fuente:

```text
HOME
→ elegir servicio
→ cargar Excel
→ confirmar significado si hace falta
→ ejecutar automáticamente el servicio elegido
→ resultado
→ descarga
```

La selección comercial queda guardada en la sesión como `selected_launch_review` y, luego de las confirmaciones semánticas, la app ejecuta directamente el control seleccionado.

El recorrido genérico histórico sigue existiendo cuando no se recibe una selección de launch, para no romper compatibilidad interna.

---

## 3. PORTFOLIO VISIBLE

La home de lanzamiento ya NO muestra como oferta principal:

- saldo de caja proyectado;
- DSO;
- payment collection gap;
- reorder point;
- inventory turnover;
- current ratio;
- sales concentration;
- interest burden;
- adjusted operating cash flow;
- index update ratio.

Estas siguen siendo capacidades internas del motor, pero no productos comerciales visibles.

---

## 4. VALIDACIÓN FÍSICA NUEVA

Se agregó prueba HTTP específica del recorrido service-first:

```text
GET /
→ muestra portfolio comercial
→ elige Control de Cobros y Conciliación
→ POST Excel
→ confirmación semántica
→ ejecución automática del servicio seleccionado
→ resultado Ventas y cobranzas
→ download XLSX disponible
```

Validación focal inmediata:

`12 passed`

Validación ampliada de assisted web + conciliación + RADAR + tenant + Consorcios no-regresión + REN_001:

`49 passed, 2 skipped`

Los 2 skips corresponden a pruebas condicionadas por entorno y no a fallos del corte.

---

## 5. CAMBIOS DE CONTRATO UX

La interfaz visible debe privilegiar lenguaje comercial y cotidiano:

- `¿Qué querés controlar hoy?`
- `Control de Cobros y Conciliación`
- `Margen Real`
- `Conciliación bancaria`
- `Archivo de Excel`
- `Iniciar control`

Se actualizaron los tests de contrato de superficie para reflejar este lenguaje.

No se expone lenguaje como P6/P8, pathology, kernel o capability al usuario.

---

## 6. ARCHIVOS MODIFICADOS EN DAY 3

Productivo:

- `pymia/smartpyme/service_1_assisted_web_v1.py`

Tests:

- `tests/smartpyme/test_service_1_assisted_web_http_v1.py`
- `tests/smartpyme/test_service_1_assisted_web_reconciliation_http_v1.py`
- `tests/smartpyme/test_service_1_assisted_web_vertical_slice_contract_v1.py`

Además permanece el ajuste Day 2:

- `tests/smartpyme/test_service_1_pyme_011_productive_root_v1.py`

No se modificó la raíz productiva canónica.

---

## 7. ESTADO REAL AL CIERRE DE DAY 3

| Área | Estado |
|---|---|
| Home service-first | `IMPLEMENTED` |
| Portfolio comercial reducido | `IMPLEMENTED` |
| Cobros service-first HTTP E2E | `PASS` |
| Conciliación bancaria HTTP | `PASS` |
| Margen Real sellable path | `PASS` |
| Assisted web regression focal | `PASS` |
| RADAR regression focal | `PASS/SKIP_BY_ENV` |
| Enterprise visual polish | `PENDING` |
| Casos recientes / reentrada general SaaS | `PENDING` |
| Caja como servicio compuesto | `PENDING` |
| Stock como servicio compuesto | `GATED` |

---

## 8. DECISIÓN DAY 3

`SERVICE_FIRST_UX: PASS`

`THREE_CORE_SERVICES_VISIBLE: PASS`

`TECHNICAL_REGRESSION: PASS`

`NEW_ARCHITECTURE: NO`

### Próximo paso

Day 4 debe concentrarse en **enterprise visual polish + estructura común de resultados** para que Cobros, Banco y Margen se perciban como tres servicios de una misma aplicación SaaS, no como pantallas técnicas independientes.

No agregar capacidades nuevas.
