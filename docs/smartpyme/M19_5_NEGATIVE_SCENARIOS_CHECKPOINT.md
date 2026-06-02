# M19.5 — Checkpoint Negative Scenarios

Fecha: 2026-06-02  
Estado: READY_COMMITTED_PUSHED  
Commit: `d3be69a test(smartpyme): add pipeline radiography negative scenarios`

---

## 1. Veredicto

```text
M19.5 Pipeline Radiography negative scenarios = CERRADO
```

El Test Drive interno de SmartPyme amplió la radiografía del pipeline formal con negativos de alta señal y bajo riesgo.

---

## 2. Escenarios existentes antes de M19.5

```text
happy path Excel → PASS / READY_TO_DELIVER
sin evidencia → BLOCKED_EXPECTED / must_not_dispatch
```

---

## 3. Escenarios agregados

### NEG-01 — evidence_type_mismatch

Objetivo:

```text
probar que una evidencia con evidence_type incorrecto no satisface requests reales.
```

Resultado esperado:

```text
BLOCKED_EXPECTED
evidence_gate bloquea
no hay dispatch prematuro
```

### NEG-02 — unsupported_runtime_classification

Objetivo:

```text
probar que una clasificación no soportada no llega a READY_TO_DELIVER.
```

Resultado esperado:

```text
bloqueo controlado en readiness/runtime_bridge
o dispatch_status == UNSUPPORTED si llega al dispatcher
```

---

## 4. Escenarios no implementados

### NEG-03 — corrupt Excel

Estado:

```text
pospuesto
```

Motivo:

```text
requiere fixture corrupto que provoque excepción real en diagnose_excel sin volverse test artificial.
```

### NEG-04 — undeliverable_output_refs

Estado:

```text
descartado como e2e por ahora
```

Motivo:

```text
es más adecuado para test contractual/unitario del execution_result_gate que para radiografía e2e.
```

---

## 5. Validaciones reportadas

```text
python -m pytest tests/smartpyme/e2e/test_pipeline_radiography_excel.py -q
→ 4 passed
```

```text
python -m pytest tests/smartpyme/test_pipeline_radiography_models.py tests/smartpyme/e2e/test_pipeline_radiography_excel.py -q
→ 7 passed
```

```text
python -m pytest tests/smartpyme -q
→ 595 passed
```

```text
rg e2e_cli / telegram / pdf / docling / html en scope M19
→ sin matches relevantes
```

---

## 6. Qué significa este cierre

M19.5 incrementa el valor de Pipeline Radiography porque ya no sólo prueba un happy path.

También prueba bloqueos sanos:

```text
- evidencia ausente;
- evidencia de tipo incorrecto;
- clasificación runtime no soportada.
```

Esto reduce falsos positivos y fortalece la radiografía del pipeline formal.

---

## 7. Estado actual del Test Drive interno

```text
Scenario + Trace: OK
Runner formal: OK
Dispatcher formal: OK
Execution result gate: OK
Delivery package: OK
Happy path: OK
Negativos mínimos: OK
Suite SmartPyme: 595 passed
```

---

## 8. Próximo frente recomendado

Opciones siguientes:

```text
M19.6 — Developer report para PipelineTrace.
M20 — capability registry machine-readable.
M17 — supplier_duplicate_check al dispatcher formal.
```

Recomendación metodológica:

```text
M19.6 antes de M20/M17 si se quiere mejorar observabilidad del Test Drive.
M20 antes de M17 si se quiere gobernar capacidades con fuente legible por máquina.
M17 antes de nuevas fichas si se quiere demostrar segunda máquina formal en dispatcher.
```

---

## 9. Frase rectora

```text
Un pipeline sano no sólo entrega cuando puede: también bloquea cuando debe.
```
