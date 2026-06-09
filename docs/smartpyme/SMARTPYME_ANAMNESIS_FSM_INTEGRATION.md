# SMARTPYME_ANAMNESIS_FSM_INTEGRATION

## Estado: Aceptado

## Resumen

Wrapper puro y determinístico que integra el FSM de anamnesis offline (`anamnesis_fsm.py`) con el flujo local de sesión/`progressive_context`, permitiendo probar conversación con estado antes de Telegram real.

Este módulo **NO** usa Telegram, **NO** usa red, **NO** usa I/O, **NO** ejecuta microservicios, **NO** lee Excel, **NO** diagnostica.

## Objetivo

Proveer una capa de integración que:

1. Recibe `tenant_id`, `session_id`, `message_text` y `previous_progressive_context`
2. Reconstruye `AnamnesisFSMState` desde `progressive_context` si existe
3. Llama a `process_message()` del FSM offline
4. Devuelve `reply_text` + `updated_progressive_context` serializable
5. Preserva estado entre turnos sin persistencia
6. Fail-closed si contexto está corrupto

## Contratos

## Semántica de taxonomía

Desde el commit `938c1f7`, este wrapper distingue explícitamente entre:

- `has_taxonomy`: significa taxonomía confirmada;
- `has_confirmed_taxonomy`: alias explícito de taxonomía confirmada;
- `has_preliminary_taxonomy`: indica que el primer mensaje natural tuvo señales fuertes;
- `preliminary_taxonomy`: señal auxiliar no confirmada derivada del `raw_first_message`.

Reglas:

1. `preliminary_taxonomy` no habilita hipótesis investigables.
2. `preliminary_taxonomy` no habilita `evidence_requests`.
3. `preliminary_taxonomy` no habilita diagnóstico.
4. `preliminary_taxonomy` no habilita ejecución.
5. `preliminary_taxonomy` no habilita salto de ficha.
6. La ficha inicial sigue siendo obligatoria:
   - `phase == FICHA_PYME_INICIAL`
   - `profile_step == ASK_CONTACT_NAME`
   - `raw_first_message` preservado
7. La taxonomía confirmada sólo nace después, usando `profile_data` confirmado.
8. `preliminary_taxonomy` puede servir como señal auxiliar, nunca como verdad soberana.

### AnamnesisTurnInput

```python
@dataclass(frozen=True)
class AnamnesisTurnInput:
    tenant_id: str
    session_id: str
    message_text: str
    previous_progressive_context: dict[str, Any] | None = None
```

**Campos:**
- `tenant_id`: Identificador del tenant (obligatorio)
- `session_id`: Identificador de sesión (obligatorio)
- `message_text`: Texto del usuario (puede ser vacío)
- `previous_progressive_context`: Contexto previo serializado (None si sesión nueva)

### AnamnesisTurnOutput

```python
@dataclass(frozen=True)
class AnamnesisTurnOutput:
    reply_text: str
    updated_progressive_context: dict[str, Any]
    phase: str
    has_hypotheses: bool
    has_evidence_requests: bool
    readiness_status: str | None = None
```

**Campos:**
- `reply_text`: Mensaje para el usuario en castellano de negocio
- `updated_progressive_context`: Contexto serializable para próximo turno
- `phase`: Fase actual del FSM (para logging/debug)
- `has_hypotheses`: True si hay hipótesis ABIERTAS
- `has_evidence_requests`: True si hay evidencia solicitada
- `readiness_status`: Status de AnamnesisReadiness (READY, NEEDS_MORE_INFO, BLOCKED)

## Función principal

```python
def run_anamnesis_turn(input_data: AnamnesisTurnInput) -> AnamnesisTurnOutput:
```

**Uso básico:**

```python
from pymia.smartpyme.anamnesis_fsm_integration import (
    AnamnesisTurnInput,
    run_anamnesis_turn,
)

# Turno 1: sesión nueva
input1 = AnamnesisTurnInput(
    tenant_id="T001",
    session_id="S001",
    message_text="hola",
    previous_progressive_context=None,
)
output1 = run_anamnesis_turn(input1)
print(output1.reply_text)  # Menú inicial

# Turno 2: usar contexto del turno 1
input2 = AnamnesisTurnInput(
    tenant_id="T001",
    session_id="S001",
    message_text="1",  # Opción 1 del menú
    previous_progressive_context=output1.updated_progressive_context,
)
output2 = run_anamnesis_turn(input2)
print(output2.reply_text)  # "Perfecto. Contame con tus palabras..."
```

## Casos obligatorios cubiertos

### Caso 1: Primer turno "hola" → menú inicial

```python
input_data = AnamnesisTurnInput(
    tenant_id="T001",
    session_id="S001",
    message_text="hola",
    previous_progressive_context=None,
)
output = run_anamnesis_turn(input_data)
# output.phase == "MENU_INICIAL"
# output.reply_text contiene "Contame qué te preocupa"
```

### Caso 2: "RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY" → anamnesis/taxonomía

