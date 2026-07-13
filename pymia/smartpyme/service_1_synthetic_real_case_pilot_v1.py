from __future__ import annotations

from pathlib import Path
from typing import Final, TypedDict

from pymia.smartpyme.service_1_case_folder_manifest_contract_v1 import (
    Service1CaseFolderManifestContractV1,
    build_service_1_case_folder_manifest_contract_v1,
)
from pymia.smartpyme.service_1_delivery_manifest_audit_contract_v1 import (
    Service1DeliveryManifestAuditContractV1,
    build_service_1_delivery_manifest_audit_contract_v1,
)
from pymia.smartpyme.service_1_microservice_activation_contract_v1 import (
    Service1MicroserviceActivationContractV1,
    build_service_1_microservice_activation_contract_v1,
)
from pymia.smartpyme.service_1_owner_delivery_package_v1 import (
    Service1OwnerDeliveryPackageV1,
    build_service_1_owner_delivery_package_v1,
)
from pymia.smartpyme.service_1_controlled_delivery_demo_harness_v1 import (
    Service1ControlledDeliveryDemoRunV1,
    build_service_1_controlled_delivery_demo_sample_case_v1,
    run_service_1_controlled_delivery_demo_harness_v1,
)
from pymia.smartpyme.service_1_owner_release_action_gate_v1 import (
    Service1OwnerReleaseActionGateV1,
    build_service_1_owner_release_action_gate_v1,
)

SYNTHETIC_REAL_CASE_SCHEMA_VERSION: Final[str] = "1.0"
SERVICE_NAME: Final[str] = "SERVICE_1"
SYNTHETIC_REAL_CASE_ID: Final[str] = "service_1_synthetic_real_case_pilot_v1"


class Service1SyntheticRealCasePilotV1(TypedDict):
    schema_version: str
    service_name: str
    case_id: str
    case_type: str
    synthetic_data: bool
    real_client_data: bool
    runtime_authorized: bool
    activation: Service1MicroserviceActivationContractV1
    harness_run: Service1ControlledDeliveryDemoRunV1
    delivery_package: Service1OwnerDeliveryPackageV1
    case_manifest: Service1CaseFolderManifestContractV1
    delivery_audit: Service1DeliveryManifestAuditContractV1
    owner_release_action_gate: Service1OwnerReleaseActionGateV1
    final_delivery_allowed: bool
    delivery_notes: list[str]


def run_service_1_synthetic_real_case_pilot_v1(output_root: str | Path) -> Service1SyntheticRealCasePilotV1:
    output_root_path = Path(output_root)
    if not output_root_path.exists():
        raise FileNotFoundError(f"Output root does not exist: {output_root_path}")

    case = build_service_1_controlled_delivery_demo_sample_case_v1()
    harness_run = run_service_1_controlled_delivery_demo_harness_v1(
        case=case,
        output_root=output_root_path,
    )
    delivery_package = build_service_1_owner_delivery_package_v1(
        harness_run=harness_run,
        package_root=output_root_path,
    )

    activation = build_service_1_microservice_activation_contract_v1(
        {
            "microservice_id": "xlsx_delivery",
            "requested_capability": "operational_xlsx_draft",
            "runtime_requested": False,
            "human_review_present": True,
        }
    )
    case_manifest = build_service_1_case_folder_manifest_contract_v1(
        {
            "case_id": SYNTHETIC_REAL_CASE_ID,
            "client_alias": "synthetic_comercio_minorista_alimentos",
            "case_family": "first_aid_xlsx_delivery",
            "period": "synthetic_period",
            "operator": "synthetic_release_responsible",
            "human_reviewer": "synthetic_release_responsible",
            "intake_status": "ACCEPTED_SYNTHETIC",
            "accepted_scope": "Servicio 1 synthetic real-case pilot under human review",
            "input_files": ["synthetic_declared_values"],
            "human_review_status": "REQUIRED",
            "forbidden_claims_check": "PASSED",
            "stop_conditions": "NONE",
            "delivery_status": "READY_FOR_CLIENT_DELIVERY",
            "next_safe_action": "DELIVER_SYNTHETIC_OPERATIONAL_DRAFT",
        }
    )
    delivery_audit = build_service_1_delivery_manifest_audit_contract_v1(
        {
            "case_id": SYNTHETIC_REAL_CASE_ID,
            "manifest_present": True,
            "case_family": "first_aid_xlsx_delivery",
            "period_present": True,
            "operator_present": True,
            "human_reviewer_present": True,
            "input_files_listed": True,
            "output_files_listed": True,
            "xlsx_review_file_present": True,
            "qa_checklist_present": True,
            "qa_status": "PASSED",
            "owner_message_present": True,
            "operator_notes_present": True,
            "evidence_gap_log_present": True,
            "visible_differences_log_present": True,
            "human_review_status": "REQUIRED",
            "forbidden_claims_check": "PASSED",
            "stop_conditions": "NONE",
            "delivery_status": "READY_FOR_CLIENT_DELIVERY",
            "next_safe_action": "DELIVER_SYNTHETIC_OPERATIONAL_DRAFT_UNDER_HUMAN_REVIEW",
            "warning_flags": ["synthetic_data_only"],
        }
    )
    owner_release_action_gate = build_service_1_owner_release_action_gate_v1(
        {
            "case_folder_manifest_status": case_manifest["status"],
            "delivery_manifest_audit_status": delivery_audit["status"],
            "requested_release_action": "deliver_operational_draft",
            "release_responsible_present": True,
            "release_review_status": "REQUIRED",
            "forbidden_claims_check": "PASSED",
            "stop_conditions": "NONE",
            "delivery_allowed_by_audit": delivery_audit["delivery_allowed"],
        }
    )

    final_delivery_allowed = (
        activation["activation_allowed"] is True
        and case_manifest["delivery_allowed"] is True
        and delivery_audit["delivery_allowed"] is True
        and owner_release_action_gate["delivery_allowed"] is True
        and harness_run["runtime_authorized"] is False
        and delivery_package["runtime_authorized"] is False
    )

    return {
        "schema_version": SYNTHETIC_REAL_CASE_SCHEMA_VERSION,
        "service_name": SERVICE_NAME,
        "case_id": SYNTHETIC_REAL_CASE_ID,
        "case_type": "synthetic_real_case_pilot",
        "synthetic_data": True,
        "real_client_data": False,
        "runtime_authorized": False,
        "activation": activation,
        "harness_run": harness_run,
        "delivery_package": delivery_package,
        "case_manifest": case_manifest,
        "delivery_audit": delivery_audit,
        "owner_release_action_gate": owner_release_action_gate,
        "final_delivery_allowed": final_delivery_allowed,
        "delivery_notes": [
            "Synthetic real-case pilot: no real client data is present.",
            "Use as rehearsal of Servicio 1 delivery chain, not as client delivery proof.",
            "All outputs remain operational drafts under human review.",
        ],
    }
