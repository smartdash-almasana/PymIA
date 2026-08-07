# Diseño — Memoria de Factoría, Learning Memory y ADN Arquitectónico

## Estado

Documento conceptual de diseño.

Este documento consolida las últimas definiciones del hilo sobre la **capa de diseño de memoria de la factoría multiagente SmartPyme**.

No es implementación.

No describe un agente autónomo mágico.

Describe una arquitectura de memoria operacional, aprendizaje gobernado y preservación del sentido arquitectónico para una factoría industrial de software asistida por IA.

---

# 1. Tesis central

La factoría no necesita, al inicio, una memoria compleja para funcionar.

Pero sí necesita un diseño claro de memoria para no degradarse cuando escale.

La diferencia es crítica:

```text
Para arrancar:
TaskSpec + Evidence + contratos + sandbox + PR.

Para escalar:
LearningMemory + SkillVersioning + ArchitecturalDNA.
```

---

# 2. Problema real

El problema principal de la factoría no es generar código.

El problema real es mantener coherencia arquitectónica acumulativa a través de muchos microciclos.

La IA puede fabricar piezas.

Pero la factoría necesita preservar:

```text
- sentido arquitectónico;
- contratos;
- restricciones;
- evidencia;
- trazabilidad;
- patrones efectivos;
- errores recurrentes;
- políticas;
- límites de ejecución;
- decisiones estructurales;
- costos;
- calidad de PRs;
- estabilidad de skills.
```

Sin eso, el sistema termina derivando.

---

# 3. Por qué no alcanza con “un modelo robot”

Un modelo robot puede operar como ejecutor inteligente.

Pero no debe ser la memoria institucional de la factoría.

Un modelo aislado:

```text
- recuerda poco;
- mezcla contexto;
- no versiona aprendizajes;
- no prueba por qué decidió;
- no distingue evidencia de opinión;
- no preserva contratos de forma estable;
- no mantiene trazabilidad suficiente;
- deriva con prompts largos;
- no separa ejecución, evidencia, aprendizaje y arquitectura.
```

Por eso el modelo debe ser tratado como:

```text
operario inteligente bajo contrato,
no como memoria soberana.
```

---

# 4. Diferencia esencial

## Evidence

Evidence responde:

```text
qué pasó.
```

Es el registro puntual de una ejecución.

Ejemplos:

```text
- task_id;
- skill_id;
- modelo usado;
- archivos tocados;
- tests ejecutados;
- resultado PASS / PARTIAL / BLOCKED;
- costo;
- tiempo;
- logs relevantes;
- PR generado;
- errores detectados.
```

## LearningMemory

LearningMemory responde:

```text
qué aprendimos.
```

No registra cualquier cosa.

Consolida aprendizajes derivados de evidencias, bajo revisión y gobierno.

Ejemplos:

```text
- este tipo de TaskSpec reduce errores;
- esta skill falla cuando falta evidencia X;
- este modelo es más eficiente para auditoría que para refactor;
- este patrón de PR produce menos regresiones;
- esta secuencia de sandbox evita roturas;
- este anti-patrón debe quedar prohibido.
```

---

# 5. Regla central de memoria

```text
Nada entra a LearningMemory automáticamente.
```

Flujo correcto:

```text
Evidence
→ evaluación
→ candidato a aprendizaje
→ revisión / política
→ aprobación
→ LearningMemory
→ mejora futura de TaskSpec, SkillSpec o políticas.
```

Esto evita que la memoria se transforme en ruido acumulativo.

---

# 6. Capas de memoria

La memoria de factoría debe separarse en capas.

---

## 6.1 Memoria episódica

Guarda ejecuciones puntuales.

```text
Una tarea.
Un resultado.
Un conjunto de evidencias.
```

Sirve para auditoría y trazabilidad.

No define políticas.

---

## 6.2 Memoria procedural

Guarda procedimientos que funcionaron.

Ejemplos:

```text
- secuencia efectiva de debugging;
- patrón de refactor seguro;
- forma estable de escribir TaskSpecs;
- estrategia de pruebas antes de PR;
- validación previa de rama y worktree.
```

Sirve para mejorar operación.

---

## 6.3 Memoria arquitectónica

Guarda decisiones estructurales persistentes.

Ejemplos:

```text
- sandbox obligatorio;
- fail-closed;
- contracts first;
- PR antes de merge;
- no autonomía total;
- no semántica PyME hardcodeada en core;
- MCP como frontera segura;
- Hermes como HITL;
- Pydantic como contrato;
- Docker como aislamiento;
- GitHub como fuente de verdad.
```

