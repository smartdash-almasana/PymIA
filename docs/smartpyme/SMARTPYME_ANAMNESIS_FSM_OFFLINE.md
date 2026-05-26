# SMARTPYME_ANAMNESIS_FSM_OFFLINE

## Estado: Aceptado

## Resumen

Implementación de un FSM (Finite State Machine) offline, puro y determinístico para guiar la conversación inicial de anamnesis operacional en SmartPyme.

Este módulo **NO** ejecuta microservicios, **NO** persiste datos, **NO** se conecta a Telegram, y **NO** diagnostica desde el relato crudo.

## Objetivo

Proveer una capa conversacional controlada que:

1. Recibe narrativa cruda del dueño PyME.
2. Extrae taxonomía de negocio (organismo, canales, áreas, flujo).
3. Detecta síntomas candidatos (margen, stock, caja, precios).
4. Formula hipótesis ABIERTAS (no confirmadas).
5. Solicita evidencia concreta cuando readiness está READY.
6. Bloquea análisis prematuro si falta información esencial.

## Estados del FSM

| Fase | Descripción |
|------|-------------|
| `INIT` | Sesión nueva, sin estado previo |
| `MENU_INICIAL` | Presentación de 4 opciones iniciales |
| `CAPTURA_RELATO_CRUDO` | Recepción de narrativa del dueño |
| `ANAMNESIS_TAXONOMIA` | Construcción de BusinessTaxonomySnapshot |
| `HIPOTESIS_FORMULADA` | Hipótesis ABIERTA (no confirmada) |
| `SOLICITUD_EVIDENCIA` | Pedido de evidencia concreta |
| `BLOQUEADO_EXPLICATIVO` | Falta información bloqueante |

## Contratos utilizados

Este FSM consume los contratos puros ya implementados:

- `BusinessTaxonomySnapshot` (pymia/smartpyme/taxonomy.py)
- `AnamnesisReadiness` (pymia/smartpyme/anamnesis_readiness.py)
- `OperationalHypothesis` (pymia/smartpyme/operational_hypothesis.py)
- `ConversationContract` (pymia/smartpyme/conversation_contract.py)
- `EvidenceRequirement` (pymia/smartpyme/evidence_requirement.py)

## Función principal

```python
def process_message(
    user_text: str,
    tenant_id: str,
    previous_state: Optional[AnamnesisFSMState] = None,
) -> tuple[AnamnesisFSMState, str]:
```

**Inputs:**
- `user_text`: texto del dueño (puede ser vacío)
- `tenant_id`: identificador del tenant (obligatorio)
- `previous_state`: estado previo (None si es sesión nueva)

**Outputs:**
- `AnamnesisFSMState`: nuevo estado con taxonomía, hipótesis, evidencia solicitada
- `str`: mensaje para el usuario en castellano de negocio

## Casos obligatorios cubiertos

### Caso 1: Sesión nueva / texto vacío → menú inicial

```python
state, message = process_message("", tenant_id="T001", previous_state=None)
# state.phase == FSMPhase.MENU_INICIAL
# message == MENU_INICIAL_TEXTO
```

**Menú inicial:**
```
Hola. Antes de revisar números necesito entender tu negocio.

1. Contame qué te preocupa
2. No sé bien, pero algo no me cierra
3. Quiero revisar mis planillas
4. Tengo una pregunta específica
```

### Caso 2: "vendo mucho pero no se si gano plata" → pregunta de anamnesis

```python
state, message = process_message(
    "vendo mucho pero no se si gano plata",
    tenant_id="T002",
    previous_state=None
)
# state.phase == FSMPhase.ANAMNESIS_TAXONOMIA
# message pregunta sobre taxonomía, NO diagnostica
```

**Prohibido:** "Tu problema parece ser margen bajo"  
**Permitido:** "Para poder ayudarte mejor necesito entender un poco más sobre tu negocio..."

### Caso 3: Descripción de flujo productivo → clasificación

```python
state, message = process_message(
    "fabrico ropa, compro tela, corto, coso, empaco y vendo por mayor y por Mercado Libre",
    tenant_id="T003",
    previous_state=None
)
# state.taxonomy.organism_type == TaxonomyType.INDUSTRIA
# state.taxonomy.sales_channels == ["mayorista", "mercado_libre"]
# state.taxonomy.areas_present == ["produccion", "ventas", "compras"]
```

### Caso 4: Taxonomía suficiente + síntoma → hipótesis ABIERTA

```python
state1, _ = process_message("fabrico ropa y vendo por mayor", tenant_id="T005", previous_state=None)
state2, message = process_message(
    "vendo mucho pero no me queda ganancia, el margen es bajo",
    tenant_id="T005",
    previous_state=state1
)
# Si readiness está READY:
# - len(state2.hypotheses) > 0
# - h.status == HypothesisStatus.ABIERTA (no CONFIRMADA)
```

### Caso 5: Solicita evidencia concreta

```python
state1, _ = process_message("fabrico ropa y vendo por mayor", tenant_id="T007", previous_state=None)
state2, message = process_message("el margen es bajo", tenant_id="T007", previous_state=state1)
# Si readiness está READY:
# - state2.phase == FSMPhase.SOLICITUD_EVIDENCIA
# - evidence_types incluye "ventas_del_periodo" y "costos_y_gastos"
# - message solicita evidencia concreta
```

### Caso 6: Campos faltantes → pregunta o BLOQUEADO_EXPLICATIVO

