# SMARTPYME_E2E_NON_EXECUTING_FLOW

## Propósito

Smoke test E2E determinístico que valida el flujo completo de SmartPyme sin ejecutar microservicios ni análisis reales.

Este test demuestra que todos los slices del intake pipeline funcionan correctamente de forma integrada:

```
create_intake_record
→ save_intake_record
→ create_evidence_record
→ save_evidence_record
→ load_intake_record_by_id
→ load_evidence_records_by_intake_id
→ evaluate_evidence_sufficiency
→ evaluate_analysis_readiness
→ AnalysisReadinessResult (READY_FOR_ANALYSIS)
```

## Alcance

Este smoke test:

- **SÍ** crea IntakeRecord con evidencia solicitada
- **SÍ** persiste en JSONL real (tmp_path)
- **SÍ** carga desde storage
- **SÍ** evalúa suficiencia de evidencia
- **SÍ** evalúa readiness para análisis
- **SÍ** verifica que NO se importen runtime modules
- **NO** ejecuta excel_diagnostic
- **NO** ejecuta supplier_duplicate_check
- **NO** procesa archivos Excel/PDF
- **NO** calcula hashes
- **NO** lee contenido documental
- **NO** despacha microservicios

## Flujo E2E

### 1. Crear IntakeRecord

```python
from pymia.smartpyme.intake import create_intake_record

intake = create_intake_record(
    tenant_id="tenant_e2e",
    raw_text="Tengo un Excel con ventas y costos pero no me cierra la plata",
)
```

Resultado:
- InterrogationResult con síntomas detectados
- TankSelectionResult con tanques activos
- EvidenceRequests con tipos de evidencia requerida
- intake_state = NEEDS_EVIDENCE

### 2. Persistir IntakeRecord

```python
from pymia.smartpyme.storage import save_intake_record

save_intake_record(
    tenant_id,
    intake,
    base_dir=tmp_path / "storage"
)
```

Resultado:
- `<base_dir>/<tenant_id>/intakes.jsonl` con 1 línea JSON

### 3. Crear EvidenceRecord

```python
from pymia.smartpyme.evidence import (
    create_evidence_record,
    SOURCE_KIND_UPLOADED_FILE,
    EVIDENCE_STATUS_RECEIVED,
)

evidence = create_evidence_record(
    tenant_id=tenant_id,
    intake_id=intake.intake_id,
    evidence_type=first_request.evidence_type,
    source_kind=SOURCE_KIND_UPLOADED_FILE,
    source_ref="/path/to/ventas_costos.xlsx",
    request_id=first_request.request_id,
    status=EVIDENCE_STATUS_RECEIVED,
)
```

Resultado:
- EvidenceRecord con metadata (no lee archivo)
- request_id vincula con IntakeEvidenceRequest

### 4. Persistir EvidenceRecord

```python
from pymia.smartpyme.storage import save_evidence_record

save_evidence_record(
    tenant_id,
    evidence,
    base_dir=tmp_path / "storage"
)
```

Resultado:
- `<base_dir>/<tenant_id>/evidences.jsonl` con 1 línea JSON

### 5. Cargar desde storage

```python
from pymia.smartpyme.storage import (
    load_intake_record_by_id,
    load_evidence_records_by_intake_id,
)

loaded_intake = load_intake_record_by_id(
    tenant_id, intake.intake_id, base_dir=base_dir
)

loaded_evidences = load_evidence_records_by_intake_id(
    tenant_id, intake.intake_id, base_dir=base_dir
)
```

Resultado:
- `loaded_intake`: dict con todos los campos
- `loaded_evidences`: list[dict] con 1 elemento

### 6. Evaluar suficiencia de evidencia

```python
from pymia.smartpyme.evidence_gate import evaluate_evidence_sufficiency

sufficiency = evaluate_evidence_sufficiency(
    loaded_intake,
    loaded_evidences
)
```

Resultado:
- EvidenceSufficiencyResult
- status = READY (si evidence_request está satisfecha)
- matched_evidence_ids poblado
- missing_request_ids vacío

### 7. Evaluar readiness para análisis

```python
from pymia.smartpyme.readiness import evaluate_analysis_readiness

readiness = evaluate_analysis_readiness(
    loaded_intake,
    sufficiency.to_dict()
)
```

Resultado:
- AnalysisReadinessResult
- status = READY_FOR_ANALYSIS
- can_execute = True
- runtime_classification = "excel_diagnostic" o "supplier_duplicate_check"

## Tests incluidos

### 1. test_import_smoke

Verifica que todos los módulos requeridos pueden importarse:
- `create_intake_record`
- `create_evidence_record`
- `save_intake_record`
- `save_evidence_record`
- `load_intake_record_by_id`
- `load_evidence_records_by_intake_id`
- `evaluate_evidence_sufficiency`
- `evaluate_analysis_readiness`

### 2. test_e2e_non_executing_flow_ready_for_excel_diagnostic

Escenario:
- Input: "Tengo un Excel con ventas y costos pero no me cierra la plata"
- Evidence: Excel file matching evidence_request
- Expected:
  - sufficiency.status = READY
  - readiness.status = READY_FOR_ANALYSIS
  - readiness.can_execute = True
  - readiness.runtime_classification = "excel_diagnostic"

### 3. test_e2e_non_executing_flow_ready_for_supplier_duplicate_check

