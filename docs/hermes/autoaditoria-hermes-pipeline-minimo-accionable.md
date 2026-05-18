# Autoauditoría Hermes — Pipeline mínimo accionable

## Estado

Documento de continuidad operativa.

Este documento consolida lo emergente de la autoauditoría de Hermes sobre su integración con PymIA y su tendencia a saltear el pipeline.

No es una autorización para implementar arquitectura completa.
No es una habilitación para contaminar el core clínico de PymIA.
Es una poda técnica: qué hallazgos son accionables, qué debe quedar afuera y cuál es el mínimo viable para dejar de operar informalmente.

---

## Contexto

Hermes está siendo interrogado con una batería de prompts para detectar:

- por qué no respeta el pipeline;
- qué contratos faltan;
- qué límites no están enforced;
- cómo debería comportarse como conducto;
- qué evidencia técnica se requiere para auditar ejecuciones;
- qué partes son diseño útil y qué partes son sobrediseño.

La lectura correcta de sus respuestas no es “implementar todo ya”.

La lectura correcta es:

```text
esto expone brechas reales del pipeline;
ahora hay que reducirlas a cambios mínimos, testeables y reversibles.
```

---

## Regla rectora vigente

```text
Hermes conversa.
PymIA computa.
```

Hermes no debe:

- abrir archivos de evidencia;
- parsear Excel, CSV, PDF o imágenes;
- calcular métricas clínicas;
- crear diagnósticos;
- modificar outputs del kernel;
- saltar contracts;
- ejecutar scripts propios de análisis;
- convertir su razonamiento en verdad operacional.

PymIA tampoco debe mezclar su core clínico con una factoría técnica de ejecución salvo que exista boundary explícito.

---

## Hallazgos concretos de la autoauditoría

Las respuestas de Hermes no son humo si se leen como backlog de brechas.

Brechas reales identificadas:

```text
1. main.py no tiene router CLI por flags.
2. No existe --register-evidence.
3. No existe --create-case.
4. No existe --execute.
5. No existe TaskEvidence / ExecutionEvidence técnico.
6. No existe CommandLogger mínimo.
7. No existe persistencia de evidencia técnica por ejecución.
8. No existe métrica por ejecución.
9. No existe detección anti-bypass.
10. No existe criterio contractual PASS / PARTIAL / BLOCKED para ejecuciones.
```

Estas brechas explican por qué Hermes tiende a improvisar:

```text
si no hay CLI permitido,
si no hay whitelist,
si no hay evidencia técnica,
si no hay status formal,
si no hay test anti-bypass,
Hermes termina usando capacidades generales en vez de pipeline.
```

---

## Separación obligatoria de evidencias

No mezclar:

```text
StructuredEvidence
```

con:

```text
ExecutionEvidence / TaskEvidence
```

### StructuredEvidence

Evidencia clínica/documental del caso PyME.

Ejemplos:

- tablas extraídas;
- columnas detectadas;
- variables operativas;
- metadata documental;
- evidencia del cliente.

### ExecutionEvidence / TaskEvidence

Evidencia técnica de una ejecución.

Ejemplos:

- comandos ejecutados;
- stdout/stderr;
- exit_code;
- tests;
- hashes;
- costo;
- duración;
- archivos tocados;
- estado PASS / PARTIAL / BLOCKED.

Regla:

```text
StructuredEvidence pertenece al dominio clínico-operativo.
ExecutionEvidence pertenece al dominio técnico-runtime.
```

Si se mezclan, se contamina el modelo mental del sistema.

---

## Qué es accionable ahora

MVP técnico mínimo recomendado:

```text
1. CLI router en conversa-engine/main.py con whitelist.
2. Comandos permitidos mínimos.
3. Separación explícita entre evidencia clínica y evidencia técnica.
4. ExecutionEvidence mínimo.
5. CommandLogger simple.
6. Status PASS / PARTIAL / BLOCKED.
7. Tests anti-bypass.
8. Documentación del boundary actualizada.
```

---

## CLI mínimo propuesto

El CLI no debe ser shell arbitrario.

Debe funcionar por whitelist:

```text
--register-evidence
--create-case
--execute
--status
```

Todo comando no permitido debe devolver:

```text
COMANDO_NO_PERMITIDO
```

Sin fallback inteligente.
Sin reinterpretar flags como texto libre.
Sin ejecutar scripts auxiliares.

---

## ExecutionEvidence mínimo

No implementar aún un sistema de auditoría completo.

Implementar solo un contrato mínimo:

```yaml
task_id:
run_id:
trace_id:
command:
exit_code:
stdout_hash:
stderr_hash:
execution_result: PASS | PARTIAL | BLOCKED
blocked_reason:
created_at:
duration_seconds:
```

Opcional en primera fase:

```yaml
model_used:
input_hash:
output_hash:
tests_executed:
files_touched:
cost:
```

Regla:

```text
La evidencia técnica registra qué pasó.
No autoriza nada.
No diagnostica nada.
No aprueba nada.
```

---

## PASS / PARTIAL / BLOCKED

Criterio mínimo:

```text
PASS
La ejecución terminó correctamente, produjo salida válida y no declaró bloqueo.

PARTIAL
La ejecución produjo salida útil pero hay evidencia faltante o resultado incompleto.

BLOCKED
La ejecución no puede avanzar por falta de evidencia, error de contrato, comando prohibido, formato no soportado o falla interna.
```

