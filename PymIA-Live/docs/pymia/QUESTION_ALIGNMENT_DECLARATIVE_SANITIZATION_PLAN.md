# PLAN DE IMPLEMENTACIÓN DE SANEAMIENTO — QUESTION ALIGNMENT DECLARATIVE SANITIZATION V1

## Estado

`CLOSED — IMPLEMENTADO`

Cierre documental registrado en:

```text
PymIA-Live/docs/pymia/QUESTION_ALIGNMENT_DECLARATIVE_SANITIZATION_CLOSED.md
```

## Fecha

2026-06-15

## Ámbito

`PymIA-Live`

## Corte propuesto

```text
QUESTION_ALIGNMENT_DECLARATIVE_SANITIZATION_V1
```

## Tipo de trabajo

```text
refactor contractual behavior-preserving
```

Este documento no implementa código.

Este documento no abre una feature nueva.

Este documento no declara producto final.

Este documento encuadra un saneamiento genético detectado en la integración ya cerrada de `QuestionAlignmentGate`.

---

## 1. Tesis del saneamiento

`PymIA-Live` ya funciona como núcleo operativo local trazable.

El problema inmediato no es agregar más capacidad, sino sanear deuda genética.

Objetivo:

```text
mantener el comportamiento funcional actual
+
extraer conocimiento hardcodeado del runtime
+
preservar trazabilidad
+
preservar tests
+
reducir deriva arquitectónica
```

No se busca crear producto nuevo.

No se busca abrir features.

No se busca rediseñar `PymIA-Live`.

No se busca reemplazar el vertical slice.

---

## 2. Fuentes leídas

Este plan se apoya en las siguientes fuentes vivas del repositorio:

```text
AGENTS.md
docs/pymia/START_HERE_FOR_AGENTS.md
docs/pymia/PYMIA_DEVELOPMENT_METHOD.md
docs/adr/ADR-024-pack-system-foundation.md
PymIA-Live/docs/pymia/PYMIA_LIVE_CORE_MANIFEST.md
PymIA-Live/docs/pymia/PYMIA_LIVE_PIPELINE.md
PymIA-Live/docs/pymia/QUESTION_ALIGNMENT_GATE_SPEC.md
Pymia-memoria/_task_actual.md
Pymia-memoria/_decisiones_vigentes.md
```

También se inspeccionaron los commits reportados para `QuestionAlignmentGate`:

```text
1327e10 feat(pymia-live): add isolated question alignment gate
740c63d feat(pymia-live): integrate question alignment gate into vertical slice owner message
7ac16a6 fix(pymia-live): include runtime catalog dependencies
c1afe56 fix(pymia-live): apply question alignment to rendered owner question
```

---

## 3. Estado funcional certificado por memoria

La memoria vigente declara cerrado:

```text
INTEGRACION_QUESTION_ALIGNMENT_GATE_EN_MARKDOWNS_REALES
```

Estado reportado:

```text
QUESTION_ALIGNMENT_GATE_ISOLATED: PASS
INTEGRACION_CLI_ALIGN_GATE: PASS
DEPENDENCIAS_CATALOGOS: PASS
CORRECCION_INTEGRACION_REAL: PASS
```

Evidencia reportada:

```text
tests/smartpyme/test_question_alignment_gate.py: 14/14 PASS
tests/e2e/test_vertical_slice_cli.py: 21/21 PASS
suite focal: 35/35 PASS
smoke real textil: PASS
```

Por lo tanto:

```text
QuestionAlignmentGate = funcionalmente cerrado
```

---

## 4. Problema genético detectado

Aunque el gate cerró funcionalmente, la lectura de commits muestra conocimiento de dominio y copy owner-facing embebidos en runtime.

Deuda detectada en `PymIA-Live/pymia/smartpyme/question_alignment_gate.py`:

```text
_OWNER_KEYWORDS
_FORMULA_PREFIX_AXIS
_PATHOLOGY_AXIS
```

Deuda detectada en `PymIA-Live/pymia/cli/vertical_slice.py`:

```text
copy de reconducción owner-facing hardcodeado
technical_reference template hardcodeado
```

Esto tensiona ADR-024:

```text
El conocimiento de dominio es enchufable.
El kernel permanece estable.
```

Conclusión:

```text
QuestionAlignmentGate = PASS funcional
QuestionAlignmentGate = PARTIAL genético
```

---

## 5. Objetivo del saneamiento

Extraer del código vivo todo conocimiento declarativo de `QuestionAlignmentGate` sin cambiar el resultado observable.

Debe salir de Python runtime:

```text
keywords por eje
mapeos formula_prefix → axis
mapeos pathology_code → axis
copy de reconducción
technical_reference template
fallbacks textuales
```

