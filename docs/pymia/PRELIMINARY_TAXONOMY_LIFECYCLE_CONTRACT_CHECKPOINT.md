# PRELIMINARY_TAXONOMY_LIFECYCLE_CONTRACT — Checkpoint

Fecha: 2026-06-10
Estado: CLOSED
Frente: TD-001 — Lifecycle de `preliminary_taxonomy`

## 1. Veredicto

TD-001 queda cerrada en el alcance técnico y metodológico del lifecycle mínimo.

La deuda original era:

```text
preliminary_taxonomy existe como señal auxiliar no confirmada,
pero no tiene contrato/lifecycle propio.
```

Resultado:

```text
RESUELTA
```

## 2. Archivos modificados / creados

Código:

```text
pymia/smartpyme/preliminary_taxonomy.py
pymia/smartpyme/anamnesis_fsm.py
```

Tests:

```text
tests/smartpyme/test_preliminary_taxonomy_lifecycle.py
```

Documentación:

```text
docs/pymia/DEUDA_TECNICA.md
docs/pymia/PRELIMINARY_TAXONOMY_LIFECYCLE_CONTRACT_TASKSPEC.md
docs/pymia/PRELIMINARY_TAXONOMY_LIFECYCLE_CONTRACT_CHECKPOINT.md
```

## 3. Contrato implementado

Se formalizó el lifecycle mínimo mediante:

```text
PreliminaryTaxonomyStatus
PreliminaryTaxonomySignal
```

Estados reconocidos:

```text
PRELIMINARY
CONFIRMED
REJECTED
SUPERSEDED
```

## 4. Semántica preservada

La señal preliminar conserva su función estricta:

```text
señal auxiliar no confirmada derivada del raw_first_message
```

No cambia el contrato operativo vigente:

- no confirma taxonomía;
- no habilita hipótesis;
- no habilita evidence_requests;
- no habilita diagnóstico;
- no habilita ejecución;
- no salta ficha;
- no modifica owner-answer reentry;
- no modifica bridge;
- no modifica DiagnosticCore;
- no modifica OwnerFacingReport.

## 5. Regla de flags preservada

```text
has_preliminary_taxonomy = existe señal auxiliar preliminar
has_taxonomy = existe taxonomía confirmada
has_confirmed_taxonomy = alias explícito de taxonomía confirmada
```

Por contrato:

```text
PRELIMINARY nunca puede producir has_taxonomy == True
```

## 6. Validación ejecutada

Comando reportado:

```bash
python -m pytest tests/smartpyme/test_preliminary_taxonomy_lifecycle.py tests/smartpyme/test_anamnesis_fsm_integration.py -q
```

Resultado:

```text
26 passed
1 warning
```

Warning:

```text
PytestCacheWarning al crear .pytest_cache
```

No bloqueante.

## 7. Evidencia funcional certificada

Queda certificado que:

- mensaje fuerte como `fabrico ropa y vendo por mayor` genera `PRELIMINARY`;
- mensaje ambiguo como `hola` no genera señal preliminar;
- `PRELIMINARY` no activa `has_taxonomy`;
- `PRELIMINARY` no activa `has_confirmed_taxonomy`;
- `PRELIMINARY` no activa hipótesis;
- `PRELIMINARY` no activa `evidence_requests`;
- la ficha inicial sigue en `FICHA_PYME_INICIAL`;
- `profile_step` sigue en `ASK_CONTACT_NAME` en primer contacto;
- el output sigue siendo serializable.

## 8. Deuda cerrada

```text
TD-001 — Lifecycle de preliminary_taxonomy no formalizado
```

Estado:

```text
CERRADA
```

## 9. Deuda remanente

No queda deuda remanente para el lifecycle mínimo de `preliminary_taxonomy`.

Persisten fuera de este frente:

```text
TD-002 — Tests architecture / forbidden imports con posible deuda legacy
TD-003 — Estado de integración C²I no consolidado como checkpoint propio
TD-004 — Piloto asistido real aún no ejecutado como validación operativa
TD-005 — Riesgo de deriva por documentación histórica abundante
```

## 10. Cierre

El frente queda cerrado sin abrir features nuevas y sin modificar fronteras soberanas del flujo integrado.

Próximo frente permitido sólo por decisión explícita del owner.
