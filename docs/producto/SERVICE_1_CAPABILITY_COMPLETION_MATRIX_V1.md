# SERVICE_1_CAPABILITY_COMPLETION_MATRIX_V1

## Estado

```text
STATUS: CONTROL_MATRIX_V1
SCOPE: Servicio 1 / First Aid / Laboratorio Operacional Asistido
SOURCE_OF_TRUTH: runtime observado + smoke existing excels + playbook versionado
PLAYBOOK: docs/producto/SERVICE_1_FULL_OPERATOR_PLAYBOOK_V1.md
STAGE_6: no habilitado
AUTONOMIA: no
COMMIT_READY: pending review
```

---

# 1. Propósito

Esta matriz es el tablero maestro para completar **Servicio 1** sin volver al caos operativo.

Debe responder, sin discusión nueva en cada ciclo:

```text
- qué capacidades están cerradas;
- qué capacidades están operativas pero frágiles;
- qué capacidades están parciales;
- qué gaps bloquean Servicio 1 full;
- qué queda explícitamente fuera de alcance.
```

Regla madre:

```text
La IA conversa.
La FSM gobierna.
Las tools ejecutan.
Los archivos son el producto.
```

---

# 2. Leyenda de estados

```text
CLOSED:
Capacidad ejecutada y demostrable con outputs suficientes. Puede usarse en operación asistida.

OPERATIONAL_WITH_CAVEATS:
Capacidad operativa, pero sensible a calidad de datos, mapping o formato del archivo.

PARTIAL:
Hay evidencia de intake, mapping o ejecución parcial, pero falta cierre operativo claro.

DESIGN_ONLY:
Existe diseño o documentación, pero no debe venderse como runtime operativo.

DEFERRED:
Diferido por decisión explícita. No abrir sin autorización.

OUT_OF_SCOPE:
No pertenece al alcance actual de Servicio 1 First Aid.

UNKNOWN:
No hay evidencia suficiente.
```

---

# 3. Matriz de capacidades principales

