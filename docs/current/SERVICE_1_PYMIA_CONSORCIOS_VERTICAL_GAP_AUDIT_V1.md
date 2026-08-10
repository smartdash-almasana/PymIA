# SERVICE_1_PYMIA_CONSORCIOS_VERTICAL_GAP_AUDIT_V1

**Fecha:** 2026-08-10  
**Estado:** `AUDIT_COMPLETE`  
**Alcance:** Servicio 1 enterprise / vertical Consorcios  
**Raíz productiva canónica:** `pymia/smartpyme/service_1_product_pipeline_v1.py`

## 1. Objetivo

Determinar qué falta exactamente para convertir el Servicio 1 actual en un primer piloto real pagable para un administrador de consorcios con operación mensual sobre 10 edificios, reutilizando la arquitectura y capacidades existentes y sin crear una segunda raíz productiva.

Unidad de trabajo:

```text
administrador real
→ archivos reales
→ comprensión semántica
→ confirmación explícita
→ controles determinísticos
→ resultado por edificio/período
→ entregable útil
```

No se evalúa crear un ERP de administración de consorcios ni reemplazar el software de origen.

## 2. Evidencia del checkout real

### 2.1 Capacidades reutilizables ya disponibles

El catálogo actual expone, entre otras:

- `sold_vs_collected_gap` / LIQ_001 — ventas y cobros;
- `net_margin_real` / REN_001 — margen neto real;
- `projected_closing_cash_balance` / LIQ_002 — saldo de caja proyectado;
- `dso` / PYME_011 — tiempo de cobro;
- `payment_collection_gap` / PYME_013 — cobros y pagos;
- `current_ratio` / PYME_024 — relación de corto plazo;
- `adjusted_operating_cash_flow` / PYME_026 — flujo operativo ajustado.

La web asistida también expone conciliación bancaria y Mercado Pago ↔ Banco mediante el flujo de conciliación gobernado existente.

Conclusión: no hace falta inventar una “capacidad Consorcios” para abrir el piloto.

### 2.2 Recorrido común ya existente

La web asistida ya soporta:

```text
XLSX
→ interpretación/confirmación de columnas
→ selección explícita de revisión
→ ejecución determinística
→ resultado comprensible
→ descarga autorizada
```

El producto mantiene las guardas vigentes:

```text
owner confirmation ≠ runtime authorization
semantic approval ≠ computability
computation ≠ diagnosis final
```

Supabase Auth, identidad tenant, persistencia semántica durable, tenant memory recall y supersession ya están integrados y físicamente cerrados en el recorrido Servicio 1.

### 2.3 Límites actuales relevantes

El checkout no contiene un modelo explícito de `consorcio`, `edificio` o `building_id`.

La web asistida tampoco implementa historial persistente completo de casos; su propia especificación lo mantiene fuera del slice actual.

Por lo tanto, hoy el sistema puede analizar archivos y producir resultados gobernados, pero no puede representar de forma productiva y explícita:

```text
administrador
→ edificio A
→ período julio
→ análisis/resultados

administrador
→ edificio B
→ período julio
→ análisis/resultados
```

como unidades diferenciadas y recuperables del producto.

## 3. Gap real del vertical

El gap principal NO es analítico.

No falta:

- otro parser;
- otro motor semántico;
- otro kernel;
- otra raíz productiva;
- una nueva patología;
- LLM runtime;
- un ERP de consorcios.

Falta una capa mínima de **contexto operativo del caso** que permita asociar el recorrido común existente a:

```text
tenant administrador
+ edificio/consorcio
+ período
+ archivos de entrada
+ revisión solicitada
+ resultados/entregables
```

Sin esa asociación, un piloto de 10 edificios puede demostrarse manualmente, pero no constituye todavía un recorrido vertical repetible y limpio.

## 4. Qué capacidades usar en el piloto V1

El piloto no debe intentar cubrir todas las capacidades del catálogo.

Primer núcleo funcional recomendado:

```text
1. cobranzas / deuda
   → sold_vs_collected_gap cuando la evidencia disponible corresponda
   → dso cuando existan cuentas por cobrar, ventas y período

2. caja
   → projected_closing_cash_balance

3. control bancario
   → bank reconciliation existente

4. resultado económico
   → net_margin_real solo cuando el archivo posea precio/ingresos, costos e impuestos compatibles con su contrato
```

La selección final de controles para cada edificio debe seguir dependiendo de evidencia y contratos; el vertical no debe forzar capacidades no computables.

`payment_collection_gap` no debe convertirse en dependencia obligatoria del piloto mientras sus prerrequisitos físicos sigan deferidos por contrato.

## 5. Corte mínimo autorizado recomendado

### `SERVICE_1_CONSORCIOS_CASE_CONTEXT_V1`

Objetivo único:

> permitir que el recorrido productivo actual opere un caso identificado por edificio/consorcio y período, sin duplicar ninguna lógica del kernel.

Contrato mínimo:

```text
TenantContext
  tenant_id
  cliente_id

ConsorcioCaseContext
  case_id
  consorcio_name
  period
  source_files
  requested_review
```

Requisitos:

1. El usuario identifica edificio/consorcio y período antes de ejecutar la revisión.
2. Ese contexto acompaña el `case_id` existente; no crea una nueva raíz productiva.
3. Los resultados y archivos descargables quedan vinculados al caso correcto.
4. La memoria semántica sigue siendo tenant-scoped y no autoriza reutilización automática.
5. No se agrega selección automática de capacidad.
6. No se agrega LLM runtime.
7. No se implementa todavía dashboard multi-edificio ni historial SaaS general.
8. No se agregan nuevas patologías.
9. Debe existir un E2E físico con al menos dos edificios distintos del mismo tenant para probar que no se mezclan casos, archivos ni delivery.

## 6. E2E de aceptación del corte

```text
Supabase Auth real
→ mismo tenant administrador
→ edificio A + período
→ XLSX A
→ confirmación explícita
→ revisión computable
→ P6/P7/P8
→ ejecución
→ P10
→ descarga A

→ edificio B + mismo período
→ XLSX B
→ confirmación explícita
→ revisión computable
→ P6/P7/P8
→ ejecución
→ P10
→ descarga B

→ verificar aislamiento A/B
```

Criterios mínimos:

```text
AUTH: PASS
TENANT_IDENTITY: PASS
CASE_A_CONTEXT: PASS
CASE_B_CONTEXT: PASS
CASE_ISOLATION: PASS
OWNER_CONFIRMATION: PASS
P6_P7_P8: PASS
DETERMINISTIC_EXECUTION: PASS
P10: PASS
DOWNLOAD: PASS
CROSS_CASE_LEAKAGE: NONE
```

## 7. Lo que NO corresponde abrir ahora

```text
NO nueva capacidad Consorcios
NO dashboard de 10 edificios
NO CRM
NO ERP
NO billing
NO conectores bancarios nuevos
NO OCR/PDF
NO LLM runtime
NO agente autónomo
NO historial general completo
NO Servicio 2/3
```

## 8. Decisión

```text
AUDIT_VERDICT: PASS

NEXT_CUT:
SERVICE_1_CONSORCIOS_CASE_CONTEXT_V1

WHY:
el motor y las capacidades ya existen;
el gap mínimo para un piloto multiedificio repetible es contexto y aislamiento de caso por edificio/período.
```

Después de cerrar físicamente ese corte, el paso siguiente debe ser ejecutar el piloto real sobre la cartera de 10 edificios y dejar que la fricción observada determine el siguiente desarrollo.
