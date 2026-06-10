# OWNER_SEMANTIC_EVIDENCE_REQUESTS_CONTRACT_TASKSPEC

Fecha: 2026-06-10
Estado: READY_FOR_IMPLEMENTATION
Frente: OWNER_SEMANTIC_EVIDENCE_REQUESTS_CONTRACT

## 1. Problema

El flujo actual bloquea correctamente cuando faltan inputs estructurales, pero todavía no convierte de forma suficiente la respuesta narrativa del dueño en un pedido de evidencia accionable.

Ejemplo:

```text
missing_key = own_price
owner_answer = "Los precios los fui cambiando porque subió la tela."
```

La respuesta narrativa no debe destrabar la evidencia dura, pero sí debe ayudar a formular un pedido más preciso:

```text
Pasame los precios de venta por producto/SKU de la última semana y, si cambiaron durante el período, desde qué fecha rigió cada precio.
```

## 2. Objetivo

Definir un contrato mínimo para traducir respuestas narrativas del dueño en pedidos de evidencia estructural más claros, sin convertir narrativa en evidencia dura y sin producir findings.

El objetivo operativo es pasar de:

```text
BLOCKED
```

a:

```text
BLOCKED_ACTIONABLE
```

## 3. Principio soberano

```text
Hermes / IA conversa y traduce.
Pydantic valida estructura.
PymIA decide sobre evidencia, bloqueo y diagnóstico.
El dueño confirma o aporta evidencia.
```

La capa conversacional puede reducir incertidumbre, pero no tiene autoridad diagnóstica.

## 4. Alcance permitido

Implementar un contrato Pydantic mínimo para representar pedidos semánticos de evidencia estructural.

Contrato sugerido:

```python
OwnerSemanticEvidenceRequest
```

Campos mínimos:

```text
request_id: str
missing_key: str
missing_input_type: Literal["STRUCTURAL_INPUT"]
owner_answer_text: str
semantic_signal: str | None
interpreted_meaning: str | None
refined_request_text: str
required_fields: list[str]
accepted_formats: list[str]
does_resolve_structural_input: bool = False
confidence: float | None
source_ref: str
metadata: dict[str, Any]
```

## 5. Reglas obligatorias

- `does_resolve_structural_input` debe ser siempre `False` para este frente.
- La narrativa del dueño no puede cerrar `missing_evidence`.
- El contrato no puede producir findings.
- El contrato no puede modificar DiagnosticCore.
- El contrato debe preservar `missing_key` técnico.
- El texto owner-facing debe pedir dato, archivo, columna, período o formato concreto.
- Si la interpretación es incierta, debe reflejarse en `confidence` o `semantic_signal`, no en una decisión diagnóstica.

## 6. Ejemplo esperado

Entrada conceptual:

```json
{
  "missing_key": "own_price",
  "missing_input_type": "STRUCTURAL_INPUT",
  "owner_answer_text": "Los precios los fui cambiando porque subió la tela.",
  "source_ref": "owner_answer://case-001/answer-001"
}
```

Salida contractual esperada:

```json
{
  "missing_key": "own_price",
  "missing_input_type": "STRUCTURAL_INPUT",
  "semantic_signal": "PRICE_VARIABILITY_DUE_TO_INPUT_COST",
  "interpreted_meaning": "El dueño indica variación de precios por aumento de insumos.",
  "refined_request_text": "Para calcular margen necesito precios de venta por producto/SKU de la última semana y, si cambiaron durante el período, desde qué fecha rigió cada precio.",
  "required_fields": ["producto/SKU", "precio de venta", "fecha o semana de vigencia"],
  "accepted_formats": ["Excel", "lista de precios", "texto estructurado"],
  "does_resolve_structural_input": false
}
```

## 7. No autorizado

Este frente no autoriza:

- agente conversacional productivo;
- Telegram;
- Hermes runtime;
- ERP;
- PDF productivo;
- nuevas fórmulas;
- cambios en DiagnosticCore;
- cambios en graph;
- findings nuevos;
- desbloqueo por narrativa.

## 8. Archivos esperados

Implementación mínima sugerida:

```text
pymia/contracts/owner_semantic_evidence_requests.py
tests/smartpyme/test_owner_semantic_evidence_requests.py
```

Opcional, sólo si se justifica en implementación posterior:

```text
pymia/smartpyme/owner_semantic_evidence_request_builder.py
```

## 9. Criterios de aceptación

- El contrato valida una solicitud semántica de evidencia estructural.
- `does_resolve_structural_input` no puede ser `True` en este frente.
- `missing_key` se conserva.
- `refined_request_text` es owner-facing y accionable.
- `required_fields` no está vacío.
- `accepted_formats` no está vacío.
- No se modifica DiagnosticCore, graph, runtime, Telegram, Hermes ni PDF.

## 10. Cierre esperado

Crear checkpoint:

```text
docs/pymia/OWNER_SEMANTIC_EVIDENCE_REQUESTS_CONTRACT_CHECKPOINT.md
```

El checkpoint debe registrar:

```text
VEREDICTO
ARCHIVOS MODIFICADOS
TESTS
DECISIONES CONTRACTUALES
BLOQUEANTES
```
