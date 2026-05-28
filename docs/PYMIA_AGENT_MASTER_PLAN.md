# Plan Maestro — PymIA Agent
## De OS determinístico a Agente PyME especializado

**Versión:** 1.0  
**Fecha:** 2026-05-29  
**Estado:** Propuesta inicial

---

## Visión del producto

```
PymIA Agent = LLM operator (cerebro)
            + PymIA OS (sistema nervioso determinístico)
            + PyME Skills (manos especializadas)
            + PyME Memory (aprendizaje por empresa)
            + Approval workflows (control humano)
```

**Propuesta de valor:** Un agente que se vuelve experto en **tu** PyME, con razonamiento conversacional de LLM pero decisiones de negocio ejecutadas por un OS determinístico, auditable y testeable.

---

## Principios arquitectónicos no negociables

1. **LLM invoca, OS ejecuta.** El LLM nunca ejecuta lógica de negocio directamente.
2. **Tools determinísticas.** Cada tool del OS retorna el mismo output para el mismo input.
3. **Contratos Pydantic.** Entrada y salida de cada tool validada con schemas.
4. **Decision trail obligatorio.** Cada invocación queda registrada en el OS.
5. **Fail-closed.** Si algo falla, el OS retorna error estructurado; el LLM no inventa.
6. **578 tests preservados.** El OS determinístico no se degrada por agregar LLM.
7. **Aislamiento multi-tenant.** Cada empresa tiene estado, memoria y skills propios.

---

## Stack tecnológico recomendado

| Capa | Tecnología | Justificación |
|------|-----------|---------------|
| LLM operator | **PydanticAI** | Tools estructuradas, validación Pydantic, multi-provider |
| LLM provider | OpenAI GPT-4o / Claude 3.5 | Balance costo/calidad/español |
| Vector memory | **ChromaDB local** | Ligero, sin infraestructura externa |
| Observabilidad | **Langfuse** | Trazabilidad LLM + OS en un solo lugar |
| Cache | Redis (opcional en fase 2+) | Para skills con cálculos pesados |
| Storage | Filesystem + SQLite (metadata) | Mantener simplicidad actual |

**No se agregan:** LangGraph, CrewAI, Hermes como framework, bases de datos relacionales pesadas.

---

## Fases del plan

### **FASE 0 — Fundación LLM** (Ciclos 15-16) · 2 semanas

**Objetivo:** Conectar el OS a un LLM operator mínimo que pueda mantener una conversación PyME básica.

**Entregables:**
- `pymia/llm_operator/operator.py` — PydanticAI Agent
- `pymia/llm_operator/tools.py` — 5 tools iniciales exponiendo capacidades del OS
- `pymia/llm_operator/prompts.py` — System prompt especializado en PyME
- `pymia/llm_operator/smoke.py` — REPL local para probar conversaciones
- Test de integración: LLM → tool del OS → resultado determinístico

**Tools iniciales:**
1. `dispatch_diagnostic(excel_path)` — Ejecuta diagnóstico Excel
2. `run_anamnesis_turn(context, message)` — Turno de anamnesis
3. `ask_evidence(evidence_type, reason)` — Pide evidencia
4. `get_conversation_summary()` — Resumen del caso actual
5. `get_company_profile()` — Perfil de la empresa (vacío al inicio)

**Criterios de éxito:**
- LLM puede mantener conversación de 5+ turnos sobre un Excel real
- Decision trail del OS registra cada tool invocada
- 600+ tests pasando (578 + ~25 nuevos)
- Smoke local funcional sin Telegram

**Riesgos:**
- Latencia LLM (mitigación: streaming de respuestas)
- Costos de API (mitigación: cache de respuestas frecuentes)
- Prompt injection (mitigación: tools validan inputs con Pydantic)

---

### **FASE 1 — Skills PyME core** (Ciclos 17-22) · 6 semanas

**Objetivo:** 5-6 skills especializados que resuelvan problemas reales de PyMEs.

**Skills priorizados (orden de impacto):**

| Skill | Microservicio | Problema que resuelve |
|-------|---------------|----------------------|
| **Conciliación bancaria** | `bank_reconciliation` | Matchear extracto vs libro contable |
| **Control de stock** | `stock_movement` | Rotación, quiebres, valoración |
| **Análisis de caja** | `cash_flow` | Proyección y desvíos |
| **Rentabilidad** | `profitability` | Margen por producto/cliente |
| **Comparativos** | `period_comparison` | Mes a mes, año a año, budget vs real |
| **Facturación** | `invoice_audit` | IVA, retenciones, duplicados |

**Patrón por skill:**
```
1. Nuevo microservicio en pymia/smartpyme/<skill>.py
2. Adapter en pymia/llm_operator/tools/<skill>.py
3. Tests del microservicio (determinísticos)
4. Tests del tool (LLM lo usa correctamente)
5. Documentación en docs/skills/<skill>.md
```

**Piloto:** Seleccionar 2-3 PyMEs reales para probar cada skill.

