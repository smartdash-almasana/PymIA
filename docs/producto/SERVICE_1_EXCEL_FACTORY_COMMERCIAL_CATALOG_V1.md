# SERVICE_1_EXCEL_FACTORY_COMMERCIAL_CATALOG_V1

## Estado

```text
DOCUMENT_TYPE: COMMERCIAL_CATALOG
SERVICE: SERVICE_1_FULL_ASSISTED_V1
FRONT: Excel Factory catalog
STATUS: V1_INITIAL_CATALOG_CLOSED_WITH_LIMITS
RUNTIME_MODIFIED: NO
TESTS_RUN: NO
NEW_XLSX_CREATED: NO
STAGE_6: NO
AGENT_LLM: NO
```

---

# 1. Objetivo

Cerrar el catálogo comercial inicial de Excel Factory para Servicio 1 Full Assisted V1.

Este documento no crea runtime, no crea templates nuevos y no habilita generación autónoma de Excel. Su función es convertir capacidades existentes en una superficie comercial repetible, vendible y gobernada.

---

# 2. Definición comercial

Excel Factory, dentro de Servicio 1 V1, significa:

```text
familia de entregables XLSX asistidos, generados o preparados bajo operación humana,
con fórmulas, estructura de revisión, evidencia declarada, caveats y límites explícitos.
```

No significa:

```text
- fábrica autónoma de Excels;
- generación libre por IA;
- ExcelSpec productivo sin arnés;
- templates ilimitados;
- reemplazo de contador;
- conciliación definitiva;
- auditoría;
- ERP;
- SaaS self-service.
```

---

# 3. Principio rector

```text
Los archivos son el producto.
La IA conversa.
La FSM gobierna.
Las tools ejecutan.
El operador valida.
```

Excel Factory V1 debe entregar archivos útiles, pero no debe vender autonomía.

---

# 4. Catálogo IN_SCOPE_V1

## 4.1 Plantilla / entregable: Precios, costos y márgenes

```text
CATALOG_ID: EF_S1_001
COMMERCIAL_NAME: Revisión Excel de precios, costos y márgenes
STATUS: IN_SCOPE_V1
PRIMARY_CAPABILITY: precio_margen_basico
PACKAGE_FIT: Starter / Operativo
```

### Para qué sirve

```text
Detectar productos sin costo, márgenes básicos visibles, precios problemáticos y faltantes mínimos para revisar rentabilidad comercial preliminar.
```

### Inputs esperados

```text
- XLSX/CSV de productos, precios y costos;
- columnas equivalentes a producto, precio_venta, costo_unitario;
- período o lista vigente si aplica.
```

### Output entregable

```text
- XLSX operativo de revisión;
- hoja de resumen;
- hoja de productos revisados;
- hallazgos de margen;
- faltantes de costo/precio;
- caveats y próximos pedidos.
```

### Caveats

```text
- no confirma rentabilidad real integral;
- no incluye impuestos, logística, financiación ni descuentos no declarados salvo evidencia explícita;
- no reemplaza análisis contable;
- no decide precios finales.
```

---

## 4.2 Plantilla / entregable: Caja diaria preliminar

```text
CATALOG_ID: EF_S1_002
COMMERCIAL_NAME: Revisión Excel de caja diaria
STATUS: IN_SCOPE_V1_WITH_CAVEATS
PRIMARY_CAPABILITY: caja_diaria_triage
PACKAGE_FIT: Operativo / Contador aliado
```

### Para qué sirve

```text
Calcular flujo preliminar de caja sobre saldo inicial, ingresos y egresos declarados, en modo agregado o por fecha bajo operación externa del operador.
```

### Inputs esperados

```text
- XLSX/CSV de movimientos de caja;
- saldo inicial declarado o inferible con confirmación humana;
- ingresos declarados;
- egresos declarados;
- fecha si se usa modo POR_FECHA.
```

### Output entregable

```text
- XLSX operativo de caja;
- resumen de saldo inicial, ingresos, egresos y saldo estimado;
- vista por fecha si aplica;
- filas excluidas o inválidas;
- advertencias operativas;
- caveats de no conciliación.
```

### Caveats

```text
- no confirma saldo bancario real;
- no equivale a conciliación bancaria;
- no valida efectivo físico;
- no incluye movimientos no declarados;
- no reemplaza revisión contable;
- POR_FECHA es agrupación externa del operador, no contrato runtime nuevo.
```

---

## 4.3 Plantilla / entregable: Stock mínimo y alertas básicas

```text
CATALOG_ID: EF_S1_003
COMMERCIAL_NAME: Revisión Excel de stock y alertas básicas
STATUS: IN_SCOPE_V1_WITH_CAVEATS
PRIMARY_CAPABILITY: stock_alertas_basicas
PACKAGE_FIT: Starter / Operativo
```

### Para qué sirve

```text
Detectar productos con stock bajo o faltantes visibles respecto de umbrales declarados.
```

### Inputs esperados

```text
- XLSX/CSV de inventario;
- producto o SKU;
- stock_actual;
- stock_minimo o umbral equivalente.
```

### Output entregable

```text
- XLSX operativo de stock;
- productos bajo mínimo;
- productos sin umbral;
- alertas visibles;
- próximos pedidos de evidencia.
```

### Caveats

