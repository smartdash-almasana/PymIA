# ADR-016 — Resolución Cognitivo-Mnemónica Hermes ↔ PymIA

## Status

Proposed

## Fecha

2026-05-27

## Frente

SMARTPYME_COGNITIVE_MNEMONIC_RESOLUTION_ARCHITECTURE

---

## Propósito

Definir una arquitectura de memoria para SmartPyme/PymIA que resuelva la amnesia conversacional entre interacciones, preserve coherencia longitudinal por tenant y evite que Hermes confunda memoria con verdad operacional.

El objetivo no es agregar “más memoria” de forma indiscriminada. El objetivo es separar capas mnémicas con funciones, autoridad, temporalidad y límites explícitos.

---

## Problema

El sistema tiene componentes funcionales pero todavía no integra memoria de forma consistente:

```text
Hermes conversa.
PymIA computa.
FSM guía anamnesis.
Gates bloquean análisis prematuro.
DeliveryPackage entrega resultados.
```

Sin embargo, la conversación puede degradarse por falta de consolidación mnémica:

```text
Turno 1: el dueño describe su negocio.
Turno 2: el sistema pregunta como si no hubiera escuchado.
Turno 3: el dueño reexplica.
Turno 4: el sistema vuelve a plantilla genérica.
```

Esto no es solo un bug de sesión. Es un problema cognitivo-mnemónico:

```text
memoria inmediata
→ memoria diferida conversacional
→ memoria operacional canónica
→ memoria pallium longitudinal
→ verdad computacional
```

Actualmente esas capas están mezcladas, ausentes o no gobernadas de forma suficiente.

---

## Tesis

La continuidad conversacional no debe depender solo del contexto activo del LLM.

La memoria debe separarse en capas:

- memoria inmediata efímera;
- memoria de sesión entre turnos vivos;
- memoria semántica diferida por tenant;
- estado operacional canónico;
- memoria pallium longitudinal;
- registros soberanos del kernel.

Regla arquitectónica central:

```text
Hermes puede recordar conversación.
Hermes no puede confirmar verdad operacional.
PymIA confirma verdad operacional.
```

---

## Principios

### 1. Separación de memorias

No existe una única memoria suficiente.

| Capa | Rol | Autoridad |
|---|---|---|
| Hermes working memory | Continuidad del turno activo | Baja |
| Hermes tenant session memory | Continuidad inmediata entre turnos vivos | Media-baja |
| Supermemory tenant recall | Memoria semántica diferida por tenant | Media |
| Supabase CMF | Estado operacional canónico | Alta |
| Obsidian Pallium | Historia cognitiva longitudinal | Auditiva / narrativa |
| PymIA records | Verdad computacional gateada | Soberana |

### 2. Tenant isolation obligatorio

Toda memoria debe estar particionada por:

```text
tenant_id
session_key
channel
```

Reglas:

```text
tenant_id ausente → BLOCK
tenant_id ambiguo → BLOCK
tenant_id cruzado → BLOCK
```

### 3. Memoria no equivale a verdad

Memoria puede contener:

```text
- declaraciones del dueño;
- hipótesis abiertas;
- señales conversacionales;
- preguntas pendientes;
- contexto operativo declarado.
```

Memoria no puede contener como verdad confirmada:

```text
- margen real;
- diagnóstico;
- hallazgos;
- readiness PASS;
- gate PASS;
- output_refs;
- conclusiones del kernel.
```

### 4. El kernel prevalece

Ante conflicto, prevalece esta jerarquía:

```text
PymIA records > Supabase CMF > Supermemory > Obsidian > Hermes working memory
```

---

## Arquitectura propuesta

Vista general:

```text
Usuario / Telegram / CLI
        ↓
Hermes working memory
        ↓
Tenant Memory Skill
        ├── Supermemory Tenant Recall
        ├── Supabase CMF Store
        └── Obsidian Pallium Skill
        ↓
Conversation / Anamnesis FSM
        ↓
Audit Skill
        ↓
PymIA Kernel, solo si gates permiten
        ↓
DeliveryPackage
        ↓
Hermes explica sin recalcular
```

---

## Capas mnémicas

### 1. Memoria inmediata efímera

