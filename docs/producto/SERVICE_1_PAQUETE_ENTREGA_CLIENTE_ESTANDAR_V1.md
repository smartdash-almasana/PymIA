# SERVICE_1_PAQUETE_ENTREGA_CLIENTE_ESTANDAR_V1

## Estado

```text
DOCUMENT_TYPE: OWNER_FACING_DELIVERY_STANDARD
SERVICE: SERVICE_1_FULL_ASSISTED_V1
STATUS: STANDARD_V1_CLOSED_WITH_LIMITS
RUNTIME_MODIFIED: NO
TESTS_RUN: NO
NEW_XLSX_CREATED: NO
STAGE_6: NO
AGENT_LLM: NO
```

---

# 1. Qué es este documento

Este documento define la estructura estándar del paquete que recibe el cliente al finalizar un Servicio 1.

No define una tool nueva.
No modifica runtime.
No reemplaza el operator delivery package técnico.

Traduce el paquete técnico existente a una entrega clara para dueño PyME, contador aliado o responsable operativo.

---

# 2. Objetivo

Garantizar que cada entrega de Servicio 1 sea:

```text
- repetible;
- entendible por el cliente;
- conservadora;
- trazable;
- revisable por humano;
- explícita sobre límites;
- separada de claims prohibidos;
- útil como trabajo entregado, no como conversación suelta.
```

---

# 3. Principio rector

```text
El cliente no compra un JSON.
El cliente no compra una tool.
El cliente no compra un experimento.
El cliente recibe un paquete de trabajo claro, ordenado y limitado.
```

Regla madre:

```text
Los archivos son el producto.
La IA conversa.
La FSM gobierna.
Las tools ejecutan.
El operador valida.
El cliente recibe claridad operativa con caveats.
```

---

# 4. Carpeta estándar de entrega

Nombre recomendado:

```text
ENTREGA_SERVICIO_1_<CLIENTE>_<FECHA>/
```

Estructura mínima:

```text
ENTREGA_SERVICIO_1_<CLIENTE>_<FECHA>/
├─ 00_LEEME_PRIMERO.md
├─ 01_RESUMEN_DUENO.md
├─ 02_EVIDENCIA_RECIBIDA.md
├─ 03_HALLAZGOS_Y_ALERTAS.md
├─ 04_LIMITES_CAVEATS_Y_NO_ALCANCE.md
├─ 05_PROXIMOS_PEDIDOS.md
├─ 06_PROXIMAS_ACCIONES_SUGERIDAS.md
├─ outputs/
│  ├─ first_aid_001_precio_margen_basico.xlsx
│  ├─ first_aid_002_caja_diaria_triage.xlsx
│  ├─ first_aid_003_stock_alertas_basicas.xlsx
│  ├─ first_aid_004_gastos_triage.xlsx
│  └─ first_aid_005_proveedores_precio_variacion_triage.xlsx
├─ tecnico/
│  ├─ manifest.json
│  ├─ summary.txt
│  └─ operator_report.txt
└─ README_ENTREGA.md
```

Si un caso no incluye todas las capacidades, los archivos ausentes deben declararse en `04_LIMITES_CAVEATS_Y_NO_ALCANCE.md`.

---

# 5. Archivo 00_LEEME_PRIMERO.md

Debe explicar en lenguaje directo:

```text
- qué contiene la entrega;
- qué archivo abrir primero;
- qué significa el resultado;
- qué no debe interpretarse como diagnóstico final;
- que requiere revisión humana;
- que no reemplaza contador, auditoría ni conciliación definitiva.
```

Plantilla mínima:

```text
Esta carpeta contiene una revisión operativa asistida sobre los archivos recibidos.
El objetivo es mostrar hallazgos visibles, faltantes de evidencia y próximos pasos seguros.
No es una auditoría, certificación, conciliación definitiva ni dictamen contable.
```

---

# 6. Archivo 01_RESUMEN_DUENO.md

Debe contener:

```text
- resumen en 10 a 20 líneas;
- estado general: NORMAL / OBSERVAR / ALTERADO / BLOQUEADO;
- 3 a 7 hallazgos principales;
- principales faltantes;
- recomendación operativa inmediata;
- próximos pasos sugeridos.
```

No debe incluir jerga de implementación como:

```text
runtime_authorized
schema_version
tool_ref
Pydantic
manifest hash
pipeline
```

Eso queda en carpeta técnica.

---

# 7. Archivo 02_EVIDENCIA_RECIBIDA.md

Debe listar:

```text
- archivos recibidos;
- hojas analizadas;
- columnas usadas;
- período declarado si existe;
- filas incluidas;
- filas excluidas;
- supuestos humanos;
- datos inferidos con confirmación requerida.
```

Debe separar:

```text
EVIDENCIA_DECLARADA
EVIDENCIA_INFERIDA
EVIDENCIA_FALTANTE
```

---

# 8. Archivo 03_HALLAZGOS_Y_ALERTAS.md

Debe ordenar hallazgos por severidad:

```text
CRITICO
ALTERADO
OBSERVAR
INFORMATIVO
```

Cada hallazgo debe tener:

```text
- título;
- evidencia;
- impacto posible;
- límite de interpretación;
- próximo paso recomendado.
```

Formato obligatorio:

```text
HALLAZGO:
EVIDENCIA:
IMPACTO POSIBLE:
LIMITE:
PROXIMO PASO:
```