```python
state, message = process_message("tengo un negocio", tenant_id="T009", previous_state=None)
# state.phase in [FSMPhase.ANAMNESIS_TAXONOMIA, FSMPhase.BLOQUEADO_EXPLICATIVO]
# message pregunta por más información
```

### Caso 7: Bloquea análisis si AnamnesisReadiness no está READY

```python
state, _ = process_message("tengo un problema", tenant_id="T011", previous_state=None)
# Si readiness no está READY:
# - len(state.hypotheses) == 0
```

### Caso 8: No importa módulos prohibidos

```python
# AST check: anamnesis_fsm.py NO importa:
# - pymia.smartpyme.excel_diagnostic
# - pymia.smartpyme.supplier_duplicate_check
# - pymia.smartpyme.microservice_dispatcher
# - pymia.smartpyme.runtime_bridge
```

## Reglas de diseño

1. **Puro y determinístico**: sin I/O, sin red, sin persistencia
2. **Fail-closed**: inputs inválidos → ValueError o estado bloqueado
3. **Inmutable**: AnamnesisFSMState es dataclass frozen
4. **Sin diagnóstico prematuro**: nunca afirma hallazgos sin evidencia
5. **Hipótesis ABIERTAS**: nunca CONFIRMADAS sin contraste
6. **Sin Excel en primer mensaje**: no pide archivos hasta tener taxonomía
7. **Mensajes en castellano de negocio**: semántica PyME, no técnica
8. **Trazabilidad**: tenant_id, created_at, updated_at en cada estado

## Detección de patrones

### Organismo (TaxonomyType)

| Keywords | Clasificación |
|----------|---------------|
| fabrico, produzco, elaboro, manufactura, corto, coso | INDUSTRIA |
| revendo, compro y vendo, distribuidor | COMERCIO |
| servicio, consultoría, asesoro | SERVICIOS |
| logística, transporte, envíos | LOGISTICA |

### Canales de venta

| Keywords | Canal |
|----------|-------|
| mayor, mayorista | mayorista |
| minorista, local, tienda | minorista |
| mercado libre, ml | mercado_libre |
| online, web, ecommerce | online |

### Áreas presentes

| Keywords | Área |
|----------|------|
| stock, inventario, almacén | stock |
| caja, banco, cobros, pagos | caja |
| producción, fabricación, elaboración | produccion |
| ventas, vendo | ventas |
| compras, proveedores | compras |
| sueldos, empleados, rrhh | rrhh |

### Síntomas candidatos

| Keywords | Síntoma |
|----------|---------|
| margen, ganancia, no gano, no me queda | margen_erosionado |
| stock, inventario, parado, no rota | stock_estancado |
| caja, efectivo, no entra | flujo_caja_negativo |
| precios, subir, bajar | precios_desalineados |

## Evidencia solicitada por hipótesis

### Hipótesis de margen

- `ventas_del_periodo`: Listado de ventas con fechas, importes y productos
- `costos_y_gastos`: Listado de costos, gastos y facturas de proveedores

### Hipótesis de stock

- `inventario_actual`: Listado de productos en stock con cantidades y antigüedad

## Tests

**Archivo:** `tests/smartpyme/test_anamnesis_fsm.py`

**Cobertura:** 40+ tests incluyendo:
- 8 casos obligatorios
- Validación de enums
- JSON serialización
- Inmutabilidad
- No mutación de inputs
- No importación de módulos prohibidos
- Formato ISO8601 de timestamps

**Ejecución:**
```bash
python -m pytest tests/smartpyme/test_anamnesis_fsm.py -q
```

## Restricciones

### NO hace

- No ejecuta microservicios
- No persiste en base de datos
- No se conecta a Telegram
- No usa HermesAdapter
- No usa conversa-engine
- No lee Excel crudo
- No diagnostica desde relato
- No confirma hipótesis sin evidencia

### NO importa

- `pymia.smartpyme.excel_diagnostic`
- `pymia.smartpyme.supplier_duplicate_check`
- `pymia.smartpyme.microservice_dispatcher`
- `pymia.smartpyme.runtime_bridge`

## Integración futura

Este FSM es **offline** y **puro**. Para integrarlo con Hermes/Telegram:

1. Wrapper que persista `AnamnesisFSMState` por sesión
2. Adaptador que traduzca mensajes Telegram ↔ FSM
3. Gateway que respete `ConversationContract.forbidden_actions`
4. HITL obligatorio antes de ejecutar microservicios

## Relación con ADR-010

Este frente implementa la capa conversacional definida en ADR-010:
- BusinessTaxonomySnapshot como input obligatorio antes de hipótesis
- OperationalHypothesis con ciclo de vida (ABIERTA → EN_CONTRASTE → CONFIRMADA/DESCARTADA)
- ConversationContract con forbidden_actions
- AnamnesisReadiness como gate previo a hipótesis

## Archivos

- `pymia/smartpyme/anamnesis_fsm.py` - FSM determinístico
- `tests/smartpyme/test_anamnesis_fsm.py` - Tests exhaustivos
- `docs/smartpyme/SMARTPYME_ANAMNESIS_FSM_OFFLINE.md` - Este documento

## Status final

✅ **Frente cerrado: SMARTPYME_ANAMNESIS_FSM_OFFLINE**

- 40+ tests passing
- Sin I/O, sin persistencia, sin kernel modificado
- Sin diagnóstico prematuro
- Sin importación de módulos prohibidos
