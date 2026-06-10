# SIMULATED_PILOT_FRICTION_RECONCILIATION

Fecha: 2026-06-10
Estado: OPEN
Origen: `ASSISTED_SIMULATED_PILOT_001_CHECKPOINT.md`
Tipo: reconciliación metodológica de fricciones

## 1. Veredicto

La simulación asistida terminó en:

```text
PARTIAL
```

No falló el flujo integrado.

Sí mostró fricciones relevantes antes de intentar un piloto real.

La simulación certifica:

- reentry de owner answer;
- bloqueo controlado;
- límites de preliminary taxonomy;
- ausencia de diagnóstico en primer turno;
- separación entre simulación y piloto real.

No certifica:

- valor diagnóstico final;
- desbloqueo completo del caso;
- utilidad comercial suficiente;
- readiness para piloto real.

## 2. Principio de tratamiento

Las fricciones observadas no deben resolverse en bloque.

Cada fricción debe clasificarse y, si corresponde, abrir un TaskSpec atómico.

Prohibido convertir esta reconciliación en permiso para:

- nuevas features;
- Telegram;
- Hermes;
- ERP;
- PDF productivo;
- nuevas fórmulas;
- runtime externo;
- refactor amplio;
- cierre artificial de TD-004.

## 3. Fricciones observadas

### SPFR-001 — `raw_first_message` queda null en graph-level simulation

Clasificación: STATE / TRACEABILITY
Prioridad: MEDIA
Bloqueante para piloto real: NO inmediato, pero debe entenderse.

Observación:

```text
raw_first_message quedó null;
la señal quedó en preliminary_taxonomy.created_from.
```

Riesgo:

- pérdida de trazabilidad narrativa del primer mensaje;
- dificultad para auditar cómo nació la señal preliminar;
- divergencia entre FSM-level contract y graph-level projection.

Criterio de cierre:

- determinar si `raw_first_message` debe persistir en graph state;
- si corresponde, abrir TaskSpec focal de preservación de primer mensaje;
- no modificar graph sin auditoría previa.

---

### SPFR-002 — F1 persiste como `phase = NEW`, no `FICHA_PYME_INICIAL`

Clasificación: STATE / SEMANTIC_ALIGNMENT
Prioridad: MEDIA
Bloqueante para piloto real: NO inmediato, pero puede confundir auditoría.

Observación:

```text
F1 persistió como phase = NEW,
pero la ficha obligatoria siguió viva vía pending_question.
```

Riesgo:

- desalineación semántica entre FSM interno y graph state;
- agentes futuros pueden interpretar `NEW` como no-iniciado;
- reportes de auditoría pueden subestimar avance conversacional.

Criterio de cierre:

- decidir si `phase` graph debe reflejar la fase FSM o si `pending_question` es la fuente visible;
- documentar la frontera si no se cambia código;
- abrir TaskSpec sólo si hay efecto real sobre flujo o auditoría.

---

### SPFR-003 — Owner-facing questions mezclan lenguaje legible con claves técnicas crudas

Clasificación: OWNER_FACING / USABILITY
Prioridad: ALTA
Bloqueante para piloto real: SÍ, si aparece ante dueño real.

Observación:

```text
owner-facing mezcla preguntas legibles con claves técnicas crudas como:
amortization, dso, own_price.
```

Riesgo:

- baja comprensión del dueño PyME;
- pérdida de confianza;
- apariencia de herramienta técnica inmadura;
- fricción comercial directa.

Criterio de cierre:

- mapear claves técnicas a lenguaje de dueño;
- evitar exponer ids/variables crudas en preguntas visibles;
- preservar trazabilidad técnica internamente;
- testear que owner_questions_bundle sea legible.

TaskSpec sugerido:

```text
OWNER_QUESTIONS_HUMANIZATION_GATE
```

---

### SPFR-004 — Respuesta narrativa del dueño no destraba faltantes estructurales

Clasificación: EVIDENCE / BLOCKING_SEMANTICS
Prioridad: MEDIA-ALTA
Bloqueante para piloto real: DEPENDE.

Observación:

```text
La respuesta simulada del dueño fue consumida por reentry,
pero el caso siguió BLOCKED.
```

Riesgo:

