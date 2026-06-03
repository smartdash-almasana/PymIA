# PymIA — Genetic Test Coverage Audit

## Estado

AUDIT_ONLY

## Resumen ejecutivo

| GEN | Capacidad | Estado | Evidencia principal | Hueco principal |
|---|---|---|---|---|
| GEN01 | Recepción | [x] | Anamnesis FSM + intake storage + reception + interrogation (~40 tests) | No hay E2E multi-formato (archivo + mensaje + metadata) |
| GEN02 | Clasificación | [x] | Interrogación con 8 escenarios, taxonomy, tank_selection, profile-to-selectors | Clasificación embebida en interrogación, sin módulo autónomo testeable |
| GEN03 | Evidencia | [x] | 8 archivos de test (~2200 líneas), post_ficha_evidence_gate es el más completo del repo | Ninguno significativo |
| GEN04 | Hallazgos | [-] | Finding projection, excel_diagnostic, delivery, execution gate tienen tests | narrative/report_generator* solo cobertura parcial; no hay test de hallazgos multi-tenant |
| GEN05 | Memoria operacional | [-] | Supermemory client + state_storage + conversation_contract + decision_record | No hay test cross-session continuity; "decisiones vigentes" sin test formal |
| GEN06 | Aprendizaje | [-] | KnowledgeItem (359 líneas) + LearningCycle (316 líneas) + pathology engine | Sin E2E de "evidencia repetida → mejora gobernada"; ciclo de aprobación humana sin test |
| GEN07 | Intervención | [-] | InterventionPlan + DecisionRecord + microservice dispatcher smoke | Sin flujo único "diagnóstico → intervención → ejecución"; no integrado con dispatcher |
| GEN08 | Gobernanza | [x] | 33 tests de dominio + architecture guardrails + 9 tests SCN + contracts | "Engramas" es abstracción sin test; DoD es metodología, no código |
| GEN09 | Producto SmartPyme | [-] | E2E CLI + pipeline radiography excel + 11 tests de orquestación | Sin E2E multi-tenant; sin test de aceptación del flujo de producto completo |

Regla de corte: GEN01–GEN05 tienen 3 de 5 en estado [x] (60%). El umbral del 40% no se activa para forzar consolidación básica. Sin embargo, GEN04 y GEN05 en [-] indican que la cadena de valor central (hallazgo → entrega → trazabilidad) tiene gaps que M26 debe considerar antes de escalar a GEN06–GEN09.

---

## Inventario de tests

| Carpeta | Archivos detectados | Tema aparente | Observaciones |
|---|---:|---|---|
| tests/ | 22 | Tests raíz, guardrails, conversaciones, narrativa | Mezcla de tests de fronteras y smoke tests |
| tests/architecture/ | 2 | Forbidden imports/terms | Guardrails arquitectónicos del proyecto |
| tests/contracts/ | 1 | Attachment lifecycle contract | Contratos entre módulos |
| tests/docs/ | 1 | Conversational contract | Test de contrato conversacional |
| tests/document_intelligence/ | 6 | Document intelligence phases 2b/2c/2d/2f | Capacidad futura no certificada |
| tests/domain/ | 33 | Entities, primitives, snapshots, types | Capa de dominio pura con cobertura densa |
| tests/fixtures/ | 2 | owner_claims.py, smartpyme/ | Datos de prueba compartidos |
| tests/golden_findings/ | 1 | la_textil_expected.json | Golden replay fixture |
| tests/hermes/ | 8 | Telegram bridge, attachment lifecycle, audit router | Bridge a Telegram (no tocar) |
| tests/interfaces/ | 1 | Conversational port | Interface abstracta |
| tests/llm_operator/ | 3 | OpenRouter provider, operator offline, smoke | LLM integration (no tocar) |
| tests/mcp/ | 1 | First clinical interview MCP server | Servidor MCP, fuera de scope actual |
| tests/microsaas/ | 1 | Microsaas registry | Registro de microservicios |
| tests/orchestration/ | 11 | State, graph, conversation adapter, OS tools, E2E longitudinal | Capa de orquestación |
| tests/pipeline/ | 2 | Admission pipeline v1 + response formatter | Pipeline de admisión |
| tests/scn/ | 9 | SCN contracts, render, runtime policy, audit | Contratos SCN del sistema |
| tests/scripts/ | 1 | Sandbox smoke test | Sandbox de pruebas |
| tests/services/ | 8 | Formula engine, anamnesis, pathology, diagnostic report | Servicios clínicos |
| tests/smartpyme/ | 44 | Cobertura principal del dominio SmartPyme | Núcleo de negocio |
| tests/smartpyme/e2e/ | 1 | Pipeline radiography excel E2E | Test E2E del pipeline completo |
| tests/telegram_runtime/ | 5 | Bot runtime, document handler, excel handler, summary | Telegram runtime (no tocar) |
| tests/utils/ | 1 | golden_replay_utils.py | Utilidades de replay |

