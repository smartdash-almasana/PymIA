# M31 — Servicio asistido repetible Checkpoint

## Estado

CLOSED / PASS

## Contexto

M31 cierra el tramo del roadmap de servicio asistido Excel + semántica PyME.

Base previa:

- M27: mensaje del dueño + Excel controlado -> IntakeRecord -> evidence gate -> READY_FOR_ANALYSIS.
- M28: ActionableFinding[] -> EvidenceItem[] -> NarrativeReport grounded -> markdown legible/auditable.
- M29: owner_message + tenant_id + case_id + evidence_refs + ActionableFinding[] -> Markdown mínimo entregable.
- M30: caso asistido persistido por tenant -> recuperación y evolución del contexto -> aislamiento entre tenants.

M31 no declara producto final, autonomía end-to-end ni servicio comercial validado.

M31 define y valida documentalmente un protocolo operativo para probar repetibilidad asistida en 3 a 5 casos piloto.

## Archivos M31

- docs/roadmap/M31_SERVICIO_ASISTIDO_REPETIBLE_PLAN.md
- docs/smartpyme/M31_SERVICIO_ASISTIDO_REPETIBLE_PROTOCOL.md
- tests/smartpyme/test_m31_service_protocol_docs.py

## Objetivo del slice

Probar repetibilidad operativa asistida, no producto.

El protocolo cubre:

- criterio de entrada;
- criterio de bloqueo;
- checklist de ejecución;
- plantilla de registro de piloto;
- medición de tiempo/costo;
- registro de bloqueos;
- registro de aprendizajes;
- criterio de repetibilidad;
- criterio de no repetibilidad.

## Validación ejecutada localmente

Comando pytest:

```text
python -m pytest tests/smartpyme/test_m31_service_protocol_docs.py -v
```

Resultado pytest exacto:

```text
============================= test session starts =============================
platform win32 -- Python 3.14.0, pytest-9.0.3, pluggy-1.6.0 -- C:\Python314\python.exe
cachedir: .pytest_cache
rootdir: E:\BuenosPasos\smartbridge\PymIA
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: cov-7.1.0, anyio-4.12.1
collecting ... collected 4 items

tests/smartpyme/test_m31_service_protocol_docs.py::test_m31_protocol_document_exists_and_declares_non_product_scope PASSED [ 25%]
tests/smartpyme/test_m31_service_protocol_docs.py::test_m31_protocol_contains_entry_block_delivery_continuity_measurement_and_learning PASSED [ 50%]
tests/smartpyme/test_m31_service_protocol_docs.py::test_m31_protocol_defines_pilot_record_template_and_decision_metrics PASSED [ 75%]
tests/smartpyme/test_m31_service_protocol_docs.py::test_m31_plan_and_protocol_preserve_scope_boundaries PASSED [100%]

============================== 4 passed in 0.73s ==============================
```

Fecha de validación:

```text
2026-06-06 16:07:05 -03:00
```

Referencia operativa:

- `docs/smartpyme/M31P_OPERATIVE_INTERNAL_CHECKPOINT.md`

Notas de cierre:

- M31 certifica protocolo de servicio asistido repetible, no producto, no autonomía.
- M31-P tiene pilotos internos computables.

## Veredicto

M31 CLOSED / PASS.

Certificado por evidencia ejecutada localmente:

1. Los artefactos de M31 son documentales y de prueba de conformidad.
2. Respetan las restricciones operativas del roadmap.
3. No modifican código productivo, dispatcher, registry, UI ni integraciones.
4. El protocolo define servicio asistido repetible y no declara producto autónomo o comercial.
5. El test documental funciona como gate estático de conformidad.
6. Existen pilotos internos computables en `docs/smartpyme/pilots/M31P-002.md`, `docs/smartpyme/pilots/M31P-003.md` y `docs/smartpyme/pilots/M31P-004.md`.

## Riesgo detectado

El test documental usa aserciones de subcadenas literales. Esto blinda el alcance, pero vuelve frágil la prueba ante cambios de redacción que preserven significado.

Decisión: aceptar esa rigidez por ahora para evitar deriva de alcance durante la fase M31.

## Certificado por M31

M31 certifica documentalmente que existe un protocolo repetible para ejecutar pilotos asistidos sin improvisar.

## No certificado por M31

M31 no certifica:

- producto final;
- pricing validado;
- servicio comercial validado;
- casos reales ya ejecutados;
- autonomía end-to-end;
- UI;
- PDF profesional;
- integración con dispatcher;
- integración con ERP;
- automatización comercial.

## Próximo paso sugerido

Cerrar M31 con commit/push.

Luego decidir, fuera de este hito, si se abre una fase de pilotos reales con registro de 3 a 5 casos usando el protocolo M31.