**Criterios de éxito:**
- 6 skills funcionando end-to-end
- 3 PyMEs piloto usando al menos 2 skills cada una
- 800+ tests pasando
- Feedback real de usuarios documentado

**Riesgos:**
- Complejidad de dominio (mitigación: trabajar con contador/asesor PyME)
- Datos reales sensibles (mitigación: anonimización + acuerdos NDA)
- Skills demasiado genéricos (mitigación: validación con empresa real antes de commit)

---

### **FASE 2 — Memoria empresarial** (Ciclos 23-25) · 3 semanas

**Objetivo:** El agente aprende de cada empresa y mejora con el tiempo.

**Entregables:**

1. **Perfil de empresa evolutivo** (`pymia/memory/company_profile.py`)
   - Estructura de costos aprendida
   - Patrones de ingresos (estacionalidad)
   - Productos/clientes más relevantes
   - Nivel técnico del operador (adapta lenguaje)

2. **Memoria vectorial** (`pymia/memory/vector_store.py`)
   - ChromaDB por tenant
   - Embeddings de conversaciones previas
   - Búsqueda semántica para context retrieval

3. **Pattern detector** (`pymia/memory/patterns.py`)
   - Detección de anomalías vs histórico
   - Tendencias de largo plazo
   - Alertas proactivas

**Criterios de éxito:**
- Agente recuerda contexto entre sesiones sin pedirlo
- Detecta al menos 3 tipos de anomalías vs histórico
- Memoria aislada por tenant (test de fuga de datos)
- 850+ tests pasando

**Riesgos:**
- Memoria que crece sin control (mitigación: políticas de retención)
- Embeddings costosos (mitigación: embedding diferido + cache)
- Sesgos aprendidos (mitigación: usuario puede "olvidar" patrones)

---

### **FASE 3 — Integraciones verticales** (Ciclos 26-30) · 5 semanas

**Objetivo:** Conectar con el ecosistema PyME argentino real.

**Conectores priorizados:**

| Integración | Tipo | Justificación |
|-------------|------|---------------|
| **MercadoPago** | Ingesta | Movimientos de pago muy usados |
| **AFIP (webservices)** | Ingesta + salida | Facturación electrónica |
| **Tango / Bejís / Xubio** | Ingesta | Software contable PyME |
| **Excel/CSV mejorado** | Ingesta | Normalización automática |
| **Email (SMTP/IMAP)** | Salida | Envío de reportes |
| **Webhooks genéricos** | Salida | Integración con otros sistemas |

**Arquitectura de plugins:**
```
pymia/plugins/
├── base.py              # Contrato Plugin (ingest, export, sync)
├── registry.py          # Descubrimiento y carga
├── mercadopago/
├── afip/
├── tango/
└── ...
```

**Criterios de éxito:**
- 5 plugins funcionando con datos reales
- Plugin API estable con contrato documentado
- Usuarios pueden habilitar/deshabilitar plugins
- 900+ tests pasando

**Riesgos:**
- APIs de terceros cambiantes (mitigación: adapters con versionado)
- Credenciales sensibles (mitigación: vault local, nunca en logs)
- Rate limiting de APIs externas (mitigación: backoff + cache)

---

### **FASE 4 — Control humano y auditoría** (Ciclos 31-33) · 3 semanas

**Objetivo:** Workflows de aprobación y reportes auditables formalmente.

**Entregables:**

1. **Approval engine** (`pymia/approvals/engine.py`)
   - Políticas configurables por acción/tenant
   - Canales de aprobación (Telegram, email, web)
   - Timeouts y escalaciones

2. **Audit reports** (`pymia/audit/reports.py`)
   - Reportes PDF firmados
   - Trazabilidad completa por decisión
   - Exportación para contadores/auditores

3. **Web dashboard read-only** (`pymia/web/dashboard.py` — opcional)
   - Vista de casos activos
   - Histórico de decisiones
   - Configuración de skills/plugins

**Criterios de éxito:**
- Approval flow funcional para acciones sensibles
- Reportes PDF generados con trazabilidad
- 950+ tests pasando

**Riesgos:**
- UX de approvals muy invasiva (mitigación: defaults razonables)
- Complejidad de dashboard (mitigación: MVP web muy acotado, quizás no hacer)

---

### **FASE 5 — Multi-tenant y escalabilidad** (Ciclos 34-36) · 3 semanas

**Objetivo:** Soporte robusto de múltiples empresas, onboarding self-service, monetización.

**Entregables:**

1. **Tenant isolation reforzado** (tests explícitos de fuga)
2. **Onboarding wizard** (alta de empresa en 5 minutos)
3. **Planes y billing** (free / pro / enterprise)
4. **Rate limiting** por tenant
5. **Backup automático** por tenant

**Criterios de éxito:**
- 10+ empresas en producción
- Onboarding completo sin asistencia humana
- 1000+ tests pasando

---

## Cronograma consolidado

