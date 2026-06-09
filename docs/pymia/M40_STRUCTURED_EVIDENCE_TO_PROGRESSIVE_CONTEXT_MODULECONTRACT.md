# M40 — Structured Evidence to Progressive Context ModuleContract

Fecha: 2026-06-08
Estado: VIGENTE
Frente: `M40_IS_NEXT`

---

## 1. Frontera

Este contrato regula la frontera entre:

```text
evidence_path + IntakeRecord
↔ structured_evidence_builder
↔ progressive_context
```

---

## 2. Responsabilidades permitidas

La frontera M40 puede:

- leer el path de evidencia ya registrado;
- invocar el parser Excel existente;
- extraer `formula_ids` del intake;
- poblar `progressive_context`.

---

## 3. Responsabilidades prohibidas

La frontera M40 no puede:

- redefinir lógica del parser;
- hardcodear `formula_ids`;
- ejecutar diagnóstico directamente;
- ocultar fallas de parseo;
- cambiar el significado del intake.

---

## 4. Dependencias permitidas

- `tools.document_ingestion.build_structured_evidence_from_xlsx`
- `pymia.orchestration.graph`
- `pymia.smartpyme.structured_evidence_builder`

---

## 5. Invariantes

- `formula_ids` se obtienen sólo desde `evidence_requests`
- el orden es determinístico
- si el parseo falla, se registra decisión y el flujo sigue por fallback legacy
