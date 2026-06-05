# M27 — Excel + semántica del dueño Checkpoint

## Estado

PASS

## Contexto

M27 forma parte del roadmap de servicio asistido Excel + semántica PyME.

Objetivo del hito:

```text
mensaje del dueño + Excel controlado
→ caso operativo estructurado
→ clasificación inicial
→ evidence gate
→ estado del caso
```

M27 no declara producto final. Certifica un slice mínimo de servicio asistido.

---

## Archivos agregados

```text
docs/roadmap/ROADMAP_SERVICIO_ASISTIDO_EXCEL_SEMANTICA_PYME.md
docs/roadmap/M27_EXCEL_SEMANTICA_DUENO_PLAN.md
tests/smartpyme/test_m27_excel_semantica_dueno.py
```

---

## Test agregado

```text
tests/smartpyme/test_m27_excel_semantica_dueno.py
```

El test valida que PymIA puede tomar un mensaje semántico del dueño sobre margen/ganancia, asociarlo con evidencia Excel controlada, generar intake, satisfacer el evidence gate y llegar a estado listo para análisis.

---

## Causa de la corrección durante M27

La primera versión del test no respetaba dos contratos reales:

1. `evidence_gate` compara `required_fields` contra campos declarados por la evidencia.
2. `missing_request_ids` puede incluir requerimientos no bloqueantes no satisfechos, por lo que no debe ser usado como condición absoluta de avance si el gate está `READY`.

Corrección aplicada:

- `metadata["fields"]` se alinea con `request.required_fields`.
- se elimina la aserción incorrecta sobre `missing_request_ids == []`.

---

## Validación reportada

Comando focal:

```text
python -m pytest tests/smartpyme/test_m27_excel_semantica_dueno.py -q
```

Comando de contratos relacionados:

```text
python -m pytest tests/smartpyme/test_intake.py tests/smartpyme/test_evidence_gate.py tests/smartpyme/test_m27_excel_semantica_dueno.py -q
```

Resultado reportado:

```text
81 passed in 1.15s
```

---

## Veredicto

M27 PASS.

Certificado:

```text
mensaje del dueño + Excel controlado
→ IntakeRecord
→ evidence gate
→ READY_FOR_ANALYSIS
```

No certificado:

- producto final;
- diagnóstico integral de empresa;
- servicio comercial validado;
- autonomía end-to-end;
- análisis de cualquier Excel arbitrario.

---

## Próximo hito sugerido

M28 — Hallazgo explicable.

Objetivo:

```text
ActionableFinding[]
→ narrativa grounded
→ markdown legible para dueño PyME
```

Mantener restricciones:

- no producto;
- no ERP;
- no registry;
- no dispatcher;
- no Telegram/PDF/HTML/UI;
- no LLM externo.
