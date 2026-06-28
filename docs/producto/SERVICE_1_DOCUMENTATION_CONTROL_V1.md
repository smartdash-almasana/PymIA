# SERVICE_1_DOCUMENTATION_CONTROL_V1

## Propósito

Reducir deriva documental de Servicio 1.

Este archivo define qué documentos son rectores, cuáles son anexos y qué documentos de frente funcional pueden existir sólo como instrumentos transitorios de trabajo.

---

# 1. Documentos rectores

```text
KEEP_AS_CORE:
- docs/producto/SERVICE_1_FULL_ASSISTED_V1_CLOSEOUT_DECLARATION.md
- docs/producto/SERVICE_1_CAPABILITY_COMPLETION_MATRIX_V1.md
- docs/producto/SERVICE_1_FULL_OPERATOR_PLAYBOOK_V1.md
- docs/producto/SERVICE_1_OWNER_FACING_DELIVERY_TEMPLATE_V1.md
- docs/producto/SERVICE_1_QA_DELIVERY_CHECKLIST_V1.md
```

Uso:

```text
- closeout: veredicto maestro;
- matriz: estado vivo de capacidades;
- playbook: operación humana;
- owner template: entrega al dueño;
- QA checklist: gate previo a entrega.
```

---

# 2. Anexos técnicos

```text
KEEP_AS_APPENDIX:
- docs/producto/SERVICE_1_DELIVERY_MANIFEST_AUDIT_V1.md
- docs/producto/SERVICE_1_OPERATOR_DELIVERY_PACKAGE_BLOCK_V1.md
- docs/producto/SERVICE_1_SYNTHETIC_XLSX_EDGE_CASE_RUN_V2.md
- docs/producto/PYMIA_SERVICE_1_FULL_CATALOG_V1.md
```

No deben convertirse en nuevos centros de decisión.

---

# 3. Documentos transitorios de frente funcional

```text
CLOSED_FRONT_DOCS:
- docs/producto/SERVICE_1_PROVEEDORES_PRECIO_VARIACION_TRIAGE_NEXT_FRONT_V1.md
- docs/producto/SERVICE_1_CAJA_DIARIA_POR_FECHA_CLOSEOUT_V1.md
```

Regla:

```text
Deben cerrarse, absorberse en la matriz o archivarse cuando el frente termine.
```

---

# 4. Regla para nueva documentación

No crear documentos nuevos salvo que cumplan una de estas condiciones:

```text
- cierre maestro;
- actualización de matriz;
- closeout de ejecución auditada;
- contrato operativo necesario;
- entrega owner-facing concreta;
- QA/checklist necesario;
- frente funcional transitorio con fecha de cierre.
```

Prohibido:

```text
- roadmaps paralelos;
- manifiestos repetidos;
- ofertas comerciales antes de cerrar evidencia;
- docs aspiracionales sobre capacidades no probadas;
- duplicar nombres para la misma cosa.
```

---

# 5. Próxima prioridad

```text
NEXT_PRIORITY: funciones faltantes reales
CURRENT_FUNCTIONAL_FRONT: Excel Factory catalog
```

La documentación debe seguir a la evidencia, no al revés.