---

# 9. Archivo 04_LIMITES_CAVEATS_Y_NO_ALCANCE.md

Debe incluir todos los límites relevantes.

Bloque mínimo obligatorio:

```text
Esta entrega no es auditoría.
Esta entrega no es certificación.
Esta entrega no confirma saldos reales.
Esta entrega no confirma stock físico.
Esta entrega no es conciliación definitiva.
Esta entrega no reemplaza revisión contable.
Esta entrega no reemplaza al contador.
Esta entrega no valida impuestos.
Esta entrega se basa en evidencia recibida y datos declarados.
```

También debe declarar capacidades no usadas:

```text
CAPACIDADES_NO_EJECUTADAS:
- motivo;
- evidencia faltante;
- si puede ejecutarse en una próxima iteración.
```

---

# 10. Archivo 05_PROXIMOS_PEDIDOS.md

Debe pedir evidencia adicional de manera concreta.

Ejemplos:

```text
Para revisar márgenes con más precisión falta lista de costos actualizada.
Para avanzar sobre caja/banco falta extracto bancario del período.
Para revisar stock físico falta inventario contado o reporte de depósito.
Para analizar proveedores falta precio histórico o facturas comparables.
```

Prohibido:

```text
Faltan datos.
Necesitamos más información.
```

Siempre debe decir qué falta y para qué.

---

# 11. Archivo 06_PROXIMAS_ACCIONES_SUGERIDAS.md

Debe proponer acciones seguras, no decisiones definitivas.

Permitido:

```text
- revisar costos faltantes;
- confirmar saldo inicial;
- clasificar egresos sin categoría;
- pedir extracto bancario;
- revisar productos con margen bajo;
- validar stock bajo mínimo;
- preparar próxima corrida con evidencia adicional.
```

Prohibido:

```text
- cambiar precios automáticamente;
- cortar proveedor;
- cerrar contablemente;
- presentar a AFIP;
- tomar decisión financiera definitiva;
- afirmar fraude, pérdida real o error contable sin evidencia.
```

---

# 12. Carpeta outputs/

Contiene los XLSX entregables.

Archivos posibles dentro de Servicio 1 V1:

```text
first_aid_001_precio_margen_basico.xlsx
first_aid_002_caja_diaria_triage.xlsx
first_aid_003_stock_alertas_basicas.xlsx
first_aid_004_gastos_triage.xlsx
first_aid_005_proveedores_precio_variacion_triage.xlsx
```

Cada XLSX debe incluir, cuando aplique:

```text
- Resumen;
- Evidencia declarada;
- Resultados;
- Filas excluidas;
- Faltantes;
- Caveats;
- Revisión humana requerida.
```

---

# 13. Carpeta tecnico/

Contiene artefactos para auditoría interna u operador.

```text
manifest.json
summary.txt
operator_report.txt
```

No debe ser la primera capa de lectura del cliente.

El cliente puede recibirla si se desea transparencia, pero la lectura primaria debe ser owner-facing.

---

# 14. README_ENTREGA.md

Este archivo puede coexistir con `00_LEEME_PRIMERO.md`.

Regla:

```text
README_ENTREGA.md conserva compatibilidad con el delivery package técnico.
00_LEEME_PRIMERO.md es la entrada comercial/humana recomendada.
```

---

# 15. Estados permitidos de entrega

```text
DELIVERED_WITH_CAVEATS
DELIVERED_PARTIAL
NEEDS_MORE_EVIDENCE
BLOCKED_BY_EVIDENCE
INTERNAL_REVIEW_REQUIRED
```

No usar:

```text
CERTIFIED
AUDITED
CONCILIATED
APPROVED
FINAL_ACCOUNTING_RESULT
TAX_READY
```

---

# 16. Checklist mínima pre-entrega

Antes de entregar al cliente:

```text
[ ] Existe 00_LEEME_PRIMERO.md.
[ ] Existe 01_RESUMEN_DUENO.md.
[ ] Evidencia recibida está declarada.
[ ] Evidencia faltante está declarada.
[ ] Cada hallazgo tiene evidencia y límite.
[ ] Claims prohibidos no aparecen.
[ ] Caveats visibles.
[ ] Outputs XLSX están dentro de outputs/.
[ ] Artefactos técnicos están dentro de tecnico/.
[ ] manifest.json existe si hay paquete técnico.
[ ] runtime_authorized=false si corresponde.
[ ] Revisión humana marcada como requerida.
```

---

# 17. Relación con Servicio 1 Full Assisted V1

Este estándar cierra la forma de entrega cliente para V1 asistido.

No cierra V2.
No habilita Stage 6.
No habilita chatbot productivo.
No habilita OCR/PDF productivo.
No habilita APIs bancarias.
No habilita conciliación definitiva.

---

# 18. Decisión

```text
SERVICE_1_OWNER_DELIVERY_PACKAGE_STANDARD: CLOSED_WITH_LIMITS
SERVICE_1_PAQUETE_ENTREGA_CLIENTE_ESTANDAR_V1: ACTIVE
NEXT_PRODUCT_FRONT: QA final de claims prohibidos y caso comercial estrella
```

---

# 19. Cierre

Servicio 1 ya no debe entregar resultados como archivos sueltos ni como reportes técnicos aislados.

Debe entregar un paquete owner-facing estándar, con archivos claros, hallazgos legibles, límites explícitos y próximos pasos seguros.