Total: ~157 archivos de test.

---

## Mapeo por capacidad genética

### GEN01 — Recepción

| Test file | Módulo/comportamiento | Estado | Evidencia | Hueco |
|---|---|---|---|---|
| test_reception.py | create_reception + validaciones | [x] | 32 líneas, validación de shape, tenant_id vacío → ValueError | Sin test de recepción multi-formato |
| test_intake.py | create_intake_record (interrogación + tank selection + hypotheses) | [x] | ~433 líneas, 8 escenarios de entrada, validación de selectors, serialización | — |
| test_intake_storage.py | save/load de IntakeRecord | [x] | ~430 líneas, JSONL persistence, cross-tenant isolation, malformed JSON | — |
| test_interrogation.py | run_interrogation → StructuredSelectors | [x] | 205 líneas, 8 síntomas definidos, status/classification derivation | Clasificación embebida (ver GEN02) |
| test_storage.py | ensure_tenant_storage + append_reception_jsonl | [x] | 39 líneas, path traversal safety | — |
| test_anamnesis_fsm.py | FSM offline completo | [x] | 289 líneas, 14-step profile, hypothesis, evidence solicitation | — |
| test_anamnesis_fsm_integration.py | run_anamnesis_turn con progressive_context | [x] | 289 líneas, 17 respuestas secuenciales, rehidratación, fail-closed | — |
| test_anamnesis_readiness.py | evaluate_anamnesis_readiness | [x] | 56 líneas, confidence threshold, symptoms validation | — |
| test_profile_to_selectors_bridge.py | build_structured_selectors_from_profile_data | [x] | 50 líneas, mapping ficha→selectors | — |
| test_initial_laboratory_anamnesis_service.py | InitialLaboratoryAnamnesisService | [x] | ~700 líneas de servicio, FASE_0, attachment lifecycle | — |
| test_supermemory_recall_integration.py | run_recall_before_reply + augmented message | [x] | 140 líneas, FakeRecallClient, safe summary building | — |
| test_post_ficha_evidence_reception_and_readiness_gate.py | E2E anamnesis + evidence reception | [x] | 228 líneas, 17 respuestas + evidence input | — |
| test_post_ficha_routing_projection.py | post-ficha routing | [x] | 206 líneas, routing ligero, idempotencia | — |
| test_e2e_non_executing_flow.py | Flujo determinístico sin microservicios | [x] | 351 líneas, excel_diagnostic + supplier_duplicate_check, NEEDS_EVIDENCE | Sin test de archivo real (solo metadata) |
| test_organization_profile_intake.py | 13-question profile intake | [x] | Test de orquestación, profile flow completo | — |
| test_reception.py (orchestration) | Reception a nivel orquestación | [x] | (incluido arriba) | — |

Veredicto GEN01: [x] — Cobertura completa de unidad + integración + flujo E2E no-ejecutante. El único gap (multi-formato) no bloquea producto mínimo.

### GEN02 — Clasificación

| Test file | Módulo/comportamiento | Estado | Evidencia | Hueco |
|---|---|---|---|---|
| test_interrogation.py | Symptom→classification mapping | [x] | 8 síntomas: DESCUADRE_DINERO, MARGIN_UNCERTAINTY, duplicate_suppliers, stock, manual_excel, structural_only, suppliers_selectors, unknown | Mapeo hardcoded en strings, no tabla explícita |
| test_taxonomy.py | BusinessTaxonomySnapshot + TaxonomyType | [x] | 68 líneas, confidence 0.0–1.0, confirm_field no mutación | — |
| test_tank_selection.py | select_tanks desde InterrogationResult | [x] | 297 líneas, 9 escenarios, runtime classification suggestions | — |
| test_profile_to_selectors_bridge.py | commerce→Revendo, manufacturing→Produzco | [x] | 50 líneas, fallbacks seguros | — |
| tests/domain/types/test_decision_types.py | DecisionType enum | [x] | Enum-based, cobertura de tipos | — |
| tests/domain/types/test_pathology_types.py | PathologyType/Stage/Severity/Status | [x] | Enums de clasificación patológica | — |
| tests/domain/types/test_health_classification.py | HealthClassification | [x] | Enum de clasificación de salud organizacional | — |
| tests/domain/types/test_functional_organ_type.py | FunctionalOrganType | [x] | Enum de órganos funcionales | — |

Veredicto GEN02: [x] — La clasificación está embebida en interrogación (no hay módulo `classification/` autónomo para tests), pero los 8 síntomas cubren las categorías operables declaradas (margen, stock, proveedores, Excel, unsupported). Si M26 quiere extraer clasificación a módulo propio, esto es trabajo de refactor, no de cobertura faltante.

