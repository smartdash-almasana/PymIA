# ADR-015 — Problema de Ingeniería No Resuelto: Colapso Estructural Hermes ↔ PymIA

Status: Accepted (diagnóstico) / Open (solución)

Fecha: 2026-05-27

Autor: Auditoría técnica acumulada del ciclo SMARTPYME

Severidad: CRÍTICA — bloquea el avance del Sistema Operativo Organizacional

---

## Abstract

PymIA y Hermes son dos subsistemas diseñados para operar como hemisferios complementarios de un Sistema Operativo Organizacional para PyMEs. Tras ~40 frentes documentales e implementativos, ambos sistemas **no logran constituirse como un organismo coherente**. El resultado observable es una conversación sorda y un kernel rígido: Hermes bypasea a PymIA, o PymIA ignora la conversación del dueño.

Este documento formula el problema de ingeniería subyacente, evidencia el colapso con trazas del repo, identifica por qué los intentos previos de resolución han fracasado, y plantea la dirección necesaria —sin proponer aún una solución— para poder avanzar.

---

## Context

### El síntoma observable

Un dueño PyME se conecta por Telegram:

1. Escribe `"hola"` → recibe menú inicial correcto.
2. Escribe `"vendo mucho pero no sé si gano plata"` → recibe respuesta genérica de anamnesis.
3. Escribe `"fabrico ropa, compro tela, corto, coso, empaco y vendo por mayor y por Mercado Libre"` → recibe `"Gracias. Para seguir necesito confirmar cómo funciona tu negocio..."`.

El dueño **acaba de describir su negocio completo**. Y el sistema le responde como si no hubiera escuchado. La conversación es robótica, sorda. El dueño abandona.

### Qué hemos intentado

| # | Problema superficial | Frente | Resultado |
|---|---|---|---|
| 1 | Faltan contratos de anamnesis | `SMARTPYME_ANAMNESIS_CONTRACTS_SLICE` | ✅ 5 contratos, 350+ tests |
| 2 | Falta FSM conversacional | `SMARTPYME_ANAMNESIS_FSM_OFFLINE` | ✅ FSM determinístico, 40+ tests |
| 3 | FSM no se integra | `SMARTPYME_ANAMNESIS_FSM_INTEGRATION` | ✅ Wrapper, 31 tests |
| 4 | Conversación rota | `SMARTPYME_CONVERSATION_LOOP_AUDIT` | ✅ Audit completo |
| 5 | Sesión no sobrevive reinicios | `SMARTPYME_CONVERSATION_SESSION_RUNTIME_DESIGN` | ⚠️ Detectada sobreingeniería |
| 6 | Hermes puede inventar hallazgos | `HERMES_AGENT_AUDIT_POLICY` | ✅ Policy ALLOW/WARN/BLOCK |
| 7 | Hermes puede sobreprometer | `CONVERSATIONAL_BOUNDARY_POLICY` | ✅ Policy documentada |
| 8 | "Anamnesis" usado en 3 sentidos | `ADR-010` | ✅ Unificado conceptualmente |
| 9 | Hermes puede bypasear kernel | `ARCHITECTURE_GUARDRAILS` | ✅ Guardrails documentados |

**Resultado acumulado:** ~400 tests passing. 0 conversación funcional.

---

## Decision

### El diagnóstico profundo

El problema real **no es ninguno de los anteriores**. El problema real es:

> **No existe un cuerpo calloso entre el hemisferio determinístico (PymIA) y el hemisferio conversacional (Hermes).**

Hay dos sistemas operando en paralelo, sin protocolo bidireccional de intercambio semántico. Los "puentes" construidos son **traductores unidireccionales frágiles**:

| Puente | Qué hace | Qué NO hace |
|---|---|---|
| `HermesAdapter` | Traduce vocabulario Hermes ↔ vocabulario kernel | No comparte estado, no enriquece semántica, no gestiona turnos |
| `run_anamnesis_turn()` | Wrapper serialización/deserialización de FSM | Bug de reconstrucción: cada turno olvida taxonomía, hipótesis, evidencia |
| `_PROGRESSIVE_CONTEXT_BY_SESSION` | Dict global en memoria | No sobrevive reinicios. No compartido entre CLI y Telegram. |
| `HermesPymiaBridge` | Conecta Telegram a kernel legacy | Bypasea completamente el FSM de anamnesis |

### Las tres dimensiones del colapso

#### 1. Doble ruta paralela no conectada

