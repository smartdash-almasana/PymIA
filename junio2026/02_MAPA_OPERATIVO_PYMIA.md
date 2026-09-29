# 02 — Mapa operativo PymIA

## Modelo mental vigente

PymIA debe leerse como un sistema de lectura operativo-financiera asistido por evidencia, no como un chatbot ni como una plataforma de agentes.

## Flujo conceptual

- Entrada del dueño y archivos/datos.
- Normalización y evidencia estructurada.
- Contratos, validación y gates.
- Reconciliación contra requerimientos y fórmulas.
- Hallazgos proporcionales.
- Salida owner-facing.
- Confirmación humana o revisión cuando falta evidencia.

## Invariantes

1. La conversación no decide verdad operacional.
2. El LLM no decide por sí mismo.
3. Los gates y contratos deciden si hay evidencia suficiente.
4. El dueño PyME aporta sentido de negocio, corrección y contexto.
5. El operador humano sigue siendo válido en MVP asistido.
6. No hay PASS sin evidencia reproducible.
7. No se llama SaaS/producto autónomo a lo que todavía requiere operador.
8. No se activa catálogo sin regla, evidencia y trazabilidad.
9. No se agrega arquitectura si no ayuda al caso real.
10. Hermes no existe como futuro del sistema.

## Capas del repo

| Capa | Lectura recomendada |
|---|---|
| `PymIA-Live/` | núcleo ejecutable/migrado, pero requiere validación técnica |
| `pymia/` raíz | posible legado/superficie vieja; auditar antes de usar |
| `tests/` raíz | puede mezclar legacy, imports rotos y tests de documentación |
| `docs/current/` | autoridad documental, salvo referencias Hermes |
| `docs/hermes/` | museo/deuda a retirar |
| `conversa-engine/` | antecedente histórico, no runtime futuro |
| `_docs_inbox/` | material entrante/no rector salvo promoción explícita |

## Separación conceptual obligatoria

- Evidencia: datos observados, archivos, columnas, variables computadas, registros y trazabilidad.
- Inferencia: interpretación limitada derivada de evidencia y reglas.
- Diagnóstico: solo cuando hay regla, evidencia suficiente y gate aprobado.
- Recomendación: proporcional, explicable y owner-facing.

## Owner-facing

La salida para el dueño debe traducir sin inventar: dato observado, posible significado, faltante de confirmación, pregunta concreta y próximo paso posible.

## Riesgo actual

PymIA tiene una arquitectura conceptual más madura que su validación con casos reales. Toda nueva capa debe justificar cómo acerca el sistema a un caso real supervisado.
