# Hallazgos — Accio Work y relevancia para PymIA

**Fecha:** 2026-08-11 18:43 (America/Argentina/Buenos_Aires)  
**Estado:** Documento de hallazgos estratégicos y arquitectónicos  
**Objeto analizado:** Accio Work (Alibaba)  
**Fuente inicial:** https://es.accio.com/work/doc?slug=help-about

---

## 1. Propósito

Este documento consolida los hallazgos obtenidos al analizar Accio Work y los contrasta con la arquitectura y filosofía actuales de PymIA / SmartPyme.

No propone copiar Accio Work como producto.

Busca identificar patrones arquitectónicos, operativos y de gobierno que puedan ser útiles para PymIA sin ampliar innecesariamente el alcance de Servicio 1.

---

# 2. Veredicto ejecutivo

Accio Work es relevante para PymIA principalmente como **referencia arquitectónica**, no como modelo comercial a copiar.

Su arquitectura confirma varios patrones que PymIA ya viene desarrollando conceptualmente:

```text
agente persistente
+ identidad
+ memoria
+ workspace
+ skills
+ herramientas
+ permisos
+ conectores
+ automatizaciones
+ equipos/subagentes
+ aprendizaje desde trazas
```

Sin embargo, existe una diferencia genética decisiva:

```text
Accio Work
→ plataforma horizontal de ejecución de trabajo

PymIA
→ capa vertical de control, evidencia, excepción y decisión empresarial
```

Copiar la superficie de Accio Work empujaría PymIA hacia un AI Workspace horizontal y aumentaría innecesariamente el alcance.

La utilización correcta es:

```text
ACCIO COMO REFERENCIA ARQUITECTÓNICA: P0
ACCIO COMO MODELO DE PRODUCTO A COPIAR: P3 / NO
```

---

# 3. Qué es Accio Work realmente

Accio Work no es solamente un chatbot con herramientas.

La documentación muestra una plataforma de agentes persistentes capaces de operar sobre archivos, web, terminal, navegador, conectores, automatizaciones y equipos de agentes.

La superficie conceptual principal es:

```text
usuario
  ↓
conversación
  ↓
Agent
  ↓
tools / skills / connectors
  ↓
ejecución
  ↓
artefactos / acciones / resultados
```

La plataforma separa explícitamente:

```text
Agents
Capabilities
  ├─ Automations
  ├─ Connectors
  ├─ Skills
  ├─ Channels
  └─ Pairings
Messages
```

---

# 4. Hallazgo P0 — El agente no es solamente prompt + LLM

Accio modela al agente como una entidad persistente con componentes separados.

La documentación describe elementos equivalentes a:

```text
Name
Role description
Template
Toolset
Workspace
Memory
Skills
```

Además utiliza un `agent-core` compuesto por archivos conceptualmente diferenciados:

```text
SOUL.md
IDENTITY.md
AGENTS.md
MEMORY.md
USER.md
diary/
skills/
```

La lección arquitectónica relevante no está en copiar esos nombres, sino en la separación:

```text
identidad
≠
instrucciones
≠
memoria
≠
historial
≠
capacidad
```

## Implicancia para PymIA

PymIA no debería confiar continuidad, identidad o políticas al contexto efímero del LLM.

Esto converge con el principio ya definido:

```text
Execution
≠
Evidence
≠
Learning
≠
Architecture
```

---

# 5. Hallazgo P0 — Workspace explícito por agente

Accio asigna un workspace propio al agente.

Conceptualmente:

```text
Agent
  ├─ identity
  ├─ memory
  ├─ skills
  └─ workspace
```

Esto reduce el riesgo de agentes con acceso indiscriminado a todos los archivos.

## Aplicación potencial a la Factoría PymIA

La frontera de trabajo debería ser física además de semántica.

Ejemplo:

```text
auditor
→ workspace / scope read-only

implementador
→ workspace / files_allowed

certificador
→ code read + test execution

integrador
→ git / PR boundary
```

No debería depender solamente de instrucciones en lenguaje natural.

---

# 6. Hallazgo P0 — Capability-scoped agents

Accio no otorga todas las herramientas a todos los agentes.

Utiliza conjuntos de capacidades según el rol, con perfiles semejantes a:

```text
Standard
Full
Minimal
Team Lead
```

La idea importante es:

```text
rol
→ capability set
→ herramientas permitidas
```

no:

```text
agente
→ acceso universal
```

## Aplicación PymIA

Conviene preservar una separación fuerte entre:

