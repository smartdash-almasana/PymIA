# Plan Integral: Conversación Inteligente Telegram/Hermes/PymIA — SmartPyme
*Documento de diseño — sin implementación. Listo para Codex Ciclo 1.*

---

## VEREDICTO

El stack Telegram→Hermes→PymIA **es arquitecturalmente coherente** con los contratos vigentes (ADR-010, boundary policy, adapter.py, conversa-engine/main.py). La brecha actual es **documental-contractual**, no de código runtime. Los contratos `BusinessTaxonomySnapshot`, `OperationalHypothesis`, `AnamnesisReadiness` y `ConversationContract` están definidos en ADR-010 pero **no tienen slices implementados**. El plan siguiente cierra esa brecha en 3 ciclos incrementales sin tocar el runtime soberano de PymIA.

---

## TESIS

> Hermes conversa, orquesta y encuadra. PymIA computa y decide.
> El canal Telegram es una capa de transporte opaca: no modifica ni interpreta el kernel clínico.
> La anamnesis operacional previene diagnósticos prematuros y construye el `BusinessTaxonomySnapshot` antes de solicitar evidencia documental.

Método aplicado: **relato crudo → síntoma → hipótesis → evidencia requerida → contraste → hallazgo → próximo paso**.

---

## ARQUITECTURA

### Diagrama de Componentes

```
┌─────────────────────────────────────────────────────────────────┐
│  CANAL: Telegram                                                │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  TelegramGateway (externo, no PymIA)                     │   │
│  │  - recibe message_text, user_id, chat_id                 │   │
│  │  - envía reply_text                                      │   │
│  │  - opaco para kernel clínico                             │   │
│  └────────────┬─────────────────────────────────────────────┘   │
└───────────────┼─────────────────────────────────────────────────┘
                │  HermesInput(tenant_id, channel="telegram",
                │              message_text, metadata={opaco})
                ▼
┌─────────────────────────────────────────────────────────────────┐
│  CONVERSA-ENGINE (runtime Hermes)                               │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  TelegramRouter / InboundEvent                           │   │
│  │  - valida formato, extrae tenant_id                      │   │
│  │  - registra RawInboundEvent (audit trail)               │   │
│  │  - llama run_message() → _pymia_reply()                  │   │
│  └────────────┬─────────────────────────────────────────────┘   │
│               │                                                  │
│  ┌────────────▼─────────────────────────────────────────────┐   │
│  │  AnamnesisOrchestrator (NUEVO — Ciclo 1)                │   │
│  │  - gestiona estado conversacional (FSM)                  │   │
│  │  - aplica menú inicial si sesión nueva                   │   │
│  │  - construye BusinessTaxonomySnapshot progresivo         │   │
│  │  - decide si enviar a interrogation o a evidence_gate    │   │
│  │  - NO diagnostica, NO computa, NO interpreta kernel      │   │
│  └────────────┬─────────────────────────────────────────────┘   │
│               │                                                  │
│  ┌────────────▼─────────────────────────────────────────────┐   │
│  │  HermesAdapter (existente — pymia/hermes/adapter.py)     │   │
│  │  - traduce HermesInput → ConversationalInput             │   │
│  │  - llama ClinicalConversationalPort.handle()             │   │
│  │  - traduce ConversationalOutput → HermesOutput           │   │
│  │  - preserva metadata como opaco en payload               │   │
│  └────────────┬─────────────────────────────────────────────┘   │
└───────────────┼─────────────────────────────────────────────────┘
                │  ConversationalInput(tenant_id, channel, text,
                │                     bundle, progressive_context)
                ▼
┌─────────────────────────────────────────────────────────────────┐
│  PYMIA KERNEL (soberano — NO modificado)                        │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  ClinicalConversationalPort                              │   │
│  │    → run_interrogation() [interrogation.py]              │   │
│  │    → select_tanks()      [tank_selection.py]             │   │
│  │    → create_intake_record() [intake.py]                  │   │
│  │    → create_evidence_record() [evidence.py]              │   │
│  │    → evaluate_analysis_readiness() [readiness.py]        │   │
│  │    → execute_diagnostic() [excel_diagnostic.py]          │   │
│  │    → DeliveryPackage + gate_verdict                      │   │
│  └────────────┬─────────────────────────────────────────────┘   │
└───────────────┼─────────────────────────────────────────────────┘
                │  ConversationalOutput(status, mode, message,
                │                      anamnesis, laboratorio,
                │                      progressive_context)
                ▼
┌─────────────────────────────────────────────────────────────────┐
│  AUDIT LAYER (transversal)                                      │
│  - HermesAuditAgent: ALLOW / WARN / BLOCK antes de reply       │
│  - ConversationContract actualizado en cada turno              │
│  - Logs de AuditDecision sin datos sensibles                   │
└─────────────────────────────────────────────────────────────────┘
```

