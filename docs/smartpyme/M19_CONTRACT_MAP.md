# M19 — Contract Map

Fecha: 2026-06-02  
Estado: auditoría automática dirigida (M19.1)  
Alcance: pipeline determinístico central SmartPyme, sin bordes externos.

---

## Phase: intake

- **File:** `pymia/smartpyme/intake.py`
- **Function:** `create_intake_record`
- **Input:**
  - `tenant_id: str` (obligatorio, no vacío)
  - `raw_text: str` (obligatorio, no vacío)
  - `structured_selectors: StructuredSelectors | None` (opcional)
- **Output:** `IntakeRecord` (dataclass serializable con `to_dict()`)
- **States (intake_state):**
  - `RECEIVED`
  - `INTERROGATED`
  - `TANKS_SELECTED`
  - `NEEDS_EVIDENCE`
  - `READY_FOR_ANALYSIS`
  - `BLOCKED`
  - `UNSUPPORTED`
- **Evidence request states (IntakeEvidenceRequest.status):**
  - `REQUESTED`
  - `RECEIVED`
  - `SATISFIED`
  - `WAIVED`
  - `BLOCKED`
- **Errors/Blocks:**
  - `ValueError` si `tenant_id` o `raw_text` están vacíos.
  - `INTAKE_BLOCKED` si `interrogation.status == STATUS_BLOCKED_INSUFFICIENT_CONTEXT`.
  - `INTAKE_BLOCKED` si `tank_selection.suggested_next_state == NEXT_BLOCKED`.
  - Fail-closed: si `suggested_next_state` no coincide con estados conocidos, retorna `INTAKE_BLOCKED`.
- **Integration notes for runner:**
  - Ejecuta internamente `run_interrogation` y `select_tanks`.
  - Genera `IntakeEvidenceRequest` con estado `REQUESTED`.
  - El runner debe capturar `intake_id`, `tenant_id`, `intake_state`, `evidence_requests` y `suggested_next_state` para la traza.
  - No ejecuta análisis ni lee archivos.

---

## Phase: evidence_requirement

- **File:** `pymia/smartpyme/evidence_requirement.py`
- **Function:** `create_evidence_requirement`
- **Input:**
  - `requirement_id: str`
  - `tenant_id: str`
  - `intake_id: str`
  - `hypothesis_id: str`
  - `evidence_type: str`
  - `description: str`
  - `required_fields: list[str]`
  - `reason: str`
  - `blocks_analysis: bool`
  - `priority: int` (1-3)
  - `telegram_message: str`
  - `enables_classification: str | None`
  - `source_tank: str | None`
  - `formula_id: str | None`
  - `formula_ids: list[str] | None`
- **Output:** `EvidenceRequirement` (dataclass serializable con `to_dict()`)
- **States:** No tiene estados propios. Es un contrato puro de metadata.
- **Errors/Blocks:**
  - `ValueError` si campos de texto obligatorios están vacíos.
  - `ValueError` si `required_fields` no es lista.
  - `ValueError` si `priority` no es int entre 1 y 3.
- **Integration notes for runner:**
  - Módulo de contrato puro. No persiste ni ejecuta acciones runtime.
  - El runner puede usarlo para validar que los `IntakeEvidenceRequest` tengan los campos mínimos antes de registrar evidencia.
  - No es estrictamente necesario en el flujo mínimo si el runner usa directamente `IntakeEvidenceRequest` del `IntakeRecord`.

---

## Phase: evidence

- **File:** `pymia/smartpyme/evidence.py`
- **Function:** `create_evidence_record`
- **Input:**
  - `tenant_id: str` (obligatorio)
  - `intake_id: str` (obligatorio)
  - `evidence_type: str` (obligatorio)
  - `source_kind: str` (obligatorio, uno de `ALLOWED_SOURCE_KINDS`)
  - `source_ref: str` (obligatorio)
  - `request_id: str | None`
  - `original_filename: str | None`
  - `mime_type: str | None`
  - `size_bytes: int | None`
  - `content_hash: str | None`
  - `status: str` (default: `RECEIVED`)
  - `notes: list[str] | None`
  - `metadata: dict[str, Any] | None`
- **Output:** `EvidenceRecord` (dataclass serializable con `to_dict()`)
- **States (status):**
  - `RECEIVED`
  - `REGISTERED`
  - `REJECTED`
  - `LINKED`
  - `SUPERSEDED`
- **Source kinds (source_kind):**
  - `uploaded_file`
  - `manual_text`
  - `external_ref`
  - `generated`
  - `unknown`
