import json
from pathlib import Path
import pytest

from pymia.contracts.evidence_v1 import StructuredEvidence
# These will fail to import initially until pymia/contracts/attachment_lifecycle_v1.py is created
from pymia.contracts.attachment_lifecycle_v1 import (
    AttachmentLifecycleState,
    AttachmentParseStatus,
    AttachmentProcessingStatus,
    EvidenceBundle,
    PymIAIngressEnvelope,
)
from pymia.interfaces.conversational_port import ConversationalInput, ClinicalConversationalPort
from pymia.hermes.adapter import HermesInput, HermesAdapter
from pymia.services.initial_laboratory_anamnesis_service import InitialLaboratoryAnamnesisService


def test_structured_evidence_remains_clean():
    """Requirement C.1: StructuredEvidence does not contain any lifecycle or parse status fields."""
    fields = set(StructuredEvidence.model_fields.keys())
    assert "lifecycle_state" not in fields
    assert "parse_status" not in fields
    assert "parse_error" not in fields
    assert "root_cause" not in fields
    assert "user_message" not in fields
    assert "attachment_id" not in fields
    assert "parser_name" not in fields


def test_attachment_processing_status_model_validation():
    """Requirement C.2 & C.3: AttachmentProcessingStatus validation and EvidenceBundle grouping."""
    status = AttachmentProcessingStatus(
        attachment_id="att-123",
        file_name="pyme_ventas.xlsx",
        mime_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        source_channel="telegram",
        lifecycle_state=AttachmentLifecycleState.PARSE_FAILED,
        parse_status=AttachmentParseStatus.FAILED,
        parse_error="Traceback (most recent call last):\nValueError: Sheet 'Ventas' missing",
        root_cause="excel_parsing_error",
        user_message="Recibí el Excel, pero no pude procesarlo correctamente. Causa: El archivo no tiene la hoja requerida.",
        parser_name="excel_evidence_v1",
        evidence=None,
    )

    assert status.attachment_id == "att-123"
    assert status.file_name == "pyme_ventas.xlsx"
    assert status.mime_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    assert status.source_channel == "telegram"
    assert status.lifecycle_state == AttachmentLifecycleState.PARSE_FAILED
    assert status.parse_status == AttachmentParseStatus.FAILED
    assert status.parse_error is not None
    assert "Traceback" in status.parse_error
    assert status.root_cause == "excel_parsing_error"
    assert status.user_message.startswith("Recibí el Excel, pero no pude")
    assert status.parser_name == "excel_evidence_v1"
    assert status.evidence is None

    # Grouping in EvidenceBundle
    bundle = EvidenceBundle(attachments=[status])
    assert len(bundle.attachments) == 1
    assert bundle.attachments[0].attachment_id == "att-123"

    # Ingress envelope
    envelope = PymIAIngressEnvelope(
        tenant_id="tenant-xyz",
        channel="telegram",
        text="hola",
        bundle=bundle,
    )
    assert envelope.tenant_id == "tenant-xyz"
    assert envelope.bundle.attachments[0].file_name == "pyme_ventas.xlsx"


def test_conversational_input_accepts_evidence_bundle():
    """Requirement C.4: ConversationalInput accepts and propagates the EvidenceBundle."""
    bundle = EvidenceBundle(
        attachments=[
            AttachmentProcessingStatus(
                attachment_id="att-abc",
                file_name="compras.xlsx",
                mime_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                source_channel="local",
                lifecycle_state=AttachmentLifecycleState.RECEIVED,
                parse_status=AttachmentParseStatus.PENDING,
            )
        ]
    )

    conv_input = ConversationalInput(
        tenant_id="tenant-test",
        channel="telegram",
        text="subo mis compras",
        bundle=bundle,
    )
    assert conv_input.bundle == bundle


def test_hermes_input_wrapper_passes_evidence_bundle():
    """Requirement C.5: HermesInput wrapper accepts and propagates evidence_bundle to port."""
    bundle = EvidenceBundle(
        attachments=[
            AttachmentProcessingStatus(
                attachment_id="att-456",
                file_name="ventas.xlsx",
                mime_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                source_channel="telegram",
                lifecycle_state=AttachmentLifecycleState.RECEIVED,
                parse_status=AttachmentParseStatus.PENDING,
            )
        ]
    )

    hermes_input = HermesInput(
        tenant_id="tenant-test",
        channel="telegram",
        message_text="subo ventas",
        evidence_bundle=bundle,
    )
    assert hermes_input.evidence_bundle == bundle

    adapter = HermesAdapter()
    captured_input = None
    original_handle = adapter._port.handle

    def spy_handle(input_obj):
        nonlocal captured_input
        captured_input = input_obj
        return original_handle(input_obj)

    adapter._port.handle = spy_handle
    try:
        adapter.handle(hermes_input)
    finally:
        adapter._port.handle = original_handle

    assert captured_input is not None
    assert captured_input.bundle == bundle