### Handoffs Clave

| From | To | Contrato | Invariante |
|---|---|---|---|
| TelegramGateway | AnamnesisOrchestrator | `RawInboundEvent` | metadata opaco |
| AnamnesisOrchestrator | HermesAdapter | `HermesInput` | sin interpretación clínica |
| HermesAdapter | ClinicalConversationalPort | `ConversationalInput` | stateless, idempotente |
| ClinicalConversationalPort | HermesAdapter | `ConversationalOutput` | kernel soberano |
| HermesAdapter | AuditAgent | `HermesOutput` | pre-reply check |
| AuditAgent | TelegramGateway | `reply_text` aprobado | ALLOW gateado |

---

## ESTADOS_CONVERSACIONALES

```
INIT (sesión nueva)
  │
  ▼
MENU_INICIAL
  │  (dueño selecciona opción o escribe relato libre)
  ▼
CAPTURA_RELATO_CRUDO
  │  run_interrogation() → InterrogationResult
  ├──[STATUS_BLOCKED_INSUFFICIENT_CONTEXT]──────────────────► SOLICITA_MAS_CONTEXTO
  │                                                                │
  ├──[STATUS_NEEDS_ORGANISM_CONTEXT]──────────────────────────► ANAMNESIS_TAXONOMIA
  │                                                                │
  ├──[STATUS_NEEDS_DISAMBIGUATION]────────────────────────────► ANAMNESIS_DESAMBIGUACION
  │                                                                │
  ▼                                                               │
HIPOTESIS_FORMULADA (OperationalHypothesis: ABIERTA)            │
  │  confirmation_question al dueño                              │
  ├──[dueño niega]────────────────────────────────────────────► ANAMNESIS_DESAMBIGUACION
  │                                                                │
  ▼                                                               │
SOLICITUD_EVIDENCIA (IntakeEvidenceRequest: REQUESTED)          │
  │  mensaje con evidencia requerida + instrucciones de carga    │
  │                                                              │
  ├──[evidencia recibida / parcial]────────────────────────────► CONTRASTE_EVIDENCIA
  │
  ▼
CONTRASTE_EVIDENCIA (evaluate_analysis_readiness)
  ├──[READINESS_NEEDS_EVIDENCE]──────────────────────────────► SOLICITUD_EVIDENCIA
  ├──[READINESS_BLOCKED]─────────────────────────────────────► BLOQUEADO_EXPLICATIVO
  ├──[READINESS_UNSUPPORTED]─────────────────────────────────► DERIVACION_HUMANO
  ▼
LISTO_PARA_ANALISIS (AnamnesisReadiness: READY)
  │
  ▼
EJECUCION_PYMIA (kernel soberano — DeliveryPackage)
  │
  ├──[gate_verdict=PASS]──────────────────────────────────────► ENTREGA_HALLAZGOS
  ├──[gate_verdict=WARN]──────────────────────────────────────► ENTREGA_CON_AVISO
  └──[gate_verdict=FAIL]──────────────────────────────────────► SOLICITUD_EVIDENCIA
```

### Reglas de Transición

- Cada transición persiste `progressive_context` en sesión (ya implementado en `conversa-engine/main.py`).
- Transición a `EJECUCION_PYMIA` requiere `AnamnesisReadiness.status = READY` y `BusinessTaxonomySnapshot.confidence ≥ 0.7`.
- `BLOQUEADO_EXPLICATIVO` informa exactamente qué falta. Nunca "error genérico".
- Fail-closed: transición desconocida → `SOLICITA_MAS_CONTEXTO`.

---

## MENU_INICIAL

Se activa solo en `sesión nueva` (primera interacción del tenant, sin `progressive_context`).