### GEN03 — Evidencia

| Test file | Módulo/comportamiento | Estado | Evidencia | Hueco |
|---|---|---|---|---|
| test_evidence.py | EvidenceRecord lifecycle | [x] | ~400 líneas, status transitions (REGISTERED→RECEIVED→LINKED→SUPERSEDED/REJECTED), immutability, to_dict | — |
| test_evidence_gate.py | evaluate_evidence_sufficiency | [x] | ~515 líneas, READY/NEEDS_MORE/BLOCKED/UNSUPPORTED, matching por request_id y evidence_type | — |
| test_evidence_requirement.py | create_evidence_requirement | [x] | 56 líneas, priority 1-3, blocks_analysis, telegram_message | — |
| test_evidence_requirement_from_formula.py | derive_evidence_requirements_from_formulas | [x] | 347 líneas, dedup, CALCULABLE vs CALCULABLE_CON_SUPUESTOS | — |
| test_evidence_storage.py | save/load EvidenceRecord | [x] | ~446 líneas, JSONL persistence, field type validation | — |
| test_post_ficha_evidence_gate.py | apply_post_ficha_evidence_turn | [x] | ~1012 líneas, parsing EVIDENCE::, fields dedup, dispatch flow, finding projection, AST forbidden imports | El test más completo del repo |
| test_parsed_document_metadata.py | ParsedDocumentMetadata | [x] | 246 líneas, sheets/tables/sections, compatibilidad con evidence_gate | — |
| test_docling_document_metadata_adapter.py | parse_docling_to_document_metadata | [x] | 220 líneas, mock-based, headings/tables, no pandas direct import | — |
| test_xlsx_document_metadata_adapter.py | parse_xlsx_to_document_metadata | [x] | 256 líneas, sheet detection, formulas/merged ranges warnings | — |
| test_document_parser_front.py | parse_document_to_metadata (router) | [x] | 191 líneas, extensión→adapter, parser_not_configured, AST boundary | — |
| test_evidence_requirement_matcher.py | Audit result evidence matcher | [x] | Matcher de requirements contra evidence records | — |
| test_structured_evidence_boundary.py | Boundary test structured evidence | [x] | Test de frontera | — |
| test_evidence_requirement.py (contracts) | EvidenceRequirement contract | [x] | Validación de contract | — |
| test_xlsx_evidence.py (root) | Excel evidence extraction | [x] | Test raíz de evidencia Excel | — |

Veredicto GEN03: [x] — Cobertura más densa del proyecto. Todos los gates (sufficiency, requirement, post-ficha), adapters (docling, xlsx, parser_front), y persistencia tienen tests con fixtures reproducibles. El gate post_ficha es el test más completo del repo (1012 líneas).

### GEN04 — Hallazgos

| Test file | Módulo/comportamiento | Estado | Evidencia | Hueco |
|---|---|---|---|---|
| test_finding_projection.py | project_actionable_findings | [x] | ~500 líneas, fail-closed, finding codes (LOW_MARGIN, PRODUCT_WITHOUT_COST, etc.), AST no-import de excel/LLM/telegram | — |
| test_excel_diagnostic.py | diagnose_excel | [x] | 129 líneas, EMPTY_PRODUCT, DUPLICATE_ROWS, LOW_MARGIN, multisheet, Spanish aliases | — |
| test_supplier_duplicate_check.py | diagnose_supplier_duplicates | [x] | 66 líneas, PASS/BLOCKED, null CUIT handling | — |
| test_delivery_package.py | build_delivery_package | [x] | 179 líneas, READY_TO_DELIVER/BLOCKED/FAILED, no-import AST | — |
| test_delivery_markdown.py | render_delivery_markdown | [x] | 159 líneas, output format, no-import AST | — |
| test_one_microservice_smoke.py | dispatch_candidate | [x] | 237 líneas, excel + supplier execution, blocked/unsupported handling | — |
| test_execution_result_gate.py | validate_execution_result | [x] | 233 líneas, PASS/BLOCKED/FAILED/UNDELIVERABLE, output_refs existence | — |
| test_e2e_cli.py | run_e2e (full CLI) | [x] | 51 líneas, diagnostic_report.md, diagnostic_result.json, reception_record.json, findings_count >= 1 | — |
| tests/domain/snapshots/test_diagnostic_report.py | DiagnosticReport snapshot | [x] | Validación de snapshot | — |
| tests/smartpyme/e2e/test_pipeline_radiography_excel.py | E2E excel pipeline | [x] | 104 líneas, PASS→READY_TO_DELIVER, output_refs existen en disco | — |
| test_narrative_pipeline.py | Narrative report pipeline | [-] | Test raíz, cobertura parcial | Sin test de narrativa multi-tenant |
| test_narrative_report_v2.py | Narrative report v2 | [-] | Test raíz, cobertura parcial | Sin test de findings narrativos cross-session |

