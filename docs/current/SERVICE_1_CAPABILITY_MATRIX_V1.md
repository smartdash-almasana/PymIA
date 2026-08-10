# SERVICE_1_CAPABILITY_MATRIX_V1

Estado: CURRENT WORKTREE EVIDENCE — 2026-08-10

## Propósito

Definir qué puede resolver Servicio 1 en los cuatro verticales comerciales sin convertir PymIA en un ERP y sin confundir capacidad implementada con capacidad vendible o físicamente probada.

Verticales:

1. Contadores / estudios contables
2. Administradores de consorcios y edificios
3. Distribuidoras mayoristas
4. Sellers Mercado Libre / Mercado Pago

## Estados

- `PHYSICAL_E2E_PROVEN`: recorrido físico probado con evidencia real/fixture representativo y gobierno productivo.
- `IMPLEMENTED`: código productivo existe, pero no hay prueba física vertical suficiente para declararlo probado en ese vertical.
- `REUSABLE_CORE`: capacidad existente y conceptualmente reutilizable, pero falta binding/pack vertical y prueba física.
- `INFRASTRUCTURE_EXISTS`: existen componentes o herramientas de soporte, pero no una capacidad comercial cerrada.
- `NOT_IMPLEMENTED`: no existe todavía el corte productivo necesario.
- `NOT_PRIORITY`: posible pero no necesario para el primer producto vendible del vertical.

> Regla: `REUSABLE_CORE` no equivale a `PHYSICAL_E2E_PROVEN`.

---

## Núcleo productivo actual de Servicio 1

### Capacidades genéricas registradas

- `projected_closing_cash_balance`
- `reorder_point`
- `inventory_turnover`
- `dpo`
- `payment_collection_gap`
- `current_ratio`
- `sales_concentration`
- `interest_burden_ratio`
- `adjusted_operating_cash_flow`
- `index_update_ratio`
- `dso`

### Capacidades/cortes especializados existentes

- `sold_vs_collected_gap` / LIQ_001 — cierre vendible probado.
- `net_margin_real` / REN_001 — cierre vendible probado.
- `BANK_RECONCILIATION` — preparación asistida y revisión humana.
- `MERCADO_PAGO_BANK_RECONCILIATION` — infraestructura productiva existente.
- `collection_aging` — worktree actual, probado físicamente en Cabildo y Rivadavia.
- `expense_variance` — worktree actual, probado físicamente en Cabildo y Rivadavia.
- Consorcio case context — cerrado en `main`, con aislamiento tenant/consorcio/período.

### Gobierno transversal ya disponible

- ingesta XLSX canónica;
- comprensión/confirmación semántica;
- contrato semántico tenant;
- memoria semántica con reconfirmación;
- P5/P6/P7/P8 fail-closed;
- raíz productiva única;
- evidencia y bounded outcomes;
- revisión humana para conciliación;
- tenant identity / Supabase Auth.

---

# Matriz por familia de capacidad