| Capacidad / familia | Estado | Evidencia actual | Gap real | Próxima acción mínima | Bloquea Servicio 1 full |
|---|---:|---|---|---|---:|
| Intake XLSX | CLOSED | Archivos existentes soportados: cafeteria_abc, distribuidora, textil, pilots, ventas/cobros | Ninguno crítico | Mantener bajo playbook | No |
| Intake CSV | CLOSED | Stage 5 cerrado con CSV intake + router común | Falta uso comercial recurrente | No abrir nuevo frente | No |
| NormalizedTableV1 | CLOSED_BOUNDARY_ONLY | Stage 5 cerrado; router común operativo | Sin consumidor downstream autorizado | No abrir Stage 6 | No, mientras operación sea asistida |
| PDF intake | DEFERRED | Runtime devuelve PDF_INTAKE_DEFERRED | OCR/PDF no productivo | Mantener diferido | No para Servicio 1 inicial |
| Unsupported file handling | CLOSED | UNSUPPORTED_FILE_TYPE / unsupported scopes observados | Ninguno crítico | Mantener guardrail | No |
| Detección de estructura | CLOSED | detected_structure.json generado en casos reales/sintéticos | Puede requerir lectura humana | Usar playbook | No |
| Column confirmation packet | CLOSED | column_confirmation_packet.json generado | No es UI final | Usar como artifact operador | No |
| Operator packet | CLOSED | operator_packet.json generado | Revisión humana obligatoria | Mantener | No |
| Delivery package | CLOSED_WITH_LIMITS | Paquete técnico existente + estándar cliente creado en `SERVICE_1_PAQUETE_ENTREGA_CLIENTE_ESTANDAR_V1.md` | Requiere ensayo operativo con caso comercial antes de declarar cierre final | Usar estructura owner-facing estándar: LEEME, resumen, evidencia, hallazgos, límites, próximos pedidos, próximas acciones, outputs y técnico | No |
| QA gate | CLOSED | QA 12/12 en demo cafeteria_abc | No cubre todas las familias | Mantener como gate | No |
| owner_message.md | CLOSED | Generado en demo y flows previos | Ajuste de tono comercial futuro | Mantener guardrails | No |
| precio_margen_basico | CLOSED | cafeteria_abc: 15/15 OK; distribuidora sample 10/10 OK; pilot_002 7 OK + 2 INVALID por datos | Ninguno runtime; sólo calidad de datos | Usar como familia estrella | No |
| stock_alertas_basicas | OPERATIONAL_WITH_CAVEATS | Smoke existente indica operación/mapeo sobre pilotos; playbook lo marca operativo con caveats | Requiere controlar calidad de inputs y mapping | Ejecutar sólo bajo playbook, sin ceremonia extra | No, pero afecta amplitud full |
| caja_diaria_triage | OPERATIONAL_WITH_CAVEATS | pilot_004 auditado: `Caja_Banco`; modo AGREGADO OK y modo POR_FECHA OK como agrupación externa del operador; POR_FECHA ejecutó 15 fechas, saldo_inicial=6000.0, saldo_final_estimado=59830.0, 3 filas excluidas | MOV-016 requiere caveat: saldo inicial interpretado por descripción, no por `Tipo movimiento`; POR_FECHA no cambia contrato runtime, no confirma saldo real ni conciliación | Usar bajo contrato actual saldo_inicial/ingresos/egresos, con confirmación humana del saldo inicial; POR_FECHA debe documentar fecha y filas fuente fuera del payload runtime | No |
| gastos_triage | OPERATIONAL_WITH_CAVEATS | pilot_004 auditado: `Caja_Banco`, `Descripción` -> concepto, `Importe declarado` -> importe; 5 movimientos incluidos, 15 excluidos, total_gastos 35070.0; runtime_authorized false | Sólo egresos positivos explícitos; categoría ausente cae a `sin_categoria`; egresos negativos no se convierten con `abs()`; no es conciliación, auditoría ni clasificación contable/fiscal | Usar bajo playbook con mapping explícito y outputs locales no commiteables | No |
| proveedores_precio_variacion_triage | OPERATIONAL_WITH_CAVEATS | constructora_nueva_era_srl.xlsx auditado: hoja `PROVEEDORES_MATERIALES`, 30 filas incluidas, 0 excluidas; mapping `proveedor` -> proveedor, `producto` -> producto_o_insumo, `precio_unitario_real` -> precio_o_costo; runtime OK | Caveat: usa `precio_unitario_real` como precio_o_costo; no calcula variación presupuestado vs real bajo contrato runtime actual; sólo detecta variación visible entre registros del mismo producto | Usar bajo playbook con caveat explícito; no prometer estrategia de compras ni auditoría de proveedores | No |
| Conciliación caja/banco definitiva | OUT_OF_SCOPE | Guardrails explícitos | No pertenece al runtime actual | No prometer | No, si oferta dice triage |
| Contabilidad fiscal / IVA / IIBB | OUT_OF_SCOPE | Guardrails explícitos | No pertenece a S1 actual | No prometer | No |
| APIs bancarias / Mercado Pago / ML | DEFERRED | Guardrails explícitos | No runtime | Mantener fuera | No |
| Chatbot productivo | DEFERRED | Regla: IA conversa, FSM gobierna, tools ejecutan | Falta arnés productivo | No abrir ahora | No para servicio asistido |
| Stage 6 auto-routing | DEFERRED | Technical certainty low; no consumer recomendado | Sin consumidor técnico real | No abrir | No |
| Producción industrial KPI | OUT_OF_SCOPE | fabrica_industrial_compleja unsupported | No First Aid actual | Registrar gap futuro | No |
| Excel Factory descargables | CLOSED_WITH_LIMITS | Catálogo comercial inicial creado en `SERVICE_1_EXCEL_FACTORY_COMMERCIAL_CATALOG_V1.md`; 5 entregables XLSX asistidos IN_SCOPE_V1 con caveats | No habilita generación autónoma ni ExcelSpec productivo; costos/Servicio 2 quedan fuera | Conectar a paquetes vendibles, no a runtime nuevo | No |
| Casos demo vendibles | PARTIAL | cafeteria_abc demo ready; synthetic case closed local | Falta paquete comercial mínimo | Preparar 1 muestra owner-facing | Sí parcial |

