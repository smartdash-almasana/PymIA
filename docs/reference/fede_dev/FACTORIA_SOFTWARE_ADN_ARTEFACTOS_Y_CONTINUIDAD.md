# Factoría SmartPyme — ADN de Software, Artefactos y Continuidad Operativa

Fecha: 2026-05-06  
Proyecto: SmartPyme Factory / factory_v2  
Estado: Documento de continuidad conceptual y operativa

---

## 1. Pregunta central

La pregunta de fondo no es solamente si la Factoría puede generar código.

La pregunta real es:

```text
¿Cómo sabe la Factoría en qué dirección fabricar,
qué pieza fabricar,
qué conectar con qué,
y bajo qué límites hacerlo?
```

La respuesta no está en un modelo más potente ni en un agente autónomo más grande.

La respuesta está en una arquitectura guiada por artefactos, contratos, políticas, evidencia y aprobación humana.

---

## 2. Lectura general del proyecto Factoría

La Factoría no debe entenderse como un chatbot que programa.

Debe entenderse como una línea industrial de fabricación de software.

El patrón correcto es:

```text
TaskSpec
-> contratos
-> policies
-> sandbox
-> evidencia
-> review
-> GitHub / PR
```

La Factoría no reemplaza al arquitecto.

Amplifica al arquitecto.

El arquitecto expresa el plano del software en artefactos que la Factoría pueda interpretar, validar y ejecutar.

---

## 3. Riesgo que se está reduciendo

Antes, el flujo tendía a ser:

```text
ChatGPT + Hermes + usuario
-> prompts grandes
-> decisiones dispersas
-> cambios sin frontera
-> deriva acumulativa invisible
```

Riesgos principales:

- decisiones no fijadas;
- prompts que cambian sin trazabilidad;
- agentes que se contradicen;
- runtime, orquestación y HITL mezclados;
- cambios sin evidencia;
- deuda arquitectónica silenciosa;
- repositorio expuesto a modificaciones improvisadas.

Con `factory_v2`, el flujo empieza a ser:

```text
microciclos
+ contratos
+ sandbox
+ policies
+ evidencia
+ GitHub
+ PRs
+ aprobación humana
```

Eso no garantiza éxito, pero reduce fuertemente el caos estructural.

---

## 4. Runtime, orquestación y ejecución

### Orquestación

La orquestación decide:

```text
qué paso sigue,
en qué orden,
con qué estado,
con qué reglas,
y qué hacer si algo falla.
```

Ejemplos en la Factoría:

- LangGraph;
- Prefect;
- Hermes como gateway/HITL parcial.

Ejemplo de orquestación:

```text
audit -> implement -> sandbox -> review
```

### Runtime

El runtime ejecuta trabajo real.

Ejemplos:

- Python;
- Docker;
- Vertex;
- Gemini;
- Qwen;
- Kimi;
- pytest;
- procesos shell;
- contenedores.

Ejemplos de runtime:

```text
ejecutar pytest
correr código
llamar Gemini
crear un archivo
levantar Docker
```

### Ejecución

La ejecución es el acto concreto:

```text
correr una tarea determinada en un runtime determinado.
```

Analogía:

| Capa | Analogía |
|---|---|
| Orquestación | cerebro / jefe de planta |
| Runtime | máquinas / manos |
| Ejecución | acción concreta de una máquina |

---

## 5. Herramientas y responsabilidades

| Herramienta | Rol en la Factoría |
|---|---|
| LangGraph | Coordina flujo y estado. Orquestador stateful. |
| Docker | Runtime aislado para ejecutar código generado. |
| Pydantic | Contratos, validación y serialización. |
| Pydantic AI | Agentes tipados con tools y salidas estructuradas. |
| Hermes | Gateway humano, HITL, autorización y safe mode. |
| Vertex AI | Runtime inteligente gestionado para modelos. |
| Gemini Vertex | Lectura, auditoría y documentación. |
| Qwen3 Coder Vertex MaaS | Builder puntual de código si no hay 429. |
| Kimi K2 Thinking Vertex MaaS | Auditor puntual de razonamiento. |
| Prefect | Orquestación durable futura: retries, scheduling, resiliencia. |
| GitHub | Fuente de verdad del código y frontera de integración. |

