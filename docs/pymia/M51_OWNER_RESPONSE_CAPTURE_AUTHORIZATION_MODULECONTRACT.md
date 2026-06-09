# M51 — Owner Response Capture Authorization ModuleContract

Fecha: 2026-06-09
Estado: VIGENTE
Frente: `M51_OWNER_RESPONSE_CAPTURE_AUTHORIZATION`

---

## 1. Módulo autorizado

`pymia/contracts/owner_answers.py`

---

## 2. Responsabilidad contractual

Este módulo define la estructura mínima para capturar respuestas explícitas del dueño PyME sin convertirlas automáticamente en evidencia ni en diagnóstico.

La frontera contractual es:

```text
OwnerQuestion / OwnerQuestionsBundle
→ OwnerAnswer / OwnerAnswersBundle
→ futuro consumo gobernado, si se autoriza en otro ciclo
```

---

## 3. Entradas conceptuales

El contrato debe poder referenciar:

- `question_id`
- `question_text`
- tipo esperado o tipo recibido
- texto de respuesta o payload estructural mínimo
- `source_ref` de captura
- metadata opcional

---

## 4. Salidas conceptuales

El módulo debe exponer:

- `OwnerAnswer`
- `OwnerAnswersBundle`

Ambos deben ser serializables y trazables.

---

## 5. Reglas obligatorias

`OwnerAnswer` debe:

- tener identificador estable;
- referenciar explícitamente la pregunta origen;
- preservar el texto de la pregunta;
- preservar referencia trazable de captura;
- permitir texto de respuesta y/o payload estructurado mínimo;
- reflejar estado de captura sin asumir veracidad.

`OwnerAnswersBundle` debe:

- agrupar respuestas;
- tener identificador estable;
- permitir metadata opcional;
- serializar de manera estable.

---

## 6. Validaciones mínimas

Se debe rechazar, como mínimo:

- respuestas sin `answer_id`;
- respuestas sin `question_id`;
- respuestas sin `question_text`;
- respuestas sin `source_ref`;
- respuestas en estado `provided` que no traigan ni texto ni payload estructurado.

---

## 7. Prohibiciones

Este módulo no puede:

- interpretar la respuesta;
- crear evidencia;
- recalcular findings;
- tocar `graph`;
- tocar `state`;
- abrir runtime conversacional;
- asumir canal productivo alguno.
