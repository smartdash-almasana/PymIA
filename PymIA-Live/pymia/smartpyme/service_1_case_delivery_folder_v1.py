"""
Service 1 Case Delivery Folder V1

Creates a governed folder with the complete packet for one Service 1
execution. Does not copy the original file, perform calculations, authorize
runtime, or produce a diagnosis.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "1.0"
SERVICE_NAME = "SERVICE_1"

_README_TEXT = (
    "Servicio 1 — Carpeta de caso asistido local\n"
    "===========================================\n\n"
    "Esta carpeta contiene la salida gobernada de una ejecucion de Servicio 1.\n\n"
    "Limites explicitos:\n"
    " - No contiene el archivo XLSX original.\n"
    " - No contiene diagnostico de negocio.\n"
    " - No contiene calculos contables, fiscales ni conciliaciones definitivas.\n"
    " - Puede contener calculos operativos preliminares First Aid si el operador ejecuto tools.\n"
    " - Requiere confirmacion del dueno cuando existan preguntas pendientes.\n"
    " - Requiere control de politica de entrega antes de usar la salida como conclusion.\n\n"
    "Archivos:\n"
    " - owner_message.md          : mensaje visible para el dueno.\n"
    " - operator_packet.json      : paquete completo gobernado.\n"
    " - pipeline_result.json      : resultado de tools First Aid ejecutadas (si aplica).\n"
    " - post_tool_owner_delivery_summary.md : resumen final post-tools para el dueno (si aplica).\n"
    " - delivery_policy_guard.json : guard de politica de entrega.\n"
    " - final_qa_delivery_gate.json : QA final sobre artefactos reales de carpeta.\n"
    " - manifest.json             : inventario final de archivos con hashes.\n"
    " - detected_structure.json   : estructura XLSX detectada (si aplica).\n"
    " - column_confirmation_packet.json : preguntas de confirmacion pendientes (si aplica).\n"
    " - question_bundle.json      : preguntas canonicas al dueno con refs estables (si aplica).\n"
    " - confirmed_columns.json    : columnas confirmadas por el operador (si aplica).\n"
    " - first_aid_eligibility_gate.json : gate de elegibilidad First Aid (si aplica).\n"
    " - first_aid_result.json     : resultados descriptivos First Aid (si aplica).\n"
    " - first_aid_owner_summary.md: resumen First Aid para el dueno (si aplica).\n"
    " - owner_reentry_bridge.json : estado de reentrada de respuesta del dueno (si aplica).\n"
    " - next_owner_question.md    : proxima pregunta legible para el dueno (si aplica).\n"
    " - evidence_loop_status.json : estado del loop evidencia/preguntas/respuestas.\n"
    " - case_record.json          : registro reproducible del caso.\n"
    " - owner_delivery_packet.json: paquete legible para el dueno.\n"
    " - product_gate.json         : gate final de producto Servicio 1.\n"
    " - README.txt                : este archivo.\n"
    )


def build_service_1_delivery_policy_guard_v1(packet: dict[str, Any]) -> dict[str, Any]:
    """Build the explicit delivery policy guard for a Service 1 delivery folder."""
    return {
        "schema_version": SCHEMA_VERSION,
        "service_name": SERVICE_NAME,
        "guard_type": "SERVICE_1_DELIVERY_POLICY_GUARD",
        "status": "PENDING_DELIVERY_POLICY_GUARD",
        "delivery_policy_guard_required": True,
        "policy_guard_agent": "pymia_delivery_policy_guard",
        "decision_required_before_client_use": True,
        "runtime_authorized": False,
        "allowed_decisions": ["APPROVED_FOR_OWNER_DELIVERY_DRAFT", "NEEDS_CORRECTION", "BLOCKED"],
        "blocked_claims": [
            "auditoria",
            "certificacion",
            "conciliacion_definitiva",
            "diagnostico_integral",
            "rentabilidad_real_confirmada",
            "reemplazo_contador",
        ],
        "notes": [
            "This guard does not approve delivery by itself.",
            "The folder is ready for delivery policy control, not for autonomous client use.",
        ],
    }


def build_service_1_human_review_gate_v1(packet: dict[str, Any]) -> dict[str, Any]:
    """Temporary legacy alias for delivery policy guard builders."""
    return build_service_1_delivery_policy_guard_v1(packet)


def write_service_1_case_delivery_folder_v1(
    packet: dict[str, Any],
    base_dir: str | Path = ".tmp/service_1_cases",
) -> dict[str, Any]:
    """Create a governed case delivery folder for a Service 1 execution.

    Args:
        packet: The serializable operator packet dict (must not be mutated).
        base_dir: Parent directory for case folders.

    Returns:
        Manifest dict with case_id, case_dir, files_written, and flags.
    """
    asset = packet.get("asset", {}) or {}
    asset_id = asset.get("asset_id", "unknown")
    case_id = f"case_{asset_id}" if asset_id else "case_unknown"

    base = Path(base_dir)
    case_dir = base / case_id
    case_dir.mkdir(parents=True, exist_ok=True)

    files_written: list[str] = []
    warnings: list[str] = []

    # Write owner_message.md
    owner_message = packet.get("owner_message", "")
    if not owner_message:
        owner_message = "Servicio 1 — ejecucion completada sin mensaje visible para el dueno."
        warnings.append("owner_message empty; fallback text written.")
    (case_dir / "owner_message.md").write_text(owner_message, encoding="utf-8")
    files_written.append("owner_message.md")

    # Write detected_structure.json if present
    detected_structure = packet.get("detected_structure")
    if detected_structure is not None:
        (case_dir / "detected_structure.json").write_text(
            json.dumps(detected_structure, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        files_written.append("detected_structure.json")

    # Write column_confirmation_packet.json if present
    column_confirmation_packet = packet.get("column_confirmation_packet")
    if column_confirmation_packet is not None:
        (case_dir / "column_confirmation_packet.json").write_text(
            json.dumps(column_confirmation_packet, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        files_written.append("column_confirmation_packet.json")

    # Write question_bundle.json if present
    question_bundle = packet.get("question_bundle")
    if question_bundle is not None:
        (case_dir / "question_bundle.json").write_text(
            json.dumps(question_bundle, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        files_written.append("question_bundle.json")

    # Write confirmed_columns.json if present
    confirmed_columns = packet.get("confirmed_columns")
    if confirmed_columns is not None:
        (case_dir / "confirmed_columns.json").write_text(
            json.dumps(confirmed_columns, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        files_written.append("confirmed_columns.json")

    # Write first_aid_eligibility_gate.json if present
    first_aid_eligibility_gate = packet.get("first_aid_eligibility_gate")
    if first_aid_eligibility_gate is not None:
        (case_dir / "first_aid_eligibility_gate.json").write_text(
            json.dumps(first_aid_eligibility_gate, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        files_written.append("first_aid_eligibility_gate.json")

    # Write first_aid_result.json if present
    first_aid_result = packet.get("first_aid_result")
    if first_aid_result is not None:
        (case_dir / "first_aid_result.json").write_text(
            json.dumps(first_aid_result, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        files_written.append("first_aid_result.json")

    # Write first_aid_owner_summary.md if first_aid_result present
    first_aid_owner_summary = packet.get("first_aid_owner_summary")
    if first_aid_owner_summary is not None:
        (case_dir / "first_aid_owner_summary.md").write_text(
            first_aid_owner_summary,
            encoding="utf-8",
        )
        files_written.append("first_aid_owner_summary.md")

    # Write owner_reentry_bridge.json if present
    owner_reentry_bridge = packet.get("owner_reentry_bridge")
    if owner_reentry_bridge is not None:
        (case_dir / "owner_reentry_bridge.json").write_text(
            json.dumps(owner_reentry_bridge, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        files_written.append("owner_reentry_bridge.json")

    # Write next_owner_question.md if present
    next_owner_question = packet.get("next_owner_question")
    if isinstance(next_owner_question, dict) and next_owner_question.get("markdown"):
        (case_dir / "next_owner_question.md").write_text(
            str(next_owner_question["markdown"]),
            encoding="utf-8",
        )
        files_written.append("next_owner_question.md")

    # Write evidence_loop_status.json if present
    evidence_loop_status = packet.get("evidence_loop_status")
    if evidence_loop_status is not None:
        (case_dir / "evidence_loop_status.json").write_text(
            json.dumps(evidence_loop_status, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        files_written.append("evidence_loop_status.json")

    # Write case_record.json if present
    case_record = packet.get("case_record")
    if case_record is not None:
        (case_dir / "case_record.json").write_text(
            json.dumps(case_record, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        files_written.append("case_record.json")

    # Write owner_delivery_packet.json if present
    owner_delivery_packet = packet.get("owner_delivery_packet")
    if owner_delivery_packet is not None:
        (case_dir / "owner_delivery_packet.json").write_text(
            json.dumps(owner_delivery_packet, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        files_written.append("owner_delivery_packet.json")

    # Write product_gate.json if present
    product_gate = packet.get("product_gate")
    if product_gate is not None:
        (case_dir / "product_gate.json").write_text(
            json.dumps(product_gate, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        files_written.append("product_gate.json")

    # Write README.txt
    (case_dir / "README.txt").write_text(_README_TEXT, encoding="utf-8")
    files_written.append("README.txt")

    # operator_packet.json is written by the CLI after adding the manifest,
    # but we track it in the manifest so the expected shape is documented.
    files_written.append("operator_packet.json")

    return {
        "schema_version": SCHEMA_VERSION,
        "service_name": SERVICE_NAME,
        "case_id": case_id,
        "case_dir": str(case_dir),
        "files_written": files_written,
        "runtime_authorized": False,
        "warnings": warnings,
    }


def finalize_service_1_case_delivery_folder_v1(
    *,
    packet: dict[str, Any],
    case_dir: str | Path,
    files_written: list[str],
) -> dict[str, Any]:
    """Finalize the canonical Service 1 delivery folder.

    This extends the existing case folder instead of creating a parallel package:
    it writes an aligned README, explicit delivery policy guard, final QA gate,
    and a manifest with hashes for the actual files present in the folder.
    """
    folder = Path(case_dir)
    folder.mkdir(parents=True, exist_ok=True)

    final_files = _unique_filenames(files_written)

    readme_filename = "README.txt"
    (folder / readme_filename).write_text(_README_TEXT, encoding="utf-8")
    _append_once(final_files, readme_filename)

    delivery_policy_guard = packet.get("delivery_policy_guard")
    if not isinstance(delivery_policy_guard, dict):
        legacy_gate = packet.get("human_review_gate")
        delivery_policy_guard = legacy_gate if isinstance(legacy_gate, dict) else build_service_1_delivery_policy_guard_v1(packet)
    product_gate = packet.get("product_gate")
    if product_gate is not None:
        product_gate_filename = "product_gate.json"
        (folder / product_gate_filename).write_text(
            json.dumps(product_gate, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        _append_once(final_files, product_gate_filename)

    delivery_policy_guard_filename = "delivery_policy_guard.json"
    (folder / delivery_policy_guard_filename).write_text(
        json.dumps(delivery_policy_guard, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    _append_once(final_files, delivery_policy_guard_filename)

    final_qa_filename = "final_qa_delivery_gate.json"
    manifest_filename = "manifest.json"

    manifest_records_for_qa = _build_file_manifest_records(
        folder=folder,
        filenames=final_files,
        excluded_filenames={manifest_filename, final_qa_filename},
    )
    legacy_human_review_gate = delivery_policy_guard
    final_qa_gate = evaluate_service_1_final_delivery_folder_gate_v1(
        packet=packet,
        case_dir=folder,
        files_written=final_files,
        human_review_gate=legacy_human_review_gate,
        manifest_file_records=manifest_records_for_qa,
    )
    (folder / final_qa_filename).write_text(
        json.dumps(final_qa_gate, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    _append_once(final_files, final_qa_filename)

    manifest_payload = {
        "schema_version": SCHEMA_VERSION,
        "service_name": SERVICE_NAME,
        "manifest_type": "SERVICE_1_CANONICAL_DELIVERY_MANIFEST",
        "case_id": packet.get("case_delivery_manifest", {}).get("case_id"),
        "case_dir": str(folder),
        "delivery_status": "READY_FOR_DELIVERY_POLICY_GUARD"
        if final_qa_gate["status"] == "PASS"
        else "BLOCKED",
        "runtime_authorized": False,
        "delivery_policy_guard": delivery_policy_guard,
        "human_review_gate": delivery_policy_guard,
        "final_qa_delivery_gate": final_qa_gate,
        "hash_policy": {
            "algorithm": "sha256",
            "excluded_files": [manifest_filename],
            "reason": "manifest.json is not self-hashed because its payload contains the hash ledger.",
        },
        "files": _build_file_manifest_records(
            folder=folder,
            filenames=final_files,
            excluded_filenames={manifest_filename},
        ),
        "warnings": [
            "This manifest inventories generated Service 1 artifacts only.",
            "The original client file is not copied into the delivery folder.",
            "manifest.json is intentionally excluded from its own hash ledger.",
        ],
    }
    (folder / manifest_filename).write_text(
        json.dumps(manifest_payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    _append_once(final_files, manifest_filename)

    files_written[:] = final_files
    return manifest_payload


def evaluate_service_1_final_delivery_folder_gate_v1(
    *,
    packet: dict[str, Any],
    case_dir: str | Path,
    files_written: list[str],
    human_review_gate: dict[str, Any] | None = None,
    manifest_file_records: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Evaluate the final canonical folder artifacts without authorizing runtime."""
    folder = Path(case_dir)
    file_set = set(files_written)
    checks: list[dict[str, Any]] = []
    blockers: list[str] = []

    def add_check(check_id: str, label: str, passed: bool, required: bool = True) -> None:
        status = "PASS" if passed else "FAIL"
        checks.append(
            {
                "check_id": check_id,
                "label": label,
                "status": status,
                "required": required,
            }
        )
        if required and not passed:
            blockers.append(label)

    def has_file(filename: str) -> bool:
        return filename in file_set and (folder / filename).is_file()

    add_check("final_qa_001", "README.txt exists", has_file("README.txt"))
    add_check("final_qa_002", "operator_packet.json exists", has_file("operator_packet.json"))
    add_check("final_qa_003", "owner_message.md exists", has_file("owner_message.md"))

    pipeline_result = packet.get("pipeline_result")
    has_pipeline = isinstance(pipeline_result, dict)
    add_check(
        "final_qa_004",
        "pipeline_result.json exists when tools ran",
        (not has_pipeline) or has_file("pipeline_result.json"),
    )
    add_check(
        "final_qa_005",
        "post_tool_owner_delivery_summary.md exists when tools ran",
        (not has_pipeline) or has_file("post_tool_owner_delivery_summary.md"),
    )

    delivery_flow = pipeline_result.get("delivery_flow") if isinstance(pipeline_result, dict) else {}
    deliveries = delivery_flow.get("deliveries") if isinstance(delivery_flow, dict) else []
    if not isinstance(deliveries, list):
        deliveries = []
    expected_xlsx = [
        Path(str(delivery.get("output_path"))).name
        for delivery in deliveries
        if isinstance(delivery, dict) and delivery.get("output_path")
    ]
    add_check(
        "final_qa_006",
        "XLSX delivery files exist when tools produced them",
        all(has_file(filename) for filename in expected_xlsx),
    )

    gate = (
        human_review_gate
        if isinstance(human_review_gate, dict)
        else packet.get("delivery_policy_guard")
        if isinstance(packet.get("delivery_policy_guard"), dict)
        else packet.get("human_review_gate")
    )
    add_check(
        "final_qa_007",
        "delivery policy guard is explicit and pending",
        isinstance(gate, dict)
        and gate.get("delivery_policy_guard_required", gate.get("human_review_required")) is True
        and gate.get("status") in {"PENDING_DELIVERY_POLICY_GUARD", "PENDING_HUMAN_REVIEW"}
        and gate.get("runtime_authorized") is False,
    )
    add_check(
        "final_qa_008",
        "no runtime_authorized=True in packet",
        not _has_forbidden_runtime_authorized_true(packet),
    )
    asset = packet.get("asset") if isinstance(packet.get("asset"), dict) else {}
    original_filename = str(asset.get("filename", "")) if isinstance(asset, dict) else ""
    add_check(
        "final_qa_009",
        "final folder does not contain original client file",
        not original_filename or not (folder / original_filename).exists(),
    )
    if manifest_file_records is not None:
        add_check(
            "final_qa_010",
            "manifest SHA256 records match actual files",
            _manifest_records_match_files(folder, manifest_file_records),
        )

    status = "BLOCKED" if blockers else "PASS"
    return {
        "schema_version": SCHEMA_VERSION,
        "service_name": SERVICE_NAME,
        "gate_type": "SERVICE_1_FINAL_DELIVERY_FOLDER_QA",
        "status": status,
        "delivery_status": "READY_FOR_DELIVERY_POLICY_GUARD" if status == "PASS" else "BLOCKED",
        "runtime_authorized": False,
        "checks": checks,
        "checks_passed": sum(1 for check in checks if check["status"] == "PASS"),
        "checks_total": len(checks),
        "blockers": blockers,
        "warnings": [
            "PASS means the folder is ready for delivery policy control, not approved for autonomous use."
        ],
    }


