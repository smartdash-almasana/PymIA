# M40 — Structured Evidence to Progressive Context TaskSpec

Fecha: 2026-06-08
Estado: VIGENTE
Frente: `M40_IS_NEXT`

---

## 1. Objetivo

Poblar automáticamente `progressive_context` con `structured_evidence` y `formula_ids` para que M39 pueda producir `core_delivery_bridge_payload` sin intervención manual.

---

## 2. Slice implementativo

Slice único:

- helper `structured_evidence_builder`
- conexión mínima en `graph.py`
- tests de parseo y fail-closed

---

## 3. Archivos permitidos

- `pymia/orchestration/graph.py`
- `pymia/smartpyme/structured_evidence_builder.py`
- `tests/orchestration/test_graph.py`
- `tests/smartpyme/test_structured_evidence_builder.py`

---

## 4. Prohibiciones

- no tocar Telegram
- no tocar parser Excel
- no tocar `DiagnosticCoreV1`
- no hardcodear fórmulas
- no duplicar parser

---

## 5. Criterios PASS

- el builder parsea Excel real usando el parser existente
- el builder extrae `formula_ids` desde `IntakeRecord`
- `graph` puebla `progressive_context`
- si el parseo falla, el flujo no colapsa y queda decisión registrada

---

## 6. Evidencia mínima

- test focal del builder
- test focal de `graph`
