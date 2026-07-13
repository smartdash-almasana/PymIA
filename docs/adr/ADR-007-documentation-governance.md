# ADR-007 — Gobierno documental por autoridad mínima

**Estado:** ACEPTADO / ACTUALIZADO

**Fecha de actualización:** 2026-07-13

## Contexto

El sistema anterior clasificaba cientos de documentos como vigentes, candidatos, archivo, superados o museo. Aunque preservaba historia, mantenía físicamente presentes fuentes contradictorias y produjo deuda cognitiva.

## Decisión

- `docs/current/README.md` enumera toda la autoridad documental vigente.
- Solo los documentos allí citados gobiernan arquitectura o implementación.
- La documentación obsoleta, duplicada o sustituida se elimina del árbol activo.
- Git conserva la historia y permite recuperar decisiones anteriores.
- La evidencia técnica permanece en tests, commits y artefactos necesarios; no requiere un closeout documental por cada microciclo.
- Nuevas reglas deben incorporarse a un documento rector existente. Solo se crea un documento nuevo cuando representa una autoridad estable que no cabe en los documentos actuales.

## Consecuencia

El objetivo es comprender PymIA y Servicio 1 leyendo menos de diez documentos rectores, sin reconstruir la arquitectura desde auditorías, roadmaps o checkpoints vencidos.