**Nombre:** `Hermes Working Memory`

Rol: mantener coherencia dentro del turno y de la sesión viva.

Vive en:

```text
Hermes runtime / proceso activo
```

Puede recordar:

```text
- últimos mensajes;
- pregunta pendiente;
- intención actual;
- referencias locales;
- contexto conversacional inmediato.
```

No garantiza:

```text
- persistencia tras restart;
- aislamiento fuerte multiworker;
- trazabilidad longitudinal.
```

### 2. Memoria inmediata entre turnos vivos

**Nombre:** `HermesTenantSessionMemory`

Rol: evitar que Hermes reinicie la conversación mientras el proceso sigue vivo.

Backend inicial:

```text
in-process dict
```

Contrato conceptual:

```yaml
HermesTenantSessionMemory:
  tenant_id: str
  session_key: str
  turn_index: int
  recent_turns: list
  current_phase: str
  pending_question: str | null
  business_context: dict
  open_threads: list
  forbidden_actions: list
  updated_at: str
```

Uso:

```text
- recuperar últimos N turnos;
- no repetir menú;
- no preguntar lo ya respondido;
- conservar taxonomía conversacional parcial.
```

Restricción: no es memoria soberana. Puede descartarse.

### 3. Memoria semántica diferida por tenant

**Nombre:** `SupermemoryTenantRecall`

Rol: permitir que Hermes recuerde contexto relevante entre sesiones o reinicios usando búsqueda semántica.

Backend:

```text
Supermemory
```

Scope obligatorio:

```text
containerTag = tenant:{tenant_id}
```

Identificadores:

```text
customId = turn:{tenant_id}:{session_key}:{turn_index}
customId = session:{tenant_id}:{session_key}
```

Guarda:

```text
- resumen seguro del turno;
- negocio declarado;
- canales declarados;
- flujo operativo;
- hipótesis abiertas;
- evidencia mencionada;
- pregunta pendiente.
```

No guarda:

```text
- Excel crudo;
- hallazgos no gateados;
- diagnósticos;
- resultados computacionales no confirmados.
```

### 4. Estado operacional canónico

**Nombre:** `ConversationMemoryField` (`CMF`)

Backend:

```text
Supabase Postgres
```

Rol: ser el checkpoint oficial del estado conversacional-operacional rehidratable.

Contrato conceptual:

```yaml
ConversationMemoryField:
  session_key: str
  tenant_id: str
  user_id: str | null
  channel: str

  conversation_state:
    turn_index: int
    phase: str
    last_user_message: str
    last_bot_message: str
    pending_question: str | null
    allowed_next_actions: list
    forbidden_next_actions: list

  anamnesis_state:
    taxonomy: dict
    hypotheses: list
    evidence_requests: list
    readiness: dict

  trace:
    last_intake_id: str | null
    last_delivery_package_id: str | null

  version: int
  updated_at: str
  expires_at: str | null
```

Propiedades obligatorias:

```text
- persistente;
- versionado;
- tenant-scoped;
- fail-closed;
- auditable;
- recuperable tras restart.
```

### 5. Memoria pallium longitudinal

**Nombre:** `Obsidian Pallium Memory Layer`

Rol: guardar historia cognitiva, narrativa y auditiva del caso.

Backend:

```text
Obsidian vault
```

Estructura:

```text
Pymia-pallium/
  tenants/
    tenant_001/
      _index.md
      timeline.md
      taxonomy.md
      hypotheses.md
      evidence_requests.md
      contradictions.md
      readiness_history.md
      kernel_outputs.md
      owner_decisions.md
```

Puede contener:

```text
- relato literal;
- señales detectadas;
- evolución de taxonomía;
- hipótesis abiertas;
- contradicciones;
- evidencia solicitada;
- decisiones humanas;
- outputs gateados del kernel.
```

No puede ser:

```text
- estado transaccional principal;
- fuente de readiness;
- fuente de hallazgos confirmados.
```

### 6. Verdad computacional soberana

**Nombre:** `PymIA Kernel Records`

Rol: confirmar o bloquear verdad operacional.

Solo PymIA puede producir:

```text
- EvidenceSufficiencyResult;
- AnalysisReadinessResult;
- RuntimeExecutionCandidate;
- MicroserviceExecutionResult;
- ExecutionResultGateVerdict;
- DeliveryPackage;
- DeliveryMarkdown.
```

---

## Plugins y Skills

### Distinción

```text
Plugin = capacidad ejecutable.
Skill = política de uso.
```

La solución debe usar ambos.

---

## Plugins propuestos

### 1. `supermemory_tenant_recall`

Funciones:

```text
recall_tenant_context(tenant_id, query, limit)
save_tenant_turn_summary(tenant_id, session_key, turn_index, summary)
save_tenant_fact(tenant_id, fact, metadata)
```

### 2. `supabase_cmf_store`

Funciones:

```text
load_cmf(session_key)
save_cmf(session_key, cmf, expected_version)
append_cmf_event(session_key, event)
```

### 3. `obsidian_pallium_writer`

Funciones:

```text
append_timeline_entry(tenant_id, entry)
update_taxonomy_note(tenant_id, taxonomy_snapshot)
append_hypothesis(tenant_id, hypothesis)
append_contradiction(tenant_id, contradiction)
append_kernel_result(tenant_id, delivery_package_ref)
```

---

## Skills propuestos

### 1. `SmartPymeTenantMemorySkill`

Responsabilidad:

```text
- resolver tenant_id;
- bloquear memoria sin tenant;
- imponer scope tenant;
- decidir qué backend consultar;
- impedir cross-tenant recall.
```

### 2. `SmartPymeMemoryRecallSkill`

Responsabilidad:

```text
- recuperar memoria útil antes de responder;
- priorizar CMF sobre Supermemory;
- usar Supermemory solo como contexto semántico;
- descartar memoria contradictoria con PymIA.
```

### 3. `SmartPymeMemoryWriteSkill`

Responsabilidad:

```text
- decidir qué se guarda;
- resumir turno de forma segura;
- diferenciar declaración, hipótesis y hallazgo;
- impedir escritura de diagnósticos no confirmados.
```

### 4. `SmartPymeMemoryAuditSkill`

Responsabilidad:

```text
- ALLOW / WARN / BLOCK;
- auditar lectura y escritura;
- bloquear uso indebido de memoria;
- impedir que Hermes use memoria como verdad computacional.
```

---

## Flujo por turno

```text
1. Mensaje entra.
2. Resolver tenant_id y session_key.
3. Cargar HermesTenantSessionMemory.
4. SmartPymeTenantMemorySkill valida tenant.
5. Cargar CMF desde Supabase si existe.
6. Buscar contexto en Supermemory con containerTag tenant:{tenant_id}.
7. Construir contexto conversacional seguro.
8. Ejecutar Hermes / FSM.
9. MemoryAuditSkill revisa propuesta.
10. Actualizar memoria inmediata.
11. Guardar CMF si cambió estado operacional.
12. Guardar resumen seguro en Supermemory.
13. Append narrativo en Obsidian Pallium.
14. Responder.
```

---

## Estados de decisión mnémica

```text
ALLOW
WARN
BLOCK
```

### ALLOW

Se permite leer/escribir memoria.

Ejemplo:

```text
Guardar que el tenant declaró fabricar ropa y vender por Mercado Libre.
```

### WARN

Se permite, pero con advertencia.

Ejemplo:

```text
La memoria recuperada dice “textil”, pero el usuario ahora dice “gastronomía”. Requiere confirmación.
```

### BLOCK

No se permite.

Ejemplo:

```text
Hermes intenta guardar “margen bajo confirmado” sin DeliveryPackage PASS.
```

---

## Reglas de bloqueo

```text
BLOCK si tenant_id está ausente.
BLOCK si búsqueda no filtra por tenant.
BLOCK si escritura no filtra por tenant.
BLOCK si se intenta guardar diagnóstico no gateado.
BLOCK si se intenta guardar readiness PASS desde Hermes.
BLOCK si se intenta guardar output_refs inventados.
BLOCK si se intenta leer Obsidian fuera de /tenants/{tenant_id}/.
BLOCK si Supermemory se consulta sin containerTag tenant-scoped.
BLOCK si se intenta ejecutar PymIA solo por memoria recuperada.
```

---

## Reglas de consolidación