## 3.1 Evidencia auditada: gastos_triage / pilot_004

```text
AUDIT_VERDICT: PASS_REPORTED_BY_CODEX_IS_VALID
CAPABILITY_STATUS_RECOMMENDED: OPERATIONAL_WITH_CAVEATS
SOURCE_FILE: prueba_excels/first_aid_pilot_004_cash_bank_reconciliation_demo.xlsx
SHEET: Caja_Banco
MAPPING: concepto -> Descripción; importe -> Importe declarado
FILTER: Tipo movimiento == Egreso AND Importe declarado numérico AND >= 0
INCLUDED_MOVEMENTS: 5
EXCLUDED_MOVEMENTS: 15
TOTAL_GASTOS: 35070.0
CATEGORY_BEHAVIOR: categoría ausente -> sin_categoria
NEGATIVE_EXPENSE_RULE: MOV-005 excluido por importe negativo; no aplicar abs()
RUNTIME_MODIFIED: NO
RUNTIME_AUTHORIZED: false
LOCAL_OUTPUTS: generados localmente; no commiteables
```

Caveats operativos:

```text
- sólo egresos positivos explícitos;
- categoría ausente cae a sin_categoria;
- egresos negativos no se convierten con abs();
- no es conciliación bancaria;
- no es auditoría;
- no es clasificación contable/fiscal.
```

## 3.2 Evidencia auditada: caja_diaria_triage / pilot_004

```text
AUDIT_VERDICT: PASS_REPORTED_IS_VALID_WITH_CAVEAT
CAPABILITY_STATUS_RECOMMENDED: OPERATIONAL_WITH_CAVEATS
SOURCE_FILE: prueba_excels/first_aid_pilot_004_cash_bank_reconciliation_demo.xlsx
SHEET: Caja_Banco
MODE: AGREGADO
CONTRACT: saldo_inicial + ingresos + egresos
SALDO_INICIAL: 6000.0
SALDO_SOURCE: MOV-016 / Descripción = Ajuste saldo inicial anterior / Tipo movimiento = Ingreso
INGRESOS: 88900.0
EGRESOS: 35070.0
FLUJO_NETO: 53830.0
SALDO_FINAL_ESTIMADO: 59830.0
RUNTIME_STATUS: OK
RUNTIME_MODIFIED: NO
RUNTIME_AUTHORIZED: false
LOCAL_OUTPUTS: generados localmente; no commiteables
```

Caveats operativos:

```text
- MOV-016 se usa como saldo_inicial por interpretación de descripción, no por tipo_movimiento;
- requiere confirmación humana del operador/cliente;
- si MOV-016 fuera ingreso ordinario, cambiarían ingresos y saldo final;
- modo AGREGADO validado bajo contrato runtime actual;
- modo POR_FECHA queda validado como operación externa del operador, sin cambio de contrato runtime;
- no es conciliación bancaria;
- no es auditoría;
- no valida efectivo físico;
- no reemplaza revisión contable.
```

## 3.3 Evidencia auditada: caja_diaria_triage POR_FECHA / pilot_004

```text
AUDIT_VERDICT: PASS_WITH_CAVEATS
CAPABILITY_STATUS_RECOMMENDED: OPERATIONAL_WITH_CAVEATS
SOURCE_FILE: prueba_excels/first_aid_pilot_004_cash_bank_reconciliation_demo.xlsx
SHEET: Caja_Banco
MODE: POR_FECHA
RUNTIME_CONTRACT: unchanged; saldo_inicial, ingresos, egresos
DATES_EXECUTED: 15
SALDO_INICIAL_DETECTED: 6000.0
SALDO_FINAL_ESTIMADO: 59830.0
EXCLUDED_ROWS: 3
RUNTIME_STATUS: OK
RUNTIME_MODIFIED: NO
RUNTIME_AUTHORIZED: false
LOCAL_OUTPUTS: generados localmente; no commiteables
```