- **Errors/Blocks:**
  - `ValueError` si campos obligatorios están vacíos.
  - `ValueError` si `source_kind` o `status` no están en las listas permitidas.
  - `ValueError` si `size_bytes` es negativo.
- **Integration notes for runner:**
  - Registra metadata de evidencia recibida. No lee archivos ni calcula hashes.
  - El runner debe crear un `EvidenceRecord` por cada archivo de evidencia del escenario.
  - Para el happy path Excel, usar `source_kind="uploaded_file"` y `source_ref` apuntando al fixture.
  - El `evidence_id` se genera automáticamente con UUID.

---

## Phase: evidence_gate

- **File:** `pymia/smartpyme/evidence_gate.py`
- **Function:** `evaluate_evidence_sufficiency`
- **Input:**
  - `intake_record: IntakeRecord | dict` (debe contener `tenant_id`, `intake_id`, `evidence_requests`)
  - `evidence_records: list[EvidenceRecord | dict]`
- **Output:** `EvidenceSufficiencyResult` (dataclass serializable con `to_dict()`)
- **States (status):**
  - `READY`
  - `NEEDS_MORE_EVIDENCE`
  - `BLOCKED`
  - `UNSUPPORTED`
- **Assessment statuses (EvidenceRequestAssessment.status):**
  - `SATISFIED`
  - `MISSING`
  - `PARTIAL`
  - `WAIVED`
  - `BLOCKED`
- **Suggested next states:**
  - `READY_FOR_ANALYSIS`
  - `NEEDS_EVIDENCE`
  - `BLOCKED`
  - `UNSUPPORTED`
- **Errors/Blocks:**
  - `ValueError` si `evidence_records` no es lista.
  - `ValueError` si `intake_record` falta `tenant_id`, `intake_id` o `evidence_requests`.
  - `ValueError` si algún `evidence_record` falta `tenant_id`, `intake_id`, `evidence_id`, `evidence_type` o `status`.
  - Short-circuit: si `intake_state == "BLOCKED"`, retorna `SUFFICIENCY_BLOCKED` inmediatamente.
- **Integration notes for runner:**
  - Evalúa si los `EvidenceRecord` satisfacen los `IntakeEvidenceRequest` del `IntakeRecord`.
  - Match fuerte por `request_id`; fallback por `evidence_type`.
  - Solo acepta evidencia con status `RECEIVED`, `REGISTERED` o `LINKED`.
  - Verifica `required_fields` contra `metadata` de la evidencia.
  - El runner debe capturar `status`, `suggested_next_state`, `matched_evidence_ids`, `missing_request_ids` y `blocking_request_ids` para la traza.

---

## Phase: readiness

- **File:** `pymia/smartpyme/readiness.py`
- **Function:** `evaluate_analysis_readiness`
- **Input:**
  - `intake_record: IntakeRecord | dict` (debe contener `tenant_id`, `intake_id`)
  - `sufficiency_result: EvidenceSufficiencyResult | dict` (debe contener `tenant_id`, `intake_id`, `status`)
- **Output:** `AnalysisReadinessResult` (dataclass serializable con `to_dict()`)
- **States (status):**
  - `READY_FOR_ANALYSIS`
  - `NEEDS_EVIDENCE`
  - `BLOCKED`
  - `UNSUPPORTED`
- **Runtime classifications:**
  - `excel_diagnostic`
  - `supplier_duplicate_check`
- **Errors/Blocks:**
  - `ValueError` si falta `tenant_id` o `intake_id` en inputs.
  - `ValueError` si `sufficiency_result.status` no es reconocido.
  - `ValueError` si `tenant_id` o `intake_id` no coinciden entre intake y sufficiency.
  - Short-circuit: si `intake_state == "BLOCKED"`, retorna `READINESS_BLOCKED`.
  - Short-circuit: si `sufficiency_result.status == "BLOCKED"`, retorna `READINESS_BLOCKED`.
  - Short-circuit: si `sufficiency_result.status == "NEEDS_MORE_EVIDENCE"`, retorna `READINESS_NEEDS_EVIDENCE`.
  - Si `sufficiency_result.status == "READY"` pero no se puede resolver `runtime_classification`, retorna `READINESS_UNSUPPORTED`.