```
RUTA A (CLI)                    RUTA B (Telegram real)
─────────────────────────       ─────────────────────────────────
main.py                         telegram_adapter.py
    ↓                               ↓
run_anamnesis_turn()            HermesPymiaBridge
    ↓                               ↓
FSM de anamnesis (NUEVO)        HermesAdapter
                                    ↓
                                ClinicalConversationalPort (LEGACY)
```

El FSM de anamnesis **nunca** se ejecuta cuando el dueño habla por Telegram. Los 5 contratos nuevos (`BusinessTaxonomySnapshot`, `OperationalHypothesis`, `ConversationContract`, `EvidenceRequirement`, `AnamnesisReadiness`) **nunca participan del flujo real**.

#### 2. Bug de reconstrucción de estado

En `pymia/smartpyme/anamnesis_fsm_integration.py` líneas 150-169:

```python
def _reconstruct_state_from_context(tenant_id, context):
    taxonomy = None           # ← SIEMPRE None
    hypotheses = tuple()      # ← SIEMPRE vacío
    evidence_requests = tuple()  # ← SIEMPRE vacío
    readiness = None          # ← SIEMPRE None
```

El wrapper serializa correctamente al final del turno, pero **al inicio del siguiente turno lo pierde**.

#### 3. Memoria de proceso vs. memoria del dueño

`_PROGRESSIVE_CONTEXT_BY_SESSION` es un `dict` global en memoria. Cuando el proceso se reinicia, **la memoria de todos los dueños desaparece**. No hay persistencia, no hay storage, no hay historia clínica.

### La metáfora del cerebro

| Hemisferio | Rol | Sub-sistema | Estado |
|---|---|---|---|
| Izquierdo | Lógico, determinístico | PymIA (kernel) | Funcional, 393 tests |
| Derecho | Conversacional, contextual | Hermes (LLM) | Funcional, gateway operativo |
| **Cuerpo calloso** | **Protocolo bidireccional** | **???** | **NO EXISTE** |

Un cerebro sin cuerpo calloso sufre **síndrome de desconexión hemisférica** (Sperry, 1968): cada hemisferio funciona, pero no hay integración. Nuestro sistema tiene ese síndrome.

---

## Evidencia del colapso (trazas del repo)

### Evidencia 1: doble ruta no conectada

**Archivo:** `SmartPyme/app/adapters/telegram_adapter.py` (línea 151-152):

```python
bridge = HermesPymiaBridge()
bridge_result = bridge.handle_text(tenant_id=cliente_id, telegram_user_id=user_id, text=text)
```

Ninguna referencia a `run_anamnesis_turn` ni a `anamnesis_fsm`.

### Evidencia 2: bug de reconstrucción

**Archivo:** `PymIA/pymia/smartpyme/anamnesis_fsm_integration.py` líneas 150-169:

```python
taxonomy = None
if taxonomy_dict and isinstance(taxonomy_dict, dict):
    # No reconstruimos el dataclass completo, solo pasamos el dict
    # process_message() aceptará None y reconstruirá desde texto
    pass  # ← BUG DOCUMENTADO
```

### Evidencia 3: memoria frágil

**Archivo:** `PymIA/conversa-engine/main.py` línea 10:

```python
_PROGRESSIVE_CONTEXT_BY_SESSION = {}
```

Dict global. Sin persistencia. Sin TTL. Sin cleanup. Sin sharing.

### Evidencia 4: contrato HermesAdapter unidireccional

**Archivo:** `PymIA/pymia/hermes/adapter.py`:

```python
class HermesAdapter:
    """
    - Traducir HermesInput → ConversationalInput
    - Llamar a ClinicalConversationalPort.handle()
    - Traducir ConversationalOutput → HermesOutput
    - Preservar metadata de Hermes en el payload de salida
    """
```

Traduce contratos. No gestiona turnos. No permite que Hermes inyecte variables conversacionales al kernel. No permite que el kernel devuelva próximo paso conversacional.

### Evidencia 5: 5 contratos implementados sin uso real

- `pymia/smartpyme/taxonomy.py` — `BusinessTaxonomySnapshot` ✅
- `pymia/smartpyme/operational_hypothesis.py` — `OperationalHypothesis` ✅
- `pymia/smartpyme/conversation_contract.py` — `ConversationContract` ✅
- `pymia/smartpyme/evidence_requirement.py` — `EvidenceRequirement` ✅
- `pymia/smartpyme/anamnesis_readiness.py` — `AnamnesisReadiness` ✅