```
🤝 Hola. Soy tu asistente operativo.
Antes de revisar números, necesito entender tu negocio.

¿Por dónde querés empezar?

1️⃣  Contame con tus palabras qué te preocupa
2️⃣  No sé bien, pero algo no me cierra
3️⃣  Quiero revisar mis Excels / planillas
4️⃣  Tengo una pregunta específica
```

**Reglas del menú:**
- Opción 1 → directo a `CAPTURA_RELATO_CRUDO` (texto libre).
- Opción 2 → pregunta orientadora mínima (sin inducir diagnóstico).
- Opción 3 → `ANAMNESIS_TAXONOMIA` (primero encuadrar el negocio; los Excels vienen después).
- Opción 4 → `CAPTURA_RELATO_CRUDO` con flag `modo_pregunta_especifica`.
- Relato libre sin seleccionar opción → `CAPTURA_RELATO_CRUDO` directamente.

**Prohibido en el menú:**
- Nombrar patologías ("si tenés problemas de flujo de caja...").
- Prometer resultado antes de evidencia.
- Solicitar Excel en el primer mensaje.

---

## ANAMNESIS_ADAPTATIVA

La anamnesis es **multi-turno**. Cada turno agrega información al `BusinessTaxonomySnapshot` progresivo. Se detiene cuando `confidence ≥ 0.7` en los campos bloqueantes.

### Campos bloqueantes (obligatorios antes de hipótesis)

| Campo | Pregunta mínima |
|---|---|
| `organism_type` | ¿Qué tipo de negocio tenés? (comercio, producción, servicio...) |
| `operational_flow_stages` | ¿Comprás para revender, fabricás algo, o prestás un servicio? |
| `sales_channels` | ¿Vendés al público, mayorista, por Mercado Libre, o varios? |
| `systems_available` | ¿Usás Excel, algún sistema, o llevás todo en papel/memoria? |

### Campos complementarios (mejoran hipótesis pero no bloquean)

| Campo | Cuándo preguntar |
|---|---|
| `size` | Si hay señal de `SOBRECARGA_MANUAL` |
| `areas_present` | Si la señal apunta a RRHH o stock |
| `jurisdiction` / `currency` | Si hay señal de múltiples provincias o monedas |
| `marketplace_presence` | Si se menciona ML, ecommerce, Shopify |

### Adaptación por taxonomía

| Tipo negocio | Preguntas activadas | Flujo operativo mapeado |
|---|---|---|
| comercio | precio/costo/stock | compra → vende minorista/mayorista → administra caja |
| producción/fábrica | materia prima, proceso, empaque | compra MP → transforma → empaca → vende |
| gastronomía | insumos, turnos, merma | compra → prepara → vende mostrador/delivery |
| servicios | horas, presupuesto, cobro | presupuesta → presta → factura → cobra |
| distribución | rutas, depósito, clientes | compra → almacena → distribuye → cobra |
| textil | telas, temporada, talles | compra tela → produce → vende temporada |
| salud/estética | turnos, insumos, honorarios | agenda → atiende → cobra → compra insumos |
| profesional | horas, honorarios, cartera | trabaja → factura → cobra → gestiona caja |
| mixto | combinación de los anteriores | se documenta explícitamente |

---

## TAXONOMIA_NEGOCIO

### Taxonomía mínima obligatoria (9 tipos)

```
comercio           → revende sin transformar; stock central
servicios          → presta servicio; no tiene stock físico
producción/fábrica → compra MP, transforma, empaca
distribución       → logística y reventa en volumen
gastronomía        → produce y vende en el acto; merma alta
textil             → moda/temporada; stock por talle/color
salud/estética     → turnos + insumos + honorarios
profesional        → honorarios por hora/proyecto
mixto              → combinación documentada explícitamente
```

### Captura conversacional

Hermes NO pregunta "¿qué tipo de empresa sos?" (inductivo).
Hermes pregunta:
1. "¿Qué hacés en tu negocio día a día?" → infiere `organism_type`
2. "¿Comprás para revender tal cual, o transformás lo que comprás?" → confirma `operational_flow_stages`
3. Confirmación no inductiva: "Entonces tu negocio compra [X] y vende [Y], ¿es así?"

### Flujo operativo representado (mapeo por etapa)

