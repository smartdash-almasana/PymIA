# SMARTPYME_INTAKE_RECORD_AND_EVIDENCE_REQUEST

## Estado y propósito

Documento canónico del slice de **Intake Record y Evidence Request** de SmartPyme.

Define la persistencia mínima determinística del flujo:

```
raw_text + structured_selectors
  → InterrogationResult
  → TankSelectionResult
  → IntakeRecord con IntakeEvidenceRequests
```

**Implementación propuesta en este slice:**
- `pymia/smartpyme/intake.py`
- `tests/smartpyme/test_intake.py`

**HEAD base:** `57ef4aa` (posterior a tank selection slice).

Este slice **no diagnostica**, **no ejecuta análisis**, **no procesa archivos**, **no genera reportes**.

Solo produce un registro serializable que documenta qué se recibió, qué se interrogó, qué tanques quedaron activos, qué evidencia se requiere y en qué estado está el intake.

## Problema que resuelve

Sin este slice:
- No hay registro formal de lo que el usuario planteó.
- No hay trazabilidad entre interrogatorio y selección de tanques.
- Los pedidos de evidencia son informales.
- No hay estado claro de cada caso.
- No hay base para futuras interacciones multi-turno.

Con este slice:
- Cada caso tiene un `IntakeRecord` con ID único.
- La evidencia requerida queda formalizada como `IntakeEvidenceRequest`.
- El estado del intake es explícito.
- Todo es serializable y auditable.

## Flujo completo

```
1. Usuario envía raw_text + selectores opcionales
       ↓
2. create_intake_record(tenant_id, raw_text, structured_selectors)
       ↓
3. Valida inputs (tenant_id no vacío, raw_text no vacío)
       ↓
4. run_interrogation(raw_text, structured_selectors)
   → InterrogationResult
       ↓
5. select_tanks(InterrogationResult)
   → TankSelectionResult
       ↓
6. Convierte EvidenceRequest → IntakeEvidenceRequest
       ↓
7. Resuelve intake_state
       ↓
8. Devuelve IntakeRecord serializable
```

## Contratos

### IntakeEvidenceRequest

```python
@dataclass
class IntakeEvidenceRequest:
    request_id: str               # ID único del pedido
    evidence_type: str            # ej. "excel_proveedores"
    description: str              # descripción humana
    required_fields: list[str]    # campos mínimos
    reason: str                   # por qué se pide
    blocks_analysis: bool         # si bloquea análisis
    enables_classification: str | None  # clasificación que habilita
    source_tank: str              # tanque que lo genera
    status: str                   # REQUESTED inicialmente
```

### IntakeRecord

```python
@dataclass
class IntakeRecord:
    intake_id: str                        # ID único del intake
    tenant_id: str                        # ID del tenant
    raw_input: str                        # texto crudo del usuario
    structured_selectors: dict            # selectores normalizados
    interrogation_result: dict            # InterrogationResult.to_dict()
    tank_selection_result: dict           # TankSelectionResult.to_dict()
    evidence_requests: list[IntakeEvidenceRequest]
    intake_state: str                     # estado del intake
    suggested_next_state: str             # próximo paso sugerido
    warnings: list[str]                   # advertencias de safety
    audit_notes: list[str]                # trazabilidad
    created_at: str                       # timestamp ISO
```

## Estados del IntakeRecord

| Estado | Significado |
|---|---|
| `RECEIVED` | Ingreso recibido, sin procesar |
| `INTERROGATED` | Interrogatorio completado, pendiente desambiguación/confirmación |
| `TANKS_SELECTED` | Tanques seleccionados, sin evidencia aún |
| `NEEDS_EVIDENCE` | Tanques activos piden evidencia |
| `READY_FOR_ANALYSIS` | Todo listo para ejecutar análisis |
| `BLOCKED` | Contexto insuficiente o fallo de safety |
| `UNSUPPORTED` | Caso fuera del alcance soportado |

### Reglas de transición determinísticas

