# SERVICE_1_POST_TOOL_OWNER_DELIVERY_SUMMARY_V1

## Estado

```text
DOCUMENT_TYPE: FRONT_SPEC
SERVICE: S1_FULL_ASSISTED_V1
FRONT: SERVICE_1_POST_TOOL_OWNER_DELIVERY_SUMMARY_V1
STATUS: IMPLEMENTED_AND_TESTED
SOURCE_REVIEW: SERVICE_1_SYNTHETIC_DELIVERY_LLM_REVIEW_V1
RUNTIME_SCOPE: OUTPUT_SYNTHESIS_ONLY
NEW_TOOLS: NO
NEW_CALCULATIONS: NO
S2_TOUCHED_ALLOWED: NO
STAGE_6_ALLOWED: NO
API_ALLOWED: NO
OCR_PDF_ALLOWED: NO
```

---

# 1. Objetivo

Crear una salida markdown final para el dueño después de ejecutar tools First Aid.

El problema detectado en la revisión LLM no está en el pipeline técnico. Está en que `owner_message.md` y `README.txt` siguen reflejando fase de intake, aunque ya existen resultados First Aid y XLSX generados.

Este frente debe producir una síntesis final post-tools, alineada con:

```text
docs/producto/SERVICE_1_OWNER_FACING_DELIVERY_TEMPLATE_V1.md
```

---

# 2. Input permitido

```text
pipeline_result.json
detected_structure.json
operator_packet.json / case_delivery_manifest
```

No debe leer ni reinterpretar el XLSX original.

---

# 3. Output esperado

Archivo markdown owner-facing, por ejemplo:

```text
first_aid_owner_delivery_summary.md
```

Contenido mínimo:

```text
1. Resumen ejecutivo.
2. Archivo revisado.
3. Alcance de la revisión.
4. Hojas detectadas relevantes.
5. Herramientas aplicadas.
6. Resultados OK / MISSING_INPUTS / INVALID_INPUT.
7. Faltantes explícitos.
8. Archivos XLSX entregados.
9. Límites de la entrega.
10. Próxima acción humana sugerida.
```

---

# 4. Caso sintético de referencia

```text
CASE_ID: case_asset_8742e876409b
INPUT_FILE: SERVICE_1_SYNTHETIC_CASE_001_CAFETERIA_CASH_MARGIN.xlsx
TOOLS_EXECUTED: 9
TOOL_STATUS: 8 OK / 1 MISSING_INPUTS
MISSING_INPUT: costo_unitario
XLSX_OUTPUTS: 9
QA_GATE: PASS
RUNTIME_AUTHORIZED: false
```

---

# 5. Reglas de lenguaje

Permitido:

```text
- revisión inicial;
- cálculo preliminar;
- según los datos declarados;
- requiere revisión humana;
- faltante detectado;
- archivos generados para revisión;
- no se pudo calcular por falta de dato.
```

Prohibido:

```text
- auditoría;
- certificación;
- rentabilidad real confirmada;
- conciliación cerrada;
- saldo real confirmado;
- cierre contable;
- cierre fiscal;
- reemplazo del contador;
- diagnóstico integral.
```

---

# 6. DoD

```text
[ ] Produce markdown final post-tools.
[ ] No contradice pipeline_result.
[ ] Lista 9 XLSX entregados.
[ ] Explica 8 OK / 1 MISSING_INPUTS.
[ ] Explica faltante costo_unitario.
[ ] Mantiene runtime_authorized=false.
[ ] No toca S2.
[ ] No crea cálculos nuevos.
[ ] No abre Stage 6.
[ ] No incluye claims prohibidos.
```

---

# 7. Próximo paso

```text
NEXT_ACTION: implement pure owner-facing summary generator or patch existing operator delivery output to emit final post-tool markdown.
```