| Fase | Duración | Semanas acumuladas | Entregable clave |
|------|----------|-------------------|------------------|
| F0 — Fundación LLM | 2 sem | 2 | LLM operator + 5 tools básicas |
| F1 — Skills PyME | 6 sem | 8 | 6 skills + 3 PyMEs piloto |
| F2 — Memoria | 3 sem | 11 | Perfil empresa + vector memory |
| F3 — Integraciones | 5 sem | 16 | 5 plugins reales |
| F4 — Control/Auditoría | 3 sem | 19 | Approvals + reportes |
| F5 — Multi-tenant | 3 sem | 22 | Producto comercializable |

**Total: ~5-6 meses** hasta producto comercializable.

---

## Plan de pruebas

### Estrategia por capa

| Capa | Tipo de tests | Objetivo |
|------|--------------|----------|
| OS determinístico | Unit tests | Mantener los 578+ |
| Tools del LLM | Integration tests | Validar que LLM no rompe contratos |
| LLM behavior | Eval tests (PydanticAI evals) | Calidad de respuestas |
| Skills PyME | Domain tests | Correctitud contable/fiscal |
| End-to-end | Longitudinal tests | Casos completos como C10 |

### Métricas de calidad

- **Cobertura:** >85% en OS, >70% en LLM layer
- **Regression rate:** <2% de tests rotos por ciclo
- **LLM eval score:** >80% en benchmark PyME propio

---

## Plan de pilotos

| Piloto | Perfil | Objetivo | Skills a validar |
|--------|--------|----------|------------------|
| **Piloto 1** | Comercio minorista | Conciliación + stock | bank_reconciliation, stock_movement |
| **Piloto 2** | Industria chica | Costos + rentabilidad | profitability, invoice_audit |
| **Piloto 3** | Servicios profesionales | Caja + comparativos | cash_flow, period_comparison |

Cada piloto: 4 semanas, feedback quincenal, ajuste de skills en caliente.

---

## Hitos de validación con usuario real

1. **Hito 1 (semana 4):** LLM conversa con piloto 1 sobre su Excel real
2. **Hito 2 (semana 10):** Piloto 1 usa conciliación bancaria sin asistencia
3. **Hito 3 (semana 14):** Piloto 2 descubre anomalía de rentabilidad que no sabía
4. **Hito 4 (semana 18):** 3 pilotos integrados con su software contable
5. **Hito 5 (semana 22):** Reporte de auditoría generado automáticamente

---

## Estrategia de rollback

Cada fase es **independiente y reversible**:

- **Si F0 falla:** OS sigue funcionando sin LLM. Solo se deshabilita el canal conversacional.
- **Si F1 falla:** Los skills no funcionan, pero el OS base sigue intacto.
- **Si F2 falla:** Se pierde memoria longitudinal, pero no funcionalidad core.
- **Si F3 falla:** Se deshabilitan integraciones, operación manual sigue posible.
- **Si F4 falla:** Se deshabilitan approvals, pero el OS responde directo.
- **Si F5 falla:** Se vuelve a single-tenant mientras se corrige.

**Principio:** cada fase agrega, ninguna fase es crítica para las anteriores.

---

## Decisiones abiertas (requieren input del negocio)

1. **¿Qué PyMEs son pilotos reales?** Necesitamos 3 empresas comprometidas.
2. **¿Modelo de monetización?** SaaS mensual, por uso, freemium, enterprise.
3. **¿Hosting?** Self-hosted por cliente vs SaaS multi-tenant.
4. **¿Equipo?** ¿Cuántos devs/contador/diseñador dedicados?
5. **¿Velocidad vs perfección?** Time-to-market agresivo o pulido antes de piloto.

---

## Próximo paso inmediato

**C15 — LLM operator con PydanticAI** es el primer paso concreto.

Si aprobás el plan, el próximo mensaje de Coder debería ser el diseño detallado de C15:
- Tools iniciales
- System prompt
- Smoke local
- Tests de integración LLM↔OS

**¿Avanzamos con C15 como primera fase del plan?**

---

## Apéndice: Estado actual del proyecto

### Lo que ya tenemos (C1-C14)

- **OS determinístico** — 578 tests, fail-closed, auditable
- **Conversación progresiva** — progressive_context, anamnesis FSM
- **Persistencia longitudinal** — state_storage, replay, audit_cli
- **Adapter conversacional** — C9 ya puentea OS ↔ dominio
- **Primer microservicio PyME** — excel_diagnostic
- **Frontera delgada Telegram** — ya funciona
- **Contratos + guardrails** — C11 + C12

### Lo que necesitamos agregar

- **Capa LLM** (F0) — Cerebro conversacional
- **Skills PyME** (F1) — Manos especializadas
- **Memoria empresarial** (F2) — Aprendizaje por empresa
- **Integraciones** (F3) — Conectores al ecosistema
- **Control humano** (F4) — Approvals y auditoría
- **Multi-tenant** (F5) — Escalabilidad comercial

---

**Documento generado:** 2026-05-29  
**Autor:** PymIA Team  
**Próxima revisión:** Post C15 implementación