Veredicto GEN04: [-] — Hallazgos técnicos (excel, supplier, projection, delivery, execution gate) tienen cobertura completa con fixtures reproducibles. Sin embargo, la capa de `narrative/report_generator*.py` solo tiene cobertura parcial desde tests raíz. El producto final SmartPyme probablemente necesitará narrativa para clientes PyME; ese gap es relevante.

### GEN05 — Memoria operacional

| Test file | Módulo/comportamiento | Estado | Evidencia | Hueco |
|---|---|---|---|---|
| test_supermemory_tenant_recall.py | SupermemoryTenantRecallClient | [x] | 285 líneas, container tag, custom_id hashing, transport error handling, 400 body sanitization, redaction | — |
| test_supermemory_recall_integration.py | run_recall_before_reply | [x] | 140 líneas, FakeRecallClient, safe summary | — |
| test_storage.py | ensure_tenant_storage + path traversal | [x] | 39 líneas, JSONL append | — |
| test_conversation_contract.py | ConversationContract + phase update | [x] | 42 líneas, immutability | — |
| tests/orchestration/test_state.py | PymIAState | [x] | State machine, 10 fases | — |
| tests/orchestration/test_state_storage.py | save/load/replay/export state | [x] | JSONL persistence, history, tenant filter | — |
| tests/orchestration/test_graph.py | run_pymia_graph | [x] | 4-node graph execution | — |
| tests/orchestration/test_e2e_longitudinal.py | E2E longitudinal | [-] | Existe pero cobertura mínima | Sin test de continuidad cross-session verificable |
| tests/domain/entities/test_decision_record.py | DecisionRecord lifecycle | [x] | 177 líneas, proposal→decision→execution→evaluation | — |
| test_memory_contract.py (root) | Memory contract | [x] | Contrato de memoria | — |
| test_conversa_supermemory_recall_runtime.py | Runtime recall | [x] | Conversa engine recall | — |

Veredicto GEN05: [-] — La memoria tiene cobertura unitaria sólida (supermemory client, state machine, storage, decision records). Pero no hay test que demuestre continuidad cross-session: "tenant A regresa 3 días después → sistema recuerda su contexto anterior → evita repreguntar". El concepto de "decisiones vigentes" existe en documentos pero no tiene test formal como entidad de memoria operacional.

### GEN06 — Aprendizaje

| Test file | Módulo/comportamiento | Estado | Evidencia | Hueco |
|---|---|---|---|---|
| tests/domain/entities/test_knowledge_item.py | KnowledgeItem | [x] | 359 líneas, ciclo epistémico completo (DECLARED→CONTRASTED→VALIDATED→REFUTED), confidence, tags, immutability | Sin test de creación desde evidencia repetida |
| tests/domain/entities/test_learning_cycle.py | LearningCycle | [x] | 316 líneas, initiated→result→attribution→closure, outcome_matches_expectation | Sin test de aprobación humana workflow |
| tests/domain/types/test_epistemic_state.py | EpistemicState enum | [x] | Enum validation | — |
| tests/domain/types/test_learning_cycle_types.py | LearningCycleState | [x] | Enum validation | — |
| tests/domain/types/test_attribution_type.py | AttributionType | [x] | Enum validation | — |
| tests/services/test_pathology_engine_service.py | PathologyEngineService | [x] | Evaluator con knowledge tank | Sin test de mejora basada en outcomes |
| tests/services/test_kernel_chip1_integration.py | Knowledge tank kernel integration | [x] | Chip 1 integration | — |
| tests/services/test_catalog_loader_v1.py | Formula + pathology catalog | [x] | Catalog loading y validación | — |

Veredicto GEN06: [-] — Las entidades de dominio (KnowledgeItem, LearningCycle) tienen tests unitarios exhaustivos con escenarios completos. Pero el flujo declarado "evidencia repetida → mejora gobernada → aprobación humana → skill update" no tiene test de integración que demuestre que la cadena funciona. La aprobación humana es un concepto sin implementación de código testeable.

### GEN07 — Intervención