- **Integration notes for runner:**
  - Decide si el intake está listo para análisis y qué clasificación runtime aplica.
  - Regla de clasificación conservadora: si solo `excel_diagnostic` está habilitado, retorna `excel_diagnostic`. Si hay ambigüedad (ambas habilitadas), intenta desempatar por `tank_selection_result.selected_tanks`.
  - El runner debe capturar `status`, `runtime_classification`, `can_execute`, `blocking_reasons` y `matched_evidence_ids` para la traza.
  - Solo si `status == READY_FOR_ANALYSIS` y `can_execute == True`, el pipeline puede continuar a `runtime_bridge`.

---

## Phase: runtime_bridge

- **File:** `pymia/smartpyme/runtime_bridge.py`
- **Function:** `prepare_runtime_execution`
- **Input:**
  - `readiness_result: AnalysisReadinessResult | dict` (debe contener `tenant_id`, `intake_id`, `status`, `can_execute`, `runtime_classification`)
- **Output:** `RuntimeExecutionCandidate` (dataclass serializable con `to_dict()`)
- **States (status):**
  - `READY_TO_EXECUTE`
  - `BLOCKED`
  - `UNSUPPORTED`
- **Microservice map:**
  - `excel_diagnostic` → `excel_diagnostic_worker`
  - `supplier_duplicate_check` → `supplier_duplicate_check_worker`
- **Errors/Blocks:**
  - `ValueError` si falta `tenant_id`, `intake_id`, `status` o `can_execute`.
  - Si `status != READY_FOR_ANALYSIS`, retorna `EXECUTION_BLOCKED`.
  - Si `can_execute == False`, retorna `EXECUTION_BLOCKED`.
  - Si `runtime_classification` está vacío, retorna `EXECUTION_BLOCKED`.
  - Si `runtime_classification` no está en `ALLOWED_RUNTIME_CLASSIFICATIONS`, retorna `EXECUTION_UNSUPPORTED`.
- **Integration notes for runner:**
  - Traduce el `AnalysisReadinessResult` en un candidato seguro para despachar.
  - El runner debe capturar `status`, `runtime_classification`, `microservice_name`, `evidence_ids`, `can_dispatch` y `blocking_reasons` para la traza.
  - Solo si `status == READY_TO_EXECUTE` y `can_dispatch == True`, el pipeline puede continuar a `microservice_dispatcher`.

---

## Phase: microservice_dispatcher

- **File:** `pymia/smartpyme/microservice_dispatcher.py`
- **Function:** `dispatch_candidate`
- **Input:**
  - `candidate: RuntimeExecutionCandidate | dict` (debe contener `tenant_id`, `intake_id`, `runtime_classification`, `microservice_name`, `status`, `can_dispatch`)
  - `evidence_path: str | Path` (ruta al archivo de evidencia, ej. Excel)
  - `output_dir: str | Path | None` (directorio de salida opcional)
- **Output:** `MicroserviceExecutionResult` (dataclass serializable con `to_dict()`)
- **States (status):**
  - `EXECUTED`
  - `BLOCKED`
  - `UNSUPPORTED`
  - `FAILED`
- **Errors/Blocks:**
  - Si `candidate.status != EXECUTION_READY_TO_EXECUTE`, retorna `EXECUTION_BLOCKED`.
  - Si `candidate.can_dispatch == False`, retorna `EXECUTION_BLOCKED`.
  - Si `runtime_classification != "excel_diagnostic"`, retorna `EXECUTION_UNSUPPORTED` (actualmente solo soporta `excel_diagnostic`).
  - Si `diagnose_excel` lanza excepción, retorna `EXECUTION_FAILED` con el error en `warnings` y `raw_result`.
- **Integration notes for runner:**
  - Ejecuta el plugin real (`diagnose_excel` para `excel_diagnostic`).
  - Genera `output_refs` si se proporciona `output_dir` (ej. `diagnostic_report.md`).
  - El runner debe capturar `status`, `output_refs`, `findings_count`, `raw_result` y `warnings` para la traza.
  - Para el happy path Excel, el runner debe pasar la ruta del fixture Excel en `evidence_path`.

---

## Phase: execution_result_gate

- **File:** `pymia/smartpyme/execution_result_gate.py`
- **Function:** `validate_execution_result`
- **Input:**
  - `result: MicroserviceExecutionResult | dict` (debe contener `status`, `tenant_id`, `intake_id`, `runtime_classification`, `output_refs`, `findings_count`, `raw_result`)
- **Output:** `ExecutionResultGateVerdict` (dataclass serializable con `to_dict()`)
- **States (verdict):**
  - `PASS`
  - `BLOCKED`
  - `FAILED`
  - `UNDELIVERABLE`