Caveats operativos:

```text
- POR_FECHA es agrupación externa del operador, no contrato runtime nuevo;
- cada fecha se ejecuta como una tool_request separada con saldo rodante;
- fecha y filas fuente deben documentarse fuera del payload runtime;
- MOV-016 sigue interpretado como saldo inicial por descripción;
- no confirma saldo bancario real;
- no equivale a conciliación;
- no valida efectivo físico;
- no incluye movimientos no declarados;
- no reemplaza revisión contable.
```

---

## 3.4 Evidencia auditada: proveedores_precio_variacion_triage / constructora_nueva_era_srl

```text
AUDIT_VERDICT: PASS_WITH_CAVEATS
CAPABILITY_STATUS_RECOMMENDED: OPERATIONAL_WITH_CAVEATS
SOURCE_FILE: prueba_excels/constructora_nueva_era_srl.xlsx
SHEET: PROVEEDORES_MATERIALES
MAPPING: proveedor -> proveedor; producto_o_insumo -> producto; precio_o_costo -> precio_unitario_real
INCLUDED_ROWS: 30
EXCLUDED_ROWS: 0
RUNTIME_STATUS: OK
RUNTIME_MODIFIED: NO
RUNTIME_AUTHORIZED: false
LOCAL_OUTPUTS: generados localmente; no commiteables
```

Caveats operativos:

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

# 4. Capacidades cerradas para operar ya

Servicio 1 ya puede operar de forma asistida en este núcleo:

```text
- recibir XLSX/CSV;
- ejecutar intake;
- detectar hojas y columnas;
- confirmar estructura;
- armar tool_requests explícitas;
- ejecutar tools allowlisted;
- generar XLSX outputs;
- generar owner_message;
- generar operator_packet;
- aplicar QA/delivery guardrails;
- bloquear sin alucinar cuando falta evidencia.
```

Familia más fuerte:

```text
precio_margen_basico
```

Uso comercial recomendado actual:

```text
Primeros Auxilios Excel para precios, costos, márgenes y señales operativas básicas sobre archivos declarados por la PyME.
```

No vender como:

```text
Servicio contable integral,
auditoría,
conciliación definitiva,
diagnóstico autónomo,
automatización fiscal,
chatbot productivo.
```

---

# 5. Gaps que sí importan para Servicio 1 full

| Gap ID | Gap | Tipo | Prioridad | Responsable sugerido | Bloquea venta inicial | Bloquea full |
|---|---|---|---:|---|---:|---:|
| GAP-001 | Paquete comercial owner-facing mínimo no consolidado | producto | Alta | GPT + operador | Sí parcial | Sí |
| GAP-002 | RESOLVED: gastos_triage tiene cierre operativo auditado sobre pilot_004 con caveats explícitos | operación | Cerrada | Codex | No | No |
| GAP-003 | RESOLVED_WITH_CAVEATS: caja_diaria_triage tiene modo AGREGADO validado y modo POR_FECHA validado como operación externa sin cambiar contrato runtime | operación | Cerrada | GPT/MCP-local | No | No |
| GAP-004 | RESOLVED: proveedores_precio_variacion_triage tiene ejecución auditada sobre archivo existente con caveats de contrato | evidencia | Cerrada | GPT/MCP-local | No | No |
| GAP-005 | RESOLVED_WITH_LIMITS: Excel Factory expresada como catálogo comercial inicial V1; autonomía y ExcelSpec productivo quedan diferidos | producto | Cerrada | GPT/MCP-local | No | No |
| GAP-006 | RESOLVED_WITH_LIMITS: paquete de entrega cliente estandarizado; falta ensayo sobre caso comercial estrella antes de cierre final | producto | Cerrada | GPT/MCP-local | No | No |
| GAP-007 | Backlog de archivos existentes sin clasificación final | orden operativo | Media | GPT/DeepSeek | No | Parcial |
| GAP-008 | Chatbot/FSM productiva pendiente | producto futuro | Baja ahora | No abrir | No | No para S1 asistido |
| GAP-009 | PDF/OCR pendiente | futuro | Baja ahora | No abrir | No | No para S1 asistido |
| GAP-010 | Stage 6 sin consumidor | arquitectura | Baja ahora | No abrir | No | No |