Esta capa forma parte del ADN arquitectónico.

---

## 6.4 Memoria estadística

Guarda señales agregadas.

Ejemplos:

```text
- tasa PASS por skill;
- costo promedio por tipo de tarea;
- modelo más efectivo por familia de trabajo;
- errores recurrentes;
- PRs revertidos;
- duración media por microciclo;
- frecuencia de BLOCKED por falta de evidencia.
```

Sirve para optimizar, no para decidir sola.

---

# 7. ArchitecturalDNA

El ADN arquitectónico es la memoria estable de identidad de la factoría.

No guarda tareas sueltas.

Guarda:

```text
- principios rectores;
- límites no negociables;
- patrones aprobados;
- patrones prohibidos;
- contratos base;
- políticas de seguridad;
- reglas de autorización;
- reglas de evidencia;
- criterios de diseño.
```

---

# 8. ArchitecturalDNA vs LearningMemory

## ArchitecturalDNA

```text
estable,
estructural,
lento de cambiar,
protege identidad.
```

## LearningMemory

```text
operacional,
adaptativa,
evolutiva,
sugiere mejoras.
```

Regla:

```text
LearningMemory puede sugerir.
ArchitecturalDNA define los límites.
```

---

# 9. Contrato conceptual de LearningMemoryRecord

```yaml
learning_id:
source_evidence_ids:
task_type:
skill_id:
skill_version:
model_used:
execution_result: PASS | PARTIAL | BLOCKED
root_cause:
reusable_pattern:
anti_pattern:
recommended_taskspec_delta:
recommended_skill_delta:
recommended_policy_delta:
cost_signal:
time_signal:
confidence_score:
human_approved:
approved_by:
created_at:
status: CANDIDATE | APPROVED | REJECTED | DEPRECATED | ARCHIVED
```

---

# 10. Contrato conceptual de EvidenceRecord

```yaml
evidence_id:
task_id:
skill_id:
skill_version:
model_used:
input_hash:
output_hash:
files_touched:
tests_executed:
test_result:
execution_result:
cost:
duration:
logs:
pr_id:
created_at:
```

---

# 11. Contrato conceptual de SkillVersion

```yaml
skill_id:
version:
purpose:
contract_hash:
allowed_tools:
required_inputs:
expected_outputs:
required_evidence:
policies:
known_limitations:
known_patterns:
known_anti_patterns:
recommended_models:
deprecated_models:
success_rate:
failure_modes:
```

---

# 12. Por qué versionar skills

Una skill no es una herramienta libre.

Una skill es una capacidad operacional contratada.

Si cambian sus inputs, outputs, herramientas, políticas, evidencias o límites, cambia la versión.

La factoría necesita saber:

```text
qué skill funcionó,
con qué contrato,
en qué versión,
con qué modelo,
sobre qué tipo de tarea,
y con qué resultado.
```

Sin versionado, la memoria se vuelve ambigua.

---

# 13. LearningMemory no ejecuta

La memoria no debe:

```text
- ejecutar sola;
- cambiar contratos sola;
- modificar skills sola;
- elegir providers sola;
- reescribir arquitectura sola;
- convertir un patrón en política sin aprobación;
- autopromocionarse.
```

La memoria:

```text
observa,
consolida,
sugiere.
```

---

# 14. Relación con TaskSpec

LearningMemory puede sugerir mejoras a TaskSpec.

Ejemplo:

```text
Las tareas de refactor delicado tienen menor tasa de regresión cuando el TaskSpec incluye:
- archivos permitidos;
- archivos solo lectura;
- archivos prohibidos;
- comandos de verificación;
- salida obligatoria;
- criterio PASS/PARTIAL/BLOCKED.
```

Eso no significa que la memoria cree tareas sin control.

Significa que alimenta mejores plantillas.

---

# 15. Relación con modelos

La memoria puede registrar efectividad de modelos.

Ejemplos:

```text
- modelo más barato para auditoría textual;
- modelo más estable para refactor;
- modelo que falla en JSON largo;
- modelo que produce más sobreingeniería;
- modelo más adecuado para lectura larga.
```

Pero la selección de modelo debe seguir políticas explícitas.

La memoria no cambia providers automáticamente.

---

# 16. Relación con costos

La factoría debe medir costo operacional.

LearningMemory puede registrar:

```text
- costo promedio por tipo de tarea;
- costo por PASS;
- costo por PR aceptado;
- costo por fallo;
- costo de modelos sobredimensionados;
- tareas que conviene mandar a modelo barato;
- tareas que justifican modelo más fuerte.
```

