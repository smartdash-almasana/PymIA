# Autoauditoría Hermes — Pipeline mínimo accionable

## Estado

Documento de continuidad operativa.

Este documento consolida lo emergente de la autoauditoría de Hermes sobre su integración con PymIA y su tendencia a saltear el pipeline.

No es una autorización para implementar arquitectura completa.
No es una habilitación para contaminar el core clínico de PymIA.
Es una poda técnica: qué hallazgos son accionables, qué debe quedar afuera y cuál es el mínimo confiable para dejar de operar informalmente.

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

prueba de frontera mínimo recomendado:

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

## Consolidado final de hallazgos honestos de Hermes

Este bloque preserva físicamente los hallazgos que no deben quedar flotando en chat.

### Hallazgo central

```text
Hermes no necesita más autonomía.
Necesita menos caminos para saltearse el pipeline.
```

### Problemas reales detectados

```text
- ausencia de boundaries fuertes;
- flags tratados como texto libre;
- reinterpretación narrativa de outputs;
- falta de fail-closed;
- ausencia de evidencia técnica mínima;
- ausencia de tests anti-bypass.
```

### Regla operacional vigente

```text
Hermes conversa.
PymIA computa.
```

Hermes no debe:

```text
- abrir evidencia del cliente;
- parsear XLSX/CSV/PDF;
- calcular métricas clínicas;
- ejecutar análisis paralelo;
- reescribir diagnósticos;
- reinterpretar stdout/stderr;
- transformar hipótesis en hallazgos.
```

### Política de verdad

```text
El verbatim es fuente de verdad.
```

Consecuencias:

```text
- stderr no se resume;
- tracebacks no se resumen;
- blocked_reason no se reescribe;
- VEREDICTO/CADENA_CAUSAL/HIPÓTESIS no se parafrasean;
- si resumen y verbatim contradicen, gana verbatim.
```

### núcleo robusto inicial anti-bypass aceptado

```text
1. CLI fail-closed.
2. Whitelist de flags.
3. Rechazo explícito de flags desconocidos.
4. PASS / PARTIAL / BLOCKED.
5. Tests anti-bypass mínimos.
6. Separación StructuredEvidence vs ExecutionEvidence.
7. Output verbatim + trazabilidad.
```

### Sobrediseño explícitamente diferido

```text
- Prefect;
- workflow engine;
- memoria compleja;
- runner universal;
- TaskSpec gigante;
- autonomía de Hermes;
- métricas autoaprobatorias;
- factoría completa dentro del core clínico.
```

### Separación de dominios

```text
StructuredEvidence = evidencia clínica/operacional.
ExecutionEvidence = evidencia técnica/runtime.
```

No mezclar ambos contratos.

### Próximo cambio técnico recomendado

```text
main.py:
- fail-closed para flags;
- flags desconocidos no entran como mensaje libre;
- comandos no implementados responden COMANDO_NO_IMPLEMENTADO.
```

No avanzar con arquitectura mayor hasta cerrar ese bypass básico.

---

## Material de ciclos posteriores: aceptado, diferido y rechazado

Durante los ciclos siguientes Hermes propuso tests anti-bypass, autoconfiguración de sesión, provider fallback, métricas y plan de migración por fases.

La decisión operativa es no tomar esas respuestas como implementación directa, sino clasificarlas.

### Aceptado como documentación y criterio de diseño

```text
- tests anti-bypass conceptuales;
- fail-closed como principio operativo;
- bootstrap de sesión como checklist externo;
- provider fallback como política futura;
- plan de migración por fases pequeñas;
- PR como frontera de cambio;
- HITL en todo cierre relevante;
- output verbatim como fuente de verdad;
- trazabilidad al final de cada respuesta operativa.
```

### Diferido para una capa técnica posterior

```text
- BypassDetector real;
- ExecutionEvidence completo;
- CommandLogger persistente;
- MetricsCollector;
- MetricsStore;
- MetricsReporter;
- SessionBootstrap en código;
- ProviderHealth;
- TaskEvidenceGenerator.
```