### De working memory a Supermemory

Guardar solo resumen seguro:

```text
El dueño declaró que fabrica ropa, vende mayorista y por Mercado Libre.
Dolor declarado: no sabe si gana plata.
Hipótesis abierta: posible margen erosionado.
No hay hallazgos confirmados.
```

### De Supermemory a CMF

Nunca directo.

Supermemory puede sugerir contexto, pero el CMF solo cambia mediante transición validada.

```text
Supermemory → propuesta contextual
CMF → estado gobernado
```

### De CMF a Obsidian

Permitido: CMF puede proyectarse a Obsidian como snapshot auditivo.

### De PymIA a Obsidian

Permitido: solo outputs gateados.

---

## Test conceptual mínimo

```text
1. Mismo tenant recuerda negocio declarado en 5 turnos.
2. Tenant B no accede a memoria de tenant A.
3. Supermemory search sin containerTag genera BLOCK.
4. Intento de guardar diagnóstico desde Hermes genera BLOCK.
5. Hipótesis abierta se permite.
6. Hallazgo confirmado solo se permite con DeliveryPackage PASS.
7. Memoria recuperada contradice CMF: gana CMF.
8. Restart simulado: Supermemory recupera contexto conversacional.
9. CMF ausente + Supermemory presente: Hermes pregunta confirmación, no asume.
10. Obsidian append fuera de carpeta tenant genera BLOCK.
```

---

## Roadmap mínimo

### Ciclo 1 — Diseño documental

Frente:

```text
SMARTPYME_COGNITIVE_MNEMONIC_RESOLUTION_ARCHITECTURE
```

Archivos:

```text
docs/adr/ADR-016-resolucion-cognitivo-mnemonica-hermes-pymia.md
docs/hermes/SMARTPYME_MEMORY_SKILLS_AND_PLUGINS.md
docs/smartpyme/COGNITIVE_MNEMONIC_BOUNDARY.md
tests/docs/test_cognitive_mnemonic_resolution_contract.py
```

PASS:

```text
- define capas de memoria;
- define autoridad por capa;
- define plugins y skills;
- define reglas de bloqueo;
- no implementa runtime.
```

### Ciclo 2 — Supermemory tenant recall

Frente:

```text
SMARTPYME_SUPERMEMORY_TENANT_RECALL_PLUGIN
```

Archivos probables:

```text
conversa-engine/plugins/supermemory_tenant_recall.py
conversa-engine/skills/smartpyme_memory_recall.md
conversa-engine/skills/smartpyme_memory_write.md
tests/conversa_engine/test_supermemory_tenant_recall.py
```

PASS:

```text
- usa tenant_id obligatorio;
- usa containerTag tenant-scoped;
- no guarda datos prohibidos;
- no mezcla tenants.
```

### Ciclo 3 — Supabase CMF

Frente:

```text
SMARTPYME_SUPABASE_CMF_STORE
```

Archivos probables:

```text
conversa-engine/plugins/supabase_cmf_store.py
docs/smartpyme/CONVERSATION_MEMORY_FIELD_CONTRACT.md
tests/conversa_engine/test_supabase_cmf_store.py
```

PASS:

```text
- load/save versionado;
- fail-closed;
- estado rehidratable;
- no sobrescribe versiones conflictivas.
```

---

## No autorizado todavía

Este ADR no autoriza:

```text
- perfiles Hermes por tenant;
- Docker por tenant;
- Hindsight;
- Honcho;
- Obsidian como estado primario;
- Telegram productivo;
- ejecución automática de kernel;
- memoria global no tenant-scoped;
- agent autonomy sobre PymIA;
- cambios en PymIA kernel;
- nuevas MCP tools productivas.
```

---

## Decisión final

La resolución cognitivo-mnemónica correcta es:

```text
Hermes recuerda conversación mediante skills y plugins gobernados.
Supermemory aporta memoria semántica tenant-scoped.
Supabase CMF conserva estado operacional canónico.
Obsidian Pallium conserva historia cognitiva longitudinal.
PymIA confirma verdad computacional.
```

Frase rectora:

```text
La memoria conversacional puede orientar la conversación, pero solo el kernel gateado puede confirmar la realidad operacional.
```
