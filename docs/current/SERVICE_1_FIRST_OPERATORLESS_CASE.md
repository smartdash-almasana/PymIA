# Servicio 1 — First Operatorless Case V1

**Ciclo:** `CYCLE_031_RUN_FIRST_OPERATORLESS_SERVICE_1_CASE`
**Fecha:** 2026-07-16
**Estado:** `PASS_OPERATORLESS_CASE_RUN`

## Declaración

Servicio 1 fue ejecutado como caso operativo inicial usando sólo el paquete operativo y la CLI oficial:

```text
python -m pymia.cli.service_1_product
```

No se usó `service_1_operator.py`, no se usó runtime bridge legacy y no se agregó una ruta técnica paralela.

## Entrada

```text
fixture: prueba_excels/cafeteria_abc.xlsx
sheet: Ventas
work_dir: .tmp\service_1_operatorless_case
runbook: docs/current/SERVICE_1_OPERABILITY_PACKET.md
```

## Primer pase

```text
returncode: 2
status: NEEDS_OWNER_CONFIRMATION
owner_questions_count: 6
tools_executed: false
result_json: .tmp\service_1_operatorless_case\first_pass.json
```

Interpretación:

```text
El sistema no ejecutó tools antes de recibir confirmación semántica del dueño.
```

## Reentry semántico

```text
semantic_owner_answers: .tmp\service_1_operatorless_case\semantic_owner_answers.json
answers_count: 6
source_rule: selected from product_pipeline.owner_questions[].allowed_option_ids; no free text
```

Regla:

```text
Cada valor salió de allowed_option_ids. No se usó texto libre.
```

## Segundo pase

```text
returncode: 0
status: PRODUCT_PIPELINE_READY
semantic_bindings_confirmed: true
tools_executed: true
executed_tool_refs: ["precio_margen_basico"]
xlsx_outputs: ["first_aid_001_precio_margen_basico.xlsx"]
result_json: .tmp\service_1_operatorless_case\final_pass.json
```

## Criterios PASS observados

```text
first_pass_status = NEEDS_OWNER_CONFIRMATION
first_pass_tools_executed = false
semantic_answers_from_allowed_ids = true
final_pass_status = PRODUCT_PIPELINE_READY
semantic_bindings_confirmed = true
tools_executed = true
executed_tool_refs = ["precio_margen_basico"]
xlsx_output_exists = true
```

## Límites honestos

```text
No prueba selección automática de tool.
No otorga autoridad runtime a LLM.
No ejecuta Servicio 2/3.
No convierte LIQ_001 en ejecución; eso queda como plan-only en el completion gate.
```

## Conclusión

```text
Servicio 1 MVP pasó su primer caso operatorless: puede ser operado desde el paquete publicado, con CLI oficial, entrada XLSX real, confirmación semántica, ejecución explícita permitida y salida XLSX trazable.
```
