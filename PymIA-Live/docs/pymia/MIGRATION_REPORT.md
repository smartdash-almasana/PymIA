# Reporte de Migración — PymIA → PymIA-Live

## Datos Generales
- **Fecha:** 2026-06-13
- **Origen:** Repositorio completo PymIA (con frentes históricos, deudas y frentes congelados)
- **Destino:** Repositorio limpio `PymIA-Live` (núcleo mínimo autoportante)

---

## Archivos Copiados
Se extrajo el 100% de la funcionalidad del pipeline ejecutable actual:
- `pymia/cli/vertical_slice.py`
- `pymia/contracts/language_corpus_v1.py`
- `pymia/contracts/language_corpus_seed.json`
- `pymia/contracts/pipeline_run_v1.py`
- `pymia/contracts/evidence_v1.py`
- `pymia/contracts/formula_contract.py`
- `pymia/diagnostic_core/evidence_sufficiency.py`
- `pymia/diagnostic_core/evidence_binding.py` (dependencia de suficiencia)
- `pymia/diagnostic_core/models.py` (modelos de suficiencia)
- `pymia/services/formula_engine_service.py`
- `pymia/smartpyme/evidence.py`
- `pymia/smartpyme/structured_evidence_builder.py`
- `pymia/smartpyme/owner_facing_report.py`
- `pymia/audit_result/evidence_requirement_matcher.py`
- `tools/document_ingestion.py`
- Paquete completo `tools/bem_schema_builder/`
- `tests/contracts/test_language_corpus_v1.py`
- `tests/e2e/test_vertical_slice_cli.py`
- `prueba_excels/la_textil_cosida_srl_mar_abr_may_2026.xlsx`
- `prueba_excels/cafeteria_abc.xlsx`
- `docs/ops/RUNBOOK_PILOTO_ASISTIDO_POST_LC.md`
- `docs/pymia/PYMIA_LIVE_CORE_MANIFEST.md`
- `docs/pymia/PYMIA_LIVE_PIPELINE.md`

---

## Archivos Reemplazados
- `pymia/smartpyme/storage.py` (reemplazado por un adaptador mínimo autoportante).

---

## Adaptadores Creados
- **`pymia/smartpyme/storage.py`**: Versión minimalista del storage que corta de raíz la dependencia heredada con `pymia/smartpyme/intake.py` y `pymia/smartpyme/reception.py`. Contiene exclusivamente las funciones `_safe_join()`, `ensure_tenant_storage()`, `_write_jsonl_line()` y `save_evidence_record()`.
- **Paquetización de tests y herramientas:** Creación de archivos `__init__.py` en directorios clave (`tests/`, `tests/contracts/`, `tests/e2e/`, `tools/`) para permitir que Python los reconozca y valide de forma estática absoluta en el nuevo alcance.

---

## Dependencias Eliminadas (Museo Histórico / Congelados)
- **FastAPI / Server:** Se eliminó toda la superficie web y los endpoints de API.
- **Telegram / Hermes / conversa-engine:** Eliminación completa de canales y motores conversacionales deprecados.
- **Orquestación antigua:** Eliminación de lógica redundante de agentes, LangGraph y prompts de LLMs antiguos.
- **Checkpoints y Documentación Inactiva:** Se excluyeron del copiado más de 150 archivos de checkpoints antiguos (`M34_S2`... `M66`), TaskSpecs redundantes y borradores de arquitectura obsoletos.

---

## Resultados del Smoke Test
El núcleo ejecutable fue verificado con éxito y arroja los siguientes resultados conformes a las invariantes clínicas del proyecto:
- **Estado de salida:** `DELIVERED_CANDIDATE` (cuando no hay bloqueos de columnas operativas).
- **Invariantes de auditoría:** Generación automática de `Evidence ID`, `Run ID` y `Output Hash` consistentes en el archivo `pipeline_runs.jsonl`.
- **Formato clínico:** Generación de markdown owner-facing con nombres legibles del Language Corpus (e.g. `ventas brutas (ventas_total)`) sin frotar diagnósticos prematuros.
- **Volumen verificado:** 5 variables computadas y 8 tablas estructuradas identificadas y validadas con éxito sobre el set de prueba textil.

---

## Riesgos Conocidos
- **Desincronización del manifiesto:** Si futuros desarrollos agregan nuevos archivos de código o tests y no actualizan `PYMIA_LIVE_CORE_MANIFEST.md` ni `PYMIA_LIVE_PIPELINE.md`, la higiene documental obtenida se degradará rápidamente.
- **Implementación sin diseño (QuestionAlignmentGate):** Que al tener disponible el contrato conceptual mínimo para la alineación conversacional, se proceda a escribir código en `vertical_slice.py` sin haber validado formalmente su `CapabilitySpec` y `ModuleContract`.
