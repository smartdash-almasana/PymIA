"""Static architecture fitness checks for Servicio 1.

This module is intentionally a repository guard, not a Servicio 1 runtime
component.  It reads Python source and the module disposition registry without
importing or executing the product pipeline.  A failing gate is therefore a
stop signal for architecture work, not a runtime fallback.

Run with::

    python -m pymia.architecture_guard
    python -m pymia.architecture_guard --json
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
from dataclasses import asdict, dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable, Mapping


CANONICAL_ROOT = "service_1_product_pipeline_v1"
CANONICAL_XLSX_READER = "service_1_xlsx_to_normalized_table_v1"
XLSX_VALIDATOR = "service_1_xlsx_quality_gate_v1"
SEMANTIC_FSM = "service_1_assisted_semantic_product_wiring_v1"
F7_MODULE = "service_1_analysis_evidence_preparation_v1"
MATH_ENGINE_MODULE = "pymia/services/formula_engine_service.py"

LEGACY_MARKERS = (
    "run_initial_pass",
    "semantic_run_override",
    "use_assisted_semantics",
    "legacy_launch_compatibility",
    "service_1_deterministic_semantic_pipeline_v1",
    "service_1_legacy_semantic_reentry_compat_v1",
)
FORBIDDEN_READ_IMPORTS = (
    "service_1_xlsx_to_normalized_table_v1",
    "service_1_assisted_semantic_product_wiring_v1",
    "service_1_dynamic_analysis_discovery_v1",
    "service_1_computability_v1",
    "service_1_analysis_evidence_preparation_v1",
    "service_1_analysis_math_execution_v1",
    "service_1_analysis_result_projection_v1",
    "service_1_p8_",
    "formula_engine_service",
    "pydantic_ai",
)
WEB_BYPASS_MODULES = (
    "service_1_analysis_evidence_preparation_v1",
    "service_1_analysis_math_execution_v1",
    "service_1_analysis_result_projection_v1",
    "service_1_consorcios_collection_aging_v1",
    "service_1_consorcios_expense_variance_v1",
    "service_1_reconciliation_product_request_v1",
)
LLM_MODULE_HINTS = (
    "llm",
    "semantic_provider",
    "semantic_interpreter",
)
AUTHORITY_FLAGS = (
    "runtime_authorized",
    "tool_execution_authorized",
    "product_ready",
    "delivery_authorized",
    "computability_authorized",
    "join_execution_authorized",
    "semantic_rebind_authorized",
    "automatic_reuse_authorized",
)
DECLARATIVE_EVALUATORS = (
    "service_1_liq_001_evaluator_v1",
    "service_1_liq_002_evaluator_v1",
    "service_1_ren_001_evaluator_v1",
    "service_1_pyme_011_evaluator_v1",
    "service_1_consorcios_collection_aging_v1",
    "service_1_consorcios_expense_variance_v1",
)


@dataclass(frozen=True)
class GateResult:
    """One deterministic architecture gate result."""

    gate_id: str
    label: str
    passed: bool
    observed: Any
    expected: Any
    detail: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _service_root(root: Path) -> Path:
    return root / "pymia" / "smartpyme"


def _service_files(root: Path) -> dict[str, Path]:
    directory = _service_root(root)
    return {path.stem: path for path in directory.glob("service_1_*.py")}


@lru_cache(maxsize=512)
def _parse_cached(path_text: str) -> ast.Module:
    path = Path(path_text)
    return ast.parse(path.read_text(encoding="utf-8"), filename=path_text)


def _parse(path: Path) -> ast.Module:
    return _parse_cached(str(path.resolve()))


def _source(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _imports(tree: ast.AST) -> set[str]:
    """Return imported module stems, preserving only useful module identity."""

    result: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                result.add(alias.name)
                if alias.name.startswith("pymia.smartpyme.service_1_"):
                    result.add(alias.name.rsplit(".", 1)[-1])
        elif isinstance(node, ast.ImportFrom) and node.module:
            result.add(node.module)
            if node.module.startswith("pymia.smartpyme.service_1_"):
                result.add(node.module.rsplit(".", 1)[-1])
    return result


def _service_imports(path: Path) -> set[str]:
    """Return direct ``service_1_*`` imports from a source file."""

    imports: set[str] = set()
    for imported in _imports(_parse(path)):
        if imported.startswith("service_1_"):
            imports.add(imported)
    return imports


def _module_defs(tree: ast.Module) -> set[str]:
    return {
        node.name
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
    }


def _registry(root: Path) -> dict[str, Any]:
    path = root / "docs" / "service_1_module_disposition.v1.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _registry_maps(registry: Mapping[str, Any]) -> tuple[dict[str, Mapping[str, Any]], list[str]]:
    entries = list(registry.get("modules") or ())
    names = [str(item.get("module") or "") for item in entries]
    return {name: item for name, item in zip(names, entries)}, names


def _root_closure(files: Mapping[str, Path], root_name: str = CANONICAL_ROOT) -> set[str]:
    reachable: set[str] = set()
    pending = [root_name]
    while pending:
        name = pending.pop()
        if name in reachable or name not in files:
            continue
        reachable.add(name)
        pending.extend(sorted(_service_imports(files[name]) - reachable))
    return reachable


def _gate(
    gate_id: str,
    label: str,
    passed: bool,
    observed: Any,
    expected: Any,
    detail: str = "",
) -> GateResult:
    return GateResult(gate_id, label, bool(passed), observed, expected, detail)


def _execution_root_gate(root: Path, files: Mapping[str, Path], registry: Mapping[str, Any]) -> GateResult:
    definitions: list[str] = []
    direct_external_callers: list[str] = []
    for name, path in files.items():
        tree = _parse(path)
        if "run_service_1_product_pipeline_v1" in _module_defs(tree):
            definitions.append(name)
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and node.id == "run_service_1_governed_analysis_v1":
                is_definition = isinstance(node.ctx, ast.Store)
                if not is_definition and name != CANONICAL_ROOT:
                    direct_external_callers.append(name)
    root_name = str(registry.get("canonical_product_root") or "")
    passed = root_name == CANONICAL_ROOT and definitions == [CANONICAL_ROOT] and not direct_external_callers
    return _gate(
        "ONE_CANONICAL_PRODUCT_ROOT",
        "Execution roots",
        passed,
        {"registry_root": root_name, "definitions": definitions, "external_governed_callers": sorted(set(direct_external_callers))},
        {"registry_root": CANONICAL_ROOT, "definitions": [CANONICAL_ROOT], "external_governed_callers": []},
        "Web/CLI surfaces must enter through the Product Root; governed analysis remains an internal root step.",
    )


def _execution_commands_gate(root: Path) -> GateResult:
    path = _service_root(root) / "service_1_product_execution_contracts_v1.py"
    expected = {
        "WorkbookSemanticStartRequestV1",
        "WorkbookSemanticContinueRequestV1",
        "WorkbookAnalysisExecuteRequestV1",
        "SpecializedDomainExecuteRequestV1",
    }
    if not path.is_file():
        return _gate("FOUR_EXPLICIT_EXECUTION_COMMANDS", "Execution commands", False, [], sorted(expected), "Contract module is missing.")
    classes = {
        node.name
        for node in _parse(path).body
        if isinstance(node, ast.ClassDef) and node.name.endswith("RequestV1")
    }
    return _gate(
        "FOUR_EXPLICIT_EXECUTION_COMMANDS",
        "Execution commands",
        classes == expected,
        sorted(classes),
        sorted(expected),
        "Only the four typed Product Root request contracts are executable command shapes.",
    )


def _xlsx_reader_gate(root: Path, files: Mapping[str, Path]) -> GateResult:
    parser = files.get(CANONICAL_XLSX_READER)
    parser_ok = parser is not None and any(
        isinstance(node, ast.ImportFrom)
        and node.module == "openpyxl"
        and any(alias.name == "load_workbook" for alias in node.names)
        for node in ast.walk(_parse(parser))
    )
    competing_readers: list[str] = []
    for name, path in files.items():
        if name in {CANONICAL_XLSX_READER, XLSX_VALIDATOR}:
            continue
        tree = _parse(path)
        imports = _imports(tree)
        text = _source(path)
        if "load_workbook" in imports or "read_excel" in text:
            competing_readers.append(name)
    observed = {"canonical_parser": CANONICAL_XLSX_READER if parser_ok else None, "competing_readers": sorted(competing_readers), "validator_exempted": XLSX_VALIDATOR in files}
    return _gate(
        "ONE_CANONICAL_XLSX_READER",
        "Canonical XLSX readers",
        parser_ok and not competing_readers,
        observed,
        {"canonical_parser": CANONICAL_XLSX_READER, "competing_readers": []},
        "The quality gate may inspect an XLSX and delivery modules may write one; parsing remains canonical.",
    )


def _semantic_fsm_gate(root: Path, files: Mapping[str, Path]) -> GateResult:
    path = files.get(SEMANTIC_FSM)
    defs = _module_defs(_parse(path)) if path else set()
    legacy_files = sorted(name for name in ("service_1_deterministic_semantic_pipeline_v1", "service_1_legacy_semantic_reentry_compat_v1") if name in files)
    expected_defs = {"run_service_1_assisted_semantic_initial_v1", "run_service_1_assisted_semantic_reentry_v1"}
    passed = path is not None and expected_defs <= defs and not legacy_files
    return _gate(
        "ONE_SEMANTIC_FSM",
        "Semantic FSMs",
        passed,
        {"canonical_module": SEMANTIC_FSM if path else None, "entrypoints": sorted(expected_defs & defs), "retired_modules_present": legacy_files},
        {"canonical_module": SEMANTIC_FSM, "entrypoints": sorted(expected_defs), "retired_modules_present": []},
        "The semantic wiring module owns the current FSM; retired composition roots must stay absent.",
    )


def _legacy_gate(root: Path, files: Mapping[str, Path]) -> GateResult:
    hits: list[dict[str, str]] = []
    for name, path in files.items():
        text = _source(path)
        for marker in LEGACY_MARKERS:
            if marker in text:
                hits.append({"module": name, "marker": marker})
    return _gate("NO_PRODUCTIVE_LEGACY_CALLERS", "Legacy semantic callers", not hits, hits, [], "Legacy flags and removed composition roots are forbidden in productive source.")


def _sheet1_gate(root: Path, files: Mapping[str, Path]) -> GateResult:
    # Scan every live Service 1 source, including Web/support surfaces that
    # can still become productive callers, while excluding tests/fixtures.
    hits = [{"module": name} for name in sorted(files) if "sheet1" in _source(files[name]).casefold()]
    return _gate("NO_PRODUCTIVE_SHEET1_FALLBACK", "Productive sheet1 fallbacks", not hits, hits, [], "Physical sheet identity must come from canonical ingestion, never a fabricated sheet1 fallback.")


def _web_bypass_gate(root: Path, files: Mapping[str, Path]) -> GateResult:
    surfaces = [name for name in ("service_1_assisted_web_v1", "service_1_assisted_web_semantic_reception_v1") if name in files]
    hits: list[dict[str, str]] = []
    for name in surfaces:
        imported = _service_imports(files[name])
        for forbidden in WEB_BYPASS_MODULES:
            if forbidden in imported:
                hits.append({"surface": name, "module": forbidden})
    return _gate("NO_WEB_ANALYSIS_BYPASSES", "Web → F7/F8/F9 bypasses", not hits, hits, [], "Web surfaces call Product Root and must not import analysis execution boundaries directly.")


def _d4_p8_gate(root: Path, files: Mapping[str, Path]) -> GateResult:
    d4 = files.get("service_1_logical_relationship_graph_v1")
    d7 = files.get("service_1_workbook_logical_model_v1")
    p8 = files.get("service_1_computability_v1")
    product = files.get(CANONICAL_ROOT)
    d4_text = _source(d4) if d4 else ""
    d7_text = _source(d7) if d7 else ""
    p8_text = _source(p8) if p8 else ""
    product_text = _source(product) if product else ""
    checks = {
        "d4_evidence_only": "evidence-only" in d4_text,
        "d4_relationship_provenance": "d4_graph_ref" in d4_text and "relationship_ref" in d4_text,
        "d7_carrier": "relationship_graph" in d7_text and "p7_p8_evidence_projection" in d7_text,
        "root_builds_d7": "build_service_1_workbook_logical_model_v1" in product_text and "workbook_logical_model" in product_text,
        "p8_governs": "build_computability_decision_from_confirmed_bindings_v1" in p8_text and "relationship_ref" in p8_text and "provenance" in p8_text,
        "root_uses_p8": "build_computability_decision_from_confirmed_bindings_v1" in product_text and "computability" in product_text,
    }
    # The source check above intentionally requires the D4 literal contract and
    # the explicit false authority default rather than executing the module.
    checks["d4_evidence_only"] = "evidence-only" in d4_text and '"join_execution_authorized": False' in d4_text
    return _gate("D4_TO_P8_PROVENANCE", "D4 → P8 provenance", all(checks.values()), checks, {key: True for key in checks}, "D4 supplies evidence; D7 carries it; P8 governs computability without creating relationships.")


def _f7_join_gate(root: Path, files: Mapping[str, Path]) -> GateResult:
    f7 = files.get(F7_MODULE)
    materializers = []
    outside_calls: list[dict[str, str]] = []
    for name, path in files.items():
        tree = _parse(path)
        defs = _module_defs(tree)
        if "_materialize_relationships" in defs:
            materializers.append(name)
        pandas_aliases: set[str] = set()
        dataframe_names: set[str] = set()
        for node in tree.body:
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name == "pandas":
                        pandas_aliases.add(alias.asname or "pandas")
            elif isinstance(node, ast.ImportFrom) and node.module == "pandas":
                for alias in node.names:
                    if alias.name == "DataFrame":
                        pandas_aliases.add(alias.asname or alias.name)
            if isinstance(node, (ast.Assign, ast.AnnAssign)):
                targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                value = node.value
                if isinstance(value, ast.Call) and isinstance(value.func, ast.Attribute) and value.func.attr == "DataFrame":
                    dataframe_names.update(target.id for target in targets if isinstance(target, ast.Name))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr in {"merge", "join"}:
                receiver = node.func.value
                is_dataframe_receiver = isinstance(receiver, ast.Name) and receiver.id in (pandas_aliases | dataframe_names)
                is_dataframe_attribute = isinstance(receiver, ast.Attribute) and receiver.attr in {"DataFrame", "dataframe"}
                if name != F7_MODULE and (is_dataframe_receiver or is_dataframe_attribute):
                    outside_calls.append({"module": name, "method": node.func.attr})
    passed = f7 is not None and materializers == [F7_MODULE] and not outside_calls
    return _gate("F7_ONLY_JOIN_MATERIALIZATION", "F7 join authorities", passed, {"materializers": materializers, "outside_join_calls": outside_calls}, {"materializers": [F7_MODULE], "outside_join_calls": []}, "F7 is the sole join materializer; D4/P8/Web remain evidence/governance surfaces.")


def _math_gate(root: Path, files: Mapping[str, Path]) -> GateResult:
    engine_path = root / MATH_ENGINE_MODULE
    class_defs = []
    scan_roots = [root / "pymia" / "services", root / "pymia" / "smartpyme", root / "pymia" / "contracts"]
    for scan_root in scan_roots:
        if not scan_root.is_dir():
            continue
        for path in scan_root.rglob("*.py"):
            if ".git" in path.parts:
                continue
            try:
                tree = _parse(path)
            except (SyntaxError, UnicodeDecodeError):
                continue
            if any(isinstance(node, ast.ClassDef) and node.name == "FormulaEngineService" for node in tree.body):
                class_defs.append(str(path.relative_to(root)).replace("\\", "/"))
    passed = engine_path.is_file() and class_defs == [MATH_ENGINE_MODULE]
    return _gate("ONE_MATH_ENGINE", "Math engines", passed, class_defs, [MATH_ENGINE_MODULE], "FormulaEngineService remains the single mathematical authority.")


def _llm_math_gate(root: Path, files: Mapping[str, Path]) -> GateResult:
    hits: list[dict[str, str]] = []
    for name, path in files.items():
        if not any(hint in name for hint in LLM_MODULE_HINTS):
            continue
        imports = _imports(_parse(path))
        for imported in sorted(imports):
            if any(token in imported for token in ("formula_engine_service", "analysis_math_execution", "analysis_evidence_preparation")):
                hits.append({"module": name, "import": imported})
    return _gate("NO_LLM_MATH_RUNTIME_AUTHORITY", "LLM → math paths", not hits, hits, [], "LLM may mediate language but cannot import math or execution authorities.")


def _post_build_gate(root: Path) -> GateResult:
    mutations: list[str] = []
    paths = (
        root / "pymia" / "cli" / "service_1_product.py",
        _service_root(root) / f"{CANONICAL_ROOT}.py",
    )
    missing = [str(path) for path in paths if not path.is_file()]
    for path in paths:
        if not path.is_file():
            continue
        tree = _parse(path)
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                targets = node.targets
            elif isinstance(node, ast.AnnAssign):
                targets = [node.target]
            else:
                continue
            for target in targets:
                if isinstance(target, ast.Subscript) and isinstance(target.value, ast.Name) and target.value.id == "ingestion_output":
                    mutations.append(f"{path.name}:line:{getattr(node, 'lineno', '?')}")
    mutations.extend(f"missing:{path}" for path in missing)
    return _gate("NO_POST_BUILD_ENVELOPE_MUTATION", "Post-build envelope mutations", not mutations, mutations, [], "The canonical ingestion envelope is passed through; it is not reinjected or reshaped after construction.")


def _result_read_gate(root: Path, files: Mapping[str, Path]) -> GateResult:
    path = files.get("service_1_result_read_boundary_v1")
    imports = sorted(_imports(_parse(path))) if path else []
    hits = [item for item in imports if any(token in item for token in FORBIDDEN_READ_IMPORTS)]
    return _gate("RESULT_READ_NO_RECALCULATION", "ResultRead → recalculation paths", path is not None and not hits, hits, [], "ResultReadBoundary validates and reads persisted F13 output without XLSX/SEM/P7/P8/F7/F8/F9/LLM execution.")


def _registry_gate(root: Path, files: Mapping[str, Path], registry: Mapping[str, Any]) -> GateResult:
    by_name, names = _registry_maps(registry)
    physical = set(files)
    duplicate_names = sorted({name for name in names if names.count(name) > 1})
    missing = sorted(physical - set(names))
    extra = sorted(set(names) - physical)
    actual_edges = {name: sorted(_service_imports(path)) for name, path in files.items()}
    recorded_edges = {name: sorted(str(dep) for dep in (item.get("imports_service_1") or ())) for name, item in by_name.items()}
    edge_drift = sorted(name for name in physical if actual_edges.get(name, []) != recorded_edges.get(name, []))
    closure = _root_closure(files)
    productive = {name for name, item in by_name.items() if item.get("disposition") == "PRODUCTIVE"}
    reachable = {name for name, item in by_name.items() if item.get("canonical_root_reachable") is True}
    count_drift = dict(registry.get("counts") or {}) != {
        key: sum(1 for item in registry.get("modules") or () if item.get("disposition") == key)
        for key in sorted({str(item.get("disposition")) for item in registry.get("modules") or ()})
    }
    passed = (
        not missing
        and not extra
        and not duplicate_names
        and not edge_drift
        and closure == reachable == productive
        and int(registry.get("total_modules") or -1) == len(names)
        and not count_drift
    )
    observed = {"missing": missing, "extra": extra, "duplicates": duplicate_names, "edge_drift": edge_drift, "root_closure_count": len(closure), "productive_count": len(productive), "reachable_count": len(reachable), "total_modules": len(names), "count_drift": count_drift}
    return _gate("REGISTRY_DRIFT_ZERO", "Registry drift", passed, observed, {"missing": [], "extra": [], "duplicates": [], "edge_drift": [], "count_drift": False}, "The registry must match physical modules, static import edges, and canonical root reachability.")


def _classification_gate(root: Path, files: Mapping[str, Path]) -> GateResult:
    missing = []
    wrong = []
    for name in DECLARATIVE_EVALUATORS:
        path = files.get(name)
        if path is None:
            missing.append(name)
            continue
        text = _source(path)
        if "classify_classification_rules" not in text:
            wrong.append(name)
    return _gate("DECLARATIVE_CLASSIFICATION", "Inline business math", not missing and not wrong, {"missing": missing, "non_declarative": wrong}, {"missing": [], "non_declarative": []}, "Migrated evaluators delegate classification to the declarative classification contract and math engine.")


def _authority_flag_gate(root: Path, files: Mapping[str, Path]) -> GateResult:
    """Ensure D7 source does not introduce truthy authority defaults."""

    path = files.get("service_1_workbook_logical_model_v1")
    if path is None:
        return _gate("D7_EVIDENCE_ONLY", "D7 evidence-only", False, ["MODULE_MISSING"], [], "D7 module is missing.")
    tree = _parse(path)
    truthy: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Dict):
            for key, value in zip(node.keys, node.values):
                if (
                    isinstance(key, ast.Constant)
                    and key.value in AUTHORITY_FLAGS
                    and isinstance(value, ast.Constant)
                    and value.value is True
                ):
                    truthy.append(str(key.value))
        if isinstance(node, ast.Assign):
            targets = node.targets
            value = node.value
        elif isinstance(node, ast.AnnAssign):
            targets = [node.target]
            value = node.value
        else:
            continue
        if isinstance(value, ast.Constant) and value.value is True:
            for target in targets:
                if isinstance(target, ast.Name) and target.id in AUTHORITY_FLAGS:
                    truthy.append(target.id)
                elif isinstance(target, ast.Dict):
                    truthy.extend(
                        str(key.value)
                        for key in target.keys
                        if isinstance(key, ast.Constant) and key.value in AUTHORITY_FLAGS
                    )
    return _gate("D7_EVIDENCE_ONLY", "D7 evidence-only", not truthy, sorted(set(truthy)), [], "D7 carries logical-model evidence only; downstream authorities remain P7/P8/F7.")


def run_architecture_guard(repo_root: str | Path | None = None) -> dict[str, Any]:
    """Run all static fitness gates and return a JSON-serializable report."""

    root = Path(repo_root).resolve() if repo_root is not None else _repo_root()
    _parse_cached.cache_clear()
    files = _service_files(root)
    registry = _registry(root)
    gates = [
        _execution_root_gate(root, files, registry),
        _execution_commands_gate(root),
        _xlsx_reader_gate(root, files),
        _semantic_fsm_gate(root, files),
        _legacy_gate(root, files),
        _sheet1_gate(root, files),
        _web_bypass_gate(root, files),
        _d4_p8_gate(root, files),
        _f7_join_gate(root, files),
        _math_gate(root, files),
        _classification_gate(root, files),
        _llm_math_gate(root, files),
        _post_build_gate(root),
        _result_read_gate(root, files),
        _authority_flag_gate(root, files),
        _registry_gate(root, files, registry),
    ]
    passed = all(gate.passed for gate in gates)
    return {
        "schema_version": "SERVICE_1_ARCHITECTURE_FITNESS_HARNESS_V1",
        "repo_root": str(root),
        "verdict": "PASS" if passed else "FAIL",
        "gates": [gate.to_dict() for gate in gates],
    }


def _format_text(report: Mapping[str, Any]) -> str:
    lines = ["PYMIA SERVICE 1 — ARCHITECTURE GUARD", ""]
    for gate in report.get("gates", ()):
        status = "PASS" if gate.get("passed") else "FAIL"
        lines.append(f"{str(gate.get('label', gate.get('gate_id', 'gate'))):36} {status}")
    lines.append("")
    lines.append(f"ARCHITECTURE: {report.get('verdict', 'FAIL')}")
    return "\n".join(lines)


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run static Servicio 1 architecture fitness gates.")
    parser.add_argument("--root", type=Path, default=None, help="Repository root (defaults to the current checkout).")
    parser.add_argument("--json", action="store_true", dest="as_json", help="Emit JSON instead of the human-readable report.")
    args = parser.parse_args(list(argv) if argv is not None else None)
    report = run_architecture_guard(args.root)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if args.as_json:
        print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False))
    else:
        print(_format_text(report))
    return 0 if report["verdict"] == "PASS" else 1


if __name__ == "__main__":  # pragma: no cover - exercised through the CLI test
    raise SystemExit(main())


__all__ = ["GateResult", "run_architecture_guard", "main"]
