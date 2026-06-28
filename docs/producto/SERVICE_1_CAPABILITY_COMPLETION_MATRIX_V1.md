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
| Delivery package | CLOSED | README, owner_message, XLSX outputs, QA artifacts disponibles | Pulido comercial pendiente | Normalizar plantilla de entrega | Parcial |
| QA gate | CLOSED | QA 12/12 en demo cafeteria_abc | No cubre todas las familias | Mantener como gate | No |
| owner_message.md | CLOSED | Generado en demo y flows previos | Ajuste de tono comercial futuro | Mantener guardrails | No |
| precio_margen_basico | CLOSED | cafeteria_abc: 15/15 OK; distribuidora sample 10/10 OK; pilot_002 7 OK + 2 INVALID por datos | Ninguno runtime; sólo calidad de datos | Usar como familia estrella | No |
| stock_alertas_basicas | OPERATIONAL_WITH_CAVEATS | Smoke existente indica operación/mapeo sobre pilotos; playbook lo marca operativo con caveats | Requiere controlar calidad de inputs y mapping | Ejecutar sólo bajo playbook, sin ceremonia extra | No, pero afecta amplitud full |
| caja_diaria_triage | PARTIAL | Sintético ejecutado; pilot_004 requiere mapping; contrato runtime saldo_inicial/ingresos/egresos | Modo por fecha es operativo externo, no contrato runtime | Usar sólo en modo agregado o por fecha consolidada | Sí parcial |
| gastos_triage | PARTIAL | pilot_004 candidato; contrato orientado a concepto/importe | Falta cierre operativo con archivo existente | Ejecutar caso controlado cuando sea prioridad | Sí parcial |
| proveedores_precio_variacion_triage | PARTIAL/UNKNOWN | Documentado como allowlisted; evidencia de archivo calzante no clara | Falta caso existente o dataset real compatible | Buscar sólo en archivos existentes; no fabricar Excel | Sí para full amplio |
| Conciliación caja/banco definitiva | OUT_OF_SCOPE | Guardrails explícitos | No pertenece al runtime actual | No prometer | No, si oferta dice triage |
| Contabilidad fiscal / IVA / IIBB | OUT_OF_SCOPE | Guardrails explícitos | No pertenece a S1 actual | No prometer | No |
| APIs bancarias / Mercado Pago / ML | DEFERRED | Guardrails explícitos | No runtime | Mantener fuera | No |
| Chatbot productivo | DEFERRED | Regla: IA conversa, FSM gobierna, tools ejecutan | Falta arnés productivo | No abrir ahora | No para servicio asistido |
| Stage 6 auto-routing | DEFERRED | Technical certainty low; no consumer recomendado | Sin consumidor técnico real | No abrir | No |
| Producción industrial KPI | OUT_OF_SCOPE | fabrica_industrial_compleja unsupported | No First Aid actual | Registrar gap futuro | No |
| Excel Factory descargables | PARTIAL | Templates/documentación previas; outputs XLSX por tool existen | Falta catálogo comercial final | Conectar a oferta, no a runtime nuevo | Sí parcial |
| Casos demo vendibles | PARTIAL | cafeteria_abc demo ready; synthetic case closed local | Falta paquete comercial mínimo | Preparar 1 muestra owner-facing | Sí parcial |

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
| GAP-002 | gastos_triage sin cierre operativo claro sobre archivo existente | operación | Alta | DeepSeek/Codex | No | Sí |
| GAP-003 | caja_diaria_triage requiere criterio estable AGREGADO/POR_FECHA | operación | Alta | DeepSeek/Codex | No | Sí |
| GAP-004 | proveedores_precio_variacion_triage sin evidencia fuerte de archivo existente | evidencia | Media | GPT/DeepSeek | No | Sí para full amplio |
| GAP-005 | Excel Factory no expresada como catálogo comercial final | producto | Media | GPT | Sí parcial | Sí |
| GAP-006 | Delivery package comercial aún técnico | producto | Media | GPT | Sí parcial | Sí |
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
3. gastos_triage con archivo existente.
4. caja_diaria_triage bajo contrato actual.
5. proveedores_precio_variacion_triage sólo si hay archivo existente calzante.
6. Excel Factory catálogo comercial.
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
[ ] gastos_triage ejecutable o explícitamente limitado.
[ ] caja_diaria_triage ejecutable bajo contrato actual o explícitamente limitado.
[ ] proveedores_precio_variacion_triage ejecutable o explícitamente limitado.
[ ] Excel Factory expresada como catálogo comercial inicial.
[ ] Claims prohibidos incorporados en entrega.
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
Crear docs/producto/SERVICE_1_OWNER_FACING_DELIVERY_TEMPLATE_V1.md
```

Objetivo:

```text
Transformar los artifacts técnicos del runtime en una entrega legible para dueño PyME sin claims indebidos.
```

No implica runtime.
No implica tests.
No implica Stage 6.
No implica nuevos Excel.

---

# 10. Veredicto

```text
SERVICE_1_STATUS: OPERABLE_ASSISTED_CORE
FULL_STATUS: NOT_YET
CHAOS_CONTROL: PLAYBOOK + MATRIX
NEXT_BOTTLENECK: OWNER_FACING_DELIVERY_TEMPLATE
```