| Etapa | Señales léxicas esperadas | Dominio PymIA |
|---|---|---|
| compra materia prima | "proveedores", "insumos", "compras" | `proveedores` |
| transforma/fabrica | "producción", "proceso", "elabora" | `produccion` |
| empaca | "packaging", "empaque", "bultos" | `produccion` |
| vende mayorista | "mayorista", "distribuidora", "lista de precios" | `comercial` |
| vende minorista | "local", "al público", "mostrador" | `comercial` |
| vende ML/ecommerce | "Mercado Libre", "ML", "tienda online" | `comercial` |
| administra caja/banco | "caja", "banco", "no me cierra" | `finanzas` |
| gestiona stock | "depósito", "stock", "faltante" | `stock` |
| compras/proveedores | "proveedor", "cuit", "orden de compra" | `proveedores` |
| RRHH/sueldos | "sueldos", "empleados", "liquidación" | `administracion` |
| logística | "envíos", "remito", "flete" | `administracion` |

---

## CONTRATOS_REQUERIDOS

### 1. `BusinessTaxonomySnapshot`
*ADR-010 §Required Conceptual Contracts — ya definido; falta slice de implementación.*

```python
# Campos canónicos (ADR-010)
tenant_id: str
organism_type: TaxonomyType          # enum 9 tipos
industry: str                         # libre, inferido
size: str                             # micro/pequeña/mediana
complexity: str                       # simple/multi-area/multi-canal
sales_channels: List[str]             # local/mayorista/ml/ecommerce/mixto
operational_flow_stages: List[str]    # etapas del flujo operativo activas
areas_present: List[str]             # finanzas/stock/produccion/rrhh/...
systems_available: List[str]         # excel/sistema/cuaderno/varios
jurisdiction: str
currency: str
confidence: float                     # 0.0–1.0 (umbral bloqueante: 0.7)
source: str                           # "conversational_anamnesis"
created_at: datetime
```

**Regla de confianza:** cada campo confirmado por el dueño sube `confidence`. Campos inferidos no confirmados contribuyen 50%.

---

### 2. `OperationalHypothesis`
*ADR-010 — ciclo de vida: ABIERTA → EN_CONTRASTE → CONFIRMADA / DESCARTADA / EVIDENCIA_INSUFICIENTE*

```python
hypothesis_id: str
tenant_id: str
intake_id: str
formulation: str                      # texto no diagnóstico
source: str                           # "interrogation" | "owner_claim"
domain: str                           # dominio PymIA
related_symptoms: List[str]           # ALLOWED_SYMPTOMS
required_evidence: List[str]          # evidence_types
status: HypothesisStatus             # enum ciclo de vida
findings_refs: List[str]             # refs a DeliveryPackage si CONFIRMADA
created_at: datetime
closed_at: Optional[datetime]
```

---

### 3. `EvidenceRequirement`
*Extensión documentada de `IntakeEvidenceRequest` — añade contexto de anamnesis*

```python
requirement_id: str
tenant_id: str
intake_id: str
hypothesis_id: str                    # hipótesis que requiere esta evidencia
evidence_type: str                    # excel_ventas_costos / excel_caja_banco / ...
description: str                      # para mostrar al dueño en lenguaje simple
required_fields: List[str]
reason: str                           # por qué se necesita
blocks_analysis: bool
priority: int                         # 1=crítico, 2=importante, 3=complementario
telegram_message: str                 # mensaje listo para Hermes → Telegram
```

---

### 4. `ConversationContract`
*ADR-010 — actualizado en cada turno*

```python
contract_id: str
tenant_id: str
anamnesis_ref: str                    # BusinessAnamnesisRecord.anamnesis_id
taxonomy_ref: str                     # BusinessTaxonomySnapshot.snapshot_id
hypotheses_open: List[str]           # hypothesis_ids ABIERTA/EN_CONTRASTE
hypotheses_closed: List[str]         # hypothesis_ids CONFIRMADA/DESCARTADA
evidence_received: List[str]          # evidence_ids REGISTERED/LINKED
evidence_pending: List[str]           # evidence_ids REQUESTED
current_phase: ConversationPhase     # enum: ANAMNESIS/HIPOTESIS/EVIDENCIA/CONTRASTE/ENTREGA
allowed_actions: List[str]           # ["pedir_evidencia", "reformular_hipotesis", ...]
forbidden_actions: List[str]         # ["diagnosticar", "saltar_gate", ...]
```