```text
CAPABILITY_AVAILABLE
EXECUTION_AUTHORIZED
DELIVERY_AUTHORIZED
BUSINESS_DECISION_AUTHORIZED
```

Estas cuatro condiciones no deben confundirse.

---

# 7. Hallazgo P0 — Reviewer físicamente read-only

Accio incluye perfiles de revisión con toolsets de solo lectura.

La diferencia crítica es:

```text
"no modifiques nada"
```

versus:

```text
"no existe herramienta de escritura disponible"
```

La segunda opción es arquitectónicamente superior.

## Aplicación PymIA / Factoría

```text
auditor
→ READ ONLY

builder
→ WRITE AUTORIZADO

certificador
→ READ + EXECUTE TESTS

integrador
→ GIT / PR
```

La diferenciación debe vivir en capacidades y políticas, no sólo en prompts.

---

# 8. Hallazgo P0 — Skills separadas del agente

Accio trata las Skills como capacidades instalables y jerarquizadas.

Conceptualmente aparece una precedencia similar a:

```text
Agent-level Skills
↓
Account-level Skills
↓
Built-in Skills
```

Esto permite que el core permanezca más estable mientras las capacidades evolucionan de manera independiente.

## Aplicación PymIA

Evitar:

```text
PymIA Core
=
margen
+ stock
+ consorcios
+ distribuidores
+ Mercado Libre
+ contadores
+ ...
```

Preferir:

```text
core estable
+
capabilities gobernadas
+
vertical/domain behavior
```

---

# 9. Hallazgo P0 — Versionado de Skills

Accio incorporó visibilidad/versionado de Skills.

Esto valida un principio importante para PymIA:

> Una capacidad que evoluciona necesita identidad y versión.

Modelo conceptual compatible con el diseño existente de PymIA:

```yaml
skill_id:
version:
purpose:
contract_hash:
allowed_tools:
required_inputs:
expected_outputs:
required_evidence:
known_limitations:
```

No implica copiar el formato de Accio, sino preservar el principio de versionado gobernado.

---

# 10. Hallazgo crítico — SkillHarvest

Uno de los hallazgos más relevantes es `SkillHarvest`.

Accio describe una capacidad para derivar nuevas Skills a partir de trazas de ejecución de los agentes.

Patrón conceptual:

```text
ejecución
↓
trace
↓
patrón útil
↓
SkillHarvest
↓
capacidad reutilizable
```

Esto converge directamente con la idea de `LearningMemory` de PymIA:

```text
Evidence
→ evaluación
→ candidato a aprendizaje
→ revisión
→ LearningMemory
→ mejora de SkillSpec / TaskSpec
```

## Decisión para PymIA

Adoptar el principio, pero con gobierno más estricto.

No usar:

```text
una ejecución
→ skill automática
```

Usar:

```text
ExecutionTrace
→ LearningCandidate
→ evidence_count
→ tenant scope / cross-tenant distinction
→ review
→ APPROVED
→ Skill / DomainPattern / EvidenceRule
```

Esto evita sobreajuste y contaminación semántica.

---

# 11. Hallazgo P1 — Memoria separada de Knowledge Base

Accio evolucionó hacia:

```text
Agent Memory
≠
Enterprise Knowledge Base
```

La distinción es conceptualmente sana.

## Correspondencia PymIA

```text
Tenant Memory
≠
LearningMemory
≠
Domain Knowledge
≠
ArchitecturalDNA
```

No todo conocimiento debe almacenarse en una memoria universal.

---

# 12. Hallazgo P1 — Dos patrones multiagente diferentes

Accio distingue:

## Agent Team

```text
Agent A
Agent B
Agent C
↓
shared project conversation
```

Útil para colaboración prolongada entre roles.

## SubAgent

```text
Main Agent
  ├─ SubAgent A
  ├─ SubAgent B
  └─ SubAgent C
```

Útil para subtareas delegables y relativamente independientes.

## Lección para PymIA

No usar multiagente como solución universal.

Servicio 1 debería continuar principalmente como:

```text
pipeline determinístico
```

Y utilizar agentes únicamente donde agreguen valor comprobable:

```text
specialist
reviewer
auditor
coordinator
```

---

# 13. Hallazgo P1 — Team Lead + verificación

Accio incorporó un patrón donde un Team Lead asigna trabajo y verifica resultados.

Conceptualmente:

```text
Team Lead
→ asignación
→ agentes ejecutan
→ resultado
→ verificación
```

Esto es superior a un conjunto de agentes conversando libremente sin frontera operacional.