**Uso real en flujo Telegram:** NINGUNO.

### Evidencia 6: respuesta plantilla cuando falla reconstrucción

**Archivo:** `PymIA/pymia/smartpyme/anamnesis_fsm.py` línea 388:

Cuando `not taxonomy and not evidence_requests and not hypotheses` → dispara plantilla genérica.

---

## Cronología del fracaso

| Fecha | Frente | Qué intentó | Por qué fracasó |
|---|---|---|---|
| T1 | `CONVERSATIONAL_ANAMNESIS_CONTRACT` | Contrato documental | El contrato no se ejecuta |
| T2 | `ANAMNESIS_CONTRACTS_SLICE` | 5 dataclasses | Los contratos existen, nadie los llama |
| T3 | `ANAMNESIS_FSM_OFFLINE` | FSM determinístico | Funciona en CLI, no en Telegram |
| T4 | `ANAMNESIS_FSM_INTEGRATION` | Wrapper integración | Bug de reconstrucción |
| T5 | `TELEGRAM_SANDBOX_ANAMNESIS` | Conectar Hermes pymiafactory | Hermes rutea a kernel legacy |
| T6 | `CONVERSATION_LOOP_AUDIT` | Auditar conversación rota | Identifica causa, no resuelve |
| T7 | `CONVERSATION_SESSION_RUNTIME_DESIGN` | ConversationSessionRuntime | Sobreingeniería (Hermes ya tiene sesión) |
| T8 | Investigación HermeSpec | Approval contracts | No resuelve cuerpo calloso |
| T9 | Investigación hermes-plugins | 7 plugins útiles | No resuelven cuerpo calloso |

**Patrón emergente:** cada frente **extremiza uno de los hemisferios sin mejorar la conexión**.

---

## El problema real (reformulado)

El problema no es técnico en el sentido de "falta código". Es **arquitectónico-semántico**:

> **¿Cómo diseñar un protocolo bidireccional entre un sistema conversacional (Hermes) y un sistema determinístico (PymIA) tal que:**
>
> 1. **Hermes pueda aportar variables conversacionales formales al kernel** (taxonomía, hipótesis, dolor declarado, contexto del dueño) **sin que el kernel pierda soberanía computacional.**
>
> 2. **El kernel pueda gobernar las decisiones operacionales** (gates, evidencia, hallazgos) **sin que la conversación se vuelva rígida o sorda.**
>
> 3. **El estado conversacional y el estado operacional sean uno solo** —no dos estados sincronizados por un wrapper frágil— **con memoria persistente entre turnos, reinicios y canales.**
>
> 4. **El dueño sienta que el sistema lo escucha** y que cada turno avanza hacia verdad operacional, sin diagnósticos prematuros ni respuestas plantilla.
>
> **Y que todo esto sea testeable sin Telegram real, determinístico, y gobernable por guardrails documentados.**

Este problema **no tiene solución conocida en el repo actual**.

---

## Lo que NO es la solución

| Propuesta | Por qué no resuelve |
|---|---|
| Más contratos puros | Ya tenemos 5 sin usar. Fetiche de documentación. |
| Más FSMs | Uno con bug ya es suficiente. |
| Más wrappers | Dos no conectados; un tercero acumula deuda. |
| Plugins de Hermes (evey-validate, etc.) | Útiles después; no resuelven cuerpo calloso. |
| HermeSpec (approval contracts) | Problema no es falta de HITL, es falta de integración semántica. |
| Redis / persistencia compleja | Persistir el bug de reconstrucción no lo arregla. |
| Reescribir PymIA | Tirar 393 tests y un año de trabajo. |
| Reescribir Hermes | Tirar infraestructura probada. |
| "Hermes que compute" | Viola `ARCHITECTURE_GUARDRAILS.md`. |
| "PymIA que converse" | Viola soberanía. Introduce LLM en kernel determinístico. |

---

## Dirección necesaria (no solución)

### 1. Un protocolo, no un wrapper

Protocolo bidireccional Hermes ↔ PymIA que defina:

- **Mensaje de Hermes a PymIA:** no solo `text`, sino `variables conversacionales formales` (taxonomía extraída, hipótesis del dueño, dolor declarado, evidencia aportada).
- **Mensaje de PymIA a Hermes:** no solo `reply_text`, sino `próximo paso conversacional` (qué preguntar, qué confirmar, qué evidencia falta).

### 2. Un estado único, no dos sincronizados