Debe entrar en contrato declarativo versionado:

```text
PymIA-Live/pymia/contracts/question_alignment_v1.json
```

con loader validado:

```text
PymIA-Live/pymia/contracts/question_alignment_v1.py
```

y tests:

```text
PymIA-Live/tests/contracts/test_question_alignment_v1.py
PymIA-Live/tests/smartpyme/test_question_alignment_gate.py
PymIA-Live/tests/e2e/test_vertical_slice_cli.py
```

---

## 6. Principios de implementación

### 6.1 No cambiar comportamiento

El saneamiento debe ser behavior-preserving.

El markdown final debe seguir emitiendo la misma reconducción cuando:

```text
owner_message = caja/liquidez
candidate_question = stock/reposición
```

### 6.2 No tocar dominios no relacionados

Prohibido tocar:

```text
formula_engine_service.py
formula_rules_v1.json
pathology_rules_v1.json
evidence_v1.py
pipeline_run_v1.py
storage.py
structured_evidence_builder.py
owner_facing_report.py
```

salvo que un test demuestre necesidad directa.

### 6.3 No abrir Pack Runtime

Este saneamiento no implementa Pack System completo.

Sólo aplica una extracción declarativa focal.

No crear:

```text
PackLoader
PackRegistry
DomainPack runtime
FormulaPack runtime
PathologyPack runtime
SectorPack runtime
```

### 6.4 No rediseñar vertical_slice.py

El vertical slice sólo debe dejar de contener copy o lógica de conocimiento.

Debe conservar:

```text
CLI args
build_pipeline
build_report
render_markdown_from_report
EvidenceRecord
PipelineRunRecord
output_hash
markdown owner-facing
```

---

## 7. Archivos permitidos

### Crear

```text
PymIA-Live/pymia/contracts/question_alignment_v1.json
PymIA-Live/pymia/contracts/question_alignment_v1.py
PymIA-Live/tests/contracts/test_question_alignment_v1.py
```

### Modificar

```text
PymIA-Live/pymia/smartpyme/question_alignment_gate.py
PymIA-Live/pymia/cli/vertical_slice.py
PymIA-Live/tests/smartpyme/test_question_alignment_gate.py
PymIA-Live/tests/e2e/test_vertical_slice_cli.py
```

### Sólo lectura

```text
PymIA-Live/docs/pymia/QUESTION_ALIGNMENT_GATE_SPEC.md
PymIA-Live/docs/pymia/PYMIA_LIVE_PIPELINE.md
PymIA-Live/docs/pymia/PYMIA_LIVE_CORE_MANIFEST.md
docs/adr/ADR-024-pack-system-foundation.md
docs/pymia/PYMIA_DEVELOPMENT_METHOD.md
AGENTS.md
```

---

## 8. Archivos prohibidos

```text
PymIA-Live/pymia/services/formula_engine_service.py
PymIA-Live/pymia/contracts/formula_rules_v1.json
PymIA-Live/pymia/contracts/pathology_rules_v1.json
PymIA-Live/pymia/contracts/formula_contract.py
PymIA-Live/pymia/diagnostic_core/*
PymIA-Live/pymia/smartpyme/storage.py
PymIA-Live/pymia/contracts/evidence_v1.py
PymIA-Live/pymia/contracts/pipeline_run_v1.py
```

También prohibido tocar:

```text
.tmp/
PymIA-Live/.tmp_smoke_owner_alignment/
_local_quarantine/
```

---

## 9. Diseño del contrato JSON

Archivo:

```text
PymIA-Live/pymia/contracts/question_alignment_v1.json
```

Estructura mínima:

```json
{
  "contract_version": "1.0.0",
  "status": "ACTIVE",
  "axes": {
    "caja_liquidez": {
      "keywords": [],
      "owner_label": "caja/liquidez"
    },
    "ventas_margen": {
      "keywords": [],
      "owner_label": "ventas/margen"
    },
    "stock_reposicion": {
      "keywords": [],
      "owner_label": "stock/reposición"
    },
    "costos_proveedores": {
      "keywords": [],
      "owner_label": "costos/proveedores"
    },
    "produccion": {
      "keywords": [],
      "owner_label": "producción"
    },
    "rrhh": {
      "keywords": [],
      "owner_label": "rrhh"
    },
    "automatizacion_manual": {
      "keywords": [],
      "owner_label": "automatización/manual"
    },
    "desconocido": {
      "keywords": [],
      "owner_label": "desconocido"
    }
  },
  "formula_prefix_axis": {
    "LIQ": "caja_liquidez",
    "INV": "stock_reposicion",
    "REN": "ventas_margen"
  },
  "pathology_axis": {
    "LIQ_001": "caja_liquidez",
    "LIQ_002": "caja_liquidez",
    "INV_001": "stock_reposicion",
    "INV_002": "stock_reposicion",
    "REN_001": "ventas_margen",
    "REN_002": "ventas_margen"
  },
  "alignment_rules": [
    {
      "rule_id": "caja_to_stock_misaligned",
      "declared_axis": "caja_liquidez",
      "question_axis": "stock_reposicion",
      "result": "MISALIGNED"
    }
  ],
  "copy_templates": {
    "misaligned_reconduction": "Entiendo que tu preocupación principal parece ser caja/liquidez. Antes de avanzar con una pregunta técnica sobre stock, ¿querés que enfoquemos el análisis en caja, banco, cobros o pagos?",
    "technical_reference": "Referencia técnica: reconducción_axis_{declared_axis}"
  }
}
```