| Familia | Contadores | Consorcios | Distribuidoras | Sellers ML/MP |
|---|---|---|---|---|
| Ingesta XLSX + semántica | PHYSICAL_E2E_PROVEN | PHYSICAL_E2E_PROVEN | REUSABLE_CORE | REUSABLE_CORE |
| Tenant/caso/período | PHYSICAL_E2E_PROVEN | PHYSICAL_E2E_PROVEN | REUSABLE_CORE | REUSABLE_CORE |
| Vendido vs cobrado | PHYSICAL_E2E_PROVEN | REUSABLE_CORE | REUSABLE_CORE | REUSABLE_CORE |
| Aging / mora detallada | REUSABLE_CORE | PHYSICAL_E2E_PROVEN* | REUSABLE_CORE | NOT_PRIORITY |
| DSO | IMPLEMENTED | NOT_PRIORITY | REUSABLE_CORE | NOT_PRIORITY |
| Conciliación bancaria | PHYSICAL_E2E_PROVEN | PHYSICAL_E2E_PROVEN* | REUSABLE_CORE | REUSABLE_CORE |
| MP ↔ Banco | IMPLEMENTED | NOT_PRIORITY | NOT_PRIORITY | REUSABLE_CORE |
| Caja proyectada | IMPLEMENTED | REUSABLE_CORE | REUSABLE_CORE | REUSABLE_CORE |
| Margen neto real | PHYSICAL_E2E_PROVEN | NOT_PRIORITY | REUSABLE_CORE | REUSABLE_CORE |
| Presupuesto vs gasto real | REUSABLE_CORE | PHYSICAL_E2E_PROVEN* | REUSABLE_CORE | REUSABLE_CORE |
| Stock / reposición | IMPLEMENTED | NOT_PRIORITY | REUSABLE_CORE | REUSABLE_CORE |
| Rotación de inventario | IMPLEMENTED | NOT_PRIORITY | REUSABLE_CORE | REUSABLE_CORE |
| Concentración comercial | IMPLEMENTED | NOT_PRIORITY | REUSABLE_CORE | REUSABLE_CORE |
| Carga financiera | IMPLEMENTED | NOT_PRIORITY | REUSABLE_CORE | REUSABLE_CORE |
| Flujo operativo ajustado | IMPLEMENTED | REUSABLE_CORE | REUSABLE_CORE | REUSABLE_CORE |
| Proveedores / DPO | IMPLEMENTED | REUSABLE_CORE | REUSABLE_CORE | NOT_PRIORITY |
| ARCA / obligaciones | INFRASTRUCTURE_EXISTS | NOT_PRIORITY | NOT_PRIORITY | NOT_PRIORITY |
| Devoluciones | NOT_PRIORITY | NOT_PRIORITY | NOT_PRIORITY | NOT_IMPLEMENTED |
| Publicidad vs margen | NOT_PRIORITY | NOT_PRIORITY | NOT_PRIORITY | NOT_IMPLEMENTED |
| Días de cobertura stock | NOT_PRIORITY | NOT_PRIORITY | REUSABLE_CORE | REUSABLE_CORE |
| Radar/priorización común | INFRASTRUCTURE_EXISTS | INFRASTRUCTURE_EXISTS | INFRASTRUCTURE_EXISTS | INFRASTRUCTURE_EXISTS |
| Reporte ejecutivo común | IMPLEMENTED/PARCIAL | IMPLEMENTED/PARCIAL | REUSABLE_CORE | REUSABLE_CORE |

`*` probado en el worktree actual; todavía no implica cierre en `main` hasta integrar el corte.

---

# Vertical 1 — Contadores / estudios contables

## Entrada mínima

- XLSX/documentos estructurados del cliente;
- período;
- identidad tenant/cliente;
- columnas confirmadas por el dueño/operador.

## Evidencia mínima

- ventas/compras/cobranzas/pagos/bancos según control solicitado;
- trazabilidad de archivo, hoja y columna;
- estado de evidencia faltante.

## Controles que Servicio 1 ya puede sostener

- vendido vs cobrado;
- conciliación bancaria asistida;
- DSO;
- DPO;
- caja proyectada;
- ratios de corto plazo;
- margen neto real cuando existe evidencia suficiente;
- concentración;
- indicadores financieros acotados.

## Gap vertical real

No faltan principalmente fórmulas. Falta **composición multicliente orientada a trabajo**:

`cliente → período → faltantes/findings → severidad → evidencia → próxima acción`.

### Próximo corte recomendado para Contadores

`SERVICE_1_ACCOUNTANT_PORTFOLIO_RADAR_V1`

No debe calcular contabilidad. Debe ordenar trabajo pendiente y reutilizar outcomes ya gobernados.

---

# Vertical 2 — Consorcios

## Entrada mínima

- tenant administrador;
- consorcio/edificio;
- período;
- Expensas;
- Cobranzas;
- Banco;
- Gastos;
- Presupuesto.

## Controles físicamente probados

- contexto e aislamiento por edificio/período;
- aging/mora por Unidad Funcional mediante períodos equivalentes de deuda;
- conciliación Cobranzas ↔ Banco;
- movimientos bancarios sin imputar;
- cobranzas sin banco;
- diferencias de importe;
- referencias ambiguas;
- gasto real por rubro vs presupuesto/promedio histórico.

## Gap vertical real después del piloto

El núcleo analítico mínimo ya existe. Lo que falta es **componer los resultados en una experiencia mensual operativa**.

### Próximo corte recomendado para Consorcios

`SERVICE_1_CONSORCIOS_MONTHLY_RADAR_V1`

Entrada: outcomes gobernados de aging + conciliación + expense variance + case context.

Salida mínima:

- situaciones que requieren atención;
- severidad;
- evidencia;
- estado (`OK`, `REQUIERE_REVISION`, `BLOQUEADO`);
- próxima acción humana;
- vínculo al detalle.

No debe recalcular nada ni crear un segundo motor.

---

# Vertical 3 — Distribuidoras mayoristas

## Núcleo reutilizable ya existente

