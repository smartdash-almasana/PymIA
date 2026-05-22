import pytest

from pymia.contracts.attachment_lifecycle_v1 import (
    AttachmentLifecycleState,
    AttachmentParseStatus,
    AttachmentProcessingStatus,
    EvidenceBundle,
)
from pymia.contracts.evidence_v1 import StructuredEvidence


LIFECYCLE_FIELDS = {"lifecycle_state", "parse_status", "parse_error"}


def _evidence() -> StructuredEvidence:
    return StructuredEvidence(
        tenant_id="tenant_test",
        document_type="xlsx_operational_evidence",
        source="xlsx_upload",
        file_name="ventas.xlsx",
        computed_variables={"ventas_total": 1000.0},
    )


def test_structured_evidence_has_no_lifecycle_fields():
    fields = set(StructuredEvidence.model_fields.keys())
    assert not (fields & LIFECYCLE_FIELDS)


def test_parse_failed_attachment_cannot_carry_structured_evidence():
    with pytest.raises(ValueError):
        AttachmentProcessingStatus(
            attachment_id="att_001",
            file_name="ventas.xlsx",
            mime_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            source_channel="telegram",
            lifecycle_state=AttachmentLifecycleState.PARSE_FAILED,
            parse_status=AttachmentParseStatus.FAILED,
            parse_error="internal parser traceback digest",
            root_cause="formato no compatible",
            user_message="Recibí el Excel, pero no pude procesarlo correctamente. Causa: formato no compatible.",
            parser_name="local_excel_evidence_v1",
            evidence=_evidence(),
        )


def test_parse_succeeded_attachment_requires_structured_evidence():
    with pytest.raises(ValueError):
        AttachmentProcessingStatus(
            attachment_id="att_002",
            file_name="ventas.xlsx",
            mime_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            source_channel="telegram",
            lifecycle_state=AttachmentLifecycleState.PARSE_SUCCEEDED,
            parse_status=AttachmentParseStatus.SUCCEEDED,
            parser_name="local_excel_evidence_v1",
            evidence=None,
        )


def test_evidence_bundle_groups_attachments_and_exposes_first_evidence():
    evidence = _evidence()
    bundle = EvidenceBundle(
        attachments=[
            AttachmentProcessingStatus(
                attachment_id="att_003",
                file_name="ventas.xlsx",
                mime_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                source_channel="telegram",
                lifecycle_state=AttachmentLifecycleState.PARSE_SUCCEEDED,
                parse_status=AttachmentParseStatus.SUCCEEDED,
                parser_name="local_excel_evidence_v1",
                evidence=evidence,
            )
        ]
    )

    assert bundle.has_attachments is True
    assert bundle.first_structured_evidence() == evidence
    assert len(bundle.succeeded_attachments()) == 1
    assert bundle.failed_attachments() == []


def test_failed_attachment_safe_user_message_does_not_expose_parse_error():
    attachment = AttachmentProcessingStatus(
        attachment_id="att_004",
        file_name="ventas.xlsx",
        mime_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        source_channel="telegram",
        lifecycle_state=AttachmentLifecycleState.PARSE_FAILED,
        parse_status=AttachmentParseStatus.FAILED,
        parse_error="Traceback at /secret/internal/path.py token=secret",
        root_cause="el archivo no tiene hojas tabulares detectables",
        parser_name="local_excel_evidence_v1",
        evidence=None,
    )

    message = attachment.safe_user_message()
    assert "Recibí ventas.xlsx" in message
    assert "hojas tabulares" in message
    assert "Traceback" not in message
    assert "/secret" not in message
    assert "token" not in message
