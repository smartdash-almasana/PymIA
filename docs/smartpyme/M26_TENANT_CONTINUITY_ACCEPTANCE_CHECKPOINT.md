# M26 — Tenant Continuity Acceptance Checkpoint

## Estado

CLOSED_PUSHED

## Fecha

2026-06-03

## Commit principal

```text
4e24bc3a697ffbdb640ba18a1907533333815b4a test(orchestration): add tenant continuity acceptance coverage
```

## Contexto

M25 dejó documentado que GEN05 — Memoria operacional estaba en estado parcial por falta de evidencia cross-session:

```text
No hay test que demuestre tenant A conversa día 1 -> tenant A regresa día 3 -> sistema recupera contexto -> evita repreguntar -> continúa diagnóstico.
```

M26 aborda ese hueco con un slice mínimo de aceptación centrado en continuidad por tenant dentro de la capa de orquestación.

## Objetivo del hito

Agregar cobertura de aceptación para demostrar que:

1. un tenant inicia una demanda operativa;
2. el sistema persiste estado conversacional;
3. otro tenant inicia una demanda independiente;
4. el primer tenant vuelve con una nueva interacción;
5. el contexto del primer tenant se recupera y evoluciona;
6. el storage por tenant no se mezcla.

## Archivo agregado

```text
tests/orchestration/test_tenant_continuity_acceptance.py
```

## Comportamiento cubierto

El test `test_tenant_continuity_acceptance` valida:

- `tenant_a` inicia con un mensaje operativo: `fabrico ropa y vendo por mayor`;
- `run_pymia_graph(...)` genera respuesta;
- `load_state(tenant_a, chat_a, tmp_path)` recupera estado persistido;
- `progressive_context` existe después del primer turno;
- `tenant_b` inicia una conversación separada;
- `tenant_a` y `tenant_b` mantienen `progressive_context` distintos;
- `tenant_a` vuelve con un segundo mensaje: `mi nombre es Juan`;
- el `progressive_context` de `tenant_a` evoluciona respecto del turno anterior;
- `find_conversations_by_tenant(...)` no mezcla chats entre tenants.

## Evidencia técnica directa

El test usa exclusivamente:

```text
pymia.orchestration.graph.run_pymia_graph
pymia.orchestration.state.PymIAEvent
pymia.orchestration.state_storage.load_state
pymia.orchestration.state_storage.find_conversations_by_tenant
```

No usa red, LLM, Supermemory real, Telegram, PDF, HTML, UI, dispatcher ni plugins.

## Validaciones reportadas

Validación individual:

```text
python -m pytest tests/orchestration/test_tenant_continuity_acceptance.py -v
```

Resultado reportado:

```text
1 passed
```

Suite orquestación:

```text
python -m pytest tests/orchestration -q
```

Resultado reportado:

```text
98 passed, 1 failed
```

Falla reportada como preexistente:

```text
test_conversation_adapter_consumption_smoke_domain_core_v1
```

Causa reportada:

```text
assert has_taxonomy is True
```

Interpretación: el FSM offline requiere múltiples respuestas para completar perfil antes de tener taxonomía; un solo mensaje no la produce. No fue introducido por M26.

Suite SmartPyme:

```text
python -m pytest tests/smartpyme -q
```

Resultado reportado:

```text
619 passed
```

## Límites preservados

M26 preservó explícitamente estos límites:

- No modificar código productivo.
- No modificar `capabilities.yaml`.
- No modificar `capability_registry.py`.
- No modificar CI.
- No tocar dispatcher.
- No tocar plugins.
- No tocar Telegram.
- No tocar PDF.
- No tocar HTML.
- No tocar UI/dashboard.
- No agregar red.
- No agregar LLM.
- No agregar Supermemory real.
- No crear nueva capacidad de negocio.

## Resultado metodológico

M26 no certifica una nueva capability de negocio.

M26 agrega una prueba de aceptación para cerrar un hueco específico detectado en M25:

```text
GEN05 Memoria operacional
-> continuidad cross-session por tenant
-> aislamiento entre tenants
```

La cobertura nueva no convierte todavía GEN09 en completo, pero reduce el riesgo de producto asociado a que el sistema olvide contexto entre interacciones.

## Estado GEN05 después de M26

GEN05 mejora respecto del diagnóstico M25.

Antes:

```text
[-] Memoria operacional parcial: sin test cross-session continuity.
```

Después:

```text
[-] Memoria operacional con aceptación cross-session mínima cubierta.
```

Sigue siendo parcial porque aún falta demostrar el ciclo completo de producto:

```text
cliente vuelve
-> sistema recuerda contexto útil
-> evita repreguntar evidencia ya conocida
-> continúa diagnóstico
-> registra siguiente paso o venta futura
```

M26 cubre la persistencia y recuperación del contexto, no todavía el comportamiento comercial/producto completo.

## Riesgo residual

El test demuestra continuidad técnica de `progressive_context`, pero no prueba todavía:

- continuidad semántica de evidencia ya recibida;
- continuidad de hallazgos entregados;
- continuidad de recomendaciones previas;
- siguiente paso comercial;
- acceptance E2E de producto multi-tenant.

Por eso M26 no debe interpretarse como cierre de GEN09.

## Próximo frente recomendado

Abrir auditoría/plan M27 orientado a GEN04:

```text
M27_HALLAZGOS_NARRATIVOS_CONSOLIDATION
```

Objetivo sugerido:

```text
cerrar la brecha entre hallazgos técnicos y reporte narrativo legible para cliente PyME.
```

No avanzar todavía a GEN06, GEN07 o GEN09 completo hasta consolidar:

1. GEN04 — hallazgos narrativos;
2. GEN05 — continuidad útil de tenant;
3. GEN09 — acceptance E2E producto mínimo.

## Regla de continuidad

No abrir M27 sin recorte explícito de scope.

M27 no debe mezclar:

- nueva capability de negocio;
- registry changes;
- dispatcher/plugin changes;
- Telegram/PDF/HTML/UI;
- CI changes;
- LLM integration;
- aprendizaje/intervención.

El próximo avance debe ser un slice de reporte/hallazgo narrativo comprobable por tests, no una expansión de producto completa.
