# SERVICE_1_PROVEEDORES_PRECIO_VARIACION_TRIAGE_NEXT_FRONT_V1

## Objetivo

Abrir el próximo frente funcional real de Servicio 1 sin deriva documental ni runtime innecesario.

```text
FRONT: proveedores_precio_variacion_triage
TYPE: pilot audit sobre archivos existentes
RUNTIME_DEFAULT: no modificar
NEW_EXCELS: no
STAGE_6: no
PDF_OCR: no
```

---

# 1. Hipótesis operativa

La capacidad existe como tool/test/toolbox, pero no tiene ejecución pilot específica auditada suficiente para declararla cerrada.

Estado conservador actual:

```text
LIMITED_IN_FULL_ASSISTED_V1
```

Estado objetivo posible:

```text
OPERATIONAL_WITH_CAVEATS
```

Sólo si se encuentra evidencia real en archivos existentes.

---

# 2. Archivos candidatos

Buscar únicamente en:

```text
prueba_excels/
```

Priorizar:

```text
- first_aid_pilot_002_lista_precios_costos_demo.xlsx
- distribuidora_mayorista_compleja.xlsx
- cafeteria_abc.xlsx
- constructora_nueva_era_srl.xlsx
- taller_mecanico_lubricar_srl.xlsx
```

No fabricar Excel.

---

# 3. Evidencia mínima requerida

Debe existir mapping razonable para:

```text
- proveedor o equivalente;
- producto / insumo / item;
- precio anterior o precio base;
- precio actual o precio nuevo;
- fecha o período si el contrato lo requiere;
- moneda/unidad si aparece.
```

Si no existe, declarar:

```text
LIMITED_IN_FULL_ASSISTED_V1
```

---

# 4. Criterio de salida

```text
OPERATIONAL_WITH_CAVEATS:
si hay archivo existente compatible, ejecución controlada, outputs locales y auditoría de mapping.

LIMITED_IN_FULL_ASSISTED_V1:
si hay tool/test pero no archivo real compatible suficiente.

BLOCKED_WITH_REASON:
si el contrato runtime exige inputs ausentes o ambiguos.
```

---

# 5. No hacer

```text
- no modificar runtime;
- no inventar columnas;
- no inferir proveedor desde texto libre débil;
- no prometer análisis de compras integral;
- no prometer negociación con proveedores;
- no prometer contabilidad de costos completa;
- no commitear outputs locales.
```