Estas piezas pueden existir en un runtime técnico o factoría futura, pero no deben introducirse como core clínico sin boundary explícito.

### Rechazado por ahora

```text
- TaskSpec obligatorio como contrato actual;
- workflow engine;
- Prefect dentro del core;
- FileTracker interceptando operaciones de bajo nivel;
- runner universal;
- memoria compleja;
- autonomía operativa de Hermes;
- métricas usadas para autoaprobar;
- cerrar PR/casos sin revisión externa.
```

---

## Plan de migración podado

La propuesta extensa de fases se reduce a una secuencia mínima y reversible.

### Fase 0 — Documentación y frontera

Objetivo:

```text
Dejar documentado el boundary real antes de tocar runtime.
```

Acciones:

```text
- consolidar esta autoauditoría;
- documentar verbatim vs resumen;
- documentar fail-closed;
- documentar separación StructuredEvidence / ExecutionEvidence;
- documentar qué queda fuera por sobrediseño.
```

Criterio de salida:

```text
Documento físico en repo y revisable por git.
```

### Fase 1 — CLI fail-closed mínimo

Objetivo:

```text
Evitar que flags desconocidos entren como mensaje libre.
```

Acciones:

```text
- agregar whitelist mínima en conversa-engine/main.py;
- rechazar flags desconocidos con COMANDO_NO_PERMITIDO;
- devolver COMANDO_NO_IMPLEMENTADO para flags reservados todavía no implementados;
- mantener modo texto actual intacto.
```

Criterio de salida:

```text
python conversa-engine/main.py --foo
=> stderr: COMANDO_NO_PERMITIDO: --foo
=> exit_code: 1

python conversa-engine/main.py --execute
=> stderr: COMANDO_NO_IMPLEMENTADO: --execute
=> exit_code: 1

python conversa-engine/main.py "vendo mucho pero no se si gano plata"
=> sigue funcionando como hoy.
```

### Fase 2 — Tests anti-bypass mínimos

Objetivo:

```text
Probar los bypasses reales, no la arquitectura imaginada.
```

Tests mínimos:

```text
- flag desconocido no se interpreta como texto;
- flag reservado no implementado no ejecuta fallback;
- texto libre sigue funcionando;
- output del kernel no se reescribe;
- NO_SIGNAL / BLOCKED se devuelve verbatim;
- Hermes no parsea archivos adjuntos.
```

### Fase 3 — Evidencia técnica mínima

Objetivo:

```text
Registrar ejecución sin construir factoría completa.
```

Contrato mínimo:

```yaml
task_id:
run_id:
trace_id:
command:
exit_code:
stdout_hash:
stderr_hash:
execution_result:
blocked_reason:
created_at:
duration_seconds:
```

Criterio:

```text
La evidencia técnica observa. No autoriza, no diagnostica, no aprueba.
```

### Fase 4 — Delegación documental futura

Objetivo:

```text
Permitir evidencia estructurada sin que Hermes parseé archivos.
```

Regla:

```text
Telegram/Hermes recibe archivo como canal.
PymIA o una frontera documental autorizada estructura evidencia.
Hermes no abre ni interpreta el archivo.
```

---

## Estado técnico real de este ciclo

Este bloque registra qué se logró efectivamente durante esta sesión y qué no debe darse por hecho.

### Logrado

```text
- se creó documentación física de autoauditoría;
- se verificó su lectura por MCP;
- se agregó política verbatim vs resumen;
- se agregó consolidado final de hallazgos honestos;
- se identificó el bypass de flags desconocidos;
- se separó el cambio de adapter.py por riesgo de traza no determinística;
- se publicó Chip 1 del kernel determinístico en origin/main.
```

### No logrado / no confirmado

```text
- no quedó confirmado el patch de main.py;
- no se pudo modificar Hermes runtime;
- no existe todavía ExecutionEvidence mínimo en código;
- no existe todavía CommandLogger persistente;
- no existe todavía test anti-bypass de flags desconocidos.
```

### Comando de rescate sugerido