---

### 5. `AnamnesisReadiness`
*ADR-010 — gate de paso de anamnesis a análisis*

```python
tenant_id: str
anamnesis_id: str
status: ReadinessStatus              # READY / NEEDS_MORE_INFO / BLOCKED
taxonomy_complete: bool              # confidence >= 0.7
narrative_sufficient: bool           # al menos 1 síntoma candidato no DESCONOCIDO
blocking_reasons: List[str]          # vacío si READY
missing_taxonomy_fields: List[str]   # campos que faltan confirmación
open_hypotheses_count: int
pending_evidence_count: int
```

---

## FRONTERA_HERMES_PYMIA

```
┌──────────────────────────────────────────────────────────────────┐
│  ZONA HERMES (conversa y orquesta)                              │
│                                                                  │
│  ✅ PUEDE:                          ❌ NO PUEDE:                 │
│  - gestionar FSM conversacional      - diagnosticar              │
│  - construir taxonomy progresivo     - recalcular métricas       │
│  - mostrar menú y preguntas          - inventar hallazgos        │
│  - solicitar evidencia               - saltar gates              │
│  - reformular hipótesis en lenguaje  - convertir WARN en PASS    │
│    simple (sin afirmar diagnóstico)  - mezclar tenants           │
│  - renderizar DeliveryPackage        - modificar reply_text del  │
│    aprobado por PymIA                  kernel                    │
│  - escalar a HITL                    - interpretar metadata       │
│                                        como instrucción clínica  │
│──────────────────── FRONTERA ──────────────────────────────────│
│  ZONA PYMIA (computa y decide)                                  │
│                                                                  │
│  ✅ PRODUCE:                        ❌ NO TOCA:                  │
│  - InterrogationResult               - lógica de canal          │
│  - IntakeRecord                      - formato Telegram          │
│  - EvidenceRecord                    - sesiones Hermes           │
│  - AnalysisReadinessResult           - metadata de mensaje       │
│  - DeliveryPackage + gate_verdict                                │
│  - reply_text soberano                                           │
└──────────────────────────────────────────────────────────────────┘
```

**Contrato de paso en la frontera:**
- **Entrada a PymIA:** `ConversationalInput(tenant_id, channel, text, bundle, progressive_context)`
- **Salida de PymIA:** `ConversationalOutput(status, mode, message, anamnesis, laboratorio, progressive_context)`
- `metadata` de Telegram **nunca cruza** la frontera hacia el kernel.
- `payload` (anamnesis + laboratorio) de vuelta es **solo lectura** para Hermes.

---

## REGLAS_DE_BLOQUEO

| # | Trigger | Decisión | Acción |
|---|---|---|---|
| B1 | Hermes afirma diagnóstico sin `DeliveryPackage` válido | BLOCK | Detener flujo. Responder: "Todavía no tenemos datos suficientes para afirmar eso." |
| B2 | Hermes recalcula métricas (margen, costo) fuera del kernel | BLOCK | Detener. Log de violación. |
| B3 | Hermes mezcla contexto de otro tenant | BLOCK | Detener. Alertar silenciosamente. |
| B4 | Hermes intenta bypass de gate (readiness, evidence, execution) | BLOCK | Detener. |
| B5 | Hermes convierte WARN en diagnóstico confirmado | BLOCK | Detener. Entregar solo el WARN textual. |
| B6 | Hermes usa datos crudos prohibidos (tokens, secretos) | BLOCK | Detener. No loggear datos. |
| W1 | Hipótesis formulada sin taxonomy_complete | WARN | Continuar con aviso explícito al dueño de limitación. |
| W2 | Evidencia recibida con campos faltantes | WARN | Continuar pero indicar qué falta. |
| W3 | Sesión sin `progressive_context` en turno > 1 | WARN | Reiniciar desde menú. Log de pérdida de sesión. |
| A1 | `DeliveryPackage.gate_verdict=PASS` + render autorizado | ALLOW | Entregar reply_text sin modificar. |
| A2 | Pedido de evidencia sin diagnóstico | ALLOW | Entregar mensaje con `EvidenceRequirement.telegram_message`. |
| A3 | Anamnesis en curso con confirmación de hipótesis | ALLOW | Continuar flujo FSM. |

