from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any

from pymia.narrative.extract_evidence import extract_evidence_pool
from pymia.narrative.grounding_validator import validate_grounding
from pymia.narrative.report_generator_v2 import build_narrative_report_v2
from pymia.smartpyme.minimum_report import render_minimum_assisted_report
from tools.document_ingestion import (
    build_structured_evidence_from_xlsx,
    curate_xlsx_document,
    persist_curation_artifacts,
)


JsonObject = dict[str, Any]


def run_local_assisted_mvp(*, excel_path: str | Path, tenant_id: str, output_dir: str | Path) -> JsonObject:
    """Run the smallest executable SmartPyme local assisted flow.

    Input: one XLSX file.
    Output: auditable JSON artifacts plus a human-readable Markdown report.
    """

    start = time.perf_counter()
    excel = Path(excel_path)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    if not excel.exists():
        summary = _summary(
            ok=False,
            tenant_id=tenant_id,
            excel_path=excel,
            output_dir=out,
            status="FILE_NOT_FOUND",
            elapsed_seconds=time.perf_counter() - start,
            error=f"Excel file not found: {excel}",
        )
        _write_json(out / "run_summary.json", summary)
        return summary

    try:
        curated = curate_xlsx_document(excel)
        evidence = build_structured_evidence_from_xlsx(excel_path=excel, tenant_id=tenant_id)
        evidence_pool = extract_evidence_pool(evidence)
        narrative_report = build_narrative_report_v2(evidence_pool)
        grounding = validate_grounding(narrative_report, evidence_pool)

        persist_curation_artifacts(
            curated=curated,
            evidence=evidence,
            output_dir=out,
            stem=excel.stem,
        )

        _write_json(out / "curation.json", curated.to_dict())
        _write_json(out / "evidence.json", evidence.model_dump(mode="json"))
        _write_json(out / "narrative_report.json", narrative_report.model_dump(mode="json"))
        _write_json(out / "grounding.json", grounding.model_dump(mode="json"))

        report_md = render_minimum_assisted_report(
            evidence=evidence,
            narrative_report=narrative_report,
            curation_report=curated.to_dict(),
            tenant_id=tenant_id,
            source_file=excel,
        )
        report_path = out / "report.md"
        report_path.write_text(report_md, encoding="utf-8")

        status = "DELIVERED" if grounding.ok else "PARTIAL"
        if curated.report.status == "BLOCKED":
            status = "BLOCKED"

        summary = _summary(
            ok=status in {"DELIVERED", "PARTIAL"},
            tenant_id=tenant_id,
            excel_path=excel,
            output_dir=out,
            status=status,
            elapsed_seconds=time.perf_counter() - start,
            computed_variables=evidence.computed_variables,
            curation_status=curated.report.status,
            report_path=report_path,
            grounding_ok=grounding.ok,
        )
        _write_json(out / "run_summary.json", summary)
        return summary
    except Exception as exc:  # pragma: no cover - defensive CLI boundary
        summary = _summary(
            ok=False,
            tenant_id=tenant_id,
            excel_path=excel,
            output_dir=out,
            status="FAILED",
            elapsed_seconds=time.perf_counter() - start,
            error=str(exc),
        )
        _write_json(out / "run_summary.json", summary)
        return summary


def _summary(
    *,
    ok: bool,
    tenant_id: str,
    excel_path: Path,
    output_dir: Path,
    status: str,
    elapsed_seconds: float,
    computed_variables: dict[str, float] | None = None,
    curation_status: str | None = None,
    report_path: Path | None = None,
    grounding_ok: bool | None = None,
    error: str | None = None,
) -> JsonObject:
    payload: JsonObject = {
        "ok": ok,
        "status": status,
        "tenant_id": tenant_id,
        "excel_path": str(excel_path),
        "output_dir": str(output_dir),
        "elapsed_seconds": round(elapsed_seconds, 4),
        "elapsed_minutes": round(elapsed_seconds / 60, 4),
        "artifacts": {
            "run_summary": str(output_dir / "run_summary.json"),
            "report_md": str(report_path or output_dir / "report.md"),
            "evidence_json": str(output_dir / "evidence.json"),
            "curation_json": str(output_dir / "curation.json"),
            "narrative_report_json": str(output_dir / "narrative_report.json"),
            "grounding_json": str(output_dir / "grounding.json"),
        },
        "computed_variables": computed_variables or {},
        "curation_status": curation_status,
        "grounding_ok": grounding_ok,
    }
    if error:
        payload["error"] = error
    return payload


def _write_json(path: Path, payload: JsonObject) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run SmartPyme local assisted MVP from one XLSX file")
    parser.add_argument("--excel", required=True, help="Path to source XLSX")
    parser.add_argument("--tenant-id", required=True, help="Tenant/case identifier")
    parser.add_argument("--out", required=True, help="Output directory")
    args = parser.parse_args(argv)

    summary = run_local_assisted_mvp(excel_path=args.excel, tenant_id=args.tenant_id, output_dir=args.out)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