```text
- no confirma stock físico real;
- no reemplaza inventario;
- no confirma merma, robo ni ajuste definitivo;
- depende de la calidad del archivo fuente.
```

---

## 4.4 Plantilla / entregable: Gastos preliminares

```text
CATALOG_ID: EF_S1_004
COMMERCIAL_NAME: Revisión Excel de gastos declarados
STATUS: IN_SCOPE_V1_WITH_CAVEATS
PRIMARY_CAPABILITY: gastos_triage
PACKAGE_FIT: Operativo / Contador aliado
```

### Para qué sirve

```text
Ordenar egresos positivos explícitos y producir una lectura preliminar de gastos declarados.
```

### Inputs esperados

```text
- XLSX/CSV de movimientos o gastos;
- concepto o descripción;
- importe;
- categoría si existe.
```

### Output entregable

```text
- XLSX operativo de gastos;
- total preliminar de gastos incluidos;
- filas excluidas;
- categorías declaradas o sin categoría;
- caveats de clasificación.
```

### Caveats

```text
- no clasifica fiscal ni contablemente de forma definitiva;
- no transforma egresos negativos con abs() salvo regla aprobada;
- no reemplaza revisión de contador;
- no confirma deducibilidad ni imputación contable.
```

---

## 4.5 Plantilla / entregable: Proveedores y variación visible de precios

```text
CATALOG_ID: EF_S1_005
COMMERCIAL_NAME: Revisión Excel de proveedores y variaciones visibles
STATUS: IN_SCOPE_V1_WITH_CAVEATS
PRIMARY_CAPABILITY: proveedores_precio_variacion_triage
PACKAGE_FIT: Operativo / Contador aliado
```

### Para qué sirve

```text
Detectar variaciones visibles de precio/costo por producto o insumo según datos declarados de proveedores.
```

### Inputs esperados

```text
- XLSX/CSV de proveedores, productos o insumos;
- proveedor;
- producto_o_insumo;
- precio_o_costo disponible;
- período o registros comparables si existen.
```

### Output entregable

```text
- XLSX operativo de proveedores;
- productos con variación visible;
- registros incluidos/excluidos;
- evidencia de precios usados;
- próximos pedidos para análisis más profundo.
```

### Caveats

```text
- no define estrategia de compras;
- no confirma proveedor óptimo;
- no audita proveedores;
- no reemplaza análisis comercial ni contable;
- si se usa precio_unitario_real como precio_o_costo, debe declararse explícitamente.
```

---

# 5. DEFERRED_V2

Quedan fuera de Excel Factory V1:

```text
- generación autónoma de templates por agente LLM;
- ExcelSpec productivo sin arnés;
- parser PDF/OCR productivo;
- APIs bancarias o Mercado Pago;
- conciliación bancaria definitiva;
- papeles de trabajo contables completos;
- IVA/IIBB;
- asientos automáticos;
- dashboards vivos;
- plantillas ilimitadas por demanda libre;
- fórmulas de Servicio 2 o diagnóstico profundo.
```

---

# 6. Paquetes comerciales sugeridos

## 6.1 Starter

```text
Cliente: dueño PyME con archivo simple.
Incluye:
- precios/costos/márgenes básicos;
- stock mínimo y alertas básicas;
- owner summary;
- caveats.
No incluye:
- caja/banco;
- gastos complejos;
- proveedor profundo;
- revisión contable.
```

## 6.2 Operativo

```text
Cliente: PyME con operación activa y varios archivos.
Incluye:
- precios/costos/márgenes;
- caja diaria preliminar;
- gastos preliminares;
- stock básico;
- proveedores con variación visible;
- paquete de entrega con README, manifest y límites.
No incluye:
- conciliación definitiva;
- auditoría;
- automatización productiva.
```

## 6.3 Contador aliado

```text
Cliente: contador o estudio que necesita ordenar evidencia operativa del cliente.
Incluye:
- caja diaria preliminar;
- gastos declarados;
- proveedores;
- archivos de revisión con caveats;
- faltantes de evidencia;
- paquete de trabajo para revisión humana.
No incluye:
- dictamen;
- liquidación fiscal;
- asientos definitivos;
- papeles de trabajo completos V2.
```

---

# 7. Reglas de entrega

Cada entregable Excel Factory V1 debe incluir:

```text
- nombre del caso;
- fuente de datos;
- fecha de generación;
- columnas usadas;
- filas incluidas;
- filas excluidas;
- hallazgos;
- faltantes;
- caveats;
- claims prohibidos;
- revisión humana requerida.
```

---

# 8. Claims prohibidos generales

No afirmar:

```text
- auditoría final;
- conciliación cerrada;
- saldo real confirmado;
- stock físico confirmado;
- rentabilidad real integral;
- decisión comercial automática;
- reemplazo del contador;
- cumplimiento fiscal;
- diagnóstico integral de la empresa;
- autonomía IA productiva.
```

---

# 9. Decisión de cierre

```text
EXCEL_FACTORY_CATALOG_V1: CLOSED_WITH_LIMITS
SERVICE_1_FULL_ASSISTED_V1_IMPACT: POSITIVE
RUNTIME_REQUIRED: NO
NEXT_PRODUCT_FRONT: owner-facing delivery package standardization
```

Excel Factory V1 queda cerrada como catálogo comercial inicial para Servicio 1 Full Assisted V1.

El catálogo habilita venta asistida, no autonomía.
