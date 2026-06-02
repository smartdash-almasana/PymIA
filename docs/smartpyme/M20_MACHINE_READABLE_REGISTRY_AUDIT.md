# M20 — Capability Registry Machine-Readable Audit

Fecha: 2026-06-03
Estado: auditoría de lectura pesada completada
Alcance: registry de capacidades SmartPyme, fuente de verdad legible por máquina.

---

## 1. Veredicto

```text
M20 Capability Registry Machine-Readable = READY_FOR_GEMINI_REVIEW
```

El registry actual en Markdown es insuficiente para que Pipeline Radiography, el dispatcher o la IA residente consulten capacidades sin inferir. Se requiere un archivo YAML/JSON con schema validado y un lector mínimo en Python.

---

## 2. Capacidades actuales: Markdown vs Código

### 2.1 Capacidades con plugin ejecutable

| capability_id | Markdown status | Código real | Dispatcher formal | Pipeline Radiography (M19) |
|---|---|---|---|---|
| `excel_diagnostic` | `AVAILABLE` | `pymia.smartpyme.excel_diagnostic.diagnose_excel` | `EXECUTED` | `PIPELINE_CERTIFIED` |
| `supplier_duplicate_check` | `PARTIALLY_AVAILABLE_BY_PATH` | `pymia.smartpyme.classifications.supplier_duplicate_check.diagnose_supplier_duplicates` | `UNSUPPORTED` | No cubierto |

### 2.2 Módulos contractuales del pipeline

| capability_id | Markdown status | Código real | Rol |
|---|---|---|---|
| `evidence_record` | `IMPLEMENTED` | `pymia.smartpyme.evidence` | metadata_contract |
| `evidence_gate` | `IMPLEMENTED` | `pymia.smartpyme.evidence_gate` | sufficiency_gate |
| `readiness_gate` | `IMPLEMENTED` | `pymia.smartpyme.readiness` | analysis_readiness_gate |
| `runtime_bridge` | `IMPLEMENTED` | `pymia.smartpyme.runtime_bridge` | execution_candidate_builder |
| `microservice_dispatcher` | `IMPLEMENTED_LIMITED` | `pymia.smartpyme.microservice_dispatcher` | dispatcher |
| `delivery_package` | `IMPLEMENTED` | `pymia.smartpyme.delivery_package` | delivery_builder |

### 2.3 Módulos conversacionales

| capability_id | Markdown status | Código real | Rol |
|---|---|---|---|
| `anamnesis_fsm` | `IMPLEMENTED` | `pymia.smartpyme.anamnesis_fsm` | conversational_profile_builder |
| `anamnesis_fsm_integration` | `IMPLEMENTED` | `pymia.smartpyme.anamnesis_fsm_integration` | integration_wrapper |

### 2.4 No localizados / no prometer

| capability_id | Markdown status | Código real | Nota |
|---|---|---|---|
| `report_html` | `MISSING_IN_REMOTE` | `NOT_FOUND` | No existe en `pymia/smartpyme/` |
| `document_parser_front` | `MISSING_IN_REMOTE` | `NOT_FOUND` | No existe en `pymia/smartpyme/` |
| `telegram_adapter_smartpyme` | `NEEDS_PATH_CONFIRMATION` | `NOT_FOUND` en `pymia/smartpyme/` | Vive en `conversa-engine/` |

---

## 3. Campos mínimos recomendados

El schema machine-readable debe incluir:

```yaml
capability_id: str          # requerido, único
label: str                  # nombre legible
domain: list[str]           # ej: ["comercial", "financiero"]
status: enum                # ver sección 4
pipeline_certified: bool    # true si pasa radiografía e2e
dispatcher_available: bool  # true si dispatcher formal lo ejecuta
cli_available: bool         # true si e2e_cli lo ejecuta
plugin_module: str | null   # ej: "pymia.smartpyme.excel_diagnostic"
plugin_function: str | null # ej: "diagnose_excel"
dispatcher_classification: str | null  # ej: "excel_diagnostic"
required_evidence_types: list[str]     # ej: ["excel_ventas_costos"]
output_kinds: list[str]     # ej: ["findings", "markdown_report"]
tests: list[str]            # paths de tests que lo cubren
docs: list[str]             # paths de documentación
notes: list[str]            # notas operativas
no_promise_reason: str | null  # por qué no debe prometerse
```