```python
if interrogation.status == BLOCKED_INSUFFICIENT_CONTEXT:
    intake_state = BLOCKED
elif tank_selection.suggested_next_state == REQUEST_EVIDENCE:
    intake_state = NEEDS_EVIDENCE
elif tank_selection.suggested_next_state == READY_FOR_ANALYSIS:
    intake_state = READY_FOR_ANALYSIS
elif tank_selection.suggested_next_state == ASK_CLARIFICATION:
    intake_state = INTERROGATED
elif tank_selection.suggested_next_state == CONFIRM_REFORMULATION:
    intake_state = INTERROGATED
else:
    intake_state = BLOCKED  # fail-closed
```

## Estados del IntakeEvidenceRequest

| Estado | Significado |
|---|---|
| `REQUESTED` | Pedido creado, esperando respuesta |
| `RECEIVED` | Archivo/dato recibido, sin validar |
| `SATISFIED` | Evidencia validada y suficiente |
| `WAIVED` | Pedido descartado por el usuario/sistema |
| `BLOCKED` | Imposible obtener esta evidencia |

Estado inicial al crear el intake: **REQUESTED**.

## Safety gates aplicados

### NO_DIAGNOSIS_WITHOUT_EVIDENCE
El intake nunca produce diagnóstico confirmado. Solo registra síntomas candidatos, hipótesis y evidencia requerida.

### NO_SELECTOR_ONLY_ACTIVATION
Si solo hay selectores estructurales sin relato, el intake queda en `INTERROGATED` o `BLOCKED`, nunca en `READY_FOR_ANALYSIS`.

### NO_UNSUPPORTED_OUTPUT_PROMISE
El intake no promete outputs que el runtime no soporta (HTML, routing automático, etc.).

### RUNTIME_COMPATIBILITY_REQUIRED
`enables_classification` solo puede ser `excel_diagnostic` o `supplier_duplicate_check`. Cualquier otra clasificación queda excluida.

### FAIL_CLOSED ON INVALID INPUT
- `tenant_id` vacío → `ValueError`.
- `raw_text` vacío → `ValueError`.
- Estado indeterminado → `BLOCKED`.

## Relación con ReceptionRecord

`ReceptionRecord` (módulo `reception.py`) registra una recepción conversacional mínima dentro del flujo actual:

- `tenant_id`
- `message`
- `classification`
- `status`
- `evidence_refs`
- `output_refs`
- `created_at`

No registra todavía hash de archivo, MIME type, tamaño, ni estado físico de storage.

`IntakeRecord` registra el contexto semántico previo al análisis:

- qué dijo el usuario;
- qué se interrogó;
- qué tanques aplican;
- qué evidencia se necesita;
- qué próximo estado operativo corresponde.

Son complementarios:

- `IntakeRecord` puede existir sin archivo todavía.
- `ReceptionRecord` representa la recepción mínima ya existente.
- Un futuro slice puede vincular `IntakeRecord`, `ReceptionRecord` y metadata física de evidencia por `tenant_id` + `intake_id`.

## Relación con InterrogationResult

`InterrogationResult` es **insumo** del `IntakeRecord`:
- Se genera llamando a `run_interrogation(raw_text, selectors)`.
- Se persiste embebido como `interrogation_result: dict`.
- No se modifica; solo se serializa.

## Relación con TankSelectionResult

`TankSelectionResult` es **insumo** del `IntakeRecord`:
- Se genera llamando a `select_tanks(InterrogationResult)`.
- Se persiste embebido como `tank_selection_result: dict`.
- Sus `evidence_requests` se convierten a `IntakeEvidenceRequest` con ID propio.

## API pública

```python
from pymia.smartpyme.intake import create_intake_record, IntakeRecord

record = create_intake_record(
    tenant_id="tenant_001",
    raw_text="Tengo proveedores duplicados y CUIT mezclados",
    structured_selectors=None,  # opcional
)

# Serialización
d = record.to_dict()
import json
json.dumps(d, ensure_ascii=False)  # OK, sin custom encoder
```

## Ejemplos

### Ejemplo 1 — Proveedores duplicados

**Input:**
```python
create_intake_record(
    tenant_id="tenant_01",
    raw_text="Tengo proveedores duplicados y CUIT mezclados",
)
```