`BusinessAnamnesisRecord` (ADR-010) debe ser **el estado compartido**. Hermes lo enriquece. PymIA lo valida. Ambos lo leen y escriben.

### 3. Persistencia de sesión como primera clase

Sesión del dueño como entidad persistente, compartida entre CLI y Telegram, con TTL y cleanup.

### 4. Unificación de rutas

CLI y Telegram deben ejecutar **el mismo código**. Hoy divergen en:

- CLI → FSM nuevo
- Telegram → kernel legacy

### 5. Corrección del bug de reconstrucción

Sin ese fix, ninguna prueba de conversación tiene sentido.

### 6. Tests end-to-end conversacionales

Tests que simulen conversaciones de 5+ turnos verificando conservación de taxonomía, hipótesis, evidencia.

---

## Consecuencias de no resolver

1. **Producto nunca usable.** Dueño abandona al tercer turno.
2. **Kernel decorativo.** 393 tests pasando sobre un sistema que nadie usa.
3. **Hermes chatbot caro.** LLM con MCP tools sin valor diferencial.
4. **Promesa diluida.** Vendemos "laboratorio clínico PyME", entregamos chatbot + Excel analyzer desconectados.
5. **Fatiga arquitectónica del equipo.** Cada frente nuevo agrega documentación sin cerrar ciclo real.
6. **Burla de la metáfora.** Dos hemisferios desconectados no son un cerebro, son dos órganos en una caja.

---

## Status de este documento

Este documento es un **reconocimiento formal de límite**. No una propuesta de solución.

Declaración:

> El Sistema Operativo Organizacional PymIA/SmartPyme está **bloqueado** en su dimensión conversacional-determinística.
>
> Los componentes individuales (kernel, Hermes, contratos, FSM) están operativos.
>
> La integración entre ellos **no lo está**.
>
> Los intentos previos han sido **extensivos** (más contratos, más FSMs, más wrappers) y han fracasado porque el problema es **intensivo** (falta el cuerpo calloso).
>
> Se requiere un rediseño de la frontera Hermes ↔ PymIA, no más capas sobre la frontera actual.
>
> **Ningún nuevo frente debe abrirse hasta que este problema sea reformulado como contrato de integración y resuelto como tal.**

---

## Próximos pasos

1. **Pausar frentes nuevos.** No abrir `SMARTPYME_ANAMNESIS_RUNTIME_INTEGRATION`, `SMARTPYME_CONVERSATION_CONTRACT_ENFORCEMENT`, ni similares. Son más de lo mismo.

2. **Diseño del cuerpo calloso.** ADR-016 (pendiente) que defina el protocolo bidireccional Hermes ↔ PymIA antes de cualquier implementación.

3. **Refactor de unificación de rutas.** CLI y Telegram convergen en una sola ruta. Decisión: FSM de anamnesis en ambos, o kernel legacy enriquecido.

4. **Fix del bug de reconstrucción.** Corrección puntual de `_reconstruct_state_from_context()`.

5. **Persistencia mínima de sesión.** File-based. Sin Redis. Sobrevive reinicios. Compartida entre CLI y Telegram.

6. **Test canónico de conversación de 5 turnos.** Un test que verifique conservación de estado completo.

7. **Revisión de `SmartPyme/telegram_adapter.py`.** El puente actual debe ser reemplazado o reformulado para usar los contratos nuevos.

---

## No implementa

- No código nuevo.
- No contratos nuevos.
- No FSMs nuevos.
- No wrappers nuevos.
- No plugins.
- No persistencia compleja.
- No reescritura de kernel.
- No reescritura de Hermes.
- No habilitación de producción.

---

## Documentos relacionados

- `ADR-008-hermes-mcp-client-pymia-mcp-server.md`
- `ADR-010-conversational-anamnesis-contract.md`
- `hermes/CONVERSATIONAL_BOUNDARY_POLICY.md`
- `conversa-engine/HERMES_AGENT_AUDIT_POLICY.md`
- `ARCHITECTURE_GUARDRAILS.md` (raíz)
- `smartpyme/SMARTPYME_ANAMNESIS_FSM_INTEGRATION.md`
- `smartpyme/SMARTPYME_TELEGRAM_HERMES_PYMIA_CONVERSATION_PLAN.md`

---

*Fin del documento. Este ADR no contiene código. Contiene únicamente el diagnóstico estructural del problema abierto. Debe citarse como referencia canónica cada vez que se proponga un nuevo frente conversacional, para evitar repetir el patrón de "extender sin integrar".*
