"""Local XLSX evidence extraction for PymIA.

Compatibility CLI over the glass-box document ingestion layer.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from pymia.contracts.evidence_v1 import StructuredEvidence
from tools.document_ingestion import (
    build_structured_evidence_from_xlsx,
    curate_xlsx_document,
    persist_curation_artifacts,
)


JsonObject = dict[str, Any]


class ExcelEvidenceBuilder:
    def build_evidence(
        self,
        *,
        excel_path: str | Path,
        tenant_id: str,
        document_type: str = "xlsx_operational_evidence",
    ) -> StructuredEvidence:
        return build_structured_evidence_from_xlsx(
            excel_path=excel_path,
            tenant_id=tenant_id,
            document_type=document_type,
        )


def build_excel_structured_evidence(
    *,
    excel_path: str | Path,
    tenant_id: str,
    document_type: str = "xlsx_operational_evidence",
) -> StructuredEvidence:
    return ExcelEvidenceBuilder().build_evidence(
        excel_path=excel_path,
        tenant_id=tenant_id,
        document_type=document_type,
    )


def evidence_to_kernel_artifact(evidence: StructuredEvidence) -> JsonObject:
    from pymia.interfaces.conversational_port import ClinicalConversationalPort, ConversationalInput

    output = ClinicalConversationalPort().handle(
        ConversationalInput(
            tenant_id=evidence.tenant_id,
            channel="local_excel_evidence",
            text="revisar rentabilidad con excel procesado localmente",
            evidence=evidence,
        )
    )
    return {
        "ok": output.status in {"ok", "no_signal"},
        "kernel": {"status": output.status, "message": output.message},
        "evidence": evidence.model_dump(mode="json"),
    }


def _write_json(path: Path, payload: JsonObject) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Extract XLSX evidence locally and run it through PymIA kernel")
    parser.add_argument("--excel", required=True)
    parser.add_argument("--tenant-id", required=True)
    parser.add_argument("--evidence-output", required=True)
    parser.add_argument("--kernel-output", required=True)
    parser.add_argument("--curation-output", required=False)
    parser.add_argument("--artifact-dir", required=False)
    args = parser.parse_args(argv)

    curated = curate_xlsx_document(args.excel)
    evidence = build_excel_structured_evidence(excel_path=args.excel, tenant_id=args.tenant_id)

    _write_json(Path(args.evidence_output), evidence.model_dump(mode="json"))
    if args.curation_output:
        _write_json(Path(args.curation_output), curated.to_dict())
    if args.artifact_dir:
        persist_curation_artifacts(
            curated=curated,
            evidence=evidence,
            output_dir=args.artifact_dir,
            stem=Path(args.excel).stem,
        )

    artifact = evidence_to_kernel_artifact(evidence)
    _write_json(Path(args.kernel_output), artifact)
    print(json.dumps({"ok": artifact["ok"], "computed_variables": evidence.computed_variables}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