**Resultado:**
- `intake_state`: `NEEDS_EVIDENCE`
- `evidence_requests`: 1 con `evidence_type="excel_proveedores"`
- `enables_classification`: `supplier_duplicate_check`
- `source_tank`: `SMARTPYME_EVIDENCE_AND_FORMULA_TANK`
- `status`: `REQUESTED`

### Ejemplo 2 — Margen dudoso con Excel

**Input:**
```python
create_intake_record(
    tenant_id="tenant_02",
    raw_text="RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY, tengo todo en Excel",
)
```

**Resultado:**
- `intake_state`: `NEEDS_EVIDENCE`
- `evidence_requests`: incluye `excel_ventas_costos`
- `enables_classification`: `excel_diagnostic`

### Ejemplo 3 — Descuadre de plata

**Input:**
```python
create_intake_record(
    tenant_id="tenant_03",
    raw_text="No me cierra la plata",
)
```

**Resultado:**
- `intake_state`: `INTERROGATED`
- `suggested_next_state`: `ASK_CLARIFICATION`
- `evidence_requests`: puede tener `excel_caja_banco`

### Ejemplo 4 — Selector-only

**Input:**
```python
create_intake_record(
    tenant_id="tenant_04",
    raw_text="quiero revisar mi negocio",
    structured_selectors=StructuredSelectors(
        sales_channel="Mercado Libre",
        stock_mode="Informal",
    ),
)
```

**Resultado:**
- `intake_state`: `INTERROGATED` o `BLOCKED`
- `evidence_requests`: vacío
- `warnings`: incluye "selector-only"

### Ejemplo 5 — Input inválido

```python
create_intake_record(tenant_id="", raw_text="hola")
# → ValueError: tenant_id must be a non-empty string
```

## No-objetivos explícitos

Este slice **NO**:
- Diagnostica.
- Ejecuta fórmulas.
- Procesa archivos.
- Genera reportes (MD/HTML/JSON).
- Modifica clasificaciones existentes.
- Hace routing automático.
- Interactúa con Hermes real.
- Genera HTML.
- Persiste en base de datos (solo devuelve objeto en memoria).
- Reemplaza `ReceptionRecord`.

## Tests

```bash
python -m pytest tests/smartpyme/test_intake.py -q
```

Cobertura:
- Validación de inputs (6 tests)
- Caso proveedor duplicado (4 tests)
- Caso margen/costo (2 tests)
- Selector-only (2 tests)
- BLOCKED (2 tests)
- Serialización JSON (3 tests)
- No clasificaciones no soportadas (2 tests)
- Integridad del IntakeRecord (7 tests)
- Descuadre dinero (2 tests)
- Estados permitidos (2 tests)

Total: **32 tests**.

## Gaps conocidos

- No hay persistencia en base de datos.
- No hay vinculación formal con `ReceptionRecord`.
- No hay multi-turno (el intake es single-shot).
- No hay actualización de estado tras recibir evidencia.
- No hay validación de archivos contra `required_fields`.
- No hay integración con `e2e_cli`.
- No hay UI para mostrar evidencia requests al usuario.

## Roadmap posterior

1. **SMARTPYME_INTAKE_MULTI_TURN**
   - Permitir actualizar `IntakeRecord` con nuevas respuestas del usuario.
   - Cambiar estados de `IntakeEvidenceRequest` (REQUESTED → RECEIVED → SATISFIED).

2. **SMARTPYME_INTAKE_RECEPTION_LINK**
   - Vincular `IntakeRecord` con `ReceptionRecord` por `tenant_id` + `intake_id`.
   - Validar archivo recibido contra `required_fields`.

3. **SMARTPYME_INTAKE_CLI_INTEGRATION**
   - Integrar `create_intake_record` en `e2e_cli` como primer paso del flujo.
   - Persistir `IntakeRecord` en storage por tenant.

4. **SMARTPYME_INTAKE_EVIDENCE_VALIDATION**
   - Validar evidencia recibida contra `required_fields` del `IntakeEvidenceRequest`.
   - Cambiar estado a `SATISFIED` o `BLOCKED` según resultado.

## Cierre

> El IntakeRecord no decide por SmartPyme. Documenta trazablemente qué se recibió, qué se interrogó, qué tanques aplican y qué evidencia se requiere, bajo safety gates y compatibilidad runtime.
