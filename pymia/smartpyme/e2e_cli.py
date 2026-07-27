from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from pymia.smartpyme.classifications.supplier_duplicate_check import diagnose_supplier_duplicates
from pymia.smartpyme.excel_diagnostic import diagnose_excel
from pymia.smartpyme.reception import ReceptionRecord, create_reception
from pymia.smartpyme.storage import append_reception_jsonl, ensure_tenant_storage, write_result_reception


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="SmartPyme local MVP E2E CLI")
    parser.add_argument("--tenant-id", required=True)
    parser.add_argument("--message", required=True)
    parser.add_argument("--classification", required=True)
    parser.add_argument("--input", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--storage-dir", required=False, default=None)
    return parser


def _run_classification(*, classification: str, excel_path: Path, tenant_id: str, report_path: Path):
    if classification == "supplier_duplicate_check":
        diag, diagnostic_status = diagnose_supplier_duplicates(
            excel_path=excel_path,
            tenant_id=tenant_id,
            markdown_output_path=report_path,
        )
        return diag, diagnostic_status

    diag = diagnose_excel(
        excel_path=excel_path,
        tenant_id=tenant_id,
        markdown_output_path=report_path,
    )
    return diag, "PASS"


def run_e2e(
    *,
    tenant_id: str,
    message: str,
    classification: str,
    input_path: str,
    out_dir: str,
    storage_dir: str | None,
) -> dict:
    excel_path = Path(input_path)
    if not excel_path.exists():
        raise FileNotFoundError(f"input file not found: {excel_path}")

    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    storage_base = Path(storage_dir) if storage_dir else (out / "storage")

    report_path = out / "diagnostic_report.md"
    result_path = out / "diagnostic_result.json"
    reception_path = out / "reception_record.json"

    diag, diagnostic_status = _run_classification(
        classification=classification,
        excel_path=excel_path,
        tenant_id=tenant_id,
        report_path=report_path,
    )
    findings = [asdict(f) for f in diag.findings]
    if not findings:
        raise RuntimeError("findings cannot be empty for MVP runtime flow")

    diagnostic_result = {
        "tenant_id": tenant_id,
        "classification": classification,
        "diagnostic_status": diagnostic_status,
        "source_file": str(excel_path),
        "findings_count": len(findings),
        "findings": findings,
    }
    result_path.write_text(json.dumps(diagnostic_result, indent=2, ensure_ascii=False), encoding="utf-8")

    evidence_refs = [str(excel_path)]
    output_refs = [str(report_path), str(result_path)]
    reception: ReceptionRecord = create_reception(
        tenant_id=tenant_id,
        message=message,
        classification=classification,
        status="BLOCKED" if diagnostic_status == "BLOCKED" else "DELIVERED",
        evidence_refs=evidence_refs,
        output_refs=output_refs,
    )
    reception_path.write_text(json.dumps(asdict(reception), indent=2, ensure_ascii=False), encoding="utf-8")

    ensure_tenant_storage(storage_base, tenant_id)
    append_reception_jsonl(storage_base, reception)
    storage_result_path = write_result_reception(storage_base, reception)

    return {
        "tenant_id": tenant_id,
        "status": reception.status,
        "diagnostic_status": diagnostic_status,
        "findings_count": len(findings),
        "output_paths": {
            "diagnostic_report_md": str(report_path),
            "diagnostic_result_json": str(result_path),
            "reception_record_json": str(reception_path),
        },
        "storage_paths": {
            "receptions_jsonl": str((Path(storage_base) / tenant_id / "receptions.jsonl").resolve()),
            "result_reception_json": str(storage_result_path),
        },
    }


def main() -> int:
    args = _build_parser().parse_args()
    result = run_e2e(
        tenant_id=args.tenant_id,
        message=args.message,
        classification=args.classification,
        input_path=args.input,
        out_dir=args.out_dir,
        storage_dir=args.storage_dir,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