- el sistema puede aceptar respuesta narrativa sin convertirla en evidencia suficiente;
- el dueño puede sentir que respondió, pero el sistema sigue bloqueado;
- falta claridad sobre qué tipo de respuesta destraba qué faltante.

Criterio de cierre:

- distinguir faltantes de sentido vs faltantes estructurales;
- si el faltante requiere dato tabular, explicarlo al dueño;
- si una respuesta narrativa puede resolver un faltante, proyectarla explícitamente;
- no inventar evidencia.

TaskSpec sugerido:

```text
OWNER_ANSWER_TO_MISSING_INPUTS_RECONCILIATION
```

---

### SPFR-005 — `findings_count = 0`

Clasificación: VALUE_DIAGNOSTIC / SIMULATION_LIMIT
Prioridad: MEDIA
Bloqueante para piloto real: NO como bloqueo técnico, SÍ como alerta de valor.

Observación:

```text
findings_count = 0.
```

Interpretación:

La simulación certifica bloqueo y reentrada, no valor diagnóstico final.

Riesgo:

- avanzar a piloto real sin evidencia de reporte útil;
- confundir pipeline integrado con entrega valiosa.

Criterio de cierre:

- no exigir findings si la evidencia es insuficiente;
- sí exigir que el reporte explique por qué no hay findings;
- antes de piloto real, ejecutar simulación con evidencia suficiente o medir bloqueo como resultado honesto.

---

### SPFR-006 — `gate_verdict` persistido quedó null

Clasificación: STATE / READINESS_TRACE
Prioridad: MEDIA
Bloqueante para piloto real: NO inmediato.

Observación:

```text
gate_verdict persistido quedó null aunque el comportamiento visible fue de bloqueo controlado.
```

Riesgo:

- pérdida de trazabilidad del gate;
- dificultad para auditar por qué el caso quedó BLOCKED;
- downstream puede depender de `delivery_status` y no de `gate_verdict`.

Criterio de cierre:

- auditar fuente soberana: `delivery_status` vs `gate_verdict`;
- documentar si `gate_verdict` es legacy, opcional o deuda real;
- no crear otro verdict paralelo.

TaskSpec sugerido:

```text
BLOCKING_GATE_TRACE_RECONCILIATION
```

## 4. Priorización

### Resolver antes de piloto real

```text
SPFR-003 — OWNER_QUESTIONS_HUMANIZATION_GATE
SPFR-004 — OWNER_ANSWER_TO_MISSING_INPUTS_RECONCILIATION
```

Motivo:

- afectan directamente la experiencia del dueño;
- pueden impedir valor percibido;
- no deben mezclarse con arquitectura amplia.

### Auditar después

```text
SPFR-001 — raw_first_message null
SPFR-002 — phase NEW vs FICHA_PYME_INICIAL
SPFR-006 — gate_verdict null
```

Motivo:

- son trazabilidad/estado;
- pueden ser deuda real o diferencia esperada entre capas;
- requieren auditoría antes de patch.

### Mantener como alerta de valor

```text
SPFR-005 — findings_count = 0
```

Motivo:

- no es necesariamente bug;
- puede ser comportamiento correcto si la evidencia no alcanza;
- debe evaluarse junto con suficiencia de evidencia.

## 5. Próximo frente recomendado

Abrir sólo:

```text
OWNER_QUESTIONS_HUMANIZATION_GATE
```

Objetivo:

Evitar que el dueño vea claves técnicas crudas en preguntas visibles.

Alcance esperado:

- auditar dónde se genera `owner_questions_bundle`;
- mapear variables técnicas a lenguaje operativo;
- preservar claves técnicas internamente;
- test focal contra claves como `amortization`, `dso`, `own_price`;
- no tocar graph, bridge ni DiagnosticCore salvo que la generación visible viva ahí y el TaskSpec lo autorice.

## 6. Relación con TD-004

TD-004 sigue abierta.

```text
ASSISTED_SIMULATED_PILOT_001 no cierra TD-004.
```

TD-004 sólo puede cerrarse con caso real.

## 7. Estado

```text
OPEN
```

Esta reconciliación queda abierta hasta que las fricciones priorizadas sean tratadas o descartadas explícitamente.