- **Errors/Blocks:**
  - Si `status == "BLOCKED"`, retorna `VERDICT_BLOCKED`.
  - Si `status == "FAILED"`, retorna `VERDICT_FAILED`.
  - Si `status == "UNSUPPORTED"`, retorna `VERDICT_BLOCKED`.
  - Si `status != "EXECUTED"`, retorna `VERDICT_UNDELIVERABLE`.
  - Si `status == "EXECUTED"` pero:
    - `tenant_id`, `intake_id` o `runtime_classification` están vacíos → `VERDICT_UNDELIVERABLE`.
    - `output_refs` está vacío o contiene rutas vacías → `VERDICT_UNDELIVERABLE`.
    - `output_refs` contiene rutas que no existen en el sistema de archivos → `VERDICT_UNDELIVERABLE`.
    - `findings_count` no es entero o es negativo → `VERDICT_UNDELIVERABLE`.
    - `raw_result` está vacío o no es serializable a JSON → `VERDICT_UNDELIVERABLE`.
- **Integration notes for runner:**
  - Valida que el resultado de ejecución sea deliverable.
  - El runner debe capturar `verdict`, `reasons` y `warnings` para la traza.
  - Solo si `verdict == "PASS"`, el pipeline puede continuar a `delivery_package` con estado `READY_TO_DELIVER`.
  - **Nota crítica:** El gate verifica que las rutas en `output_refs` existan físicamente. El runner debe asegurar que `microservice_dispatcher` haya generado los archivos de salida.

---

## Phase: delivery_package

- **File:** `pymia/smartpyme/delivery_package.py`
- **Function:** `build_delivery_package`
- **Input:**
  - `result: MicroserviceExecutionResult | dict` (debe contener `tenant_id`, `intake_id`, `runtime_classification`, `output_refs`, `warnings`)
  - `verdict: ExecutionResultGateVerdict | dict` (debe contener `verdict`, `reasons`, `warnings`)
- **Output:** `DeliveryPackage` (dataclass serializable con `to_dict()`)
- **States (status):**
  - `READY_TO_DELIVER`
  - `BLOCKED`
  - `FAILED`
- **Errors/Blocks:**
  - `ValueError` si `result` falta `tenant_id`, `intake_id`, `runtime_classification` o `output_refs`.
  - `ValueError` si `result.output_refs` no es lista.
  - `ValueError` si `verdict` falta `verdict`.
  - `ValueError` si `verdict.verdict` no es `PASS`, `BLOCKED`, `FAILED` o `UNDELIVERABLE`.
- **Integration notes for runner:**
  - Construye el paquete final para el tenant.
  - Si `verdict == "PASS"`, `status = READY_TO_DELIVER`.
  - Si `verdict == "BLOCKED"`, `status = BLOCKED`.
  - Si `verdict == "FAILED"` o `verdict == "UNDELIVERABLE"`, `status = FAILED`.
  - El runner debe capturar `status`, `output_refs`, `summary`, `gate_verdict`, `warnings` y `reasons` para la traza.
  - Este es el último paso del pipeline determinístico central.

---

## Resumen de estados del pipeline

| Fase | Estados posibles |
|---|---|
| intake | RECEIVED, INTERROGATED, TANKS_SELECTED, NEEDS_EVIDENCE, READY_FOR_ANALYSIS, BLOCKED, UNSUPPORTED |
| evidence | RECEIVED, REGISTERED, REJECTED, LINKED, SUPERSEDED |
| evidence_gate | READY, NEEDS_MORE_EVIDENCE, BLOCKED, UNSUPPORTED |
| readiness | READY_FOR_ANALYSIS, NEEDS_EVIDENCE, BLOCKED, UNSUPPORTED |
| runtime_bridge | READY_TO_EXECUTE, BLOCKED, UNSUPPORTED |
| microservice_dispatcher | EXECUTED, BLOCKED, UNSUPPORTED, FAILED |
| execution_result_gate | PASS, BLOCKED, FAILED, UNDELIVERABLE |
| delivery_package | READY_TO_DELIVER, BLOCKED, FAILED |

---

## Flujo mínimo happy path (excel_diagnostic)