---

## 4. Estados recomendados

```text
PIPELINE_CERTIFIED          # pasa radiografía e2e OK (M19)
AVAILABLE                   # implementado y conectado por dispatcher y/o CLI
PARTIALLY_AVAILABLE_BY_PATH # implementado pero solo por CLI o solo por dispatcher
UNSUPPORTED_IN_DISPATCHER   # el dispatcher lo rechaza explícitamente
DOCUMENTED_NOT_IMPLEMENTED  # documentado pero no hay código
NOT_FOUND                   # no hay código ni documentación clara
CONCEPTUAL                  # idea sin implementación
```

---

## 5. Formato recomendado

### 5.1 Archivo

```text
pymia/smartpyme/capabilities.yaml
```

**Por qué YAML y no JSON:**
- YAML es más legible para mantenimiento humano.
- YAML soporta comentarios (útil para `notes` y `no_promise_reason`).
- Python tiene librerías estándar (`PyYAML` o `ruamel.yaml`) para cargarlo.

**Por qué no Python dataclass estático:**
- Un archivo YAML permite actualizar el registry sin tocar código Python.
- Facilita que herramientas externas (IA residente, scripts de auditoría) lean el registry sin importar módulos.

### 5.2 Estructura del archivo

```yaml
version: "1.0"
capabilities:
  - capability_id: excel_diagnostic
    label: Diagnóstico Excel
    domain: [comercial, financiero, stock, compras]
    status: PIPELINE_CERTIFIED
    pipeline_certified: true
    dispatcher_available: true
    cli_available: true
    plugin_module: pymia.smartpyme.excel_diagnostic
    plugin_function: diagnose_excel
    dispatcher_classification: excel_diagnostic
    required_evidence_types: [excel_file, excel_ventas_costos]
    output_kinds: [findings, markdown_report]
    tests:
      - tests/smartpyme/test_excel_diagnostic.py
      - tests/smartpyme/e2e/test_pipeline_radiography_excel.py
    docs:
      - docs/smartpyme/SMARTPYME_CAPABILITY_PLUGIN_REGISTRY.md
    notes:
      - Diagnóstico inicial sobre evidencia tabular.
      - No equivale a diagnóstico total de empresa.
    no_promise_reason: null

  - capability_id: supplier_duplicate_check
    label: Revisión de proveedores duplicados
    domain: [proveedores, datos_maestros]
    status: PARTIALLY_AVAILABLE_BY_PATH
    pipeline_certified: false
    dispatcher_available: false
    cli_available: true
    plugin_module: pymia.smartpyme.classifications.supplier_duplicate_check
    plugin_function: diagnose_supplier_duplicates
    dispatcher_classification: supplier_duplicate_check
    required_evidence_types: [excel_proveedores]
    output_kinds: [findings, markdown_report]
    tests:
      - tests/smartpyme/test_supplier_duplicate_check.py
    docs:
      - docs/smartpyme/SMARTPYME_CAPABILITY_PLUGIN_REGISTRY.md
      - docs/smartpyme/M17_SUPPLIER_DISPATCHER_CONTRACT_FINDING.md
    notes:
      - Funciona por camino CLI.
      - No está conectado al dispatcher formal.
    no_promise_reason: No debe prometerse como disponible por dispatcher hasta M17.
```

---

## 6. Lector mínimo requerido

### 6.1 Módulo

```text
pymia/smartpyme/capability_registry.py
```

### 6.2 API mínima

