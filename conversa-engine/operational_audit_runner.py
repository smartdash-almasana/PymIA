from __future__ import annotations

import base64
import sys
from dataclasses import dataclass
from pathlib import Path

from pymia.contracts.attachment_lifecycle_v1 import (
    AttachmentLifecycleState,
    AttachmentParseStatus,
    AttachmentProcessingStatus,
)


@dataclass
class OperationalAuditRunResult:
    ok: bool
    evidence_path: Path
    kernel_path: Path
    audit_path: Path
    attachment_status: AttachmentProcessingStatus


def _safe_root_cause(exc: Exception | None = None) -> str:
    if exc is None:
        return "no se pudo generar evidencia computable a partir del archivo"
    return "el archivo no pudo procesarse con el parser disponible"


def _failed_attachment_status(
    *,
    excel_path: str | Path,
    source_channel: str,
    parser_name: str,
    exc: Exception | None = None,
) -> AttachmentProcessingStatus:
    file_name = Path(excel_path).name
    root_cause = _safe_root_cause(exc)
    return AttachmentProcessingStatus(
        attachment_id=file_name,
        file_name=file_name,
        mime_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        source_channel=source_channel,
        lifecycle_state=AttachmentLifecycleState.PARSE_FAILED,
        parse_status=AttachmentParseStatus.FAILED,
        parse_error=repr(exc) if exc is not None else "audit output was not produced",
        root_cause=root_cause,
        user_message=f"Recibí el Excel, pero no pude procesarlo correctamente. Causa: {root_cause}.",
        parser_name=parser_name,
        evidence=None,
    )


def run_excel_operational_audit(
    excel_path: str | Path,
    tenant_id: str,
    session_id: str,
    output_dir: str | Path,
) -> OperationalAuditRunResult:
    # Ensure repo root is on path for tools.excel_evidence
    repo_root = Path(__file__).resolve().parents[1]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))

    from tools.excel_evidence import build_excel_structured_evidence, main

    session_bytes = str(session_id).encode("utf-8")
    encoded_id = base64.urlsafe_b64encode(session_bytes).decode("ascii").rstrip("=")
    session_dir = Path(output_dir) / encoded_id
    session_dir.mkdir(parents=True, exist_ok=True)

    evidence_path = session_dir / "evidence.json"
    kernel_path = session_dir / "kernel.json"
    audit_path = session_dir / "operational_audit_result.json"
    parser_name = "local_excel_evidence_v1"

    argv = [
        "--excel", str(excel_path),
        "--tenant-id", tenant_id,
        "--evidence-output", str(evidence_path),
        "--kernel-output", str(kernel_path),
        "--audit-output", str(audit_path),
    ]

    try:
        ret = main(argv)
        ok = (ret == 0 and audit_path.exists())
        if not ok:
            return OperationalAuditRunResult(
                ok=False,
                evidence_path=evidence_path,
                kernel_path=kernel_path,
                audit_path=audit_path,
                attachment_status=_failed_attachment_status(
                    excel_path=excel_path,
                    source_channel="telegram",
                    parser_name=parser_name,
                ),
            )

        evidence = build_excel_structured_evidence(excel_path=excel_path, tenant_id=tenant_id)
        attachment_status = AttachmentProcessingStatus(
            attachment_id=Path(excel_path).name,
            file_name=Path(excel_path).name,
            mime_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            source_channel="telegram",
            lifecycle_state=AttachmentLifecycleState.PARSE_SUCCEEDED,
            parse_status=AttachmentParseStatus.SUCCEEDED,
            parser_name=parser_name,
            evidence=evidence,
        )
        return OperationalAuditRunResult(
            ok=True,
            evidence_path=evidence_path,
            kernel_path=kernel_path,
            audit_path=audit_path,
            attachment_status=attachment_status,
        )
    except Exception as exc:
        return OperationalAuditRunResult(
            ok=False,
            evidence_path=evidence_path,
            kernel_path=kernel_path,
            audit_path=audit_path,
            attachment_status=_failed_attachment_status(
                excel_path=excel_path,
                source_channel="telegram",
                parser_name=parser_name,
                exc=exc,
            ),
        )