**Regla general: fail-closed.** Cualquier caso no mapeado → BLOCK + mensaje genérico de "necesito más información".

---

## TESTS_PROPUESTOS

### Tests Documentales / Contractuales (no ejecutan código)

| ID | Descripción | Verifica |
|---|---|---|
| TCON-001 | `BusinessTaxonomySnapshot` válido con todos los campos bloqueantes completos | Estructura del contrato vs ADR-010 |
| TCON-002 | `OperationalHypothesis` con ciclo completo ABIERTA→CONFIRMADA | Transiciones de estado |
| TCON-003 | `ConversationContract.forbidden_actions` incluye `["diagnosticar", "saltar_gate"]` | Boundary policy |
| TCON-004 | `AnamnesisReadiness.status=READY` solo cuando `taxonomy_complete=True AND narrative_sufficient=True` | Gate de anamnesis |
| TCON-005 | `EvidenceRequirement.telegram_message` es string no vacío para cada tipo | Usabilidad |

### Tests de Contrato Hermes↔PymIA (fixture determinístico)

| ID | Escenario | Input | Resultado esperado |
|---|---|---|---|
| TINT-001 | Relato: "vendo mucho pero no me queda nada" | `message_text` sin selectors | `InterrogationResult.candidate_symptoms=[MARGEN_DUDOSO]`, `status=NEEDS_EVIDENCE` |
| TINT-002 | Sesión nueva sin texto | Vacío | Menú inicial, no análisis |
| TINT-003 | Hermes intenta afirmar diagnóstico sin `DeliveryPackage` | Mock de output con `gate_verdict=None` | `AuditDecision=BLOCK` |
| TINT-004 | `progressive_context` perdido en turno 2 | `previous_progressive_context=None` + turno > 1 | `AuditDecision=WARN`, reinicio desde menú |
| TINT-005 | Anamnesis con `confidence=0.4` intenta ir a análisis | `BusinessTaxonomySnapshot.confidence=0.4` | `AnamnesisReadiness.status=NEEDS_MORE_INFO`, bloqueo |
| TINT-006 | Relato de gastronomía | "tengo un restaurante y no me cierran los insumos" | `organism_type=gastronomia`, `domain=proveedores`, pregunta de desambiguación |
| TINT-007 | Producción/fábrica con señal de margen | "fabrico ropa y no sé si me queda ganancia" | `organism_type=textil` o `produccion`, `MARGEN_DUDOSO`, solicita excel_ventas_costos |
| TINT-008 | Flujo completo feliz | Relato + taxonomy + evidence Excel | `READINESS_READY_FOR_ANALYSIS`, `can_execute=True` |

### Tests de Integración Hermes↔conversa-engine (smoke, no ejecutantes en este plan)

| ID | Descripción |
|---|---|
| TSMK-001 | `run_message("vendo mucho pero no se si gano plata")` devuelve reply_text no vacío |
| TSMK-002 | `_PROGRESSIVE_CONTEXT_BY_SESSION` persiste entre turnos del mismo tenant/user |
| TSMK-003 | Comando reservado `--execute` devuelve `COMANDO_NO_IMPLEMENTADO` |
| TSMK-004 | `route_from_operational_audit` no cruza metadata al kernel |

---

## ROADMAP_IMPLEMENTACION

### Ciclo 1: Contratos y Fixtures Determinísticos
*Entregable: slices documentales + smoke tests sin runtime nuevo*

- [ ] Implementar `BusinessTaxonomySnapshot` como dataclass/Pydantic slice
  - campos bloqueantes, `confidence`, validación fail-closed
- [ ] Implementar `AnamnesisReadiness` como gate puro (análogo a `readiness.py`)
  - input: `BusinessTaxonomySnapshot + InterrogationResult`
  - output: `status, blocking_reasons, missing_taxonomy_fields`
- [ ] Implementar `OperationalHypothesis` slice (dataclass con ciclo de vida)
- [ ] Implementar `ConversationContract` como snapshot mutable por turno
- [ ] Implementar `EvidenceRequirement` (extensión de `IntakeEvidenceRequest` con `telegram_message`)
- [ ] Tests documentales TCON-001 a TCON-005
- [ ] Tests de contrato TINT-001 a TINT-008 (fixtures determinísticos, sin canal real)
- [ ] Actualizar `conversa-engine/main.py` con stub de `AnamnesisOrchestrator` (sin FSM completo)

