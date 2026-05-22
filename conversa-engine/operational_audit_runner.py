from __future__ import annotations

import base64
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class OperationalAuditRunResult:
    ok: bool
    evidence_path: Path
    kernel_path: Path
    audit_path: Path


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

    from tools.excel_evidence import main

    session_bytes = str(session_id).encode("utf-8")
    encoded_id = base64.urlsafe_b64encode(session_bytes).decode("ascii").rstrip("=")
    session_dir = Path(output_dir) / encoded_id
    session_dir.mkdir(parents=True, exist_ok=True)

    evidence_path = session_dir / "evidence.json"
    kernel_path = session_dir / "kernel.json"
    audit_path = session_dir / "operational_audit_result.json"

    argv = [
        "--excel", str(excel_path),
        "--tenant-id", tenant_id,
        "--evidence-output", str(evidence_path),
        "--kernel-output", str(kernel_path),
        "--audit-output", str(audit_path),
    ]

    ret = main(argv)
    ok = (ret == 0 and audit_path.exists())

    return OperationalAuditRunResult(
        ok=ok,
        evidence_path=evidence_path,
        kernel_path=kernel_path,
        audit_path=audit_path,
    )