## Aplicación potencial a la Factoría

```text
TaskSpec
→ coordinator
→ builder / auditor / certifier
→ evidence
→ verification
→ PR
```

No debe implicar autonomía irrestricta.

---

# 14. Hallazgo P1 — Herramientas y conectores como frontera, no como negocio

Accio puede integrar capacidades como:

```text
file search
file read/write
terminal
web
browser automation
scheduled tasks
Gmail
Google Drive
Slack
Notion
MCP
```

La lección para PymIA es:

> MCP, conectores y tools son fronteras de ejecución, no arquitectura de negocio.

Servicio 1 debe conservar la lógica empresarial dentro de contratos y pipeline, sin delegarla a conectores.

---

# 15. Hallazgo P2 — Browser automation

Accio puede operar navegador real mediante automatización.

Esto puede resultar útil cuando una fuente empresarial carece de API o exportación adecuada.

Patrón futuro posible:

```text
sistema sin API
→ browser connector
→ read / extract
→ EvidenceRecord
```

## Decisión PymIA

No priorizar para Servicio 1.

Orden recomendado:

```text
1. archivos
2. APIs
3. exportaciones
4. browser automation
```

Browser automation debe considerarse conector de último recurso por fragilidad y costo operacional.

---

# 16. Hallazgo P0 — Permisos independientes de capacidad

Accio distingue autorización de disponibilidad de herramienta.

Patrones de permisos observados:

```text
auto-approve
ask every time
remember choice
always deny
```

Esto implica:

```text
tool availability
≠
tool authorization
```

## Aplicación PymIA

Preservar explícitamente:

```text
CAPABILITY_AVAILABLE
≠
EXECUTION_AUTHORIZED
≠
DELIVERY_AUTHORIZED
≠
BUSINESS_DECISION_AUTHORIZED
```

PymIA requiere incluso más cautela porque una conclusión incorrecta puede alterar decisiones empresariales.

---

# 17. Hallazgo P0 — Automatización no eleva privilegios

Las automatizaciones de Accio pueden ejecutarse de forma programada, pero no obtienen automáticamente permisos superiores.

Principio:

```text
schedule
≠
privilege escalation
```

Esto es directamente aplicable a RADAR.

## Patrón recomendado

```text
RADAR rule
↓
trigger
↓
control job
↓
read authorized evidence
↓
deterministic evaluation
↓
finding / exception
↓
human review cuando corresponda
```

Nunca:

```text
RADAR trigger
→ agente con libertad total
```

---

# 18. Hallazgo P1 — Artefactos con historia y provenance

Accio incorporó historial/versionado de artefactos.

Esto confirma que una plataforma agente seria necesita:

```text
artifact
+
history
+
provenance
```

## Aplicación PymIA

La cadena ideal debe permanecer trazable:

```text
InputEvidence
→ normalized evidence
→ computation
→ Finding
→ Review
→ Output / Workpaper
```

Cada etapa debe poder explicar su procedencia.

---

# 19. Diferencia genética entre Accio y PymIA

Accio optimiza:

```text
intent
→ agent
→ action
```

PymIA debe optimizar:

```text
business evidence
→ normalization
→ deterministic control
→ exception
→ evidence
→ human decision
```

Accio es principalmente un ejecutor de trabajo.

PymIA debe ser principalmente un sistema de control y explicación de desvíos.

---

# 20. Relación con SmartPyme Laboratorio

Accio confirma que existe valor comercial en transformar documentos empresariales dispersos en estructura, comparaciones y acciones.

Esto converge con la tesis de SmartPyme:

```text
recibir caos operativo
→ estructurarlo
→ pedir evidencia
→ ejecutar análisis
→ devolver hallazgo
```

La diferenciación PymIA debe estar en:

```text
contrato semántico
+
control determinístico
+
trazabilidad
+
tenant memory
+
evidence requirements
+
human review
```

No en competir como workspace generalista.

---

# 21. Qué conviene absorber

## P0

1. **Capability-scoped agents**.
2. **Tool availability separada de authorization**.
3. **Reviewer físicamente read-only**.
4. **Workspace/scope explícito por ejecutor**.
5. **Skill identity + versioning**.
6. **ExecutionTrace → LearningCandidate gobernado**.
7. **Automations sin elevación de privilegios**.

## P1

8. Separación Agent Memory / Knowledge Base.
9. Team Lead + verification para Factoría.
10. Artefactos con historial y provenance.

## P2

