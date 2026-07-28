"""
contamination guard
"""
from pathlib import Path
from .policy import get_project_root, iter_python_files, scan_file_for_terms

FORBIDDEN_TERMS = ["create_job", "authorization", "decision_type", "workflow", "orchestration"]

# Guardarraíl por término con excepciones estrictas por ruta/capa.
# El término se sigue escaneando globalmente, pero solo puede aparecer
# dentro de rutas explícitamente permitidas.
TERM_ALLOWED_PATH_PREFIXES = {
    "decision_type": [
        "pymia/domain/entities/decision_record.py",
        "pymia/domain/types/decision_type.py",
        "pymia/domain/types/__init__.py",
        "tests/domain/entities/test_decision_record.py",
        "tests/domain/types/test_decision_types.py",
    ],
    "authorization": [
        "pymia/contracts/primary_case_file_v1.py",
        "pymia/smartpyme/service_1_canonical_ingestion_output_to_semantic_bridge_v1.py",
        "pymia/smartpyme/service_1_column_understanding_corpus_report_v1.py",
        "pymia/smartpyme/service_1_column_understanding_engine_v1.py",
        "pymia/smartpyme/service_1_column_understanding_owner_question_adapter_v1.py",
        "pymia/smartpyme/service_1_column_understanding_owner_question_corpus_audit_v1.py",
        "pymia/smartpyme/service_1_computability_v1.py",
        "pymia/smartpyme/service_1_owner_confirmation_event_v1.py",
        "pymia/smartpyme/service_1_semantic_bridge_to_controlled_execution_gate_v1.py",
        "pymia/smartpyme/accounting_workpaper_draft_packet_v1.py",
        "pymia/smartpyme/first_aid_delivery_aggregate_v1.py",
        "pymia/smartpyme/owner_pure_view.py",
        "tests/contracts/test_first_aid_toolbox_pack_seed_v1.py",
        "tests/contracts/test_primary_case_file_v1.py",
        "tests/smartpyme/test_accounting_workpaper_draft_packet_v1.py",
        "tests/smartpyme/test_owner_message_formatter_v1.py",
        "tests/smartpyme/test_service_1_12_productive_pathology_roadmap_v1.py",
        "tests/smartpyme/test_service_1_canonical_ingestion_output_to_semantic_bridge_v1.py",
        "tests/smartpyme/test_service_1_cycle_044a_generic_capability_kernel_architecture_v1.py",
        "tests/smartpyme/test_service_1_semantic_concept_catalog_candidate_v1.py",
        "tests/smartpyme/test_service_1_semantic_concept_catalog_contract_v1.py",
        "tests/smartpyme/test_service_1_semantic_concept_catalog_readiness_gate_v1.py",
        "tests/smartpyme/test_service_1_stock_movement_semantic_contract_v1.py",
        "tests/smartpyme/test_service_1_web_column_confirmation_intake_boundary_v1.py",
    ],
    "orchestration": [
        "pymia/orchestration/",
        "tests/orchestration/",
        "pymia/telegram_bot_runtime.py",
        "pymia/llm_operator/smoke_openrouter.py",
        "tests/llm_operator/test_operator_offline.py",
        "tests/diagnosticcore/test_core_audit_delivery_bridge.py",
        "tests/smartpyme/test_core_delivery_bridge_reentry.py",
        "tests/smartpyme/test_depth_e2e_textile_owner_excel_flow.py",
        "tests/smartpyme/test_owner_facing_report.py",
        "tests/telegram_runtime/test_telegram_bot_runtime_e2e_sequence.py",
        "tests/telegram_runtime/test_telegram_bot_runtime_evidence_bridge.py",
        "tests/telegram_runtime/test_telegram_bot_runtime_fsm_integration.py",
        "pymia/smartpyme/service_1_column_understanding_owner_question_adapter_v1.py",
        "pymia/smartpyme/service_1_column_understanding_owner_question_corpus_audit_v1.py",
        "tests/smartpyme/test_functional_pack_loader_navigator.py",
    ],
}

# Excepciones para prohibiciones explicitas (en docs o docstrings/tests)
ALLOW_PATTERNS = [
    "forbidden",
    "no incluye",
    "no recibe",
    "no devuelve",
    " no debe",
    " no se",
    "ni ",
    "sin ",
    "ausencia",
    "without",
    "ningún",
    "ningun",
    "boundary",
    "intenta",
    "- create_job",
    "crear workflows",
    "escalar a orchestration",
    '"workflow",',
    '"authorization",',
    '"orchestration",',
    '"create_job",',
    '"decision_type",',
    "'workflow',",
    "'authorization',",
    "'orchestration',",
    "'create_job',",
    "'decision_type',"
]

def test_no_forbidden_terms_in_code():
    root = get_project_root()
    
    dirs_to_scan = [root / "pymia", root / "tests"]
    
    files_to_scan = []
    for d in dirs_to_scan:
        if d.exists():
            files_to_scan.extend(iter_python_files(d))
            
    violations = []
    for fpath in files_to_scan:
        # Exceptions: architecture tests
        if "architecture" in fpath.parts and ("policy.py" in fpath.name or "test_forbidden_terms.py" in fpath.name or "test_forbidden_imports.py" in fpath.name or "__init__.py" in fpath.name):
            continue
            
        findings = scan_file_for_terms(fpath, FORBIDDEN_TERMS, ALLOW_PATTERNS)
        rel_path = fpath.relative_to(root).as_posix()
        for lineno, term, context in findings:
            allowed_prefixes = TERM_ALLOWED_PATH_PREFIXES.get(term, [])
            if any(
                rel_path == allowed or rel_path.startswith(allowed)
                for allowed in allowed_prefixes
            ):
                continue
            violations.append(f"{fpath.relative_to(root)}:{lineno} -> {term} (context: {context})")
            
    assert not violations, "Found forbidden terms in code:\n" + "\n".join(violations)
