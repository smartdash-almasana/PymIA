# ADR-007 — Gobierno documental por autoridad mínima

**Estado:** ACEPTADO / ACTUALIZADO

**Fecha de actualización:** 2026-08-23

## Contexto

El sistema anterior clasificaba cientos de documentos como vigentes, candidatos, archivo, superados o museo. Aunque preservaba historia, mantenía físicamente presentes fuentes contradictorias y produjo deuda cognitiva.

Durante la convergencia arquitectónica de Servicio 1 se verificó además otro riesgo: decisiones normativas podían quedar únicamente en chats, prompts de ejecución o artefactos temporales, mientras el código seguía evolucionando. Eso permite que una implementación localmente verde introduzca contratos, flags, rutas transitorias o compatibilidades que no fueron incorporados a la autoridad documental vigente.

## Decisión

- `docs/current/README.md` enumera toda la autoridad documental vigente.
- Solo los documentos allí citados gobiernan arquitectura o implementación.
- **Una decisión de arquitectura no existe como autoridad si sólo vive en un chat, prompt, auditoría temporal o memoria de sesión.**
- **Toda decisión normativa debe quedar incorporada a un documento rector del repositorio antes de que su implementación continúe o se dé por aceptada.**
- Cuando una decisión cambie topología, límites de autoridad, contratos canónicos, rutas productivas, request kinds, política de compatibilidad o invariantes de Servicio 1, debe actualizarse en el mismo frente documental `SERVICE_1_CANONICAL_AXIS.md` y/o `SERVICE_1_ARCHITECTURE_LOCK.md`. Si cambia la autoridad documental, también se actualiza `docs/current/README.md`.
- Chats, prompts de Codex/OpenCode y artefactos `_audit/` son medios de trabajo y evidencia; **no son fuente normativa**.
- Una decisión abierta o todavía discutida debe marcarse explícitamente como `UNDER_REVIEW`; no puede entrar al runtime por inercia ni transformarse en contrato permanente porque un test local pase.
- La documentación obsoleta, duplicada o sustituida se elimina del árbol activo.
- Git conserva la historia y permite recuperar decisiones anteriores.
- La evidencia técnica permanece en tests, commits y artefactos necesarios; no requiere un closeout documental por cada microciclo.
- Nuevas reglas deben incorporarse a un documento rector existente. Solo se crea un documento nuevo cuando representa una autoridad estable que no cabe en los documentos actuales.

## Regla operativa obligatoria

```text
decisión arquitectónica
→ actualización del documento rector
→ revisión de contradicciones con autoridad vigente
→ implementación
→ prueba
→ veredicto
```

Queda prohibido el orden inverso `implementar primero → documentar después` cuando la implementación introduce o modifica una decisión arquitectónica.

## Consecuencia

El objetivo es comprender PymIA y Servicio 1 leyendo menos de diez documentos rectores, sin reconstruir la arquitectura desde auditorías, roadmaps, chats o checkpoints vencidos.

A partir de esta actualización, ninguna conversación puede funcionar como memoria arquitectónica primaria de Servicio 1.
