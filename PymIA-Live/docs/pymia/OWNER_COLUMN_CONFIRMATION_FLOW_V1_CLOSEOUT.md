# OWNER_COLUMN_CONFIRMATION_FLOW_V1_CLOSEOUT

## STATUS

```text
CLOSED
```

## OBJECTIVE

Cerrar el flujo mínimo por el cual una respuesta del dueño puede confirmar, rechazar, ignorar o mantener bloqueada una columna previamente sugerida por el mapper.

Este frente no agrega inteligencia autónoma. Agrega fidelidad operacional:

```text
El mapper sugiere.
El dueño confirma.
La respuesta del dueño se clasifica bajo contrato.
Sólo una confirmación computacional válida puede desbloquear cálculo.
```

## PREVIOUS FRONT

```text
COLUMN_CONFIRMATION_LAYER_V1
```

Ese frente garantizó que una columna no confirmada no alimente cálculos y que columnas dudosas generen preguntas al dueño.

## THIS FRONT

```text
OWNER_COLUMN_CONFIRMATION_FLOW_V1
```

Este frente agrega el ciclo mínimo posterior:

```text
columna dudosa
→ pregunta al dueño
→ respuesta del dueño
→ respuesta clasificada
→ confirmación / rechazo / insuficiencia / ignorar explícito
→ cálculo desbloqueado sólo si corresponde
```

## FILES_COMMITTED

```text
PymIA-Live/pymia/contracts/column_confirmation_v1.py
PymIA-Live/tests/contracts/test_column_confirmation_v1.py
```

## COMMIT

```text
feat(pymia-live): add owner column confirmation flow
```

## TESTS

Command reported:

```bash
python -m pytest tests/contracts/test_column_confirmation_v1.py -q
```

Result reported:

```text
35 passed in 0.61s
```

## CONTRACTS_ADDED

```text
OwnerColumnConfirmationOutcome
OwnerColumnConfirmationAnswer
ColumnConfirmationMatrix.apply_owner_answer(...)
ColumnConfirmationMatrix._find_entry(...)
```

## OWNER_ANSWER_OUTCOMES

```text
CONFIRMED_COMPUTATIONAL
CONFIRMED_INFORMATIONAL
CONFIRMED_NOT_RELEVANT
OWNER_REJECTED_MAPPING
OWNER_UNKNOWN
INSUFFICIENT_ANSWER
CONFLICTING_ANSWER
```

## INVARIANTS

- La respuesta del dueño no entra directo al cálculo.
- Toda respuesta debe clasificarse como `OwnerColumnConfirmationAnswer` antes de modificar una columna.
- `CONFIRMED_COMPUTATIONAL` puede confirmar rol y desbloquear cálculo dependiente.
- `CONFIRMED_INFORMATIONAL` confirma una columna descriptiva, pero no alimenta cálculo monetario.
- `CONFIRMED_NOT_RELEVANT` permite `IGNORED_NOT_RELEVANT` sólo después de respuesta explícita del dueño.
- `OWNER_UNKNOWN` mantiene la columna pendiente.
- `INSUFFICIENT_ANSWER` mantiene la columna pendiente.
- `OWNER_REJECTED_MAPPING` pasa la columna a `BLOCKED_AMBIGUOUS`.
- `CONFLICTING_ANSWER` pasa la columna a `BLOCKED_AMBIGUOUS`.
- `MetodoPago` confirmado como `payment_method` nunca se convierte en monto ni alimenta cálculo.

## RISK_REDUCED

Este frente reduce el riesgo de que una respuesta textual del dueño sea tomada como autorización computacional sin pasar por un contrato explícito.

Riesgo reducido principal:

```text
Desbloqueo de cálculo por respuesta humana ambigua, insuficiente o contradictoria.
```

## VALIDATED_CASES

```text
owner confirma columna computacional → desbloquea variable
owner confirma columna informativa → no alimenta cálculo monetario
owner dice "no sé" → sigue pendiente
owner rechaza mapping → BLOCKED_AMBIGUOUS
owner pide ignorar columna → IGNORED_NOT_RELEVANT sólo después de respuesta explícita
MetodoPago confirmado como payment_method → nunca se vuelve monto
respuesta insuficiente → sigue pendiente
```

## NON_GOALS

Este frente no abrió:

```text
storage
replay
OCF productivo
diagnostic_core
Nivel 2
dashboard
chatbot
canales externos
nuevos pilotos Excel
```

## RESIDUAL_RISKS

- Falta vista owner-facing consolidada para mostrar preguntas de columnas y capturar respuestas.
- Falta persistencia de respuestas del dueño si el flujo productivo lo requiere.
- Falta replay específico del ciclo pregunta → respuesta → desbloqueo.
- Falta UI/UX para distinguir respuestas confirmatorias, insuficientes y contradictorias.
- Falta integración end-to-end con el canal real de interacción del dueño.

## NEXT_FRONT_RECOMMENDED

```text
COLUMN_CONFIRMATION_OWNER_VIEW_V1
```

Objetivo recomendado:

```text
exponer al dueño las preguntas de columnas en un formato claro,
recibir sus respuestas,
y convertirlas en OwnerColumnConfirmationAnswer sin tocar todavía storage, replay ni canales externos.
```

## FINAL_VERDICT

```text
OWNER_COLUMN_CONFIRMATION_FLOW_V1: CLOSED
```