**Criterio de cierre Ciclo 1:** todos los contratos tienen implementación mínima + tests PASS + sin cambios en kernel PymIA.

---

### Ciclo 2: FSM Conversacional + Menú Inicial + Anamnesis Adaptativa
*Entregable: flujo conversacional completo offline (sin Telegram real)*

- [ ] Implementar `AnamnesisOrchestrator` con FSM de estados (ver sección ESTADOS_CONVERSACIONALES)
- [ ] Implementar menú inicial (detecta sesión nueva vía `progressive_context is None`)
- [ ] Implementar preguntas de anamnesis adaptativa por taxonomía (9 tipos)
- [ ] Integrar `BusinessTaxonomySnapshot` progresivo con `ProgressiveTenantClinicalContext` existente
- [ ] Implementar `HermesAuditAgent` (ALLOW/WARN/BLOCK) como capa pre-reply
- [ ] Mapear flujo operativo completo (11 etapas) a señales léxicas + dominios PymIA
- [ ] Tests de integración TSMK-001 a TSMK-004
- [ ] Validar con 4 casos controlados (análogos a los definidos en `HERMES_AGENT_AUDIT_POLICY.md §Roadmap`)

**Criterio de cierre Ciclo 2:** flujo offline E2E funcional + audit layer operativo + sin canal Telegram real.

---

### Ciclo 3: Canal Telegram Real + Hardening de Producción
*Entregable: bot Telegram funcional con frontera Hermes↔PymIA auditada*

- [ ] Integrar `TelegramGateway` real (webhook o polling)
- [ ] Gestión de sesiones multi-tenant (mapping `chat_id → tenant_id`)
- [ ] Persistencia de `ConversationContract` por sesión (no solo en memoria)
- [ ] Manejo de archivos adjuntos (Excel vía `EvidenceBundle` existente)
- [ ] Rate limiting + reintentos con backoff
- [ ] Hardening de `HermesAuditAgent` con log de violaciones (sin datos sensibles)
- [ ] Test de carga con múltiples tenants simultáneos
- [ ] Runbook mínimo: inicio/parada, rollback, monitoreo de drift

**Criterio de cierre Ciclo 3:** bot en producción con audit trail completo + cero diagnósticos prematuros verificados.

---

## RIESGOS

| ID | Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|---|
| R1 | Deriva conversacional: Hermes afirma diagnóstico sin gate | Alta | Crítico | `HermesAuditAgent` obligatorio pre-reply (Ciclo 2) |
| R2 | `progressive_context` perdido entre turnos | Media | Alto | Reinicio desde menú + WARN log (implementado parcialmente) |
| R3 | Taxonomy inferida sin confirmación (confidence inflado) | Media | Alto | Confirmación explícita del dueño antes de `confidence ≥ 0.7` |
| R4 | Mezcla de tenants en sesiones de Telegram compartidas | Baja | Crítico | Mapping estricto `chat_id → tenant_id` desde Ciclo 3 |
| R5 | ADR-CAT-001 aspiracional malinterpretado como autorizado | Baja | Alto | Mantener nota explícita en ADR-010: no autoriza 12 catálogos |
| R6 | Implementación de contratos rompe slices existentes | Baja | Medio | Nuevos slices son independientes; no tocar `intake.py`, `readiness.py`, `interrogation.py` |

---

## DECISIONES_ABIERTAS

| # | Pregunta | Impacto | Urgencia |
|---|---|---|---|
| D1 | ¿`BusinessTaxonomySnapshot` vive en memoria (progressive_context) o persiste en storage? | Ciclo 2 | Alta |
| D2 | ¿`ConversationContract` se persiste por turno en storage o solo en sesión? | Ciclo 2 | Alta |
| D3 | ¿El `HermesAuditAgent` es un módulo Python puro o un LLM-judge separado? | Ciclo 2 | Media |
| D4 | ¿Se permite al dueño subir Excel en el turno de anamnesis o solo después de `LISTO_PARA_ANALISIS`? | Ciclo 1 | Media |
| D5 | ¿Mapping `chat_id → tenant_id` es manual (admin) o auto-generado en primer contacto? | Ciclo 3 | Baja |
| D6 | ¿`organism_type=mixto` requiere sub-encuadre o puede ir directo a interrogation? | Ciclo 1 | Baja |