| Test file | Módulo/comportamiento | Estado | Evidencia | Hueco |
|---|---|---|---|---|
| tests/domain/entities/test_intervention_plan.py | InterventionPlan | [x] | 168 líneas, status transitions, priority validation, actions, success_criteria | Sin integración con dispatcher |
| tests/domain/entities/test_decision_record.py | DecisionRecord | [x] | 177 líneas, proposal→execution→evaluation | — |
| tests/domain/types/test_intervention_types.py | InterventionType/Priority/Status | [x] | Enum validation | — |
| tests/smartpyme/test_one_microservice_smoke.py | dispatch_candidate | [x] | 237 líneas, dispatching a excel/supplier | — |
| tests/services/test_diagnostic_report_service.py | DiagnosticReportService | [x] | CONFIRMED/INSUFFICIENT_EVIDENCE | — |
| tests/services/test_pathology_engine_service.py | PathologyEngineService | [x] | Pathology evaluation | — |
| tests/services/test_pathology_adapter.py | pathology_finding_to_finding_record | [x] | Adapter test | — |
| tests/microsaas/test_microsaas_registry.py | Microsaas registry | [x] | Registry de microservicios | — |
| tests/services/test_kernel_chip1_integration.py | Kernel chip integration | [x] | Integration con knowledge tank | — |

Veredicto GEN07: [-] — Las entidades de intervención (InterventionPlan, DecisionRecord) tienen tests unitarios sólidos. El dispatcher de microservicios funciona. Pero no hay test que coordine el flujo completo: "diagnosticar patología X → InterventionPlan proposed → decisión humana → ejecutar microservicio estabilizador → evaluar outcome". La pieza de "decisión humana" no está implementada ni testeada.

### GEN08 — Gobernanza

| Test file | Módulo/comportamiento | Estado | Evidencia | Hueco |
|---|---|---|---|---|
| tests/domain/entities/test_governance_profile.py | GovernanceProfile | [x] | 164 líneas, decision_maker_count, process_count, coherence_mechanism_count | — |
| tests/domain/entities/test_organization_profile.py | OrganizationProfile | [x] | 284 líneas, 9 invariantes de dominio, add_commitment, mark_validated | — |
| tests/domain/entities/test_organizational_identity.py | OrganizationalIdentity | [x] | 4 identities + 3 layers | — |
| tests/domain/entities/test_organizational_pathology.py | OrganizationalPathology | [x] | Pathology entity | — |
| tests/domain/primitives/test_*.py (7 archivos) | ExchangeCommitment, FunctionalOrgan, IdentityCrisis, OrganizationalConstraint, OrganizationalDependency, StructuralRelationship, StructuralTension | [x] | Cobertura completa de primitives | — |
| tests/domain/snapshots/test_*.py (5 archivos) | HealthAssessment, DiagnosticReport, PrognosisAssessment, DecisionCapabilityAssessment, DomainIntegrationIndex | [x] | Snapshots tienen tests | — |
| tests/domain/types/test_*.py (13 archivos) | Todos los enums de gobernanza, patología, intervención, aprendizaje | [x] | Cobertura densa de tipos | — |
| tests/architecture/test_forbidden_imports.py | Guardrails de imports prohibidos | [x] | AST-based enforcement | — |
| tests/architecture/test_forbidden_terms.py | Guardrails de términos prohibidos | [x] | Terminology enforcement | — |
| tests/contracts/test_attachment_lifecycle_contract.py | Attachment lifecycle v1 | [x] | Contract test | — |
| tests/scn/test_scn_contract_schemas.py | SCN contract schemas | [x] | Schemas validados | — |
| tests/scn/test_runtime_policy_contract.py | Runtime policy | [x] | Policy enforcement | — |
| tests/scn/test_runtime_policy_enforcement_cases.py | Policy enforcement cases | [x] | Casos de enforcement | — |
| tests/scn/test_scn_operational_audit_verifier.py | SCN audit verifier | [x] | Verifier de auditoría | — |
| tests/scn/test_scn_output_gateway.py | SCN output gateway | [x] | Gateway de salida | — |
| tests/scn/test_scn_render_contract_builder.py | SCN render contract builder | [x] | Builder de contratos de render | — |
| tests/scn/test_operational_audit_result_boundary.py | Audit result boundary | [x] | Boundary de auditoría | — |
| tests/scn/test_render_contract_boundary.py | Render contract boundary | [x] | Boundary de render | — |
| tests/scn/test_scn_chain_offline_integration.py | SCN chain offline integration | [x] | Integración offline | — |
| tests/orchestration/test_contracts_enforcement.py | Contracts enforcement | [x] | Enforcement de contratos | — |
| tests/orchestration/test_audit_cli.py | audit_cli | [x] | CLI de auditoría | — |
| tests/test_audit_boundary_graph.py (root) | Audit boundary graph | [x] | Boundary de graph | — |
| tests/scripts/test_sandbox_smoke_test.py | Sandbox smoke | [x] | Smoke de sandbox | — |