Regla:

```text
Hermes no decide el estado.
Hermes transmite el estado emitido por PymIA/runtime.
```

---

## Tests anti-bypass mínimos

Casos obligatorios:

```text
1. Flag desconocido no se interpreta como texto.
2. --register-evidence sin file devuelve BLOCKED o error de validación.
3. --create-case sin message devuelve BLOCKED o error de validación.
4. --execute sin case_id/run_id devuelve BLOCKED o error de validación.
5. Hermes no abre archivos adjuntos.
6. Hermes no parsea XLSX/CSV/PDF.
7. Hermes no calcula diagnóstico propio.
8. Output crudo de PymIA no se reescribe.
9. status != REGISTERED detiene el ciclo.
10. NO_SIGNAL / ERROR / EMPTY_EVIDENCE se devuelve verbatim.
```

---

## Qué NO implementar ahora

Sobrediseño a evitar:

```text
FileTracker interceptando open()
CostEstimator perfecto
MetricsReporter completo
workflow engine
runner universal
TaskSpec grande
Prefect dentro del core
scheduler
memory compleja
autonomía de Hermes
```

Estas piezas pueden tener sentido en una factoría futura, pero no son necesarias para cerrar la brecha inicial de bypass.

---

## Prefect

No aparece como dependencia actual en PymIA y no debe introducirse en el core clínico.

Criterio:

```text
Prefect ahora: NO.
Prefect futuro: solo como orquestador externo, si existe boundary explícito.
```

---

## Pydantic

Pydantic sí es parte central del diseño.

Función:

```text
- contratos tipados;
- validación de entrada/salida;
- reducción de texto libre como interfaz operativa;
- separación entre Hermes, PymIA y runtime;
- enforcement temprano de campos obligatorios.
```

Pydantic fija bordes.
No diagnostica.
No orquesta.
No autoriza.

---

## Función correcta de los skills

Una skill no decide.

Una skill ejecuta una investigación bajo condiciones.

Cadena correcta:

```text
dolor del dueño
→ síntoma operativo
→ patologías posibles
→ hipótesis investigable
→ skill candidata
→ variables necesarias
→ evidencia requerida
→ pregunta mayéutica
→ evidencia recibida
→ caso investigable
→ diagnóstico con evidencia
```

Reglas:

```text
El dolor no es diagnóstico.
El síntoma no es patología confirmada.
La hipótesis no afirma: investiga.
La skill no decide: ejecuta bajo condiciones.
Sin evidencia trazable, no hay diagnóstico confirmado.
```

---

## Decisión operativa

La autoauditoría de Hermes sí aporta valor, pero debe podarse.

Veredicto:

```text
No es humo.
No se implementa todo.
Se convierte en backlog mínimo anti-bypass.
```

Backlog recomendado:

```text
1. Documentar boundary vigente.
2. Crear CLI whitelist mínimo.
3. Impedir que flags desconocidos entren como texto libre.
4. Separar StructuredEvidence de ExecutionEvidence.
5. Agregar ExecutionEvidence mínimo.
6. Agregar tests anti-bypass.
7. Validar con pytest.
```

---

## Política verbatim vs resumen

La autoauditoría también identificó una forma silenciosa de bypass:

```text
Hermes resume, corrige o reinterpreta una salida que debería transmitir cruda.
```

Eso rompe trazabilidad aunque no ejecute scripts.

### Verbatim obligatorio

Debe devolverse sin modificar:

```text
- stdout de --execute emitido por PymIA;
- stderr de cualquier comando CLI;
- tracebacks completos;
- exit_code;
- blocked_reason;
- input_hash y output_hash;
- repreguntas mayéuticas del kernel;
- TaskEvidence / ExecutionEvidence cuando exista;
- comandos ejecutados con stdout/stderr;
- tests individuales y resultados;
- archivos tocados con hashes.
```

Regla:

```text
El output crudo es fuente de verdad.
El resumen nunca reemplaza la evidencia.
```

### Resumen permitido

El resumen solo puede existir como capa auxiliar cuando:

```text
- el usuario lo pide explícitamente;
- el output es demasiado extenso;
- hay varias ejecuciones en un mismo turno.
```

Condiciones:

```text
- el resumen va antes del verbatim;
- el verbatim completo debe seguir disponible;
- el resumen no puede contradecir la salida cruda;
- si hay contradicción, se elimina el resumen y gana el verbatim.
```

### Prohibiciones

Hermes no debe:

```text
- resumir tracebacks;
- reformular blocked_reason;
- cambiar una repregunta mayéutica;
- convertir stderr en explicación propia;
- convertir VEREDICTO / CADENA_CAUSAL / HIPÓTESIS en paráfrasis;
- agregar cierres conversacionales después de la trazabilidad.
```

Formato final deseado:

```text
[resumen opcional]
[verbatim]
---
task_id:
run_id:
trace_id:
evidence_id:
pipeline:
input_hash:
output_hash:
execution_result:
duration:
cost:
```

La trazabilidad es el último bloque. No se agrega comentario posterior.

---

## Frase rectora

```text
Hermes no necesita ser más inteligente.
Necesita tener menos caminos para saltearse el pipeline.
```