---

## PROMPT_CODEX_CICLO_1

```
CONTEXTO
========
Repo: PymIA (SmartPyme — motor clínico conversacional)
Branch objetivo: feature/taxonomy-anamnesis-contracts-slice

FUENTE CANÓNICA
===============
- docs/adr/ADR-010-conversational-anamnesis-contract.md (contratos a implementar)
- pymia/smartpyme/readiness.py (patrón de implementación a seguir)
- pymia/smartpyme/intake.py (patrón de implementación a seguir)
- pymia/smartpyme/evidence.py (patrón de implementación a seguir)
- pymia/hermes/adapter.py (frontera Hermes↔PymIA — NO modificar)

OBJETIVO DEL CICLO 1
====================
Implementar 5 slices contractuales como módulos Python puros.
NO tocar kernel existente. NO crear MCP tools. NO crear UI ni bot real.

SLICES A IMPLEMENTAR
====================

1. pymia/smartpyme/taxonomy.py
   - BusinessTaxonomySnapshot (dataclass)
   - TaxonomyType enum (9 tipos: comercio, servicios, produccion_fabrica,
     distribucion, gastronomia, textil, salud_estetica, profesional, mixto)
   - create_taxonomy_snapshot() factory (fail-closed, confidence 0.0–1.0)
   - confirm_field() función que sube confidence al confirmar campo
   - Exportar __all__ correcto
   - NO diagnostica, NO persiste, NO llama a kernel

2. pymia/smartpyme/anamnesis_readiness.py
   - AnamnesisReadiness (dataclass)
   - ReadinessStatus enum (READY / NEEDS_MORE_INFO / BLOCKED)
   - evaluate_anamnesis_readiness(snapshot: BusinessTaxonomySnapshot,
                                   interrogation_result: InterrogationResult)
     -> AnamnesisReadiness
   - Criterio: READY iff confidence >= 0.7 AND candidate_symptoms != [DESCONOCIDO]
   - Fail-closed: cualquier ValueError → BLOCKED con blocking_reasons

3. pymia/smartpyme/operational_hypothesis.py
   - OperationalHypothesis (dataclass)
   - HypothesisStatus enum (ABIERTA, EN_CONTRASTE, CONFIRMADA, DESCARTADA,
     EVIDENCIA_INSUFICIENTE)
   - create_hypothesis() factory
   - update_hypothesis_status() función pura (no muta, devuelve nuevo objeto)

4. pymia/smartpyme/conversation_contract.py
   - ConversationContract (dataclass)
   - ConversationPhase enum (ANAMNESIS, HIPOTESIS, EVIDENCIA, CONTRASTE, ENTREGA)
   - create_conversation_contract() factory
   - update_contract_phase() función pura

5. pymia/smartpyme/evidence_requirement.py
   - EvidenceRequirement (dataclass, extiende semánticamente IntakeEvidenceRequest)
   - create_evidence_requirement() factory
   - Campo adicional: telegram_message: str (mensaje listo para enviar al dueño)
   - Campo adicional: priority: int (1=crítico, 2=importante, 3=complementario)

TESTS A IMPLEMENTAR
===================
tests/smartpyme/test_taxonomy.py — TCON-001 (BusinessTaxonomySnapshot)
tests/smartpyme/test_anamnesis_readiness.py — TCON-004 + TINT-005
tests/smartpyme/test_operational_hypothesis.py — TCON-002
tests/smartpyme/test_conversation_contract.py — TCON-003
tests/smartpyme/test_evidence_requirement.py — TCON-005

REGLAS OBLIGATORIAS
===================
- Cada módulo: puro, determinístico, fail-closed con ValueError.
- Sin persistencia, sin I/O, sin llamadas a HermesAdapter, sin MCP.
- Seguir exactamente el patrón de readiness.py (dataclass + __all__ + to_dict()).
- Sin imports de módulos Hermes ni de conversa-engine.
- Documentar cada función con docstring mínimo (qué hace, qué NO hace).

CRITERIO DE DONE
================
- pytest tests/smartpyme/ pasa en verde sin modificar código existente.
- mypy sobre los 5 módulos nuevos sin errores.
- Ningún import roto en módulos existentes.
```
