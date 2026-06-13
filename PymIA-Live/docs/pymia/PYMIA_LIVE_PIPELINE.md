# PYMIA LIVE PIPELINE

## Estado

`LIVE_PIPELINE_V1`

## Propósito

Describir la cadena ejecutable viva de PymIA después del cierre de `PYMIA_LIVE_CORE_MANIFEST.md`.

Este documento no crea una capacidad nueva. Ordena el flujo real que hoy corre desde `pymia/cli/vertical_slice.py` y marca el punto exacto donde debe entrar una futura capacidad de alineación conversacional.

---

## 1. Fuente rectora

Este pipeline deriva de:

```text
pymia/cli/vertical_slice.py
```

y queda subordinado a:

```text
AGENTS.md
docs/pymia/PYMIA_LIVE_CORE_MANIFEST.md
docs/ops/RUNBOOK_PILOTO_ASISTIDO_POST_LC.md
```

---

## 2. Pipeline vivo ejecutable

```text
CLI args
  --excel
  --message
  --tenant-id
  --intake-id
  --formula-id
  --storage-dir
        ↓
main(argv)
        ↓
build_pipeline(path, message, tenant_id, intake_id, formula_ids, storage_dir)
        ↓
inspect_excel(path)
        ↓
build_report(path, message, profile, tenant_id, intake_id, formula_ids, storage_dir)
        ↓
register_evidence_record(...)
        ↓
build_structured_summary(...)
        ↓
build_structured_evidence_context(...)
        ↓
StructuredEvidence.model_validate(...)
        ↓
match_evidence_requirements(...)
        ↓
build_owner_facing_report(...)
        ↓
register_pipeline_run_record(...)
        ↓
render_markdown_from_report(...)
        ↓
owner-facing markdown
```

---

## 3. Entradas vivas

| Entrada | Origen | Uso vivo |
|---|---|---|
| `excel_upload` | `--excel` | Perfilado, evidencia, estructura computable |
| `owner_message` | `--message` | Reporte, traza de ejecución, contexto visible |
| `tenant_id` | `--tenant-id` | Separación técnica de evidencia y runs |
| `intake_id` | `--intake-id` | Identidad de caso |
| `formula_ids` | `--formula-id` | Filtro opcional de suficiencia/reconciliación |
| `storage_dir` | `--storage-dir` | Persistencia local controlada |

---

## 4. Salidas vivas

| Salida | Dónde se produce | Función |
|---|---|---|
| `EvidenceRecord` | `register_evidence_record` | Registrar archivo, hash, tenant, intake |
| `StructuredEvidence` | `build_structured_summary` | Representar evidencia computable derivada del Excel |
| `catalog_reconciliation` | `match_evidence_requirements` | Comparar evidencia disponible contra requerimientos |
| `owner_facing_report` | `build_owner_facing_report` | Construir salida candidata para dueño/operador |
| `PipelineRunRecord` | `register_pipeline_run_record` | Registrar run_id, output_hash y pasos |
| `markdown` | `render_markdown_from_report` | Entregar reporte owner-facing local |

---

## 5. Punto actual de decisión de próxima pregunta

La próxima pregunta se decide hoy dentro de:

```text
render_markdown_from_report(...)
```

Regla actual observada:

```text
1. Si existe catalog_reconciliation:
   toma el primer entry que pueda construir una pregunta con _build_owner_question(entry).
2. Si no existe pregunta de catálogo:
   usa next_questions del reporte base.
3. Si tampoco existe:
   cae en pregunta genérica de confirmación de columnas/proceso real.
```

Fragmento lógico:

```text
catalog_reconciliation
↓
for entry in reconciliation
↓
_build_owner_question(entry)
↓
primera pregunta válida
```

---

## 6. Gap vivo del pipeline

```text
owner_message queda visible y trazado, pero todavía no gobierna la selección de la próxima pregunta.
```

Consecuencia operativa:

```text
El sistema puede recibir un síntoma dominante de caja/liquidez y emitir una pregunta técnica sobre stock si ese faltante aparece primero en la reconciliación de catálogo.
```

Mitigación vigente:

```text
RUNBOOK_PILOTO_ASISTIDO_POST_LC.md
→ regla transitoria de reconducción humana
```

---

## 7. Punto de inserción futuro

La futura mejora debe entrar entre:

```text
catalog_reconciliation
```

y:

```text
_build_owner_question(entry)
```

Nombre operativo previsto:

```text
QuestionAlignmentGate
```

Ubicación conceptual:

```text
catalog_reconciliation
+
owner_message
+
structured_evidence_summary
        ↓
QuestionAlignmentGate
        ↓
aligned_owner_question | reconduction_question | neutral_clarification_question
```

---

## 8. Contrato mínimo requerido antes de código

Antes de implementar `QuestionAlignmentGate`, debe existir un contrato propio que defina al menos:

```text
OwnerDeclaredAxis
EvidenceDetectedAxis
CandidateQuestionAxis
QuestionAlignmentGateResult
```

Resultados esperados:

```text
ALIGNED
MISALIGNED
UNKNOWN
```

Regla metodológica:

```text
Este documento sólo ubica el punto de integración.
No autoriza implementación.
```

---

## 9. Invariantes protegidas

El pipeline vivo debe preservar:

```text
- trazabilidad por tenant_id e intake_id
- EvidenceRecord con hash de contenido
- PipelineRunRecord con run_id y output_hash
- salida owner-facing en lenguaje entendible
- separación entre label visible y referencia técnica
- límite de no diagnóstico automático
- reconducción humana cuando la pregunta no acompaña el síntoma dominante
```

---

## 10. Criterio de cierre de este documento

Este documento queda cerrado si:

```text
1. refleja el flujo real de vertical_slice.py
2. no declara capacidades inexistentes como implementadas
3. ubica el gap vivo sin abrir código
4. preserva el manifiesto Live Core como rector
5. permite diseñar el contrato futuro sin deriva
```
