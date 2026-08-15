# Servicio 1 — Excel Reality Lab A3 Rubro Matrix V1

**Fecha:** 2026-08-15
**Estado:** LOCAL_PASS
**Prerequisitos:** A0 corpus contract, A1 structural matrix, A2 calculation matrix.

## Objetivo

Medir cómo se comporta el intake semántico seguro de Servicio 1 frente a vocabulario y estructuras representativas de ocho rubros PyME, sin crear reglas de runtime por sector, aliases ad hoc, nuevas capabilities ni nuevos parsers.

A3 no certifica P8, cálculo, delivery ni producción.

## Rubros requeridos

```text
comercio_minorista
mayorista_distribuidora
textil
produccion_fabrica
servicios_profesionales_estudio_contable
gastronomia
administracion_consorcios
mercado_libre_mercado_pago
```

Cobertura observada: **8/8**.

## Resultado

```text
PASS_DETERMINISTIC_UNDERSTANDING: 1
PASS_NEEDS_OWNER: 7
PASS_BLOCKED_FAIL_CLOSED: 0
FAIL_DEFECT: 0
```

El único representante completamente determinístico fue `textil`.

Los otros siete rubros mantuvieron comportamiento seguro: vocabulario no gobernado o ambiguo quedó en owner-confirmation en lugar de recibir equivalencias sectoriales inventadas.

## Evidencia por rubro

### Comercio minorista

Representante: `S1-SYN-002`

Vocabulario reconocido incluye fecha, comprobante, producto, cantidad, precio unitario y venta total. Campos irrelevantes deliberados (`color_favorito`, `nota_gerencia`) permanecen unknown.

Estado: `PASS_NEEDS_OWNER`.

### Mayorista / distribuidora

Representante: `S1-STR-002`

5000 filas. Vocabulario operativo: cantidad, cliente, costo, fecha, margen, ruta, SKU, venta.

`ruta` permanece unknown.

Estado: `PASS_NEEDS_OWNER`.

### Textil

Representante: `S1-STR-003`

2500 filas. Canal, cantidad, costo, descuento, factura, fecha, margen, SKU y venta fueron curados sin unknown/ambiguous.

Estado: `PASS_DETERMINISTIC_UNDERSTANDING`.

### Producción / fábrica

Representante: `S1-STR-004`

3000 filas. Vocabulario observado: fecha, horas, máquina, OEE, operario, orden, scrap, unidades.

`horas`, `maquina`, `oee`, `operario`, `orden` y `scrap` quedan unknown. El contexto no se convierte en semántica productiva automáticamente.

Estado: `PASS_NEEDS_OWNER`.

### Servicios profesionales / estudio contable

Representante incorporado en A3: `S1-RUB-001`, fixture `S1_A1_SYNTH_016_estudio_contable_honorarios.xlsx`.

Vocabulario: cliente, fecha, importe_facturado, servicio.

`importe_facturado` y `servicio` permanecen unknown.

Estado: `PASS_NEEDS_OWNER`.

### Gastronomía

Representante: `S1-STR-001`, `cafeteria_abc.xlsx`.

3 hojas / 5020 filas. Contextos observados: ventas, productos y generic.

El corpus expone vocabulario realista de sucursal, canal, método de pago, empleado, categoría, producto y precio. Los campos no gobernados permanecen owner-safe.

Estado: `PASS_NEEDS_OWNER`.

### Administración de consorcios

Representante: `S1-STR-007`.

7 hojas / 145 filas. Vocabulario amplio: expensas, cobranzas, banco, gastos, presupuesto, unidad funcional, coeficiente, propietario, proveedor, saldos y períodos.

La mayoría de la semántica específica de consorcios no está gobernada todavía; `estado_pago`, `saldo` y `saldo_anterior` aparecen ambiguos.

Estado: `PASS_NEEDS_OWNER`.

### Mercado Libre / Mercado Pago

Representante: `S1-STR-006`.

4 hojas / 84 filas. Aparecen ventas, Mercado Pago, banco y caso esperado; vocabulario de comisión, retención, importes bruto/neto, IDs de operación y movimientos bancarios.

La mayor parte de esa semántica específica permanece unknown; `retencion_total` queda ambiguo.

Estado: `PASS_NEEDS_OWNER`.

## Interpretación

A3 demuestra dos cosas distintas:

1. Servicio 1 no rompe al cambiar de rubro y mantiene fail-safe/owner-safe.
2. La cobertura semántica específica de rubro todavía es desigual.

Esto NO autoriza completar automáticamente los unknowns. Los gaps detectados son evidencia para futuros contratos de vocabulario/capability, no permiso para hardcodear sectores.

## Autoridad

```text
RUBRO != RUNTIME_AUTHORITY
RUBRO != NEW_CAPABILITY
RUBRO != ALIAS_AD_HOC
```

El evaluador A3 usa `curate_xlsx_document` canónico y no importa `openpyxl`, `read_excel`, product root, P8 ni kernel.

## Siguiente gate

```text
EXCEL_REALITY_LAB_A4_ADVERSARIAL_MATRIX_V1
```

Objetivo: someter el pipeline a inputs deliberadamente engañosos —signos invertidos, cero vs vacío, períodos fuera de rango, moneda inconsistente, subtotales, granularidad incompatible y evidencia material ausente— y demostrar bloqueo seguro antes de cálculo engañoso.
