# ASSISTED_SIMULATED_PILOT_002_VALUE_CHECKPOINT

Fecha: 2026-06-10
Estado: PARTIAL
Tipo: simulación asistida orientada a valor operativo
Caso: La Textil Cosida SRL

## 1. Veredicto

```text
PARTIAL
```

La simulación confirma que el flujo controlado puede ejecutar F1 -> F2 -> F3 con el fixture indicado y mantener un bloqueo seguro, trazable y owner-facing.

No confirma todavía una entrega cobrable autónoma. El valor operativo existe como protocolo asistido, pero el informe generado no alcanza todavía como lectura clara de negocio porque no aparecen findings útiles y el caso queda bloqueado por faltantes estructurales.

No es piloto real.
No cierra TD-004.
No se hizo push.

## 2. Evidencia usada

Archivo usado:

```text
prueba_excels/la_textil_cosida_srl_mar_abr_may_2026.xlsx
```

Directorio local de ejecución:

```text
.tmp_assisted_simulated_pilot_002/run_20260610_141930
```

Entradas simuladas:

```text
F1:
Hola, fabrico ropa y vendo por mayor. No se si estoy ganando plata porque cada vez compro mas tela y me queda menos margen.

F2:
Subo el Excel para revisar margen, cobranzas y stock.

Diagnostic request:
diagnosticalo

F3:
El plazo promedio de cobro es 30 dias. Los impuestos los tiene mi contador y puedo conseguir el detalle si hace falta.
```

Artefactos observados:

```text
delivery_summary.md
operational_audit_result.json
render_contract.json
owner_questions_bundle.json
owner_facing_report.json
```

## 3. Resultado operativo

F1:

- El sistema pidió ficha inicial antes de diagnosticar.
- Se capturó `preliminary_taxonomy` con `industry = textil`, `organism_type = textil`, `sales_channels = ["wholesale"]`, `status = PRELIMINARY`, `confidence = 0.65`.
- `has_preliminary_taxonomy = true`.
- `has_confirmed_taxonomy = false`.
- `has_taxonomy = false`.
- No hubo hipótesis, evidence requests ni diagnóstico en primer turno.

F2:

- El flujo generó `core_delivery_bridge_payload`.
- El bridge produjo `owner_questions_bundle.json` y `owner_facing_report.json`.
- El estado final quedó `phase = BLOCKED`.
- `gate_verdict = BLOCKED`.
- `delivery_status = BLOCKED`.
- `findings_count = 0`.
- `operational_status = pending_data`.

F3:

- La respuesta del dueño fue consumida por la rama owner-answer bridge reentry.
- El estado siguió `BLOCKED`.
- `findings_count` siguió en `0`.
- El `OwnerFacingReport` incorporó la explicación:

```text
Tu respuesta fue considerada, pero todavía falta evidencia o dato estructurado para resolver este punto.
```

- El reporte conservó la advertencia trazable:

```text
Advertencia trazable: la respuesta del dueño fue considerada, pero no reemplaza evidencia estructurada faltante.
```

## 4. Findings

```text
findings_count = 0
```

No aparecieron findings útiles para decisión operativa.

Interpretación:

- El sistema no inventó diagnóstico.
- El sistema no promovió narrativa del dueño a evidencia dura.
- El sistema se detuvo por faltantes estructurales antes de producir conclusiones.

Esto es correcto metodológicamente, pero limita el valor operativo de esta simulación como entrega a una PyME.

## 5. Faltantes estructurales

`missing_evidence` observado:

```text
average_sales
average_stock
client_direct_costs
client_revenue
client_service_costs
closing_index
lead_time
market_price
origin_index
own_price
safety_stock
taxes
```

Todos los missing inputs derivados de `missing_evidence` quedaron clasificados como:

```text
STRUCTURAL_INPUT
```

La respuesta narrativa del dueño no los resolvió. El estado aplicable quedó:

```text
still_blocked_requires_structured_evidence
```

## 6. Preguntas al dueño

El `owner_questions_bundle.json` generó 15 preguntas.

Textos visibles principales:

```text
¿Podés aportar el dato, archivo o aclaración que falta para poder avanzar con el análisis?
¿Podés informar los impuestos del período analizado?
El caso está bloqueado. ¿Podés aportar la evidencia o aclaración necesaria para destrabarlo?
```

Fortaleza:

- Las preguntas visibles ya no exponen claves técnicas crudas como `own_price`, `average_stock` o `client_revenue`.
- La trazabilidad técnica queda preservada en `missing_key`.

Fricción:

- Muchas preguntas colapsan al fallback genérico.
- Un dueño PyME todavía necesitaría asistencia humana para traducir "dato, archivo o aclaración" en documentos concretos.
- El campo `missing_evidence` del `OwnerFacingReport` conserva claves técnicas. Si ese JSON se expone directamente al dueño, todavía requiere mediación o render controlado.

## 7. Claridad del OwnerFacingReport

Evaluación:

```text
MIXTA
```

Lo entendible:

- El reporte comunica bloqueo.
- La primera pregunta visible está en lenguaje natural.
- Después de F3 explica que la respuesta fue considerada pero no reemplaza evidencia estructurada.

Lo insuficiente:

- No hay findings ni insight operativo sobre margen, cobranzas o stock.
- El summary queda en una pregunta genérica.
- El reporte no prioriza cuál evidencia concreta pedir primero.
- La lista de `missing_evidence` sigue siendo técnica.
- `evidence_used` quedó vacío en el `OwnerFacingReport`, aunque el fixture Excel sí fue usado para construir evidencia estructurada.

## 8. Fricciones humanas

Fricción estimada:

```text
ALTA
```

Motivos:

- Se necesita completar ficha antes de interpretar el caso como entrega.
- El dueño no puede resolver faltantes estructurales sólo con narrativa.
- Hace falta asistencia para pedir documentos o datos concretos equivalentes a los missing keys.
- El resultado no produce aún una lectura de decisión sino un bloqueo ordenado.
- La respuesta F3 fue considerada, pero no redujo los faltantes estructurales.

Tiempo humano estimado para transformar esto en una entrega asistida:

```text
20-40 minutos
```

Incluye explicar faltantes, pedir evidencia concreta, validar si el Excel contiene columnas suficientes y reintentar con datos estructurados.

## 9. Valor operativo

Valor certificado:

- Control metodológico correcto.
- No diagnóstico prematuro.
- No causalidad inventada.
- Preguntas owner-facing humanizadas.
- Clasificación estructural de faltantes.
- Reentrada owner-answer trazable.
- Explicación visible de por qué una respuesta narrativa no destraba evidencia estructural.

Valor no certificado:

- No hay findings accionables.
- No hay recomendación operativa.
- No hay informe cobrable sin mediación.
- No hay validación con dueño real.
- No hay cierre de TD-004.

Conclusión:

```text
Se acerca a una entrega cobrable asistida sólo como etapa de intake/evidence recovery.
No alcanza todavía como informe de valor operativo entregable.
```

## 10. Qué impide pasar a piloto real

- Completar ficha PyME con datos confirmados.
- Convertir missing keys estructurales en pedidos concretos de datos/documentos.
- Reducir preguntas fallback genéricas.
- Asegurar que `OwnerFacingReport` no exponga campos técnicos crudos si se entrega directamente.
- Proveer evidencia suficiente para que aparezcan findings reales.
- Validar utilidad con un dueño PyME real.
- Definir protocolo humano de recuperación de evidencia antes de operación real.

## 11. Controles de seguridad

Certificado durante la simulación:

- No se tocó Telegram.
- No se tocó Hermes.
- No se tocó ERP.
- No se tocó PDF productivo.
- No se tocó runtime externo.
- No se modificó DiagnosticCore.
- No se crearon fórmulas nuevas.
- No se crearon reportes nuevos.
- No se hizo push.

## 12. Próximo paso metodológico

Abrir un frente focal de valor, no de integración:

```text
OWNER_FACING_EVIDENCE_REQUEST_PRIORITIZATION
```

Objetivo sugerido:

Convertir faltantes estructurales trazados (`missing_key`) en pedidos concretos, priorizados y entendibles para dueño PyME, sin promover narrativa a evidencia y sin tocar DiagnosticCore.
