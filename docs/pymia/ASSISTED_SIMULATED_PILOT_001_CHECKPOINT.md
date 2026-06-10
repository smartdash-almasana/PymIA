# ASSISTED_SIMULATED_PILOT_001_CHECKPOINT

Fecha: 2026-06-10
Estado: PARTIAL
Tipo: simulación operativa asistida
Caso: La Textil Cosida SRL

## 1. Veredicto

La simulación F1 → F2 → F3 pudo ejecutarse en entorno controlado con el fixture real:

```text
prueba_excels/la_textil_cosida_srl_mar_abr_may_2026.xlsx
```

El flujo integrado quedó observable y la reentrada owner-answer quedó consumida por bridge.

No es piloto real.
No cierra TD-004.
No valida adopción operativa externa.

El veredicto queda en:

```text
PARTIAL
```

porque el flujo existe, pero la experiencia owner-facing todavía muestra fricciones relevantes.

## 2. Evidencia ejecutada

Simulación controlada sobre `run_pymia_graph(...)` en tres pasos:

```text
F1 text_message
F2 document_received + diagnostic_request
F3 text_message owner-answer reentry
```

Entrada F1:

```text
Hola, fabrico ropa y vendo por mayor. No se si estoy ganando plata porque cada vez compro mas tela y me queda menos margen.
```

Respuesta simulada del dueño en F3:

```text
Los productos Remera Basica y Buzo Frisa son los que mas vendo. En mayo subio mucho la tela y no actualice todos los precios. Algunas ventas mayoristas tienen descuento especial.
```

Hechos observados:

- F1 preservó la ficha obligatoria vía `pending_question` de contacto.
- F1 registró `preliminary_taxonomy` con:
  - `industry = textil`
  - `sales_channels = ["wholesale"]`
  - `status = PRELIMINARY`
  - `confidence = 0.65`
- F1 mantuvo:
  - `has_preliminary_taxonomy = true`
  - `has_confirmed_taxonomy = false`
  - `has_taxonomy = false`
- F1 no generó `evidence_requests`.
- F1 no generó `hypotheses`.
- F2 dejó artefactos trazables:
  - `operational_audit_result.json`
  - `render_contract.json`
  - `owner_questions_bundle.json`
  - `owner_facing_report.json`
- F2 quedó en `phase = BLOCKED`.
- F3 tomó la rama:

```text
Route: owner_answer_reentry
Owner answer bridge reentry consumed
```

- F3 no pasó por adapter conversacional en la reentrada.
- F3 no reejecutó runtime legacy ni dispatch legacy.

## 3. Validaciones pedidas

### No diagnóstico en primer turno

```text
CERTIFICADO
```

No aparecieron hipótesis, findings, execution ni delivery bridge en F1.

### preliminary_taxonomy no confirma taxonomía

```text
CERTIFICADO
```

Se observó `has_preliminary_taxonomy = true` con `has_confirmed_taxonomy = false` y `has_taxonomy = false`.

### No evidence_requests antes de ficha

```text
CERTIFICADO
```

En F1 `evidence_requests` quedó ausente.

### No causalidad inventada

```text
CERTIFICADO
```

El bridge quedó en modo bloqueo por faltantes; no inventó causalidad financiera nueva a partir del relato del dueño.

### La simulación no se confunde con piloto real

```text
CERTIFICADO
```

La evidencia usada fue fixture local + respuesta simulada del dueño. No hubo operación real, canal real ni validación externa.

## 4. Pasos ejecutados

1. Se simuló primer contacto natural de una PyME textil mayorista.
2. Se verificó que la ficha siguiera obligatoria.
3. Se subió el fixture Excel de La Textil Cosida SRL.
4. Se forzó el camino bridge actual sin runtime legacy para observar el estado integrado vigente.
5. Se inspeccionaron artefactos `owner_questions_bundle.json` y `owner_facing_report.json`.
6. Se ingresó una respuesta textual simulada del dueño.
7. Se verificó la reentrada owner-answer y la reproyección del reporte.

## 5. Preguntas al dueño observadas

La primera pregunta visible después del bridge fue:

```text
¿Podés aportar el dato o documento faltante para 'amortization'?
```

También aparecieron preguntas sobre:

- `client_direct_costs`
- `client_revenue`
- `client_service_costs`
- `closing_index`
- `collected_amount`
- `depreciation`
- `dpo`
- `dso`
- `expected_collections`
- `expected_payments`
- `initial_balance`
- `market_price`
- `net_income`
- `origin_index`
- `own_price`
- `taxes`
- `working_capital_change`

## 6. Calidad del OwnerFacingReport

Lectura observada:

```text
MIXTA
```

Fortalezas:

- existe artefacto owner-facing trazable;
- el summary visible no inventa diagnóstico;
- después de F3 el reporte se re-proyecta y reduce `next_questions` a una sola pregunta activa.

Debilidades:

- muchas preguntas aparecen como nombres técnicos crudos (`amortization`, `dso`, `own_price`);
- el primer bloqueo visible no está priorizado en lenguaje de negocio;
- la respuesta narrativa simulada del dueño no destraba evidencia dura;
- `findings_count` quedó en `0`, por lo que esta simulación ejercita bloqueo y reentrada, no lectura diagnóstica útil para decisión.

## 7. Fricciones observadas

- En F1 el estado persistido observado fue `phase = NEW`, no `FICHA_PYME_INICIAL` explícito.
- En F1 `raw_first_message` apareció `null`, aunque la señal preliminar sí quedó capturada en `preliminary_taxonomy.created_from`.
- En F2 el paquete de preguntas owner-facing mezcla preguntas legibles con claves técnicas crudas.
- En F3 la respuesta simulada del dueño no fue suficiente para resolver faltantes estructurales; el caso siguió `BLOCKED`.
- `gate_verdict` persistido quedó `null` aunque el flujo visible sí se comportó como bloqueo controlado.

## 8. Qué faltaría para piloto real

- canal real asistido con dueño real;
- ficha inicial realmente completada, no sólo primer mensaje;
- evidencia operativa adicional alineada con los faltantes estructurales;
- priorización owner-facing de preguntas en lenguaje de negocio;
- trazabilidad más nítida entre bloqueo metodológico y pregunta accionable;
- validación humana de utilidad del reporte para una decisión concreta.

## 9. Cierre metodológico

Resultado de esta simulación:

```text
El flujo integrado F1 → F2 → F3 existe y puede observarse.
No alcanza para declarar piloto real.
No cierra TD-004.
```
