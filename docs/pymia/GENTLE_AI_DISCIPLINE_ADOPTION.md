# GENTLE AI DISCIPLINE ADOPTION FOR PYMIA-LIVE

## Estado

```text
DOCUMENTARY_ADOPTION_ONLY
NO_RUNTIME_CHANGE
NO_REFACTOR_AUTHORIZATION
NO_BIG_BANG_AUTHORIZATION
```

## Propósito

Registrar cómo PymIA-Live puede adoptar disciplina técnica tipo Gentle AI sin alterar su ADN arquitectónico actual ni convertir esa disciplina en una arquitectura rectora.

Este documento no autoriza:

```text
- mover archivos;
- refactorizar runtime;
- crear ports/adapters en código;
- crear packs;
- tocar CLI;
- tocar vertical_pipeline;
- tocar diagnostic_core;
- introducir FastHTML;
- introducir auth/JWT;
- introducir Postgres obligatorio.
```

---

## 1. Veredicto

```text
Gentle AI se adopta como disciplina, no como arquitectura rectora.
```

Lectura correcta:

- PymIA conserva su ADN arquitectónico.
- Gentle AI aporta orden técnico y guardrails.
- La identidad del sistema sigue gobernada por evidencia, flujo asistido, CLI-first y kernel estable.

---

## 2. Qué se adopta

Se adopta de Gentle AI lo que fortalece disciplina sin forzar una arquitectura SaaS/CRUD:

- tipado estricto;
- tests como frontera obligatoria antes de refactorizar;
- config explícita;
- ports/adapters como dirección futura, no como imposición inmediata;
- guardrails metodológicos y arquitectónicos;
- `AGENTS.md` como contrato operativo;
- `CLI-first`;
- separación entre UI, runtime y core.

### Traducción operativa

| Disciplina adoptada | Lectura en PymIA-Live |
|---|---|
| Tipado estricto | Reducir ambigüedad contractual y hacer más verificables las fronteras |
| Tests | No abrir extracción ni refactor sin verde previo |
| Config explícita | Hacer visible qué depende de config y qué depende de dominio |
| Ports/adapters | Usarlos sólo cuando una frontera real lo exija |
| Guardrails | Frenar deriva hacia web-first, storage lock-in o core inflado |
| `AGENTS.md` | Mantener método y stop conditions por encima de la ansiedad de implementación |
| CLI-first | Preservar el canal vivo verificado antes de abrir otros |
| Separación UI/runtime/core | Evitar que renderer, storage o canal absorban lógica central |

---

## 3. Qué NO se adopta

No se adopta de Gentle AI ninguna deriva que reemplace la identidad de PymIA:

- web-first;
- SaaS/CRUD como modelo rector;
- FastHTML como centro;
- auth/JWT prematuro;
- Postgres obligatorio;
- big bang migration;
- dominio sectorial hardcodeado.

### Regla de interpretación

```text
Si una práctica “moderna” obliga a PymIA a comportarse como SaaS CRUD antes de estabilizar su núcleo operativo, esa práctica queda rechazada para esta etapa.
```

---

## 4. Mapa conceptual actual → objetivo

Este mapa no mueve archivos. Sólo aclara lectura arquitectónica.

| Superficie actual | Lectura actual válida | Dirección conceptual |
|---|---|---|
| `PymIA-Live/pymia/cli/vertical_slice.py` | adaptador CLI vivo | `interface/cli` |
| `PymIA-Live/pymia/application/vertical_pipeline.py` | frontera de orquestación viva | application orchestration boundary |
| `PymIA-Live/pymia/smartpyme/evidence.py` | contrato evidence-first puro | evidence/kernel-compatible |
| `PymIA-Live/pymia/rendering/owner_markdown_renderer.py` | render/presentación | presentation adapter |
| `PymIA-Live/pymia/smartpyme/case_replay.py` + `PymIA-Live/pymia/smartpyme/ocf_snapshot.py` | continuidad mínima de caso | `case_state` seed |
| `PymIA-Live/pymia/services/pathology_engine_service.py` | consumidor de conocimiento inyectable | injectable knowledge consumer |
| `PymIA-Live/pymia/smartpyme/service_depth.py` | heurística viva útil pero riesgosa | future pack/contract candidate |
| `PymIA-Live/pymia/smartpyme/pipeline_registration.py` + `PymIA-Live/pymia/smartpyme/storage.py` | persistencia local y traza actual | filesystem/jsonl adapter candidates |

### Lectura clave

El punto importante NO es renombrar carpetas ahora.

El punto importante es evitar confundir:

```text
archivo actual
≠
frontera conceptual futura
```

---

## 5. Guardrails

Toda adopción disciplinada de Gentle AI en PymIA-Live queda subordinada a estos guardrails:

- no big bang;
- no refactor without green tests;
- no knowledge hardcoded in kernel;
- no UI-first migration;
- no storage lock-in;
- el Pack System sigue siendo el camino para fórmulas, patologías y sectores.

### Implicancias

1. Ninguna extracción se autoriza sólo porque “queda más prolija”.
2. Ninguna interfaz web futura puede desplazar el canal CLI verificado.
3. Ninguna decisión de persistencia local actual debe presentarse como verdad arquitectónica final.
4. Ningún hardcode sectorial nuevo debe entrar al kernel vivo.
5. `ADR-024` sigue gobernando la frontera kernel ↔ conocimiento enchufable.

---

## 6. Roadmap incremental

La adopción disciplinada queda permitida sólo como secuencia incremental:

### Step 1

```text
document current mapping
```

Primero se aclara qué representa cada superficie actual sin mover comportamiento.

### Step 2

```text
extract ports only around storage/evidence when needed
```

No antes. Sólo cuando una frontera real lo exija y con tests verdes.

### Step 3

```text
declare adapters without moving behavior
```

La declaración conceptual puede preceder a la extracción física.

### Step 4

```text
move service_depth routing vocabulary toward pack/contract
```

`service_depth.py` queda identificado como zona de riesgo documental para una futura migración a contrato/pack, no como trabajo autorizado en esta etapa.

### Step 5

```text
introduce web only as interface after CLI remains stable
```

Web puede existir más adelante sólo como interfaz. No como centro del sistema.

---

## 7. Validation references

Referencias de validación relevantes al momento de esta adopción documental:

- OCF snapshot green:
  - `tests/smartpyme/test_ocf_snapshot.py`
  - resultado verificado: `13 passed`
- Focal no-regression green:
  - `tests/smartpyme/test_service_depth.py`
  - `tests/application/test_vertical_pipeline_boundary.py`
  - `tests/rendering/test_owner_markdown_renderer_boundary.py`
  - `tests/smartpyme/test_question_alignment_gate.py`
  - resultado verificado: `27 passed`

Estas referencias validan una precondición metodológica importante:

```text
antes de registrar disciplina futura, la slice OCF roja debía estar verde.
```

---

## 8. Decisión operativa de cierre

```text
Gentle AI entra en PymIA-Live como disciplina técnica de bajo riesgo.
No entra como reemplazo de la arquitectura de PymIA.
```

Próximo paso permitido desde este documento:

```text
usar este mapa como guardrail documental para cambios futuros,
sin presentar web/auth/postgres/refactor como obligación inmediata.
```
