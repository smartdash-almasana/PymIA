# COLUMN_CONFIRMATION_LAYER_V1_CLOSEOUT

## STATUS

```text
CLOSED
```

## OBJECTIVE

Garantizar que ninguna columna humana alimente cálculos sin confirmación explícita del dueño.

Este frente reduce el riesgo de diagnóstico falso producido por mapeo semántico débil, substring matching o inferencias automáticas sobre nombres de columnas ambiguas.

## RULE

```text
El mapper sugiere.
El dueño confirma.
Sólo columnas confirmadas alimentan cálculos.
```

## CONTEXT

Durante pruebas con `cafeteria_abc.xlsx`, se detectó que PymIA podía mapear mal columnas humanas y calcular sin confirmación.

Caso crítico:

```text
MetodoPago podía clasificarse como pago/monto por substring matching.
```

También se detectó que `UNKNOWN` / `AMBIGUOUS` existían, pero no se convertían correctamente en preguntas vivas al dueño.

## FILES_COMMITTED

```text
PymIA-Live/pymia/contracts/column_confirmation_v1.py
PymIA-Live/tools/document_ingestion.py
PymIA-Live/tools/bem_schema_builder/excel_profile_builder.py
PymIA-Live/tests/contracts/test_column_confirmation_v1.py
PymIA-Live/tests/tools/test_column_confirmation_builder.py
PymIA-Live/tests/tools/test_structured_evidence_compute_blocks_unconfirmed_columns.py
PymIA-Live/tests/tools/test_column_semantic_classifier_confirmation_behavior.py
```

## COMMIT

```text
feat(pymia-live): add owner column confirmation before computation
```

## TESTS

Command reported:

```bash
pytest tests/contracts/test_column_confirmation_v1.py tests/tools/test_column_confirmation_builder.py tests/tools/test_structured_evidence_compute_blocks_unconfirmed_columns.py tests/tools/test_column_semantic_classifier_confirmation_behavior.py -v
```

Result reported:

```text
71 passed
```

## RECHECK

Command reported:

```bash
python -X utf8 .tmp/_recheck_cafeteria_confirmation.py
```

Result reported:

```text
RECHECK cafeteria_abc: PASS
```

## VALIDATIONS

```text
AUTO_IGNORED_COLUMNS: NO
ALL_COLUMNS_HAVE_OWNER_QUESTION: YES
COMPUTATIONAL_COLUMNS_BLOCK_CALC: YES
INFORMATIONAL_COLUMNS_DO_NOT_BLOCK_BUT_ASK: YES
METODO_PAGO_AS_MONTO: FALSE
VENTAS_TOTAL_BEFORE_CONFIRMATION: NOT_COMPUTED
MARGEN_BEFORE_CONFIRMATION: NOT_COMPUTED
RULE_FIDELITY: YES
```

## INVARIANTS

- Ninguna columna se considera irrelevante automáticamente.
- `IGNORED_NOT_RELEVANT` sólo puede existir después de confirmación explícita del dueño.
- Toda columna no confirmada debe tener `owner_question`.
- Las columnas informativas preguntan, pero no bloquean ventas/margen.
- Las columnas computacionales pendientes bloquean sólo los cálculos que dependen de ellas.
- `MetodoPago` nunca alimenta monto/pago sin confirmación.
- `UNKNOWN` y `AMBIGUOUS` deben convertirse en preguntas vivas al dueño.

## RISK_REDUCED

Este frente impide que el sistema ejecute cálculos sobre columnas cuyo significado o función todavía no fue confirmado por el dueño.

Riesgo reducido principal:

```text
Cálculo aparentemente determinístico sobre evidencia semánticamente mal interpretada.
```

## RESIDUAL_RISKS

- Falta flujo visible completo owner → respuesta → desbloqueo.
- Falta persistencia explícita de respuestas de confirmación del dueño si el flujo futuro lo requiere.
- Falta replay específico de confirmación de columnas.
- Falta UX owner-facing consolidada para mostrar, responder y auditar confirmaciones de columnas.
- Falta cerrar cómo se representa una confirmación parcial, insuficiente o contradictoria del dueño.

## NON_GOALS

Este frente no abrió:

```text
diagnostic_core
OCF productivo
replay
storage
Nivel 2
canales externos
dashboard
chatbot
nuevos pilotos Excel
docs decorativas
```

## NEXT_FRONT_RECOMMENDED

```text
OWNER_COLUMN_CONFIRMATION_FLOW_V1
```

Objetivo recomendado:

```text
columna dudosa detectada
→ pregunta al dueño
→ dueño confirma significado
→ sistema registra confirmación
→ cálculo se desbloquea sólo si corresponde
→ cálculo sigue bloqueado si la respuesta no alcanza
```

## FINAL_VERDICT

```text
COLUMN_CONFIRMATION_LAYER_V1: CLOSED
```
