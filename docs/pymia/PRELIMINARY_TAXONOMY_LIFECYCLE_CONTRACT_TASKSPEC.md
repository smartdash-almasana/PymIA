# PRELIMINARY_TAXONOMY_LIFECYCLE_CONTRACT — TaskSpec

Fecha: 2026-06-10
Estado: CLOSED
Tipo: TaskSpec técnico-contractual
Frente: TD-001 — Lifecycle de `preliminary_taxonomy`

## 1. Objetivo

Formalizar el lifecycle mínimo de `preliminary_taxonomy` como contrato explícito, sin cambiar el comportamiento externo del flujo integrado.

El objetivo específico es cerrar la ambigüedad técnica donde `preliminary_taxonomy` existía como `dict` auxiliar no confirmado, pero sin contrato propio de estado y validación.

## 2. Alcance autorizado

Archivos permitidos:

```text
pymia/smartpyme/preliminary_taxonomy.py
pymia/smartpyme/anamnesis_fsm.py
tests/smartpyme/test_preliminary_taxonomy_lifecycle.py
docs/pymia/DEUDA_TECNICA.md
docs/pymia/PRELIMINARY_TAXONOMY_LIFECYCLE_CONTRACT_TASKSPEC.md
docs/pymia/PRELIMINARY_TAXONOMY_LIFECYCLE_CONTRACT_CHECKPOINT.md
```

## 3. Fuera de alcance

Este TaskSpec no autoriza:

- cambios en `graph.py`;
- cambios en `core_delivery_bridge.py`;
- cambios en DiagnosticCore;
- cambios en OwnerFacingReport;
- cambios en owner-answer reentry;
- Telegram;
- Hermes;
- ERP;
- PDF productivo;
- nuevas fórmulas;
- nuevos reportes;
- runtime externo;
- refactor amplio del FSM.

## 4. Contrato requerido

Crear o preservar un contrato mínimo con:

```text
PreliminaryTaxonomyStatus:
- PRELIMINARY
- CONFIRMED
- REJECTED
- SUPERSEDED
```

Y una señal serializable:

```text
PreliminaryTaxonomySignal:
- tenant_id
- source
- status
- organism_type
- sales_channels
- confidence
- created_from
```

## 5. Reglas obligatorias

- `preliminary_taxonomy` es señal auxiliar no confirmada.
- `PRELIMINARY` no equivale a taxonomía confirmada.
- `PRELIMINARY` no habilita hipótesis.
- `PRELIMINARY` no habilita `evidence_requests`.
- `PRELIMINARY` no habilita diagnóstico.
- `PRELIMINARY` no habilita ejecución.
- `PRELIMINARY` no salta ficha.
- `has_taxonomy` significa taxonomía confirmada.
- `has_confirmed_taxonomy` significa taxonomía confirmada.
- `has_preliminary_taxonomy` sólo indica existencia de señal auxiliar.
- La ficha inicial sigue obligatoria.
- `profile_step` inicial sigue siendo `ASK_CONTACT_NAME`.
- `raw_first_message` se preserva.

## 6. Validaciones esperadas

La implementación debe probar:

- construcción válida de señal `PRELIMINARY`;
- `to_dict()` serializable;
- campos obligatorios fail-closed;
- `PRELIMINARY` exige `confidence < 1.0`;
- mensaje fuerte como `fabrico ropa y vendo por mayor` genera señal preliminar;
- mensaje ambiguo como `hola` no genera señal;
- señal preliminar no activa `has_taxonomy`;
- señal preliminar no activa hipótesis;
- señal preliminar no activa `evidence_requests`.

## 7. Comandos de validación

```bash
python -m pytest tests/smartpyme/test_preliminary_taxonomy_lifecycle.py tests/smartpyme/test_anamnesis_fsm_integration.py -q
```

Resultado certificado por ejecución local:

```text
26 passed
1 warning
```

Warning observado: `PytestCacheWarning` al crear `.pytest_cache`; no bloquea la suite.

## 8. Criterio de cierre

Este TaskSpec queda cerrado si:

- existe contrato explícito para lifecycle de taxonomía preliminar;
- `_build_preliminary_taxonomy_signal()` usa el contrato;
- el output serializado mantiene compatibilidad;
- los tests focales y de anamnesis pasan;
- no se modifican fronteras prohibidas.

## 9. Resultado

Estado: CLOSED

TD-001 queda cerrada técnica y metodológicamente para el alcance de lifecycle mínimo.
