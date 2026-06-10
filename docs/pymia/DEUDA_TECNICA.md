# PymIA — Deuda técnica post-C²I

Fecha: 2026-06-10
Estado: AUDITORIA_INICIAL_ACTUALIZADA
Alcance: deuda técnica visible post integración controlada C²I.

## 1. Veredicto operativo

PymIA se considera en estado INTEGRADO_CONTROLADO para el flujo actual.

No hay bloqueantes observados para el circuito integrado ya validado:

```text
F1 primer contacto
→ F2 evidencia/documento
→ bridge + OwnerFacingReport
→ owner_questions_bundle
→ F3 owner-answer reentry
→ reporte actualizado
```

Esta auditoría no autoriza features nuevas ni cambios de runtime.

## 2. Regla de trabajo

Toda deuda debe resolverse por TaskSpec atómico.

Prohibido resolver "toda la deuda" en un único patch.

Orden recomendado:

```text
1. Deuda bloqueante
2. Deuda contractual / lifecycle
3. Deuda de tests / CI
4. Deuda operativa para pilotos
5. Limpieza menor
```

## 3. Deuda técnica identificada

### TD-001 — Lifecycle de preliminary_taxonomy no formalizado

Clasificación: CONTRACTUAL / LIFECYCLE
Prioridad: ALTA
Estado: CERRADA
Bloqueante: NO

Resolución aplicada:

- Se creó contrato explícito en `pymia/smartpyme/preliminary_taxonomy.py`.
- Se formalizó `PreliminaryTaxonomyStatus`.
- Se formalizó `PreliminaryTaxonomySignal`.
- `_build_preliminary_taxonomy_signal()` instancia el contrato y conserva salida dict serializable.
- Se agregaron tests focales de lifecycle.
- Se creó TaskSpec dedicado.
- Se creó checkpoint de cierre.

Validación reportada:

```bash
python -m pytest tests/smartpyme/test_preliminary_taxonomy_lifecycle.py tests/smartpyme/test_anamnesis_fsm_integration.py -q
```

Resultado:

```text
26 passed
1 warning
```

Veredicto:

```text
TD-001 CERRADA técnica y metodológicamente para el alcance PRELIMINARY_TAXONOMY_LIFECYCLE_CONTRACT.
```

---

### TD-002 — Tests architecture / forbidden imports con posible deuda legacy

Clasificación: TEST / CI / ARCHITECTURE
Prioridad: MEDIA
Estado: CERRADA
Bloqueante: NO

Evidencia observada originalmente:

- `tests/architecture/test_forbidden_terms.py` fallaba por referencias legítimas a `orchestration` en tests de integración.
- Codex clasificó el fallo como falso positivo de policy.
- No había evidencia de contaminación arquitectónica nueva en runtime productivo.

Resolución aplicada:

- Se amplió estrictamente `TERM_ALLOWED_PATH_PREFIXES["orchestration"]` sólo con rutas puntuales de tests legítimos.
- No se permitió una carpeta amplia de `tests/smartpyme/`.
- No se tocó runtime.
- No se debilitó el guardrail de imports prohibidos.

Validación reportada:

```bash
python -m pytest tests/architecture -q
```

Resultado:

```text
2 passed, 1 warning in 1.36s
```

Warning:

```text
PytestCacheWarning
```

No bloqueante.

Veredicto:

```text
TD-002 CERRADA.
```

---

### TD-003 — Estado de integración C²I no consolidado como checkpoint propio

Clasificación: DOCUMENTAL / GOVERNANCE
Prioridad: MEDIA
Estado: CERRADA
Bloqueante: NO

Evidencia observada originalmente:

- El estado C²I post-98df386 fue reportado en conversación como favorable.
- Lectura prudente adoptada: INTEGRADO_CONTROLADO, C²I operativo 8.7–8.9.
- Faltaba checkpoint canónico único que consolidara estado, deuda no bloqueante y límites de expansión.

Resolución aplicada:

- Se creó `docs/pymia/POST_C2I_INTEGRATION_CONTROL_CHECKPOINT.md`.
- Se consolidó el estado `INTEGRADO_CONTROLADO`.
- Se registró que no hay bloqueantes conocidos para el flujo integrado actual.
- Se registraron TD-001, TD-002 y TD-003 como cerradas.
- Se preservaron restricciones contra features múltiples y expansión desordenada.

Veredicto:

```text
TD-003 CERRADA.
```

---

### TD-004 — Piloto asistido real aún no ejecutado como validación operativa

Clasificación: OPERATIVA / PRODUCT VALIDATION
Prioridad: MEDIA
Estado: ABIERTA
Bloqueante: NO técnico, SÍ para aprendizaje comercial.

Evidencia observada:

- El flujo integrado está listo para usarse controladamente.
- La deuda operativa no es de código: falta medir un caso real asistido.
- No hay caso real disponible en este momento.

Riesgo:

- Seguir agregando arquitectura sin contraste con dueño PyME real.
- No medir tiempo, fricción, costo humano ni utilidad del OwnerFacingReport.
- Confundir simulación con validación de mercado.

Criterio de cierre:

- Ejecutar `ASSISTED_REAL_PILOT_001` con caso real, sin abrir features nuevas.
- Registrar:
  - tiempo operativo real;
  - fricciones;
  - evidencia faltante;
  - calidad de preguntas;
  - comprensión del dueño;
  - utilidad del reporte;
  - costo operativo humano;
  - blockers.

Nota:

```text
TD-004 no puede cerrarse con simulación.
```

---

### TD-005 — Deuda potencial por documentación histórica abundante

Clasificación: DOCUMENTAL / DRIFT RISK
Prioridad: BAJA-MEDIA
Estado: ABIERTA
Bloqueante: NO.

Evidencia observada:

- El repo contiene documentación heredada, migrada, conceptual y normativa.
- `docs/DOCUMENTATION_INDEX.md` y `docs/DEPRECATED_DOCS.md` existen para gobernar fuente de verdad.
- Riesgo persistente: agentes futuros pueden usar documentos históricos como autorización runtime.

Riesgo:

- Reabrir Hermes, Telegram, ERP, runtime externo, PDF o features no autorizadas por documentación histórica.

Criterio de cierre:

- Auditar si los documentos recientes del hilo post-C²I están indexados correctamente.
- Verificar que documentos históricos sigan marcados como ARCHIVO / DEPRECATED / no autorizantes.
- No modificar contenido doctrinal sin TaskSpec documental específico.

TaskSpec sugerido:

```text
DOCUMENTATION_AUTHORITY_INDEX_RECONCILIATION
```

## 4. Priorización actual

### Cerradas

```text
TD-001 — PRELIMINARY_TAXONOMY_LIFECYCLE_CONTRACT
TD-002 — ARCHITECTURE_TESTS_LEGACY_RECONCILIATION
TD-003 — POST_C2I_INTEGRATION_CONTROL_CHECKPOINT
```

### Abiertas

```text
TD-004 — ASSISTED_REAL_PILOT_001
TD-005 — DOCUMENTATION_AUTHORITY_INDEX_RECONCILIATION
```

## 5. No autorizado por esta auditoría

Esta auditoría NO autoriza:

- Telegram;
- Hermes;
- ERP;
- PDF productivo;
- nuevas fórmulas;
- nuevos reportes;
- runtime externo;
- cambios en graph, bridge o DiagnosticCore sin TaskSpec explícito;
- refactors amplios;
- resolver múltiples TD en un solo patch.

## 6. Próximo paso recomendado

Como no hay caso real disponible, no corresponde cerrar TD-004.

Próximo frente posible:

```text
ASSISTED_SIMULATED_PILOT_001
```

Debe registrarse como simulación, no como validación real de mercado.

Alternativa documental:

```text
TD-005 — DOCUMENTATION_AUTHORITY_INDEX_RECONCILIATION
```

No abrir más de uno a la vez.