11. Browser automation como conector de último recurso.
12. Teams/subagents sólo donde exista ventaja comprobable.

---

# 22. Qué NO conviene copiar

No adoptar como prioridad:

```text
agent workspace horizontal universal
SOUL autoevolutiva como autoridad
agentes generalistas en toda la arquitectura
marketplace prematuro de Skills
Teams como solución universal
browser automation como base
CRM
social media execution
store builder
sourcing universal
task manager generalista
```

Eso expandiría PymIA hasta convertirlo en una plataforma horizontal antes de cerrar una vertical vendible.

---

# 23. Arquitectura PymIA compatible con los hallazgos

```text
                  PYMIA
                    │
              Tenant Context
                    │
             ReceptionRecord
                    │
                 Evidence
                    │
            Semantic Contract
                    │
          Product Pipeline S1
                    │
        Deterministic Controls
                    │
          ┌─────────┴─────────┐
          │                   │
       Finding            Exception
                              │
                        Human Review
                              │
                           Output
                              │
                      Execution Trace
                              │
                      LearningCandidate
                              │
                          Approval
                              │
                  Domain / Skill Evolution
```

Capas periféricas:

```text
Connectors
Workspaces
Permissions
Skills
RADAR
```

---

# 24. Comparación sintética

| Dimensión | Accio Work | PymIA |
|---|---|---|
| Producto | AI work platform | capa de control operacional |
| Core | agentes | pipeline determinístico |
| Entrada | intención / tarea | evidencia empresarial |
| Salida | acción / artefacto | hallazgo / excepción / evidencia |
| Memoria | agent-centric | tenant-centric + governed learning |
| Automatización | ejecución | monitoreo / control |
| Multiagente | central | opcional |
| Skills | extensiones del agente | capacidades gobernadas |
| HITL | autorización | autorización + juicio empresarial |
| Riesgo principal | acción indebida | conclusión empresarial incorrecta |
| Diferenciación | ejecutar trabajo | detectar qué no cierra y demostrarlo |

---

# 25. Decisiones propuestas

## Decisión 1

Mantener **Servicio 1 determinístico** como raíz productiva.

No introducir agentes en runtime simplemente porque Accio los utilice ampliamente.

## Decisión 2

Incorporar al ADN de Factoría el principio:

```text
role
→ capability set
→ workspace scope
→ policy
→ evidence
```

## Decisión 3

Diseñar más adelante un contrato formal:

```text
ExecutionTrace
→ LearningCandidate
```

sin promoción automática a memoria o Skill.

## Decisión 4

Preservar la separación:

```text
TenantMemory
LearningMemory
DomainKnowledge
ArchitecturalDNA
```

## Decisión 5

RADAR nunca debe otorgar por sí mismo privilegios nuevos.

## Decisión 6

Tratar browser automation como integración secundaria, no como fundamento de Servicio 1.

---

# 26. Conclusión

Accio Work constituye una validación externa significativa de varios principios que PymIA ya venía formulando:

```text
identidad persistente
capacidades acotadas
skills versionables
memoria separada
workspace explícito
permisos HITL
coordinación multiagente gobernada
aprendizaje desde ejecución
```

La lección central no es construir otro Accio.

La ventaja potencial de PymIA está precisamente en ser más estrecho y más verificable:

```text
datos del ERP / Excel / banco
→ control cruzado
→ diferencia / desviación
→ excepción
→ evidencia
→ decisión humana
```

El hallazgo más estratégico para evolución futura es:

```text
ExecutionTrace
→ governed LearningCandidate
→ Skill / DomainPattern / EvidenceRule
```

Esto permite que los pilotos y ejecuciones reales alimenten la evolución del sistema sin convertir la memoria en contexto acumulativo no gobernado.

---

# 27. Fuentes Accio revisadas

Fuentes oficiales utilizadas durante el análisis:

- `https://es.accio.com/work/doc?slug=help-about`
- `https://es.accio.com/work/doc?slug=quickstart`
- `https://es.accio.com/work/doc?slug=create-agent-guide`
- `https://www.accio.com/work/doc?slug=agent-tools-guide`
- `https://www1.accio.com/work/doc?slug=agent-collaboration-overview`
- `https://es.accio.com/work/doc?slug=automations-guide`
- `https://es.accio.com/work/doc?slug=changelog`
- `https://www.accio.com/work/`

---

**Regla de lectura:** los patrones de Accio son evidencia externa de soluciones convergentes, no prueba de que PymIA deba adoptar sus decisiones de producto o implementación.