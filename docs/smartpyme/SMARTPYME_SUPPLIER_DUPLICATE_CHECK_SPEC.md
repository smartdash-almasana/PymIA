# SMARTPYME_SUPPLIER_DUPLICATE_CHECK_SPEC

Estado: IMPLEMENTADO (MVP mínimo)

## Objetivo

Agregar clasificación `supplier_duplicate_check` para analizar maestros de proveedores en Excel.

## Input esperado

Columnas:
- `proveedor` (obligatoria)
- `cuit` (opcional)
- `razon_social` (opcional)

## Reglas de estado

- `PASS`: existe `proveedor` y al menos una de `cuit` o `razon_social`.
- `PARTIAL`: existe `proveedor` pero faltan `cuit` y `razon_social`.
- `BLOCKED`: falta `proveedor`.

## Findings mínimos

- `DUPLICATE_CUIT`
- `MISSING_CUIT`
- `MISSING_RAZON_SOCIAL`
- `NORMALIZATION_NEEDED`
- `LEGAL_SUFFIX_VARIATION`

## Restricciones

- Sin routing `auto`.
- Sin `--html-out`.
- Sin fuzzy avanzado.
- Sin cambios en runtime externo (Hermes/producción).
