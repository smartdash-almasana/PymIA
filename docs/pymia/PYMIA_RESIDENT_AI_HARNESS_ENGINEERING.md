# PymIA — Ingeniería de Arnés para IA Residente

Fecha: 2026-06-01  
Estado: posición arquitectónica  
Alcance: arnés operativo para una IA nativa, residente y confinada al sistema PymIA.

---

## 1. Propósito

Este documento fija la posición de PymIA sobre **ingeniería de arnés** aplicada a una IA residente.

La IA residente no debe operar como chatbot libre, asistente externo o agente imaginativo.

Debe operar dentro de un arnés.

El arnés es el conjunto de contratos, fuentes de verdad, fases, entradas, salidas, límites, memoria, registry, gates y formatos que sujetan a la IA dentro del sistema operativo PymIA.

---

## 2. Definición madre

```text
La ingeniería de arnés de PymIA es la disciplina que permite que una IA residente habite el neurosoftware PymIA sin escapar de su jaula arquitectónica, alimentándola sólo con fuentes válidas, limitando sus acciones a contratos vigentes, obligándola a respetar fases, inputs y outputs, y exigiendo que toda respuesta sea trazable al sistema PymIA.
```

---

## 3. El arnés no es la IA

El arnés no es:

```text
- el modelo;
- el prompt suelto;
- el agente;
- el plugin;
- el dispatcher;
- el dashboard;
- el microservicio.
```

El arnés es:

```text
la estructura que sujeta, alimenta, limita, mide, valida y orienta a la IA residente.
```

Sin arnés:

```text
IA creativa alrededor de PymIA.
```

Con arnés:

```text
IA nativa confinada al neurosoftware PymIA.
```

---

## 4. Por qué hace falta arnés

Una IA residente sin arnés tiende a:

```text
- inventar capacidades;
- confundir documentación con disponibilidad;
- saltar gates;
- diagnosticar sin evidencia;
- proponer features antes de auditar;
- mezclar CLI path con dispatcher path;
- confundir ficha abierta con plugin operativo;
- degradar PymIA a una colección de herramientas;
- responder desde conocimiento general y no desde PymIA.
```

El arnés evita eso.

El arnés convierte inteligencia general en inteligencia situada.

---

## 5. Relación con la jaula PymIA

La jaula de la IA residente es PymIA.

El arnés es la ingeniería concreta de esa jaula.

```text
Jaula = universo permitido.
Arnés = mecanismo operativo que obliga a permanecer dentro de ese universo.
```

La jaula define:

```text
qué existe.
```

El arnés define:

```text
cómo puede moverse la IA dentro de lo que existe.
```

---

## 6. Relación con la supracorteza

La supracorteza es la zona neurocomputacional donde conviven IA y determinismo.

El arnés es lo que impide que la supracorteza se convierta en improvisación.

```text
Corteza determinística: ejecuta.
Supracorteza IA: comprende y acompaña.
Arnés: limita, alimenta y valida a la supracorteza.
```

---

## 7. Componentes mínimos del arnés

### 7.1 Arnés de contexto

Define qué contexto puede recibir la IA residente.

Fuentes permitidas:

```text
- documentos madre;
- registry de fichas/plugins;
- contratos de fase;
- tests relevantes;
- código fuente relevante;
- runtime traces;
- memoria arquitectónica;
- memoria organizacional;
- issues/PRs si están conectados al repo.
```

Regla:

```text
La IA residente no debe responder desde contexto genérico cuando existe fuente PymIA.
```

---

### 7.2 Arnés de fases

Obliga a razonar según el pipeline PymIA:

```text
relato / input
→ ficha
→ hipótesis
→ evidencia requerida
→ evidencia recibida
→ suficiencia
→ readiness
→ candidato runtime
→ dispatch
→ resultado
→ entrega
→ memoria
```

Si falta una fase, la IA debe responder:

```text
bloqueado por fase faltante.
```

No debe saltar hacia diagnóstico o ejecución.

---

### 7.3 Arnés de capacidades

Conecta a la IA residente con el registry.

Debe responder según estados reales:

```text
AVAILABLE
PARTIALLY_AVAILABLE_BY_PATH
UNSUPPORTED_IN_PATH
MISSING_IN_REMOTE
NEEDS_PATH_CONFIRMATION
CONCEPTUAL
```

Ejemplo:

```text
excel_diagnostic = disponible por dispatcher y CLI.
supplier_duplicate_check = disponible por CLI, pendiente dispatcher.
PDF = no confirmado.
HTML report = no localizado.
```

---

### 7.4 Arnés de entrada

Define qué inputs acepta la IA residente.

Ejemplos:

```yaml
question: "¿por qué no ejecuta supplier_duplicate_check?"
scope:
  - registry
  - dispatcher
  - tests
  - runtime_bridge
case_trace: optional
```

La IA no debe asumir trazas no provistas.

---

### 7.5 Arnés de salida

La IA residente debe devolver estructuras auditables.

Formato recomendado:

```yaml
status: CONTRACT_MISMATCH
current_phase: dispatch
blocked_at: microservice_dispatcher
summary: supplier_duplicate_check existe por CLI pero no por dispatcher formal.
evidence:
  - registry
  - e2e_cli
  - microservice_dispatcher
  - tests
next_action:
  - update dispatcher
  - update tests
  - update registry
risk:
  - code-only change breaks tests
  - tests-only change creates false promise
```

---