Regla central:

```text
No mezclar responsabilidades.
```

---

## 6. Agente tipado

Un agente tipado es un agente que no trabaja solo con texto libre.

Trabaja con entradas y salidas estructuradas.

En vez de:

```text
“hacé algo y devolveme texto”
```

trabaja así:

```text
entrada = esquema válido
salida = esquema válido
```

Ejemplo conceptual:

```python
class TaskSpec(BaseModel):
    task_id: str
    objective: str

class ReviewResult(BaseModel):
    approved: bool
    reasons: list[str]
```

El agente:

- recibe datos validados;
- devuelve datos validados;
- no inventa formatos;
- reduce outputs incompatibles;
- trabaja dentro de contratos.

La IA sigue siendo probabilística, pero los bordes del sistema se vuelven más determinísticos.

---

## 7. Pull Request / PR

PR significa:

```text
Pull Request
```

Es el mecanismo de GitHub para proponer cambios sin meterlos directamente al repositorio principal.

Flujo típico:

```text
1. Crear rama
2. Hacer cambios
3. Push
4. Abrir PR
5. Revisar
6. Aprobar o rechazar
7. Merge
```

En la Factoría, el PR funciona como frontera de seguridad.

Flujo ideal:

```text
IA
-> branch
-> PR draft
-> review humano
-> merge
```

La IA puede preparar cambios, tests, evidencia y diffs.

Pero no debería mergear automáticamente al core.

---

## 8. El costo de la fábrica frente al producto

Riesgo real:

```text
la fábrica cuesta más que lo que fabrica
```

Ese riesgo aparece cuando la Factoría intenta fabricar todo desde el primer día.

Ejemplos de sobrediseño:

- scheduler propio;
- memory universal;
- agentes omniscientes;
- autonomy engine prematuro;
- observabilidad sobredimensionada;
- demasiados frameworks;
- cambios de arquitectura continuos.

La respuesta económica correcta es que la Factoría empiece fabricando piezas repetitivas y de bajo riesgo:

```text
tests
contratos
adapters
DTOs
policies
validadores
migraciones pequeñas
conectores
scaffolds
documentación técnica
PR drafts
```

Si reduce fricción en esas tareas, aunque sea un 10%-20%, empieza a tener sentido económico.

---

## 9. Qué es un artefacto

Un artefacto es cualquier objeto estructurado que transmite información útil al sistema o al equipo.

No es solo código.

Puede ser:

- documento;
- contrato;
- test;
- diagrama;
- TaskSpec;
- PR;
- JSON;
- evidencia;
- schema;
- config;
- log;
- blueprint.

En la Factoría, un artefacto es algo que:

```text
define,
restringe,
describe,
o valida comportamiento.
```

### Elementos de un artefacto

| Elemento | Descripción | Ejemplo |
|---|---|---|
| Identidad | Qué es | `TaskSpecV2`, `DockerSandboxAdapter` |
| Estructura | Cómo está organizado | campos Pydantic |
| Semántica | Qué significa | `files_allowed` = zonas permitidas |
| Reglas | Qué permite o prohíbe | `AUDIT_ONLY`, `fail-closed` |
| Evidencia | Cómo se demuestra que vale | tests, PASS, `run.json` |

Los artefactos reemplazan memoria informal humana por objetos explícitos y auditables.

---

## 10. Relación con Spec-Driven Development

Spec-Driven Development es una metodología.

La idea es:

```text
primero definir especificaciones,
después implementar.
```

La spec gobierna el desarrollo.

Un artefacto es el objeto concreto que materializa esa especificación.

Relación:

```text
la spec es la estrategia;
los artefactos son las piezas concretas.
```

En la Factoría, el movimiento natural es hacia una:

```text
Spec-Driven Factory
```

Antes:

```text
prompt-driven improvisation
```

Ahora:

```text
spec-driven industrial workflow
```

---

## 11. De dónde surge el TaskSpec

El `TaskSpec` no debería surgir de un prompt improvisado.

