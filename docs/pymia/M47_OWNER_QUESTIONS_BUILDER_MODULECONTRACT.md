# M47 — Owner Questions Builder ModuleContract

Fecha: 2026-06-09
Estado: VIGENTE
Frente: `M47_OWNER_QUESTIONS_BUILDER_IMPLEMENTATION`

---

## 1. Frontera

Este contrato regula la frontera entre:

```text
faltantes explícitos ya trazados
↔ OwnerQuestionsBuilder
↔ OwnerQuestionsBundle
```

La frontera M47 construye estructura determinística.

No abre canal conversacional ni interpreta diagnóstico.

---

## 2. Responsabilidades permitidas

La frontera M47 puede:

- leer `missing_evidence`, `next_questions`, `blocked_message` y `source_ref`;
- aplicar un mapeo estático de variables conocidas;
- construir preguntas genéricas seguras para claves desconocidas;
- deduplicar contenido repetido;
- preservar orden estable;
- generar IDs determinísticos;
- devolver `OwnerQuestionsBundle`.

---

## 3. Responsabilidades prohibidas

La frontera M47 no puede:

- usar heurísticas libres;
- llamar LLM o NLP;
- abrir runtime o graph;
- tocar Telegram, Hermes o FastAPI;
- recalcular diagnóstico;
- alterar artefactos soberanos;
- crear narrativa libre;
- inferir valores faltantes.

---

## 4. Invariantes

- mismo input → mismo orden y mismos `question_id`;
- `source_ref` no cambia;
- `required=True` por defecto;
- entradas repetidas no deben duplicar preguntas;
- variables conocidas usan mapeo estático;
- variables desconocidas usan fallback seguro;
- `next_questions` se integran como texto explícito de origen;
- `blocked_message` debe preservarse en la pregunta contextual o en su metadata.

---

## 5. Dependencias permitidas

- `pymia/contracts/owner_questions.py`
- librerías estándar de Python

No se autorizan dependencias a componentes conversacionales, runtime ni red.

---

## 6. Side effects

El builder no debe escribir archivos, llamar red ni ejecutar procesos.

---

## 7. Estado

```text
M47 ModuleContract = AUTHORIZED_FOR_IMPLEMENTATION
```

Este contrato autoriza la implementación mínima y determinística del builder.
