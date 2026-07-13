"""
QA Delivery Gate for Service 1 operator flow.

This gate evaluates whether a Service 1 case has the minimum artifacts
required for assisted delivery. It does NOT authorize calculation,
diagnosis, or runtime execution.
"""
from __future__ import annotations

import copy
from typing import Any


def _has_forbidden_runtime_authorized_true(obj: Any) -> bool:
    """Recursively check if any nested dict/list contains runtime_authorized=True."""
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key == "runtime_authorized" and value is True:
                return True
            if _has_forbidden_runtime_authorized_true(value):
                return True
    elif isinstance(obj, list):
        for item in obj:
            if _has_forbidden_runtime_authorized_true(item):
                return True
    return False


def _has_forbidden_key(obj: Any, forbidden_key: str) -> bool:
    """Recursively check if any nested dict contains a forbidden key."""
    if isinstance(obj, dict):
        if forbidden_key in obj:
            return True
        for value in obj.values():
            if _has_forbidden_key(value, forbidden_key):
                return True
    elif isinstance(obj, list):
        for item in obj:
            if _has_forbidden_key(item, forbidden_key):
                return True
    return False


def _has_strong_recommendation(obj: Any) -> bool:
    """Check if packet contains strong recommendation claims."""
    strong_terms = ["recomendamos", "debes", "tienes que", "obligatorio", "urgent"]
    if isinstance(obj, dict):
        for key, value in obj.items():
            if isinstance(value, str):
                value_lower = value.lower()
                for term in strong_terms:
                    if term in value_lower:
                        return True
            if _has_strong_recommendation(value):
                return True
    elif isinstance(obj, list):
        for item in obj:
            if _has_strong_recommendation(item):
                return True
    return False


