# AUDIT_QUESTION_ALIGNMENT_GATE_STATUS

## Estado

```text
DOCUMENTARY_AND_CODE_AUDIT
READ_ONLY_AUDIT
NO_RUNTIME_CHANGE
NO_CODE_CHANGE
NO_PROMOTION
```

## Pregunta auditada

```text
¿QuestionAlignmentGate ya existe como contrato vivo en el repo,
o la documentación sólo declara que debe existir?
```

## Veredicto

```text
MIXED
```

Interpretación:

```text
QuestionAlignmentGate existe como contrato activo, loader, implementación y tests.
Pero la documentación viva todavía conserva planes/advertencias de saneamiento que describen estados previos o parcialmente superados.
```

No es `DECLARED_ONLY`.

No es `NOT_FOUND`.

Tampoco conviene marcarlo como `EXISTS_CONTRACT` puro sin aclaración, porque hay docs vivas que todavía hablan de saneamiento, deuda genética y plan documental.

---

## Repo state observado

```text
 M AGENTS.md
?? .agents/
?? .graphifyignore
?? .opencode/
?? _docs_inbox/
?? docs/pymia/FUNCTIONAL_GRAPH_PACK_MINIMAL_V1_CONTRACT.md
?? graphify-out/
```

No se observaron modificaciones tracked en `PymIA-Live` durante esta auditoría.

---

## Fuentes leídas

```text
AGENTS.md
PymIA-Live/pymia/contracts/question_alignment_v1.py
PymIA-Live/pymia/contracts/question_alignment_v1.json
PymIA-Live/tests/contracts/test_question_alignment_v1.py
PymIA-Live/tests/smartpyme/test_question_alignment_gate.py
PymIA-Live/pymia/smartpyme/question_alignment_gate.py
PymIA-Live/pymia/application/vertical_pipeline.py
PymIA-Live/pymia/smartpyme/question_resolution.py
PymIA-Live/docs/pymia/QUESTION_ALIGNMENT_DECLARATIVE_SANITIZATION_PLAN.md
```

---

## Evidencia de contrato vivo

Existe:

```text
PymIA-Live/pymia/contracts/question_alignment_v1.json
```

Estado declarado:

```json
"schema_version": "1.0",
"status": "ACTIVE"
```

Contiene:

```text
owner_keywords
formula_prefix_axis
pathology_axis
misalignment_rules
copy_templates
```

Existe loader:

```text
PymIA-Live/pymia/contracts/question_alignment_v1.py
```

Funciones observadas:

```text
load_question_alignment_contract()
validate_question_alignment_contract(data)
```

Valida estructura mínima:

```text
schema_version
status
owner_keywords
formula_prefix_axis
pathology_axis
misalignment_rules
copy_templates
```

---

## Evidencia de tests contractuales

Existe:

```text
PymIA-Live/tests/contracts/test_question_alignment_v1.py
```

Cubre:

```text
- carga de contrato activo
- status ACTIVE obligatorio
- owner_keywords obligatorio
- copy_templates obligatorio
```

---

## Evidencia de implementación

Existe:

```text
PymIA-Live/pymia/smartpyme/question_alignment_gate.py
```

Funciones observadas:

```text
detect_owner_axis(message)
detect_question_axis(entry)
align_next_question(owner_message, candidates)
load_question_alignment_rules()
```

El gate consume:

```text
load_question_alignment_contract()
```

y usa datos declarativos mediante helpers:

```text
_owner_keywords()
_formula_prefix_axis()
_pathology_axis()
_misalignment_rules()
_copy_templates()
```

---

## Evidencia de integración

Existe integración en:

```text
PymIA-Live/pymia/application/vertical_pipeline.py
```

Observado:

```text
from pymia.smartpyme.question_alignment_gate import align_next_question
```

Y uso:

```text
report["evidence_request_alignment"] = align_next_question(message, request_question_candidates)
```

Existe además resolución owner-facing en:

```text
PymIA-Live/pymia/smartpyme/question_resolution.py
```