```bash
cd E:\BuenosPasos\smartbridge\PymIA
git switch -c docs/hermes-anti-bypass-audit
git push origin docs/hermes-anti-bypass-audit
```

### Cambio técnico pendiente más importante

```text
conversa-engine/main.py debe pasar a fail-closed para flags.
```

No avanzar con métricas, TaskEvidence completo ni bootstrap hasta cerrar este bypass básico.

---

## Próximo backlog mínimo

Orden sugerido:

```text
1. Rescatar commit documental a rama normal.
2. Push de rama documental.
3. PR documental.
4. Rama separada para main.py fail-closed.
5. Test mínimo de flag desconocido.
6. Test de compatibilidad texto libre.
7. Recién después discutir ExecutionEvidence mínimo.
```

---

## Diagnóstico arquitectónico adicional: kernel no ensamblado

La convivencia defectuosa entre Hermes y PymIA no se explica solo por mala configuración de Hermes.

El problema más profundo es:

```text
El kernel determinístico todavía no está ensamblado como autoridad operativa completa.
```

Consecuencia:

```text
Hermes encuentra vacíos de ejecución y los llena con razonamiento propio, scripts ad-hoc o interpretación narrativa.
```

Esto ocurre porque faltan piezas de ensamble entre:

```text
- intake conversacional;
- evidencia estructurada;
- catálogo clínico-operativo;
- selección de skill;
- validación de condiciones mínimas;
- ejecución determinística;
- generación de diagnóstico;
- estado PASS / PARTIAL / BLOCKED;
- trazabilidad final.
```

Mientras ese ensamble no exista, Hermes tenderá a comportarse como analista por defecto.

### Regla de diseño derivada

```text
No se corrige este problema haciendo a Hermes más inteligente.
Se corrige ensamblando el kernel para que Hermes no tenga huecos que completar.
```

### Implicación operativa

Antes de construir métricas, bootstrap, provider fallback o TaskEvidence completo, hay que cerrar el circuito mínimo del kernel:

```text
mensaje/evidencia
→ contrato de entrada
→ catálogo/condiciones
→ skill candidata
→ validación de evidencia mínima
→ ejecución determinística
→ output crudo
→ estado
→ trazabilidad
```

Si cualquier etapa falta, el sistema debe responder:

```text
BLOCKED
```

No debe transferir el control a Hermes.

### Decisión

```text
El bypass de Hermes es síntoma.
El kernel no ensamblado es causa raíz.
```

Por lo tanto, el backlog no debe priorizar autonomía de Hermes, sino ensamble del kernel determinístico.

---

## Corrección sobre el núcleo robusto inicial: prematuro y pobre

La lectura posterior de los ciclos con Hermes obliga a corregir el diagnóstico del núcleo robusto inicial.

El núcleo robusto inicial no fue solamente incompleto.

Fue:

```text
prematuro y pobre para convivir con una IA operativa.
```

### Prematuro

Fue prematuro porque se expuso Hermes antes de que el kernel determinístico estuviera ensamblado como circuito cerrado.

Faltaban piezas mínimas:

```text
- contrato de entrada fuerte;
- evidencia estructurada operativa;
- validación de condiciones mínimas;
- selección formal de skill;
- ejecución determinística trazable;
- estados BLOCKED / PARTIAL / PASS;
- output verbatim con trazabilidad;
- tests anti-bypass;
- frontera clara entre conversación y cómputo.
```

Al faltar ese circuito, Hermes ocupó el vacío.

### Pobre

Fue pobre porque el núcleo robusto inicial redujo demasiado la frontera operativa.

El sistema quedó con:

```text
- main.py texto-only;
- integración documental incompleta;
- evidencia clínica no conectada al flujo real;
- sin enforcement de CLI;
- sin bloqueo de herramientas laterales;
- sin auditoría técnica mínima;
- sin fail-closed real;
- sin control efectivo sobre lo que Hermes podía hacer.
```

Eso generó una convivencia defectuosa:

```text
PymIA existe como intención determinística.
Hermes opera como analista de facto.
```

### Consecuencia

El núcleo robusto inicial permitió demostrar conversación, pero no permitió demostrar autoridad determinística.