```python
input_data = AnamnesisTurnInput(
    tenant_id="T002",
    session_id="S002",
    message_text="RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY",
    previous_progressive_context=None,
)
output = run_anamnesis_turn(input_data)
# output.phase in ["ANAMNESIS_TAXONOMIA", "MENU_INICIAL"]
# output.reply_text pregunta sobre taxonomía, NO diagnostica
```

**Prohibido:** "Tu problema es margen bajo"  
**Permitido:** "Para poder ayudarte necesito entender tu negocio..."

### Caso 3: Primer contacto con señales fuertes → taxonomía preliminar sin confirmar

```python
input_data = AnamnesisTurnInput(
    tenant_id="T003",
    session_id="S003",
    message_text="fabrico ropa, compro tela, corto, coso, empaco y vendo por mayor y por Mercado Libre",
    previous_progressive_context=None,
)
output = run_anamnesis_turn(input_data)
# output.updated_progressive_context["has_taxonomy"] == False
# output.updated_progressive_context["has_confirmed_taxonomy"] == False
# output.updated_progressive_context["has_preliminary_taxonomy"] == True
# fsm_state["profile_step"] == "ASK_CONTACT_NAME"
# fsm_state["taxonomy"] is None
# fsm_state["preliminary_taxonomy"]["status"] == "PRELIMINARY"
# fsm_state["preliminary_taxonomy"]["organism_type"] in ["textil", "produccion_fabrica"]
# fsm_state["preliminary_taxonomy"]["sales_channels"] incluye "wholesale"
```

### Caso 4: Preservación de estado entre turnos

```python
# Turno 1
input1 = AnamnesisTurnInput(
    tenant_id="T004",
    session_id="S004",
    message_text="hola",
    previous_progressive_context=None,
)
output1 = run_anamnesis_turn(input1)

# Turno 2 usando contexto del turno 1
input2 = AnamnesisTurnInput(
    tenant_id="T004",
    session_id="S004",
    message_text="1",
    previous_progressive_context=output1.updated_progressive_context,
)
output2 = run_anamnesis_turn(input2)
# output2.phase == "CAPTURA_RELATO_CRUDO"
```

### Caso 5: Taxonomía suficiente + síntoma → hipótesis ABIERTA

```python
# Turno 1: taxonomía
input1 = AnamnesisTurnInput(
    tenant_id="T005",
    session_id="S005",
    message_text="fabrico ropa y vendo por mayor",
    previous_progressive_context=None,
)
output1 = run_anamnesis_turn(input1)

# Turno 2: síntoma
input2 = AnamnesisTurnInput(
    tenant_id="T005",
    session_id="S005",
    message_text="RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY",
    previous_progressive_context=output1.updated_progressive_context,
)
output2 = run_anamnesis_turn(input2)

if output2.readiness_status == "READY":
    # output2.has_hypotheses == True
    # fsm_state["hypotheses"][0]["status"] == "ABIERTA" (no CONFIRMADA)
    pass
```

### Caso 6: Solicita evidencia concreta

```python
# Turno 1: taxonomía
input1 = AnamnesisTurnInput(
    tenant_id="T006",
    session_id="S006",
    message_text="fabrico ropa y vendo por mayor",
    previous_progressive_context=None,
)
output1 = run_anamnesis_turn(input1)

# Turno 2: síntoma
input2 = AnamnesisTurnInput(
    tenant_id="T006",
    session_id="S006",
    message_text="el margen es bajo",
    previous_progressive_context=output1.updated_progressive_context,
)
output2 = run_anamnesis_turn(input2)

if output2.readiness_status == "READY":
    # output2.has_evidence_requests == True
    # evidence_types incluye "ventas_del_periodo" y "costos_y_gastos"
    pass
```

### Caso 7: Contexto corrupto → fail-closed

```python
corrupt_context = {"invalid": "data", "no_fsm_state": True}

input_data = AnamnesisTurnInput(
    tenant_id="T007",
    session_id="S007",
    message_text="hola",
    previous_progressive_context=corrupt_context,
)
output = run_anamnesis_turn(input_data)
# output.reply_text es válido (menú inicial o captura de relato)
# output.updated_progressive_context es válido
```

### Caso 8: No importa módulos prohibidos

```python
# AST check: anamnesis_fsm_integration.py NO importa:
# - pymia.smartpyme.excel_diagnostic
# - pymia.smartpyme.supplier_duplicate_check
# - pymia.smartpyme.microservice_dispatcher
# - pymia.smartpyme.runtime_bridge
# - pymia.hermes.adapter
# - telegram
# - requests
# - httpx
```

## Estructura de progressive_context

