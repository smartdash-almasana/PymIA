# OWNER_SEMANTIC_CONFIRMATION_GATE_TASKSPEC

Fecha: 2026-06-10
Estado: READY_FOR_VALIDATION
Frente: OWNER_SEMANTIC_CONFIRMATION_GATE

## 1. Fundamento documental

La arquitectura vigente establece:

```text
SmartPyme no decide. SmartPyme propone. El dueño confirma.
```

También establece que el dueño es agente creacional: define intención, autoriza el camino, corrige el rumbo, valida utilidad y decide qué se interviene.

## 2. Problema

El contrato `OwnerSemanticEvidenceRequest` permite representar un pedido semántico de evidencia estructural, pero todavía faltaba representar el acto soberano anterior:

```text
interpretación tentativa
→ confirmación / rechazo / corrección del dueño
→ eje semántico autorizado o corregido
```

Sin este gate, una interpretación conversacional podría ser usada como si ya estuviera confirmada.

## 3. Objetivo

Crear un contrato Pydantic mínimo para representar el gate de confirmación semántica del dueño.

Contrato implementado:

```text
pymia/contracts/owner_semantic_confirmation.py
```

Clase principal:

```python
OwnerSemanticConfirmationGate
```

## 4. Estados soberanos

```text
PENDING_OWNER_CONFIRMATION
CONFIRMED_BY_OWNER
REJECTED_BY_OWNER
CORRECTED_BY_OWNER
```

## 5. Tipos de eje confirmable

```text
SEMANTIC_INTERPRETATION
EVIDENCE_REQUEST_AXIS
PATHOLOGY_AXIS
FORMULA_AXIS
```

## 6. Reglas obligatorias

- Un gate pendiente no puede tener respuesta ni corrección del dueño.
- Un gate confirmado requiere `owner_response_text`.
- Un gate rechazado requiere `owner_response_text`.
- Un gate corregido requiere `owner_response_text` y `corrected_interpretation`.
- `proposed_interpretation`, `confirmation_question`, `source_ref` y `gate_id` no pueden estar vacíos.
- El contrato no diagnostica.
- El contrato no calcula.
- El contrato no genera evidencia dura.
- El contrato no autoriza runtime ni agente productivo.

## 7. Ejemplo conceptual

```text
proposed_interpretation:
Estoy entendiendo que el eje a revisar es variación de precios por suba de tela.

confirmation_question:
¿Confirmás que este es el eje correcto para avanzar?

status:
PENDING_OWNER_CONFIRMATION
```

Si el dueño responde:

```text
Sí, es eso.
```

el gate puede pasar a:

```text
CONFIRMED_BY_OWNER
```

Si responde:

```text
No, el problema principal es que me pagan tarde.
```

el gate debe pasar a:

```text
CORRECTED_BY_OWNER
```

con `corrected_interpretation` trazable.

## 8. No autorizado

Este frente no autoriza:

- integración en graph;
- runtime conversacional;
- Telegram;
- Hermes productivo;
- PDF;
- ERP;
- nuevas fórmulas;
- nuevos findings;
- promoción de narrativa a evidencia dura.

## 9. Validación esperada por Codex

Crear tests en:

```text
tests/smartpyme/test_owner_semantic_confirmation_gate.py
```

Validar estados, invariantes y serialización.