Surge de capas superiores.

Cadena correcta:

```text
visión
-> blueprint
-> arquitectura
-> dominio
-> capacidades
-> workflows
-> TaskSpecs
-> código
```

El `TaskSpec` es una expresión local de un ADN arquitectónico superior.

Ejemplo:

Blueprint:

```text
Docker nunca debe ser default global.
```

TaskSpec derivado:

```text
Crear docker_runner explícito sin modificar graph.py.
```

Si el TaskSpec nace desde prompts improvisados, produce deriva.

Si nace desde arquitectura explícita, produce coherencia acumulativa.

---

## 12. ADN arquitectónico del software

No existe necesariamente un archivo mágico único.

El “código genético” del software es un conjunto de artefactos fundacionales:

- blueprints;
- principios rectores;
- taxonomías;
- contratos;
- reglas operativas;
- catálogos;
- arquitectura;
- restricciones;
- lenguaje de dominio;
- estados válidos;
- modos permitidos.

Esto actúa como:

```text
ADN arquitectónico
```

Los TaskSpecs son expresiones locales de ese ADN.

---

## 13. Artefactos superiores al TaskSpec

La Factoría necesita artefactos de nivel superior al TaskSpec.

Estos artefactos definen dirección, límites, capacidades, conexiones y decisiones.

| Artefacto | Qué es | Qué define | Relación |
|---|---|---|---|
| `DomainBlueprint` | Plano maestro del dominio | visión, límites, lenguaje, arquitectura conceptual, principios rectores | Capa más alta. Origina capacidades, políticas y contratos. |
| `CapabilitySpec` | Definición de una capacidad del sistema | qué sabe hacer el sistema y bajo qué condiciones | Surge del DomainBlueprint. Genera workflows y TaskSpecs. |
| `SystemPolicy` | Reglas globales del sistema | restricciones, seguridad, compliance, límites operativos | Cruza todas las capas. Afecta módulos, runtimes, TaskSpecs y PRs. |
| `IntegrationMap` | Mapa de conexiones del sistema | qué componente habla con cuál, protocolos, flujos y dependencias | Usa módulos, contratos y capacidades. Reduce acoplamiento caótico. |
| `ArchitecturalDecisionRecord` / `ADR` | Registro formal de decisiones arquitectónicas | por qué se eligió algo y qué alternativas se descartaron | Congela decisiones para evitar rediscutir arquitectura continuamente. |
| `ModuleContract` | Contrato explícito de un módulo | inputs, outputs, errores, side effects y responsabilidades | Permite ensamblar módulos sin ambigüedad. Base de integración y testing. |

Relación jerárquica simplificada:

```text
DomainBlueprint
    ↓
CapabilitySpec
    ↓
IntegrationMap
    ↓
ModuleContract
    ↓
TaskSpec
    ↓
Código
```

Transversales:

```text
SystemPolicy
ADR
```

Estos influyen sobre todas las capas.

---

## 14. Ejemplo de cadena completa

### DomainBlueprint

Define:

```text
La IA no mergea directo al core.
```

### SystemPolicy

Impone:

```text
Todo código generado pasa por sandbox.
```

### CapabilitySpec

Describe:

```text
Generar PR drafts auditables.
```

### IntegrationMap

Define:

```text
LangGraph -> Docker -> GitHub
Hermes -> HITL
```

### ModuleContract

Especifica:

```python
run_with_docker(TaskSpecV2) -> GraphState
```

### ADR

Registra:

```text
Docker no será runtime global por default.
```

### TaskSpec

Pide:

```text
Agregar docker_runner explícito.
```

### Código

Implementa:

```text
factory_v2/docker_runner.py
```

---

## 15. Estado operativo del chat anterior / factory_v2

Estado al cierre del ciclo anterior:

```text
factory_v2: estable
tests base: PASS
repo: limpio
docker_runner: validado
langgraph_runner: creado/documentado
validación completa LangGraph: pendiente en entorno estable
bloqueo operativo: OpenRouter key limit en Hermes
```

Bloqueo Hermes:

