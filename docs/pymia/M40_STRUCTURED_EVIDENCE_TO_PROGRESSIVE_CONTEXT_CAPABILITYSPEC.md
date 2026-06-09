# M40 — Structured Evidence to Progressive Context CapabilitySpec

Fecha: 2026-06-08
Estado: VIGENTE
Frente: `M40_IS_NEXT`

---

## 1. Capacidad

PymIA puede poblar automáticamente `progressive_context` con `structured_evidence` y `formula_ids`, usando el parser Excel ya existente y el intake ya registrado, sin duplicar parser ni hardcodear fórmulas.

La capacidad autorizada es:

```text
latest_evidence_path
+ IntakeRecord.evidence_requests[].formula_ids
→ structured_evidence_builder
→ progressive_context["structured_evidence"]
→ progressive_context["formula_ids"]
```

---

## 2. Qué puede hacer

M40 puede:

- usar `tools.document_ingestion.build_structured_evidence_from_xlsx`;
- extraer `formula_ids` desde `IntakeRecord`;
- poblar `progressive_context`;
- habilitar que M39 produzca automáticamente el payload del bridge.

---

## 3. Inputs requeridos

- `latest_evidence_path`
- `IntakeRecord`
- `evidence_requests[].formula_ids`

---

## 4. Outputs requeridos

- `structured_evidence`
- `formula_ids`
- decisión registrada si el parseo falla

---

## 5. Limitaciones obligatorias

M40 no autoriza:

- duplicar parser Excel;
- hardcodear fórmulas;
- tocar Telegram;
- tocar `DiagnosticCoreV1`;
- inventar variables.

---

## 6. Failure states

La capacidad debe admitir:

- parseo exitoso y contexto poblado;
- deduplicación determinística preservando orden;
- fail-closed si el parseo falla;
- fallback legacy sin colapso del flujo.

---

## 7. Fuera de alcance

- ejecutar diagnóstico por sí solo
- owner-facing report
- cambios en intake protocol