- vendido vs cobrado;
- DSO / DPO;
- margen neto real;
- stock/reorder point;
- inventory turnover;
- sales concentration;
- caja proyectada;
- expense variance reutilizable conceptualmente;
- conciliación bancaria reutilizable.

## Lo que todavía NO está físicamente probado como vertical

- aging por cliente/factura;
- margen por SKU con descuentos/bonificaciones/comisiones;
- stock inmovilizado por SKU y capital;
- días de cobertura;
- riesgo de quiebre combinando venta + stock + lead time;
- ranking comercial de clientes/SKUs/proveedores.

### Primer corte recomendado para Distribuidoras

`SERVICE_1_DISTRIBUTOR_PILOT_V1`

No implementar funciones primero. Tomar un dataset realista/real con:

`Ventas + Cobranzas + Clientes + Productos + Stock + Costos + Proveedores`

y medir qué cubre el núcleo actual antes de abrir gaps.

---

# Vertical 4 — Sellers Mercado Libre / Mercado Pago

## Núcleo reutilizable ya existente

- margen neto real;
- conciliación Mercado Pago ↔ Banco;
- conciliación bancaria;
- stock/reposición;
- rotación;
- concentración;
- vendido vs cobrado;
- expense variance reutilizable para publicidad/costos si el dato existe.

## Gaps verticales probables que requieren piloto antes de implementar

- margen real por publicación/SKU incorporando comisión, envío, publicidad, retenciones y devoluciones;
- devoluciones y su impacto económico;
- publicidad vs margen generado;
- días de cobertura por SKU;
- fondos pendientes desde venta → MP → banco.

### Primer corte recomendado para Sellers

`SERVICE_1_SELLER_PILOT_V1`

Dataset mínimo:

`Ventas + Publicaciones/SKU + Comisiones + Envíos + Publicidad + Retenciones + Devoluciones + Acreditaciones MP + Banco + Stock + Costos`.

Primero medir cobertura del núcleo existente; implementar sólo gaps demostrados.

---

# Radar de Situación — decisión arquitectónica

El Radar NO es una nueva capacidad de cálculo.

Debe ser una capa de composición sobre resultados ya gobernados:

```text
case context
+ bounded outcomes
+ reconciliation review
+ evidence / provenance
+ severity
+ pending evidence
        ↓
normalización de findings
        ↓
ranking determinístico
        ↓
próxima acción
        ↓
radar vertical
```

Contrato conceptual mínimo de cada item del radar:

- `case_id`
- `vertical`
- `capability_ref`
- `finding_ref`
- `status`
- `severity`
- `entity_ref`
- `period`
- `summary`
- `evidence_refs`
- `requires_human_review`
- `next_action`
- `source_outcome_ref`

El Radar no puede:

- inventar findings;
- cambiar la clasificación del cálculo fuente;
- autorizar ejecución;
- cerrar conciliaciones;
- cerrar contabilidad;
- sustituir evidencia faltante;
- usar LLM como autoridad.

---

# Orden recomendado desde este corte

## Corte 1 — cerrar worktree Consorcios actual

Integrar y publicar conjuntamente:

- `collection_aging`;
- matcher mejorado;
- `expense_variance`;
- tests físicos Cabildo/Rivadavia.

## Corte 2 — `SERVICE_1_FINDING_ENVELOPE_V1`

Crear un contrato transversal pequeño para proyectar outcomes existentes a un formato común de finding, sin recalcular.

## Corte 3 — `SERVICE_1_CONSORCIOS_MONTHLY_RADAR_V1`

Primer radar vertical real usando sólo resultados ya probados.

## Corte 4 — piloto Distribuidoras

Dataset físico antes de nuevas capacidades.

## Corte 5 — piloto Sellers

Dataset físico antes de nuevas capacidades.

## Corte 6 — Contadores multicliente

Composición portfolio/ranking sobre capacidades existentes.

---

# Conclusión

Servicio 1 no necesita decenas de módulos verticales independientes.

La arquitectura que emerge del repo real es:

```text
CANONICAL INGESTION + TENANT SEMANTICS + GOVERNANCE
                    ↓
          TRANSVERSAL CAPABILITIES
                    ↓
             BOUNDED OUTCOMES
                    ↓
          FINDING ENVELOPE COMÚN
                    ↓
              VERTICAL RADAR
```

La próxima inversión estructural correcta no es otra fórmula. Es **normalizar los findings existentes y componerlos en un Radar**, empezando por Consorcios porque ya tiene tres controles físicamente probados sobre dos edificios heterogéneos.