```text
1. create_intake_record(tenant_id, raw_text) → IntakeRecord (intake_state=NEEDS_EVIDENCE o READY_FOR_ANALYSIS)
2. create_evidence_record(tenant_id, intake_id, evidence_type, source_kind="uploaded_file", source_ref=excel_path) → EvidenceRecord
3. evaluate_evidence_sufficiency(intake_record, [evidence_record]) → EvidenceSufficiencyResult (status=READY)
4. evaluate_analysis_readiness(intake_record, sufficiency_result) → AnalysisReadinessResult (status=READY_FOR_ANALYSIS, runtime_classification=excel_diagnostic)
5. prepare_runtime_execution(readiness_result) → RuntimeExecutionCandidate (status=READY_TO_EXECUTE)
6. dispatch_candidate(candidate, evidence_path=excel_path, output_dir=output_dir) → MicroserviceExecutionResult (status=EXECUTED)
7. validate_execution_result(execution_result) → ExecutionResultGateVerdict (verdict=PASS)
8. build_delivery_package(execution_result, verdict) → DeliveryPackage (status=READY_TO_DELIVER)
```

---

## Hallazgos de auditoría

1. **Todos los archivos existen** y tienen contratos bien definidos.
2. **execution_result_gate** está en `pymia/smartpyme/execution_result_gate.py` (no es un módulo separado, está en el paquete `smartpyme`).
3. **microservice_dispatcher** actualmente solo soporta `excel_diagnostic`. Si se intenta despachar `supplier_duplicate_check`, retorna `EXECUTION_UNSUPPORTED`.
4. **execution_result_gate** verifica que las rutas en `output_refs` existan físicamente. Esto es crítico: si `microservice_dispatcher` no genera los archivos de salida (ej. porque `output_dir` es `None`), el gate retornará `VERDICT_UNDELIVERABLE`.
5. **readiness** tiene una regla de clasificación conservadora: si hay ambigüedad entre `excel_diagnostic` y `supplier_duplicate_check`, intenta desempatar por `tank_selection_result.selected_tanks`. Si no puede, retorna `UNSUPPORTED`.
6. **evidence_gate** hace match fuerte por `request_id` y fallback por `evidence_type`. Si el `IntakeEvidenceRequest` no tiene `request_id`, el match puede ser ambiguo.
7. **intake** genera `IntakeEvidenceRequest` con estado `REQUESTED`. El runner debe asegurar que los `EvidenceRecord` tengan `status` en `RECEIVED`, `REGISTERED` o `LINKED` para que sean aceptados por el gate.

---

## Riesgos para el runner

1. **output_refs vacíos:** Si `microservice_dispatcher` se llama con `output_dir=None`, no generará archivos de salida. `execution_result_gate` rechazará el resultado con `VERDICT_UNDELIVERABLE` porque `output_refs` estará vacío. **Solución:** El runner debe siempre proporcionar un `output_dir` temporal para el happy path.

2. **Rutas inexistentes:** `execution_result_gate` verifica que las rutas en `output_refs` existan físicamente. Si el runner usa rutas temporales que se borran antes de la validación, el gate fallará. **Solución:** El runner debe asegurar que los archivos existan hasta después de `build_delivery_package`.

3. **findings_count:** Para el happy path Excel, el fixture debe producir al menos un hallazgo (`findings_count >= 1`). Si el fixture está mal formado, `diagnose_excel` puede retornar 0 hallazgos, pero el gate no lo rechaza por eso (solo verifica que sea entero no negativo). Sin embargo, el test e2e debe afirmar `findings_count >= 1`.

4. **Ambigüedad de clasificación:** Si el `IntakeRecord` tiene `evidence_requests` que habilitan tanto `excel_diagnostic` como `supplier_duplicate_check`, `readiness` puede retornar `UNSUPPORTED` si no puede desempatar. **Solución:** El escenario happy path debe asegurar que solo `excel_diagnostic` esté habilitado.

5. **supplier_duplicate_check no soportado en dispatcher:** Aunque `readiness` y `runtime_bridge` soportan `supplier_duplicate_check`, `microservice_dispatcher` actualmente retorna `EXECUTION_UNSUPPORTED` para cualquier clasificación que no sea `excel_diagnostic`. **Impacto:** El pipeline puede llegar hasta `runtime_bridge` con `READY_TO_EXECUTE`, pero `microservice_dispatcher` lo bloqueará. Esto es consistente con el contrato de M19 (solo certificar `excel_diagnostic`).

---

## Veredicto

**READY_FOR_CODEX**

El mapa de contratos está completo y es consistente. Todos los archivos existen, las funciones están bien definidas, y los estados son explícitos. Codex puede proceder a implementar el runner mínimo y los tests e2e para `excel_diagnostic` basándose en este mapa.

No se detectaron bloqueos estructurales. Los riesgos identificados son manejables con un runner bien implementado (proporcionar `output_dir`, asegurar existencia de archivos, usar fixture Excel válido).