```json
{
  "fsm_state": {
    "phase": "MENU_INICIAL",
    "tenant_id": "T001",
    "user_text": "hola",
    "taxonomy": null,
    "contract": null,
    "hypotheses": [],
    "evidence_requests": [],
    "readiness": null,
    "blocking_reasons": [],
    "created_at": "2026-05-27T10:30:00+00:00",
    "updated_at": "2026-05-27T10:30:00+00:00"
  },
  "tenant_id": "T001",
  "phase": "MENU_INICIAL",
  "has_taxonomy": false,
  "has_confirmed_taxonomy": false,
  "has_preliminary_taxonomy": false,
  "preliminary_taxonomy": null,
  "has_hypotheses": false,
  "has_evidence_requests": false,
  "readiness_status": null
}
```

## Reglas de diseño

1. **Puro y determinístico**: sin I/O, sin red, sin persistencia
2. **Fail-closed**: contexto corrupto → sesión nueva; inputs inválidos → ValueError
3. **Inmutable**: `AnamnesisTurnInput` y `AnamnesisTurnOutput` son dataclass frozen
4. **Sin diagnóstico prematuro**: nunca afirma hallazgos sin evidencia
5. **Hipótesis ABIERTAS**: nunca CONFIRMADAS sin contraste
6. **Sin Excel en primer turno**: no pide archivos hasta tener taxonomía
7. **Mensajes en castellano de negocio**: semántica PyME, no técnica
8. **Trazabilidad**: tenant_id, session_id en cada turno
9. **Sesiones independientes**: diferentes session_id no comparten estado

## Integración con conversa-engine

Este wrapper puede ser consumido por `conversa-engine/main.py` sin modificar el kernel:

```python
# En conversa-engine/main.py (futuro)
from pymia.smartpyme.anamnesis_fsm_integration import (
    AnamnesisTurnInput,
    run_anamnesis_turn,
)

_PROGRESSIVE_CONTEXT_BY_SESSION = {}

def run_message(text: str, tenant_id: str = "telegram:42", user_id: str = "42") -> str:
    session_id = f"{tenant_id}/{user_id}"
    
    input_data = AnamnesisTurnInput(
        tenant_id=tenant_id,
        session_id=session_id,
        message_text=text,
        previous_progressive_context=_PROGRESSIVE_CONTEXT_BY_SESSION.get(session_id),
    )
    
    output = run_anamnesis_turn(input_data)
    
    _PROGRESSIVE_CONTEXT_BY_SESSION[session_id] = output.updated_progressive_context
    
    return output.reply_text
```

**Nota:** Esta integración es **opcional**. El wrapper funciona standalone y puede ser consumido por cualquier capa superior (Hermes real, bot, CLI) sin acoplamiento directo.

## Tests

**Archivo:** `tests/smartpyme/test_anamnesis_fsm_integration.py`

**Cobertura:** 30+ tests incluyendo:
- 8 casos obligatorios
- Validación de inputs (tenant_id, session_id obligatorios)
- JSON serialización de output y progressive_context
- Inmutabilidad de input/output
- No mutación de inputs
- No importación de módulos prohibidos
- Preservación de estado entre turnos
- Sesiones independientes
- Contexto corrupto → fail-closed

**Ejecución:**
```bash
python -m pytest tests/smartpyme/test_anamnesis_fsm_integration.py -q
```

## Restricciones

### NO hace

- No ejecuta microservicios
- No persiste en base de datos
- No se conecta a Telegram
- No usa HermesAdapter (puede coexistir, pero no lo invoca)
- No lee Excel crudo
- No diagnostica desde relato
- No confirma hipótesis sin evidencia

### NO importa

- `pymia.smartpyme.excel_diagnostic`
- `pymia.smartpyme.supplier_duplicate_check`
- `pymia.smartpyme.microservice_dispatcher`
- `pymia.smartpyme.runtime_bridge`
- `pymia.hermes.adapter`
- `telegram`
- `requests`
- `httpx`

## Relación con otros frentes

### SMARTPYME_ANAMNESIS_CONTRACTS_SLICE
Este wrapper consume los contratos puros:
- `BusinessTaxonomySnapshot`
- `AnamnesisReadiness`
- `OperationalHypothesis`
- `ConversationContract`
- `EvidenceRequirement`

### SMARTPYME_ANAMNESIS_FSM_OFFLINE
Este wrapper invoca `process_message()` del FSM offline.

### SMARTPYME_CONVERSATION_CONTRACT_ENFORCEMENT (futuro)
Este wrapper respeta `ConversationContract.forbidden_actions` pero no lo enforce activamente (eso lo hace el FSM).

## Archivos

- `pymia/smartpyme/anamnesis_fsm_integration.py` - Wrapper de integración
- `tests/smartpyme/test_anamnesis_fsm_integration.py` - Tests exhaustivos
- `docs/smartpyme/SMARTPYME_ANAMNESIS_FSM_INTEGRATION.md` - Este documento

## Status final

✅ **Frente cerrado: SMARTPYME_ANAMNESIS_FSM_INTEGRATION**

- 30+ tests passing
- Sin I/O, sin persistencia, sin kernel modificado
- Sin diagnóstico prematuro
- Sin importación de módulos prohibidos
- Preservación de estado entre turnos vía progressive_context
- Fail-closed con contexto corrupto