def test_parse_succeeded_passes_evidence_to_port():
    """Requirement C.6: PARSE_SUCCEEDED passes the StructuredEvidence directly to the service processing."""
    service = InitialLaboratoryAnamnesisService()
    
    evidence = StructuredEvidence(
        tenant_id="tenant-success-test",
        document_type="xlsx_operational_evidence",
        source="xlsx_upload",
        file_name="good.xlsx",
        computed_variables={"ventas_total": 1000000.0, "costos_total": 450000.0},
    )

    status = AttachmentProcessingStatus(
        attachment_id="att-success",
        file_name="good.xlsx",
        mime_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        source_channel="telegram",
        lifecycle_state=AttachmentLifecycleState.PARSE_SUCCEEDED,
        parse_status=AttachmentParseStatus.SUCCEEDED,
        evidence=evidence,
    )
    bundle = EvidenceBundle(attachments=[status])

    result = service.process(
        tenant_id="tenant-success-test",
        channel="telegram",
        text="hola subo mi planilla",
        bundle=bundle,
    )

    assert result is not None
    # Verify that the service successfully used the evidence and is not in error state
    assert result.anamnesis.estado_conversacional != "error_procesamiento_evidencia"
    assert result.laboratorio.estado_conversacional != "error_procesamiento_evidencia"


def test_parse_failed_generates_explicit_response():
    """Requirement C.7: PARSE_FAILED prevents silent fallback and returns an explicit clinical error message to user."""
    service = InitialLaboratoryAnamnesisService()

    status = AttachmentProcessingStatus(
        attachment_id="att-failed",
        file_name="bad_columns.xlsx",
        mime_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        source_channel="telegram",
        lifecycle_state=AttachmentLifecycleState.PARSE_FAILED,
        parse_status=AttachmentParseStatus.FAILED,
        parse_error="ValueError: Column 'venta' is missing",
        root_cause="invalid_column_header",
        user_message="Recibí el Excel, pero no pude procesarlo correctamente. Causa: El archivo no contiene la columna requerida.",
        evidence=None,
    )
    bundle = EvidenceBundle(attachments=[status])

    result = service.process(
        tenant_id="tenant-fail-test",
        channel="telegram",
        text="subo mi excel para que lo mires",
        bundle=bundle,
    )

    assert result is not None
    assert "Recibí el Excel, pero no pude procesarlo correctamente." in result.message
    assert "El archivo no contiene la columna requerida" in result.message
    # No technical tracebacks leaked to user
    assert "ValueError:" not in result.message

    # Conversation status reflects error
    assert result.anamnesis.estado_conversacional == "error_procesamiento_evidencia"
    assert result.laboratorio.estado_conversacional == "error_procesamiento_evidencia"


def test_parser_exception_becomes_parse_failed_contractual(tmp_path: Path):
    """Requirement C.8: Parser exception is converted into a failed AttachmentProcessingStatus."""
    from tools.excel_evidence import main

    evidence_out = tmp_path / "evidence.json"
    kernel_out = tmp_path / "kernel.json"
    audit_out = tmp_path / "audit.json"

    # Supply an invalid non-existent path to trigger FileNotFoundError
    argv = [
        "--excel", "completamente_inexistente.xlsx",
        "--tenant-id", "tenant-exception-test",
        "--evidence-output", str(evidence_out),
        "--kernel-output", str(kernel_out),
        "--audit-output", str(audit_out),
    ]

    ret = main(argv)
    assert ret == 0  # Tool exits with 0 and writes error contract

    assert evidence_out.exists()
    assert kernel_out.exists()
    assert not audit_out.exists()  # No audit file generated on failure

    with open(evidence_out, "r", encoding="utf-8") as f:
        status_data = json.load(f)

    status = AttachmentProcessingStatus.model_validate(status_data)
    assert status.file_name == "completamente_inexistente.xlsx"
    assert status.lifecycle_state == AttachmentLifecycleState.PARSE_FAILED
    assert status.parse_status == AttachmentParseStatus.FAILED
    assert status.root_cause == "file_not_found"
    assert "FileNotFoundError" in status.parse_error
    assert "El archivo Excel no pudo ser encontrado" in status.user_message
    assert status.evidence is None


def test_metadata_does_not_contain_opaque_parse_fields():
    """Requirement C.9: StructuredEvidence.metadata must not carry control/lifecycle attributes."""
    evidence = StructuredEvidence(
        tenant_id="tenant-123",
        document_type="xlsx_operational_evidence",
        source="xlsx_upload",
        file_name="pyme.xlsx",
        metadata={"sheet_reports": {"ventas": "OK"}},
    )
    # Check that metadata does not contain parse_status or parse_error
    assert "parse_status" not in evidence.metadata
    assert "parse_error" not in evidence.metadata