def _has_forbidden_runtime_authorized_true(obj: Any) -> bool:
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key == "runtime_authorized" and value is True:
                return True
            if _has_forbidden_runtime_authorized_true(value):
                return True
    if isinstance(obj, list):
        return any(_has_forbidden_runtime_authorized_true(item) for item in obj)
    return False


def _unique_filenames(filenames: list[str]) -> list[str]:
    unique: list[str] = []
    for filename in filenames:
        _append_once(unique, filename)
    return unique


def _append_once(filenames: list[str], filename: str) -> None:
    if filename and filename not in filenames:
        filenames.append(filename)


def _build_file_manifest_records(*, folder: Path, filenames: list[str], excluded_filenames: set[str]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for filename in filenames:
        if filename in excluded_filenames:
            continue
        path = folder / filename
        if path.is_file():
            records.append(_build_file_manifest_record(path))
    return records


def _manifest_records_match_files(folder: Path, records: list[dict[str, Any]]) -> bool:
    for record in records:
        if not isinstance(record, dict):
            return False
        filename = record.get("filename")
        if not isinstance(filename, str) or filename == "manifest.json":
            return False
        path = folder / filename
        if not path.is_file():
            return False
        payload = path.read_bytes()
        if record.get("bytes") != len(payload):
            return False
        if record.get("sha256") != hashlib.sha256(payload).hexdigest():
            return False
    return True


def _build_file_manifest_record(path: Path) -> dict[str, Any]:
    payload = path.read_bytes()
    return {
        "filename": path.name,
        "bytes": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
    }