Esto permite mantener una factoría low-cost sin degradar calidad.

---

# 17. Relación con PRs

La memoria debe aprender de PRs.

Ejemplos:

```text
- PRs pequeños tienen menor tasa de regresión;
- PRs que mezclan docs + runtime + tests tienden a fallar;
- PRs con TaskSpec atómico son más auditables;
- PRs sin sandbox previo son más riesgosos;
- PRs que tocan core sin contrato generan deriva.
```

---

# 18. Relación con fallos recurrentes

LearningMemory puede convertir fallos repetidos en anti-patrones.

Ejemplos:

```text
- tocar core sin TaskSpec explícito;
- mezclar runtime, orquestación, skills y memoria;
- diagnosticar sin evidencia;
- usar prompts gigantes permanentes;
- crear agentes mágicos autónomos;
- saltar sandbox;
- no verificar rama;
- no verificar worktree limpio;
- tocar legacy durante ciclo factory_v2.
```

---

# 19. Memoria saludable

Una memoria saludable:

```text
- reduce repetición;
- reduce errores;
- mejora TaskSpecs;
- mejora selección de modelos;
- preserva arquitectura;
- evita deriva;
- mejora trazabilidad;
- mantiene coherencia entre ciclos.
```

---

# 20. Memoria tóxica

Una memoria tóxica:

```text
- acumula todo;
- mezcla logs con decisiones;
- convierte conversaciones en políticas;
- contradice contratos;
- alimenta prompts infinitos;
- degrada precisión;
- contamina el core;
- aumenta deriva.
```

---

# 21. Separación obligatoria

La regla arquitectónica es:

```text
Execution
≠ Evidence
≠ Learning
≠ Architecture
```

Cada capa tiene función distinta.

Si se mezclan, aparece caos.

---

# 22. Relación con Domain Packs y Knowledge Tanks

Los Domain Packs y Knowledge Tanks contienen conocimiento de dominio.

Ejemplos:

```text
- síntomas;
- patologías;
- fórmulas;
- evidencias;
- preguntas mayéuticas;
- buenas prácticas;
- skills de dominio.
```

LearningMemory contiene aprendizajes operacionales de la factoría.

Ejemplo:

```text
KnowledgeTank:
cómo investigar pérdida de margen gastronómico.

LearningMemory:
qué workflow fue más efectivo para implementar esa investigación sin romper contratos.
```

No deben mezclarse.

---

# 23. Criterio práctico de implementación

La memoria no es estrictamente necesaria para el MVP.

Sí es necesaria para escalar.

## Fase 1 — MVP sin LearningMemory compleja

Implementar o preservar solo:

```text
- TaskSpec;
- EvidenceRecord;
- contratos Pydantic;
- sandbox;
- PR;
- salida PASS/PARTIAL/BLOCKED.
```

Objetivo:

```text
fabricar piezas útiles sin perder trazabilidad básica.
```

## Fase 2 — Memoria mínima

Agregar:

```text
- registro de fallos recurrentes;
- patrones exitosos;
- anti-patrones;
- métrica básica por skill/modelo;
- vínculo Evidence → LearningCandidate.
```

Objetivo:

```text
dejar de repetir errores.
```

## Fase 3 — LearningMemory gobernada

Agregar:

```text
- aprobación de aprendizajes;
- estados CANDIDATE / APPROVED / DEPRECATED;
- SkillVersioning completo;
- mejoras sugeridas a TaskSpec;
- métricas costo/efectividad;
- gobierno explícito del ArchitecturalDNA.
```

Objetivo:

```text
factoría evolutiva sin caos.
```

---

# 24. Conclusión operativa

Para el MVP:

```text
NO implementar memoria compleja todavía.
```

Pero sí dejar el diseño escrito.

Porque cuando existan muchas skills, modelos, PRs, errores recurrentes y dominios, la memoria será necesaria para mantener coherencia.

---

# 25. Frase rectora

```text
La factoría no necesita recordar todo.
Necesita consolidar lo que vale la pena preservar.
```

---

# 26. Cierre

La factoría multiagente no debe comportarse como una inteligencia amorfa que acumula contexto.

Debe comportarse como una organización industrial que:

```text
ejecuta,
mide,
audita,
aprende,
consolida,
preserva identidad,
y mejora incrementalmente.
```

La memoria correcta no es acumulación indiscriminada.

La memoria correcta es:

```text
aprendizaje operacional gobernado.
```
