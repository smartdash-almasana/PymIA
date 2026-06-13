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
    ],
    "authorization": [
        "pymia/llm_operator/providers_openrouter.py",
        "pymia/smartpyme/supermemory_tenant_recall.py",
        "tests/llm_operator/test_openrouter_provider.py",
        "tests/smartpyme/test_supermemory_tenant_recall.py",
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