Observado:

```text
alignment = align_next_question(message, question_candidates)
if alignment["status"] == "MISALIGNED":
    owner_question = alignment["final_question_text"]
    tech_reference = alignment["technical_reference"]
```

---

## Evidencia de tests funcionales del gate

Existe:

```text
PymIA-Live/tests/smartpyme/test_question_alignment_gate.py
```

Cubre:

```text
- detect_owner_axis
- detect_question_axis
- contrato JSON válido
- uso de reglas declarativas vía monkeypatch
- ALIGNED / MISALIGNED / UNKNOWN
- no candidates
- copy declarativo de reconducción
```

---

## Evidencia documental viva conflictiva o histórica

Existe:

```text
PymIA-Live/docs/pymia/QUESTION_ALIGNMENT_DECLARATIVE_SANITIZATION_PLAN.md
```

Declara:

```text
PLAN_DOCUMENTAL
```

y describe el saneamiento como objetivo:

```text
Extraer del código vivo todo conocimiento declarativo de QuestionAlignmentGate sin cambiar el resultado observable.
```

Pero el código actual ya muestra:

```text
question_alignment_v1.json
question_alignment_v1.py
tests/contracts/test_question_alignment_v1.py
question_alignment_gate.py consumiendo loader declarativo
```

Por lo tanto, esta documentación parece representar un plan previo, o parcialmente superado por implementación posterior.

---

## Hardcodes residuales observados

En `question_alignment_gate.py` quedan constantes de ejes:

```text
AXIS_CAJA_LIQUIDEZ
AXIS_VENTAS_MARGEN
AXIS_STOCK_REPOSICION
AXIS_COSTOS_PROVEEDORES
AXIS_PRODUCCION
AXIS_RRHH
AXIS_AUTOMATIZACION_MANUAL
AXIS_DESCONOCIDO
```

No se observaron en ese archivo mapas grandes hardcodeados equivalentes a:

```text
_OWNER_KEYWORDS
_FORMULA_PREFIX_AXIS
_PATHOLOGY_AXIS
copy owner-facing directo
```

Los mapas y copy principal viven en:

```text
question_alignment_v1.json
```

Riesgo restante:

```text
Las constantes AXIS_* siguen acoplando nombres de ejes al runtime, aunque el conocimiento pesado ya está en contrato.
```

Severidad:

```text
LOW / MEDIUM
```

No parece bloqueo inmediato.

---

## Clasificación final

```text
MIXED
```

Detalle:

```text
Contrato vivo: SÍ
Loader vivo: SÍ
JSON activo: SÍ
Tests contractuales: SÍ
Implementación: SÍ
Integración: SÍ
Documentación completamente reconciliada: NO
```

---

## Próximo paso metodológico correcto

No crear QuestionAlignmentGate desde cero.

No repetir contrato ya existente.

Siguiente paso correcto:

```text
AUDIT_QUESTION_ALIGNMENT_DECLARATIVE_SANITIZATION_COMPLETION
```

Objetivo:

```text
comparar el plan documental de saneamiento contra el estado actual de código,
marcar qué puntos ya están cumplidos,
qué puntos quedan pendientes,
y si corresponde cerrar el plan con checkpoint o actualizar documentación.
```

---

## Qué NO hacer ahora

```text
- no implementar otro QuestionAlignmentGate
- no crear contrato duplicado
- no tocar motor
- no tocar formula_rules_v1.json
- no tocar formula_engine_service.py
- no promover MD del inbox como autoridad todavía
- no abrir owner_labels_v1 hasta cerrar esta reconciliación
```

---

## Veredicto operativo

```text
QuestionAlignmentGate no es el próximo corte de creación.
Es el próximo corte de reconciliación/cierre documental.
```

Después de cerrar esa reconciliación, se puede reordenar la cola:

```text
1. cerrar estado documental de QuestionAlignmentGate
2. decidir si PrimaryCaseFile mínimo es próximo contrato
3. revaluar owner_labels_v1 como saneamiento secundario
```
