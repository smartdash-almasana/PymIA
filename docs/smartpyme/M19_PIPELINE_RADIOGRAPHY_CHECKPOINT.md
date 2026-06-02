# M19 — Checkpoint Pipeline Radiography v0

Fecha: 2026-06-02  
Estado: READY_COMMITTED_PUSHED  
Commit: `6e2b53c feat(smartpyme): add pipeline radiography v0`

---

## 1. Veredicto

```text
M19 Pipeline Radiography v0 = CERRADO
```

El primer Test Drive interno de SmartPyme quedó implementado, testeado y publicado en `main`.

---

## 2. Qué se incorporó

```text
pymia/pipeline_radiography/__init__.py
pymia/pipeline_radiography/scenario.py
pymia/pipeline_radiography/trace.py
pymia/pipeline_radiography/runner.py
tests/smartpyme/test_pipeline_radiography_models.py
tests/smartpyme/e2e/test_pipeline_radiography_excel.py
tests/fixtures/smartpyme/ventas_costos_margen.xlsx
docs/smartpyme/M19_CONTRACT_MAP.md
```

También se agregó:

```text
.pipeline_radiography/
```

a `.gitignore` para evitar persistir salidas locales del runner.

---

## 3. Qué prueba M19 v0

M19 v0 radiografía el pipeline formal `excel_diagnostic` sin usar el camino CLI lateral.

Pipeline ejercitado:

```text
create_intake_record
→ create_evidence_record
→ evaluate_evidence_sufficiency
→ evaluate_analysis_readiness
→ prepare_runtime_execution
→ dispatch_candidate(output_dir=...)
→ validate_execution_result
→ build_delivery_package
```

---

## 4. Qué NO usa

```text
pymia/smartpyme/e2e_cli.py
Telegram
PDF
HTML
Docling
UI
supplier_duplicate_check
IA residente runtime
```

---

## 5. Escenarios cubiertos

### 5.1 Happy path

```text
scenario_id: margin_excel_happy_path
owner_message: "No sé si vendo con margen"
evidence: Excel ventas/costos
runtime_classification: excel_diagnostic
expected: READY_TO_DELIVER
```

### 5.2 Negativo mínimo

```text
scenario_id: margin_without_evidence
expected: BLOCKED_EXPECTED
must_not_dispatch: true
```

---

## 6. Corrección post-review

Gemini/reviewer marcó `REQUEST_CHANGES` por un fallback inseguro en el runner:

```python
if match is None and len(available_items) == 1:
    match = available_items[0]
```

Ese fallback fue eliminado.

Estado final del emparejamiento:

```text
evidence_request → ScenarioEvidence
match estricto por evidence_type
```

Si no hay match, el runner no crea `EvidenceRecord`; el bloqueo queda a cargo de `evidence_gate`.

---

## 7. Validaciones reportadas

```text
python -m pytest tests/smartpyme/test_pipeline_radiography_models.py tests/smartpyme/e2e/test_pipeline_radiography_excel.py -q
→ 5 passed
```

```text
python -m pytest tests/smartpyme -q
→ 593 passed
```

```text
rg e2e_cli / supplier / telegram / pdf / docling / html en scope M19
→ sin matches relevantes
```

---

## 8. Qué significa este cierre

M19 v0 no certifica todo PymIA.

Certifica la existencia de un primer mecanismo interno para radiografiar el pipeline central por escenarios.

Resultado conceptual:

```text
PymIA deja de depender sólo de inferencias arquitectónicas.
Empieza a observar su pipeline fase por fase mediante trazas.
```

---

## 9. Limitaciones conocidas

```text
- M19 v0 cubre excel_diagnostic, no supplier_duplicate_check.
- No convierte el registry en machine-readable.
- No implementa IA residente ni arnés runtime.
- No cubre PDF/HTML/Telegram.
- La metadata de escenario sigue siendo sintética para M19 v0; no es extractor real.
```

---

## 10. Próximo frente recomendado

Orden recomendado después de M19:

```text
1. M19.5 — ampliar radiografías negativas y reporte developer.
2. M20 — registry machine-readable.
3. M17 — supplier_duplicate_check al dispatcher formal.
4. Luego: arnés mínimo / IA residente v0.
```

---

## 11. Frase rectora

```text
No se declara sano un pipeline por intuición.
Se lo radiografía por escenarios.
```