Veredicto GEN08: [x] — Capa de gobernanza tiene la cobertura más densa después de GEN03. 33 tests de dominio + 9 tests SCN + guardrails arquitectónicos + enforcement de contratos. Los conceptos abstractos como "engramas" o "DoD" son metodología/documentación, no código testeable, y se marcan como tales implícitamente al no tener módulo dedicado.

### GEN09 — Producto SmartPyme

| Test file | Módulo/comportamiento | Estado | Evidencia | Hueco |
|---|---|---|---|---|
| test_e2e_cli.py | run_e2e full CLI | [x] | 51 líneas, Excel→diagnostic→reception→deliver | Sin multi-tenant |
| test_e2e_non_executing_flow.py | Flujo determinístico sin microservicios | [x] | 351 líneas, excel + supplier paths | — |
| tests/smartpyme/e2e/test_pipeline_radiography_excel.py | E2E pipeline radiography | [x] | 104 líneas, PASS→READY_TO_DELIVER, developer report generado | — |
| tests/smartpyme/test_domain_core_v1_consumption_smoke.py | Smoke domain core v1 | [x] | 26 líneas, boundary smoke | — |
| tests/orchestration/test_os_tool_registry.py | OS tool registry | [x] | 6 tools registradas | — |
| tests/orchestration/test_conversation_adapter.py | Conversation adapter | [x] | Adaptación de anamnesis a OS | — |
| tests/orchestration/test_organization_profile_intake.py | 13-question profile intake | [x] | Profile flow completo | — |
| tests/orchestration/test_graph.py | run_pymia_graph | [x] | 4-node graph execution | — |
| tests/orchestration/test_e2e_longitudinal.py | E2E longitudinal | [-] | Existe pero cobertura mínima | Sin test de ciclo de vida del tenant |
| tests/pipeline/test_admission_pipeline_v1.py | Admission pipeline v1 | [x] | Pipeline de admisión | — |
| tests/pipeline/test_admission_response_formatter_v1.py | Response formatter | [x] | Formatting de respuesta | — |
| tests/test_conversa_engine_boundary_consumption_smoke.py | Conversa engine boundary | [x] | Smoke de frontera | — |
| tests/test_conversa_operational_audit_runner.py | Audit runner | [x] | Runner de auditoría operacional | — |
| tests/test_golden_replay.py | Golden replay | [x] | Replay de findings dorados | — |

Veredicto GEN09: [-] — Existen E2E tests (CLI, pipeline radiography excel) y la orquestación tiene cobertura. Pero no hay test que ejecute el flujo de producto declarado: "cliente trae caos PyME → sistema registra tenant → pide evidencia → procesa archivo real → devuelve hallazgo útil → entrega reporte → conserva trazabilidad → habilita seguimiento o próxima venta". El test más cercano (test_e2e_cli.py) cubre Excel→diagnóstico pero no el ciclo completo de producto con multi-tenant y seguimiento.

---

## Tests huérfanos o ambiguos