Escenario:
- Input: "Tengo proveedores duplicados en el Excel con CUIT repetidos"
- Evidence: Excel file matching evidence_request
- Expected:
  - sufficiency.status = READY
  - readiness.status = READY_FOR_ANALYSIS
  - readiness.can_execute = True
  - readiness.runtime_classification = "supplier_duplicate_check"

### 4. test_e2e_non_executing_flow_needs_evidence_when_evidence_missing

Escenario:
- Input: "No me cierra la plata pero no tengo archivos"
- Evidence: vacío
- Expected:
  - Si hay blocking evidence_requests:
    - readiness.status = NEEDS_EVIDENCE
    - readiness.can_execute = False

### 5. test_e2e_does_not_execute_runtime_modules

Verifica que el flujo E2E NO importa:
- `pymia.smartpyme.excel_diagnostic`
- `pymia.smartpyme.supplier_duplicate_check`

Mide `sys.modules` antes y después del flujo.

## Safety gates

Este smoke test:

- ✅ No ejecuta análisis reales
- ✅ No importa runtime modules
- ✅ No procesa archivos
- ✅ No lee contenido documental
- ✅ No calcula hashes
- ✅ No despacha microservicios
- ✅ Usa tmp_path (aislado)
- ✅ Persiste en JSONL real
- ✅ Carga desde storage

## Relación con otros slices

### Intake pipeline (completo)

```
SMARTPYME_INTERROGATION_TAXONOMY_SLICE
  → InterrogationResult

SMARTPYME_TANK_SELECTION_SLICE
  → TankSelectionResult + EvidenceRequests

SMARTPYME_INTAKE_RECORD_AND_EVIDENCE_REQUEST
  → IntakeRecord

SMARTPYME_INTAKE_STORAGE_PERSISTENCE
  → save_intake_record / load_intake_record_by_id

SMARTPYME_EVIDENCE_RECORD_MINIMAL
  → EvidenceRecord

SMARTPYME_EVIDENCE_STORAGE_PERSISTENCE
  → save_evidence_record / load_evidence_records_by_intake_id

SMARTPYME_EVIDENCE_SUFFICIENCY_GATE
  → EvidenceSufficiencyResult

SMARTPYME_READY_FOR_ANALYSIS_GATE
  → AnalysisReadinessResult

SMARTPYME_E2E_NON_EXECUTING_FLOW (este slice)
  → Valida integración completa
```

### Próximo slice recomendado

**SMARTPYME_INTAKE_STATE_TRANSITION**

Objetivo:
- Aplicar AnalysisReadinessResult para actualizar intake_state
- Transición: NEEDS_EVIDENCE → READY_FOR_ANALYSIS
- Persistir nuevo estado en intakes.jsonl

Integración:
```python
intake = load_intake_record_by_id(...)
evidences = load_evidence_records_by_intake_id(...)
sufficiency = evaluate_evidence_sufficiency(intake, evidences)
readiness = evaluate_analysis_readiness(intake, sufficiency.to_dict())

if readiness.status == "READY_FOR_ANALYSIS":
    intake.intake_state = "READY_FOR_ANALYSIS"
    save_intake_record(intake.tenant_id, intake, base_dir=...)
```

## Ejecución

```bash
# Solo este test
python -m pytest tests/smartpyme/test_e2e_non_executing_flow.py -q

# Con readiness y evidence_gate
python -m pytest tests/smartpyme/test_readiness.py \
                  tests/smartpyme/test_evidence_gate.py \
                  tests/smartpyme/test_e2e_non_executing_flow.py -q

# Suite completa
python -m pytest tests/smartpyme/test_interrogation.py \
                  tests/smartpyme/test_tank_selection.py \
                  tests/smartpyme/test_intake.py \
                  tests/smartpyme/test_intake_storage.py \
                  tests/smartpyme/test_evidence.py \
                  tests/smartpyme/test_evidence_storage.py \
                  tests/smartpyme/test_evidence_gate.py \
                  tests/smartpyme/test_readiness.py \
                  tests/smartpyme/test_e2e_non_executing_flow.py -q
```

## No-goals

Este smoke test NO:

- Ejecuta excel_diagnostic
- Ejecuta supplier_duplicate_check
- Procesa archivos Excel/PDF
- Lee contenido documental
- Calcula hashes
- Valida contenido de evidencia
- Despacha microservicios
- Crea CLI
- Crea runtime/job
- Actualiza intake_state (eso es SMARTPYME_INTAKE_STATE_TRANSITION)

## Limitaciones

1. **Depende de fixtures realistas**: Los tests usan inputs específicos que deben generar evidence_requests. Si el input no genera requests, el test hace `pytest.skip`.

2. **No valida contenido**: Solo verifica que EvidenceRecord existe y tiene metadata correcta. No abre archivos.

3. **No ejecuta análisis**: El flujo termina en AnalysisReadinessResult. No hay un slice posterior que ejecute el runtime (todavía).

## Git history

```
<commit> test(smartpyme): add non executing e2e flow
```

Archivos incluidos:
- `tests/smartpyme/test_e2e_non_executing_flow.py` (13,229 bytes)
- `docs/smartpyme/SMARTPYME_E2E_NON_EXECUTING_FLOW.md` (este archivo)

## Verificación

```bash
git status --short
# ?? docs/mermaid/  (ruido conocido)

git log --oneline -1
# <hash> test(smartpyme): add non executing e2e flow
```
