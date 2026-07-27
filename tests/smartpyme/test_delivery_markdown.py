from __future__ import annotations

import ast
import copy
from pathlib import Path

import pytest

from pymia.smartpyme.delivery_package import DeliveryPackage


def _package_dict(status: str = "READY_TO_DELIVER") -> dict:
    return {
        "tenant_id": "tenant_1",
        "intake_id": "intake_1",
        "runtime_classification": "excel_diagnostic",
        "output_refs": ["C:/tmp/diagnostic_report.md"],
        "summary": "Entrega lista.",
        "warnings": ["w1"],
        "reasons": ["r1"],
        "gate_verdict": "PASS",
        "status": status,
        "created_at": "2026-05-26T00:00:00+00:00",
    }


def test_import_smoke():
    from pymia.smartpyme.delivery_markdown import render_delivery_markdown  # noqa: F401


def test_render_with_ready_to_deliver_contains_all_fields():
    from pymia.smartpyme.delivery_markdown import render_delivery_markdown

    md = render_delivery_markdown(_package_dict("READY_TO_DELIVER"))
    assert "**Status:** READY_TO_DELIVER" in md
    assert "tenant_1" in md
    assert "intake_1" in md
    assert "excel_diagnostic" in md
    assert "2026-05-26T00:00:00+00:00" in md
    assert "Entrega lista." in md
    assert "- C:/tmp/diagnostic_report.md" in md


def test_render_with_blocked_contains_reasons_prominently():
    from pymia.smartpyme.delivery_markdown import render_delivery_markdown

    data = _package_dict("BLOCKED")
    data["reasons"] = ["blocked reason"]
    md = render_delivery_markdown(data)
    assert "**Status:** BLOCKED" in md
    assert "## Reasons" in md
    assert "- blocked reason" in md


def test_render_with_failed_contains_reasons_and_gate_verdict_context():
    from pymia.smartpyme.delivery_markdown import render_delivery_markdown

    data = _package_dict("FAILED")
    data["reasons"] = ["failed reason"]
    md = render_delivery_markdown(data)
    assert "**Status:** FAILED" in md
    assert "## Reasons" in md
    assert "- failed reason" in md


def test_accepts_delivery_package_and_dict():
    from pymia.smartpyme.delivery_markdown import render_delivery_markdown

    d = _package_dict()
    md_dict = render_delivery_markdown(d)

    p = DeliveryPackage(
        tenant_id=d["tenant_id"],
        intake_id=d["intake_id"],
        runtime_classification=d["runtime_classification"],
        output_refs=list(d["output_refs"]),
        summary=d["summary"],
        warnings=list(d["warnings"]),
        reasons=list(d["reasons"]),
        gate_verdict=d["gate_verdict"],
        status=d["status"],
        created_at=d["created_at"],
    )
    md_dc = render_delivery_markdown(p)

    assert md_dict == md_dc


def test_no_mutation_of_input():
    from pymia.smartpyme.delivery_markdown import render_delivery_markdown

    package = _package_dict()
    snap = copy.deepcopy(package)
    render_delivery_markdown(package)
    assert package == snap


def test_output_is_valid_string():
    from pymia.smartpyme.delivery_markdown import render_delivery_markdown

    md = render_delivery_markdown(_package_dict())
    assert isinstance(md, str)
    assert md


def test_does_not_import_excel_or_supplier_modules_ast():
    source = Path("pymia/smartpyme/delivery_markdown.py").read_text(encoding="utf-8")
    tree = ast.parse(source)

    forbidden_prefixes = (
        "pymia.smartpyme.excel_diagnostic",
        "pymia.smartpyme.supplier_duplicate_check",
        "pymia.smartpyme.classifications.supplier_duplicate_check",
    )

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert not alias.name.startswith(forbidden_prefixes)
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            assert not module.startswith(forbidden_prefixes)


def test_empty_warnings_shows_placeholder():
    from pymia.smartpyme.delivery_markdown import render_delivery_markdown

    d = _package_dict()
    d["warnings"] = []
    md = render_delivery_markdown(d)
    assert "No warnings." in md


def test_empty_reasons_shows_placeholder():
    from pymia.smartpyme.delivery_markdown import render_delivery_markdown

    d = _package_dict()
    d["reasons"] = []
    md = render_delivery_markdown(d)
    assert "No reasons." in md


def test_empty_output_refs_shows_placeholder():
    from pymia.smartpyme.delivery_markdown import render_delivery_markdown

    d = _package_dict()
    d["output_refs"] = []
    md = render_delivery_markdown(d)
    assert "No output references." in md


def test_invalid_package_raises_value_error():
    from pymia.smartpyme.delivery_markdown import render_delivery_markdown

    class Invalid:
        pass

    with pytest.raises(ValueError):
        render_delivery_markdown(Invalid())
