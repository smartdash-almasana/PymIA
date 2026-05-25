# SMARTPYME_TANK_SELECTION_SLICE

## 1. Estado y propósito

**Estado:** Implementado y testeado (slice mínimo determinístico).

**Propósito:** Selección determinística de KnowledgeTanks a partir de `InterrogationResult`.

Este slice:
- **NO** ejecuta análisis
- **NO** procesa archivos
- **NO** diagnostica
- **NO** reemplaza clasificaciones reales
- **NO** asume routing automático
- **NO** asume HTML output

Produce `TankSelectionResult` serializable que indica:
- qué tanques están activos
- qué tanques son candidatos
- qué tanques están desactivados
- qué evidencia pedir
- qué warnings aplicar
- qué próximo estado sugiere

## 2. Relación con la arquitectura

Referencia:
- `SMARTPYME_KNOWLEDGE_TANKS_CONTRACT.md` (contrato formal)
- `SMARTPYME_KNOWLEDGE_TANKS_ARCHITECTURE.md` (subarquitectura)
- `SMARTPYME_OPERATIONAL_PATHOLOGY_TANK.md` (primer tanque)
- `SMARTPYME_EVIDENCE_AND_FORMULA_TANK.md` (segundo tanque)
- `SMARTPYME_INTERROGATION_SLICE.md` (slice previo)

Flujo:
```
raw_text + selectors
  → InterrogationResult (interrogation.py)
  → TankSelectionResult (tank_selection.py)
  → EvidenceRequest (conceptual)
  → [futuro] análisis ejecutable
```

## 3. API pública

```python
from pymia.smartpyme.interrogation import run_interrogation
from pymia.smartpyme.tank_selection import select_tanks

ir = run_interrogation("Tengo proveedores duplicados y CUIT mezclados")
result = select_tanks(ir)
```

## 4. Tanques soportados

| tank_id | Activador principal | Desactivador principal |
|---------|---------------------|------------------------|
| `SMARTPYME_OPERATIONAL_PATHOLOGY_TANK` | Síntomas reales != DESCONOCIDO | Contexto insuficiente / solo selectores |
| `SMARTPYME_EVIDENCE_AND_FORMULA_TANK` | evidence_needs + clasificación sugerida | Sin evidence_needs ni clasificación |

## 5. Estados del ciclo de vida

| Estado | Significado |
|--------|-------------|
| `AVAILABLE` | Tanque existe en catálogo pero no aplica al caso |
| `CANDIDATE` | Señales iniciales sugieren que puede aplicar |
| `ACTIVE` | Condiciones suficientes para aportar preguntas/evidencia |
| `SUSPENDED` | Señales contradictorias, puede reactivarse |
| `DEACTIVATED` | No aplica al caso (ej. contexto bloqueado) |
| `REJECTED` | Explícitamente descartado |

## 6. TankSelectionResult

```python
@dataclass
class TankSelectionResult:
    input_summary: str
    selected_tanks: List[TankEvaluation]      # ACTIVE
    candidate_tanks: List[TankEvaluation]     # CANDIDATE
    suspended_tanks: List[TankEvaluation]     # SUSPENDED
    rejected_tanks: List[TankEvaluation]      # DEACTIVATED/AVAILABLE/REJECTED
    evidence_requests: List[EvidenceRequest]
    warnings: List[str]
    suggested_next_state: str
    suggested_classifications: List[str]
    runtime_compatibility: Dict[str, bool]
    audit_notes: List[str]
```

Serializable vía `result.to_dict()` → JSON.

## 7. Safety gates aplicados

| Gate | Aplicación |
|------|-----------|
| `NO_SELECTOR_ONLY_ACTIVATION` | Selectores sin relato → tanques AVAILABLE, no ACTIVE |
| `NO_DIAGNOSIS_WITHOUT_EVIDENCE` | Ningún tanque produce diagnóstico confirmado |
| `RUNTIME_COMPATIBILITY_REQUIRED` | Solo sugiere `excel_diagnostic` y `supplier_duplicate_check` |
| `NO_UNSUPPORTED_OUTPUT_PROMISE` | `unsupported_outputs` explícito por tanque |
| `FAIL_CLOSED_ON_CONFLICT` | Contexto insuficiente → DEACTIVATED |

