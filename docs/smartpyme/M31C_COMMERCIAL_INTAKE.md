# M31-C — Intake comercial-operativo

## Estado

READY_FOR_ASSISTED_PILOT_INTAKE

## Propósito

Capturar la información mínima necesaria para decidir si una PyME/prospecto puede entrar a un piloto asistido SmartPyme.

Este intake no es diagnóstico.

Este intake no declara producto.

## Regla principal

No aceptar un caso si no puede aportar al menos:

```text
problema declarado + evidencia mínima + sentido operativo mínimo o gap registrable
```

## Bloque 1 — Identificación

```yaml
prospect_ref:
contact_date:
business_name_or_alias:
business_type:
owner_or_operator_role:
case_origin:
```

Preguntas:

1. ¿Qué tipo de PyME es?
2. ¿Quién habla: dueño, socio, administrativo, contador, operador?
3. ¿El caso es real, prospecto, referido o demo?

## Bloque 2 — Dolor declarado

```yaml
owner_problem_statement:
```

Preguntas:

1. ¿Qué querés entender o resolver?
2. ¿Qué te preocupa hoy?
3. ¿Qué decisión tenés que tomar?
4. ¿Qué pasa si no lo resolvés?

Ejemplos válidos:

- No sé si gano plata.
- Vendo mucho pero no queda plata.
- No entiendo mis costos.
- No me cierra caja/banco.
- Tengo Excel pero no claridad.

## Bloque 3 — Evidencia disponible

```yaml
available_evidence:
  -
```

Preguntas:

1. ¿Qué archivos tenés?
2. ¿Excel, PDF, extractos, facturas, reportes, listas de precios?
3. ¿De qué período son?
4. ¿Quién los genera?
5. ¿Están completos o faltan partes?

## Bloque 4 — Sentido operativo

```yaml
operational_meaning:
```

Preguntas:

1. ¿Qué significa cada archivo?
2. ¿Qué columnas son importantes?
3. ¿Qué período querés mirar?
4. ¿Qué proceso real generó los datos?
5. ¿Qué dato falta pero existe en otro lado?
6. ¿Qué decisión querés tomar con la respuesta?

## Bloque 5 — Evidencia faltante preliminar

```yaml
preliminary_missing_evidence:
  -
```

Registrar lo que ya se sabe que falta.

Ejemplos:

- costos;
- ventas por período;
- compras;
- stock;
- extracto bancario;
- significado de columnas;
- fecha/período;
- relación entre hojas.

## Bloque 6 — Aptitud del caso

```yaml
fit_status: FIT | PARTIAL_FIT | NOT_FIT | NEEDS_MORE_INFO
fit_reason:
```

### FIT

Tiene problema claro, evidencia mínima y sentido operativo suficiente.

### PARTIAL_FIT

Puede avanzar, pero con salida limitada o bloqueo probable.

### NEEDS_MORE_INFO

Falta información antes de decidir.

### NOT_FIT

Está fuera de alcance.

## Bloque 7 — No-promesa aceptada

Confirmar:

```yaml
accepted_no_promises:
  no_total_diagnosis_without_evidence: true | false
  no_accounting_audit: true | false
  no_erp_integration: true | false
  no_autonomous_product: true | false
  no_guaranteed_profit_result: true | false
```

Si no acepta la no-promesa, no iniciar piloto.

## Bloque 8 — Tiempo/costo operativo

```yaml
estimated_time_minutes:
commercial_mode:
operational_cost_criteria:
```

Valores posibles de `commercial_mode`:

```text
free_feedback_pilot
symbolic_price_pilot
paid_assisted_pilot
internal_realistic_case
```

## Bloque 9 — Decisión de intake

```yaml
intake_decision: ACCEPT_FOR_PILOT | REQUEST_MORE_EVIDENCE | REJECT_OUT_OF_SCOPE | BLOCKED
next_step:
```

## Plantilla vacía

```yaml
prospect_ref:
contact_date:
business_name_or_alias:
business_type:
owner_or_operator_role:
case_origin:
owner_problem_statement:
available_evidence:
  -
operational_meaning:
preliminary_missing_evidence:
  -
fit_status:
fit_reason:
accepted_no_promises:
  no_total_diagnosis_without_evidence:
  no_accounting_audit:
  no_erp_integration:
  no_autonomous_product:
  no_guaranteed_profit_result:
estimated_time_minutes:
commercial_mode:
operational_cost_criteria:
intake_decision:
next_step:
```

## Criterio para pasar a piloto real/prospecto

Pasar a piloto sólo si:

- `fit_status` es FIT o PARTIAL_FIT;
- la no-promesa fue aceptada;
- hay evidencia mínima;
- hay sentido operativo mínimo o gap registrable;
- se definió tiempo/costo operativo;
- se puede cerrar como entrega, salida parcial o bloqueo documentado.

## Restricciones

- No diagnosticar en intake.
- No prometer producto.
- No prometer resultado económico.
- No aceptar caso sin evidencia mínima.
- No aceptar caso fuera de alcance como si fuera apto.
- No abrir M32.
- No tocar código productivo.

## Próximo paso

Usar este intake para preparar 3 a 5 pilotos con prospectos o clientes reales si M31-C cierra documentalmente.