```text
HTTP 403: Key limit exceeded
OpenRouter total key limit exceeded
```

Decisión:

```text
No gastar más reintentos por OpenRouter.
No usar Hermes vía OpenRouter para este ciclo.
Reconfigurar Hermes a Vertex/Gemini o Qwen MaaS antes de usarlo como ejecutor.
```

---

## 16. Hitos técnicos ya cerrados

### Docker y policies

```text
DockerSandboxAdapter ejecuta código permitido en Docker real.
CodePolicyV2 bloquea import os antes de Docker.
CommandPolicyV2 se mantiene sobre el wrapper Docker.
```

### run_graph + DockerSandboxAdapter

```text
run_graph(..., sandbox_adapter=DockerSandboxAdapter()) termina PASS.
Evidencia por nodo y run.json confirmados.
```

### run_with_docker

```text
run_with_docker(TaskSpecV2(...)) termina PASS.
run.json confirma audit/implement/sandbox/review PASS.
```

### LangGraph aislado

```text
.venv-langgraph
langgraph==1.1.10
StateGraph mínimo audit -> review -> END
Salida: {'message': 'LANGGRAPH_SMOKE -> audit -> review'}
```

### LangGraph integrado mínimo

```text
factory_v2/langgraph_runner.py creado.
tests/factory_v2/test_langgraph_runner.py creado.
Test salta correctamente si falta langgraph.
Validación completa con langgraph instalado queda pendiente en entorno estable.
```

---

## 17. Estado actual de componentes

| Componente | Archivo | Estado |
|---|---|---|
| Contratos | `factory_v2/contracts.py` | VALIDADO |
| Evidencia | `factory_v2/evidence.py` | VALIDADO |
| Grafo determinístico | `factory_v2/graph.py` | VALIDADO |
| Sandbox fake | `factory_v2/sandbox.py` | VALIDADO |
| DockerSandboxAdapter | `factory_v2/sandbox.py` | VALIDADO |
| CommandPolicyV2 | `factory_v2/policy.py` | VALIDADO |
| CodePolicyV2 | `factory_v2/code_policy.py` | VALIDADO |
| Docker runner | `factory_v2/docker_runner.py` | VALIDADO |
| LangGraph runner | `factory_v2/langgraph_runner.py` | CREADO / VALIDACIÓN COMPLETA PENDIENTE |
| Tooling guide | `docs/factory/FACTORY_V2_TOOLING_CONFIG_GUIDE.md` | VALIDADO COMO GUÍA INICIAL |

---

## 18. Próximos pasos recomendados

### 1. Reconfigurar Hermes fuera de OpenRouter

Objetivo:

```text
Evitar bloqueos por límite de key en OpenRouter.
Usar Vertex/Gemini o Qwen MaaS como provider operativo.
```

### 2. Validar LangGraph runner en entorno estable

Objetivo:

```text
Ejecutar tests/factory_v2/test_langgraph_runner.py con langgraph instalado en sesión estable de PC o CI/dev.
```

Condiciones:

```text
No usar SSH móvil si corta la sesión.
No dejar .venv temporal en repo.
```

### 3. Diseñar Hermes HITL mínimo

Objetivo:

```text
Definir cómo Hermes aprueba/deniega una tarea antes de escalar autonomía.
```

### 4. Definir GitHub PR plan

Objetivo:

```text
Crear branch/diff/PR draft sin merge automático.
```

---

## 19. Frase rectora

```text
Factory_v2 avanza por ciclos cortos,
contratos explícitos,
evidencia,
políticas mínimas,
sandbox real validado,
GitHub como verdad,
PRs como frontera,
y aprobación humana antes de integración.
```

---

## 20. Idea final

La Factoría no necesita ser una AGI.

Necesita fabricar piezas pequeñas, auditables, reversibles y conectables.

La clave no es que el modelo “sepa todo”.

La clave es que el arquitecto pueda expresar bien el plano del software en artefactos que la Factoría pueda leer, validar y ejecutar.

Con buen plano:

```text
la Factoría se vuelve línea de producción.
```

Sin buen plano:

```text
la Factoría deriva.
```