| Test file | Ubicación | Razón de ambigüedad |
|---|---|---|
| test_operational_harness.py | tests/smartpyme/ | Infraestrutura de observabilidad, no capacidad de negocio. No mapea a ningún GEN. |
| test_pipeline_radiography_models.py | tests/smartpyme/ | Test de modelos de la infraestrutura de testing, no capacidad de negocio. |
| test_pipeline_radiography_run_scenarios.py | tests/smartpyme/ | Test del runner de escenarios, infraestrutura. |
| test_capability_registry.py | tests/smartpyme/ | Validador de registry, no capacidad. |
| test_interrogation_cli.py (source) | pymia/smartpyme/ | CLI de interrogación sin test dedicado. |
| tests/smartpyme/test_anamnesis_readiness.py | tests/smartpyme/ | Test pequeño (56 líneas) que podría ser absorbed por test_anamnesis_fsm_integration.py. |
| tests/test_conversational_contract.py | tests/docs/ | Ubicación ambigua (docs/ vs orchestration/ vs smartpyme/ tiene test_conversation_contract.py). |
| tests/test_conversa_*.py (5 archivos) | tests/ (raíz) | Tests del conversa engine, ubicación raíz los hace difíciles de categorizar. |
| tests/document_intelligence/* (6 archivos) | tests/document_intelligence/ | Capacidad futura no certificada, no mapea a GEN actual. |
| tests/hermes/* (8 archivos) | tests/hermes/ | Bridge a Telegram (área prohibida). |
| tests/telegram_runtime/* (5 archivos) | tests/telegram_runtime/ | Runtime de Telegram (área prohibida). |
| tests/llm_operator/* (3 archivos) | tests/llm_operator/ | Integración LLM (área prohibida). |
| tests/mcp/test_first_clinical_interview_mcp_server.py | tests/mcp/ | MCP server, fuera de scope actual. |
| tests/test_architecture_guardrails.py (raíz) | tests/ (raíz) | Ubicación raíz, debería estar en tests/architecture/. |
| tests/test_audit_boundary_graph.py (raíz) | tests/ (raíz) | Ubicación raíz, naturaleza similar a tests/scn/. |

Los tests de Telegram, Hermes y LLM operator se excluyen de este análisis por ser áreas explícitamente prohibidas.

---

## Capacidades sin cobertura visible

Tras mapear 157 archivos de test contra GEN01–GEN09, no se identifican capacidades completamente sin cobertura visible. Sin embargo, los siguientes flujos de capacidad no tienen test de integración reproducible que demuestre el comportamiento end-to-end:

1. **Continuidad cross-session del tenant (GEN05)**: No hay test que demuestre "tenant A conversa día 1 → tenant A regresa día 3 → sistema recupera contexto → evita repreguntar → continúa diagnóstico". Los tests unitarios de supermemory existen, pero el flujo completo de continuidad no.

2. **Cadena de aprendizaje E2E (GEN06)**: No hay test que demuestre "evidencia repetida detectada → KnowledgeItem creado → LearningCycle iniciado → outcome registrado → skill actualizado". Las entidades de dominio tienen tests, pero el flujo gobernado no.

3. **Coordinación diagnóstico→intervención→ejecución (GEN07)**: No hay test que demuestre "diagnosticar patología → InterventionPlan proposed → decisión humana → ejecutar microservicio estabilizador → outcome evaluado". La decisión humana no tiene implementación de código.

4. **Flujo de producto multi-tenant (GEN09)**: No hay test que ejecute el flujo declarado: "cliente trae caos → registra tenant → pide evidencia → procesa archivo real → devuelve hallazgo → entrega reporte → conserva trazabilidad → habilita seguimiento". El test_e2e_cli cubre Excel→diagnóstico pero no el ciclo completo con múltiples tenants y seguimiento posterior.

5. **Narrativa de hallazgos multi-tenant (GEN04)**: narrative/report_generator*.py tiene cobertura parcial desde tests raíz. El producto SmartPyme probablemente necesitará narrativa para clientes PyME, y ese gap es relevante si M26 apunta a producto vendible.

---

## Riesgos

| Riesgo | Severidad | Impacto en M26 |
|---|---|---|
| GEN04 en [-] limita capacidad de entrega de hallazgos a clientes | Media | Si M26 apunta a producto mínimo, la narrativa de hallazgos es necesaria. Sin test E2E, el reporte puede romperse en producción. |
| GEN05 en [-] impide verificar continuidad de tenant | Alta | Un producto que olvida al cliente entre sesiones no es producto. Si M26 prioriza GEN09, este gap es bloqueante. |
| GEN06 en [-] sin cadena de aprendizaje verificable | Media | Si M26 quiere acumular inteligencia de tenant, necesita flujo testeado. Sin él, "aprendizaje" es aspiracional. |
| GEN07 en [-] sin flujo de intervención testeable | Media | El producto declarado promete "estabilización". Sin test, es promesa sin verificación. |
| GEN09 en [-] sin E2E de producto | Alta | El criterio de éxito de producto no tiene test que lo valide. Cualquier afirmación de "producto funcional" es no reproducible. |
| Tests de Telegram/Hermes/LLM en tests/ no deben tocarse | Baja | Áreas explícitamente prohibidas. La auditoría los ignora. |
| Marco GEN es nuevo y puede no ser el mejor marco para M26 | Media | Si M26 decide usar otro marco, esta auditoría es punto de partida, no camisa de fuerza. |
| 157 tests es una base sólida pero el 60% de GEN01–GEN05 está en [x]; el resto está en [-] | Media | M26 debe decidir si consolidar GEN04–GEN05 antes de escalar a GEN06–GEN09, o avanzar asumiendo el riesgo. |

---

## Recomendaciones para M26

### Recomendación primaria

**M26 debe consolidar GEN04 (Hallazgos completos) y GEN05 (Memoria operacional cross-session) antes de cualquier intento de producto vendible.**

Justificación:
- GEN01–GEN03 son la base de recepción/clasificación/evidencia y están sólidos.
- GEN04 tiene la cadena de hallazgos técnicos funcionando (excel, supplier, projection, delivery) pero la narrativa de hallazgos para clientes PyME está parcial.
- GEN05 es la pieza que hace que el sistema "recuerde" al cliente. Sin test cross-session verificable, el producto no tiene continuidad.
- GEN06–GEN09 dependen de GEN04 y GEN05 estables. Construir sobre bases parciales amplifica la deuda.

### Recomendaciones secundarias

1. **No avanzar a GEN06 (Aprendizaje) como candidato para M26**: La cadena de aprendizaje no tiene E2E. M26 debería primero definir el flujo "evidencia repetida → mejora gobernada" y luego testearlo.

2. **No avanzar a GEN07 (Intervención) sin decisión humana implementada**: El concepto de "aprobación humana" es central pero no tiene código. Si M26 quiere GEN07, debe primero decidir si la aprobación humana es gate obligatorio o metadata opcional.

3. **GEN08 (Gobernanza) está sólido y no necesita M26 dedicado**: Los tests de governance están completos. Mantener el ritmo de guardrails arquitectónicos (forbidden imports, contracts) es suficiente.

4. **GEN09 (Producto) no es candidato para M26 directo**: El producto completo requiere GEN04–GEN05 consolidados. M26 debería apuntar a un milestone que cierre los gaps de GEN04–GEN05 y produzca un E2E multi-tenant verificable.

### Candidatos descartados para M26

- **M26_NEXT_CAPABILITY_IMPLEMENTATION**: No hay capacidad candidata real. `report_html` y `document_parser_front` están NOT_FOUND. Construir sobre NOT_FOUND es inventar roadmap.
- **M26_REGISTRY_HARDENING**: No hay inconsistencias reales que resolver. Registry funciona correctamente.
- **M26_CI_ENHANCEMENT**: CI ya ejecuta run_scenarios + harness + pytest + upload. Aserciones adicionales no aportan valor real.
- **M26_TESTS_REFACTOR**: Los tests están bien organizados. Refactor sin propósito claro es burocracia.

### Candidatos viables para M26

1. **M26_HALLAZGOS_NARRATIVOS_CONSOLIDATION**: Cerrar el gap de GEN04. Definir flujo de narrativa para hallazgos Excel/Supplier, testear E2E multi-tenant, integrar con delivery_markdown. Riesgo: bajo. Beneficio: habilita producto vendible.

2. **M26_TENANT_CONTINUITY_TEST**: Cerrar el gap de GEN05. Definir y testear el flujo cross-session: tenant retorna → sistema recupera contexto previo → continúa sin repreguntar. Requiere decidir si la continuidad es automática o solicitada. Riesgo: medio (decisión de diseño). Beneficio: habilita seguimiento y próxima venta.

3. **M26_E2E_PRODUCT_ACCEPTANCE**: Una vez GEN04 y GEN05 consolidados, crear test de aceptación de producto que ejecute el flujo declarado de GEN09 de extremo a extremo. Riesgo: bajo si los gaps previos están cerrados. Beneficio: prueba reproducible de que el producto funciona.

### Regla de continuidad para M26

No iniciar M26 sin:
1. M25 cerrado y pusheado.
2. Revisión externa de este documento.
3. Decisión explícita sobre cuál de los candidatos viables (arriba) se prioriza.
4. Recorte de scope confirmado.

No ampliar M26 para incluir:
- Nueva capacidad de negocio.
- Refactor de contratos existentes.
- Modificaciones a capabilities.yaml o capability_registry.py.
- Integración con Telegram, PDF, HTML o UI.
- Mejoras de CI.
- IA residente o integración LLM.

---

## Veredicto final

```text
ESTADO: AUDIT_COMPLETE
ALCANCE: AUDIT_ONLY (cero código modificado)
ARTEFACTO: docs/roadmap/GENETIC_TEST_COVERAGE_AUDIT.md
GENS MAPEADOS: 9 de 9
TESTS INVENTARIADOS: 157
GENS EN [x]: 4 (GEN01, GEN02, GEN03, GEN08)
GENS EN [-]: 5 (GEN04, GEN05, GEN06, GEN07, GEN09)
GENS EN [ ]: 0
GENS EN [!]: 0
GENS EN [~]: 0 (todos tienen al menos cobertura parcial)
```

**Diagnóstico para decisión de M26:**

La base del producto (recepción, clasificación, evidencia, gobernanza) está sólida. Las piezas de valor agregado (hallazgos narrativos, memoria cross-session, aprendizaje, intervención, producto completo) están parciales. M26 debe apuntar a cerrar los gaps de GEN04 y GEN05 antes de escalar a GEN06–GEN09. Construir producto vendible sobre hallazgos parciales y memoria sin continuidad cross-session es apuesta, no ingeniería.

El marco GEN01–GEN09 resulta útil como herramienta de navegación: expone dónde están los gaps reales, qué se puede construir sobre qué, y dónde está la frontera entre "base sólida" y "promesa no verificada". Si M26 lo adopta, debería ser como lens de priorización, no como checklist exhaustivo.

**Próximo paso metodológico:**

1. Coder revisa este documento.
2. Coder selecciona uno de los tres candidatos viables para M26 (recomendación primaria: consolidación de GEN04–GEN05).
3. Recorte de scope.
4. Implementación mínima.
5. Pytest.
6. Checkpoint.