Eso cambia la prioridad.

No alcanza con mejorar prompts, skills o configuración de Hermes.

Hay que reconstruir el núcleo robusto inicial alrededor del kernel:

```text
kernel primero;
Hermes después;
contrato antes que conversación;
BLOCKED antes que workaround;
evidencia antes que diagnóstico;
verbatim antes que resumen.
```

### Decisión

```text
El interfaz experimental debe considerarse una prueba prematura de interfaz, no un núcleo robusto inicial suficiente de sistema.
```

La siguiente iteración no debe agregar más inteligencia a Hermes.

Debe completar el ensamble mínimo del kernel determinístico y reducir la superficie operativa de Hermes.

---

## Pregunta rectora siguiente: kernel mínimo confiable

La pregunta correcta posterior a esta autoauditoría ya no es cómo mejorar Hermes.

La pregunta correcta es:

```text
¿Cuál es el kernel mínimo confiable?
¿Cuál es el corpus mínimo del kernel?
```

El interfaz experimental fue prematuro porque expuso una interfaz antes de tener un kernel operativo cerrado.

Por lo tanto, la próxima iteración debe definir el mínimo núcleo determinístico que puede recibir una demanda PyME, exigir evidencia, ejecutar una investigación y emitir un resultado trazable sin transferir control analítico a Hermes.

### Definición provisional

```text
Kernel mínimo confiable = circuito determinístico mínimo capaz de transformar una demanda operativa en un estado trazable: BLOCKED, PARTIAL o PASS.
```

No necesita cubrir todas las patologías.
No necesita tener todas las skills.
No necesita métricas avanzadas.
No necesita autonomía.

Sí necesita cerrar el circuito:

```text
entrada → síntoma → hipótesis investigable → evidencia mínima → ejecución → resultado → trazabilidad
```

### Corpus mínimo del kernel

El corpus mínimo no es una biblioteca grande.

Es el conjunto mínimo de documentos, contratos y reglas que permiten que el kernel opere sin improvisación.

Componentes mínimos:

```text
1. Contrato de entrada conversacional.
2. Catálogo mínimo de síntomas operativos.
3. Catálogo mínimo de patologías candidatas.
4. Mapa síntoma → hipótesis investigable.
5. Mapa hipótesis → evidencia requerida.
6. Mapa hipótesis → skill candidata.
7. Contrato de evidencia estructurada.
8. Reglas de suficiencia de evidencia.
9. Reglas de bloqueo.
10. Contrato de salida diagnóstica.
11. Contrato de trazabilidad.
12. Tests de regresión anti-bypass.
```

### Criterio de mínimo confiable

Un kernel mínimo confiable existe solo si puede hacer esto:

```text
Dado un mensaje del dueño,
identificar un síntoma operativo,
formular hipótesis investigable,
pedir evidencia mínima si falta,
bloquear si no hay evidencia,
ejecutar una skill si la evidencia alcanza,
y devolver un resultado trazable sin que Hermes analice por fuera.
```

### Primer recorte recomendado

No empezar por todas las áreas PyME.

Elegir una sola familia clínica-operativa:

```text
rentabilidad / margen / vendo pero no sé si gano
```

Porque permite validar el circuito completo con pocas variables:

```text
ventas;
costo directo;
unidades;
precio;
margen bruto;
gastos básicos;
período;
fuente de datos.
```

### Resultado esperado del kernel mínimo

El kernel debe poder devolver solo tres tipos de estado:

```text
BLOCKED: falta evidencia mínima o el contrato no alcanza.
PARTIAL: hay indicios pero falta evidencia para cierre.
PASS: hay hallazgo trazable, cuantificado y reproducible.
```

### Decisión

```text
Antes de seguir ampliando Hermes, hay que definir y ensamblar el corpus mínimo del kernel.
```

Hermes debe quedar como interfaz alrededor de ese corpus, no como sustituto del corpus.

---

## Frase rectora

```text
Hermes no necesita ser más inteligente.
Necesita tener menos caminos para saltearse el pipeline.
```
