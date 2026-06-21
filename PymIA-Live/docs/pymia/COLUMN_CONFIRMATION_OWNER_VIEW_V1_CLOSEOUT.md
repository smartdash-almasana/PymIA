# COLUMN_CONFIRMATION_OWNER_VIEW_V1_CLOSEOUT

## STATUS

```text
CLOSED
```

## OBJECTIVE

Cerrar la capa owner-facing mínima para mostrar al dueño las preguntas de confirmación de columnas antes de usar esas columnas en cálculos.

Este frente convierte la seguridad interna de `COLUMN_CONFIRMATION_LAYER_V1` y el contrato de respuesta de `OWNER_COLUMN_CONFIRMATION_FLOW_V1` en una vista clara, legible y respondible por el dueño.

## RULE

```text
El mapper sugiere.
El dueño confirma.
La vista debe explicar qué se está preguntando.
Sólo columnas confirmadas alimentan cálculos.
```

## PREVIOUS FRONTS

```text
COLUMN_CONFIRMATION_LAYER_V1
OWNER_COLUMN_CONFIRMATION_FLOW_V1
```

Cadena consolidada:

```text
columna dudosa detectada
→ pregunta owner_question generada
→ cálculo inseguro bloqueado
→ vista owner-facing renderizada
→ respuesta del dueño clasificada bajo contrato
→ cálculo desbloqueado sólo si corresponde
```

## THIS FRONT

```text
COLUMN_CONFIRMATION_OWNER_VIEW_V1
```

Este frente agrega una función de renderizado owner-facing para que las preguntas internas de confirmación de columnas puedan presentarse en lenguaje claro.

No implementa canal externo, storage, replay, dashboard ni UI web.

## FILES_COMMITTED

```text
PymIA-Live/pymia/rendering/column_confirmation_owner_view.py
PymIA-Live/tests/rendering/test_column_confirmation_owner_view.py
```

## COMMIT

```text
feat(pymia-live): add column confirmation owner view
```

## TESTS

Commands reported:

```bash
python -m pytest tests/rendering/test_column_confirmation_owner_view.py -q
python -m pytest tests/contracts/test_column_confirmation_v1.py tests/rendering/test_column_confirmation_owner_view.py -q
```

Results reported:

```text
tests/rendering/test_column_confirmation_owner_view.py
8 passed in 0.98s

tests/contracts/test_column_confirmation_v1.py + tests/rendering/test_column_confirmation_owner_view.py
43 passed in 0.95s
```

## BEHAVIOR_ADDED

```text
render_column_confirmation_owner_view(matrix: ColumnConfirmationMatrix) -> str
```

The renderer produces a text view containing:

```text
- file name
- sheet name
- column name
- owner question
- suggested role
- relevance explanation
- allowed response options
```

## OWNER_RESPONSE_OPTIONS

The view exposes the allowed owner responses:

```text
1. Si, es correcto.
2. No, significa otra cosa: ______
3. No se.
4. Ignorar esta columna.
```

## INVARIANTS

- Only actionable columns are rendered.
- `CONFIRMED` columns are not rendered.
- `IGNORED_NOT_RELEVANT` columns are not rendered.
- Computational columns explicitly say they may block dependent calculations.
- Informational columns explicitly say they do not block sales/margin, but still require confirmation.
- `MetodoPago` is rendered as a payment method / form of payment, never as an amount.
- If there are no pending confirmations, the view returns an explicit no-pending-confirmations message.

## RISK_REDUCED

This front reduces the risk that column-confirmation questions remain internal-only and never become understandable to the owner.

Risk reduced:

```text
A safe internal blocker without a clear owner-facing resolution path.
```

## VALIDATED_CASES

```text
pending questions are rendered
file, sheet, column and question are included
confirmed columns are excluded
ignored columns are excluded
computational relevance is explained
informational relevance is explained
response options are included
MetodoPago is not rendered as amount
no-pending-confirmations message is rendered
```

## NON_GOALS

This front did not open:

```text
storage
replay
OCF productivo
diagnostic_core
Nivel 2
dashboard
chatbot
external channels
new Excel pilots
```

## RESIDUAL_RISKS

- The owner view is not yet integrated into the CLI/report delivery path.
- Owner responses are not yet captured from this rendered view end-to-end.
- There is no persisted owner-confirmation session.
- There is no replay trace for view → owner answer → apply_owner_answer.
- There is no final UX decision about accent marks, wording or channel-specific presentation.

## NEXT_FRONT_RECOMMENDED

```text
OWNER_COLUMN_CONFIRMATION_E2E_TRACE_V1
```

Recommended objective:

```text
Validate a minimal end-to-end trace without storage or external channels:

ColumnConfirmationMatrix
→ render_column_confirmation_owner_view
→ simulated OwnerColumnConfirmationAnswer
→ apply_owner_answer
→ can_compute_variable changes only when allowed
```

## FINAL_VERDICT

```text
COLUMN_CONFIRMATION_OWNER_VIEW_V1: CLOSED
```