```python
def load_registry(path: str | Path | None = None) -> dict:
    """Carga capabilities.yaml y retorna dict con schema validado."""

def get_capability(capability_id: str) -> dict | None:
    """Retorna la capacidad por ID o None si no existe."""

def list_capabilities(status: str | None = None) -> list[dict]:
    """Lista capacidades, opcionalmente filtradas por status."""

def is_pipeline_certified(capability_id: str) -> bool:
    """Retorna True si la capacidad está PIPELINE_CERTIFIED."""

def is_dispatcher_available(capability_id: str) -> bool:
    """Retorna True si la capacidad está disponible en dispatcher formal."""
```

### 6.3 Validaciones

- `capability_id` debe ser único.
- `status` debe estar en el enum permitido.
- `plugin_module` y `plugin_function` deben ser consistentes (si uno existe, el otro también).

---

## 7. Archivos que tocaría Codex

```text
pymia/smartpyme/capabilities.yaml              # nuevo
pymia/smartpyme/capability_registry.py         # nuevo
tests/smartpyme/test_capability_registry.py    # nuevo
docs/smartpyme/SMARTPYME_CAPABILITY_PLUGIN_REGISTRY.md  # actualizar para referenciar YAML
```

---

## 8. Tests mínimos requeridos

### 8.1 Test de carga

```python
def test_load_registry_valid():
    registry = load_registry()
    assert "capabilities" in registry
    assert len(registry["capabilities"]) > 0
```

### 8.2 Test de validación de schema

```python
def test_registry_schema_validation():
    # Debe fallar si capability_id falta
    # Debe fallar si status no es válido
```

### 8.3 Test de consulta

```python
def test_get_capability():
    cap = get_capability("excel_diagnostic")
    assert cap is not None
    assert cap["status"] == "PIPELINE_CERTIFIED"
    assert cap["pipeline_certified"] is True
```

### 8.4 Test de estados actuales

```python
def test_current_capability_states():
    assert is_pipeline_certified("excel_diagnostic")
    assert is_dispatcher_available("excel_diagnostic")
    
    supplier = get_capability("supplier_duplicate_check")
    assert supplier["status"] == "PARTIALLY_AVAILABLE_BY_PATH"
    assert supplier["dispatcher_available"] is False
```

---

## 9. Riesgos: M17 antes vs después de M20

### 9.1 Si M17 se hace antes de M20

```text
- M17 cambia el contrato del dispatcher para soportar supplier_duplicate_check.
- El registry en Markdown debe actualizarse manualmente.
- No hay validación automática de que el registry refleje el nuevo estado.
- La deuda técnica de "fuente de verdad no legible por máquina" persiste.
- Pipeline Radiography no puede consultar el registry para decidir qué escenarios correr.
```

### 9.2 Si M20 se hace antes de M17

```text
- M20 establece el registry machine-readable con el estado actual.
- M17 solo necesita actualizar capabilities.yaml (dispatcher_available: true, status: AVAILABLE).
- Los tests de M17 pueden verificar que el registry se actualizó correctamente.
- Pipeline Radiography puede consultar el registry para descubrir capacidades certificadas.
- La IA residente puede consultar el registry para saber qué puede ejecutar.
```

### 9.3 Recomendación

```text
M20 antes de M17.
```

Motivo: M20 establece la infraestructura de gobernanza de capacidades. M17 es un cambio de contrato que se beneficia de tener un registry machine-readable para validar que el cambio se reflejó correctamente.

---

## 10. Qué no debe hacer M20

```text
- No conectar supplier_duplicate_check al dispatcher (eso es M17).
- No implementar nuevas capacidades.
- No cambiar la lógica de excel_diagnostic.
- No mezclar Telegram/PDF/HTML/UI.
- No inferir estados desde el código; el registry debe ser la fuente de verdad declarativa.
```

---

## 11. Frase rectora

```text
Un registry que solo los humanos pueden leer no es una fuente de verdad.
M20 convierte el registry en una máquina consultable.
```
