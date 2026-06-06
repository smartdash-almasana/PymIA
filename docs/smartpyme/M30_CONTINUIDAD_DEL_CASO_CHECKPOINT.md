# M30 — Continuidad del caso Checkpoint

## Estado

CLOSED / PASS

## Contexto

M30 continúa el roadmap de servicio asistido Excel + semántica PyME.

M27 cerró el puente: mensaje del dueño + Excel controlado -> IntakeRecord -> evidence gate -> READY_FOR_ANALYSIS.

M28 cerró el puente: ActionableFinding[] -> EvidenceItem[] -> NarrativeReport grounded -> markdown legible/auditable.

M29 cerró el puente: owner_message + tenant_id + case_id + evidence_refs + ActionableFinding[] -> Markdown mínimo entregable.

M30 demuestra continuidad mínima del caso asistido por tenant usando contratos existentes de orquestación y storage.

No declara producto final, autonomía end-to-end ni servicio comercial validado.

## Archivos creados

- docs/roadmap/M30_CONTINUIDAD_DEL_CASO_PLAN.md
- tests/orchestration/test_m30_case_continuity_acceptance.py

## Objetivo del slice

Demostrar que un caso asistido puede persistir y recuperarse sin reiniciar desde cero, conservando:

- dolor inicial;
- evidencia usada;
- hallazgos generados;
- reporte mínimo o referencia de reporte;
- próximo paso sugerido;
- estado del caso;
- aislamiento entre tenants.

## Contratos usados

- pymia.orchestration.state.PymIAState
- pymia.orchestration.state_storage.save_state
- pymia.orchestration.state_storage.load_state
- pymia.orchestration.state_storage.find_conversations_by_tenant

No se modificó producción.
No se tocó dispatcher, registry, plugins, Telegram, PDF, HTML, UI, CI, ERP, red ni LLM.

## Validación ejecutada localmente

Comando focal:

```text
python -m pytest tests/orchestration/test_m30_case_continuity_acceptance.py -v
```

Resultado focal exacto:

```text
============================= test session starts =============================
platform win32 -- Python 3.14.0, pytest-9.0.3, pluggy-1.6.0 -- C:\Python314\python.exe
cachedir: .pytest_cache
rootdir: E:\BuenosPasos\smartbridge\PymIA
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: cov-7.1.0, anyio-4.12.1
collecting ... collected 1 item

tests/orchestration/test_m30_case_continuity_acceptance.py::test_m30_case_continuity_acceptance PASSED [100%]

============================= 1 passed in 23.55s ==============================
```

Comando de continuidad combinada:

```text
python -m pytest tests/orchestration/test_tenant_continuity_acceptance.py tests/orchestration/test_m30_case_continuity_acceptance.py -v
```

Resultado combinado exacto:

```text
============================= test session starts =============================
platform win32 -- Python 3.14.0, pytest-9.0.3, pluggy-1.6.0 -- C:\Python314\python.exe
cachedir: .pytest_cache
rootdir: E:\BuenosPasos\smartbridge\PymIA
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: cov-7.1.0, anyio-4.12.1
collecting ... collected 2 items

tests/orchestration/test_tenant_continuity_acceptance.py::test_tenant_continuity_acceptance PASSED [ 50%]
tests/orchestration/test_m30_case_continuity_acceptance.py::test_m30_case_continuity_acceptance PASSED [100%]

============================= 2 passed in 12.13s ==============================
```

Comando storage/state:

```text
python -m pytest tests/orchestration/test_state_storage.py tests/orchestration/test_state.py -v
```

Resultado storage/state exacto:

```text
============================= test session starts =============================
platform win32 -- Python 3.14.0, pytest-9.0.3, pluggy-1.6.0 -- C:\Python314\python.exe
cachedir: .pytest_cache
rootdir: E:\BuenosPasos\smartbridge\PymIA
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: cov-7.1.0, anyio-4.12.1
collecting ... collected 30 items

tests/orchestration/test_state_storage.py::test_save_state_creates_file PASSED [  3%]
tests/orchestration/test_state_storage.py::test_save_state_appends PASSED [  6%]
tests/orchestration/test_state_storage.py::test_load_state_returns_latest PASSED [ 10%]
tests/orchestration/test_state_storage.py::test_load_state_returns_none_if_not_found PASSED [ 13%]
tests/orchestration/test_state_storage.py::test_load_state_filters_by_chat_id PASSED [ 16%]
tests/orchestration/test_state_storage.py::test_save_state_preserves_decision_trail PASSED [ 20%]
tests/orchestration/test_state_storage.py::test_save_state_preserves_evidence_path PASSED [ 23%]
tests/orchestration/test_state_storage.py::test_replay_conversation_returns_latest PASSED [ 26%]
tests/orchestration/test_state_storage.py::test_get_conversation_history_sorted_and_filtered PASSED [ 30%]
tests/orchestration/test_state_storage.py::test_find_conversations_by_tenant_groups_by_conversation PASSED [ 33%]
tests/orchestration/test_state_storage.py::test_export_conversation_jsonl_exports_filtered_history PASSED [ 36%]
tests/orchestration/test_state_storage.py::test_conversation_queries_return_empty_when_storage_missing PASSED [ 40%]
tests/orchestration/test_state_storage.py::test_get_conversation_history_raises_on_corrupt_jsonl PASSED [ 43%]
tests/orchestration/test_state_storage.py::test_save_load_preserves_delivery_serializable_fields PASSED [ 46%]
tests/orchestration/test_state_storage.py::test_load_state_supports_legacy_jsonl_missing_delivery_fields PASSED [ 50%]
tests/orchestration/test_state_storage.py::test_replay_conversation_recovers_delivered_fields PASSED [ 53%]
tests/orchestration/test_state_storage.py::test_export_conversation_jsonl_includes_delivery_summary PASSED [ 56%]
tests/orchestration/test_state_storage.py::test_save_load_preserves_progressive_context PASSED [ 60%]
tests/orchestration/test_state_storage.py::test_load_state_legacy_without_progressive_context_defaults_empty_dict PASSED [ 63%]
tests/orchestration/test_state_storage.py::test_replay_conversation_preserves_progressive_context PASSED [ 66%]
tests/orchestration/test_state_storage.py::test_export_conversation_jsonl_includes_progressive_context PASSED [ 70%]
tests/orchestration/test_state.py::test_pymia_state_creation PASSED      [ 73%]
tests/orchestration/test_state.py::test_pymia_state_progressive_context_default_is_empty_dict PASSED [ 76%]
tests/orchestration/test_state.py::test_pymia_state_add_decision PASSED  [ 80%]
tests/orchestration/test_state.py::test_pymia_state_add_error PASSED     [ 83%]
tests/orchestration/test_state.py::test_pymia_event_creation_text_message PASSED [ 86%]
tests/orchestration/test_state.py::test_pymia_event_creation_document_received PASSED [ 90%]
tests/orchestration/test_state.py::test_pymia_state_with_evidence PASSED [ 93%]
tests/orchestration/test_state.py::test_pymia_state_serialization_roundtrip PASSED [ 96%]
tests/orchestration/test_state.py::test_state_source_does_not_reintroduce_complex_delivery_fields PASSED [100%]

============================= 30 passed in 24.48s =============================
```

Fecha de validación:

```text
2026-06-06 15:50:16 -03:00
```

Nota de cierre:

```text
M30 certifica continuidad mínima por tenant/caso sin CRM, sin Supermemory obligatorio, sin memoria avanzada.
```

## Veredicto

M30 CLOSED / PASS.

Certificado por evidencia ejecutada localmente:

caso asistido tenant_a -> persistencia de contexto útil -> tenant_b independiente -> tenant_a vuelve -> recuperación y evolución del caso -> aislamiento entre tenants.

No certificado:

- producto final;
- servicio comercial validado;
- diagnóstico integral;
- flujo con dispatcher;
- casos reales de cliente;
- automatización end-to-end.

## Próximo hito sugerido

Según el roadmap vigente, el siguiente hito natural es M31 — Servicio asistido repetible.

Antes de abrir M31, cerrar M30 con commit/push y dejar repo limpio.