---

## 10. Loader Python

Archivo:

```text
PymIA-Live/pymia/contracts/question_alignment_v1.py
```

Responsabilidades:

```text
cargar JSON
validar estructura mínima
exponer contrato como dict normalizado
fallar cerrado si falta archivo
fallar cerrado si status != ACTIVE
fallar cerrado si axes falta
fallar cerrado si copy_templates falta
```

No debe:

```text
diagnosticar
clasificar owner_message
elegir pregunta
depender de vertical_slice.py
leer Excel
leer EvidenceRecord
escribir storage
```

API mínima sugerida:

```python
load_question_alignment_contract() -> dict
validate_question_alignment_contract(data: dict) -> dict
```

---

## 11. Refactor de QuestionAlignmentGate

Archivo:

```text
PymIA-Live/pymia/smartpyme/question_alignment_gate.py
```

Antes:

```text
usa constantes internas hardcodeadas
```

Después:

```text
recibe contrato cargado o carga default contract
```

API mínima compatible:

```python
detect_owner_axis(message: str, contract: dict | None = None) -> str
detect_question_axis(entry: dict, contract: dict | None = None) -> str
align_next_question(owner_message: str, candidates: list[dict], contract: dict | None = None) -> dict
```

Esto permite preservar tests existentes y migrar progresivamente.

---

## 12. Refactor de vertical_slice.py

Archivo:

```text
PymIA-Live/pymia/cli/vertical_slice.py
```

Objetivo:

```text
sacar copy hardcodeado
```

Antes:

```python
owner_question = "Entiendo que tu preocupación principal parece ser caja/liquidez..."
tech_reference = f"Referencia técnica: reconducción_axis_{alignment['declared_axis']}"
```

Después:

```python
owner_question = alignment["final_question_text"]
tech_reference = alignment["technical_reference"]
```

El gate debe devolver el copy final a partir del contrato.

---

## 13. Tests contractuales

Crear:

```text
PymIA-Live/tests/contracts/test_question_alignment_v1.py
```

Casos mínimos:

```text
1. carga contrato válido
2. exige contract_version
3. exige status ACTIVE
4. exige axes
5. exige caja_liquidez
6. exige desconocido
7. exige formula_prefix_axis
8. exige pathology_axis
9. exige copy_templates.misaligned_reconduction
10. exige copy_templates.technical_reference
```

Criterio PASS:

```text
10/10 PASS
```

---

## 14. Tests del gate

Modificar:

```text
PymIA-Live/tests/smartpyme/test_question_alignment_gate.py
```

Preservar casos existentes:

```text
caja → caja = ALIGNED
caja → stock = MISALIGNED
mensaje vacío = UNKNOWN
mensaje ambiguo = UNKNOWN
sin candidatos = UNKNOWN
```

Agregar:

```text
el resultado MISALIGNED usa copy_template del contrato
technical_reference usa template del contrato
sin contrato explícito usa default contract
```

---

## 15. Tests E2E

Modificar sólo si es necesario:

```text
PymIA-Live/tests/e2e/test_vertical_slice_cli.py
```

Debe seguir verificando:

```text
si owner_message habla de caja
y el primer candidato técnico es stock
el markdown final NO muestra la pregunta de stock
y SÍ muestra reconducción hacia caja/liquidez
```

---

## 16. Validaciones obligatorias

Desde:

```text
cd E:\BuenosPasos\smartbridge\PymIA\PymIA-Live
```

Ejecutar:

```bash
python -m pytest tests/contracts/test_question_alignment_v1.py -v --tb=short
python -m pytest tests/smartpyme/test_question_alignment_gate.py -v --tb=short
python -m pytest tests/e2e/test_vertical_slice_cli.py -v --tb=short
```

Validación ampliada opcional:

```bash
python -m pytest tests/contracts/test_formula_rules_v1.py -v --tb=short
```

---

## 17. Criterio PASS

PASS sólo si:

```text
contrato JSON existe
loader existe
tests contractuales pasan
tests del gate pasan
tests e2e del vertical slice pasan
no cambia el comportamiento visible esperado
no se toca formula_engine_service.py
no se toca formula_rules_v1.json
no se toca diagnostic_core
no se agregan features
no se abre Pack Runtime
```

---

## 18. Criterio PARTIAL

PARTIAL si:

```text
contrato existe
loader existe
gate usa contrato
pero queda copy hardcodeado residual
o falla un test e2e no relacionado
o no se puede validar suite completa por entorno
```

---

## 19. Criterio BLOCKED

BLOCKED si:

```text
no se puede leer estado actual del repo
no se puede confirmar rama
no se puede ejecutar pytest
hay cambios remotos inesperados
aparece otro contrato question_alignment ya existente
vertical_slice.py cambió sustancialmente desde los commits leídos
```

---

## 20. Criterio HARD_FAIL

HARD_FAIL si:

```text
se rompe salida owner-facing
se pierde EvidenceRecord
se pierde PipelineRunRecord
se elimina trazabilidad
se cambia diagnóstico/suficiencia
se introduce LLM
se introduce LangGraph
se abre UI/API/SaaS
se hardcodea más conocimiento
```

---

## 21. Política de commit

Un solo commit focal.

Mensaje sugerido para implementación futura:

```text
refactor(pymia-live): move question alignment rules to declarative contract
```

No push automático salvo autorización explícita posterior.

---

## 22. Auditoría post-implementación

Después del cambio, revisar diff y responder:

```text
Repo state
Sources read
Files changed
What was externalized
What remains hardcoded
Tests run
Evidence
Commit status
Push status
Next step
```

---

## 23. Auditoría externa recomendada

Pedir a Gemini / Opus / Qwen:

```text
Auditar si el refactor QUESTION_ALIGNMENT_DECLARATIVE_SANITIZATION_V1 preserva comportamiento y reduce deuda genética sin violar ADR-024.
Verificar:
- no cambio funcional visible
- no nuevo runtime de packs
- no contaminación de diagnostic_core
- no hardcodes residuales relevantes
- tests suficientes
- coherencia con PYMIA_DEVELOPMENT_METHOD
```

---

## 24. Riesgos

### Riesgo 1 — Convertir saneamiento en feature

Mitigación:

```text
no agregar nuevos ejes
no agregar nuevas reglas semánticas
no mejorar copy
sólo mover lo existente a contrato
```

### Riesgo 2 — Crear Pack Runtime prematuro

Mitigación:

```text
contrato local simple
loader simple
sin registry
sin discovery
sin versiones múltiples
```

### Riesgo 3 — Romper markdown

Mitigación:

```text
e2e obligatorio
comparar copy esperado
preservar status DELIVERED_CANDIDATE/BLOCKED
```

### Riesgo 4 — Sobredocumentar

Mitigación:

```text
no crear ADR nuevo
no crear roadmap nuevo
no crear manifiesto nuevo
sólo TaskSpec o checkpoint si se requiere
```

---

## 25. Roadmap de saneamiento posterior

Después de cerrar este corte, revisar si quedan hardcodes similares en:

```text
vertical_slice.py
owner-facing labels
pathology labels
field labels
formula labels
```

Sólo entonces considerar:

```text
owner_labels_v1
```

Pero `owner_labels_v1` no debe anteceder al saneamiento de `QuestionAlignmentGate`, porque el problema actual certificado está en el gate ya implementado.

---

## 26. Secuencia recomendada

```text
1. Verificar estado remoto/local.
2. Crear question_alignment_v1.json.
3. Crear question_alignment_v1.py.
4. Crear test_question_alignment_v1.py.
5. Refactorizar question_alignment_gate.py.
6. Refactorizar vertical_slice.py para consumir final_question_text del gate.
7. Ajustar tests existentes.
8. Ejecutar tests focales.
9. Revisar diff.
10. Commit focal.
11. Auditoría externa.
12. Decidir siguiente saneamiento.
```

---

## 27. Resultado esperado

Al terminar, `PymIA-Live` quedará así:

```text
QuestionAlignmentGate funcional
+
QuestionAlignmentGate declarativo
+
copy owner-facing gobernado por contrato
+
axis mappings fuera del runtime
+
menos deuda genética
+
sin nuevas features
+
sin romper baseline operativo
```

Frase de cierre:

```text
El saneamiento correcto no aumenta capacidad.
Aumenta gobernabilidad.
```
