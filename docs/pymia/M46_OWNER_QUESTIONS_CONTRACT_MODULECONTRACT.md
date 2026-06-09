# M46 — Owner Questions Contract ModuleContract

Fecha: 2026-06-09
Estado: VIGENTE
Frente: `M46_OWNER_QUESTIONS_CONTRACT_AUTHORIZATION`

---

## 1. Frontera

Este contrato regula la frontera entre:

```text
faltantes ya trazados en artefactos soberanos
↔ representación estructurada de preguntas explícitas al dueño
```

La frontera M46 no decide qué preguntar por heurística.

Sólo define cómo representar una pregunta ya autorizada por artefactos fuente.

---

## 2. Responsabilidades permitidas

La frontera M46 puede:

- modelar una pregunta explícita al dueño;
- registrar el motivo de la pregunta;
- registrar la clave faltante si existe;
- registrar la referencia trazable al artefacto fuente;
- registrar el tipo esperado de respuesta;
- agrupar preguntas en un bundle.

---

## 3. Responsabilidades prohibidas

La frontera M46 no puede:

- diagnosticar;
- generar preguntas automáticamente desde narrativa libre;
- completar datos faltantes;
- abrir canales conversacionales;
- tocar runtime, Telegram, Hermes, FastAPI o graph;
- alterar artefactos soberanos;
- reinterpretar findings o gates.

---

## 4. Invariantes

- Toda pregunta debe ser explícita y trazable.
- `source_ref` no puede omitirse.
- `question_text` no puede estar vacío.
- `reason` no puede estar vacío.
- `required` debe representar obligación contractual de respuesta, no prioridad heurística.
- El bundle puede estar vacío, pero si contiene preguntas todas deben respetar el mismo contrato.

---

## 5. Dependencias permitidas

- `pydantic`
- tipos estándar de Python

No se autorizan dependencias a runtime, transporte, network ni componentes conversacionales.

---

## 6. Side effects

El módulo contractual no debe escribir archivos, llamar red ni ejecutar procesos.

---

## 7. Determinismo

Para los mismos datos explícitos de entrada, el contrato debe producir el mismo payload serializado.

---

## 8. Estado

```text
M46 ModuleContract = AUTHORIZED_FOR_IMPLEMENTATION
```

Este contrato autoriza sólo el modelado estructural.
