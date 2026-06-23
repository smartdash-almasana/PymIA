from __future__ import annotations

from typing import Any, Literal, TypedDict

from pymia.smartpyme.service_1_microservice_registry_contract_v1 import (
    build_service_1_microservice_registry_contract_v1,
)

ActivationStatus = Literal[
    "ACTIVATION_ALLOWED",
    "INVALID_INPUT",
    "MISSING_REQUIRED_FIELDS",
    "UNKNOWN_MICROSERVICE",
    "BLOCKED_BY_REGISTRY",
    "BLOCKED_BY_DEPENDENCIES",
    "BLOCKED_BY_FORBIDDEN_CAPABILITY",
    "BLOCKED_BY_RUNTIME_REQUEST",
    "BLOCKED_BY_MISSING_HUMAN_REVIEW",
]

REQUIRED_ACTIVATION_FIELDS: tuple[str, ...] = (
    "microservice_id",
    "requested_capability",
    "runtime_requested",
    "human_review_present",
)

FINALITY_CAPABILITY_TERMS: tuple[str, ...] = (
    "definitiva",
    "cerrada",
    "final",
    "certificacion",
    "certificación",
    "auditoria",
    "auditoría",
    "fiscal",
    "impuesto",
    "asiento",
    "api",
    "ocr",
    "parser",
    "chatbot",
    "llm",
)


class Service1MicroserviceActivationContractV1(TypedDict):
    status: ActivationStatus
    microservice_id: str | None
    requested_capability: str
    activated_microservice: str | None
    activation_allowed: bool
    runtime_authorized: bool
    human_review_required: bool
    required_human_actions: list[str]
    blocked_reason: str | None
    blocked_capabilities: list[str]
    next_allowed_action: str


def build_service_1_microservice_activation_contract_v1(activation_input: dict[str, Any]) -> Service1MicroserviceActivationContractV1:
    if not isinstance(activation_input, dict):
        return _blocked(
            status="INVALID_INPUT",
            microservice_id=None,
            requested_capability="",
            reason="activation_input_must_be_dict",
            next_action="provide_activation_input_dict",
        )

    missing = [field for field in REQUIRED_ACTIVATION_FIELDS if field not in activation_input or _is_blank(activation_input[field])]
    if missing:
        return _blocked(
            status="MISSING_REQUIRED_FIELDS",
            microservice_id=_optional_text(activation_input.get("microservice_id")),
            requested_capability=_optional_text(activation_input.get("requested_capability")) or "",
            reason="missing_required_fields:" + ",".join(missing),
            next_action="complete_required_fields",
        )

    microservice_id = str(activation_input["microservice_id"]).strip()
    requested_capability = str(activation_input["requested_capability"]).strip()
    registry_result = build_service_1_microservice_registry_contract_v1(
        {
            "microservice_id": microservice_id,
            "available_microservices": activation_input.get("available_microservices"),
        }
    )

    if registry_result["status"] == "UNKNOWN_MICROSERVICE":
        return _blocked(
            status="UNKNOWN_MICROSERVICE",
            microservice_id=microservice_id,
            requested_capability=requested_capability,
            reason="unknown_microservice",
            next_action="select_supported_service_1_microservice",
        )

    if registry_result["status"] == "BLOCKED_MICROSERVICE":
        return _blocked_from_registry(
            status="BLOCKED_BY_REGISTRY",
            requested_capability=requested_capability,
            registry_result=registry_result,
            reason="microservice_blocked_by_registry",
            next_action="keep_microservice_blocked",
        )

    if registry_result["status"] == "BLOCKED_BY_DEPENDENCIES":
        return _blocked_from_registry(
            status="BLOCKED_BY_DEPENDENCIES",
            requested_capability=requested_capability,
            registry_result=registry_result,
            reason="missing_dependencies:" + ",".join(registry_result["missing_dependencies"]),
            next_action="complete_microservice_dependencies",
        )

    if bool(activation_input["runtime_requested"]):
        return _blocked_from_registry(
            status="BLOCKED_BY_RUNTIME_REQUEST",
            requested_capability=requested_capability,
            registry_result=registry_result,
            reason="runtime_not_authorized_for_service_1_v1",
            next_action="request_non_runtime_activation",
        )

    blocked_capability = _matches_blocked_capability(
        requested_capability=requested_capability,
        blocked_capabilities=registry_result["blocked_capabilities"],
    )
    if blocked_capability:
        return _blocked_from_registry(
            status="BLOCKED_BY_FORBIDDEN_CAPABILITY",
            requested_capability=requested_capability,
            registry_result=registry_result,
            reason="forbidden_capability:" + blocked_capability,
            next_action=registry_result["next_allowed_action"],
        )

    if bool(registry_result["human_review_required"]) and activation_input["human_review_present"] is not True:
        return _blocked_from_registry(
            status="BLOCKED_BY_MISSING_HUMAN_REVIEW",
            requested_capability=requested_capability,
            registry_result=registry_result,
            reason="human_review_required",
            next_action="assign_human_review",
            required_human_actions=["assign_human_review"],
        )

    return {
        "status": "ACTIVATION_ALLOWED",
        "microservice_id": microservice_id,
        "requested_capability": requested_capability,
        "activated_microservice": microservice_id,
        "activation_allowed": True,
        "runtime_authorized": False,
        "human_review_required": bool(registry_result["human_review_required"]),
        "required_human_actions": ["maintain_human_review"] if registry_result["human_review_required"] else [],
        "blocked_reason": None,
        "blocked_capabilities": list(registry_result["blocked_capabilities"]),
        "next_allowed_action": registry_result["next_allowed_action"],
    }


def _matches_blocked_capability(*, requested_capability: str, blocked_capabilities: list[str]) -> str | None:
    normalized_request = _normalize(requested_capability)
    for blocked in blocked_capabilities:
        normalized_blocked = _normalize(blocked)
        if normalized_blocked and (normalized_blocked in normalized_request or normalized_request in normalized_blocked):
            return blocked
    if any(term in normalized_request for term in FINALITY_CAPABILITY_TERMS):
        return "finality_or_external_runtime_request"
    return None


def _normalize(value: str) -> str:
    return value.strip().lower().replace(" ", "_").replace("-", "_")


def _is_blank(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip() == ""
    if isinstance(value, (list, tuple, set, dict)):
        return len(value) == 0
    return False


def _optional_text(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _blocked(*, status: ActivationStatus, microservice_id: str | None, requested_capability: str, reason: str, next_action: str) -> Service1MicroserviceActivationContractV1:
    return {
        "status": status,
        "microservice_id": microservice_id,
        "requested_capability": requested_capability,
        "activated_microservice": None,
        "activation_allowed": False,
        "runtime_authorized": False,
        "human_review_required": True,
        "required_human_actions": [],
        "blocked_reason": reason,
        "blocked_capabilities": [],
        "next_allowed_action": next_action,
    }


def _blocked_from_registry(
    *,
    status: ActivationStatus,
    requested_capability: str,
    registry_result: dict[str, Any],
    reason: str,
    next_action: str,
    required_human_actions: list[str] | None = None,
) -> Service1MicroserviceActivationContractV1:
    return {
        "status": status,
        "microservice_id": registry_result["microservice_id"],
        "requested_capability": requested_capability,
        "activated_microservice": None,
        "activation_allowed": False,
        "runtime_authorized": False,
        "human_review_required": bool(registry_result["human_review_required"]),
        "required_human_actions": required_human_actions or [],
        "blocked_reason": reason,
        "blocked_capabilities": list(registry_result["blocked_capabilities"]),
        "next_allowed_action": next_action,
    }