## 8. Próximos estados sugeridos

| Estado | Cuándo aplica |
|--------|--------------|
| `ASK_CLARIFICATION` | `InterrogationResult.status == NEEDS_DISAMBIGUATION` |
| `REQUEST_EVIDENCE` | Al menos un tanque ACTIVE con evidence_needs |
| `CONFIRM_REFORMULATION` | Tanques CANDIDATE pero no ACTIVE |
| `BLOCKED` | `InterrogationResult.status == BLOCKED_INSUFFICIENT_CONTEXT` |
| `READY_FOR_ANALYSIS` | (reservado para futuro, no se alcanza en este slice) |

## 9. Runtime compatibility

```python
runtime_compatibility = {
    "excel_diagnostic": True,
    "supplier_duplicate_check": True,
    "classification_auto": False,
    "html_output": False,
    "cash_reconciliation": False,
    "margin_analysis": False,
}
```

Solo las dos clasificaciones reales están marcadas como compatibles.

## 10. Ejemplos

### Ejemplo 1 — Proveedores duplicados
```python
ir = run_interrogation("Tengo proveedores duplicados y CUIT mezclados")
result = select_tanks(ir)
# Operational Pathology: ACTIVE (score >= 40)
# Evidence & Formula: CANDIDATE/ACTIVE
# suggested_next_state: REQUEST_EVIDENCE
# suggested_classifications: ["supplier_duplicate_check"]
# evidence_requests: [{excel_proveedores}]
```

### Ejemplo 2 — Texto vacío
```python
ir = run_interrogation("")
result = select_tanks(ir)
# Ambos tanques: DEACTIVATED
# suggested_next_state: BLOCKED
# evidence_requests: []
```

### Ejemplo 3 — Solo selectores
```python
sel = StructuredSelectors(sales_channel="Mercado Libre", tools_used="Excel")
ir = run_interrogation("quiero revisar mi negocio", sel)
result = select_tanks(ir)
# Operational Pathology: AVAILABLE (no activado por selector solo)
# warnings: ["Solo selectores estructurales sin relato..."]
```

### Ejemplo 4 — Descuadre de dinero
```python
ir = run_interrogation("No me cierra la plata")
result = select_tanks(ir)
# Operational Pathology: ACTIVE/CANDIDATE
# suggested_next_state: ASK_CLARIFICATION
# evidence_requests: [{excel_caja_banco}]
```

## 11. Archivos

- `pymia/smartpyme/tank_selection.py` — Implementación (20 KB)
- `tests/smartpyme/test_tank_selection.py` — Tests (12 KB, 25+ casos)

## 12. Tests mínimos

```bash
python -m pytest tests/smartpyme/test_tank_selection.py -v
```

Cobertura:
- Activación por síntomas reales
- Activación de Evidence and Formula por evidence_needs
- NO_SELECTOR_ONLY_ACTIVATION
- Clasificaciones runtime-compatible
- Texto vacío/bloqueado
- Serialización JSON
- TypeError por input inválido
- End-to-end (proveedores, sobrecarga, stock, mercado libre)

## 13. Limitaciones explícitas

Este slice NO:
- Carga YAML de tanques
- Implementa DomainPacks
- Ejecuta fórmulas
- Procesa archivos
- Genera reportes
- Asume routing automático
- Asume HTML output

## 14. Gaps conocidos

- No hay loader YAML de tanques
- No hay integración con `e2e_cli`
- No hay `IntakeRecord` persistente
- No hay `EvidenceRequest` formal implementado (solo conceptual)
- No hay DomainPack ejecutable

## 15. Roadmap posterior

1. `SMARTPYME_INTAKE_RECORD_AND_EVIDENCE_REQUEST` — Persistir `InterrogationResult` + `TankSelectionResult` y generar pedidos de evidencia formales.
2. Implementación de DomainPacks como agrupaciones versionadas.
3. Integración con `e2e_cli` para selección asistida de clasificación.
4. Loader YAML de tanques (cuando los YAMLs existan).

## 16. Cierre

> Los tanques seleccionados no diagnostican. Preparan el terreno para pedir la evidencia correcta y habilitar análisis trazables.
