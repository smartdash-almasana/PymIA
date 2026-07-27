# HISTORICAL_DOC_VALUE_AUDIT_V1

**Date:** 2026-07-27  
**Scope:** the 677 documents previously classified `MOVE_TO_MUSEUM` by `SERVICE_1_DOCUMENTARY_PURGE_AUDIT_V2`.  
**Mode:** audit only; no deletion, move, commit, or push.

## Verdict

```text
CANDIDATES: 677
KEEP_REFERENCE: 337
DELETE: 340
DELETED_NOW: 0
```

## Decision rule

A historical candidate is `KEEP_REFERENCE` only when at least one of these is true:

- it has an incoming reference from current/reference documentation or executable/test/tool surfaces;
- it is explicitly preserved as provenance/history by existing documentary governance;
- it is an active tracked worktree modification;
- it is pilot/incident evidence;
- it is a quarantine snapshot preserving deletion provenance.

Otherwise it is `DELETE`.

`tracked=true` by itself is not sufficient to preserve an obsolete document. Untracked status by itself is not sufficient to delete one.

## KEEP_REFERENCE

| Path | Reasons | Tracked |
|---|---|---:|
| `docs/ingenieria_conversacional.CATALOGO_FORMULAS_MATEMATICAS_PYME_v1.md` | explicit_provenance, incoming_reference | false |
| `docs/ingenieria_conversacional.CATALOGO_HIPOTESIS_Y_EVIDENCIA_v1.md` | explicit_provenance, incoming_reference | false |
| `docs/ingenieria_conversacional.corpus_migrado.md` | explicit_provenance, incoming_reference | false |
| `docs/ingenieria_conversacional.ENSAMBLE_DOCUMENTAL_FASE1_v1.md` | explicit_provenance, incoming_reference | false |
| `docs/ingenieria_conversacional.MAPA_INTEGRACION_v1.md` | explicit_provenance, incoming_reference | false |
| `docs/ingenieria_conversacional.MIGRACION_SMARTPYME_CONVERSACIONAL_v1.md` | explicit_provenance, incoming_reference | false |
| `docs/ingenieria_conversacional.NORMATIVA_v1.md` | explicit_provenance, incoming_reference | false |
| `docs/ingenieria_conversacional.PATOLOGIAS_PYME_Y_TANQUES_DE_CONOCIMIENTO_v1.md` | explicit_provenance, incoming_reference | false |
| `docs/ingenieria_conversacional.PROTOCOLO_PRIMER_CONTACTO_v1.md` | explicit_provenance, incoming_reference | false |
| `docs/migrado_desde_smartpyme_ARQUEOLOGIA_FASE3.md` | explicit_provenance, incoming_reference | false |
| `docs/migrado_desde_smartpyme_catalogos_SYMPTOM_PATHOLOGY_CATALOG_DESIGN.md` | explicit_provenance, incoming_reference | false |
| `docs/migrado_desde_smartpyme_conversacional_CONVERSATIONAL_COMMERCE_MULTIUSER_STRATEGY.md` | explicit_provenance, incoming_reference | false |
| `docs/migrado_desde_smartpyme_DRIFT_REPORT.md` | explicit_provenance, incoming_reference | false |
| `docs/migrado_desde_smartpyme_epistemologia_NOCION_001_ORGANISMO_PYME.md` | explicit_provenance, incoming_reference | false |
| `docs/migrado_desde_smartpyme_formulas_CLINICAL_MATHEMATICAL_KERNEL_AND_HUMAN_COGNITIVE_LOOP.md` | explicit_provenance, incoming_reference | false |
| `docs/migrado_desde_smartpyme_MIGRACION_FISICA_FASE3.md` | explicit_provenance, incoming_reference | false |
| `docs/migrado_desde_smartpyme_MIGRATION_INDEX.md` | explicit_provenance, incoming_reference | false |
| `docs/migrado_desde_smartpyme_REPORTE_CIERRE_FASE1.md` | explicit_provenance, incoming_reference | false |
| `docs/arquitectura/arquitectura-maestra.md` | incoming_reference | true |
| `docs/arquitectura/capability-runtime.md` | incoming_reference | true |
| `docs/arquitectura/CONTRATO_PRIMER_ENCUENTRO_TAXONOMICO.md` | incoming_reference | false |
| `docs/arquitectura/DOCUMENT_CONTEXT_CLASSIFIER_V1.md` | incoming_reference | false |
| `docs/arquitectura/domain-classification.md` | incoming_reference | true |
| `docs/arquitectura/entropy-routing.md` | incoming_reference | true |
| `docs/arquitectura/GLOSARIO_SEMANTICO_PYMIA.md` | incoming_reference | true |
| `docs/arquitectura/harness-engineering.md` | incoming_reference | true |
| `docs/arquitectura/HERMES_CAPABILITY_AUDIT.md` | incoming_reference | false |
| `docs/arquitectura/HERMES_CONTRATO_SEMANTICO.md` | incoming_reference | false |
| `docs/arquitectura/HERMES_MCP1_GATEWAY_CONTROLLED_INTEGRATION.md` | incoming_reference | false |
| `docs/arquitectura/HERMES_MCP1_SANDBOX_EXECUTION_CHECKLIST.md` | incoming_reference | false |
| `docs/arquitectura/HERMES_MCP1_SANDBOX_EXECUTION_RESULT.md` | incoming_reference | false |
| `docs/arquitectura/HERMES_MCP2_SANDBOX_REPEATABILITY_DECISION.md` | incoming_reference | false |
| `docs/arquitectura/HERMES_MCP2_SANDBOX_REPEATABILITY_RESULT.md` | incoming_reference | false |
| `docs/arquitectura/HERMES_OPERATIONAL_VERIFICATION.md` | incoming_reference | false |
| `docs/arquitectura/HERMES_SM1_SM2_ISOLATED_VALIDATION_PLAN.md` | incoming_reference | false |
| `docs/arquitectura/HERMES_SM1_VM_GATEWAY_AUDIT_RESULT.md` | incoming_reference | false |
| `docs/arquitectura/HERMES_SM2_VM_MCP_ROUNDTRIP_RESULT.md` | incoming_reference | false |
| `docs/arquitectura/HERMES_SM2_VM_MCP_ROUNDTRIP_RETRY_RESULT.md` | incoming_reference | false |
| `docs/arquitectura/HERMES_SM2_VM_MCP_ROUNDTRIP_RUNBOOK.md` | incoming_reference | false |
| `docs/arquitectura/KERNEL_ANALITICA_TABULAR_SOBERANA.md` | incoming_reference | true |
| `docs/arquitectura/ONTOLOGIA_AGENTES_SISTEMA.md` | incoming_reference | false |
| `docs/arquitectura/orchestration-boundary.md` | incoming_reference | false |
| `docs/arquitectura/palantir-principles.md` | incoming_reference | false |
| `docs/arquitectura/PDF_IMAGE_EXTRACTION_BENCHMARK.md` | incoming_reference | false |
| `docs/arquitectura/pipeline-traceability-boundary-v1.md` | incoming_reference | true |
| `docs/arquitectura/SCN_001_SOVEREIGN_COMPUTATION_BOUNDARY.md` | incoming_reference | false |
| `docs/arquitectura/SCN_002_CONTRACT_VALIDATION_LAYER_DESIGN.md` | incoming_reference | false |
| `docs/arquitectura/SCN_TEST_FRONTIER_PLAN.md` | incoming_reference | false |
| `docs/arquitectura/SEMANTICA_CONVERSACIONAL_PYMIA_HERMES_BEM.md` | incoming_reference | false |
| `docs/arquitectura/signal-admission-refactor.md` | incoming_reference | false |
| `docs/arquitectura/TECH_DEBT_CLOSURE_PLAN_DOCS_ONLY.md` | incoming_reference | false |
| `docs/arquitectura/TECH_DEBT_CLOSURE_RESULT_DOCS_ONLY.md` | incoming_reference | false |
| `docs/arquitectura/TECH_DEBT_REGISTER.md` | incoming_reference | false |
| `docs/conversa-engine/HERMES_AGENT_AUDIT_POLICY.md` | incoming_reference | false |
| `docs/hermes/autoaditoria-hermes-pipeline-minimo-accionable.md` | incoming_reference | false |
| `docs/hermes/boundary-integracion-conversacional.md` | incoming_reference | false |
| `docs/hermes/contrato-minimo-integracion-externa.md` | incoming_reference | false |
| `docs/hermes/CONVERSATIONAL_BOUNDARY_POLICY.md` | incoming_reference | false |
| `docs/hermes/decision-ensamblaje-chip1-estructura-destino.md` | incoming_reference | false |
| `docs/hermes/flujo-objetivo-hermes-como-conducto-parte-1.md` | incoming_reference | false |
| `docs/hermes/HERMES_BASIC_COMMANDS.md` | incoming_reference | false |
| `docs/hermes/HERMES_CONFIG_HARDENING_PLAN.md` | incoming_reference | false |
| `docs/hermes/HERMES_CONFIG_HARDENING_PLAN_REVIEW.md` | incoming_reference | false |
| `docs/hermes/HERMES_LOCAL_INSTANCE_INVENTORY.md` | incoming_reference | false |
| `docs/hermes/HERMES_LOCAL_RUNTIME_GATE.md` | incoming_reference | false |
| `docs/hermes/HERMES_LOCAL_SCN_OFFLINE_CHAIN_AUDIT_RESULT.md` | incoming_reference | false |
| `docs/hermes/HERMES_LOCAL_SCN_SANDBOX_CHAIN_AUDIT_RESULT.md` | incoming_reference | false |
| `docs/hermes/HERMES_LOCAL_SCN_SANDBOX_COMMAND_PLAN.md` | incoming_reference | false |
| `docs/hermes/HERMES_LOCAL_SCN_SANDBOX_PLAN.md` | incoming_reference | false |
| `docs/hermes/HERMES_LOCAL_SCN_SANDBOX_PREP_CHECKLIST.md` | incoming_reference | false |
| `docs/hermes/HERMES_LOCAL_STRUCTURE_AUDIT.md` | incoming_reference | false |
| `docs/hermes/HERMES_OFFICIAL_DOCS_DIGEST.md` | incoming_reference | false |
| `docs/hermes/HERMES_RUNTIME_SOURCE_AUDIT.md` | incoming_reference | false |
| `docs/hermes/hipotesis-ensamble-nodos-smartpyme-para-kernel-pymia.md` | incoming_reference | false |
| `docs/hermes/incidente-integracion-hermes-pymia-a-mitad-de-construccion.md` | incoming_reference, pilot_or_incident_evidence | false |
| `docs/hermes/inventario-smartpyme-nodos-colgados-para-pymia.md` | incoming_reference | false |
| `docs/hermes/kernel-minimo-viable-y-corpus-minimo.md` | incoming_reference | false |
| `docs/hermes/pipeline-funcional-pymia-nodos-existentes.md` | incoming_reference | false |
| `docs/hermes/plano-logico-kernel-integrado-pines-estados-compuertas.md` | incoming_reference | false |
| `docs/hermes/principio-obligatorio-hermes-runtime-orchestrator.md` | incoming_reference | false |
| `docs/hermes/protocolo-doble-lectura-codex-kernel.md` | incoming_reference | false |
| `docs/hermes/RUNBOOK_TELEGRAM_DIRECT_RUNTIME.md` | incoming_reference | false |
| `docs/hermes/soul.md` | incoming_reference | false |
| `docs/hermes/TELEGRAM_DIRECT_RUNTIME_CHECKPOINT.md` | incoming_reference | false |
| `docs/ops/PILOTO_001_DATOS_SESION.md` | pilot_or_incident_evidence | false |
| `docs/ops/PILOTO_REAL_001_PLAN.md` | pilot_or_incident_evidence | false |
| `docs/ops/RUNBOOK_PILOTO_ASISTIDO_POST_LC.md` | explicit_provenance, incoming_reference, pilot_or_incident_evidence | false |
| `docs/producto/asertividades-operativas.md` | incoming_reference | true |
| `docs/producto/capa-00-canal-entrada.md` | incoming_reference | false |
| `docs/producto/capa-01-admision-epistemologica.md` | incoming_reference | false |
| `docs/producto/FIRST_AID_GPT_V1_ASSISTED_PILOT_001.md` | incoming_reference, pilot_or_incident_evidence | false |
| `docs/producto/FIRST_AID_GPT_V1_ASSISTED_PILOT_002.md` | incoming_reference, pilot_or_incident_evidence | false |
| `docs/producto/FIRST_AID_GPT_V1_ASSISTED_PILOT_003.md` | incoming_reference, pilot_or_incident_evidence | false |
| `docs/producto/FIRST_AID_GPT_V1_ASSISTED_PILOT_004.md` | incoming_reference, pilot_or_incident_evidence | false |
| `docs/producto/FIRST_AID_GPT_V1_PILOT_BATCH_REVIEW.md` | incoming_reference, pilot_or_incident_evidence | false |
| `docs/producto/FIRST_AID_GPT_V1_PILOT_CASE_LOG_TEMPLATE.md` | incoming_reference, pilot_or_incident_evidence | false |
| `docs/producto/FIRST_AID_GPT_V1_PILOT_OFFER.md` | incoming_reference, pilot_or_incident_evidence | false |
| `docs/producto/FIRST_AID_GPT_V1_PILOT_SCRIPT.md` | incoming_reference, pilot_or_incident_evidence | false |
| `docs/producto/FIRST_AID_GPT_V1_REAL_PILOT_INTAKE_PROTOCOL.md` | incoming_reference, pilot_or_incident_evidence | false |
| `docs/producto/FIRST_AID_MARGIN_TEXTILE_LOCAL_CHECK.md` | incoming_reference | false |
| `docs/producto/FIRST_AID_PRODUCTION_PERFORMANCE_LOCAL_CHECK.md` | incoming_reference | false |
| `docs/producto/FIRST_AID_TRIAGE_COMPONENTS_DECISION_V1.md` | incoming_reference | false |
| `docs/producto/protocolo-anamnesis-mvp.md` | incoming_reference | true |
| `docs/producto/PYMIA_DOCUMENTARY_AXIS_PURGE_AND_CANONICAL_INDEX_AUDIT_V1.md` | incoming_reference | false |
| `docs/producto/PYMIA_DOCUMENTARY_PURGE_BATCH_001_AUDIT_ONLY.md` | incoming_reference | false |
| `docs/producto/PYMIA_DOCUMENTARY_PURGE_BATCH_001_DELETE_CONFIRMATION_AUDIT.md` | incoming_reference | false |
| `docs/producto/registro-ciclos-operativos.md` | incoming_reference | false |
| `docs/producto/S1_AUTONOMOUS_GUARDED_SAAS_V1_ACTIVE_FRONT_DECISION.md` | incoming_reference | false |
| `docs/producto/S1_AUTONOMOUS_OWNER_EVIDENCE_GATE_CHAIN_CONTRACT_V1.md` | incoming_reference | false |
| `docs/producto/S1_AUTONOMOUS_OWNER_EVIDENCE_GATE_CHAIN_REUSE_MAPPING_V1.md` | incoming_reference | false |
| `docs/producto/S1_AUTONOMOUS_OWNER_EVIDENCE_GATE_CHAIN_TASKSPEC_V1.md` | incoming_reference | false |
| `docs/producto/S1_AUTONOMOUS_OWNER_EVIDENCE_GATE_CHAIN_TRACE_AUDIT_V1.md` | incoming_reference | false |
| `docs/producto/S1_FIRST_REAL_CLIENT_PILOT_INTAKE_PACKET_V1.md` | pilot_or_incident_evidence | false |
| `docs/producto/S1_FIRST_REAL_CLIENT_PILOT_PROTOCOL_V1.md` | pilot_or_incident_evidence | false |
| `docs/producto/S1_FIRST_REAL_CLIENT_PILOT_RUNBOOK_V1.md` | pilot_or_incident_evidence | false |
| `docs/producto/S1_REAL_CLIENT_PILOT_READINESS_AUDIT_V1.md` | pilot_or_incident_evidence | false |
| `docs/producto/SERVICE_1_ACCOUNTING_CONTRACTS_V1.md` | active_worktree_change | true |
| `docs/producto/SERVICE_1_ACCOUNTING_CONTRACT_FAMILY_INDEX_V1.md` | active_worktree_change | true |
| `docs/producto/SERVICE_1_ACCOUNTING_WORKPAPER_CONTRACT_V1.md` | active_worktree_change | true |
| `docs/producto/SERVICE_1_ACCOUNTING_WORKPAPER_CONTROLLED_PILOT_SERIES_SUMMARY_V1.md` | pilot_or_incident_evidence | false |
| `docs/producto/SERVICE_1_ACCOUNTING_WORKPAPER_CONTROLLED_REAL_PILOT_V1.md` | pilot_or_incident_evidence | false |
| `docs/producto/SERVICE_1_ACCOUNTING_WORKPAPER_FIRST_CONTROLLED_PILOT_RESULT_REVIEW_V1.md` | pilot_or_incident_evidence | false |
| `docs/producto/SERVICE_1_ACCOUNTING_WORKPAPER_PILOT_INTAKE_PACKET_V1.md` | pilot_or_incident_evidence | false |
| `docs/producto/SERVICE_1_ACCOUNTING_WORKPAPER_PILOT_SCRIPT_V1.md` | pilot_or_incident_evidence | false |
| `docs/producto/SERVICE_1_ACCOUNTING_WORKPAPER_SECOND_CONTROLLED_PILOT_PLAN_V1.md` | pilot_or_incident_evidence | false |
| `docs/producto/SERVICE_1_ACCOUNTING_WORKPAPER_SECOND_CONTROLLED_PILOT_RESULT_REVIEW_V1.md` | pilot_or_incident_evidence | false |
| `docs/producto/SERVICE_1_BANK_RECONCILIATION_CONTRACT_V1.md` | active_worktree_change | true |
| `docs/producto/SERVICE_1_COLUMN_CONFIRMATION_REENTRY_MODULE_CONTRACT_V1.md` | incoming_reference | false |
| `docs/producto/SERVICE_1_COLUMN_CONFIRMATION_REENTRY_TASKSPEC_V1.md` | incoming_reference | false |
| `docs/producto/SERVICE_1_EVIDENCE_CUSTODY_V1.md` | active_worktree_change | true |
| `docs/producto/SERVICE_1_INTEGRALITY_AND_MATURITY_AUDIT_V1.md` | incoming_reference | false |
| `docs/producto/SERVICE_1_INVOICE_COLLECTION_MATCHING_CONTRACT_V1.md` | active_worktree_change | true |
| `docs/producto/SERVICE_1_MERCADO_PAGO_RECONCILIATION_CONTRACT_V1.md` | active_worktree_change | true |
| `docs/producto/SERVICE_1_SUPPLIER_PURCHASE_REVIEW_CONTRACT_V1.md` | active_worktree_change | true |
| `docs/producto/SERVICE_1_SYNTHETIC_REAL_CASE_PILOT_V1.md` | pilot_or_incident_evidence | false |
| `docs/producto/SERVICE_1_XLSX_ACCEPTANCE_AND_BLOCKING_PROTOCOL_V1.md` | active_worktree_change | true |
| `docs/producto/SERVICE_1_XLSX_DELIVERY_GENERALIZATION_V1.md` | active_worktree_change | true |
| `docs/producto/SERVICE_1_XLSX_FORMULA_POLICY_V1.md` | active_worktree_change | true |
| `docs/prompts/PROMPT_MASTER_DOCUMENT_INTELLIGENCE_ENTERPRISE.md` | incoming_reference | false |
| `docs/prompts/PROMPT_PHASE1_DOCUMENT_INTELLIGENCE_ISOLATED.md` | incoming_reference | false |
| `docs/prompts/README.md` | incoming_reference | false |
| `docs/pymia/AAAS_OPERATIONAL_BOUNDARY.md` | incoming_reference | false |
| `docs/pymia/ASSISTED_SIMULATED_PILOT_001.md` | incoming_reference, pilot_or_incident_evidence | false |
| `docs/pymia/ASSISTED_SIMULATED_PILOT_001_CHECKPOINT.md` | incoming_reference, pilot_or_incident_evidence | false |
| `docs/pymia/ASSISTED_SIMULATED_PILOT_002_BIS_BLOCKED_ACTIONABLE_CHECKPOINT.md` | pilot_or_incident_evidence | false |
| `docs/pymia/ASSISTED_SIMULATED_PILOT_002_VALUE_CHECK.md` | pilot_or_incident_evidence | false |
| `docs/pymia/ASSISTED_SIMULATED_PILOT_002_VALUE_CHECKPOINT.md` | pilot_or_incident_evidence | false |
| `docs/pymia/CLOSING_AUDIT_2026_06_12.md` | incoming_reference | false |
| `docs/pymia/DEUDA_TECNICA.md` | incoming_reference | false |
| `docs/pymia/FUNCTIONAL_PACK_LOADER_NAVIGATOR_V1_CAPABILITYSPEC.md` | incoming_reference | false |
| `docs/pymia/FUNCTIONAL_PACK_LOADER_NAVIGATOR_V1_EXTERNAL_AUDIT_CHECKPOINT.md` | incoming_reference | false |
| `docs/pymia/FUNCTIONAL_PACK_LOADER_NAVIGATOR_V1_MODULECONTRACT.md` | incoming_reference | false |
| `docs/pymia/FUNCTIONAL_PACK_LOADER_NAVIGATOR_V1_TASKSPEC.md` | incoming_reference | false |
| `docs/pymia/KERNEL_PIPELINE_INVENTORY.md` | incoming_reference | false |
| `docs/pymia/KNOWLEDGETANKS_PACKSYSTEM_RECONCILIATION_AUDIT.md` | incoming_reference | false |
| `docs/pymia/M36_PORTS_AND_GATES_AUTHORIZATION_CAPABILITYSPEC.md` | incoming_reference | false |
| `docs/pymia/M36_PORTS_AND_GATES_EXECUTION_BOUNDARY_MODULECONTRACT.md` | incoming_reference | false |
| `docs/pymia/M36_PORTS_AND_GATES_FOUNDATION_TASKSPEC.md` | incoming_reference | false |
| `docs/pymia/M37_CORE_TO_AUDIT_AND_DELIVERY_INTEGRATION_CAPABILITYSPEC.md` | incoming_reference | false |
| `docs/pymia/M37_CORE_TO_AUDIT_AND_DELIVERY_INTEGRATION_MODULECONTRACT.md` | incoming_reference | false |
| `docs/pymia/M37_CORE_TO_AUDIT_AND_DELIVERY_INTEGRATION_TASKSPEC.md` | incoming_reference | false |
| `docs/pymia/M38_CORE_DELIVERY_BRIDGE_CONSUMPTION_CAPABILITYSPEC.md` | incoming_reference | false |
| `docs/pymia/M38_CORE_DELIVERY_BRIDGE_CONSUMPTION_MODULECONTRACT.md` | incoming_reference | false |
| `docs/pymia/M38_CORE_DELIVERY_BRIDGE_CONSUMPTION_TASKSPEC.md` | incoming_reference | false |
| `docs/pymia/M39_CORE_BRIDGE_PAYLOAD_PRODUCTION_CAPABILITYSPEC.md` | incoming_reference | false |
| `docs/pymia/M39_CORE_BRIDGE_PAYLOAD_PRODUCTION_MODULECONTRACT.md` | incoming_reference | false |
| `docs/pymia/M39_CORE_BRIDGE_PAYLOAD_PRODUCTION_TASKSPEC.md` | incoming_reference | false |
| `docs/pymia/M40_STRUCTURED_EVIDENCE_TO_PROGRESSIVE_CONTEXT_CAPABILITYSPEC.md` | incoming_reference | false |
| `docs/pymia/M40_STRUCTURED_EVIDENCE_TO_PROGRESSIVE_CONTEXT_MODULECONTRACT.md` | incoming_reference | false |
| `docs/pymia/M40_STRUCTURED_EVIDENCE_TO_PROGRESSIVE_CONTEXT_TASKSPEC.md` | incoming_reference | false |
| `docs/pymia/M41_CORE_DELIVERY_REPLAY_CHECKPOINT.md` | incoming_reference | false |
| `docs/pymia/M42_OWNER_FACING_REPORT_V1_CAPABILITYSPEC.md` | incoming_reference | false |
| `docs/pymia/M42_OWNER_FACING_REPORT_V1_MODULECONTRACT.md` | incoming_reference | false |
| `docs/pymia/M42_OWNER_FACING_REPORT_V1_TASKSPEC.md` | incoming_reference | false |
| `docs/pymia/M43_OWNER_REPORT_DELIVERY_INTEGRATION_CHECKPOINT.md` | incoming_reference | false |
| `docs/pymia/M44_VISIBLE_OWNER_REPORT_OUTPUT_CAPABILITYSPEC.md` | incoming_reference | false |
| `docs/pymia/M44_VISIBLE_OWNER_REPORT_OUTPUT_CHECKPOINT.md` | incoming_reference | false |
| `docs/pymia/M44_VISIBLE_OWNER_REPORT_OUTPUT_MODULECONTRACT.md` | incoming_reference | false |
| `docs/pymia/M44_VISIBLE_OWNER_REPORT_OUTPUT_TASKSPEC.md` | incoming_reference | false |
| `docs/pymia/M45_GUIDED_EVIDENCE_RECOVERY_AUTHORIZATION_CAPABILITYSPEC.md` | incoming_reference | false |
| `docs/pymia/M45_GUIDED_EVIDENCE_RECOVERY_AUTHORIZATION_MODULECONTRACT.md` | incoming_reference | false |
| `docs/pymia/M45_GUIDED_EVIDENCE_RECOVERY_AUTHORIZATION_TASKSPEC.md` | incoming_reference | false |
| `docs/pymia/M46_OWNER_QUESTIONS_CONTRACT_CAPABILITYSPEC.md` | incoming_reference | false |
| `docs/pymia/M46_OWNER_QUESTIONS_CONTRACT_MODULECONTRACT.md` | incoming_reference | false |
| `docs/pymia/M46_OWNER_QUESTIONS_CONTRACT_TASKSPEC.md` | incoming_reference | false |
| `docs/pymia/M47_OWNER_QUESTIONS_BUILDER_CAPABILITYSPEC.md` | incoming_reference | false |
| `docs/pymia/M47_OWNER_QUESTIONS_BUILDER_MODULECONTRACT.md` | incoming_reference | false |
| `docs/pymia/M47_OWNER_QUESTIONS_BUILDER_TASKSPEC.md` | incoming_reference | false |
| `docs/pymia/M48_OWNER_QUESTIONS_DELIVERY_INTEGRATION_CAPABILITYSPEC.md` | incoming_reference | false |
| `docs/pymia/M48_OWNER_QUESTIONS_DELIVERY_INTEGRATION_MODULECONTRACT.md` | incoming_reference | false |
| `docs/pymia/M48_OWNER_QUESTIONS_DELIVERY_INTEGRATION_TASKSPEC.md` | incoming_reference | false |
| `docs/pymia/M49_VISIBLE_OWNER_QUESTIONS_CAPABILITYSPEC.md` | incoming_reference | false |
| `docs/pymia/M49_VISIBLE_OWNER_QUESTIONS_MODULECONTRACT.md` | incoming_reference | false |
| `docs/pymia/M49_VISIBLE_OWNER_QUESTIONS_TASKSPEC.md` | incoming_reference | false |
| `docs/pymia/M50_GUIDED_EVIDENCE_RECOVERY_REPLAY_CHECKPOINT.md` | incoming_reference | false |
| `docs/pymia/M51_OWNER_RESPONSE_CAPTURE_AUTHORIZATION_CAPABILITYSPEC.md` | incoming_reference | false |
| `docs/pymia/M51_OWNER_RESPONSE_CAPTURE_AUTHORIZATION_MODULECONTRACT.md` | incoming_reference | false |
| `docs/pymia/M51_OWNER_RESPONSE_CAPTURE_AUTHORIZATION_TASKSPEC.md` | incoming_reference | false |
| `docs/pymia/M52_OWNER_ANSWER_EVALUATION_AUTHORIZATION_CAPABILITYSPEC.md` | incoming_reference | false |
| `docs/pymia/M52_OWNER_ANSWER_EVALUATION_AUTHORIZATION_MODULECONTRACT.md` | incoming_reference | false |
| `docs/pymia/M52_OWNER_ANSWER_EVALUATION_AUTHORIZATION_TASKSPEC.md` | incoming_reference | false |
| `docs/pymia/M53_OWNER_ANSWER_EVALUATION_MINIMAL_FLOW_CAPABILITYSPEC.md` | incoming_reference | false |
| `docs/pymia/M53_OWNER_ANSWER_EVALUATION_MINIMAL_FLOW_MODULECONTRACT.md` | incoming_reference | false |
| `docs/pymia/M53_OWNER_ANSWER_EVALUATION_MINIMAL_FLOW_TASKSPEC.md` | incoming_reference | false |
| `docs/pymia/M54_OWNER_ANSWER_EVALUATION_REPLAY_CHECKPOINT.md` | incoming_reference | false |
| `docs/pymia/M55_OWNER_NEXT_ACTION_DECISION_CAPABILITYSPEC.md` | incoming_reference | false |
| `docs/pymia/M55_OWNER_NEXT_ACTION_DECISION_MODULECONTRACT.md` | incoming_reference | false |
| `docs/pymia/M55_OWNER_NEXT_ACTION_DECISION_TASKSPEC.md` | incoming_reference | false |
| `docs/pymia/M56_VISIBLE_OWNER_NEXT_ACTION_CAPABILITYSPEC.md` | incoming_reference | false |
| `docs/pymia/M56_VISIBLE_OWNER_NEXT_ACTION_MODULECONTRACT.md` | incoming_reference | false |
| `docs/pymia/M56_VISIBLE_OWNER_NEXT_ACTION_TASKSPEC.md` | incoming_reference | false |
| `docs/pymia/M57_OWNER_ACTION_TARGET_RESOLUTION_CAPABILITYSPEC.md` | incoming_reference | false |
| `docs/pymia/M57_OWNER_ACTION_TARGET_RESOLUTION_MODULECONTRACT.md` | incoming_reference | false |
| `docs/pymia/M57_OWNER_ACTION_TARGET_RESOLUTION_TASKSPEC.md` | incoming_reference | false |
| `docs/pymia/M58_OWNER_NEXT_ACTION_REPORT_PROJECTION_CAPABILITYSPEC.md` | incoming_reference | false |
| `docs/pymia/M58_OWNER_NEXT_ACTION_REPORT_PROJECTION_MODULECONTRACT.md` | incoming_reference | false |
| `docs/pymia/M58_OWNER_NEXT_ACTION_REPORT_PROJECTION_TASKSPEC.md` | incoming_reference | false |
| `docs/pymia/M59_OWNER_ACTION_PIPELINE_BOUNDARY_CAPABILITYSPEC.md` | incoming_reference | false |
| `docs/pymia/M59_OWNER_ACTION_PIPELINE_BOUNDARY_MODULECONTRACT.md` | incoming_reference | false |
| `docs/pymia/M59_OWNER_ACTION_PIPELINE_BOUNDARY_TASKSPEC.md` | incoming_reference | false |
| `docs/pymia/M60_OWNER_ANSWER_ENTRYPOINT_AUDIT_CAPABILITYSPEC.md` | incoming_reference | false |
| `docs/pymia/M60_OWNER_ANSWER_ENTRYPOINT_AUDIT_MODULECONTRACT.md` | incoming_reference | false |
| `docs/pymia/M60_OWNER_ANSWER_ENTRYPOINT_AUDIT_TASKSPEC.md` | incoming_reference | false |
| `docs/pymia/M61_OWNER_ANSWER_STRUCTURED_CAPTURE_CAPABILITYSPEC.md` | incoming_reference | false |
| `docs/pymia/M61_OWNER_ANSWER_STRUCTURED_CAPTURE_MODULECONTRACT.md` | incoming_reference | false |
| `docs/pymia/M61_OWNER_ANSWER_STRUCTURED_CAPTURE_TASKSPEC.md` | incoming_reference | false |
| `docs/pymia/M62_OWNER_ANSWER_TO_ACTION_COMPOSITION_CAPABILITYSPEC.md` | incoming_reference | false |
| `docs/pymia/M62_OWNER_ANSWER_TO_ACTION_COMPOSITION_MODULECONTRACT.md` | incoming_reference | false |
| `docs/pymia/M62_OWNER_ANSWER_TO_ACTION_COMPOSITION_TASKSPEC.md` | incoming_reference | false |
| `docs/pymia/M63C_OWNER_ACTION_BRIDGE_REENTRY_CONTRACT_CAPABILITYSPEC.md` | incoming_reference | false |
| `docs/pymia/M63C_OWNER_ACTION_BRIDGE_REENTRY_CONTRACT_MODULECONTRACT.md` | incoming_reference | false |
| `docs/pymia/M63C_OWNER_ACTION_BRIDGE_REENTRY_CONTRACT_TASKSPEC.md` | incoming_reference | false |
| `docs/pymia/M63_OWNER_ACTION_VISIBILITY_REENTRY_BOUNDARY_CAPABILITYSPEC.md` | incoming_reference | false |
| `docs/pymia/M63_OWNER_ACTION_VISIBILITY_REENTRY_BOUNDARY_MODULECONTRACT.md` | incoming_reference | false |
| `docs/pymia/M63_OWNER_ACTION_VISIBILITY_REENTRY_BOUNDARY_TASKSPEC.md` | incoming_reference | false |
| `docs/pymia/M64_SANDBOX_OWNER_ANSWER_REPLAY_CAPABILITYSPEC.md` | incoming_reference | false |
| `docs/pymia/M64_SANDBOX_OWNER_ANSWER_REPLAY_TASKSPEC.md` | incoming_reference | false |
| `docs/pymia/M65_VISIBLE_REPLAY_OUTPUT_REVIEW_CAPABILITYSPEC.md` | incoming_reference | false |
| `docs/pymia/M65_VISIBLE_REPLAY_OUTPUT_REVIEW_TASKSPEC.md` | incoming_reference | false |
| `docs/pymia/M66_OWNER_REPLAY_REENTRY_CAPABILITYSPEC.md` | incoming_reference | false |
| `docs/pymia/M66_OWNER_REPLAY_REENTRY_TASKSPEC.md` | incoming_reference | false |
| `docs/pymia/MISSING_INPUT_TYPE_CLASSIFICATION_CHECKPOINT.md` | incoming_reference | false |
| `docs/pymia/MISSING_INPUT_TYPE_CLASSIFICATION_TASKSPEC.md` | incoming_reference | false |
| `docs/pymia/OD1_OWNER_DECISION_CAPTURE_BOUNDARY_FOR_CONFIRMED_CATALOG_SUMMARY_CAPABILITYSPEC.md` | incoming_reference | false |
| `docs/pymia/OD1_OWNER_DECISION_CAPTURE_BOUNDARY_FOR_CONFIRMED_CATALOG_SUMMARY_CHECKPOINT.md` | incoming_reference | false |
| `docs/pymia/OWNER_ANSWER_ACKNOWLEDGEMENT_TRACE_CHECKPOINT.md` | incoming_reference | false |
| `docs/pymia/OWNER_ANSWER_TO_MISSING_INPUTS_RECONCILIATION_CHECKPOINT.md` | incoming_reference | false |
| `docs/pymia/OWNER_ANSWER_TO_MISSING_INPUTS_RECONCILIATION_TASKSPEC.md` | incoming_reference | false |
| `docs/pymia/OWNER_CONFIRMED_SEMANTIC_REQUEST_FLOW_TASKSPEC.md` | incoming_reference | false |
| `docs/pymia/OWNER_CONVERSATION_TO_INITIAL_DIAGNOSIS_MODULECONTRACT.md` | incoming_reference | false |
| `docs/pymia/OWNER_CONVERSATION_TO_INITIAL_DIAGNOSIS_TASKSPEC.md` | incoming_reference | false |
| `docs/pymia/OWNER_INTERACTION_ATOMIC_TRACE.md` | incoming_reference | false |
| `docs/pymia/OWNER_QUESTIONS_HUMANIZATION_GATE_CHECKPOINT.md` | incoming_reference | false |
| `docs/pymia/OWNER_QUESTIONS_HUMANIZATION_GATE_TASKSPEC.md` | incoming_reference | false |
| `docs/pymia/OWNER_SEMANTIC_CONFIRMATION_GATE_METADATA_PROJECTION_CAPABILITYSPEC.md` | incoming_reference | false |
| `docs/pymia/OWNER_SEMANTIC_CONFIRMATION_GATE_METADATA_PROJECTION_CHECKPOINT.md` | incoming_reference | false |
| `docs/pymia/OWNER_SEMANTIC_CONFIRMATION_LOOP_SANDBOX_CHECKPOINT.md` | incoming_reference | false |
| `docs/pymia/OWNER_SEMANTIC_GATE_BUILDER_CAPABILITYSPEC.md` | incoming_reference | false |
| `docs/pymia/OWNER_SEMANTIC_GATE_BUILDER_CHECKPOINT.md` | incoming_reference | false |
| `docs/pymia/OWNER_SEMANTIC_GATE_BUILDER_MODULECONTRACT.md` | incoming_reference | false |
| `docs/pymia/OWNER_SEMANTIC_GATE_BUILDER_TASKSPEC.md` | incoming_reference | false |
| `docs/pymia/OWNER_SEMANTIC_LOOP_THREE_LAYER_FLOW.md` | incoming_reference | false |
| `docs/pymia/PACK_BOUNDARY_CODE_RECONCILIATION.md` | incoming_reference | false |
| `docs/pymia/PORTS_AND_GATES_CONTRACT_REGISTRY.md` | incoming_reference | false |
| `docs/pymia/POST_ADR_025_NEXT_FRONT_CLASSIFICATION_TASKSPEC.md` | incoming_reference | false |
| `docs/pymia/POST_C2I_INTEGRATION_CONTROL_CHECKPOINT.md` | incoming_reference | false |
| `docs/pymia/PRELIMINARY_TAXONOMY_LIFECYCLE_CONTRACT_CHECKPOINT.md` | incoming_reference | false |
| `docs/pymia/PRELIMINARY_TAXONOMY_LIFECYCLE_CONTRACT_TASKSPEC.md` | incoming_reference | false |
| `docs/pymia/PRIMARY_CASE_FILE_V1_MINIMAL_CONTRACT_TASKSPEC.md` | incoming_reference | false |
| `docs/pymia/PRIMEROS_AUXILIOS_GPT_V1_CHECKPOINT.md` | incoming_reference | false |
| `docs/pymia/PYMIA_AUDIT_LEDGER.md` | explicit_provenance, incoming_reference | false |
| `docs/pymia/PYMIA_DEVELOPMENT_METHOD.md` | explicit_provenance, incoming_reference | false |
| `docs/pymia/PYMIA_GENETIC_AUDIT_MATRIX.md` | explicit_provenance | false |
| `docs/pymia/PYMIA_LIVE_CORE_MANIFEST.md` | explicit_provenance, incoming_reference | false |
| `docs/pymia/PYMIA_LIVE_PIPELINE.md` | explicit_provenance, incoming_reference | false |
| `docs/pymia/PYMIA_MOTHERBOARD_INDEX.md` | explicit_provenance | false |
| `docs/pymia/SEMANTIC_CONFIRMATION_REENTRY_BLOCK_CLOSURE.md` | incoming_reference | false |
| `docs/pymia/SERVICE_1_SEMANTIC_RUNTIME_LANE_CLASSIFICATION_V1_CAPABILITYSPEC.md` | incoming_reference | false |
| `docs/pymia/SIMULATED_PILOT_FRICTION_RECONCILIATION.md` | incoming_reference, pilot_or_incident_evidence | false |
| `docs/pymia/SUPERAUDITORIA_INFORME_0.md` | incoming_reference | false |
| `docs/roadmap/M31_SERVICIO_ASISTIDO_REPETIBLE_PLAN.md` | incoming_reference | false |
| `docs/smartpyme/M17_SUPPLIER_DISPATCHER_CONTRACT_FINDING.md` | incoming_reference | false |
| `docs/smartpyme/M19_7_SINGLE_COMMAND_CHECKPOINT.md` | incoming_reference | false |
| `docs/smartpyme/M31C_ASSISTED_SERVICE_OFFER.md` | incoming_reference | false |
| `docs/smartpyme/M31C_COMMERCIAL_INTAKE.md` | incoming_reference | false |
| `docs/smartpyme/M31C_PREPARACION_COMERCIAL_PLAN.md` | incoming_reference | false |
| `docs/smartpyme/M31P_CAPABILITY_SPEC.md` | incoming_reference | false |
| `docs/smartpyme/M31P_PILOTOS_ASISTIDOS_PLAN.md` | pilot_or_incident_evidence | false |
| `docs/smartpyme/M31P_PILOTS_REGISTRY.md` | pilot_or_incident_evidence | false |
| `docs/smartpyme/M31P_PILOT_RECORD_TEMPLATE.md` | pilot_or_incident_evidence | false |
| `docs/smartpyme/M31P_PILOT_VALIDATION_CHECKLIST.md` | pilot_or_incident_evidence | false |
| `docs/smartpyme/M31P_TASK_SPEC.md` | incoming_reference | false |
| `docs/smartpyme/M31R_CAPABILITY_SPEC.md` | incoming_reference | false |
| `docs/smartpyme/M31R_REAL_PILOTS_REGISTRY.md` | incoming_reference, pilot_or_incident_evidence | false |
| `docs/smartpyme/M31R_TASK_SPEC.md` | incoming_reference | false |
| `docs/smartpyme/M31_SERVICIO_ASISTIDO_REPETIBLE_PROTOCOL.md` | incoming_reference | false |
| `docs/smartpyme/M32_PILOTOS_ASISTIDOS_CONTROLADOS_PLAN.md` | pilot_or_incident_evidence | false |
| `docs/smartpyme/PYMIA_OPERATING_METHOD_POST_FICHA.md` | incoming_reference | false |
| `docs/smartpyme/SMARTPYME_ANAMNESIS_FSM_INTEGRATION.md` | incoming_reference | false |
| `docs/smartpyme/SMARTPYME_CAPABILITY_PLUGIN_REGISTRY.md` | incoming_reference | false |
| `docs/smartpyme/SMARTPYME_DELIVERY_MARKDOWN_MINIMAL.md` | incoming_reference | false |
| `docs/smartpyme/SMARTPYME_DELIVERY_PACKAGE_MINIMAL.md` | incoming_reference | false |
| `docs/smartpyme/SMARTPYME_EVIDENCE_AND_FORMULA_TANK.md` | incoming_reference | false |
| `docs/smartpyme/SMARTPYME_EVIDENCE_RECORD_MINIMAL.md` | incoming_reference | false |
| `docs/smartpyme/SMARTPYME_EVIDENCE_SUFFICIENCY_GATE.md` | incoming_reference | false |
| `docs/smartpyme/SMARTPYME_EXECUTION_RESULT_GATE.md` | incoming_reference | false |
| `docs/smartpyme/SMARTPYME_HERMES_RECALL_BEFORE_REPLY_INTEGRATION.md` | incoming_reference | false |
| `docs/smartpyme/SMARTPYME_INTAKE_RECORD_AND_EVIDENCE_REQUEST.md` | incoming_reference | false |
| `docs/smartpyme/SMARTPYME_INTERROGATION_SLICE.md` | incoming_reference | false |
| `docs/smartpyme/SMARTPYME_INTERROGATION_TAXONOMY.md` | incoming_reference | false |
| `docs/smartpyme/SMARTPYME_KNOWLEDGE_TANKS_ARCHITECTURE.md` | incoming_reference | false |
| `docs/smartpyme/SMARTPYME_KNOWLEDGE_TANKS_CONTRACT.md` | incoming_reference | false |
| `docs/smartpyme/SMARTPYME_LOCAL_MVP_RUNTIME.md` | incoming_reference | false |
| `docs/smartpyme/SMARTPYME_OPERATIONAL_PATHOLOGY_TANK.md` | incoming_reference | false |
| `docs/smartpyme/SMARTPYME_READY_FOR_ANALYSIS_GATE.md` | incoming_reference | false |
| `docs/smartpyme/SMARTPYME_TANK_SELECTION_SLICE.md` | incoming_reference | false |
| `docs/smartpyme/SMARTPYME_TELEGRAM_HERMES_PYMIA_CONVERSATION_PLAN.md` | incoming_reference | false |
| `docs/smartpyme/SUPERMEMORY_TENANT_RECALL_PLUGIN.md` | incoming_reference | false |
| `docs/transient-design/CONVERSATION_CLINICAL_RUNTIME_STRATEGIC_DIRECTION.md` | incoming_reference | false |
| `docs/transient-design/TENANT_CLINICAL_CONTEXT_AND_DOCUMENT_INTELLIGENCE_DESIGN.md` | incoming_reference | false |
| `docs/vision/SMARTPYME_LABORATORIO_PYME_Y_ESTABILIZACION_OPERACIONAL.md` | explicit_provenance, incoming_reference | false |
| `docs/vision/SMARTPYME_MVP_REALISTA_Y_FILOSOFIA_OPERACIONAL.md` | explicit_provenance, incoming_reference | false |
| `docs/smartpyme/pilots/M31P-001.md` | pilot_or_incident_evidence | false |
| `docs/smartpyme/pilots/M31P-001_DATA_REQUEST.md` | pilot_or_incident_evidence | false |
| `docs/smartpyme/pilots/M31P-001_INTAKE.md` | pilot_or_incident_evidence | false |
| `docs/smartpyme/pilots/M31P-002.md` | pilot_or_incident_evidence | false |
| `docs/smartpyme/pilots/M31P-002_DATA_REQUEST.md` | pilot_or_incident_evidence | false |
| `docs/smartpyme/pilots/M31P-003.md` | pilot_or_incident_evidence | false |
| `docs/smartpyme/pilots/M31P-004.md` | pilot_or_incident_evidence | false |
| `docs/smartpyme/pilots/M32-001.md` | pilot_or_incident_evidence | false |
| `docs/smartpyme/pilots/M32-001_TELEGRAM_CHANNEL_CHECK.md` | pilot_or_incident_evidence | false |
| `docs/smartpyme/pilots/M32-S-001.md` | pilot_or_incident_evidence | false |
| `docs/smartpyme/pilots/M32-S-001_EXECUTION_SCRIPT.md` | pilot_or_incident_evidence | false |
| `docs/smartpyme/pilots/README.md` | incoming_reference, pilot_or_incident_evidence | false |
| `docs/auditoria/quarantine_p0a2/service_1_operator_delivery_package_v1.py.txt` | quarantine_provenance | false |
| `docs/auditoria/quarantine_p0a2/test_service_1_operator_delivery_package_v1.py.txt` | quarantine_provenance | false |
| `docs/auditoria/quarantine_p0c/accounting_review_gate_legacy_v1.py.txt` | quarantine_provenance | false |

