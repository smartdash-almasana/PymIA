from __future__ import annotations

from pymia.audit_result.models import OperationalAuditResult


class OperationalAuditValidationError(ValueError):
    pass


def validate_operational_audit_result(result: OperationalAuditResult) -> OperationalAuditResult:
    payload = result.model_dump(mode="json")

    forbidden = {"tables", "raw_tables", "kernel_output", "excel_bytes"}
    for key in forbidden:
        if key in payload:
            raise OperationalAuditValidationError(f"Forbidden top-level key present: {key}")

    if not result.narrative_payload.forbidden_inferences:
        raise OperationalAuditValidationError("forbidden_inferences cannot be empty")

    if not result.narrative_payload.allowed_messages:
        raise OperationalAuditValidationError("allowed_messages cannot be empty")

    for message in result.narrative_payload.allowed_messages:
        if not message.evidence_ids:
            raise OperationalAuditValidationError(f"Message without evidence ids: {message.message_id}")

    return result
