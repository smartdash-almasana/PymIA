# SERVICE_1_PROVEEDORES_PRECIO_VARIACION_TRIAGE_NEXT_FRONT_V1

## Estado

```text
STATUS: CLOSED_AS_OPERATIONAL_WITH_CAVEATS
FRONT: proveedores_precio_variacion_triage
RUNTIME_MODIFIED: NO
NEW_EXCELS: NO
STAGE_6: NO
```

---

# 1. Resultado

El frente fue ejecutado sobre archivo existente.

```text
SOURCE_FILE: prueba_excels/constructora_nueva_era_srl.xlsx
SHEET: PROVEEDORES_MATERIALES
ROWS_INCLUDED: 30
ROWS_EXCLUDED: 0
RUNTIME_STATUS: OK
```

---

# 2. Mapping auditado

```text
proveedor -> proveedor
producto_o_insumo -> producto
precio_o_costo -> precio_unitario_real
```

---

# 3. Caveats

```text
- usa precio_unitario_real como precio_o_costo;
- no calcula variación precio_unitario_presupuestado vs precio_unitario_real bajo contrato runtime actual;
- sólo detecta variación visible entre registros del mismo producto;
- no define estrategia de compras;
- no confirma rentabilidad por proveedor;
- no recomienda compra final;
- no audita proveedores;
- no reemplaza revisión comercial ni contable.
```

---

# 4. Decisión

```text
CAPABILITY_STATUS: OPERATIONAL_WITH_CAVEATS
MATRIX_UPDATE: DONE
LOCAL_OUTPUTS: prueba_excels/SERVICE_1_PROVEEDORES_PRECIO_VARIACION_RUN_OUTPUT/
COMMIT_OUTPUTS: NO
```

---

# 5. Próximo frente

```text
NEXT_FRONT: choose between caja_diaria POR_FECHA or Excel Factory catalog
```