## DELETE

| Path | Tracked |
|---|---:|
| `docs/auditoria/AUDIT_SERVICE_1_ROBUST_COMPLETION_CENTERLINE_V1.md` | false |
| `docs/auditoria/HASHLINE_HARNESS_POC_V1.md` | false |
| `docs/auditoria/OPERATOR_AND_ACCOUNTING_GATE_CLEANUP_CLOSEOUT_V1.md` | false |
| `docs/auditoria/OPERATOR_PARASITE_FULL_AUDIT_V1.txt` | false |
| `docs/auditoria/OPERATOR_RESCUE_AND_DEATH_BOUNDARY_V1.md` | false |
| `docs/auditoria/P0A2_OWNER_DELIVERY_PACKAGE_CLOSEOUT_V1.md` | false |
| `docs/auditoria/P0A_SERVICE_1_OPERATOR_HARNESS_RENAME_TASKSPEC_V1.md` | false |
| `docs/auditoria/P0B_OPERATOR_HARNESS_V2_FUNCTION_AUDIT_ONLY_V1.md` | false |
| `docs/auditoria/P0B_OPERATOR_HARNESS_V2_RENAME_TASKSPEC_V1.md` | false |
| `docs/auditoria/P0B_OWNER_RELEASE_ACTION_GATE_CLOSEOUT_V1.md` | false |
| `docs/auditoria/P0C_ACCOUNTING_HUMAN_REVIEW_GATE_RENAME_TASKSPEC_V1.md` | false |
| `docs/auditoria/P0C_HUMAN_REVIEW_REVIEWER_ASSISTED_SITUATIONAL_AUDIT_V1.md` | false |
| `docs/auditoria/P0_OPERATOR_CRITICAL_FILE_MATRIX_AUDIT_ONLY_V1.md` | false |
| `docs/auditoria/P0_OPERATOR_REFERENCE_CHECK_AUDIT_ONLY_V1.md` | false |
| `docs/auditoria/SERVICE_1_ASSISTED_COMPLETION_OPERATIONAL_AUDIT_V1.md` | false |
| `docs/auditoria/SERVICE_1_BATCH_016_MULTISHEET_PARITY_REAUDIT_V1.md` | true |
| `docs/auditoria/SERVICE_1_CANONICAL_MULTISHEET_INGESTION_IMPLEMENTATION_V1.md` | true |
| `docs/auditoria/SERVICE_1_MICROCYCLE_ANTI_DRIFT_AUDIT_PROTOCOL_V1.md` | false |
| `docs/auditoria/SERVICE_1_MICROSERVICE_RUNTIME_MATURITY_EXTERNAL_AUDIT_V1.md` | false |
| `docs/auditoria/SERVICE_1_OWNER_CONFIRMATION_BOUNDARY_PLAN_V1.md` | false |
| `docs/auditoria/SERVICE_1_OWNER_CONFIRMATION_BOUNDARY_TEST_PLAN_V1.md` | false |
| `docs/auditoria/SERVICE_1_OWNER_DIALOGUE_AND_REENTRY_AUDIT_V1.md` | false |
| `docs/auditoria/SERVICE_1_PIPELINE_READINESS_GATE_PLAN_V1.md` | false |
| `docs/auditoria/SERVICE_1_PIPELINE_READINESS_GATE_TEST_PLAN_V1.md` | false |
| `docs/auditoria/SERVICE_1_RISKY_MODULES_QUARANTINE_REGISTRY_V1.md` | false |
| `docs/auditoria/SERVICE_1_RUNTIME_CATALOG_BINDING_ADAPTER_PLAN_V1.md` | false |
| `docs/auditoria/SERVICE_1_RUNTIME_CATALOG_BINDING_ADAPTER_TEST_PLAN_V1.md` | false |
| `docs/auditoria/SERVICE_1_RUNTIME_CATALOG_BINDING_CONTRACT_TEST_PLAN_V1.md` | false |
| `docs/auditoria/SERVICE_1_RUNTIME_CATALOG_BINDING_CONTRACT_V1.md` | false |
| `docs/auditoria/SERVICE_1_RUNTIME_CATALOG_LOADER_AUDIT_V1.md` | false |
| `docs/auditoria/SERVICE_1_RUNTIME_CATALOG_MIGRATION_PLAN_V1.md` | false |
| `docs/auditoria/SERVICE_1_RUNTIME_CATALOG_PIPELINE_COMPOSITION_PLAN_V1.md` | false |
| `docs/auditoria/SERVICE_1_RUNTIME_CATALOG_PIPELINE_COMPOSITION_TEST_PLAN_V1.md` | false |
| `docs/auditoria/SERVICE_1_RUNTIME_CATALOG_RECONCILIATION_V1.md` | false |
| `docs/auditoria/SERVICE_1_RUNTIME_CATALOG_TO_SEMANTIC_BINDING_HANDOFF_PLAN_V1.md` | false |
| `docs/auditoria/SERVICE_1_RUNTIME_CATALOG_TO_SEMANTIC_BINDING_HANDOFF_TEST_PLAN_V1.md` | false |
| `docs/auditoria/SERVICE_1_SEMANTIC_BINDING_ACTIVATION_PLAN_V1.md` | false |
| `docs/auditoria/SERVICE_1_SEMANTIC_BINDING_ACTIVATION_TEST_PLAN_V1.md` | false |
| `docs/auditoria/SERVICE_1_SEMANTIC_BINDING_EXECUTION_HARNESS_PLAN_V1.md` | false |
| `docs/auditoria/SERVICE_1_SEMANTIC_BINDING_EXECUTION_HARNESS_TEST_PLAN_V1.md` | false |
| `docs/auditoria/SERVICE_1_SEMANTIC_CATALOG_COVERAGE_AUDIT_V1.md` | false |
| `docs/auditoria/SERVICE_1_SEMANTIC_EVIDENCE_BINDING_FAILURE_AUDIT_V1.md` | false |
| `docs/auditoria/SERVICE_1_SEMANTIC_PIPELINE_CLOSURE_AUDIT_V1.md` | false |
| `docs/auditoria/SERVICE_1_SEMANTIC_PIPELINE_NEXT_BOUNDARY_DECISION_V1.md` | false |
| `docs/auditoria/SERVICE_1_SHADOW_EVIDENCE_TO_OWNER_DIALOGUE_PACKET_TASKSPEC_V1.md` | false |
| `docs/conversa-engine/CONVERSATIONAL_RUNTIME_OFFLINE_E2E.md` | false |
| `docs/hermes/TELEGRAM_EXCEL_STRUCTURAL_PREVIEW.md` | false |
| `docs/microsaas/MICROSAAS_CODE_QUARRIES_CHECKPOINT.md` | false |
| `docs/microsaas/MICROSAAS_PLUGIN_BAY.md` | false |
| `docs/producto/ACCOUNTING_WORKPAPER_COMPLETION_SLICE_V1.md` | false |
| `docs/producto/BANK_RECONCILIATION_SANDBOX_COMPLETION_SLICE_V1.md` | false |
| `docs/producto/DOCUMENT_INGESTION_DUPLICATION_FIX_V1_CLOSEOUT.md` | false |
| `docs/producto/EXCEL_TREATMENT_LAB_COMPLETION_SLICE_V1.md` | false |
| `docs/producto/EXCEL_TREATMENT_LAB_PRODUCT_CONCEPT.md` | false |
| `docs/producto/FIRST_AID_ACTIVATION_SCENARIOS_TEST_V1_CLOSEOUT.md` | false |
| `docs/producto/FIRST_AID_ACTIVATION_SCENARIOS_V1.md` | false |
| `docs/producto/FIRST_AID_MINIMAL_TOOLSET_CLOSEOUT_V1.md` | false |
| `docs/producto/FIRST_AID_OWNER_EXPERIENCE_V1.md` | false |
| `docs/producto/FIRST_AID_PYME_PAIN_AUDIT_V1.md` | false |
| `docs/producto/FIRST_AID_TOOLBOX_ARCHAEOLOGY_EXCELAND_V1.md` | false |
| `docs/producto/FIRST_AID_TOOLBOX_PACK_CONTRACT_V1.md` | true |
| `docs/producto/FIRST_AID_TOOLBOX_RESCUE_WORK_SPLIT_V1.md` | false |
| `docs/producto/FIRST_AID_TOOL_ACTIVATION_EVALUATOR_V1_CLOSEOUT.md` | false |
| `docs/producto/FIRST_AID_TOOL_ACTIVATION_V1.md` | false |
| `docs/producto/INVOICE_COLLECTION_MATCHING_SANDBOX_COMPLETION_SLICE_V1.md` | false |
| `docs/producto/PIPELINE_OWNER_PURE_VIEW_MODULE_CONTRACT_V1.md` | false |
| `docs/producto/PYMIA_PRODUCT_UNIVERSE_AND_SERVICE_DEPTH_MODEL_FINAL.md` | false |
| `docs/producto/PYMIA_SERVICE_1_ARCHAEOLOGY_AUDIT_V1.md` | false |
| `docs/producto/PYMIA_SERVICE_1_CAPABILITY_MATRIX_V1.md` | false |
| `docs/producto/PYMIA_SERVICE_1_CAPABILITY_MATRIX_V2.md` | false |
| `docs/producto/PYMIA_SERVICE_1_EXTERNAL_AUDIT_PROMPTS_V1.md` | false |
| `docs/producto/PYMIA_SERVICE_1_FILE_INTAKE_V1.md` | false |
| `docs/producto/PYMIA_SERVICE_1_FILE_INTAKE_V1_AUDIT.md` | false |
| `docs/producto/PYMIA_SERVICE_1_FULL_CATALOG_V1.md` | false |
| `docs/producto/PYMIA_SERVICE_1_IMPLEMENTATION_INTEGRATION_PLAN_V1.md` | false |
| `docs/producto/PYMIA_SERVICE_1_OPERATIONAL_FSM_V1.md` | false |
| `docs/producto/PYMIA_SERVICE_1_TASKSPEC_V1.md` | false |
| `docs/producto/S2_RECONCILIATION_ASSISTED_REVIEW_BLOCK_CLOSEOUT_V1.md` | false |
| `docs/producto/S2_RECONCILIATION_ASSISTED_REVIEW_DELIVERY_PACKET_CLOSEOUT_V1.md` | false |
| `docs/producto/SERVICE_1_ACCOUNTING_CONTRACT_FAMILY_CLOSURE_V1.md` | false |
| `docs/producto/SERVICE_1_ACCOUNTING_HUMAN_REVIEW_GATE_V1.md` | false |
| `docs/producto/SERVICE_1_ACCOUNTING_RUNTIME_MATRIX_V1.md` | false |
| `docs/producto/SERVICE_1_ACCOUNTING_SANDBOX_PATTERN_V1.md` | false |
| `docs/producto/SERVICE_1_ACCOUNTING_WORKPAPER_DRAFT_PACKET_V1.md` | false |
| `docs/producto/SERVICE_1_ACCOUNTING_WORKPAPER_MANIFEST_MODEL_V1.md` | false |
| `docs/producto/SERVICE_1_ACCOUNTING_WORKPAPER_OPERATOR_RUNBOOK_V1.md` | false |
| `docs/producto/SERVICE_1_ACCOUNTING_WORKPAPER_OWNER_OPERATOR_WORDING_REFINEMENT_V1.md` | false |
| `docs/producto/SERVICE_1_ACCOUNTING_WORKPAPER_PRODUCT_CLOSEOUT_V1.md` | false |
| `docs/producto/SERVICE_1_ACCOUNTING_WORKPAPER_PUBLIC_OFFER_COPY_V1.md` | false |
| `docs/producto/SERVICE_1_ACCOUNTING_WORKPAPER_REAL_CLIENT_OPERATOR_PACKET_V1.md` | false |
| `docs/producto/SERVICE_1_ACCOUNTING_WORKPAPER_SANDBOX_PATTERN_V1.md` | false |
| `docs/producto/SERVICE_1_ACCOUNTING_WORKPAPER_SYNTHETIC_EDGE_CASE_SERIES_V1.md` | false |
| `docs/producto/SERVICE_1_ACCOUNTING_XLSX_RUNTIME_V1_DESIGN.md` | false |
| `docs/producto/SERVICE_1_AGENT_BOOTSTRAP.md` | false |
| `docs/producto/SERVICE_1_ALIGNED_OWNER_PROMPT_DISPLAY_PACKET_V1.md` | false |
| `docs/producto/SERVICE_1_AUTONOMOUS_SAAS_ORCHESTRATION_TRACE_AUDIT_V1.md` | false |
| `docs/producto/SERVICE_1_AUTONOMOUS_SAAS_ORCHESTRATION_TRACE_REUSE_MAP_V1.md` | false |
| `docs/producto/SERVICE_1_BANK_RECONCILIATION_SANDBOX_FIXTURE_HANDOFF_V1.md` | false |
| `docs/producto/SERVICE_1_BANK_RECONCILIATION_SANDBOX_FIXTURE_MODEL_V1.md` | false |
| `docs/producto/SERVICE_1_BANK_RECONCILIATION_SANDBOX_REVIEW_PACKET_V1.md` | false |
| `docs/producto/SERVICE_1_BANK_RECONCILIATION_SANDBOX_RUNTIME_CONTRACT_V1.md` | false |
| `docs/producto/SERVICE_1_BASELINE_CORRECTION_MINIMAL_PATCH_V1.md` | false |
| `docs/producto/SERVICE_1_CAJA_DIARIA_POR_FECHA_CLOSEOUT_V1.md` | false |
| `docs/producto/SERVICE_1_CANDIDATE_TOOLS_TO_CONTROLLED_EXECUTION_BRIDGE_CLOSEOUT_V1.md` | false |
| `docs/producto/SERVICE_1_CAPABILITY_COMPLETION_MATRIX_V1.md` | false |
| `docs/producto/SERVICE_1_CAPABILITY_MATURITY_AUDIT_V1.md` | false |
| `docs/producto/SERVICE_1_CASE_FOLDER_MANIFEST_CONTRACT_V1.md` | false |
| `docs/producto/SERVICE_1_CASE_FOLDER_MANIFEST_V1.md` | false |
| `docs/producto/SERVICE_1_CASE_REENTRY_READ_MODEL_V1.md` | false |
| `docs/producto/SERVICE_1_CODE_DOC_CONFRONTATION_AUDIT_V1.md` | false |
| `docs/producto/SERVICE_1_COLUMN_CONFIRMATION_APPLIER_V1.md` | false |
| `docs/producto/SERVICE_1_COLUMN_CONFIRMATION_CASE_PATCH_V1.md` | false |
| `docs/producto/SERVICE_1_COLUMN_CONFIRMATION_CLASSIFIER_V1.md` | false |
| `docs/producto/SERVICE_1_COLUMN_CONFIRMATION_OWNER_PROMPT_BATCH_V1.md` | false |
| `docs/producto/SERVICE_1_COLUMN_CONFIRMATION_OWNER_PROMPT_V1.md` | false |
| `docs/producto/SERVICE_1_COLUMN_CONFIRMATION_REENTRY_ACCEPTANCE_TEST_DESIGN_V1.md` | false |
| `docs/producto/SERVICE_1_COLUMN_CONFIRMATION_REENTRY_AUDIT_V1.md` | false |
| `docs/producto/SERVICE_1_COLUMN_CONFIRMATION_REENTRY_CAPABILITYSPEC_V1.md` | false |
| `docs/producto/SERVICE_1_COLUMN_INTERPRETATION_TO_OWNER_PROMPT_BRIDGE_V1.md` | false |
| `docs/producto/SERVICE_1_COMMERCIAL_OFFER_V1.md` | false |
| `docs/producto/SERVICE_1_COMPLETION_DEFINITION_OF_DONE_V1.md` | false |
| `docs/producto/SERVICE_1_CURRENT_CHECKPOINT_AFTER_DISPLAY_PACKET_V1.md` | false |
| `docs/producto/SERVICE_1_CURRENT_STATE_V1.md` | false |
| `docs/producto/SERVICE_1_DELIVERY_MANIFEST_AUDIT_CONTRACT_V1.md` | false |
| `docs/producto/SERVICE_1_DELIVERY_MANIFEST_AUDIT_V1.md` | false |
| `docs/producto/SERVICE_1_DEVELOPMENT_AUDIT_AND_COMPLETION_ROADMAP_V1.md` | false |
| `docs/producto/SERVICE_1_DOCUMENTATION_CONTROL_V1.md` | false |
| `docs/producto/SERVICE_1_DOCUMENT_CURATION_REPORT_TO_OWNER_PROMPT_BATCH_BRIDGE_V1.md` | false |
| `docs/producto/SERVICE_1_END_TO_END_DRY_RUN_V1.md` | false |
| `docs/producto/SERVICE_1_EVIDENCE_PROFILE_TO_CANDIDATE_TOOLS_CONTRACT_CLOSEOUT_V1.md` | false |
| `docs/producto/SERVICE_1_EXCELAND_BRIDGE_V1.md` | false |
| `docs/producto/SERVICE_1_EXCEL_FACTORY_COMMERCIAL_CATALOG_V1.md` | false |
| `docs/producto/SERVICE_1_EXCEL_LAB_CLOSEOUT_V1.md` | false |
| `docs/producto/SERVICE_1_EXCEL_TREATMENT_LAB_PRODUCTIZATION_V1.md` | false |
| `docs/producto/SERVICE_1_EXECUTABLE_ENTRYPOINT_V1.md` | false |
| `docs/producto/SERVICE_1_FIRST_AID_FAMILY_CLOSEOUT_V1.md` | false |
| `docs/producto/SERVICE_1_FIRST_AID_FAMILY_CLOSURE_V1.md` | false |
| `docs/producto/SERVICE_1_FIRST_AID_LANE_CLOSEOUT_V1.md` | false |
| `docs/producto/SERVICE_1_FULL_ASSISTED_V1_CLOSEOUT_DECLARATION.md` | false |
| `docs/producto/SERVICE_1_FULL_ASSISTED_V1_FINAL_DECLARATION.md` | false |
| `docs/producto/SERVICE_1_FULL_ASSISTED_V1_FINAL_DECLARATION_WITH_LIMITS.md` | false |
| `docs/producto/SERVICE_1_FULL_ASSISTED_V1_HARDENING_CLOSEOUT.md` | false |
| `docs/producto/SERVICE_1_FULL_CLOSURE_RECTOR_V1.md` | false |
| `docs/producto/SERVICE_1_FULL_LAYERED_IMPLEMENTATION_TRACE_V1.md` | false |
| `docs/producto/SERVICE_1_FULL_OPERATOR_PLAYBOOK_V1.md` | false |
| `docs/producto/SERVICE_1_LIVE_CHAIN_MAP_V1.md` | false |
| `docs/producto/SERVICE_1_LIVE_CHAIN_MAP_V2.md` | false |
| `docs/producto/SERVICE_1_MANUAL_OPERATOR_RUNBOOK_V1.md` | false |
| `docs/producto/SERVICE_1_MATURITY_CLOSEOUT_POST_EXCEL_TREATMENT_LAB_V1.md` | false |
| `docs/producto/SERVICE_1_MATURITY_MAP_POST_INVOICE_COLLECTION_V1.md` | false |
| `docs/producto/SERVICE_1_MICROSERVICE_ACTIVATION_CONTRACT_V1.md` | false |
| `docs/producto/SERVICE_1_MICROSERVICE_CHAIN_DRY_RUN_V1.md` | false |
| `docs/producto/SERVICE_1_MICROSERVICE_REGISTRY_CONTRACT_V1.md` | false |
| `docs/producto/SERVICE_1_OPERATOR_DELIVERY_PACKAGE_BLOCK_V1.md` | false |
| `docs/producto/SERVICE_1_OPERATOR_HARNESS_REAL_OUTPUT_AUDIT_V1.md` | false |
| `docs/producto/SERVICE_1_OPERATOR_HARNESS_V2_DESIGN.md` | false |
| `docs/producto/SERVICE_1_OPERATOR_HARNESS_V2_MINIMAL_CONTRACT.md` | false |
| `docs/producto/SERVICE_1_OPERATOR_HARNESS_V2_SYNTHETIC_DRY_RUN.md` | false |
| `docs/producto/SERVICE_1_OPERATOR_READY_PACKET_V1.md` | false |
| `docs/producto/SERVICE_1_OPERATOR_RUNBOOK_V1.md` | false |
| `docs/producto/SERVICE_1_OWNER_ANSWER_REENTRY_PERSISTENCE_V1.md` | false |
| `docs/producto/SERVICE_1_OWNER_ANSWER_REENTRY_V1.md` | false |
| `docs/producto/SERVICE_1_OWNER_CONVERSATION_LAYER_CONTRACT_V1.md` | true |
| `docs/producto/SERVICE_1_OWNER_FACING_DELIVERY_TEMPLATE_V1.md` | true |
| `docs/producto/SERVICE_1_OWNER_FACING_ROLE_EXPLANATION_CATALOG_V1.md` | false |
| `docs/producto/SERVICE_1_OWNER_OUTPUT_CLOSEOUT_V1.md` | false |
| `docs/producto/SERVICE_1_OWNER_PROMPT_BATCH_TO_QUESTION_BUNDLE_ALIGNMENT_V1.md` | false |
| `docs/producto/SERVICE_1_OWNER_RECTIFIED_EVIDENCE_PROFILE_CONTRACT_CLOSEOUT_V1.md` | false |
| `docs/producto/SERVICE_1_OWNER_RECTIFIED_SEMANTIC_FUNCTIONS_CONTRACT_PATCH_V1.md` | false |
| `docs/producto/SERVICE_1_OWNER_RECTIFIED_SEMANTIC_FUNCTIONS_RULE_V1.md` | false |
| `docs/producto/SERVICE_1_OWNER_RECTIFIED_SEMANTIC_FUNCTIONS_RUNTIME_PATCH_CLOSEOUT_V1.md` | false |
| `docs/producto/SERVICE_1_PAQUETE_ENTREGA_CLIENTE_ESTANDAR_V1.md` | true |
| `docs/producto/SERVICE_1_PATHOLOGY_CATALOG_INTEGRATION_V1.md` | true |
| `docs/producto/SERVICE_1_PATHOLOGY_SHADOW_ARTIFACT_CLOSEOUT_V1.md` | false |
| `docs/producto/SERVICE_1_PATHOLOGY_SHADOW_ARTIFACT_EVALUATION_AUDIT_V1.md` | false |
| `docs/producto/SERVICE_1_PATHOLOGY_SHADOW_ARTIFACT_MODULE_CONTRACT_V1.md` | false |
| `docs/producto/SERVICE_1_PATHOLOGY_SHADOW_ARTIFACT_TASKSPEC_V1.md` | false |
| `docs/producto/SERVICE_1_PATHOLOGY_SHADOW_MODE_V1.md` | false |
| `docs/producto/SERVICE_1_POST_PATHOLOGY_SHADOW_ROADMAP_ALIGNMENT_V1.md` | false |
| `docs/producto/SERVICE_1_POST_SLICES_STATE_CLOSEOUT_V1.md` | false |
| `docs/producto/SERVICE_1_POST_TOOL_OWNER_DELIVERY_SUMMARY_CLOSEOUT_V1.md` | false |
| `docs/producto/SERVICE_1_POST_TOOL_OWNER_DELIVERY_SUMMARY_V1.md` | false |
| `docs/producto/SERVICE_1_PRODUCTIZATION_PACK_V1.md` | false |
| `docs/producto/SERVICE_1_PROVEEDORES_PRECIO_VARIACION_TRIAGE_NEXT_FRONT_V1.md` | false |
| `docs/producto/SERVICE_1_QA_CLAIMS_AND_REPRESENTATIVE_DELIVERY_CASE_V1.md` | false |
| `docs/producto/SERVICE_1_QA_DELIVERY_CHECKLIST_V1.md` | true |
| `docs/producto/SERVICE_1_QUESTION_BUNDLE_AND_REF_V1.md` | false |
| `docs/producto/SERVICE_1_REENTRY_PROJECTION_V1.md` | false |
| `docs/producto/SERVICE_1_REVIEW_CHECKLIST_V1.md` | false |
| `docs/producto/SERVICE_1_RUNTIME_GOVERNANCE_V1.md` | false |
| `docs/producto/SERVICE_1_SAAS_ADAPTER_CODE_DOC_ALIGNMENT_AUDIT_V1.md` | false |
| `docs/producto/SERVICE_1_SAAS_JOB_TO_PIPELINE_REQUEST_ADAPTER_CONTRACT_V1.md` | false |
| `docs/producto/SERVICE_1_STAGE_4_EXCEL_FACTORY_CLOSEOUT_V1.md` | false |
| `docs/producto/SERVICE_1_STAGE_5_CLOSEOUT_V1.md` | false |
| `docs/producto/SERVICE_1_SYNTHETIC_DELIVERY_LLM_REVIEW_V1.md` | false |
| `docs/producto/SERVICE_1_SYNTHETIC_REAL_CASE_RUN_CLOSEOUT_V1.md` | false |
| `docs/producto/SERVICE_1_SYNTHETIC_XLSX_EDGE_CASE_RUN_V2.md` | false |
| `docs/producto/SERVICE_1_TOOLBOX_AND_COMMERCIAL_MODULES_BOUNDARY_V1.md` | false |
| `docs/producto/SERVICE_1_VALIDATION_CASE_CORPUS_V1.md` | true |
| `docs/producto/SERVICE_1_WEB_TEST_INTERFACE_DESIGN_V1.md` | false |
| `docs/producto/SERVICE_1_WEB_TEST_INTERFACE_ROUTE_REGISTRY_V1.md` | false |
| `docs/producto/SERVICE_1_WEB_TEST_INTERFACE_RUN_SPEC_V1.md` | false |
| `docs/producto/SERVICE_1_XLSX_BROWSER_SANDBOX_LANDING_V1.md` | false |
| `docs/producto/SERVICE_1_XLSX_OWNER_CHAT_BROWSER_V1.md` | false |
| `docs/producto/SERVICE_2_ADMIN_OPERATIONS_FOUNDATION_V1.md` | false |
| `docs/producto/SERVICE_2_RECONCILIATION_BOUNDARY_CONTRACT_V1.md` | false |
| `docs/producto/SERVICE_2_RECONCILIATION_MATCH_CANDIDATES_CLOSEOUT_V1.md` | false |
| `docs/prompts/M29_REPORTE_MINIMO_ENTREGABLE_AGENT_PROMPT.md` | false |
| `docs/pymia/C1_FAITHFUL_OPERATOR_CATALOG_RECONCILIATION_CHECKPOINT.md` | false |
| `docs/pymia/C1_FAITHFUL_OPERATOR_CATALOG_RECONCILIATION_task.md` | false |
| `docs/pymia/C1_FAITHFUL_OPERATOR_CATALOG_RECONCILIATION_TASKSPEC.md` | false |
| `docs/pymia/C2_OWNER_FACING_CATALOG_RECONCILIATION_SUMMARY_CHECKPOINT.md` | false |
| `docs/pymia/C2_OWNER_FACING_CATALOG_RECONCILIATION_SUMMARY_TASKSPEC.md` | false |
| `docs/pymia/C3_OWNER_CONFIRMATION_BOUNDARY_FOR_CATALOG_SUMMARY_CHECKPOINT.md` | false |
| `docs/pymia/C3_OWNER_CONFIRMATION_BOUNDARY_FOR_CATALOG_SUMMARY_TASKSPEC.md` | false |
| `docs/pymia/FUNCTIONAL_GRAPH_PACK_MINIMAL_V1_CONTRACT.md` | false |
| `docs/pymia/GENTLE_AI_DISCIPLINE_ADOPTION.md` | false |
| `docs/pymia/M34_DIAGNOSTIC_CORE_V1_CLOSURE.md` | false |
| `docs/pymia/M34_DIAGNOSTIC_CORE_V1_TASKSPEC.md` | false |
| `docs/pymia/M34_S10_INV001_PUNTO_REPOSICION_TASKSPEC.md` | false |
| `docs/pymia/M34_S11_PUNTO_EQUILIBRIO_VENTAS_TASKSPEC.md` | false |
| `docs/pymia/M34_S12_PYME026_FLUJO_OPERATIVO_TASKSPEC.md` | false |
| `docs/pymia/M34_S13_PYME027_INTERESES_EBITDA_TASKSPEC.md` | false |
| `docs/pymia/M34_S14_PYME044_MARGEN_CLIENTE_TASKSPEC.md` | false |
| `docs/pymia/M34_S15_PYME033_CONCENTRACION_SKU_TASKSPEC.md` | false |
| `docs/pymia/M34_S16_REN002_COEFICIENTE_REPOSICION_TASKSPEC.md` | false |
| `docs/pymia/M34_S2_REN001_TASKSPEC.md` | false |
| `docs/pymia/M34_S3_LIQ001_TASKSPEC.md` | false |
| `docs/pymia/M34_S4_INV002_TASKSPEC.md` | false |
| `docs/pymia/M34_S5_PYME011_DSO_TASKSPEC.md` | false |
| `docs/pymia/M34_S6_PYME013_DSO_DPO_GAP_TASKSPEC.md` | false |
| `docs/pymia/M34_S7_LIQ002_SALDO_FINAL_PROYECTADO_TASKSPEC.md` | false |
| `docs/pymia/M34_S8_PYME024_LIQUIDEZ_CORRIENTE_TASKSPEC.md` | false |
| `docs/pymia/M34_S9_PYME017_PRICING_DRIFT_TASKSPEC.md` | false |
| `docs/pymia/M35_EVIDENCE_TO_CORE_CHECKPOINT.md` | false |
| `docs/pymia/M35_S1_STRUCTURED_EVIDENCE_TO_DIAGNOSTIC_CORE_INPUT_TASKSPEC.md` | false |
| `docs/pymia/M35_S2_STRUCTURED_EVIDENCE_CORE_EXECUTION_FIXTURE_TASKSPEC.md` | false |
| `docs/pymia/M35_S3_FORMULA_SCOPED_SOURCE_REFS_TASKSPEC.md` | false |
| `docs/pymia/M35_S4_EXCEL_FIXTURE_TO_CORE_EXECUTION_TASKSPEC.md` | false |
| `docs/pymia/M35_S5_EXTEND_EVIDENCE_BINDING_NEW_FORMULAS_TASKSPEC.md` | false |
| `docs/pymia/M35_S6_EVIDENCE_SUFFICIENCY_REPORT_TASKSPEC.md` | false |
| `docs/pymia/OWNER_CONFIRMED_SEMANTIC_REQUEST_FLOW_CHECKPOINT.md` | false |
| `docs/pymia/OWNER_CONFIRMED_SEMANTIC_REQUEST_OWNER_FACING_PROJECTION_CHECKPOINT.md` | false |
| `docs/pymia/OWNER_SEMANTIC_CONFIRMATION_GATE_CHECKPOINT.md` | false |
| `docs/pymia/OWNER_SEMANTIC_CONFIRMATION_GATE_TASKSPEC.md` | false |
| `docs/pymia/OWNER_SEMANTIC_CONFIRMATION_REENTRY_PROJECTION_CHECKPOINT.md` | false |
| `docs/pymia/OWNER_SEMANTIC_EVIDENCE_REQUESTS_CONTRACT_CHECKPOINT.md` | false |
| `docs/pymia/OWNER_SEMANTIC_EVIDENCE_REQUESTS_CONTRACT_TASKSPEC.md` | false |
| `docs/pymia/OWNER_SEMANTIC_EVIDENCE_REQUEST_BUILDER_CHECKPOINT.md` | false |
| `docs/pymia/P1_AUDIT_CHECKPOINT.md` | false |
| `docs/pymia/P1_FIRST_REPORT_BOUNDARY.md` | false |
| `docs/pymia/P1_FIRST_REPORT_SCHEMA.md` | false |
| `docs/pymia/P1_INITIAL_DIAGNOSIS_CONTRACT.md` | false |
| `docs/pymia/P1_REENTRY_CHECKPOINT.md` | false |
| `docs/pymia/P1_SCHEMA_INITIAL_DIAGNOSIS.md` | false |
| `docs/pymia/PYMIA_FAITHFUL_OPERATOR_ASSISTED_PACKET_EXAMPLE.md` | false |
| `docs/pymia/PYMIA_FAITHFUL_OPERATOR_ASSISTED_RUNBOOK.md` | false |
| `docs/pymia/PYMIA_FAITHFUL_OPERATOR_LOCAL_DEMO_CHECKPOINT.md` | false |
| `docs/pymia/PYMIA_FAITHFUL_OPERATOR_V1_PLAN.md` | false |
| `docs/pymia/PYMIA_RESIDENT_AI_HARNESS_ENGINEERING.md` | false |
| `docs/pymia/PYMIA_RESIDENT_INTELLIGENCE_CONTRACT.md` | false |
| `docs/pymia/PYMIA_SUPRACORTEX_NEUROSOFTWARE.md` | false |
| `docs/pymia/SERVICE_1_COLUMN_CONFIRMATION_OWNER_PROMPT_BATCH_V1_CAPABILITYSPEC.md` | false |
| `docs/pymia/SERVICE_1_COLUMN_CONFIRMATION_OWNER_PROMPT_BATCH_V1_MODULECONTRACT.md` | false |
| `docs/pymia/SERVICE_1_COLUMN_CONFIRMATION_OWNER_PROMPT_BATCH_V1_TASKSPEC.md` | false |
| `docs/pymia/SERVICE_1_DOCUMENT_CURATION_REPORT_TO_OWNER_PROMPT_BATCH_BRIDGE_V1_CAPABILITYSPEC.md` | false |
| `docs/pymia/SERVICE_1_DOCUMENT_CURATION_REPORT_TO_OWNER_PROMPT_BATCH_BRIDGE_V1_MODULECONTRACT.md` | false |
| `docs/pymia/SERVICE_1_DOCUMENT_CURATION_REPORT_TO_OWNER_PROMPT_BATCH_BRIDGE_V1_TASKSPEC.md` | false |
| `docs/pymia/SERVICE_1_OWNER_PROMPT_BATCH_TO_QUESTION_BUNDLE_ALIGNMENT_V1_CAPABILITYSPEC.md` | false |
| `docs/pymia/SERVICE_1_OWNER_PROMPT_BATCH_TO_QUESTION_BUNDLE_ALIGNMENT_V1_MODULECONTRACT.md` | false |
| `docs/pymia/SERVICE_1_OWNER_PROMPT_BATCH_TO_QUESTION_BUNDLE_ALIGNMENT_V1_TASKSPEC.md` | false |
| `docs/pymia/SERVICE_1_XLSX_NORMALIZATION_SOURCE_OF_TRUTH_LOCK_V1_MODULECONTRACT.md` | false |
| `docs/pymia/START_HERE_FOR_AGENTS.md` | false |
| `docs/refactor/SERVICE_1_SEMANTIC_EVIDENCE_BINDING_RECOVERY_BRIEF_V1.md` | false |
| `docs/roadmap/GENETIC_TEST_COVERAGE_AUDIT.md` | false |
| `docs/roadmap/M27_EXCEL_SEMANTICA_DUENO_PLAN.md` | false |
| `docs/roadmap/M29_REPORTE_MINIMO_ENTREGABLE_PLAN.md` | false |
| `docs/roadmap/M30_CONTINUIDAD_DEL_CASO_PLAN.md` | false |
| `docs/roadmap/ROADMAP_SERVICIO_ASISTIDO_EXCEL_SEMANTICA_PYME.md` | false |
| `docs/smartpyme/CONVERSA_REAL_RECALL_SMOKE.md` | false |
| `docs/smartpyme/M17_SUPPLIER_DISPATCHER_INTEGRATION_AUDIT.md` | false |
| `docs/smartpyme/M17_SUPPLIER_DISPATCHER_INTEGRATION_CHECKPOINT.md` | false |
| `docs/smartpyme/M19_5_NEGATIVE_SCENARIOS_AUDIT.md` | false |
| `docs/smartpyme/M19_5_NEGATIVE_SCENARIOS_CHECKPOINT.md` | false |
| `docs/smartpyme/M19_6_DEVELOPER_REPORT_AUDIT.md` | false |
| `docs/smartpyme/M19_6_DEVELOPER_REPORT_CHECKPOINT.md` | false |
| `docs/smartpyme/M19_7_SINGLE_COMMAND_AUDIT.md` | false |
| `docs/smartpyme/M19_8_PIPELINE_RADIOGRAPHY_CI_AUDIT.md` | false |
| `docs/smartpyme/M19_8_PIPELINE_RADIOGRAPHY_CI_CHECKPOINT.md` | false |
| `docs/smartpyme/M19_CONTRACT_MAP.md` | false |
| `docs/smartpyme/M19_INTERNAL_TEST_DRIVE_DECISION.md` | false |
| `docs/smartpyme/M19_PIPELINE_RADIOGRAPHY_CHECKPOINT.md` | false |
| `docs/smartpyme/M19_PIPELINE_RADIOGRAPHY_WORKPACK.md` | false |
| `docs/smartpyme/M20_MACHINE_READABLE_REGISTRY_AUDIT.md` | false |
| `docs/smartpyme/M20_MACHINE_READABLE_REGISTRY_CHECKPOINT.md` | false |
| `docs/smartpyme/M21_MINIMAL_OPERATIONAL_HARNESS_AUDIT.md` | false |
| `docs/smartpyme/M21_OPERATIONAL_HARNESS_CHECKPOINT.md` | false |
| `docs/smartpyme/M22_REGISTRY_HARDENING_CHECKPOINT.md` | false |
| `docs/smartpyme/M23_CI_INTEGRATION_CHECKPOINT.md` | false |
| `docs/smartpyme/M23_NEXT_MILESTONE_AUDIT.md` | false |
| `docs/smartpyme/M24_NEXT_MILESTONE_AUDIT.md` | false |
| `docs/smartpyme/M26_TENANT_CONTINUITY_ACCEPTANCE_CHECKPOINT.md` | false |
| `docs/smartpyme/M27_A_TEXTILE_CASE_UNDERSTANDING_CHECKPOINT.md` | false |
| `docs/smartpyme/M27_EXCEL_SEMANTICA_DUENO_CHECKPOINT.md` | false |
| `docs/smartpyme/M28_EXPLICABLE_FINDING_CHECKPOINT.md` | false |
| `docs/smartpyme/M29_REPORTE_MINIMO_ENTREGABLE_CHECKPOINT.md` | false |
| `docs/smartpyme/M30_CONTINUIDAD_DEL_CASO_CHECKPOINT.md` | false |
| `docs/smartpyme/M31C_CHECKPOINT.md` | false |
| `docs/smartpyme/M31C_MINIMUM_DELIVERABLE_TEMPLATE.md` | false |
| `docs/smartpyme/M31C_PROSPECT_FIT_CRITERIA.md` | false |
| `docs/smartpyme/M31P_CASE_SELECTION_CRITERIA.md` | false |
| `docs/smartpyme/M31P_CHECKPOINT.md` | false |
| `docs/smartpyme/M31P_OPERATIVE_INTERNAL_CHECKPOINT.md` | false |
| `docs/smartpyme/M31P_OPERATOR_RUNBOOK.md` | false |
| `docs/smartpyme/M31_CLOSURE_CLARIFICATION.md` | false |
| `docs/smartpyme/M31_SERVICIO_ASISTIDO_REPETIBLE_CHECKPOINT.md` | false |
| `docs/smartpyme/M32S_SIMULACION_INTERACTIVA_PLAN.md` | false |
| `docs/smartpyme/PRODUCT_CONTRACT_V0.md` | false |
| `docs/smartpyme/SMARTPYME_ANAMNESIS_FSM_OFFLINE.md` | false |
| `docs/smartpyme/SMARTPYME_DETERMINISTIC_PIPELINE_CONTRACT.md` | false |
| `docs/smartpyme/SMARTPYME_E2E_NON_EXECUTING_FLOW.md` | false |
| `docs/smartpyme/SMARTPYME_EVIDENCE_STORAGE_PERSISTENCE.md` | false |
| `docs/smartpyme/SMARTPYME_INTAKE_STORAGE_PERSISTENCE.md` | false |
| `docs/smartpyme/SMARTPYME_MEMORY_RUNTIME_SMOKE.md` | false |
| `docs/smartpyme/SMARTPYME_ONE_MICROSERVICE_EXECUTION_SMOKE.md` | false |
| `docs/smartpyme/SMARTPYME_PIPELINE_RADIOGRAPHY_IMPLEMENTATION_PLAN.md` | false |
| `docs/smartpyme/SMARTPYME_RUNTIME_BRIDGE_MINIMAL.md` | false |
| `docs/smartpyme/SMARTPYME_SEMANTIC_DIALECTIC_PHASE.md` | false |
| `docs/smartpyme/SMARTPYME_SUPPLIER_DUPLICATE_CHECK_SPEC.md` | false |
| `docs/smartpyme/SUPERMEMORY_REAL_API_SMOKE.md` | false |
| `docs/smartpyme/SUPERMEMORY_RECALL_MATCH_SMOKE.md` | false |
| `docs/pymia/cases/PYMIA_ASSISTED_CASES_INDEX.md` | false |
| `docs/pymia/cases/PYMIA_ASSISTED_CASE_NEXT_ACTION_BOARD.md` | false |
| `docs/pymia/cases/PYMIA_ASSISTED_CASE_TEMPLATE.md` | false |
| `docs/pymia/cases/PYMIA_CASE_CAFETERIA_ABC_ASSISTED.md` | false |
| `docs/pymia/cases/PYMIA_CASE_CAFETERIA_ABC_MARGIN_FOCUS.md` | false |
| `docs/pymia/cases/PYMIA_CASE_CAFETERIA_ABC_OWNER_SESSION.md` | false |
| `docs/pymia/cases/PYMIA_CASE_CAFETERIA_ABC_SESSION_RECORD.md` | false |
| `docs/pymia/motherboard/DRAFT_NOT_APPROVED_00_CONSTITUTION.md` | false |
| `docs/pymia/motherboard/DRAFT_NOT_APPROVED_01_INVARIANTS.md` | false |

## Safety gate before execution

Before physical deletion of the 340 `DELETE` paths:

1. re-run this audit against the then-current worktree;
2. verify no candidate gained a current/reference/code/test incoming reference;
3. protect any path that became actively modified;
4. delete only the exact audited paths, never by wildcard directory purge;
5. run `git diff --check` and the documentary/architecture tests afterward.

## Next action

```text
EXECUTE_HISTORICAL_DOC_DELETE_BATCH_V1
```

This audit itself does not authorize deletion of files whose classification changes after this snapshot.