def test_textual_fallback_blocked_if_attachments_not_empty():
    """Requirement C.10: Falling back to textual request is blocked if bundle has attachments (refuse to silently bypass)."""
    service = InitialLaboratoryAnamnesisService()

    status = AttachmentProcessingStatus(
        attachment_id="att-failed-2",
        file_name="ventas_rotas.xlsx",
        mime_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        source_channel="telegram",
        lifecycle_state=AttachmentLifecycleState.PARSE_FAILED,
        parse_status=AttachmentParseStatus.FAILED,
        parse_error="KeyError: 'costo'",
        root_cause="excel_parsing_error",
        user_message="Recibí el Excel, pero no pude procesarlo correctamente. Causa: Estructura de tabla rota.",
        evidence=None,
    )
    bundle = EvidenceBundle(attachments=[status])

    result = service.process(
        tenant_id="tenant-fallback-block",
        channel="telegram",
        text="hola subo mi excel de ventas",
        bundle=bundle,
    )

    assert result is not None
    # The message returned should be the explicit parsing failure explanation
    assert "Recibí el Excel, pero no pude procesarlo correctamente." in result.message
    # It must NOT fall back to requesting sales/costs textually
    assert "Señal económico-operacional registrada" not in result.message


def test_document_intake_received_or_downloaded_but_not_parsed(tmp_path: Path):
    """Requirement F: If state is RECEIVED or DOWNLOADED but not PARSE_ATTEMPTED, return 'Recibí el archivo, pero todavía no fue procesado.'"""
    import importlib.util
    import sys
    conversa_dir = Path(__file__).resolve().parent.parent.parent / "conversa-engine"
    if str(conversa_dir) not in sys.path:
        sys.path.insert(0, str(conversa_dir))

    # Load document_intake
    module_path = conversa_dir / "document_intake.py"
    spec = importlib.util.spec_from_file_location("document_intake", module_path)
    document_intake = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(document_intake)
    intake_document = document_intake.intake_document

    # Force a scenario where route is BEM_AI (meaning not INTERNAL_FACT/parsed), so it is not PARSE_ATTEMPTED
    state_path = tmp_path / "state"
    file_path = "documento_administrativo.pdf"

    msg = intake_document(
        tenant_id="tenant-intake-not-parsed-test",
        user_id="user-999",
        file_path=file_path,
        file_name="documento_administrativo.pdf",
        mime_type="application/pdf",
        expected_schema="unknown",
        entropy_level=0.9,  # higher entropy leads to BEM_AI/NARRATIVE
        base_path=state_path,
    )

    # In BEM_AI/NARRATIVE route, the file is received/downloaded but not parse_attempted for clinical evidence.
    # The requirement specifies that for RECEIVED/DOWNLOADED but not PARSE_ATTEMPTED, we return the explicit status.
    assert "Recibí el archivo, pero todavía no fue procesado." in msg


def test_document_intake_fails_and_saves_state(tmp_path: Path):
    """E2E/Integration test: Verifies document_intake failure paths and state store persistence."""
    import importlib.util
    import sys
    conversa_dir = Path(__file__).resolve().parent.parent.parent / "conversa-engine"
    if str(conversa_dir) not in sys.path:
        sys.path.insert(0, str(conversa_dir))

    # Load document_intake
    module_path = conversa_dir / "document_intake.py"
    spec = importlib.util.spec_from_file_location("document_intake", module_path)
    document_intake = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(document_intake)
    intake_document = document_intake.intake_document

    # Load intake_repository
    module_path_repo = conversa_dir / "intake_repository.py"
    spec_repo = importlib.util.spec_from_file_location("intake_repository", module_path_repo)
    intake_repository = importlib.util.module_from_spec(spec_repo)
    spec_repo.loader.exec_module(intake_repository)
    DocumentIntakeRepository = intake_repository.DocumentIntakeRepository

    state_path = tmp_path / "state"
    file_path = "broken_file.xlsx"

    msg = intake_document(
        tenant_id="tenant-intake-e2e-fail",
        user_id="user-111",
        file_path=file_path,
        file_name="broken_file.xlsx",
        mime_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        expected_schema="unknown",
        entropy_level=0.1,  # triggers INTERNAL_FACT
        base_path=state_path,
    )

    assert "Recibí el Excel, pero no pude procesarlo correctamente." in msg

    # State repository must contain updated lifecycle status
    repo = DocumentIntakeRepository(base_path=state_path)
    state = repo.load(session_id="tenant-intake-e2e-fail/user-111")

    assert state.last_file_name == "broken_file.xlsx"
    assert state.last_lifecycle_state == AttachmentLifecycleState.PARSE_FAILED
    assert state.last_parse_status == AttachmentParseStatus.FAILED
    assert state.last_parse_error is not None
    assert "FileNotFoundError" in state.last_parse_error or "Exception" in state.last_parse_error
    assert state.last_root_cause == "file_not_found"
    assert "El archivo Excel no pudo ser encontrado" in state.last_user_message