---

# 6. Orden de cierre recomendado

No avanzar por curiosidad. Cerrar en este orden:

```text
1. Paquete comercial owner-facing mínimo.
2. Delivery template estándar.
3. caja_diaria_triage bajo contrato actual.
4. proveedores_precio_variacion_triage sólo si hay archivo existente calzante.
5. Excel Factory catálogo comercial inicial cerrado con límites.
```

Prohibido en esta fase:

```text
- inventar nuevos Excel;
- abrir Stage 6;
- crear mapeo automático universal;
- convertir cada ejecución en auditoría triple;
- commitear outputs locales;
- prometer Servicio 1 full antes de cerrar gaps críticos.
```

---

# 7. Criterio para declarar Servicio 1 full asistido

Servicio 1 puede declararse **FULL ASSISTED V1** cuando estén cumplidas estas condiciones:

```text
[ ] Playbook versionado.
[ ] Matriz de capacidades versionada.
[ ] Oferta owner-facing mínima definida.
[ ] Delivery template estándar definido.
[ ] precio_margen_basico cerrado.
[ ] stock_alertas_basicas operativa con caveats documentados.
[x] gastos_triage ejecutable con caveats documentados.
[x] caja_diaria_triage ejecutable bajo contrato actual con caveat MOV-016; modo POR_FECHA validado como agrupación externa.
[x] proveedores_precio_variacion_triage ejecutable con caveats documentados.
[x] Excel Factory expresada como catálogo comercial inicial con límites V1.
[x] Claims prohibidos incorporados en entrega mediante SERVICE_1_QA_CLAIMS_AND_REPRESENTATIVE_DELIVERY_CASE_V1.
[ ] Stage 6 sigue cerrado.
[ ] PDF/OCR sigue diferido.
[ ] Outputs locales no se commitean.
```

Si una familia no se completa, puede quedar como:

```text
LIMITED_IN_FULL_ASSISTED_V1
```

siempre que la oferta comercial no la prometa como cerrada.

---

# 8. Qué NO bloquea vender una versión inicial

No bloquea venta inicial asistida:

```text
- no tener PDF/OCR;
- no tener APIs;
- no tener Stage 6;
- no tener chatbot productivo;
- no tener conciliación definitiva;
- no cubrir producción industrial;
- no automatizar todos los mappings.
```

Sí bloquea vender sin riesgo:

```text
- no tener promesa comercial clara;
- no tener entrega owner-facing comprensible;
- no separar triage de diagnóstico;
- no explicar faltantes;
- no registrar bloqueos;
- no seguir el playbook.
```

---

# 9. Próxima acción única

```text
NEXT_ACTION:
Avanzar en S2_RECONCILIATION_ASSISTED_REVIEW_BLOCK_V1
```

Objetivo:

```text
Continuar Servicio 2 sobre conciliación asistida sin reabrir Servicio 1.
```

Servicio 1 queda cerrado con límites.
No implica runtime S1.
No implica Stage 6.
No implica nuevos Excel S1.

---

# 10. Veredicto

```text
SERVICE_1_STATUS: FINAL_DECLARED_WITH_LIMITS
FULL_STATUS: SELLABLE_WITH_EXPLICIT_LIMITS
CHAOS_CONTROL: PLAYBOOK + MATRIX + BASELINE_CORRECTION_MINIMAL_PATCH
NEXT_BOTTLENECK: S2_RECONCILIATION_ASSISTED_REVIEW_BLOCK_V1
```