def evaluate_service_1_qa_delivery_gate_v1(packet: dict) -> dict:
    """
    Evaluate QA delivery gate for Service 1 case.

    Args:
        packet: The complete operator packet dict.

    Returns:
        Gate evaluation result with status PASS or BLOCKED.
        Does NOT mutate the original packet.
    """
    # Deep copy to avoid mutation
    packet_copy = copy.deepcopy(packet)

    checks: list[dict[str, Any]] = []
    blockers: list[str] = []
    warnings: list[str] = []

    # Check 1: packet.service_name == "SERVICE_1"
    check_1 = {
        "check_id": "qa_001",
        "label": "Service name is SERVICE_1",
        "status": "PASS" if packet_copy.get("service_name") == "SERVICE_1" else "FAIL",
        "required": True,
    }
    checks.append(check_1)
    if check_1["status"] == "FAIL":
        blockers.append("service_name is not SERVICE_1")

    # Check 2: packet.runtime_authorized is False
    check_2 = {
        "check_id": "qa_002",
        "label": "Top-level runtime_authorized is False",
        "status": "PASS" if packet_copy.get("runtime_authorized") is False else "FAIL",
        "required": True,
    }
    checks.append(check_2)
    if check_2["status"] == "FAIL":
        blockers.append("top-level runtime_authorized is not False")

    # Check 3: owner_message exists and is not empty
    owner_message = packet_copy.get("owner_message", "")
    check_3 = {
        "check_id": "qa_003",
        "label": "Owner message present and not empty",
        "status": "PASS" if isinstance(owner_message, str) and len(owner_message.strip()) > 0 else "FAIL",
        "required": True,
    }
    checks.append(check_3)
    if check_3["status"] == "FAIL":
        blockers.append("owner_message is missing or empty")

    # Check 4: detected_structure exists for XLSX (if XLSX was processed)
    detected_structure = packet_copy.get("detected_structure")
    asset = packet_copy.get("asset", {})
    filename = asset.get("filename", "") if isinstance(asset, dict) else ""
    has_xlsx = detected_structure is not None or filename.lower().endswith(".xlsx")
    check_4 = {
        "check_id": "qa_004",
        "label": "Detected structure present for XLSX",
        "status": "PASS" if detected_structure is not None else "FAIL",
        "required": has_xlsx,
    }
    checks.append(check_4)
    if check_4["status"] == "FAIL" and check_4["required"]:
        blockers.append("detected_structure missing for XLSX case")

    # Check 5: column_confirmation_packet exists for XLSX
    column_confirmation = packet_copy.get("column_confirmation_packet")
    check_5 = {
        "check_id": "qa_005",
        "label": "Column confirmation packet present for XLSX",
        "status": "PASS" if column_confirmation is not None else "FAIL",
        "required": has_xlsx,
    }
    checks.append(check_5)
    if check_5["status"] == "FAIL" and check_5["required"]:
        blockers.append("column_confirmation_packet missing for XLSX case")

    # Check 6: column_confirmation_packet.runtime_authorized is False
    if column_confirmation is not None:
        check_6_status = column_confirmation.get("runtime_authorized") is False
    else:
        check_6_status = True  # Not applicable if no column_confirmation
    check_6 = {
        "check_id": "qa_006",
        "label": "Column confirmation packet runtime_authorized is False",
        "status": "PASS" if check_6_status else "FAIL",
        "required": column_confirmation is not None,
    }
    checks.append(check_6)
    if check_6["status"] == "FAIL":
        blockers.append("column_confirmation_packet.runtime_authorized is not False")

    # Check 7: case_delivery_manifest exists
    case_manifest = packet_copy.get("case_delivery_manifest")
    check_7 = {
        "check_id": "qa_007",
        "label": "Case delivery manifest present",
        "status": "PASS" if case_manifest is not None else "FAIL",
        "required": True,
    }
    checks.append(check_7)
    if check_7["status"] == "FAIL":
        blockers.append("case_delivery_manifest missing")

    # Check 8: case_delivery_manifest.runtime_authorized is False
    if case_manifest is not None:
        check_8_status = case_manifest.get("runtime_authorized") is False
    else:
        check_8_status = True  # Not applicable if no manifest
    check_8 = {
        "check_id": "qa_008",
        "label": "Case delivery manifest runtime_authorized is False",
        "status": "PASS" if check_8_status else "FAIL",
        "required": case_manifest is not None,
    }
    checks.append(check_8)
    if check_8["status"] == "FAIL":
        blockers.append("case_delivery_manifest.runtime_authorized is not False")

    # Check 9: packet does not contain "diagnosis"
    check_9 = {
        "check_id": "qa_009",
        "label": "No diagnosis key in packet",
        "status": "PASS" if not _has_forbidden_key(packet_copy, "diagnosis") else "FAIL",
        "required": True,
    }
    checks.append(check_9)
    if check_9["status"] == "FAIL":
        blockers.append("packet contains forbidden 'diagnosis' key")

    # Check 10: packet does not contain "accounting_result"
    check_10 = {
        "check_id": "qa_010",
        "label": "No accounting_result key in packet",
        "status": "PASS" if not _has_forbidden_key(packet_copy, "accounting_result") else "FAIL",
        "required": True,
    }
    checks.append(check_10)
    if check_10["status"] == "FAIL":
        blockers.append("packet contains forbidden 'accounting_result' key")

    # Check 11: packet does not contain strong recommendation
    check_11 = {
        "check_id": "qa_011",
        "label": "No strong recommendation in packet",
        "status": "PASS" if not _has_strong_recommendation(packet_copy) else "FAIL",
        "required": True,
    }
    checks.append(check_11)
    if check_11["status"] == "FAIL":
        blockers.append("packet contains strong recommendation claims")

    # Check 12: no runtime_authorized=True anywhere in packet
    check_12 = {
        "check_id": "qa_012",
        "label": "No runtime_authorized=True at any level",
        "status": "PASS" if not _has_forbidden_runtime_authorized_true(packet_copy) else "FAIL",
        "required": True,
    }
    checks.append(check_12)
    if check_12["status"] == "FAIL":
        blockers.append("packet contains runtime_authorized=True at some level")

    # Determine overall status
    required_failures = [c for c in checks if c["required"] and c["status"] == "FAIL"]
    status = "BLOCKED" if required_failures else "PASS"

    # Count passed
    passed_count = sum(1 for c in checks if c["status"] == "PASS")
    total_count = len(checks)

    return {
        "schema_version": "1.0",
        "service_name": "SERVICE_1",
        "gate_type": "QA_DELIVERY_GATE",
        "status": status,
        "runtime_authorized": False,
        "checks": checks,
        "checks_passed": passed_count,
        "checks_total": total_count,
        "warnings": warnings,
        "blockers": blockers,
    }