### 7.6 Arnés de seguridad epistémica

Reglas obligatorias:

```text
1. No inventar módulos.
2. No declarar disponibilidad sin registry.
3. No saltar gates.
4. No diagnosticar sin evidencia.
5. No confundir ficha con plugin.
6. No confundir evidencia registrada con evidencia comprendida.
7. No confundir CLI path con dispatcher path.
8. No confundir cableado con validación.
9. No prometer capacidades no localizadas.
10. Si hay duda, auditar antes de diseñar.
```

---

### 7.7 Arnés de memoria

Define qué puede recordar la IA residente.

Debe recordar:

```text
- decisiones arquitectónicas;
- contratos vigentes;
- cambios de contrato;
- inconsistencias detectadas;
- tests obsoletos;
- capabilities disponibles;
- capabilities parciales;
- bloqueos recurrentes;
- no-promesas;
- hallazgos relevantes.
```

No debe recordar ruido.

Regla:

```text
memoria útil = memoria que mejora comprensión operativa.
```

---

## 8. PymIA-SDD: desarrollo guiado por contrato PymIA

La IA residente necesita un SDD propio.

No un SDD genérico.

Un **PymIA-SDD**.

Fases:

```text
1. Leer documento madre.
2. Leer registry.
3. Leer circuito afectado.
4. Leer tests que defienden el contrato.
5. Leer código relevante.
6. Formular hallazgo.
7. Clasificar el problema:
   - código roto;
   - test obsoleto;
   - contrato viejo;
   - registry desactualizado;
   - feature incompleta;
   - fuente no localizada.
8. Proponer cambio mínimo.
9. Exigir validación.
10. Registrar memoria arquitectónica.
```

Reglas:

```text
No hay cambio de código válido sin contrato leído.
No hay cambio de contrato válido sin tests identificados.
No hay disponibilidad válida sin registry actualizado.
```

---

## 9. Skills internas del arnés

Las skills de la IA residente son habilidades PymIA-específicas.

No son skills genéricas de frameworks.

Skills mínimas:

```text
- audit_capability_registry;
- trace_pipeline_phase;
- compare_cli_vs_dispatcher;
- explain_blocked_gate;
- detect_contract_mismatch;
- map_tests_to_contracts;
- classify_plugin_availability;
- enforce_no_promises;
- produce_developer_report;
- protect_ser_tener_hacer;
- request_minimum_evidence;
- distinguish_hypothesis_from_diagnosis.
```

Cada skill debe tener:

```text
input esperado;
fuentes permitidas;
output esperado;
límites;
estados de bloqueo.
```

---

## 10. Ejemplo aplicado: M17

Caso:

```text
supplier_duplicate_check
```

Sin arnés, una IA podría decir:

```text
Agreguemos supplier al dispatcher.
```

Con arnés, debe decir:

```yaml
status: CONTRACT_MISMATCH
summary: supplier_duplicate_check existe y funciona por CLI, pero el dispatcher formal conserva contrato viejo.
known_sources:
  - pymia/smartpyme/classifications/supplier_duplicate_check.py
  - pymia/smartpyme/e2e_cli.py
  - pymia/smartpyme/microservice_dispatcher.py
  - tests/smartpyme/test_one_microservice_smoke.py
  - docs/smartpyme/SMARTPYME_CAPABILITY_PLUGIN_REGISTRY.md
classification:
  code: implemented
  cli_path: available
  dispatcher_path: unsupported
  tests: old_contract
next_action:
  - update dispatcher
  - update smoke tests
  - update registry
risk:
  - code-only change fails tests
  - tests-only change creates false promise
```

---

## 11. Implementación mínima sugerida

Antes de construir una IA compleja, implementar arnés documental + estructuras mínimas.

Posible estructura:

```text
pymia/resident_ai/
  harness/
    context_harness.py
    phase_harness.py
    capability_harness.py
    output_harness.py
    safety_harness.py
  contracts/
    native_ai_contract.py
    phase_contracts.py
  prompts/
    resident_system.md
    developer_report.md
```

Pero no implementar todavía sin cerrar:

```text
- contrato operativo nativo;
- phase map;
- registry legible por máquina;
- formatos de salida;
- fuentes de verdad;
- memory policy.
```

---

## 12. Criterio de aceptación v0

La primera versión de arnés será suficiente cuando la IA residente pueda responder:

```text
1. Qué fase está activa.
2. Qué input falta.
3. Qué output debería existir.
4. Qué gate bloqueó.
5. Qué plugin está disponible.
6. Por qué camino está disponible.
7. Qué contrato gobierna el estado.
8. Qué test defiende el comportamiento.
9. Qué próximo paso mínimo corresponde.
10. Qué no debe prometerse.
```

---

## 13. Veredicto

La ingeniería de arnés es la pieza que vuelve viable la IA residente de PymIA.

Sin arnés, la IA es externa, imaginativa y riesgosa.

Con arnés, la IA se vuelve:

```text
nativa,
situada,
contractual,
trazable,
segura,
y útil para el neurosoftware PymIA.
```

---

## 14. Frases rectoras

```text
El arnés convierte una IA general en una IA residente.
```

```text
La jaula define el mundo; el arnés define el movimiento.
```

```text
La IA residente sólo puede pensar con PymIA, desde PymIA y para PymIA.
```

```text
Sin arnés, PymIA tiene un chatbot. Con arnés, PymIA tiene supracorteza.
```
